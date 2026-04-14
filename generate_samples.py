"""
SAMPLE GENERATOR — 15 full tracks with different preset combinations.
Uses the v7 composition engine + factory Surge XT presets.
Each track gets a random combination of presets from the audition winners.
"""

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt
from pedalboard import load_plugin
import os, sys, glob, random

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

SR = 44100
BPM = 150
BEAT = 60.0 / BPM
BAR = BEAT * 4
S16 = BEAT / 4
# Shorter version for samples: 80 bars ~ 2 min (enough to hear the vibe)
TOTAL_BARS = 80
TOTAL_TIME = TOTAL_BARS * BAR
TOTAL_SAMPLES = int(TOTAL_TIME * SR)

SURGE_PATH = 'C:/Program Files/Common Files/VST3/Surge Synth Team/Surge XT.vst3/Contents/x86_64-win/Surge XT.vst3'
PRESETS_BASE = 'C:/ProgramData/Surge XT'
OUTPUT_DIR = 'C:/Users/Juan/Desktop/samples'
os.makedirs(OUTPUT_DIR, exist_ok=True)

ROOT = 40
rng = random.Random(42)
np_rng = np.random.RandomState(666)

print("=" * 60)
print(" SAMPLE GENERATOR — 15 tracks, different preset combos")
print(f" BPM: {BPM} | Bars: {TOTAL_BARS} | Duration: {TOTAL_TIME/60:.1f} min each")
print("=" * 60)


# ============================================================
# SECTION MAP (shortened version)
# ============================================================
smap = {}
def ss(s, e, t):
    for b in range(s, min(e, TOTAL_BARS)): smap[b] = t

ss(0, 4, 'intro')
ss(4, 20, 'order')
ss(20, 21, 'silence')
ss(21, 23, 'drop')
ss(23, 35, 'chaos')
ss(35, 36, 'silence')
ss(36, 38, 'drop')
ss(38, 58, 'order')
ss(58, 59, 'silence')
ss(59, 61, 'drop')
ss(61, 73, 'chaos')
ss(73, 74, 'silence')
ss(74, 76, 'drop')
ss(76, TOTAL_BARS, 'order')
for b in range(TOTAL_BARS):
    if b not in smap: smap[b] = 'order'
def sec(b): return smap.get(b, 'order')

# Drop patterns
def drop_gradual():
    return [(0.0,.6),(1.5,.5),(2.0,.7),(2.5,.65),(3.0,.8),(3.5,.75),(3.75,.85),
            (4.0,.95),(5.0,.9),(6.0,.9),(7.0,.85)]
def drop_dramatic():
    return [(0.0,1.0),(2.0,.75),(3.0,.8),(3.5,.85),(3.75,.9),
            (4.0,.95),(5.0,.9),(6.0,.9),(7.0,.85)]
DROPS = [drop_gradual, drop_dramatic]
drop_moments = {}
di = 0
for b in range(TOTAL_BARS):
    if sec(b) == 'drop' and (b == 0 or sec(b-1) != 'drop'):
        drop_moments[b] = DROPS[di % len(DROPS)]; di += 1


# ============================================================
# MIDI GENERATORS (compact, reusable)
# ============================================================

