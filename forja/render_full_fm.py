# -*- coding: utf-8 -*-
"""
Full track with the chaos-driven FM wired in.

Reuses the existing Surge-rendered stems (stems_v9: kick/bass/lead/acid/pad/fx/drums)
and REPLACES the old static fm_texture with the new chaos-driven FM (fm_chaos.py),
then mixes + masters. Fast (no Surge re-render) — so you can hear the FM morph
ORDER->CHAOS across the whole track.

Run:  python forja/render_full_fm.py
"""
import os, sys
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fm_chaos

if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STEMS = os.path.join(REPO, "stems_v9")
OUT = os.path.join(REPO, "forja", "recreation_out", "DarkPsy_chaosFM.wav")
os.makedirs(os.path.dirname(OUT), exist_ok=True)
SR = 44100

# (file, fader) — fm is generated fresh, not loaded
MIX = [("kick.wav", 0.90), ("bass.wav", 0.85), ("acid.wav", 0.55),
       ("drums.wav", 0.55), ("lead.wav", 0.50), ("pad.wav", 0.40), ("fx.wav", 0.48)]
FM_FADER = 0.50

def read(path):
    sr, d = wavfile.read(path)
    if d.ndim == 1: d = np.column_stack([d, d])
    if d.dtype == np.int16: d = d.astype(np.float64) / 32768.0
    elif d.dtype == np.int32: d = d.astype(np.float64) / 2147483648.0
    return d

print("=" * 56); print(" FULL TRACK + chaos-driven FM"); print("=" * 56)

# length from kick stem
ref = read(os.path.join(STEMS, "kick.wav"))
N = len(ref)
mL = np.zeros(N); mR = np.zeros(N)
for fname, fad in MIX:
    p = os.path.join(STEMS, fname)
    if not os.path.exists(p): print(f"  falta {fname}"); continue
    d = read(p)
    n = min(N, len(d))
    mL[:n] += d[:n, 0] * fad; mR[:n] += d[:n, 1] * fad
    print(f"  + {fname:10s} x{fad}")

# new chaos FM
nbars = int(N / SR / fm_chaos.BAR)
print(f"  generando FM chaos-driven ({nbars} bars)...")
fL, fR = fm_chaos.render_fm_stem(nbars, gate=True)
fpk = max(np.max(np.abs(fL)), np.max(np.abs(fR))) + 1e-9
fL = fL / fpk; fR = fR / fpk
n = min(N, len(fL))
mL[:n] += fL[:n] * FM_FADER; mR[:n] += fR[:n] * FM_FADER
print(f"  + FM (chaos-driven) x{FM_FADER}")

# sidechain (kick-env duck, parity with v9)
kick = read(os.path.join(STEMS, "kick.wav"))
km = (kick[:N, 0] + kick[:N, 1]) / 2
ke = np.abs(km); w = int(0.03 * SR)
ks = np.convolve(ke, np.ones(w) / w, mode="same"); ks /= (ks.max() + 1e-9)
sc = 1 - ks * 0.15
kL = kick[:N, 0] * 0.90; kR = kick[:N, 1] * 0.90
mL = kL + (mL - kL) * sc; mR = kR + (mR - kR) * sc

# light master
def hp(x, fc): return sosfilt(butter(2, fc, btype="high", fs=SR, output="sos"), x)
def ws(x, a=1.7): return np.tanh(x * a) / np.tanh(a)
mL = hp(mL, 28); mR = hp(mR, 28)
mL = ws(mL); mR = ws(mR)
pk = max(np.max(np.abs(mL)), np.max(np.abs(mR)))
if pk > 0: mL /= pk; mR /= pk
rms = np.sqrt(np.mean(mL ** 2 + mR ** 2) / 2)
g = min((10 ** (-9.0 / 20)) / (rms + 1e-9), 3.0)
mL = np.clip(mL * g, -0.98, 0.98); mR = np.clip(mR * g, -0.98, 0.98)

wavfile.write(OUT, SR, np.column_stack([(mL * 32767).astype(np.int16), (mR * 32767).astype(np.int16)]))
print(f"\n  -> {OUT}  ({N/SR:.0f}s)")
print("  El FM morphea limpio->alien siguiendo la curva de chaos del track.")
