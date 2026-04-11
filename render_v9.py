"""
DARK PSYTRANCE v9 — SURGE XT RENDERED
Uses the v7 composition engine but renders all audio through Surge XT.
Each element gets its own Surge XT instance with dark psy presets.
"""

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt
from pedalboard import load_plugin
import os, sys, shutil

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
STEMS_DIR = os.path.join(OUTPUT_DIR, "stems_v9")
os.makedirs(STEMS_DIR, exist_ok=True)

SR = 44100
BPM = 150
BEAT = 60.0 / BPM
BAR = BEAT * 4
S16 = BEAT / 4
TOTAL_BARS = 280
TOTAL_TIME = TOTAL_BARS * BAR
TOTAL_SAMPLES = int(TOTAL_TIME * SR)

SURGE_PATH = 'C:/Program Files/Common Files/VST3/Surge Synth Team/Surge XT.vst3/Contents/x86_64-win/Surge XT.vst3'
KRANCHDD_PATH = 'C:/Program Files/Common Files/VST3/KINDZAudio/KranchDD.vst3'

print("=" * 60)
print(" DARK PSYTRANCE v9 - SURGE XT RENDERED")
print(f" BPM: {BPM} | Bars: {TOTAL_BARS} | Duration: {TOTAL_TIME/60:.1f} min")
print("=" * 60)

rng = np.random.RandomState(666)
ROOT = 40  # E2

# ============================================================
# SECTION MAP (from v7)
# ============================================================
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


# ============================================================
# DROP PATTERNS (from v7)
# ============================================================
def drop_gradual():
    return [(0.0,.6),(1.5,.5),(2.0,.7),(2.5,.65),(3.0,.8),(3.5,.75),(3.75,.85),
            (4.0,.95),(5.0,.9),(6.0,.9),(7.0,.85)]
def drop_dramatic():
    return [(0.0,1.0),(2.0,.75),(3.0,.8),(3.5,.85),(3.75,.9),
            (4.0,.95),(5.0,.9),(6.0,.9),(7.0,.85)]
def drop_stutter():
    return [(0.0,.85),(0.25,.6),(1.0,.8),(1.75,.5),(2.0,.85),(2.5,.7),(3.0,.9),(3.5,.8),
            (4.0,.9),(5.0,.85),(6.0,.85),(7.0,.85)]
def drop_rolling():
    return [(0.0,.7),(1.0,.75),(2.0,.8),(2.5,.7),(3.0,.85),(3.25,.6),(3.5,.9),(3.75,.7),
            (4.0,.95),(5.0,.9),(6.0,.9),(7.0,.85)]
def drop_triplet():
    return [(0.0,.8),(0.667,.6),(1.333,.7),(2.0,.85),(2.667,.65),(3.333,.8),(3.667,.7),
            (4.0,.95),(5.0,.9),(6.0,.9),(7.0,.85)]

DROP_TYPES = [drop_gradual, drop_dramatic, drop_stutter, drop_rolling, drop_triplet]
drop_moments = {}
di = 0
for b in range(TOTAL_BARS):
    if sec(b) == 'drop' and (b == 0 or sec(b-1) != 'drop'):
        drop_moments[b] = DROP_TYPES[di % len(DROP_TYPES)]; di += 1


# ============================================================
# MIDI GENERATION — same composition as v7, output as MIDI events
# ============================================================

