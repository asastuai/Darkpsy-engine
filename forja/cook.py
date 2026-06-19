# -*- coding: utf-8 -*-
"""
COOK — el plato: junta todo lo que venimos hablando en un bocado del set.

  motor (render_full_fm, ya con disciplina de high-pass horneada)
    -> bajado a techno 132 por vari-speed (la técnica que enganchó a Juan)
    -> con el bajo de "Everybody" (palette) METIDO como momento icónico en el
       break (149-165), en la tonalidad del motor (E menor), con la mezcla
       duckeando debajo para que el guiño se luzca.

Es una cata, no el master final: muestra la dirección (generado + curado +
mezcla pro). Uso: python forja/cook.py
"""
import os
import sys
import numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly, butter, sosfilt
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import palette
import fm_chaos

SR = 44100
BPM = 150.0
BPM_DST = 132.0
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "forja", "recreation_out", "DarkPsy_chaosFM.wav")
ROOT_E1 = 28   # E1: el bajo de BSB en la tonalidad del motor (ROOT E2=40)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def read(path):
    sr, d = wavfile.read(path)
    if d.ndim == 1:
        d = np.column_stack([d, d])
    return d.astype(np.float64) / 32768.0


# 1) el motor (ya masterizado a 150, con high-pass discipline)
mix = read(SRC)
N = len(mix)
BAR = fm_chaos.BAR

# 2) el momento icónico: bajo de BSB en el break (bars 149-165), E menor.
#    patch con un toque más de drive (sabor Kranch del amigo).
bsb_patch = {"drive": 3.0, "resonance": 4.6, "cutoff_env_hz": 2900.0}
bsb = palette.render_riff(palette.bsb_everybody_bass, BPM, loops=8,
                          root_midi=ROOT_E1, p=bsb_patch)   # 8 loops x 2 bars = 16 bars
b0, b1 = 149, 165
a = int(b0 * BAR * SR)
e = min(int(b1 * BAR * SR), N)
win = e - a

# duck del motor bajo el guiño (-6 dB con rampas de 1 bar), y entra el BSB encima
duck = np.ones(N)
ramp = int(BAR * SR)
duck[a:e] = 0.5
if a - ramp > 0:
    duck[a - ramp:a] = np.linspace(1, 0.5, ramp)
if e + ramp < N:
    duck[e:e + ramp] = np.linspace(0.5, 1, ramp)
mix *= duck[:, None]

bm = bsb[:win]
mix[a:a + len(bm), 0] += bm * 0.85
mix[a:a + len(bm), 1] += bm * 0.85
print(f"  momento BSB en el break: bars {b0}-{b1}  ({a/SR:.0f}s-{e/SR:.0f}s @150)")

# 3) a techno 132 por vari-speed (tempo y pitch bajan juntos = más oscuro)
frac = Fraction(int(BPM * 10), int(BPM_DST * 10)).limit_denominator(10000)
up, down = frac.numerator, frac.denominator
y = np.column_stack([resample_poly(mix[:, ch], up, down) for ch in range(2)])
print(f"  {BPM}->{BPM_DST} BPM (vari-speed, pitch {12*np.log2(BPM_DST/BPM):+.1f} st)")

# 4) un pelo de pegamento y normalizo
y = np.tanh(y * 1.05) / np.tanh(1.05)
pk = np.max(np.abs(y)) + 1e-9
y = y / pk * 0.97
rms = np.sqrt(np.mean(y ** 2))
g = min((10 ** (-9.0 / 20)) / (rms + 1e-9), 2.0)
y = np.clip(y * g, -0.98, 0.98)

dst = os.path.join(os.path.expanduser("~"), "Desktop", "DarkPsy_COOK_v1.wav")
wavfile.write(dst, SR, (y * 32767).astype(np.int16))
print(f"\n  -> {dst}  ({len(y)/SR:.0f}s)")
print(f"  el momento BSB cae cerca de {a/SR*BPM/BPM_DST:.0f}s en esta versión 132")
