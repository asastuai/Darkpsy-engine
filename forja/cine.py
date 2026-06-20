# -*- coding: utf-8 -*-
"""
CINE — cómo IMAGINO el momento. Todo sintetizado desde cero (sin samples de
nadie): un bocado del set que demuestra el arma del silencio.

  groove de tekno oscuro rueda → DISPARO → corte total →
  silbido tipo Morricone solo en el vacío + viento + drone de tensión →
  espuelas + riser → medio segundo de NADA (el que eriza) →
  IMPACTO + el groove explota de vuelta.

Cada sonido es paramétrico (whistle, gunshot, wind, spurs, kick, bass, stab):
la misma filosofía del motor, ahora con paleta de cine western.

Uso: python forja/cine.py
"""
import os
import sys
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 44100
BPM = 132.0
BEAT = 60.0 / BPM
BAR = BEAT * 4
S16 = BEAT / 4

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def nf(m): return 440.0 * 2 ** ((m - 69) / 12.0)
def lp(x, fc): return sosfilt(butter(2, min(fc, SR*0.45), btype="low", fs=SR, output="sos"), x)
def hp(x, fc): return sosfilt(butter(2, max(fc, 20), btype="high", fs=SR, output="sos"), x)
def bp(x, lo, hi): return sosfilt(butter(2, [lo, min(hi, SR*0.45)], btype="band", fs=SR, output="sos"), x)
def env_ad(n, a, d, sustain=0.0, r=None):
    e = np.ones(n); na = int(a*SR)
    if na > 0: e[:na] = np.linspace(0, 1, na)
    nd = int(d*SR)
    if nd > 0 and na+nd < n: e[na:na+nd] = np.linspace(1, sustain, nd); e[na+nd:] = sustain
    if r:
        nr = int(r*SR)
        if nr < n: e[-nr:] *= np.linspace(1, 0, nr)
    return e


# ---------------- paleta de cine (todo síntesis) ----------------
def whistle(midi, dur, vib=5.0, vib_depth=0.18, breath=0.04):
    """Silbido tipo Morricone: sine + 2º armónico, vibrato que entra tarde,
    scoop de pitch al ataque, soplido al inicio. Solitario, expresivo."""
    n = int(dur*SR); t = np.arange(n)/SR
    f = nf(midi)
    scoop = 1.0 - 0.06*np.exp(-t/0.05)               # leve caída de pitch al entrar
    vdelay = np.clip((t-0.12)/0.2, 0, 1)             # el vibrato entra después
    vibrato = 1.0 + (vib_depth/12.0)*vdelay*np.sin(2*np.pi*vib*t)
    ph = 2*np.pi*np.cumsum(f*scoop*vibrato)/SR
    tone = np.sin(ph) + 0.18*np.sin(2*ph) + 0.05*np.sin(3*ph)
    air = hp(np.random.RandomState(int(midi*7)%999).randn(n), 3000) * np.exp(-t/0.06) * breath
    e = env_ad(n, 0.03, 0.0, 1.0, r=min(0.12, dur*0.5))
    return (tone*0.5 + air) * e


def wind(dur, level=0.12):
    n = int(dur*SR)
    nz = np.random.RandomState(3).randn(n)
    lfo = 0.5 + 0.5*np.sin(2*np.pi*0.15*np.arange(n)/SR)
    w = bp(nz, 350, 1100) * (0.5 + 0.5*lfo)
    return w/ (np.max(np.abs(w))+1e-9) * level


def drone(midi, dur, level=0.16):
    n = int(dur*SR); t = np.arange(n)/SR
    f = nf(midi)
    sig = (np.sin(2*np.pi*f*t) + 0.6*np.sin(2*np.pi*f*1.005*t)
           + 0.4*np.sin(2*np.pi*nf(midi+7)*t))
    sig = lp(sig, 600)
    swell = np.clip(t/(dur*0.6), 0, 1) * np.clip((dur-t)/(dur*0.4), 0, 1)
    return sig*swell*level


