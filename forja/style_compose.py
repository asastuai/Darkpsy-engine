# -*- coding: utf-8 -*-
"""
STYLE-COMPOSE — generate a NEW arrangement from the ARTIST's own grammar.

Closes the "abismo": instead of our generic engine patterns, it uses the track's
OWN vocabulary — his kick patterns, his bass rhythms, his density/build arc, his
groove — recombined into a new arrangement, played with his cloned sounds.

  python forja/style_compose.py --stems <dir with drums.wav,bass.wav> [--bpm N] [--bars N]
Reuses the cached stems from style_learn (recreation_out/<name>_stems/).
"""
import os, sys, glob, argparse
import numpy as np
import librosa
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 44100
rng = np.random.RandomState(7)

ap = argparse.ArgumentParser()
default_stems = sorted(glob.glob(os.path.join(REPO, "forja", "recreation_out", "*_stems")))
ap.add_argument("--stems", default=(default_stems[0] if default_stems else ""))
ap.add_argument("--bpm", type=float, default=0.0)
ap.add_argument("--bars", type=int, default=48)
ap.add_argument("--out", default=os.path.join(REPO, "forja", "recreation_out", "sampler", "style_compose.wav"))
A = ap.parse_args()
if not A.stems or not os.path.exists(os.path.join(A.stems, "drums.wav")):
    print("  falta --stems <dir con drums.wav,bass.wav> (corré style_learn primero)"); sys.exit(1)
os.makedirs(os.path.dirname(A.out), exist_ok=True)

def lp(x, fc): return sosfilt(butter(2, fc, btype="low", fs=SR, output="sos"), x)
def hp(x, fc): return sosfilt(butter(2, fc, btype="high", fs=SR, output="sos"), x)
def loadm(p):
    sr, d = wavfile.read(p)
    if d.dtype == np.int16: d = d.astype(np.float64)/32768.0
    elif d.dtype == np.int32: d = d.astype(np.float64)/2147483648.0
    else: d = d.astype(np.float64)
    return d.mean(axis=1) if d.ndim > 1 else d

drums = loadm(os.path.join(A.stems, "drums.wav"))
bass = loadm(os.path.join(A.stems, "bass.wav"))
N = min(len(drums), len(bass)); drums, bass = drums[:N], bass[:N]

# --- tempo (kick-IOI) ---
kick_on = librosa.onset.onset_detect(y=lp(drums, 160).astype(np.float32), sr=SR, units="time", backtrack=True)
bass_on = librosa.onset.onset_detect(y=bass.astype(np.float32), sr=SR, units="time", backtrack=True)
hat_on = librosa.onset.onset_detect(y=hp(drums, 6000).astype(np.float32), sr=SR, units="time", backtrack=True)
if A.bpm > 0:
    bpm = A.bpm
else:
    d = np.diff(kick_on); d = d[(d > 0.30) & (d < 0.52)]
    bpm = 60.0/float(np.median(d)) if len(d) >= 8 else 150.0
beat = 60.0/bpm; bar = beat*4; s16 = beat/4
nbars = int(N/SR/bar)
print(f"  fuente: {os.path.basename(A.stems)}  BPM {bpm:.1f}  {nbars} bars")

