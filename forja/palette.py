# -*- coding: utf-8 -*-
"""
PALETTE — voces icónicas recreadas por síntesis, para dispararlas en momentos
puntuales del live. NO se samplea el master de nadie: el timbre no tiene
copyright (solo la grabación y la melodía), así que lo RECREAMOS. Resultado:
es nuestro, lo controla el motor (filtro/caos/drive en vivo) y vive dentro del
esqueleto en vez de ser un parche pegado.

Cada voz es una función paramétrica. Cuando el oído de Juan confirma el timbre,
sus números se cristalizan en palette.json (igual que grammar.json para el género).

Voces:
  bsb_everybody_bass  — el bajo gruñón/resonante de "Everybody" (Cheiron, 1997):
                        sierras detuneadas + LP resonante con envolvente rápida
                        (el "wow"/squelch) + saturación (el growl).

Demo:  python forja/palette.py bsb_everybody_bass [bpm]
"""
import os
import sys
import numpy as np
from scipy.io import wavfile

SR = 44100


def nf(midi):
    return 440.0 * 2 ** ((midi - 69) / 12.0)


# ---------------- bloques de síntesis ----------------
def saw(freq_hz, n, detune_cents=0.0, phase0=0.0):
    """Sierra naïve (el LP resonante después tapa el aliasing en registro grave)."""
    f = freq_hz * 2 ** (detune_cents / 1200.0)
    t = np.arange(n) / SR
    ph = (f * t + phase0) % 1.0
    return 2.0 * ph - 1.0


def svf_lowpass(x, cutoff_hz, q):
    """Filtro state-variable TPT (Cytomic), pasa-bajos resonante, cutoff por
    muestra para el barrido. Loop por muestra: el feedback no se vectoriza."""
    n = len(x)
    out = np.empty(n)
    cutoff = np.clip(cutoff_hz, 20.0, SR * 0.45)
    k = 1.0 / max(q, 0.5)
    ic1 = 0.0
    ic2 = 0.0
    for i in range(n):
        g = np.tan(np.pi * cutoff[i] / SR)
        a1 = 1.0 / (1.0 + g * (g + k))
        a2 = g * a1
        a3 = g * a2
        v3 = x[i] - ic2
        v1 = a1 * ic1 + a2 * v3
        v2 = ic2 + a2 * ic1 + a3 * v3
        ic1 = 2.0 * v1 - ic1
        ic2 = 2.0 * v2 - ic2
        out[i] = v2
    return out


def adsr_amp(n, a=0.004, d=0.0, s=1.0, r=0.03):
    """Envolvente de amplitud sencilla (segundos)."""
    env = np.ones(n)
    na = min(n, int(a * SR))
    nr = min(n - na, int(r * SR))
    if na > 0:
        env[:na] = np.linspace(0, 1, na)
    nd = min(n - na - nr, int(d * SR))
    if nd > 0:
        env[na:na + nd] = np.linspace(1, s, nd)
        env[na + nd:n - nr] = s
    if nr > 0:
        env[n - nr:] *= np.linspace(1, 0, nr)
    return env


def drive(x, amount):
    if amount <= 0:
        return x
    return np.tanh(x * amount) / np.tanh(amount)


# ---------------- la voz: bajo de "Everybody" ----------------
def bsb_everybody_bass(midi, dur_s, p=None):
    """Una nota del bajo de Everybody. p = dict de parámetros (sin él usa el
    patch v1). Devuelve mono float en [-1,1] aprox."""
    p = p or {}
    detune = p.get("detune_cents", 11.0)     # ancho de las 2 sierras
    sub_lvl = p.get("sub_level", 0.55)        # seno una octava abajo (peso)
    cut_base = p.get("cutoff_base_hz", 230.0)  # filtro cerrado (cuerpo)
    cut_depth = p.get("cutoff_env_hz", 2600.0)  # cuánto abre el "wow"
    cut_decay = p.get("cutoff_decay_s", 0.075)  # qué tan rápido se cierra (squelch)
    q = p.get("resonance", 4.2)               # la resonancia = el gruñido vocal
    drv = p.get("drive", 2.4)                 # growl
    amp_d = p.get("amp_decay_s", 0.0)
    amp_s = p.get("amp_sustain", 1.0)

    n = max(1, int(dur_s * SR))
    f = nf(midi)
    osc = 0.5 * (saw(f, n, +detune) + saw(f, n, -detune, phase0=0.5))
    if sub_lvl > 0:
        t = np.arange(n) / SR
        osc = osc + sub_lvl * np.sin(2 * np.pi * (f / 2) * t)

    # envolvente de cutoff: salta arriba y se cierra rápido = el squelch resonante
    t = np.arange(n) / SR
    cenv = cut_base + cut_depth * np.exp(-t / max(cut_decay, 1e-3))
    sig = svf_lowpass(osc, cenv, q)
    sig = drive(sig, drv)
    sig *= adsr_amp(n, a=0.003, d=amp_d, s=amp_s, r=min(0.04, dur_s * 0.4))
    return sig * 0.9


# ---------------- riff de demo (evoca el groove, A menor) ----------------
# (offset en semitonos desde A1, duración en 16avos). Bajo pulsante con saltos
# de octava y un giro descendente G-F-E al cierre, el sabor del original.
_A1 = 33  # MIDI A1
_BSB_RIFF = [
    (0, 1), (0, 1), (12, 1), (0, 1),  (0, 1), (0, 1), (12, 1), (0, 1),
    (0, 1), (0, 1), (12, 1), (0, 1),  (0, 1), (-2, 1), (-4, 1), (-5, 1),
    (0, 1), (0, 1), (12, 1), (0, 1),  (0, 1), (0, 1), (12, 1), (0, 1),
    (0, 1), (0, 1), (12, 1), (-2, 1), (-4, 1), (-5, 1), (-7, 1), (0, 1),
]

VOICES = {"bsb_everybody_bass": bsb_everybody_bass}


def render_riff(voice_fn, bpm, riff=_BSB_RIFF, gate=0.92, p=None, loops=2, root_midi=_A1):
    s16 = 60.0 / bpm / 4.0
    total = int(sum(d for _, d in riff) * s16 * SR * loops) + SR
    out = np.zeros(total)
    pos = 0
    for _ in range(loops):
        for off, d in riff:
            dur = d * s16
            note = voice_fn(root_midi + off, dur * gate, p)
            e = min(pos + len(note), total)
            out[pos:e] += note[:e - pos]
            pos += int(dur * SR)
    pk = np.max(np.abs(out)) + 1e-9
    return out / pk * 0.97


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    name = sys.argv[1] if len(sys.argv) > 1 else "bsb_everybody_bass"
    bpm = float(sys.argv[2]) if len(sys.argv) > 2 else 150.0
    if name not in VOICES:
        print(f"  voz desconocida: {name}. disponibles: {list(VOICES)}")
        raise SystemExit(1)
    print(f"  recreando '{name}' @ {bpm} BPM...")
    mono = render_riff(VOICES[name], bpm)
    st = np.column_stack([mono, mono])
    dst = os.path.join(os.path.expanduser("~"), "Desktop", f"palette_{name}_{int(bpm)}bpm.wav")
    wavfile.write(dst, SR, (st * 32767).astype(np.int16))
    print(f"  -> {dst}  ({len(mono)/SR:.1f}s)")