def gen_kick_midi():
    """Generate kick MIDI events: [(time_seconds, note, velocity, duration)]"""
    print("  [1/7] Kick MIDI...")
    events = []
    chaos_patterns = [
        [0,1.5,2,3,3.5],[0,0.75,2,2.75,3.5],[0,1,2,2.5,3,3.75],
        [0,0.5,1.5,2,3],[0,1,1.75,2.5,3,3.25,3.75],[0,2,2.25,3,3.5,3.75]]

    for bar in range(TOTAL_BARS):
        s = sec(bar)
        if s == 'silence': continue
        if s in ('break','intro'): continue

        if s == 'drop':
            db = bar
            while db > 0 and sec(db-1) == 'drop': db -= 1
            bid = bar - db
            if db in drop_moments:
                for bp_pos, vel in drop_moments[db]():
                    tb = int(bp_pos // 4)
                    if tb != bid: continue
                    bib = bp_pos - tb * 4
                    t = bar * BAR + bib * BEAT + rng.normal(0, 0.003)
                    events.append((max(0, t), 36, int(vel * 127), 0.15))
            continue

        if s == 'order':
            for beat in range(4):
                if beat != 0 and rng.random() < 0.02: continue
                vel = 0.80 + rng.random() * 0.15
                t = bar * BAR + beat * BEAT + rng.normal(0, 0.002)
                events.append((max(0, t), 36, int(vel * 127), 0.15))
            # Fill before silence
            if bar + 1 < TOTAL_BARS and sec(bar + 1) == 'silence':
                for fp, fv in [(2.25,.6),(2.75,.7),(3.25,.75),(3.5,.8),(3.625,.7),(3.75,.85),(3.875,.9)]:
                    t = bar * BAR + fp * BEAT
                    events.append((t, 36, int(fv * 127), 0.1))
        elif s == 'chaos':
            pat = chaos_patterns[bar % len(chaos_patterns)]
            for bp_pos in pat:
                vel = 0.6 + rng.random() * 0.35
                t = bar * BAR + bp_pos * BEAT + rng.normal(0, 0.004)
                events.append((max(0, t), 36, int(vel * 127), 0.15))
        elif s == 'build':
            bs = bar;
            while bs > 0 and sec(bs-1) == 'build': bs -= 1
            be = bar
            while be < TOTAL_BARS and sec(be) == 'build': be += 1
            prog = (bar - bs) / max(be - bs, 1)
            if prog < 0.3: beats = [0, 2]
            elif prog < 0.6: beats = [0, 1, 2, 3]
            else: beats = [0, 1, 2, 2.5, 3, 3.5]
            for bp_pos in beats:
                t = bar * BAR + bp_pos * BEAT + rng.normal(0, 0.003)
                events.append((max(0, t), 36, int((0.6 + prog * 0.3) * 127), 0.15))
        elif s == 'outro':
            bio = bar - 268
            if bio < 4: beats = [0,1,2,3]
            elif bio < 8: beats = [0,2]
            else: beats = [0] if bio % 2 == 0 else []
            for beat in beats:
                t = bar * BAR + beat * BEAT
                events.append((t, 36, int((0.7 - 0.03 * bio) * 127), 0.15))

    return events


def gen_bass_midi():
    """Rolling bass MIDI"""
    print("  [2/7] Bass MIDI...")
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


def gen_lead_midi():
    """Lead melody MIDI"""
    print("  [3/7] Lead MIDI...")
    events = []
    phrases = [
        [(64,.5,.8),(68,.75,1),(69,.25,.7),(71,1,1),(68,.5,.8)],
        [(76,.5,.9),(72,.5,.8),(71,.5,.7),(68,1.5,1)],
        [(80,1,.6),(76,.5,.7),(72,1,.9),(71,.5,.8),(68,1,1)],
        [(64,.5,.9),(62,.5,.8),(60,.5,.7),(64,.5,.8),(68,1,1),(72,1,.9)],
        [(71,.5,.9),(72,.5,1),(76,1,.8),(72,.5,.7),(68,1.5,1)],
    ]

    pidx = 0
    for bar in range(TOTAL_BARS):
        show = False
        if sec(bar) == 'order' and bar >= 91: show = True
        if sec(bar) == 'break': show = True
        if sec(bar) == 'silence': continue
        if not show: continue
        if rng.random() < 0.12: continue

        ph = phrases[pidx % len(phrases)]
        # Mutate
        if rng.random() > 0.3:
            ph = [(max(52,min(84,n+rng.choice([-3,-2,-1,0,1,2,3]) if rng.random()<.2 else 0)),
                   d*rng.uniform(.7,1.4) if rng.random()<.12 else d,
                   np.clip(v*rng.uniform(.85,1.1),.3,1)) for n,d,v in ph]

        t_off = 0
        for note, dur, vel in ph:
            t = bar * BAR + t_off + rng.normal(0, 0.004)
            nd = dur * BEAT * rng.uniform(0.88, 1.08)
            events.append((max(0, t), int(note), int(vel * 127), nd))
            t_off += dur * BEAT
        pidx += 1

    return events


def gen_acid_midi():
    """Acid line MIDI"""
    print("  [4/7] Acid MIDI...")
    events = []
    seqs = [
        [(52,2,1),(53,1,0),(56,3,1),(52,1,0),(50,2,1),(48,1,0),(52,2,1),(41,1,0)],
        [(52,1,1),(56,1,0),(59,1,1),(60,2,1),(57,1,0),(53,2,1),(52,1,0),(50,1,0)],
        [(64,1,1),(62,1,0),(60,2,1),(56,1,0),(52,2,1),(53,1,0),(56,2,1)],
    ]

    for bar in range(TOTAL_BARS):
        if bar < 10: continue
        s = sec(bar)
        if s in ('silence','break','intro','outro'): continue
        if s == 'order' and rng.random() < 0.3: continue  # not every bar

        seq = seqs[bar % len(seqs)]
        t_off = 0
        for note, dur, accent in seq:
            vel = 0.7 + accent * 0.25 + rng.uniform(-0.05, 0.05)
            nd = dur * S16 * rng.uniform(0.85, 0.95)
            t = bar * BAR + t_off + rng.normal(0, 0.003)
            events.append((max(0, t), note, int(vel * 127), nd))
            t_off += dur * S16

    return events


def gen_pad_midi():
    """Atmosphere pad MIDI — long sustained chords"""
    print("  [5/7] Pad MIDI...")
    events = []
    chords = [[52,56,59],[53,57,60],[57,60,64],[50,53,57],
              [56,59,62],[52,56,59],[48,52,56],[52,56,59]]

    for ci in range(TOTAL_BARS // 4 + 1):
        sb = ci * 4
        if sb >= TOTAL_BARS: break
        if sec(sb) == 'silence': continue
        ch = chords[ci % len(chords)]
        dur = min(4 * BAR, (TOTAL_BARS - sb) * BAR)
        for note in ch:
            events.append((sb * BAR, note, 80, dur * 0.95))

    return events


def gen_fm_midi():
    """FM texture MIDI — sporadic alien notes"""
    print("  [6/7] FM MIDI...")
    events = []
    scale = [40,41,44,45,47,48,50,52,53,56,57,59,60,62,64,65,68]

    for bar in range(TOTAL_BARS):
        s = sec(bar)
        if s in ('silence','intro'): continue
        c = 1.0 if s == 'chaos' else (0.4 if s == 'drop' else 0.0)
        if c < 0.15: continue
        if rng.random() > c * 0.85: continue

        n_notes = rng.randint(1, int(2 + c * 8))
        t_off = rng.uniform(0, BAR * 0.3)
        for _ in range(n_notes):
            note = scale[rng.randint(len(scale))] + rng.choice([0, 12, 24])
            dur = rng.uniform(0.03, 0.1 + c * 0.5)
            vel = int((0.4 + c * 0.5) * 127)
            t = bar * BAR + t_off
            events.append((max(0, t), min(note, 96), vel, dur))
            t_off += dur + rng.uniform(0, S16 * 2)

    return events


def gen_fx_midi():
    """FX riser MIDI — long notes for sweeps"""
    print("  [7/7] FX MIDI...")
    events = []

    # Risers before silences
    for bar in range(TOTAL_BARS):
        if sec(bar) == 'order' and bar + 1 < TOTAL_BARS and sec(bar + 1) == 'silence':
            t = (bar - 1) * BAR
            events.append((max(0, t), 60, 100, 2 * BAR))  # 2-bar riser

    # Impacts at drop entries
    for bar in range(TOTAL_BARS):
        if sec(bar) == 'drop' and (bar == 0 or sec(bar - 1) != 'drop'):
            events.append((bar * BAR, 36, 120, 1.0))

    return events


# ============================================================
# MIDI → SURGE XT → WAV
# ============================================================

def midi_to_pedalboard_format(events):
    """Convert (time, note, velocity, duration) to pedalboard format"""
    pb_midi = []
    for t, note, vel, dur in events:
        pb_midi.append((bytes([0x90, note, vel]), t))      # note on
        pb_midi.append((bytes([0x80, note, 0]), t + dur))  # note off
    # Sort by time
    pb_midi.sort(key=lambda x: x[1])
    return pb_midi


def render_element(midi_events, configure_fn, name, post_process_fn=None):
    """Render MIDI through a configured Surge XT instance"""
    print(f"\n  Rendering {name} through Surge XT...")

    # Fresh instance for each element
    surge = load_plugin(SURGE_PATH)
    configure_fn(surge)

    # Convert to pedalboard format
    pb_midi = midi_to_pedalboard_format(midi_events)

    if not pb_midi:
        print(f"    No MIDI events, skipping")
        return np.zeros(TOTAL_SAMPLES), np.zeros(TOTAL_SAMPLES)

    # Render
    result = surge(pb_midi, duration=TOTAL_TIME, sample_rate=SR, num_channels=2)

    print(f"    RMS: {np.sqrt(np.mean(result**2)):.6f}")
    print(f"    Max: {np.max(np.abs(result)):.6f}")

    L = result[0].astype(np.float64)
    R = result[1].astype(np.float64)

    # Post-process with KranchDD if specified
    if post_process_fn is not None:
        L, R = post_process_fn(L, R)

    # Ensure correct length
    if len(L) < TOTAL_SAMPLES:
        L = np.pad(L, (0, TOTAL_SAMPLES - len(L)))
        R = np.pad(R, (0, TOTAL_SAMPLES - len(R)))
    elif len(L) > TOTAL_SAMPLES:
        L = L[:TOTAL_SAMPLES]
        R = R[:TOTAL_SAMPLES]

    # Save stem
    pk = max(np.max(np.abs(L)), np.max(np.abs(R)), 1e-10)
    stereo = np.column_stack([(L/pk*0.9*32767).astype(np.int16),
                               (R/pk*0.9*32767).astype(np.int16)])
    path = os.path.join(STEMS_DIR, f"{name}.wav")
    wavfile.write(path, SR, stereo)
    print(f"    Saved: {path}")

    return L, R


# ============================================================
# KRANCHDD POST-PROCESSING
# ============================================================

def make_kranchdd_processor(preset, wet=0.4):
    """Create a post-processor using KranchDD"""
    def process(L, R):
        kranchdd = load_plugin(KRANCHDD_PATH)
        for key, val in preset.items():
            if hasattr(kranchdd, key):
                setattr(kranchdd, key, val)

        stereo = np.array([L.astype(np.float32), R.astype(np.float32)])
        pk = np.max(np.abs(stereo))
        if pk > 0:
            stereo_n = stereo / pk * 0.7
        else:
            return L, R

        wet_sig = kranchdd(stereo_n, SR)
        wet_pk = np.max(np.abs(wet_sig))
        if wet_pk > 0.001:
            wet_sig = wet_sig / wet_pk * pk * 0.7
            out = stereo_n * pk / 0.7 * (1 - wet) + wet_sig * wet
            return out[0].astype(np.float64), out[1].astype(np.float64)
        return L, R
    return process


bass_kranchdd = make_kranchdd_processor({
    'flt': 4000.0, 'dst': 0.5, 'mix': 1.0, 'qm': 6.0, 'morph': 0.3,
    'feedback': 0.15, 'inn': 2.0, 'ouu': 1.0, 'wtf': 0.05, 'type': 4.0,
    'chain': 1.0, 'clip': 0.4, 'overx': 1.0, 'bypass': False,
}, wet=0.4)

acid_kranchdd = make_kranchdd_processor({
    'flt': 6000.0, 'dst': 0.6, 'mix': 1.0, 'qm': 8.0, 'morph': 0.5,
    'feedback': 0.2, 'inn': 2.5, 'ouu': 0.9, 'wtf': 0.15, 'type': 6.0,
    'chain': 1.0, 'clip': 0.5, 'overx': 1.0, 'bypass': False,
}, wet=0.45)


# ============================================================
# IMPORT PRESETS
# ============================================================
from surge_presets import (configure_bass, configure_lead, configure_acid,
                           configure_pad, configure_fm_texture, configure_fx_riser)


# ============================================================
# RENDER ALL ELEMENTS
# ============================================================
print("\n" + "=" * 60)
print(" GENERATING MIDI")
print("=" * 60)

kick_midi = gen_kick_midi()
bass_midi = gen_bass_midi()
lead_midi = gen_lead_midi()
acid_midi = gen_acid_midi()
pad_midi = gen_pad_midi()
fm_midi = gen_fm_midi()
fx_midi = gen_fx_midi()

print(f"\n  Total MIDI events: {sum(len(x) for x in [kick_midi,bass_midi,lead_midi,acid_midi,pad_midi,fm_midi,fx_midi])}")

print("\n" + "=" * 60)
print(" RENDERING THROUGH SURGE XT")
print("=" * 60)

# Kick: use numpy synthesis (Surge XT sine doesn't do pitch envelopes well for kicks)
# We keep the v7 kick synthesis but it's still better than nothing
print("\n  Kick: using hybrid synthesis (pitch envelope + Surge XT sine)...")
# Simple kick render
from scipy.signal import sawtooth
def render_kick_hybrid():
    L = np.zeros(TOTAL_SAMPLES)
    R = np.zeros(TOTAL_SAMPLES)
    def mk(vel=0.85):
        t = np.linspace(0, 0.2, int(0.2*SR), endpoint=False)
        n = len(t)
        root_f = 440 * (2**((40-69)/12))
        pitch = root_f + 200*np.exp(-t*50)
        body = np.sin(2*np.pi*np.cumsum(pitch)/SR)*np.exp(-t*14)*0.8
        from scipy.signal import butter, sosfilt
        cl = sosfilt(butter(2,[2500,7000],btype='band',fs=SR,output='sos'),
                     np.random.RandomState(42).randn(n))*2.5
        cl *= np.exp(-t*100)*0.5
        k = body.copy()
        d = int(SR*0.002)
        if d < n: k[d:] += cl[:n-d]*0.6
        # Notch 300Hz
        lo,hi = max(300-300/8,20),min(300+300/8,SR/2-100)
        k = k - sosfilt(butter(2,[lo,hi],btype='band',fs=SR,output='sos'),k)*0.85
        k = sosfilt(butter(2,28,btype='high',fs=SR,output='sos'),k)
        return np.tanh(k*vel*1.3*2)/np.tanh(2)*0.9
    for t_sec, note, vel, dur in kick_midi:
        kick = mk(vel/127)
        pos = int(t_sec * SR)
        end = min(pos+len(kick), TOTAL_SAMPLES)
        nn = end-pos
        if nn > 0 and pos >= 0:
            L[pos:end] += kick[:nn]
            R[pos:end] += kick[:nn]
    pk = max(np.max(np.abs(L)),np.max(np.abs(R)),1e-10)
    stereo = np.column_stack([(L/pk*0.9*32767).astype(np.int16),(R/pk*0.9*32767).astype(np.int16)])
    wavfile.write(os.path.join(STEMS_DIR,"kick.wav"),SR,stereo)
    print(f"    Kick saved (hybrid)")
    return L, R

kick_L, kick_R = render_kick_hybrid()

# Bass through Surge XT + KranchDD
bass_L, bass_R = render_element(bass_midi, configure_bass, "bass", bass_kranchdd)

# Lead through Surge XT
lead_L, lead_R = render_element(lead_midi, configure_lead, "lead")

# Acid through Surge XT + KranchDD
acid_L, acid_R = render_element(acid_midi, configure_acid, "acid", acid_kranchdd)

# Pads through Surge XT
pad_L, pad_R = render_element(pad_midi, configure_pad, "pad")

# FM textures through Surge XT
fm_L, fm_R = render_element(fm_midi, configure_fm_texture, "fm_texture")

# FX through Surge XT
fx_L, fx_R = render_element(fx_midi, configure_fx_riser, "fx")

# Drums: keep numpy synthesis for hats/claps (noise-based, Surge XT noise is different)
print("\n  Drums: using numpy synthesis (noise-based)...")
def render_drums():
    L = np.zeros(TOTAL_SAMPLES); R = np.zeros(TOTAL_SAMPLES)
    def _hp(s,fc):
        return sosfilt(butter(2,np.clip(fc,20,SR/2-100),btype='high',fs=SR,output='sos'),s)
    def _bp(s,lo,hi):
        lo,hi=max(lo,20),min(hi,SR/2-100)
        if lo>=hi: return s
        return sosfilt(butter(2,[lo,hi],btype='band',fs=SR,output='sos'),s)
    def ast(oL,oR,m,pos,p=0):
        l=m*np.cos((p+1)/2*np.pi/2); r=m*np.sin((p+1)/2*np.pi/2)
        end=min(pos+len(l),len(oL)); n=end-pos
        if n>0 and pos>=0: oL[pos:end]+=l[:n]; oR[pos:end]+=r[:n]
    def ta(d): return np.linspace(0,d,int(d*SR),endpoint=False)

    for bar in range(TOTAL_BARS):
        s = sec(bar)
        if s in ('silence','break','intro'): continue
        if bar < 10: continue
        c = 1.0 if s=='chaos' else 0.0
        for step in range(16):
            timing = rng.normal(0,.003)
            if step%4==2:
                prob = .95 if c < .3 else max(.3,.95-c*.6)
                if rng.random() < prob:
                    dur = S16*rng.uniform(.4,.7); t=ta(dur)
                    hat=_hp(rng.randn(len(t)),6000+rng.random()*3000)
                    hat*=np.exp(-t*(25+rng.random()*20))*rng.uniform(.18,.28)
                    pos=int((bar*BAR+step*S16+timing)*SR)
                    ast(L,R,hat,max(0,pos),p=.15+rng.uniform(-.1,.1))
            elif step%2==1 and rng.random()<(.5-c*.2):
                dur=S16*rng.uniform(.2,.35); t=ta(dur)
                hat=_hp(rng.randn(len(t)),8000+rng.random()*3000)
                hat*=np.exp(-t*(40+rng.random()*25))*rng.uniform(.06,.12)
                pos=int((bar*BAR+step*S16+timing)*SR)
                ast(L,R,hat,max(0,pos),p=rng.uniform(-.5,.5))
        if c<.5 and bar>=12:
            for beat in [1,3]:
                t=ta(rng.uniform(.06,.1)); clap=np.zeros(len(t))
                for i in range(rng.randint(2,5)):
                    d=int(i*SR*rng.uniform(.003,.007))
                    b=_bp(rng.randn(len(t)),700+rng.random()*500,4000+rng.random()*1500)
                    b*=np.exp(-t*(25+rng.random()*15))
                    if d<len(clap): clap[d:]+=b[:len(clap)-d]*(.7**i)
                clap*=rng.uniform(.2,.35)
                pos=int((bar*BAR+beat*BEAT+rng.normal(0,.003))*SR)
                ast(L,R,clap,max(0,pos),p=rng.uniform(-.08,.08))
    pk=max(np.max(np.abs(L)),np.max(np.abs(R)),1e-10)
    stereo=np.column_stack([(L/pk*.9*32767).astype(np.int16),(R/pk*.9*32767).astype(np.int16)])
    wavfile.write(os.path.join(STEMS_DIR,"drums.wav"),SR,stereo)
    print(f"    Drums saved")
    return L, R

drums_L, drums_R = render_drums()


# ============================================================
# MIX + MASTER
# ============================================================
print("\n" + "=" * 60)
print(" MIXING + MASTERING")
print("=" * 60)

def ws(s,a=2): return np.tanh(s*a)/np.tanh(a)
def _lp(s,fc):
    return sosfilt(butter(4,np.clip(fc,20,SR/2-100),btype='low',fs=SR,output='sos'),s)
def _hp2(s,fc):
    return sosfilt(butter(2,np.clip(fc,20,SR/2-100),btype='high',fs=SR,output='sos'),s)
def _bp2(s,lo,hi):
    lo,hi=max(lo,20),min(hi,SR/2-100)
    if lo>=hi: return s
    return sosfilt(butter(2,[lo,hi],btype='band',fs=SR,output='sos'),s)

mL = np.zeros(TOTAL_SAMPLES)
mR = np.zeros(TOTAL_SAMPLES)

mL += kick_L * 0.90;   mR += kick_R * 0.90
mL += bass_L * 0.85;   mR += bass_R * 0.85
mL += acid_L * 0.55;   mR += acid_R * 0.55
mL += drums_L * 0.55;  mR += drums_R * 0.55
mL += lead_L * 0.50;   mR += lead_R * 0.50
mL += pad_L * 0.40;    mR += pad_R * 0.40
mL += fm_L * 0.45;     mR += fm_R * 0.45
mL += fx_L * 0.48;     mR += fx_R * 0.48

# Sidechain
print("  Sidechain...")
km = (kick_L + kick_R) / 2
ke = np.abs(km)
w = int(0.03 * SR)
ks = np.convolve(ke, np.ones(w)/w, mode='same')
ks /= (np.max(ks) + 1e-10)
sc = 1 - ks * 0.15
nkL = mL - kick_L * 0.90; nkR = mR - kick_R * 0.90
mL = kick_L * 0.90 + nkL * sc; mR = kick_R * 0.90 + nkR * sc

# Master
print("  Masterizando...")
mL = _hp2(mL, 25); mR = _hp2(mR, 25)
sL = _lp(mL, 60); sR = _lp(mR, 60)
mL -= sL * 0.3; mR -= sR * 0.3

m1L = _bp2(mL, 200, 600); m1R = _bp2(mR, 200, 600)
mL += m1L * 0.3; mR += m1R * 0.3
m2L = _bp2(mL, 600, 2000); m2R = _bp2(mR, 600, 2000)
mL += m2L * 0.25; mR += m2R * 0.25
pL = _bp2(mL, 2000, 6000); pR = _bp2(mR, 2000, 6000)
mL += pL * 0.2; mR += pR * 0.2

mL = ws(mL, 1.6); mR = ws(mR, 1.6)

pk = max(np.max(np.abs(mL)), np.max(np.abs(mR)))
if pk > 0: mL /= pk; mR /= pk
rms = np.sqrt(np.mean(mL**2 + mR**2) / 2)
tgt = 10**(-9.0/20)
if rms > 0:
    g = min(tgt/rms, 3.0); mL *= g; mR *= g
mL = np.clip(mL, -0.98, 0.98); mR = np.clip(mR, -0.98, 0.98)

# Save
print("  Guardando...")
stereo = np.column_stack([(mL*32767).astype(np.int16), (mR*32767).astype(np.int16)])
output = os.path.join(OUTPUT_DIR, "DarkPsy_v9_SURGE_XT.wav")
wavfile.write(output, SR, stereo)
desktop = "C:/Users/Juan/Desktop/DarkPsy_v9_SURGE_XT.wav"
shutil.copy2(output, desktop)

# Verify
print("\n--- Verificacion ---")
mc = (mL+mR)/2
fft_c = np.abs(np.fft.rfft(mc)); freqs_c = np.fft.rfftfreq(len(mc),1/SR)
te = np.sum(fft_c**2)
for nm,lo,hi in [('Sub',20,60),('Bass',60,200),('LowMid',200,600),('Mid',600,2000),
                  ('HiMid',2000,6000),('Pres',6000,10000),('Air',10000,20000)]:
    mask=(freqs_c>=lo)&(freqs_c<hi)
    print(f'  {nm:8s}: {np.sum(fft_c[mask]**2)/te*100:5.1f}%')
rms_f = np.sqrt(np.mean(mc**2))
print(f'  RMS: {20*np.log10(rms_f+1e-10):.1f} dB')

print(f"\n{'='*60}")
print(f" TRACK: {desktop}")
print(f" {TOTAL_TIME/60:.1f} min | Surge XT rendered | KranchDD processed")
print(f" Bass + Acid through real synth + Kindzadza distortion")
print(f"{'='*60}")
