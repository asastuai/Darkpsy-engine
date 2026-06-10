# -*- coding: utf-8 -*-
"""
MOTOR-SAMPLER — "fórmula nueva con sonidos calcados".

The convergence of the project: take a track's SEPARATED stems, slice out its
REAL sounds (kick / hat / bass one-shots), read its BPM + root, then let the
DarkPsy generative engine (ORDER/CHAOS/DROPS) compose a BRAND-NEW arrangement
that TRIGGERS those cloned samples. Output is genuinely new music — new patterns,
new structure — but in the original's actual sounds, key and tempo.

This is NOT the jukebox (which only re-orders the original). This INVENTS.

v1 = rhythm section (kick + hat + rolling bass), the reliably-extractable layer.

Run:
  python forja/motor_sampler.py [--kick wav] [--drums wav] [--bass wav] [--bars N]
Defaults use stems_v9/ (a clean proof). Point --kick/--drums/--bass at a
recreations/<id>/ folder to compose with a real track's cloned sounds.
"""
import os, sys, argparse
import numpy as np
import librosa
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 44100

ap = argparse.ArgumentParser()
ap.add_argument("--kick", default=os.path.join(REPO, "stems_v9", "kick.wav"))
ap.add_argument("--drums", default=os.path.join(REPO, "stems_v9", "drums.wav"))
ap.add_argument("--bass", default=os.path.join(REPO, "stems_v9", "bass.wav"))
ap.add_argument("--bars", type=int, default=32)
ap.add_argument("--seed", type=int, default=7)
ap.add_argument("--out", default=os.path.join(REPO, "forja", "recreation_out", "sampler", "new_arrangement.wav"))
A = ap.parse_args()
os.makedirs(os.path.dirname(A.out), exist_ok=True)
rng = np.random.RandomState(A.seed)


def load_mono(path):
    sr, d = wavfile.read(path)
    if d.dtype == np.int16: d = d.astype(np.float64) / 32768.0
    elif d.dtype == np.int32: d = d.astype(np.float64) / 2147483648.0
    else: d = d.astype(np.float64)
    if d.ndim > 1: d = d.mean(axis=1)
    if sr != SR: d = librosa.resample(d.astype(np.float32), orig_sr=sr, target_sr=SR).astype(np.float64)
    return d

def lp(x, fc): return sosfilt(butter(2, fc, btype="low", fs=SR, output="sos"), x)
def hp(x, fc): return sosfilt(butter(2, fc, btype="high", fs=SR, output="sos"), x)

def grab_oneshot(sig, onset_sig, ms, fade_ms=8):
    """Extract a one-shot at the strongest onset of onset_sig from sig."""
    on = librosa.onset.onset_detect(y=onset_sig.astype(np.float32), sr=SR, units="samples", backtrack=True)
    if len(on) == 0:
        on = [int(np.argmax(np.abs(onset_sig)))]
    n = int(ms / 1000 * SR)
    best, bestE = on[0], -1
    for s in on:
        e = np.sum(sig[s:s + n] ** 2)
        if e > bestE: bestE, best = e, s
    shot = sig[best:best + n].copy()
    if len(shot) < n: shot = np.pad(shot, (0, n - len(shot)))
    f = int(fade_ms / 1000 * SR)
    shot[-f:] *= np.linspace(1, 0, f)
    shot[:f] *= np.linspace(0, 1, f)
    pk = np.max(np.abs(shot)) + 1e-9
    return shot / pk

print("=" * 60)
print(" MOTOR-SAMPLER — fórmula nueva con sonidos calcados")
print("=" * 60)

# --- slice REAL sounds ---
drums = load_mono(A.drums)
kick_src = load_mono(A.kick)
bass_src = load_mono(A.bass)

kick_shot = grab_oneshot(kick_src, lp(kick_src, 160), ms=320)
try:
    hat_shot = grab_oneshot(drums, hp(drums, 6000), ms=90, fade_ms=4)
    if np.max(np.abs(hat_shot)) < 1e-3: hat_shot = None
except Exception:
    hat_shot = None
print(f"  kick one-shot: {len(kick_shot)/SR*1000:.0f}ms   hat: {'sí' if hat_shot is not None else 'no'}")

# --- bass one-shot + its base pitch ---
benv = np.abs(librosa.feature.rms(y=bass_src.astype(np.float32))[0])
beat_len = int(0.4 * SR)  # ~one beat at 150
loud = int(np.argmax(benv)) * 512
bseg = bass_src[loud:loud + beat_len]
if len(bseg) < beat_len: bseg = np.pad(bseg, (0, beat_len - len(bseg)))
f0 = librosa.yin(bseg.astype(np.float32), fmin=28, fmax=400, sr=SR)
base_hz = float(np.median(f0[np.isfinite(f0)])) if np.any(np.isfinite(f0)) else 82.4
base_midi = librosa.hz_to_midi(base_hz)
fb = int(0.01 * SR)
bseg[:fb] *= np.linspace(0, 1, fb); bseg[-fb:] *= np.linspace(1, 0, fb)
bseg /= (np.max(np.abs(bseg)) + 1e-9)
print(f"  bass one-shot: base ~{base_hz:.1f}Hz (MIDI {base_midi:.1f})")