def gunshot():
    n = int(0.9*SR); t = np.arange(n)/SR
    crack = hp(np.random.RandomState(11).randn(n), 1800) * np.exp(-t/0.012)
    boom = np.sin(2*np.pi*(120*np.exp(-t/0.03)+45)*t) * np.exp(-t/0.08)
    tail = lp(np.random.RandomState(5).randn(n), 1500) * np.exp(-t/0.22) * 0.4
    s = crack*0.9 + boom*0.8 + tail
    return s/(np.max(np.abs(s))+1e-9)*0.95


def spurs(n_jingle=5):
    out = np.zeros(int(0.8*SR))
    rng = np.random.RandomState(21)
    for i in range(n_jingle):
        pos = int((0.06 + i*0.13 + rng.uniform(0, 0.02))*SR)
        m = int(0.05*SR); t = np.arange(m)/SR
        ring = (np.sin(2*np.pi*3200*t)+0.7*np.sin(2*np.pi*4700*t))*np.exp(-t/0.03)
        ring = hp(ring, 2500) * rng.uniform(0.5, 1.0)
        e = min(pos+m, len(out)); out[pos:e] += ring[:e-pos]
    return out/(np.max(np.abs(out))+1e-9)*0.5


def riser(dur):
    n = int(dur*SR); t = np.linspace(0, 1, n)
    nz = np.random.RandomState(7).randn(n)
    out = np.zeros(n); segs = 20
    for s in range(segs):
        a, b = int(n*s/segs), int(n*(s+1)/segs)
        fc = 300*(18)**(s/(segs-1))
        out[a:b] = bp(nz, fc*0.7, fc*1.5)[a:b]
    return out*(t**2.0)


def impact():
    n = int(1.6*SR); t = np.arange(n)/SR
    thump = np.sin(2*np.pi*(55*np.exp(-t/0.06)+40)*t)*np.exp(-t/0.5)
    crash = hp(np.random.RandomState(9).randn(n), 2000)*np.exp(-t/0.4)*0.5
    return (thump + crash)


# ---------------- groove de tekno oscuro (kick + bass roll + hat + stab) ----------------
def kick():
    n = int(0.32*SR); t = np.arange(n)/SR
    f = 50 + 95*np.exp(-t/0.018)
    body = np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t/0.12)
    click = hp(np.random.RandomState(1).randn(n), 3000)*np.exp(-t/0.004)*0.5
    k = np.tanh((body + click)*1.6)/np.tanh(1.6)
    return k*0.95
KICK = kick()

def hat():
    n = int(0.06*SR); t = np.arange(n)/SR
    return hp(np.random.RandomState(2).randn(n), 7000)*np.exp(-t/0.018)*0.35
HAT = hat()

def bass_note(midi, dur):
    n = int(dur*SR); t = np.arange(n)/SR
    f = nf(midi)
    saw = 2*((f*t) % 1.0)-1
    sig = lp(saw, 260)                                   # filtro grave, bass oscuro
    sig = np.tanh(sig*1.5)/np.tanh(1.5)
    return sig*env_ad(n, 0.002, dur*0.5, 0.3, r=dur*0.2)*0.8

def stab(root_midi, dur):
    n = int(dur*SR); t = np.arange(n)/SR
    sig = np.zeros(n)
    for off in (0, 3, 7):                                # tríada menor
        f = nf(root_midi+off)
        sig += 2*(((f*1.003)*t) % 1.0)-1
    sig = sosfilt(butter(2, [200, 1400], btype="band", fs=SR, output="sos"), sig)
    sig = np.tanh(sig*1.2)/np.tanh(1.2)
    return sig*env_ad(n, 0.003, dur*0.7, 0.0)*0.22


def add(buf, x, t0, g=1.0):
    p = int(t0*SR); e = min(p+len(x), len(buf))
    if p >= 0 and e > p: buf[p:e] += x[:e-p]*g


