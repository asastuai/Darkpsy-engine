# -*- coding: utf-8 -*-
"""
EXPORT-STEMS-REAPER — los stems del track, procesados como en el render
(growl en bass, arrangement, sidechain), bajados a BPM techno por vari-speed,
y un proyecto .rpp que los carga con los faders del automix ya puestos.

El master bus (HP/saturador/matching EQ/micro-silencio) NO se aplica: eso es
lo que Juan va a tweakear en Reaper. Por eso la suma suena mas cruda que el
v14 — es la materia prima, no el plato terminado.

Uso: python forja/export_stems_reaper.py [bpm_destino]
"""
import os
import sys
import numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fm_chaos
import automix
import arrangement
from grammar import G

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STEMS = os.path.join(REPO, "stems_v9")
FM_CACHE = os.path.join(REPO, "forja", "recreation_out", "fm_stem_cache.npy")
SR = 44100
BPM_SRC = 150
GROWL_AMOUNT = 2.0
STEM_ORDER = ["kick", "bass", "acid", "drums", "lead", "pad", "fx"]

bpm_dst = float(sys.argv[1]) if len(sys.argv) > 1 else 132.0
OUTDIR = os.path.join(os.path.expanduser("~"), "Desktop", f"DarkPsy_techno{int(bpm_dst)}_stems")
os.makedirs(OUTDIR, exist_ok=True)


def read(path):
    sr, d = wavfile.read(path)
    if d.ndim == 1:
        d = np.column_stack([d, d])
    if d.dtype == np.int16:
        d = d.astype(np.float64) / 32768.0
    elif d.dtype == np.int32:
        d = d.astype(np.float64) / 2147483648.0
    return d


frac = Fraction(BPM_SRC * 10, int(bpm_dst * 10)).limit_denominator(10000)
up, down = frac.numerator, frac.denominator
print(f"  {BPM_SRC} -> {bpm_dst} BPM (vari-speed x{up}/{down}, pitch {12*np.log2(bpm_dst/BPM_SRC):+.1f} st)")

ref = read(os.path.join(STEMS, "kick.wav"))
N = len(ref)
nbars = int(N / SR / fm_chaos.BAR)
plan = arrangement.make_plan(nbars, fm_chaos.sec, seed=4)
gains = G["mix"]["stem_gains"]
print(f"  faders (automix vs {G['mix'].get('stem_gains_ref','?')}): " +
      "  ".join(f"{k}:{v}" for k, v in gains.items()))

# kick procesado primero: alimenta el sidechain de todos los demas
kick = read(os.path.join(STEMS, "kick.wav"))
kick_p = arrangement.process_stem("kick", kick, plan, fm_chaos.BAR)
km = (kick[:N, 0] + kick[:N, 1]) / 2
ke = np.abs(km)
w = int(0.03 * SR)
ks = np.convolve(ke, np.ones(w) / w, mode="same")
ks /= (ks.max() + 1e-9)
sc = (1 - ks * 0.15)[:, None]

fm = np.load(FM_CACHE)
fm = np.column_stack([fm[0].astype(np.float64), fm[1].astype(np.float64)])

items = {}
for name in STEM_ORDER + ["fm"]:
    if name == "kick":
        d = kick_p
    elif name == "fm":
        d = arrangement.process_stem("fm", fm, plan, fm_chaos.BAR)[:N] * sc
    else:
        d = read(os.path.join(STEMS, name + ".wav"))
        if name == "bass":
            d = automix.growl_saturate(d, GROWL_AMOUNT)
        d = arrangement.process_stem(name, d, plan, fm_chaos.BAR)[:N] * sc
    d = np.column_stack([resample_poly(d[:, ch], up, down) for ch in range(2)])
    pk = np.max(np.abs(d)) + 1e-9
    norm = min(1.0, 0.97 / pk)          # solo evita clip; el fader vive en el RPP
    d = d * norm
    p = os.path.join(OUTDIR, f"{name}.wav")
    wavfile.write(p, SR, (d * 32767).astype(np.int16))
    items[name] = {"file": p, "len_s": len(d) / SR, "vol": gains.get(name, 0.5) / norm}
    print(f"  + {name:6s} -> {os.path.basename(p)}  ({len(d)/SR:.0f}s, vol RPP {items[name]['vol']:.3f})")

# ---- proyecto Reaper ----
tracks = []
for name, it in items.items():
    f = it["file"].replace("\\", "/")
    tracks.append(f'''  <TRACK
    NAME "{name}"
    VOLPAN {it["vol"]:.6f} 0 -1 -1 1
    <ITEM
      POSITION 0
      LENGTH {it["len_s"]:.6f}
      NAME "{name}"
      <SOURCE WAVE
        FILE "{f}"
      >
    >
  >''')
rpp = f'''<REAPER_PROJECT 0.1 "7.0" 0
  TEMPO {bpm_dst} 4 4
{chr(10).join(tracks)}
>
'''
rpp_path = os.path.join(OUTDIR, f"DarkPsy_techno{int(bpm_dst)}.rpp")
with open(rpp_path, "w", encoding="utf-8") as fh:
    fh.write(rpp)
print(f"\n  -> {rpp_path}")
print("  master bus vacio a proposito: HP 28 Hz + saturacion + EQ es lo tuyo ahora.")
