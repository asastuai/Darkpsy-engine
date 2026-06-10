# -*- coding: utf-8 -*-
"""
STYLE-LEARN — read the ARTIST's rhythmic grammar from a track (the "entiende").

Juan's key insight: cloned SOUNDS aren't enough — the abyss is in HOW the artist
uses rhythm, timing, space and transitions. So before generating, we must LEARN
his grammar from the track itself, as data:
  - his KICK pattern per bar (quantized onset grid)
  - his BASS phrasing per bar (onset grid + pitch)
  - his use of SPACE (energy/density per bar -> where he drops out / builds)
  - his GROOVE (microtiming deviation from the grid)
  - his TRANSITIONS (fills = onset-density spikes before section changes)

This script EXTRACTS and REPORTS that grammar so we can verify we captured it,
then later drive generation from it (instead of our generic patterns).

  python forja/style_learn.py "C:/.../Glosolalia - Blueprints.wav" [--sec 120] [--bpm 150]
Stems are separated once and cached in recreation_out/<name>_stems/.
"""
import os, sys, argparse, subprocess
import numpy as np
import librosa
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 44100
PY = sys.executable

ap = argparse.ArgumentParser()
ap.add_argument("track")
ap.add_argument("--sec", type=int, default=120)
ap.add_argument("--bpm", type=float, default=0.0, help="forzar BPM (0 = detectar)")
A = ap.parse_args()

name = os.path.splitext(os.path.basename(A.track))[0].replace(" ", "_").replace("-", "").replace("__", "_")[:20]
stem_dir = os.path.join(REPO, "forja", "recreation_out", f"{name}_stems")

def lp(x, fc): return sosfilt(butter(2, fc, btype="low", fs=SR, output="sos"), x)
def hp(x, fc): return sosfilt(butter(2, fc, btype="high", fs=SR, output="sos"), x)
def loadm(p):
    sr, d = wavfile.read(p)
    if d.dtype == np.int16: d = d.astype(np.float64)/32768.0
    elif d.dtype == np.int32: d = d.astype(np.float64)/2147483648.0
    else: d = d.astype(np.float64)
    if d.ndim > 1: d = d.mean(axis=1)
    return d

# --- separate once (cache) ---
if not (os.path.exists(os.path.join(stem_dir, "drums.wav")) and os.path.exists(os.path.join(stem_dir, "bass.wav"))):
    os.makedirs(stem_dir, exist_ok=True)
    print(f"  separando {os.path.basename(A.track)} (cache nuevo)...")
    y, _ = librosa.load(A.track, sr=SR, mono=False)
    if y.ndim == 1: y = np.vstack([y, y])
    y = y[:, : A.sec*SR]
    clip = os.path.join(stem_dir, "_clip.wav")
    wavfile.write(clip, SR, (np.clip(y.T, -1, 1)*32767).astype(np.int16))
    subprocess.run([PY, "-m", "demucs", "-n", "htdemucs", "-d", "cpu", "-o", stem_dir,
                    "--filename", "{stem}.wav", clip], check=True)
    import shutil
    for s in ["drums", "bass", "other", "vocals"]:
        src = os.path.join(stem_dir, "htdemucs", f"{s}.wav")
        if os.path.exists(src): shutil.copy(src, os.path.join(stem_dir, f"{s}.wav"))
else:
    print(f"  usando stems cacheados: {stem_dir}")

drums = loadm(os.path.join(stem_dir, "drums.wav"))
bass = loadm(os.path.join(stem_dir, "bass.wav"))
N = min(len(drums), len(bass))
drums, bass = drums[:N], bass[:N]

print("=" * 64)
print(f" STYLE-LEARN — gramática de {os.path.basename(A.track)}")
print("=" * 64)

# --- onsets ---
kick_on = librosa.onset.onset_detect(y=lp(drums, 160).astype(np.float32), sr=SR, units="time", backtrack=True)
hat_on = librosa.onset.onset_detect(y=hp(drums, 6000).astype(np.float32), sr=SR, units="time", backtrack=True)
bass_on = librosa.onset.onset_detect(y=bass.astype(np.float32), sr=SR, units="time", backtrack=True)

# --- tempo from KICK inter-onset interval (robust for 4-on-floor psy) ---
if A.bpm > 0:
    bpm, how = A.bpm, "forzado"
else:
    diffs = np.diff(kick_on)
    diffs = diffs[(diffs > 0.30) & (diffs < 0.52)]    # plausible beat = 115..200 BPM
    if len(diffs) >= 8:
        bpm, how = 60.0 / float(np.median(diffs)), "kick-IOI"
    else:
        tempo, _ = librosa.beat.beat_track(y=drums.astype(np.float32), sr=SR, start_bpm=148)
        bpm, how = float(np.atleast_1d(tempo)[0]), "beat_track"
beat = 60.0/bpm; bar = beat*4; s16 = beat/4
nbars = int(N/SR/bar)
print(f"  BPM: {bpm:.1f} ({how})   bars analizados: {nbars}")

def grid_per_bar(onsets):
    """16-step binary grid per bar from onset times."""
    G = np.zeros((nbars, 16), dtype=int)
    devs = []
    for t in onsets:
        b = int(t // bar)
        if b >= nbars: continue
        pos = (t - b*bar)/s16
        step = int(round(pos)) % 16
        G[b, step] = 1
        devs.append((pos - round(pos))*s16*1000)  # ms deviation
    return G, (np.std(devs) if devs else 0.0)

Kg, kdev = grid_per_bar(kick_on)
Hg, _ = grid_per_bar(hat_on)
Bg, bdev = grid_per_bar(bass_on)

# --- density / space per bar ---
def bar_rms(sig):
    out = []
    for b in range(nbars):
        seg = sig[int(b*bar*SR):int((b+1)*bar*SR)]
        out.append(np.sqrt(np.mean(seg**2)) if len(seg) else 0)
    r = np.array(out); return r/(r.max()+1e-9)
dens = bar_rms(drums + bass)

# --- report ---
def row(g): return "".join("X" if x else "." for x in g)
spark = " .:-=+*#%@"
def bar_spark(v): return spark[min(len(spark)-1, int(v*(len(spark)-1)))]

print(f"\n  GROOVE (microtiming): kick ±{kdev:.0f}ms, bass ±{bdev:.0f}ms desviación del grid")
uniq_k = len(set(row(Kg[b]) for b in range(nbars)))
print(f"  VOCABULARIO kick: {uniq_k} patrones distintos en {nbars} bars")
print(f"  ESPACIO: {(dens<0.25).sum()} bars casi vacíos (silencios/breaks), {(dens>0.8).sum()} bars de alta energía")

print("\n  GRILLA POR BAR  (K=kick  H=hat  B=bass | densidad)")
print("  bar  kick.............  density")
for b in range(min(nbars, 40)):
    print(f"  {b:3d}  {row(Kg[b])}  {bar_spark(dens[b])}  {row(Bg[b])[:16]}")
if nbars > 40: print(f"  ... (+{nbars-40} bars)")

print(f"\n  densidad completa: {''.join(bar_spark(d) for d in dens)}")
print("\n  -> esta es SU gramática como datos. El siguiente paso: generar desde acá.")
print("  Done.")
