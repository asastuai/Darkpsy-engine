"""
DARK PSYTRANCE v6 — THE DROP
Silence as weapon. Accelerando on re-entry. Euphoria engineering.

Key concepts:
- ORDER sections: clean locked groove (1/16 rolling)
- SILENCE: 1-4 beats of NOTHING before drops
- RE-ENTRY: burst at 1/32 or triplets, then settle back
- CHAOS: FM, granular, filter madness
- Fast transitions, abrupt cuts, no gradual fades
"""

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt, sawtooth, square, resample
import os, sys

# Force UTF-8
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
SR = 44100
BPM = 150
BEAT = 60.0 / BPM
BAR = BEAT * 4
S16 = BEAT / 4
S32 = BEAT / 8  # for accelerando bursts
TOTAL_BARS = 256  # ~6.8 min
TOTAL_TIME = TOTAL_BARS * BAR
TOTAL_SAMPLES = int(TOTAL_TIME * SR)

print("=" * 60)
print(" DARK PSYTRANCE v6 - THE DROP")
print(f" BPM: {BPM} | Bars: {TOTAL_BARS} | Duration: {TOTAL_TIME/60:.1f} min")
print("=" * 60)

rng = np.random.RandomState(666)

# ============================================================
# DSP (compact)
# ============================================================
def ta(d): return np.linspace(0, d, int(d*SR), endpoint=False)
def _lp(s, fc, o=4):
    fc = np.clip(fc, 20, SR/2-100)
    return sosfilt(butter(o, fc, btype='low', fs=SR, output='sos'), s)
def _hp(s, fc, o=2):
    fc = np.clip(fc, 20, SR/2-100)
    return sosfilt(butter(o, fc, btype='high', fs=SR, output='sos'), s)
def _bp(s, lo, hi, o=2):
    lo, hi = max(lo,20), min(hi,SR/2-100)
    if lo >= hi: return s
    return sosfilt(butter(o, [lo,hi], btype='band', fs=SR, output='sos'), s)
def _notch(s, fc, q=8):
    lo, hi = max(fc-fc/q,20), min(fc+fc/q,SR/2-100)
    if lo >= hi: return s
    return s - _bp(s, lo, hi, o=2)*0.85
def nf(n): return 440*(2**((n-69)/12))
def ws(s, a=2): return np.tanh(s*a)/np.tanh(a)
def adsr(t, a=.01, d=.1, s=.7, r=.2, dur=None):
    if dur is None: dur = t[-1] if len(t) else 1
    e = np.zeros_like(t)
    for i, ti in enumerate(t):
        if ti < a: e[i] = ti/a if a > 0 else 1
        elif ti < a+d: e[i] = 1-(1-s)*(ti-a)/d
        elif ti < dur-r: e[i] = s
        else: e[i] = s*max(0,(dur-ti)/r) if r > 0 else 0
    return e
def ps(m, p=0):
    l = np.cos((p+1)/2*np.pi/2)
    r = np.sin((p+1)/2*np.pi/2)
    return m*l, m*r
def ast(oL, oR, m, pos, p=0):
    L, R = ps(m, p)
    end = min(pos+len(L), len(oL))
    n = end-pos
    if n > 0 and pos >= 0:
        oL[pos:end] += L[:n]; oR[pos:end] += R[:n]
def fm_s(t, cf, mf, mi):
    return np.sin(2*np.pi*cf*t + np.sin(2*np.pi*mf*t)*mi)

ROOT = 40
ROOT_F = nf(ROOT)

# ============================================================
# SECTION MAP — with SILENCE markers and DROP types
# ============================================================
# Section types:
# 'order'   — locked groove, dance
# 'chaos'   — entropic madness
# 'silence' — 1-2 bars of NOTHING (the weapon)
# 'drop_32' — re-entry at 1/32 speed (accelerando burst)
# 'drop_trip'— re-entry with triplets
# 'break'   — stripped atmospheric
# 'build'   — energy returning
# 'intro'/'outro'

smap = {}

def set_sec(start, end, typ):
    for b in range(start, min(end, TOTAL_BARS)):
        smap[b] = typ

# INTRO
set_sec(0, 8, 'intro')

# ORDER 1 — establish the groove
set_sec(8, 28, 'order')

# SILENCE + DROP 1 (first euphoria)
set_sec(28, 29, 'silence')       # 1 bar silence
set_sec(29, 31, 'drop_32')       # BURST at 1/32
set_sec(31, 32, 'drop_trip')     # triplet madness
set_sec(32, 40, 'chaos')         # chaos explosion

# Back to order
set_sec(40, 41, 'silence')       # breath
set_sec(41, 42, 'drop_32')       # burst back in
set_sec(42, 62, 'order')         # long groove

# SILENCE + DROP 2 (bigger)
set_sec(62, 63, 'silence')
set_sec(63, 65, 'drop_32')
set_sec(65, 66, 'drop_trip')
set_sec(66, 80, 'chaos')         # longer chaos

