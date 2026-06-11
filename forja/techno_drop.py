# -*- coding: utf-8 -*-
"""
TECHNO-DROP — experimento: el track darkpsy bajado a BPM de techno por
resampleo puro (vari-speed, como bajar la velocidad de una bandeja).
El pitch baja junto con el tempo (150->132 = ~-2.2 semitonos): el kick cae
de ~50 a ~44 Hz y todo se oscurece. Es el truco clasico del dark techno.

Uso: python forja/techno_drop.py [bpm_destino] [tag]
"""
import os
import sys
import numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "forja", "recreation_out", "DarkPsy_chaosFM.wav")
BPM_SRC = 150
bpm_dst = float(sys.argv[1]) if len(sys.argv) > 1 else 132.0
tag = sys.argv[2] if len(sys.argv) > 2 else f"techno{int(bpm_dst)}"

sr, d = wavfile.read(SRC)
x = d.astype(np.float64) / 32768.0
semis = 12 * np.log2(bpm_dst / BPM_SRC)
print(f"  {BPM_SRC} -> {bpm_dst} BPM  (pitch {semis:+.1f} semitonos, kick ~{50*bpm_dst/BPM_SRC:.0f} Hz)")
up, down = int(round(BPM_SRC * 100)), int(round(bpm_dst * 100))
y = np.column_stack([resample_poly(x[:, ch], up, down) for ch in range(2)])
pk = np.max(np.abs(y)) + 1e-9
y = np.clip(y / pk * 0.97, -0.98, 0.98)
dst = os.path.join(os.path.expanduser("~"), "Desktop", f"DarkPsy_{tag}.wav")
wavfile.write(dst, sr, (y * 32767).astype(np.int16))
print(f"  -> {dst}  ({len(y)/sr:.0f}s)")
