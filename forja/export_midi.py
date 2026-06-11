# -*- coding: utf-8 -*-
"""
EXPORT-MIDI — las notas del motor como MIDI estándar para Ableton (o cualquier DAW).

El motor es paramétrico: las notas no están enterradas en el audio, las
generamos. Esto las emite como un .mid tipo 1 multipista:
  KICK      four-on-floor (ley del género)
  BASS      KBBB en 16avos, root E1, phase-reset implícito en cada nota
  FM STABS  los stabs chaos-driven (misma lógica de _schedule_bar)
  FM ATMOS  las notas alargadas de atmósfera (2 voces, root+quinta)

Más OPERATOR_RECIPE.txt: cómo recrear la voz FM en Operator de Ableton con
nuestros números de grammar.json (ratio C:M, índice, envolventes).

Lo que NO se exporta: acid/drums/lead/pad/fx — texturas horneadas en Surge
(v9); sus notas no existen como datos. Para esos canales el MIDI no aplica.

Uso: python forja/export_midi.py [bpm] [carpeta_salida]
"""
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import fm_chaos
from grammar import G, lerp, lerp_axis

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BPM = float(sys.argv[1]) if len(sys.argv) > 1 else 150.0
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.expanduser("~"), "Desktop", "DarkPsy_MIDI")
os.makedirs(OUTDIR, exist_ok=True)

TPQ = 480                       # ticks por negra
BAR_T = TPQ * 4                 # compás 4/4
S16_T = TPQ // 4                # un 16avo
TOTAL_BARS = fm_chaos.TOTAL_BARS
ROOT = fm_chaos.ROOT            # E2 = 40
KICK_NOTE = 36                  # C1, estándar de drum maps
BASS_ROOT = ROOT - 12           # E1 = 28


# ---------------- mini-escritor de MIDI tipo 1 (sin dependencias) ----------------
def vlq(n):
    """Variable-length quantity."""
    out = [n & 0x7F]
    n >>= 7
    while n:
        out.append((n & 0x7F) | 0x80)
        n >>= 7
    return bytes(reversed(out))


def track_bytes(events, name):
    """events: lista (tick, on/off, note, vel). Devuelve el chunk MTrk."""
    events.sort(key=lambda e: (e[0], e[1]))   # offs (0) antes que ons (1) en el mismo tick
    data = b"\x00\xff\x03" + bytes([len(name)]) + name.encode("ascii")
    last = 0
    for tick, kind, note, vel in events:
        data += vlq(tick - last)
        data += bytes([0x90 if kind else 0x80, note & 0x7F, vel & 0x7F])
        last = tick
    data += b"\x00\xff\x2f\x00"
    return b"MTrk" + struct.pack(">I", len(data)) + data


def tempo_track(bpm):
    us = int(60_000_000 / bpm)
    data = b"\x00\xff\x51\x03" + struct.pack(">I", us)[1:] + b"\x00\xff\x2f\x00"
    return b"MTrk" + struct.pack(">I", len(data)) + data


def write_midi(path, named_tracks, bpm):
    chunks = [tempo_track(bpm)] + [track_bytes(ev, nm) for nm, ev in named_tracks]
    hdr = b"MThd" + struct.pack(">IHHH", 6, 1, len(chunks), TPQ)
    with open(path, "wb") as f:
        f.write(hdr + b"".join(chunks))


def add_note(ev, tick, note, dur_t, vel):
    note = max(0, min(127, int(note)))
    ev.append((int(tick), 1, note, int(vel)))
    ev.append((int(tick + max(1, dur_t)), 0, note, 0))


# ---------------- las notas, desde la misma ley que el render ----------------
def playable(bar):
    return fm_chaos.sec(bar) != "silence"


kick_ev, bass_ev, stab_ev, atmo_ev = [], [], [], []
_ATMO = G["atmosphere"]
PAD_CHAOS = _ATMO["pad_chaos_threshold"]
rng = np.random.RandomState(7)   # misma semilla que el render

bass_decay_t = int(S16_T * 0.75)  # note_len_frac_of_16th ~0.7-0.8 (grammar)