# ORDER 3 — the big dance
set_sec(80, 81, 'silence')
set_sec(81, 82, 'drop_32')
set_sec(82, 110, 'order')        # longest order section, lead enters

# SILENCE + DROP 3 — CLIMAX
set_sec(110, 111, 'silence')     # the silence before the storm
set_sec(111, 114, 'drop_32')     # longest burst ever, 3 bars of 1/32
set_sec(114, 116, 'drop_trip')
set_sec(116, 136, 'chaos')       # peak chaos, 20 bars

# BREAKDOWN — breathing space
set_sec(136, 137, 'silence')     # cut to nothing
set_sec(137, 150, 'break')       # pads, atmosphere, matices de luz

# BUILD
set_sec(150, 160, 'build')

# ORDER 4 — resolution with lead
set_sec(160, 161, 'silence')     # silence before final groove
set_sec(161, 163, 'drop_32')
set_sec(163, 190, 'order')

# FINAL CHAOS
set_sec(190, 191, 'silence')
set_sec(191, 193, 'drop_32')
set_sec(193, 194, 'drop_trip')
set_sec(194, 216, 'chaos')

# OUTRO
set_sec(216, 217, 'silence')     # final silence
set_sec(217, 218, 'drop_32')     # one last burst
set_sec(218, 240, 'order')       # wind down
set_sec(240, TOTAL_BARS, 'outro')

# Fill any unmapped bars
for b in range(TOTAL_BARS):
    if b not in smap: smap[b] = 'order'

def sec(b): return smap.get(b, 'order')
def is_order(b): return sec(b) == 'order'
def is_chaos(b): return sec(b) == 'chaos'
def is_silence(b): return sec(b) == 'silence'
def is_drop32(b): return sec(b) == 'drop_32'
def is_drop_trip(b): return sec(b) == 'drop_trip'
def is_break(b): return sec(b) in ('break','intro','outro')
def is_build(b): return sec(b) == 'build'
def is_drop(b): return sec(b).startswith('drop')

# Chaos amount for mixing
def ca(b):
    s = sec(b)
    if s == 'order': return 0.0
    if s == 'chaos': return 1.0
    if s in ('drop_32','drop_trip'): return 0.7
    if s == 'silence': return 0.0
    if s == 'break': return 0.1
    if s == 'build':
        # Find build start
        bs = b
        while bs > 0 and sec(bs-1) == 'build': bs -= 1
        be = b
        while be < TOTAL_BARS and sec(be) == 'build': be += 1
        return 0.1 + 0.5 * (b-bs)/(be-bs)
    return 0.3

# Print structure
print("\nESTRUCTURA:")
prev = ''
for b in range(TOTAL_BARS):
    s = sec(b)
    if s != prev:
        e = b
        while e < TOTAL_BARS and sec(e) == s: e += 1
        labels = {
            'intro':'INTRO', 'order':'>>> ORDER (DANCE)',
            'chaos':'*** CHAOS (MIND)', 'silence':'[SILENCE]',
            'drop_32':'!! DROP 1/32 (BURST)', 'drop_trip':'!! DROP TRIPLETS',
            'break':'... BREAKDOWN', 'build':'^^ BUILD', 'outro':'OUTRO'
        }
        ts = b*BAR/60
        te = e*BAR/60
        print(f"  {b:3d}-{e-1:3d} ({ts:.1f}-{te:.1f}m): {labels.get(s,s)}")
        prev = s


