# -*- coding: utf-8 -*-
"""
Re-render the BASS stem cleanly.

The full render_v9 run produced a corrupt bass.wav: KranchDD's feedback filter
blew up to inf on the bass input, and inf/inf -> NaN propagated into the saved
stem (RMS -240 dB = dead). Acid (also KranchDD) survived; only bass broke.

This re-renders bass through Surge XT, applies a SANITIZED KranchDD pass
(nan_to_num + clip), and if the wet signal is still degenerate, falls back to a
clean Surge bass with a tanh drive so it always produces a usable stem.
"""
import os, sys
import numpy as np
from scipy.io import wavfile
from pedalboard import load_plugin

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

SR = 44100
BPM = 150
BEAT = 60.0 / BPM
BAR = BEAT * 4
S16 = BEAT / 4
TOTAL_BARS = 280
TOTAL_TIME = TOTAL_BARS * BAR
TOTAL_SAMPLES = int(TOTAL_TIME * SR)
ROOT = 40

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STEMS_DIR = os.path.join(REPO, "stems_v9")
SURGE_PATH = 'C:/Program Files/Common Files/VST3/Surge Synth Team/Surge XT.vst3/Contents/x86_64-win/Surge XT.vst3'
KRANCHDD_PATH = 'C:/Program Files/Common Files/VST3/KINDZAudio/KranchDD.vst3'

sys.path.insert(0, REPO)
from surge_presets import configure_bass

rng = np.random.RandomState(666)

# --- section map (from render_v9) ---
smap = {}
def ss(s, e, t):
    for b in range(s, min(e, TOTAL_BARS)): smap[b] = t
ss(0,10,'intro'); ss(10,30,'order'); ss(30,31,'silence'); ss(31,33,'drop')
ss(33,42,'chaos'); ss(42,43,'silence'); ss(43,45,'drop'); ss(45,70,'order')
ss(70,71,'silence'); ss(71,73,'drop'); ss(73,88,'chaos'); ss(88,89,'silence')
ss(89,91,'drop'); ss(91,120,'order'); ss(120,122,'silence'); ss(122,124,'drop')
ss(124,148,'chaos'); ss(148,149,'silence'); ss(149,165,'break')
ss(165,175,'build'); ss(175,176,'silence'); ss(176,178,'drop')
ss(178,210,'order'); ss(210,211,'silence'); ss(211,213,'drop')
ss(213,240,'chaos'); ss(240,241,'silence'); ss(241,243,'drop')
ss(243,268,'order'); ss(268,TOTAL_BARS,'outro')
for b in range(TOTAL_BARS):
    if b not in smap: smap[b] = 'order'
def sec(b): return smap.get(b, 'order')

# --- bass MIDI (copied from render_v9.gen_bass_midi) ---
def gen_bass_midi():
    events = []
    order_pats = [[0]*16, [0,0,4,0,0,0,4,0,0,0,0,0,0,0,4,0], [0,0,0,0,0,0,4,0,0,0,0,0,0,0,7,0]]
    chaos_pats = [[0,0,1,0,0,0,4,0,0,0,1,0,0,4,0,0],[0,0,0,4,0,0,0,0,0,0,4,0,0,0,0,4]]
    drop_pat = [0]*16
    for bar in range(TOTAL_BARS):
        s = sec(bar)
        if s in ('silence','break','intro'): continue
        if bar < 6: continue
        if s == 'drop': pat = drop_pat
        elif s == 'order': pat = order_pats[bar % len(order_pats)]
        elif s == 'chaos':
            pat = list(chaos_pats[bar % len(chaos_pats)])
            for i in range(16):
                if rng.random() < 0.12: pat[i] = rng.choice([0,1,4,5,7])
        else: pat = order_pats[0]
        for step in range(16):
            if s == 'chaos' and rng.random() < 0.12: continue
            if s == 'outro' and bar - 268 > 8 and step % 4 != 0: continue
            note = ROOT + pat[step % len(pat)]
            vel = 0.7 + 0.25 * (step % 4 == 0) + rng.uniform(-0.05, 0.05)
            delay = 0.03 if step % 4 == 0 else 0
            t = bar * BAR + step * S16 + delay + rng.normal(0, 0.002)
            events.append((max(0, t), note, int(vel * 127), S16 * 0.82))
    return events

def midi_to_pb(events):
    pb = []
    for t, note, vel, dur in events:
        pb.append((bytes([0x90, note, vel]), t))
        pb.append((bytes([0x80, note, 0]), t + dur))
    pb.sort(key=lambda x: x[1])
    return pb

def safe(x):
    return np.nan_to_num(np.asarray(x, dtype=np.float64), nan=0.0, posinf=0.0, neginf=0.0)

print("Re-rendering bass through Surge XT...")
surge = load_plugin(SURGE_PATH)
configure_bass(surge)
events = gen_bass_midi()
result = surge(midi_to_pb(events), duration=TOTAL_TIME, sample_rate=SR, num_channels=2)
L = safe(result[0]); R = safe(result[1])
raw_rms = float(np.sqrt(np.mean(L**2 + R**2) / 2))
print(f"  Surge raw RMS: {20*np.log10(raw_rms+1e-12):.1f} dB  peak {20*np.log10(max(np.max(np.abs(L)),np.max(np.abs(R)))+1e-12):.1f} dB")

# --- sanitized KranchDD pass ---
def kranchdd_safe(L, R, wet=0.4):
    preset = {'flt': 4000.0, 'dst': 0.5, 'mix': 1.0, 'qm': 6.0, 'morph': 0.3,
              'feedback': 0.15, 'inn': 2.0, 'ouu': 1.0, 'wtf': 0.05, 'type': 4.0,
              'chain': 1.0, 'clip': 0.4, 'overx': 1.0, 'bypass': False}
    k = load_plugin(KRANCHDD_PATH)
    for key, val in preset.items():
        if hasattr(k, key): setattr(k, key, val)
    stereo = np.array([L.astype(np.float32), R.astype(np.float32)])
    pk = float(np.max(np.abs(stereo)))
    if pk <= 0: return L, R
    stn = stereo / pk * 0.7
    wet_sig = safe(k(stn, SR))                      # <-- sanitize KranchDD output
    wet_pk = float(np.max(np.abs(wet_sig)))
    if not np.isfinite(wet_pk) or wet_pk <= 0.001:
        print("  KranchDD wet degenerate -> fallback to Surge+drive")
        return None, None
    wet_sig = wet_sig / wet_pk * pk * 0.7
    out = stn * pk / 0.7 * (1 - wet) + wet_sig * wet
    return safe(out[0]), safe(out[1])

bL, bR = kranchdd_safe(L, R, wet=0.4)
if bL is None:
    # fallback: clean Surge bass with gentle tanh drive for character
    drive = 1.8
    bL = np.tanh(L * drive) / np.tanh(drive)
    bR = np.tanh(R * drive) / np.tanh(drive)
else:
    print("  KranchDD applied (sanitized).")

bL = safe(bL); bR = safe(bR)
out_rms = float(np.sqrt(np.mean(bL**2 + bR**2) / 2))
print(f"  Final bass RMS: {20*np.log10(out_rms+1e-12):.1f} dB")

# save (same normalize-to-0.9 convention as render_v9)
pk = max(np.max(np.abs(bL)), np.max(np.abs(bR)), 1e-10)
stereo = np.column_stack([(bL/pk*0.9*32767).astype(np.int16),
                           (bR/pk*0.9*32767).astype(np.int16)])
out_path = os.path.join(STEMS_DIR, "bass.wav")
wavfile.write(out_path, SR, stereo)
print(f"  Saved: {out_path}")
