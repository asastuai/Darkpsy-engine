# -*- coding: utf-8 -*-
"""
ENGINE-SAMPLER — the PROVEN engine composition, played with CLONED sounds.

Juan's insight: the v7/v9 engine already composes WELL (ORDER/CHAOS, the 5 musical
drop types, silence-as-a-weapon, fills, humanization). Don't rebuild a cruder
generator — reuse that proven composition and just swap the SOUND SOURCE for the
sampled one-shots cloned from a real track.

= the first-session magic, with the sounds we now have.

  python forja/engine_sampler.py --stems <dir drums.wav,bass.wav> [--bars 64]
Composition: kick + rolling bass + hats from render_v9 (smap, drops, silence,
humanization). Sounds: sliced from the stems. Mix + light master from v9.
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
BPM = 150
BEAT = 60.0/BPM; BAR = BEAT*4; S16 = BEAT/4
TOTAL_BARS = 280
ROOT = 40
rng = np.random.RandomState(666)

ap = argparse.ArgumentParser()
_st = sorted(glob.glob(os.path.join(REPO, "forja", "recreation_out", "*_stems")))
ap.add_argument("--stems", default=(_st[0] if _st else ""))
ap.add_argument("--bars", type=int, default=64)   # render window (engine soul lives in 0-64: intro/order/silence/drop/chaos)
ap.add_argument("--out", default=os.path.join(REPO, "forja", "recreation_out", "sampler", "engine_sampler.wav"))
A = ap.parse_args()
if not A.stems or not os.path.exists(os.path.join(A.stems, "drums.wav")):
    print("  falta --stems (corré style_learn primero)"); sys.exit(1)
os.makedirs(os.path.dirname(A.out), exist_ok=True)

# ================= COMPOSITION (from render_v9 — the proven soul) =================
smap = {}
def ss(s, e, t):
    for b in range(s, min(e, TOTAL_BARS)): smap[b] = t
ss(0,10,'intro'); ss(10,30,'order'); ss(30,31,'silence'); ss(31,33,'drop')
ss(33,42,'chaos'); ss(42,43,'silence'); ss(43,45,'drop'); ss(45,70,'order')
ss(70,71,'silence'); ss(71,73,'drop'); ss(73,88,'chaos'); ss(88,89,'silence')
ss(89,91,'drop'); ss(91,120,'order'); ss(120,122,'silence'); ss(122,124,'drop')
ss(124,148,'chaos'); ss(148,149,'silence'); ss(149,165,'break'); ss(165,175,'build')
ss(175,176,'silence'); ss(176,178,'drop'); ss(178,210,'order'); ss(210,211,'silence')
ss(211,213,'drop'); ss(213,240,'chaos'); ss(240,241,'silence'); ss(241,243,'drop')
ss(243,268,'order'); ss(268,TOTAL_BARS,'outro')
for b in range(TOTAL_BARS): smap.setdefault(b, 'order')
def sec(b): return smap.get(b, 'order')

def drop_gradual(): return [(0.0,.6),(1.5,.5),(2.0,.7),(2.5,.65),(3.0,.8),(3.5,.75),(3.75,.85),(4.0,.95),(5.0,.9),(6.0,.9),(7.0,.85)]
def drop_dramatic(): return [(0.0,1.0),(2.0,.75),(3.0,.8),(3.5,.85),(3.75,.9),(4.0,.95),(5.0,.9),(6.0,.9),(7.0,.85)]
def drop_stutter(): return [(0.0,.85),(0.25,.6),(1.0,.8),(1.75,.5),(2.0,.85),(2.5,.7),(3.0,.9),(3.5,.8),(4.0,.9),(5.0,.85),(6.0,.85),(7.0,.85)]
def drop_rolling(): return [(0.0,.7),(1.0,.75),(2.0,.8),(2.5,.7),(3.0,.85),(3.25,.6),(3.5,.9),(3.75,.7),(4.0,.95),(5.0,.9),(6.0,.9),(7.0,.85)]
def drop_triplet(): return [(0.0,.8),(0.667,.6),(1.333,.7),(2.0,.85),(2.667,.65),(3.333,.8),(3.667,.7),(4.0,.95),(5.0,.9),(6.0,.9),(7.0,.85)]
DROP_TYPES = [drop_gradual, drop_dramatic, drop_stutter, drop_rolling, drop_triplet]
drop_moments = {}; di = 0
for b in range(TOTAL_BARS):
    if sec(b) == 'drop' and (b == 0 or sec(b-1) != 'drop'):
        drop_moments[b] = DROP_TYPES[di % len(DROP_TYPES)]; di += 1

def gen_kick_midi():
    ev = []; cps = [[0,1.5,2,3,3.5],[0,0.75,2,2.75,3.5],[0,1,2,2.5,3,3.75],[0,0.5,1.5,2,3],[0,1,1.75,2.5,3,3.25,3.75],[0,2,2.25,3,3.5,3.75]]
    for bar in range(TOTAL_BARS):
        s = sec(bar)
        if s in ('silence','break','intro'): continue
        if s == 'drop':
            db = bar
            while db > 0 and sec(db-1) == 'drop': db -= 1
            bid = bar - db
            if db in drop_moments:
                for bp, vel in drop_moments[db]():
                    tb = int(bp//4)
                    if tb != bid: continue
                    t = bar*BAR + (bp-tb*4)*BEAT + rng.normal(0,0.003)
                    ev.append((max(0,t), vel))
            continue
        if s == 'order':
            for beat in range(4):
                if beat and rng.random() < 0.02: continue
                ev.append((max(0, bar*BAR+beat*BEAT+rng.normal(0,0.002)), 0.80+rng.random()*0.15))
            if bar+1 < TOTAL_BARS and sec(bar+1) == 'silence':
                for fp,fv in [(2.25,.6),(2.75,.7),(3.25,.75),(3.5,.8),(3.625,.7),(3.75,.85),(3.875,.9)]:
                    ev.append((bar*BAR+fp*BEAT, fv))
        elif s == 'chaos':
            for bp in cps[bar % len(cps)]:
                ev.append((max(0, bar*BAR+bp*BEAT+rng.normal(0,0.004)), 0.6+rng.random()*0.35))
        elif s == 'build':
            bs = bar
            while bs > 0 and sec(bs-1) == 'build': bs -= 1
            be = bar
            while be < TOTAL_BARS and sec(be) == 'build': be += 1
            prog = (bar-bs)/max(be-bs,1)
            beats = [0,2] if prog < 0.3 else ([0,1,2,3] if prog < 0.6 else [0,1,2,2.5,3,3.5])
            for bp in beats: ev.append((max(0, bar*BAR+bp*BEAT+rng.normal(0,0.003)), 0.6+prog*0.3))
    return ev

def gen_bass_midi():
    ev = []; op = [[0]*16,[0,0,4,0,0,0,4,0,0,0,0,0,0,0,4,0],[0,0,0,0,0,0,4,0,0,0,0,0,0,0,7,0]]
    cp = [[0,0,1,0,0,0,4,0,0,0,1,0,0,4,0,0],[0,0,0,4,0,0,0,0,0,0,4,0,0,0,0,4]]
    for bar in range(TOTAL_BARS):
        s = sec(bar)
        if s in ('silence','break','intro') or bar < 6: continue
        if s == 'drop': pat = [0]*16
        elif s == 'order': pat = op[bar % len(op)]
        elif s == 'chaos':
            pat = list(cp[bar % len(cp)])
            for i in range(16):
                if rng.random() < 0.12: pat[i] = rng.choice([0,1,4,5,7])
        else: pat = op[0]
        for step in range(16):
            if s == 'chaos' and rng.random() < 0.12: continue
            note = ROOT + pat[step % len(pat)]
            vel = 0.7 + 0.25*(step % 4 == 0) + rng.uniform(-0.05,0.05)
            t = bar*BAR + step*S16 + (0.03 if step % 4 == 0 else 0) + rng.normal(0,0.002)
            ev.append((max(0,t), note, vel))
    return ev

def gen_hats():
    ev = []
    for bar in range(TOTAL_BARS):
        s = sec(bar)
        if s in ('silence','break','intro') or bar < 10: continue
        c = 1.0 if s == 'chaos' else 0.0
        for step in range(16):
            if step % 4 == 2 and rng.random() < (0.95 if c < .3 else max(.3,.95-c*.6)):
                ev.append((bar*BAR+step*S16+rng.normal(0,0.003), 0.9, rng.uniform(-.15,.15)))
            elif step % 2 == 1 and rng.random() < (.5-c*.2):
                ev.append((bar*BAR+step*S16+rng.normal(0,0.003), 0.5, rng.uniform(-.4,.4)))
    return ev

# ================= SOUNDS (cloned from the stems) =================
def lp(x, fc): return sosfilt(butter(2, fc, btype="low", fs=SR, output="sos"), x)
def hp(x, fc): return sosfilt(butter(2, fc, btype="high", fs=SR, output="sos"), x)
def loadm(p):
    sr, d = wavfile.read(p)
    if d.dtype == np.int16: d = d.astype(np.float64)/32768.0
    elif d.dtype == np.int32: d = d.astype(np.float64)/2147483648.0
    else: d = d.astype(np.float64)
    return d.mean(axis=1) if d.ndim > 1 else d
def grab(sig, on_sig, ms, fade=8):
    on = librosa.onset.onset_detect(y=on_sig.astype(np.float32), sr=SR, units="samples", backtrack=True)
    if len(on) == 0: on = [int(np.argmax(np.abs(on_sig)))]
    n = int(ms/1000*SR); best = max(on, key=lambda s: np.sum(sig[s:s+n]**2))
    shot = sig[best:best+n].copy()
    if len(shot) < n: shot = np.pad(shot, (0, n-len(shot)))
    f = int(fade/1000*SR); shot[:f] *= np.linspace(0,1,f); shot[-f:] *= np.linspace(1,0,f)
    return shot/(np.max(np.abs(shot))+1e-9)

drums = loadm(os.path.join(A.stems, "drums.wav"))
bass = loadm(os.path.join(A.stems, "bass.wav"))
print(f"  sonidos de: {os.path.basename(A.stems)}")
kick_shot = grab(drums, lp(drums,160), 300)
try:
    hat_shot = grab(drums, hp(drums,6000), 80, 4)
    if np.max(np.abs(hat_shot)) < 1e-3: hat_shot = None
except Exception: hat_shot = None
benv = np.abs(librosa.feature.rms(y=bass.astype(np.float32))[0]); loud = int(np.argmax(benv))*512
bshot = bass[loud:loud+int(BEAT*SR)].copy()
if len(bshot) < int(BEAT*SR): bshot = np.pad(bshot, (0, int(BEAT*SR)-len(bshot)))
fb = int(0.008*SR); bshot[:fb]*=np.linspace(0,1,fb); bshot[-fb:]*=np.linspace(1,0,fb)
bshot /= (np.max(np.abs(bshot))+1e-9)
# pre-render bass at the semitone shifts the engine uses (relative to ROOT)
bass_cache = {}
def bass_at(note):
    sh = int(note - ROOT)
    if sh not in bass_cache:
        bass_cache[sh] = librosa.effects.pitch_shift(bshot.astype(np.float32), sr=SR, n_steps=float(sh)).astype(np.float64) if sh != 0 else bshot
    return bass_cache[sh]

# ================= RENDER with samples =================
RB = min(A.bars, TOTAL_BARS)
total = int(RB*BAR*SR) + SR
kL=np.zeros(total); kR=np.zeros(total); bL=np.zeros(total); bR=np.zeros(total); hL=np.zeros(total); hR=np.zeros(total)
def place(L,R,shot,t,g,pan=0.0):
    pos=int(t*SR); e=min(pos+len(shot),total); n=e-pos
    if n>0 and pos>=0:
        L[pos:e]+=shot[:n]*g*(1-pan)*0.5*2; R[pos:e]+=shot[:n]*g*(1+pan)*0.5*2

for t,vel in gen_kick_midi():
    if t < RB*BAR: place(kL,kR,kick_shot,t,0.95*vel)
for t,note,vel in gen_bass_midi():
    if t < RB*BAR:
        seg = bass_at(note)[:int(S16*0.9*SR)]
        place(bL,bR,seg,t,0.8*vel)
if hat_shot is not None:
    for t,vel,pan in gen_hats():
        if t < RB*BAR: place(hL,hR,hat_shot,t,0.28*vel,pan)

# mix (v9 faders-ish) + sidechain + light master
mL = kL*0.95 + bL*0.85 + hL*0.5
mR = kR*0.95 + bR*0.85 + hR*0.5
# simple sidechain: duck non-kick by kick envelope
ke = np.abs(kL+kR)/2; w = int(0.03*SR); ks = np.convolve(ke, np.ones(w)/w, mode='same'); ks /= (ks.max()+1e-9)
sc = 1 - ks*0.18
mL = kL*0.95 + (mL-kL*0.95)*sc
mR = kR*0.95 + (mR-kR*0.95)*sc
def ws(x,a=1.7): return np.tanh(x*a)/np.tanh(a)
mL = sosfilt(butter(2,28,btype='high',fs=SR,output='sos'), mL)
mR = sosfilt(butter(2,28,btype='high',fs=SR,output='sos'), mR)
mL = ws(mL); mR = ws(mR)
pk = max(np.max(np.abs(mL)), np.max(np.abs(mR)))+1e-9
mL=mL/pk*0.97; mR=mR/pk*0.97
wavfile.write(A.out, SR, np.column_stack([(mL*32767).astype(np.int16),(mR*32767).astype(np.int16)]))
print(f"  -> {A.out}  ({total/SR:.0f}s, {RB} bars del engine probado, sonidos calcados)")
print("  composición v7/v9 (ORDEN/CAOS/silencio/drops/humanización) + sonidos del track.")