# ============================================================
# KICK
# ============================================================
def gen_kick():
    print("\n  [1/9] Kick...")
    L = np.zeros(TOTAL_SAMPLES)
    R = np.zeros(TOTAL_SAMPLES)

    def mk(vel=.85, var=0):
        t = ta(0.2)
        n = len(t)
        cl = _bp(rng.randn(n), 2500+var*300, 7000+var*500, o=2)*2.5
        cl *= np.exp(-t*100)*.5
        d = int(SR*.002)
        pitch = ROOT_F + (250+var*50)*np.exp(-t*(55+var*10))
        body = np.sin(2*np.pi*np.cumsum(pitch)/SR)*np.exp(-t*(12+var*2))*.8
        k = body.copy()
        if d < n: k[d:] += cl[:n-d]*.6
        k = _notch(k, 300, q=8)
        k = _hp(k, 28)
        return ws(k*vel*1.3, 2+var*.5)*.9

    for bar in range(TOTAL_BARS):
        s = sec(bar)

        # SILENCE — absolutely nothing
        if is_silence(bar):
            continue

        if is_break(bar) and s in ('break','intro'):
            continue

        # DROP 1/32 — machine gun burst!
        if is_drop32(bar):
            for step in range(32):  # 32 hits per bar = 1/32 notes
                vel = 0.6 + (step/32)*0.35  # crescendo through bar
                timing = rng.normal(0, 0.001)  # very tight
                kick = mk(vel=vel, var=rng.randint(0,2))
                pos = int((bar*BAR + step*S32 + timing)*SR)
                ast(L, R, kick, max(0,pos), p=rng.uniform(-.03,.03))
            continue

        # DROP TRIPLETS — 12 hits per bar (triplet feel at 1/16)
        if is_drop_trip(bar):
            for step in range(24):  # 6 per beat = triplet 16ths
                vel = 0.65 + rng.random()*.3
                trip_dur = BEAT / 6
                pos = int((bar*BAR + step*trip_dur + rng.normal(0,.002))*SR)
                kick = mk(vel=vel, var=rng.randint(0,3))
                ast(L, R, kick, max(0,pos), p=rng.uniform(-.04,.04))
            continue

        # ORDER — locked 4/4
        if is_order(bar):
            for beat in range(4):
                if beat != 0 and rng.random() < 0.02: continue
                vel = .80 + rng.random()*.15
                kick = mk(vel=vel, var=rng.randint(0,2))
                pos = int((bar*BAR + beat*BEAT + rng.normal(0,.002))*SR)
                ast(L, R, kick, max(0,pos), p=rng.uniform(-.03,.03))

            # Fill on last bar before silence
            if bar+1 < TOTAL_BARS and is_silence(bar+1):
                # Accelerating fill in last 2 beats
                fill_pos = [2.0, 2.5, 2.75, 2.875, 3.0, 3.25, 3.5, 3.625, 3.75, 3.8125, 3.875, 3.9375]
                for fp in fill_pos:
                    v = 0.6 + (fp-2)/2 * 0.4
                    kick = mk(vel=v, var=rng.randint(0,3))
                    pos = int((bar*BAR + fp*BEAT)*SR)
                    ast(L, R, kick, max(0,pos), p=rng.uniform(-.05,.05))
            continue

        # CHAOS — irregular, sparse
        if is_chaos(bar):
            n_hits = rng.randint(2, 8)
            positions = sorted(rng.uniform(0, BAR, n_hits))
            for p in positions:
                vel = rng.uniform(.5, .95)
                kick = mk(vel=vel, var=rng.randint(0,4))
                pos = int((bar*BAR + p)*SR)
                ast(L, R, kick, max(0,pos), p=rng.uniform(-.05,.05))
            continue

        # BUILD — accelerating density
        if is_build(bar):
            progress = ca(bar)
            n_hits = int(4 + progress * 12)
            for i in range(n_hits):
                beat_pos = i * BAR / n_hits
                vel = 0.6 + progress * 0.3
                kick = mk(vel=vel, var=rng.randint(0,2))
                pos = int((bar*BAR + beat_pos + rng.normal(0,.003))*SR)
                ast(L, R, kick, max(0,pos), p=rng.uniform(-.04,.04))

    return L, R


# ============================================================
# ROLLING BASS
# ============================================================
def gen_bass():
    print("  [2/9] Rolling bass...")
    L = np.zeros(TOTAL_SAMPLES)
    R = np.zeros(TOTAL_SAMPLES)
    kick_tail = .05

    order_pats = [[0]*16, [0,0,4,0,0,0,4,0,0,0,0,0,0,0,4,0], [0,0,0,0,0,0,4,0,0,0,0,0,0,0,7,0]]
    chaos_pats = [[0,1,4,7,5,0,1,4,7,5,0,1,4,7,5,0], [7,0,4,1,0,5,7,0,4,1,0,5,7,0,4,1]]

    def bass_note(freq, dur, vel, chaos_lvl):
        t = ta(dur)
        n = len(t)
        saw = sawtooth(2*np.pi*freq*(1+rng.uniform(-.003,.003))*t)
        sub = np.sin(2*np.pi*freq*.5*t)*.4
        raw = saw*.6+sub*.4
        cutoff = 45+20*(vel>.8)+chaos_lvl*1500
        raw = _lp(raw, cutoff)
        mid = _bp(raw, 150, 800)
        raw += ws(mid*3, 4)*.3
        raw = ws(raw*1.5*vel, 2.5+chaos_lvl*1.5)
        amp = np.ones(n)
        atk = min(int(rng.uniform(10,35)), n)
        amp[:atk] = np.linspace(0,1,atk)
        dec = int(n*(.65+rng.random()*.15))
        if dec < n: amp[dec:] = np.linspace(1,.1,n-dec)
        return raw*amp*.65

    for bar in range(TOTAL_BARS):
        s = sec(bar)
        if is_silence(bar): continue
        if s in ('break','intro'): continue
        if bar < 6: continue

        c = ca(bar)

        # DROP 1/32 — bass also at 1/32!
        if is_drop32(bar):
            pat = [0,0,4,0, 0,0,7,0, 0,4,0,0, 0,0,4,7, 0,0,4,0, 0,0,7,0, 0,4,0,0, 0,0,4,7]
            for step in range(32):
                note = ROOT + pat[step % len(pat)]
                freq = nf(note)
                vel = .7 + (step/32)*.25
                b = bass_note(freq, S32*.85, vel, .5)
                pos = int((bar*BAR + step*S32)*SR)
                ast(L, R, b, max(0,pos), p=np.sin(step*.3)*.1)
            continue

        # DROP TRIPLETS
        if is_drop_trip(bar):
            trip = BEAT/6
            for step in range(24):
                note = ROOT + rng.choice([0,0,4,0,7,0])
                freq = nf(note)
                b = bass_note(freq, trip*.85, .75+rng.random()*.2, .5)
                pos = int((bar*BAR + step*trip)*SR)
                ast(L, R, b, max(0,pos), p=np.sin(step*.4)*.15)
            continue

        # ORDER
        if is_order(bar):
            pat = order_pats[bar % len(order_pats)]
        elif is_chaos(bar):
            pat = chaos_pats[bar % len(chaos_pats)]
            for i in range(16):
                if rng.random() < .15: pat[i] = rng.choice([0,1,4,5,7])
        else:
            pat = order_pats[0]

        for step in range(16):
            if is_chaos(bar) and rng.random() < .15: continue
            note = ROOT + pat[step % len(pat)]
            freq = nf(note)
            is_on = step%4==0
            delay = kick_tail*.6 if is_on and c < .5 else 0
            vel = .7+.25*(is_on)+rng.uniform(-.05,.05)
            b = bass_note(freq, S16*.82, vel, c)
            pos = int((bar*BAR + step*S16 + delay + rng.normal(0,.002+c*.004))*SR)
            ast(L, R, b, max(0,pos), p=np.sin(step*.25+bar*.07)*(.08+c*.15))

    return L, R