def gen_kick_midi():
    events = []
    chaos_pats = [[0,1.5,2,3,3.5],[0,0.75,2,2.75,3.5],[0,1,2,2.5,3,3.75]]
    for bar in range(TOTAL_BARS):
        s = sec(bar)
        if s in ('silence','intro'): continue
        if s == 'drop':
            db = bar
            while db > 0 and sec(db-1) == 'drop': db -= 1
            bid = bar - db
            if db in drop_moments:
                for bp_pos, vel in drop_moments[db]():
                    tb = int(bp_pos // 4)
                    if tb != bid: continue
                    t = bar*BAR + (bp_pos - tb*4)*BEAT
                    events.append((max(0,t), 36, int(vel*127), 0.15))
            continue
        if s == 'order':
            for beat in range(4):
                t = bar*BAR + beat*BEAT + np_rng.normal(0,.002)
                events.append((max(0,t), 36, 105, 0.15))
            if bar+1<TOTAL_BARS and sec(bar+1)=='silence':
                for fp,fv in [(3.5,.8),(3.75,.85),(3.875,.9)]:
                    events.append((bar*BAR+fp*BEAT, 36, int(fv*127), 0.1))
        elif s == 'chaos':
            pat = chaos_pats[bar % len(chaos_pats)]
            for bp_pos in pat:
                t = bar*BAR + bp_pos*BEAT + np_rng.normal(0,.004)
                events.append((max(0,t), 36, int((.6+np_rng.random()*.35)*127), 0.15))
    return events

def gen_bass_midi():
    events = []
    order_pats = [[0]*16,[0,0,4,0,0,0,4,0,0,0,0,0,0,0,4,0]]
    for bar in range(TOTAL_BARS):
        s = sec(bar)
        if s in ('silence','intro'): continue
        if bar < 3: continue
        pat = [0]*16 if s in ('drop','chaos') else order_pats[bar%len(order_pats)]
        for step in range(16):
            if s=='chaos' and np_rng.random()<.12: continue
            note = ROOT + pat[step%len(pat)]
            vel = 80 + 30*(step%4==0) + np_rng.randint(-5,5)
            t = bar*BAR + step*S16 + 0.03*(step%4==0) + np_rng.normal(0,.002)
            events.append((max(0,t), note, min(127,max(1,vel)), S16*0.82))
    return events

def gen_lead_midi():
    events = []
    phrases = [
        [(64,.5,.8),(68,.75,1),(69,.25,.7),(71,1,1),(68,.5,.8)],
        [(76,.5,.9),(72,.5,.8),(71,.5,.7),(68,1.5,1)],
        [(80,1,.6),(76,.5,.7),(72,1,.9),(71,.5,.8),(68,1,1)],
    ]
    pidx = 0
    for bar in range(TOTAL_BARS):
        if sec(bar) != 'order' or bar < 38: continue
        if np_rng.random() < .15: continue
        ph = phrases[pidx % len(phrases)]; t_off = 0
        for note,dur,vel in ph:
            t = bar*BAR + t_off
            events.append((max(0,t), int(note), int(vel*100), dur*BEAT*0.9))
            t_off += dur*BEAT
        pidx += 1
    return events

def gen_acid_midi():
    events = []
    seqs = [[(52,2,110),(53,1,80),(56,3,110),(52,1,80),(50,2,100)],
            [(52,1,110),(56,1,80),(59,1,110),(60,2,100),(57,1,80)]]
    for bar in range(TOTAL_BARS):
        if bar < 8 or sec(bar) in ('silence','intro'): continue
        if sec(bar) == 'order' and np_rng.random() < .4: continue
        seq = seqs[bar%len(seqs)]; t_off = 0
        for note,dur,vel in seq:
            d = dur*S16
            t = bar*BAR + t_off
            events.append((max(0,t), note, vel, d*0.85))
            t_off += d
    return events

def gen_pad_midi():
    events = []
    chords = [[52,56,59],[53,57,60],[57,60,64],[50,53,57]]
    for ci in range(TOTAL_BARS//8 + 1):
        sb = ci*8
        if sb >= TOTAL_BARS or sec(sb) == 'silence': continue
        ch = chords[ci%len(chords)]
        dur = min(8*BAR, (TOTAL_BARS-sb)*BAR)
        for note in ch:
            events.append((sb*BAR, note, 80, dur*0.95))
    return events

def gen_fx_midi():
    events = []
    for bar in range(TOTAL_BARS):
        if sec(bar) == 'order' and bar+1 < TOTAL_BARS and sec(bar+1) == 'silence':
            events.append(((bar-1)*BAR, 60, 100, 2*BAR))
    return events


def midi_to_pb(events):
    pb = []
    for t, n, v, d in events:
        pb.append((bytes([0x90, n, min(127,max(1,v))]), max(0,t)))
        pb.append((bytes([0x80, n, 0]), max(0, t+d)))
    pb.sort(key=lambda x: x[1])
    return pb


# ============================================================
# FIND BEST PRESETS PER CATEGORY
# ============================================================

def find_all_presets(categories, subfolder='patches_factory'):
    presets = []
    for cat in categories:
        path = os.path.join(PRESETS_BASE, subfolder, cat)
        if os.path.exists(path):
            presets.extend(sorted(glob.glob(os.path.join(path, '**', '*.fxp'), recursive=True)))
    return presets

def find_3rd_party(categories):
    presets = []
    base = os.path.join(PRESETS_BASE, 'patches_3rdparty')
    for author in os.listdir(base):
        for cat in categories:
            path = os.path.join(base, author, cat)
            if os.path.exists(path):
                presets.extend(sorted(glob.glob(os.path.join(path, '*.fxp'))))
    return presets

# Gather preset pools
bass_presets = find_all_presets(['Basses']) + find_3rd_party(['Basses', 'Bass'])
lead_presets = find_all_presets(['Leads']) + find_3rd_party(['Leads'])
acid_presets = find_all_presets(['Leads', 'Sequences']) + find_3rd_party(['Leads', 'Sequences'])
pad_presets = find_all_presets(['Pads']) + find_3rd_party(['Pads', 'Atmospheres'])
fx_presets = find_all_presets(['FX']) + find_3rd_party(['FX'])

print(f"\nPreset pools:")
print(f"  Bass: {len(bass_presets)} | Lead: {len(lead_presets)} | Acid: {len(acid_presets)}")
print(f"  Pad: {len(pad_presets)} | FX: {len(fx_presets)}")


# ============================================================
# RENDER ELEMENT THROUGH PRESET
# ============================================================

def render_through_preset(preset_path, midi_pb, duration):
    """Render MIDI through a Surge XT preset, return stereo numpy array or None"""
    try:
        surge = load_plugin(SURGE_PATH)
        with open(preset_path, 'rb') as f:
            surge.raw_state = f.read()
        result = surge(midi_pb, duration=duration, sample_rate=SR, num_channels=2)
        rms = np.sqrt(np.mean(result**2))
        if rms < 0.0005:
            return None
        return result[0].astype(np.float64), result[1].astype(np.float64)
    except:
        return None


# ============================================================
# KICK — keep hybrid numpy (works well, other session confirmed)
# ============================================================
def render_kick(events):
    L = np.zeros(TOTAL_SAMPLES); R = np.zeros(TOTAL_SAMPLES)
    def mk(vel=0.85):
        t = np.linspace(0, 0.18, int(0.18*SR), endpoint=False)
        n = len(t)
        root_f = 440*(2**((40-69)/12))
        pitch = root_f + 320*np.exp(-t*50)
        body = np.sin(2*np.pi*np.cumsum(pitch)/SR)
        amp = np.exp(-t*22)*0.6 + np.exp(-t*7)*0.4
        from scipy.signal import butter, sosfilt
        cl = sosfilt(butter(2,[2500,7000],btype='band',fs=SR,output='sos'),
                     np.random.RandomState(42).randn(n))*2
        cl *= np.exp(-t*120)*0.4
        k = body*amp
        d = int(SR*0.002)
        if d < n: k[d:] += cl[:n-d]
        lo,hi = max(300-37,20),min(300+37,SR/2-100)
        k = k - sosfilt(butter(2,[lo,hi],btype='band',fs=SR,output='sos'),k)*0.85
        k = sosfilt(butter(2,35,btype='high',fs=SR,output='sos'),k)
        return np.tanh(k*vel*1.5*2)/np.tanh(2)*0.85
    for t_sec, note, vel, dur in events:
        kick = mk(vel/127)
        pos = int(t_sec*SR)
        end = min(pos+len(kick), TOTAL_SAMPLES)
        nn = end-pos
        if nn > 0 and pos >= 0:
            L[pos:end] += kick[:nn]; R[pos:end] += kick[:nn]
    return L, R


# ============================================================
# GENERATE 15 TRACKS
# ============================================================

# Pre-generate all MIDI (same for all tracks — only presets change)
print("\nGenerando MIDI...")
kick_events = gen_kick_midi()
bass_pb = midi_to_pb(gen_bass_midi())
lead_pb = midi_to_pb(gen_lead_midi())
acid_pb = midi_to_pb(gen_acid_midi())
pad_pb = midi_to_pb(gen_pad_midi())
fx_pb = midi_to_pb(gen_fx_midi())

print("Renderizando kick (fijo para todos)...")
kick_L, kick_R = render_kick(kick_events)

def ws(s, a=2): return np.tanh(s*a)/np.tanh(a)
def _hp(s,fc): return sosfilt(butter(2,np.clip(fc,20,SR/2-100),btype='high',fs=SR,output='sos'),s)
def _lp(s,fc): return sosfilt(butter(4,np.clip(fc,20,SR/2-100),btype='low',fs=SR,output='sos'),s)
def _bp(s,lo,hi):
    lo,hi=max(lo,20),min(hi,SR/2-100)
    if lo>=hi: return s
    return sosfilt(butter(2,[lo,hi],btype='band',fs=SR,output='sos'),s)

N_TRACKS = 15
successful = 0

for track_num in range(1, N_TRACKS + 1):
    print(f"\n{'='*50}")
    print(f" TRACK {track_num:02d}/{N_TRACKS}")
    print(f"{'='*50}")

    # Pick random presets
    bp = rng.choice(bass_presets)
    lp_preset = rng.choice(lead_presets)
    ap = rng.choice(acid_presets)
    pp = rng.choice(pad_presets)
    fp = rng.choice(fx_presets)

    names = {
        'bass': os.path.basename(bp)[:-4],
        'lead': os.path.basename(lp_preset)[:-4],
        'acid': os.path.basename(ap)[:-4],
        'pad': os.path.basename(pp)[:-4],
        'fx': os.path.basename(fp)[:-4],
    }

    print(f"  Bass: {names['bass']}")
    print(f"  Lead: {names['lead']}")
    print(f"  Acid: {names['acid']}")
    print(f"  Pad:  {names['pad']}")
    print(f"  FX:   {names['fx']}")

    # Render each element
    print("  Rendering...")
    bass_result = render_through_preset(bp, bass_pb, TOTAL_TIME + 1)
    lead_result = render_through_preset(lp_preset, lead_pb, TOTAL_TIME + 1)
    acid_result = render_through_preset(ap, acid_pb, TOTAL_TIME + 1)
    pad_result = render_through_preset(pp, pad_pb, TOTAL_TIME + 1)
    fx_result = render_through_preset(fp, fx_pb, TOTAL_TIME + 1)

    # Mix
    n = TOTAL_SAMPLES
    mL = np.zeros(n); mR = np.zeros(n)

    mL += kick_L[:n] * 0.90; mR += kick_R[:n] * 0.90

    if bass_result:
        bL, bR = bass_result
        mL += bL[:n] * 0.85; mR += bR[:n] * 0.85
    if lead_result:
        lL, lR = lead_result
        mL += lL[:n] * 0.45; mR += lR[:n] * 0.45
    if acid_result:
        aL, aR = acid_result
        mL += aL[:n] * 0.50; mR += aR[:n] * 0.50
    if pad_result:
        pL, pR = pad_result
        mL += pL[:n] * 0.38; mR += pR[:n] * 0.38
    if fx_result:
        fL, fR = fx_result
        mL += fL[:n] * 0.45; mR += fR[:n] * 0.45

    mL = np.nan_to_num(mL, 0); mR = np.nan_to_num(mR, 0)

    # Quick master
    mL = _hp(mL, 28); mR = _hp(mR, 28)
    sL = _lp(mL, 60); sR = _lp(mR, 60)
    mL -= sL * 0.2; mR -= sR * 0.2
    mL = ws(mL, 1.5); mR = ws(mR, 1.5)

    pk = max(np.max(np.abs(mL)), np.max(np.abs(mR)))
    if pk > 0: mL /= pk; mR /= pk
    rms = np.sqrt(np.mean(mL**2 + mR**2) / 2)
    if rms > 0:
        g = min(10**(-9/20) / rms, 3)
        mL *= g; mR *= g
    mL = np.clip(mL, -.98, .98); mR = np.clip(mR, -.98, .98)

    # Save
    stereo = np.column_stack([(mL*32767).astype(np.int16), (mR*32767).astype(np.int16)])
    # Filename includes preset names
    safe = lambda s: "".join(c if c.isalnum() else '_' for c in s)[:20]
    filename = f"Track_{track_num:02d}_B-{safe(names['bass'])}_L-{safe(names['lead'])}.wav"
    out_path = os.path.join(OUTPUT_DIR, filename)
    wavfile.write(out_path, SR, stereo)
    print(f"  Saved: {filename}")

    # Log presets used
    with open(os.path.join(OUTPUT_DIR, f"Track_{track_num:02d}_presets.txt"), 'w') as f:
        f.write(f"Track {track_num:02d} Preset Configuration\n")
        f.write(f"{'='*40}\n")
        for elem, name in names.items():
            f.write(f"  {elem:6s}: {name}\n")
        f.write(f"\nPreset paths:\n")
        f.write(f"  Bass: {bp}\n  Lead: {lp_preset}\n  Acid: {ap}\n  Pad: {pp}\n  FX: {fp}\n")

    successful += 1

print(f"\n{'='*60}")
print(f" DONE — {successful} tracks en {OUTPUT_DIR}")
print(f" Cada track tiene un .txt con los presets usados")
print(f" Escucha y decime cuales te gustan!")
print(f"{'='*60}")