# --- extract HIS grammar: per-bar grids + density ---
def grid(onsets):
    G = np.zeros((nbars, 16), int)
    for t in onsets:
        b = int(t // bar)
        if 0 <= b < nbars: G[b, int(round((t - b*bar)/s16)) % 16] = 1
    return G
Kg, Bg, Hg = grid(kick_on), grid(bass_on), grid(hat_on)
def bar_rms(sig):
    r = np.array([np.sqrt(np.mean(sig[int(b*bar*SR):int((b+1)*bar*SR)]**2) or 0) for b in range(nbars)])
    return r/(r.max()+1e-9)
dens = bar_rms(drums + bass)

# his vocabulary = the kick/bass patterns from bars with real energy
kick_vocab = [Kg[b] for b in range(nbars) if dens[b] > 0.3 and Kg[b].sum() > 0]
bass_vocab = [Bg[b] for b in range(nbars) if dens[b] > 0.3 and Bg[b].sum() > 0]
hat_vocab = [Hg[b] for b in range(nbars) if Hg[b].sum() > 0]
print(f"  vocabulario: {len(kick_vocab)} kicks, {len(bass_vocab)} bass, {len(hat_vocab)} hats")
if not kick_vocab or not bass_vocab:
    print("  vocabulario insuficiente"); sys.exit(1)

def pick_by_density(vocab, target):
    """choose a pattern whose hit-count best matches the target density."""
    want = max(1, int(target * 8))   # 0..8-ish hits
    vocab = sorted(vocab, key=lambda g: abs(int(g.sum()) - want))
    k = min(len(vocab), 4)
    return vocab[rng.randint(k)]

# --- slice cloned one-shots ---
def grab(sig, onset_sig, ms, fade=8):
    on = librosa.onset.onset_detect(y=onset_sig.astype(np.float32), sr=SR, units="samples", backtrack=True)
    if len(on) == 0: on = [int(np.argmax(np.abs(onset_sig)))]
    n = int(ms/1000*SR)
    best = max(on, key=lambda s: np.sum(sig[s:s+n]**2))
    shot = sig[best:best+n].copy()
    if len(shot) < n: shot = np.pad(shot, (0, n-len(shot)))
    f = int(fade/1000*SR); shot[:f] *= np.linspace(0,1,f); shot[-f:] *= np.linspace(1,0,f)
    return shot/(np.max(np.abs(shot))+1e-9)
kick_shot = grab(drums, lp(drums,160), 320)
try:
    hat_shot = grab(drums, hp(drums,6000), 90, 4)
    if np.max(np.abs(hat_shot)) < 1e-3: hat_shot = None
except Exception: hat_shot = None
# bass one-shot
benv = np.abs(librosa.feature.rms(y=bass.astype(np.float32))[0]); loud = int(np.argmax(benv))*512
bshot = bass[loud:loud+int(s16*SR)].copy()
if len(bshot) < int(s16*SR): bshot = np.pad(bshot, (0, int(s16*SR)-len(bshot)))
fb = int(0.008*SR); bshot[:fb]*=np.linspace(0,1,fb); bshot[-fb:]*=np.linspace(1,0,fb)
bshot /= (np.max(np.abs(bshot))+1e-9)

# --- compose: follow HIS density arc, using HIS patterns + groove ---
GROOVE_MS = 18
total = int(A.bars*bar*SR)+SR
outL = np.zeros(total); outR = np.zeros(total)
def place(buf, shot, t, g=1.0):
    pos = int(t*SR); e = min(pos+len(shot), len(buf)); n = e-pos
    if n > 0 and pos >= 0: buf[pos:e] += shot[:n]*g
# build a density arc: replay his shape stretched to A.bars
arc = np.interp(np.linspace(0, len(dens)-1, A.bars), np.arange(len(dens)), dens)
kc = bc = hc = 0
for b in range(A.bars):
    td = arc[b]
    kp = pick_by_density(kick_vocab, td)
    bp = pick_by_density(bass_vocab, td)
    hp_ = hat_vocab[rng.randint(len(hat_vocab))] if hat_vocab else np.zeros(16, int)
    for s in range(16):
        gr = rng.normal(0, GROOVE_MS/1000)
        t0 = b*bar + s*s16 + gr
        if kp[s]: place(outL, kick_shot, t0, 0.95); place(outR, kick_shot, t0, 0.95); kc += 1
        if bp[s]:
            g = 0.55 + 0.15*(s % 4 == 0); seg = bshot[:int(s16*0.95*SR)]
            place(outL, seg, t0, g); place(outR, seg, t0, g); bc += 1
        if hat_shot is not None and hp_[s] and td > 0.35:
            pan = rng.uniform(-.2,.2)
            place(outL, hat_shot, t0, 0.22*(1-pan)); place(outR, hat_shot, t0, 0.22*(1+pan)); hc += 1
print(f"  arreglo NUEVO: {A.bars} bars, {kc} kicks/{bc} bass/{hc} hats, siguiendo SU curva de densidad")

def ws(x, a=1.6): return np.tanh(x*a)/np.tanh(a)
outL, outR = ws(outL), ws(outR)
pk = max(np.max(np.abs(outL)), np.max(np.abs(outR)))+1e-9
outL, outR = outL/pk*0.97, outR/pk*0.97
wavfile.write(A.out, SR, np.column_stack([(outL*32767).astype(np.int16), (outR*32767).astype(np.int16)]))
print(f"\n  -> {A.out}  ({total/SR:.0f}s)")
print("  patrones de ÉL + densidad de ÉL + groove de ÉL + sonidos de ÉL.")