# ============================================================
# FM TEXTURES — chaos only
# ============================================================
def gen_fm():
    print("  [3/9] FM textures...")
    L = np.zeros(TOTAL_SAMPLES)
    R = np.zeros(TOTAL_SAMPLES)
    scale = [40,41,44,45,47,48,50,52,53,56,57,59,60,62,64,65,68]

    for bar in range(TOTAL_BARS):
        c = ca(bar)
        if c < .2: continue
        if is_silence(bar): continue
        if rng.random() > c*.8: continue

        n_notes = rng.randint(1, int(2+c*8))
        t_off = rng.uniform(0, BAR*.3)

        for _ in range(n_notes):
            note = scale[rng.randint(len(scale))]
            freq = nf(note + rng.choice([0,12,24]))
            dur = rng.uniform(.03, .1+c*.5)
            t = ta(dur)
            mr = rng.choice([1,1.5,2,3,4,5.33,7,11])
            mi = rng.uniform(.5,2)+c*10
            fm = fm_s(t, freq, freq*mr, mi)
            amp = adsr(t, a=.002, d=rng.uniform(.02,.15), s=.3, r=.05, dur=dur)
            fm = ws(fm*amp*.25*c, 2)*c
            pos = int((bar*BAR+t_off)*SR)
            ast(L, R, fm, max(0,pos), p=rng.uniform(-.7,.7))
            t_off += dur + rng.uniform(0, S16*2)

    return L*.5, R*.5