def groove(buf, bar0, nbars, root=33, level=1.0, hats=True, stabs=True):
    """root = A1 (MIDI 33). Pone kick 4x4, bass roll 16avos (KBBB), hats, stabs."""
    for b in range(nbars):
        tb = (bar0+b)*BAR
        for beat in range(4):
            add(buf, KICK, tb+beat*BEAT, level)
            if hats: add(buf, HAT, tb+beat*BEAT+S16*2, level*0.9)
            for s in (1, 2, 3):                          # KBBB: kick ocupa el 16avo 0
                add(buf, bass_note(root, S16*0.9), tb+beat*BEAT+s*S16, level)
        if stabs and b % 2 == 1:
            add(buf, stab(root+12, BEAT*0.5), tb+2*BEAT, level)


# ---------------- la película: silencio como antesala ----------------
def build():
    total = int(13*BAR*SR)
    L = np.zeros(total); R = np.zeros(total)
    M = np.zeros(total)   # mono work buffer; lo paneamos al final

    # 1) el groove rueda (bars 0-3)
    groove(M, 0, 4)
    # 2) el disparo en el último beat del bar 3, y CORTE: el groove no entra en bar 4
    add(M, gunshot(), 4*BAR - BEAT*0.5, 0.9)
    # corte limpio: silenciamos cualquier cola justo en el downbeat del bar 4
    cut = int(4*BAR*SR)
    M[cut:cut+int(0.02*SR)] *= np.linspace(1, 0, int(0.02*SR))
    M[cut+int(0.02*SR):int(4*BAR*SR + 0.05*SR)] = 0.0

    # 3) el vacío (bars 4-5): silbido Morricone solo + viento + drone de tensión
    add(M, wind(2*BAR, 0.12), 4*BAR)
    add(M, drone(33, 2*BAR, 0.16), 4*BAR)               # A1 drone
    # frase del silbido (A menor, registro agudo) — haunting
    phrase = [(76, 0.5, 1.0), (81, 1.5, 1.0), (83, 2.5, 1.6), (81, 4.2, 2.2)]
    for midi, beat, dur in phrase:
        add(M, whistle(midi, dur*BEAT), 4*BAR + beat*BEAT, 0.55)

    # 4) espuelas + riser (bar 6), tensión al máximo
    add(M, spurs(6), 6*BAR + BEAT*0.5, 0.5)
    add(M, riser(BAR*0.9), 6*BAR, 0.22)
    add(M, drone(33, BAR, 0.14), 6*BAR)

    # 5) el medio segundo de NADA antes de la explosión (el que eriza)
    silcut = int((7*BAR - 0.42)*SR)
    M[silcut-int(0.01*SR):int(7*BAR*SR)] = 0.0
    if silcut-int(0.03*SR) > 0:
        M[silcut-int(0.03*SR):silcut-int(0.01*SR)] *= np.linspace(1, 0, int(0.02*SR))

    # 6) IMPACTO + el groove explota (bars 7-11), más fuerte
    add(M, impact(), 7*BAR, 0.9)
    groove(M, 7, 5, level=1.0)
    # cierre
    fade = int(0.5*SR); M[-fade:] *= np.linspace(1, 0, fade)

    # leve glue + normalizo, y un toque de stereo
    M = np.tanh(M*1.1)/np.tanh(1.1)
    L = M.copy(); R = M.copy()
    return L, R, total


if __name__ == "__main__":
    print("  construyendo el momento (silencio como antesala)...")
    L, R, total = build()
    pk = max(np.max(np.abs(L)), np.max(np.abs(R)))+1e-9
    L = L/pk*0.97; R = R/pk*0.97
    out = np.column_stack([(L*32767).astype(np.int16), (R*32767).astype(np.int16)])
    dst = os.path.join(os.path.expanduser("~"), "Desktop", "DarkPsy_MOMENTO_silencio.wav")
    wavfile.write(dst, SR, out)
    print(f"  -> {dst}  ({total/SR:.0f}s)")
    print("  groove → disparo → vacío + silbido → espuelas → NADA → explosión")