# --- BPM (from drums) ---
tempo, _ = librosa.beat.beat_track(y=drums.astype(np.float32), sr=SR, start_bpm=145)
BPM = float(np.atleast_1d(tempo)[0])
BPM = min(max(BPM, 138), 160)
BEAT = 60.0 / BPM; BAR = BEAT * 4; S16 = BEAT / 4
print(f"  BPM ~{BPM:.0f}   componiendo {A.bars} bars NUEVOS...")

# pre-render bass at the scale offsets we use (cheap + fast)
SCALE = [0, 1, 4, 5, 7]  # E Phrygian-ish degrees
bass_cache = {}
for off in SCALE:
    bass_cache[off] = librosa.effects.pitch_shift(bseg.astype(np.float32), sr=SR, n_steps=float(off)).astype(np.float64)

# --- GENERATE A NEW ARRANGEMENT (engine logic, not the original's pattern) ---
def sec(b):
    if b % 16 == 15: return "drop"
    return "chaos" if (b // 8) % 2 == 1 else "order"

order_pats = [[0]*16, [0,0,4,0,0,0,4,0,0,0,0,0,0,0,4,0], [0,0,0,0,0,0,4,0,0,0,0,0,0,0,7,0]]
chaos_pats = [[0,0,1,0,0,0,4,0,0,0,1,0,0,4,0,0], [0,0,0,4,0,0,0,0,0,0,4,0,0,0,0,4]]
chaos_kick = [[0,1.5,2,3,3.5],[0,0.75,2,2.75,3.5],[0,1,2,2.5,3,3.75],[0,0.5,1.5,2,3]]

total = int(A.bars * BAR * SR) + SR
outL = np.zeros(total); outR = np.zeros(total)
def place(buf, shot, pos, g=1.0, pan=0.0):
    e = min(pos + len(shot), len(buf)); n = e - pos
    if n > 0 and pos >= 0: buf[pos:e] += shot[:n] * g

kick_ev = bass_ev = hat_ev = 0
for bar in range(A.bars):
    s = sec(bar)
    # KICK
    if s == "order":
        for beat in range(4):
            if beat and rng.random() < 0.03: continue
            t = bar*BAR + beat*BEAT + rng.normal(0, 0.002)
            place(outL, kick_shot, int(t*SR), 0.95); place(outR, kick_shot, int(t*SR), 0.95); kick_ev += 1
    elif s == "chaos":
        for bp in chaos_kick[bar % len(chaos_kick)]:
            t = bar*BAR + bp*BEAT + rng.normal(0, 0.004)
            place(outL, kick_shot, int(t*SR), 0.9); place(outR, kick_shot, int(t*SR), 0.9); kick_ev += 1
    else:  # drop: gradual re-entry
        for bp, v in [(0,.6),(1.5,.5),(2,.7),(2.5,.65),(3,.8),(3.5,.75),(3.75,.9)]:
            t = bar*BAR + bp*BEAT
            place(outL, kick_shot, int(t*SR), v); place(outR, kick_shot, int(t*SR), v); kick_ev += 1
    # BASS (rolling 1/16, skips the kick downbeats feel)
    if s != "drop":
        pat = order_pats[bar % len(order_pats)] if s == "order" else list(chaos_pats[bar % len(chaos_pats)])
        for step in range(16):
            if s == "chaos" and rng.random() < 0.12: continue
            off = pat[step % len(pat)]
            t = bar*BAR + step*S16 + (0.03 if step % 4 == 0 else 0)
            g = 0.5 + 0.2*(step % 4 == 0)
            shot = bass_cache[off if off in bass_cache else 0]
            dur = int(S16*0.9*SR); seg = shot[:dur]
            place(outL, seg, int(t*SR), g); place(outR, seg, int(t*SR), g); bass_ev += 1
    # HAT offbeats
    if hat_shot is not None and s != "drop":
        for step in range(16):
            if step % 4 == 2 and rng.random() < 0.9:
                t = bar*BAR + step*S16 + rng.normal(0, 0.003)
                pan = rng.uniform(-.2, .2)
                place(outL, hat_shot, int(t*SR), 0.25*(1-pan)); place(outR, hat_shot, int(t*SR), 0.25*(1+pan)); hat_ev += 1

print(f"  eventos generados: {kick_ev} kicks, {bass_ev} bass, {hat_ev} hats")

# --- light master ---
def ws(x, a=1.6): return np.tanh(x*a)/np.tanh(a)
outL = ws(outL); outR = ws(outR)
pk = max(np.max(np.abs(outL)), np.max(np.abs(outR))) + 1e-9
outL = outL/pk*0.97; outR = outR/pk*0.97
stereo = np.column_stack([(outL*32767).astype(np.int16), (outR*32767).astype(np.int16)])
wavfile.write(A.out, SR, stereo)
print(f"\n  -> {A.out}   ({total/SR:.0f}s, arreglo NUEVO con sonidos del original)")
print("  Done.")
