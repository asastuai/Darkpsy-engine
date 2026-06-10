# -*- coding: utf-8 -*-
"""
End-to-end: a real track -> NEW arrangement with its cloned sounds.

  python forja/sample_from_track.py "C:/path/to/glosolalia.mp3" [--sec 120] [--bars 32]

1) loads the track (mp3/wav/flac), trims a section
2) separates it with Demucs (drums / bass / other)
3) runs the motor-sampler: slices the REAL kick/hat/bass and the engine composes
   a brand-new arrangement triggering those cloned sounds.

PRIVATE use only — the separated stems / original audio are never distributed
(forja/recreation_out is gitignored).
"""
import os, sys, subprocess, argparse, tempfile, shutil
import numpy as np
import librosa
from scipy.io import wavfile

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 44100
PY = sys.executable

ap = argparse.ArgumentParser()
ap.add_argument("track", help="ruta al audio (mp3/wav/flac)")
ap.add_argument("--sec", type=int, default=120, help="segundos a analizar")
ap.add_argument("--bars", type=int, default=32, help="bars del arreglo nuevo")
A = ap.parse_args()

if not os.path.exists(A.track):
    print(f"  NO existe: {A.track}"); sys.exit(1)

name = os.path.splitext(os.path.basename(A.track))[0].replace(" ", "_")[:24]
out_dir = os.path.join(REPO, "forja", "recreation_out", "sampler")
os.makedirs(out_dir, exist_ok=True)
work = tempfile.mkdtemp(prefix="darkpsy_smp_")

print("=" * 60)
print(f" SAMPLE FROM TRACK: {os.path.basename(A.track)}")
print("=" * 60)

# 1) load + trim + write clip
print(f"  cargando + recortando {A.sec}s...")
y, _ = librosa.load(A.track, sr=SR, mono=False)
if y.ndim == 1:
    y = np.vstack([y, y])
y = y[:, : A.sec * SR]
clip = os.path.join(work, "clip.wav")
wavfile.write(clip, SR, (np.clip(y.T, -1, 1) * 32767).astype(np.int16))

# 2) demucs
print("  separando con Demucs (CPU, ~1 min)...")
subprocess.run([PY, "-m", "demucs", "-n", "htdemucs", "-d", "cpu",
                "-o", work, "--filename", "{stem}.wav", clip], check=True)
demux = os.path.join(work, "htdemucs")
drums = os.path.join(demux, "drums.wav")
bass = os.path.join(demux, "bass.wav")
if not (os.path.exists(drums) and os.path.exists(bass)):
    print("  demucs no produjo drums/bass"); shutil.rmtree(work, ignore_errors=True); sys.exit(1)

# 3) motor-sampler with the cloned sounds
out = os.path.join(out_dir, f"new_{name}.wav")
print("  componiendo arreglo NUEVO con los sonidos del track...")
subprocess.run([PY, os.path.join(REPO, "forja", "motor_sampler.py"),
                "--kick", drums, "--drums", drums, "--bass", bass,
                "--bars", str(A.bars), "--out", out], check=True)

shutil.rmtree(work, ignore_errors=True)
print("\n" + "=" * 60)
print(f"  LISTO -> {out}")
print("  (arreglo nuevo, sonidos de tu Glosolalia)")
print("=" * 60)