for ab in range(TOTAL_BARS):
    t0 = ab * BAR_T
    if playable(ab):
        for beat in range(4):
            add_note(kick_ev, t0 + beat * TPQ, KICK_NOTE, int(TPQ * 0.4), 120)
            for s in (1, 2, 3):   # KBBB: el kick ocupa el 16avo 0
                add_note(bass_ev, t0 + beat * TPQ + s * S16_T, BASS_ROOT, bass_decay_t, 105)
    # FM: misma estructura de decisión que fm_chaos._schedule_bar
    c = fm_chaos.chaos_at(ab)
    if c < 0.15:
        continue   # el stem FM está gateado bajo ese umbral
    if c >= PAD_CHAOS:
        n_notes = _ATMO["accent_stabs_per_bar"]
        run0 = ab
        while run0 > 0 and fm_chaos.chaos_at(run0 - 1) >= PAD_CHAOS:
            run0 -= 1
        if (ab - run0) % _ATMO["pad_every_bars"] == 0:
            off = fm_chaos.PHRASE[ab % len(fm_chaos.PHRASE)]
            dur_t = int(_ATMO["pad_bars"] * BAR_T)
            for v in _ATMO["voices"]:
                add_note(atmo_ev, t0, ROOT + off + v["offset"], dur_t, 75)
    else:
        n_notes = int(round(lerp_axis("chaos", "stab_notes_per_bar", c)))
    step = 16 // max(1, n_notes)
    for k in range(n_notes):
        off = fm_chaos.PHRASE[(ab * n_notes + k) % len(fm_chaos.PHRASE)]
        if c > 0.5 and rng.random() < 0.4:
            off += rng.choice([-1, 1, 2])
        dur_16ths = 1.5 if c < 0.3 else (0.8 + rng.random() * 1.2)
        vel = int(lerp(85, 115, c))
        add_note(stab_ev, t0 + k * step * S16_T, ROOT + off, int(dur_16ths * S16_T), vel)

mid_path = os.path.join(OUTDIR, f"DarkPsy_{int(BPM)}bpm.mid")
write_midi(mid_path, [
    ("KICK", kick_ev), ("BASS", bass_ev), ("FM STABS", stab_ev), ("FM ATMOS", atmo_ev),
], BPM)

# ---------------- receta Operator ----------------
ax = G["axes"]["chaos"]
recipe = f"""RECETA OPERATOR (Ableton) — la voz FM del motor, de grammar.json
=================================================================
Estructura: 2 operadores, algoritmo B->A en serie (el clasico FM de Chowning).
  Operator A = carrier (Coarse 1, Fine 0)
  Operator B = modulator -> su Coarse/Fine fija el ratio C:M
  El "indice de modulacion" = nivel (Level) del operador B.

EJE ORDEN<->CAOS (mover juntos = el morph del motor):
  ORDEN (limpio, armonico):
    Ratio C:M = {ax['fm_ratio']['from']}  -> Operator B Coarse 2, Fine 0
    Indice    = bajo  -> Level de B ~ -30 dB
    Amp env   = pluck: Decay corto (~300 ms), Sustain -inf
  CAOS (metalico, alien):
    Ratio C:M = {ax['fm_ratio']['to']}  -> Operator B Coarse 2, Fine ~730 (2.73)
    Indice    = alto y SUBIENDO durante la nota
              -> Level de B ~ -8 dB + envolvente de pitch/level ascendente
    Amp env   = sostenida: Decay largo, Sustain audible

ATMOSFERA (notas largas del track "FM ATMOS"):
  Mismo patch en modo CAOS + amp env con attack lento (swell raised-cosine,
  pico al {int(G['atmosphere']['rise_range'][0]*100)}-{int(G['atmosphere']['rise_range'][1]*100)}% de la nota). Dos voces ya vienen en el MIDI (root+quinta);
  panealas -55 / +55 como el motor.

BASS (track "BASS"):
  Cualquier sinte mono con: phase reset por nota (Retrigger ON),
  decay max {G['bass']['max_decay_ms_formula']} ms, filtro LP cerrado.
  Es el rolling KBBB: el 16avo 1 de cada beat lo ocupa el kick.

KICK: four-on-floor, fundamental {G['kick']['fundamental_hz'][0]}-{G['kick']['fundamental_hz'][1]} Hz, click {G['kick']['click_band_hz'][0]}-{G['kick']['click_band_hz'][1]} Hz.

NO exportado (texturas Surge sin datos de notas): acid, drums, lead, pad, fx.
"""
rp = os.path.join(OUTDIR, "OPERATOR_RECIPE.txt")
with open(rp, "w", encoding="utf-8") as f:
    f.write(recipe)

print(f"  {len(kick_ev)//2} notas kick | {len(bass_ev)//2} bass | "
      f"{len(stab_ev)//2} fm stabs | {len(atmo_ev)//2} fm atmos")
print(f"  -> {mid_path}")
print(f"  -> {rp}")