# ============================================================
# ELECTRICITY — chaos signature
# ============================================================
def gen_elec():
    print("  [4/9] Electricity...")
    L = np.zeros(TOTAL_SAMPLES)
    R = np.zeros(TOTAL_SAMPLES)

    for bar in range(TOTAL_BARS):
        c = ca(bar)
        if c < .5: continue
        if is_silence(bar): continue
        if rng.random() > c*.6: continue

        dur = rng.uniform(.3, 1+c*2)
        t = ta(dur)
        bf = nf(ROOT+rng.choice([0,12,7,5,24]))
        # Resonant filter sweep
        raw = ws(sawtooth(2*np.pi*bf*t)*2, 3)
        n = len(t)
        ch = max(1, n//512)
        cs = n//ch
        out = np.zeros(n)
        for i in range(ch):
            s, e = i*cs, min((i+1)*cs, n)
            sw = np.sin(2*np.pi*rng.uniform(.5,4)*i/ch*dur)*.5+.5
            fc = 200+rng.random()*500 + (5000+rng.random()*8000)*sw
            fc = np.clip(fc, 30, SR/2-100)
            bw = fc*(1-(.85+rng.random()*.12)*.95)
            lo, hi = max(fc-bw/2,20), min(fc+bw/2,SR/2-100)
            cc = raw[s:e]
            if lo < hi and len(cc) > 20:
                out[s:e] = _bp(cc, lo, hi, o=2)*4
            else:
                out[s:e] = cc
        amp = adsr(t, a=.01, d=.1, s=.6, r=.15, dur=dur)
        out = out*amp*.2*c
        pos = int((bar*BAR+rng.uniform(0,BAR*.5))*SR)
        ast(L, R, out, max(0,pos), p=rng.uniform(-.5,.5))

    return L*.5, R*.5


# ============================================================
# DRUMS — tight in order, sparse in chaos, NOTHING in silence
# ============================================================
def gen_drums():
    print("  [5/9] Drums...")
    L = np.zeros(TOTAL_SAMPLES)
    R = np.zeros(TOTAL_SAMPLES)

    for bar in range(TOTAL_BARS):
        if is_silence(bar): continue
        if sec(bar) in ('break','intro'): continue
        if bar < 8: continue
        c = ca(bar)

        # DROP sections: hats also at double speed
        if is_drop32(bar):
            for step in range(32):
                if step % 4 == 2:  # offbeat at 1/32
                    t = ta(S32*.5)
                    hat = _hp(rng.randn(len(t)), 7000+rng.random()*2000)
                    hat *= np.exp(-t*(30+rng.random()*20))*.25
                    pos = int((bar*BAR+step*S32)*SR)
                    ast(L, R, hat, max(0,pos), p=rng.uniform(-.3,.3))
            continue

        for step in range(16):
            timing = rng.normal(0, .003+c*.005)

            # Offbeat hat
            if step%4==2:
                prob = .95 if c < .3 else max(.3, .95-c*.6)
                if rng.random() < prob:
                    dur = S16*rng.uniform(.4,.7)
                    t = ta(dur)
                    hat = _hp(rng.randn(len(t)), 6000+rng.random()*3000)
                    hat *= np.exp(-t*(25+rng.random()*20))*rng.uniform(.18,.28)
                    pos = int((bar*BAR+step*S16+timing)*SR)
                    ast(L, R, hat, max(0,pos), p=.15+rng.uniform(-.1,.1))

            # Ghost
            elif step%2==1 and rng.random() < (.5-c*.2):
                dur = S16*rng.uniform(.2,.35)
                t = ta(dur)
                hat = _hp(rng.randn(len(t)), 8000+rng.random()*3000)
                hat *= np.exp(-t*(40+rng.random()*25))*rng.uniform(.06,.12)
                pos = int((bar*BAR+step*S16+timing)*SR)
                ast(L, R, hat, max(0,pos), p=rng.uniform(-.5,.5))

        # Clap
        if c < .5 and bar >= 12:
            for beat in [1,3]:
                t = ta(rng.uniform(.06,.1))
                clap = np.zeros(len(t))
                for i in range(rng.randint(2,5)):
                    d = int(i*SR*rng.uniform(.003,.007))
                    b = _bp(rng.randn(len(t)), 700+rng.random()*500, 4000+rng.random()*1500)
                    b *= np.exp(-t*(25+rng.random()*15))
                    if d < len(clap): clap[d:] += b[:len(clap)-d]*(.7**i)
                clap *= rng.uniform(.2,.35)
                pos = int((bar*BAR+beat*BEAT+rng.normal(0,.003))*SR)
                ast(L, R, clap, max(0,pos), p=rng.uniform(-.08,.08))

        # Tribal
        if bar%2==1 and bar>=16 and rng.random() < (.55 if c < .3 else .2):
            t = ta(rng.uniform(.08,.15))
            freq = rng.uniform(70,150)
            tom = np.sin(2*np.pi*freq*t*np.exp(-t*(3+rng.random()*4)))
            tom *= np.exp(-t*(8+rng.random()*6))*.3
            pos = int((bar*BAR+rng.uniform(2.5,3.8)*BEAT)*SR)
            ast(L, R, ws(tom,1.5), max(0,pos), p=rng.uniform(-.4,.4))

    return L, R


# ============================================================
# LEAD — matices de luz
# ============================================================
def gen_lead():
    print("  [6/9] Lead...")
    L = np.zeros(TOTAL_SAMPLES)
    R = np.zeros(TOTAL_SAMPLES)

    phrases = [
        [(64,.5,.8),(68,.75,1),(69,.25,.7),(71,1,1),(68,.5,.8)],
        [(76,.5,.9),(72,.5,.8),(71,.5,.7),(68,1.5,1)],
        [(80,1,.6),(76,.5,.7),(72,1,.9),(71,.5,.8),(68,1,1)],
        [(64,.5,.9),(62,.5,.8),(60,.5,.7),(64,.5,.8),(68,1,1),(72,1,.9)],
        [(71,.5,.9),(72,.5,1),(76,1,.8),(72,.5,.7),(68,1.5,1)],
    ]

    def mut(ph):
        p = list(ph)
        for i in range(len(p)):
            n,d,v = p[i]
            if rng.random() < .2: n += rng.choice([-3,-2,-1,1,2,3,4])
            if rng.random() < .12: d *= rng.uniform(.7,1.4)
            p[i] = (max(52,min(84,n)), d, np.clip(v*rng.uniform(.85,1.1),.3,1))
        return p

    pidx = 0
    for bar in range(TOTAL_BARS):
        show = False
        if is_order(bar) and bar >= 82: show = True
        if sec(bar) == 'break': show = True
        if is_silence(bar): continue
        if not show: continue
        if rng.random() < .12: continue

        ph = mut(phrases[pidx%len(phrases)]) if rng.random() > .3 else phrases[pidx%len(phrases)]
        t_off = 0

        for note, dur, vel in ph:
            freq = nf(note)
            nd = dur*BEAT*rng.uniform(.88,1.08)
            t = ta(nd)
            n = len(t)
            sp = rng.uniform(.003,.008)
            sm = np.zeros(n)
            for dt in [1-sp*2,1-sp,1,1+sp,1+sp*2]:
                sm += sawtooth(2*np.pi*freq*dt*t)
            sm /= 5
            fm_c = fm_s(t, freq, freq*rng.choice([2,3,4]), rng.uniform(.5,2))
            lead = sm*.7+fm_c*.3
            lead = _bp(lead, 300, min(freq*8,SR/2-100))
            amp = adsr(t, a=rng.uniform(.008,.025), d=.08, s=.7, r=.1, dur=nd)
            lead = ws(lead*1.2, 1.5)*amp*vel*.3
            pos = int((bar*BAR+t_off+rng.normal(0,.004))*SR)
            ast(L, R, lead, max(0,pos), p=.2+rng.uniform(-.1,.1))
            t_off += dur*BEAT

        pidx += 1

    # Delay
    dt = int(BEAT*.75*SR)
    for i in range(5):
        d = dt*(i+1)
        dc = .28**(i+1)
        if d < TOTAL_SAMPLES:
            if i%2==0: L[d:] += R[:TOTAL_SAMPLES-d]*dc*.35
            else: R[d:] += L[:TOTAL_SAMPLES-d]*dc*.35

    return L*.5, R*.5


# ============================================================
# ATMOSPHERE
# ============================================================
def gen_atmo():
    print("  [7/9] Atmosphere...")
    L = np.zeros(TOTAL_SAMPLES)
    R = np.zeros(TOTAL_SAMPLES)

    chords = [[52,56,59],[53,57,60],[57,60,64],[50,53,57],
              [56,59,62],[52,56,59],[48,52,56],[52,56,59]]

    for ci in range(TOTAL_BARS//4+1):
        sb = ci*4
        if sb >= TOTAL_BARS: break

        # Silence sections: no atmosphere either
        if is_silence(sb): continue

        ch = chords[ci%len(chords)]
        dur = min(4*BAR, (TOTAL_BARS-sb)*BAR)
        t = ta(dur)
        n = len(t)
        pL, pR = np.zeros(n), np.zeros(n)

        for i, note in enumerate(ch):
            freq = nf(note)
            det = rng.uniform(.002,.005)
            oL = np.sin(2*np.pi*freq*(1-det)*t)*.35
            oR = np.sin(2*np.pi*freq*(1+det)*t)*.35
            saw = _lp(sawtooth(2*np.pi*freq*t)*.2, min(freq*2.5,SR/2-100))
            lfo = .5+.5*np.sin(2*np.pi*(.06+i*.04)*t+rng.random()*6.28)
            pL += (oL+saw*.5)*lfo
            pR += (oR+saw*.5)*lfo

        pL /= len(ch); pR /= len(ch)
        fade = min(int(3*SR), n//3)
        pL[:fade] *= np.linspace(0,1,fade)
        pL[-fade:] *= np.linspace(1,0,fade)
        pR[:fade] *= np.linspace(0,1,fade)
        pR[-fade:] *= np.linspace(1,0,fade)

        vol = .45 if sec(sb) == 'break' else .3
        pos = int(sb*BAR*SR)
        end = min(pos+n, TOTAL_SAMPLES)
        nn = end-pos
        L[pos:end] += pL[:nn]*vol
        R[pos:end] += pR[:nn]*vol

    return L, R


# ============================================================
# GRANULAR — chaos textures
# ============================================================
def gen_gran(bass_mono, fm_mono):
    print("  [8/9] Granular...")
    L = np.zeros(TOTAL_SAMPLES)
    R = np.zeros(TOTAL_SAMPLES)

    sources = []
    for _ in range(10):
        s = int(rng.uniform(.1,.8)*len(bass_mono))
        cl = int(SR*rng.uniform(1,4))
        e = min(s+cl, len(bass_mono))
        if e-s > SR: sources.append(bass_mono[s:e])
    for _ in range(5):
        s = int(rng.uniform(.2,.9)*len(fm_mono))
        cl = int(SR*rng.uniform(.5,2))
        e = min(s+cl, len(fm_mono))
        if e-s > SR//2: sources.append(fm_mono[s:e])
    if not sources: sources = [rng.randn(SR*2)]

    for bar in range(TOTAL_BARS):
        c = ca(bar)
        if c < .3: continue
        if is_silence(bar): continue

        dens = 5+c*20
        src = sources[rng.randint(len(sources))]
        no = int(BAR*SR)
        oL, oR = np.zeros(no), np.zeros(no)
        ng = int(BAR*dens)
        for _ in range(ng):
            gd = rng.uniform(.008+rng.random()*.02, .04+rng.random()*.06)
            gs = int(gd*SR)
            if gs < 10 or gs > len(src): continue
            sp = rng.randint(0, max(1,len(src)-gs))
            g = src[sp:sp+gs].copy()
            p = rng.uniform(.3+rng.random()*.5, 1.5+rng.random()*1.5)
            nl = max(10, int(len(g)/p))
            g = resample(g, nl)
            g *= np.hanning(len(g))
            op = rng.randint(0, max(1,no-len(g)))
            sc = .1+c*.35
            pan = rng.uniform(-.8,.8)
            gL, gR = ps(g*sc, pan)
            end = min(op+len(gL), no)
            nn = end-op
            if nn > 0: oL[op:end] += gL[:nn]; oR[op:end] += gR[:nn]

        pos = int(bar*BAR*SR)
        end = min(pos+no, TOTAL_SAMPLES)
        nn = end-pos
        if nn > 0: L[pos:end] += oL[:nn]; R[pos:end] += oR[:nn]

    return L*.4, R*.4


# ============================================================
# FX
# ============================================================
def gen_fx():
    print("  [9/9] FX...")
    L = np.zeros(TOTAL_SAMPLES)
    R = np.zeros(TOTAL_SAMPLES)

    def riser(dur):
        t = ta(dur)
        n = len(t)
        noise = rng.randn(n)
        r = np.zeros(n)
        ch = 80
        cs = n//ch
        for i in range(ch):
            s, e = i*cs, min((i+1)*cs, n)
            fc = min(60+(16000*(i/ch)**2.5), SR/2-100)
            c = noise[s:e]
            if len(c) > 20: r[s:e] = _lp(c, fc)
        r *= np.linspace(0,1,n)**2
        return r*.3

    def impact():
        t = ta(1.2)
        noise = _lp(rng.randn(len(t)), 2000)*.3
        sub = np.sin(2*np.pi*ROOT_F*.5*t)*np.exp(-t*3)
        return (noise+sub*.7)*np.exp(-t*3.5)*.7

    # Risers before silences (building anticipation)
    for bar in range(TOTAL_BARS):
        if is_order(bar) and bar+1 < TOTAL_BARS and is_silence(bar+1):
            # 2-bar riser before the silence
            start_bar = max(0, bar - 1)
            r = riser(2*BAR)
            pos = int(start_bar*BAR*SR)
            ast(L, R, r, max(0,pos), p=0)

    # Impacts on drop entries
    imp = impact()
    for bar in range(TOTAL_BARS):
        if is_drop32(bar) and (bar == 0 or not is_drop(bar-1)):
            pos = int(bar*BAR*SR)
            ast(L, R, imp, max(0,pos), p=0)

    # Downlifters after chaos
    for bar in range(TOTAL_BARS):
        if is_silence(bar) and bar+1 < TOTAL_BARS and is_order(bar+1):
            t = ta(BAR)  # 1 bar downlifter leading into order
            n = len(t)
            noise = rng.randn(n)
            dl = np.zeros(n)
            chs = 20
            cs = n//chs
            for i in range(chs):
                s, e = i*cs, min((i+1)*cs, n)
                fc = max(min(10000-9500*(i/chs), SR/2-100), 30)
                c = noise[s:e]
                if len(c) > 20: dl[s:e] = _lp(c, fc)
            dl *= np.linspace(1,0,n)**.8*.15
            # This plays DURING the silence bar — only the noise sweep
            pos = int(bar*BAR*SR)
            ast(L, R, dl, max(0,pos), p=rng.uniform(-.3,.3))

    return L, R


# ============================================================
# RENDER
# ============================================================
print("\nSintetizando...")

kick_L, kick_R = gen_kick()
bass_L, bass_R = gen_bass()
fm_L, fm_R = gen_fm()
elec_L, elec_R = gen_elec()
drums_L, drums_R = gen_drums()
lead_L, lead_R = gen_lead()
atmo_L, atmo_R = gen_atmo()
gran_L, gran_R = gen_gran(bass_L+bass_R, fm_L+fm_R)
fx_L, fx_R = gen_fx()

print("\nMezclando...")
mL = np.zeros(TOTAL_SAMPLES)
mR = np.zeros(TOTAL_SAMPLES)

mL += kick_L*.90;  mR += kick_R*.90
mL += bass_L*.85;  mR += bass_R*.85
mL += fm_L*.50;    mR += fm_R*.50
mL += elec_L*.45;  mR += elec_R*.45
mL += drums_L*.55; mR += drums_R*.55
mL += lead_L*.52;  mR += lead_R*.52
mL += atmo_L*.40;  mR += atmo_R*.40
mL += gran_L*.38;  mR += gran_R*.38
mL += fx_L*.48;    mR += fx_R*.48

# Light sidechain
print("Sidechain...")
km = (kick_L+kick_R)/2
ke = np.abs(km)
w = int(.03*SR)
ks = np.convolve(ke, np.ones(w)/w, mode='same')
ks /= (np.max(ks)+1e-10)
sc = 1-ks*.15
nkL = mL-kick_L*.90; nkR = mR-kick_R*.90
mL = kick_L*.90+nkL*sc; mR = kick_R*.90+nkR*sc

# MASTER
print("Masterizando...")
mL = _hp(mL, 25); mR = _hp(mR, 25)
sL = _lp(mL,60); sR = _lp(mR,60)
mL -= sL*.35; mR -= sR*.35
m1L = _bp(mL,200,600); m1R = _bp(mR,200,600)
mL += m1L*.4; mR += m1R*.4
m2L = _bp(mL,600,2000); m2R = _bp(mR,600,2000)
mL += m2L*.35; mR += m2R*.35
pL = _bp(mL,2000,6000); pR = _bp(mR,2000,6000)
mL += pL*.25; mR += pR*.25
aL = _bp(mL,6000,16000); aR = _bp(mR,6000,16000)
mL += aL*.15; mR += aR*.15
mL = ws(mL, 1.8); mR = ws(mR, 1.8)

pk = max(np.max(np.abs(mL)), np.max(np.abs(mR)))
if pk > 0: mL /= pk; mR /= pk
rms = np.sqrt(np.mean(mL**2+mR**2)/2)
tgt = 10**(-9/20)
if rms > 0:
    g = min(tgt/rms, 3)
    mL *= g; mR *= g
mL = np.clip(mL,-.98,.98); mR = np.clip(mR,-.98,.98)

# SAVE
print("Guardando...")
stereo = np.column_stack([(mL*32767).astype(np.int16),(mR*32767).astype(np.int16)])
output = os.path.join(OUTPUT_DIR, "DarkPsy_v6_THE_DROP.wav")
wavfile.write(output, SR, stereo)

import shutil
desktop = "C:/Users/Juan/Desktop/DarkPsy_v6_THE_DROP.wav"
shutil.copy2(output, desktop)

# Verify
print("\n--- Verificacion ---")
mc = (mL+mR)/2
fft_c = np.abs(np.fft.rfft(mc))
freqs_c = np.fft.rfftfreq(len(mc), 1/SR)
te = np.sum(fft_c**2)
for nm,lo,hi in [('Sub',20,60),('Bass',60,200),('LowMid',200,600),('Mid',600,2000),
                  ('HiMid',2000,6000),('Pres',6000,10000),('Air',10000,20000)]:
    mask = (freqs_c>=lo)&(freqs_c<hi)
    print(f'  {nm:8s}: {np.sum(fft_c[mask]**2)/te*100:5.1f}%')
rms_f = np.sqrt(np.mean(mc**2))
print(f'  RMS: {20*np.log10(rms_f+1e-10):.1f} dB')

# Entropy by section
ents_o, ents_c = [], []
for i in range(0, len(mc)-SR, SR):
    f = mc[i:i+SR]
    ff = np.abs(np.fft.rfft(f))
    ff = ff/(np.sum(ff)+1e-10)
    ff = ff[ff>0]
    ent = -np.sum(ff*np.log2(ff))
    bar_a = int(i/(BAR*SR))
    if bar_a < TOTAL_BARS:
        if is_order(bar_a): ents_o.append(ent)
        elif is_chaos(bar_a): ents_c.append(ent)

print(f'  Entropy ORDER: {np.mean(ents_o):.2f} bits' if ents_o else '  No order data')
print(f'  Entropy CHAOS: {np.mean(ents_c):.2f} bits' if ents_c else '  No chaos data')
if ents_o and ents_c:
    print(f'  Contrast: {np.mean(ents_c)-np.mean(ents_o):.2f} bits (should be positive)')

# Count silences
n_silence = sum(1 for b in range(TOTAL_BARS) if is_silence(b))
n_drops = sum(1 for b in range(TOTAL_BARS) if is_drop(b))
print(f'  Silence bars: {n_silence}')
print(f'  Drop bars: {n_drops}')

print(f"\n{'='*60}")
print(f" TRACK: {desktop}")
print(f" {TOTAL_TIME/60:.1f} min | {n_silence} silencios | {n_drops} drops")
print(f" ORDER -> SILENCE -> DROP(1/32) -> CHAOS -> repeat")
print(f"{'='*60}")
