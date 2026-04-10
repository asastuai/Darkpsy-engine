"""
DARK PSYTRANCE v7 — MUSICAL DROPS
The drop is not a machine gun. It's a re-entry with INTENTION.

Silence creates the question. The drop answers it.
The answer starts quiet and BUILDS within the phrase.

Drop anatomy:
1. Silence (1 bar)
2. Single kick, alone, almost shy
3. Bass joins, rhythm tightens
4. By beat 3-4 you're back in the groove but HARDER
5. Energy carries into next section with momentum
"""

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt, sawtooth, square, resample
import os, sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
SR = 44100
BPM = 150
BEAT = 60.0 / BPM
BAR = BEAT * 4
S16 = BEAT / 4
TOTAL_BARS = 280  # ~7.5 min
TOTAL_TIME = TOTAL_BARS * BAR
TOTAL_SAMPLES = int(TOTAL_TIME * SR)

print("=" * 60)
print(" DARK PSYTRANCE v7 - MUSICAL DROPS")
print(f" BPM: {BPM} | Bars: {TOTAL_BARS} | Duration: {TOTAL_TIME/60:.1f} min")
print("=" * 60)

rng = np.random.RandomState(666)

# ============================================================
# DSP
# ============================================================
def ta(d): return np.linspace(0, d, int(d*SR), endpoint=False)
def _lp(s,fc,o=4):
    return sosfilt(butter(o,np.clip(fc,20,SR/2-100),btype='low',fs=SR,output='sos'),s)
def _hp(s,fc,o=2):
    return sosfilt(butter(o,np.clip(fc,20,SR/2-100),btype='high',fs=SR,output='sos'),s)
def _bp(s,lo,hi,o=2):
    lo,hi=max(lo,20),min(hi,SR/2-100)
    if lo>=hi: return s
    return sosfilt(butter(o,[lo,hi],btype='band',fs=SR,output='sos'),s)
def _notch(s,fc,q=8):
    lo,hi=max(fc-fc/q,20),min(fc+fc/q,SR/2-100)
    if lo>=hi: return s
    return s-_bp(s,lo,hi,o=2)*.85
def nf(n): return 440*(2**((n-69)/12))
def ws(s,a=2): return np.tanh(s*a)/np.tanh(a)
def adsr(t,a=.01,d=.1,s=.7,r=.2,dur=None):
    if dur is None: dur=t[-1] if len(t) else 1
    e=np.zeros_like(t)
    for i,ti in enumerate(t):
        if ti<a: e[i]=ti/a if a>0 else 1
        elif ti<a+d: e[i]=1-(1-s)*(ti-a)/d
        elif ti<dur-r: e[i]=s
        else: e[i]=s*max(0,(dur-ti)/r) if r>0 else 0
    return e
def ps(m,p=0):
    return m*np.cos((p+1)/2*np.pi/2), m*np.sin((p+1)/2*np.pi/2)
def ast(oL,oR,m,pos,p=0):
    L,R=ps(m,p)
    end=min(pos+len(L),len(oL))
    n=end-pos
    if n>0 and pos>=0: oL[pos:end]+=L[:n]; oR[pos:end]+=R[:n]
def fm_s(t,cf,mf,mi):
    return np.sin(2*np.pi*cf*t+np.sin(2*np.pi*mf*t)*mi)

ROOT=40; ROOT_F=nf(ROOT)


# ============================================================
# DROP TYPES — musical re-entries
# ============================================================
# Each drop is a function that returns (kick_hits, bass_hits) for 2 bars
# Format: list of (beat_position_in_bars, velocity, character)

def drop_gradual():
    """Shy re-entry: single kick, then builds"""
    kicks = [
        # Bar 0: sparse, building
        (0.0, 0.6, 'soft'),       # one kick, alone
        (1.5, 0.5, 'soft'),       # another, off-grid (surprise)
        (2.0, 0.7, 'normal'),     # beat 3, getting confident
        (2.5, 0.65, 'normal'),    # and-of-3
        (3.0, 0.8, 'normal'),     # beat 4
        (3.5, 0.75, 'normal'),    # and-of-4
        (3.75, 0.85, 'hard'),     # pickup into bar 2
        # Bar 1: full groove restored with extra energy
        (4.0, 0.95, 'hard'),
        (5.0, 0.9, 'normal'),
        (6.0, 0.9, 'normal'),
        (7.0, 0.85, 'normal'),
    ]
    return kicks

def drop_dramatic():
    """Big impact, then groove"""
    kicks = [
        # Bar 0: impact then space
        (0.0, 1.0, 'hard'),       # BIG hit
        # ... silence for a beat ...
        (2.0, 0.75, 'normal'),    # comes back mid-bar
        (3.0, 0.8, 'normal'),
        (3.5, 0.85, 'normal'),
        (3.75, 0.9, 'hard'),
        # Bar 1: full
        (4.0, 0.95, 'hard'),
        (5.0, 0.9, 'normal'),
        (6.0, 0.9, 'normal'),
        (7.0, 0.85, 'normal'),
    ]
    return kicks

def drop_stutter():
    """Quick stutter that resolves into groove"""
    kicks = [
        # Bar 0: stutter rhythm (not machine gun — musical)
        (0.0, 0.85, 'hard'),
        (0.25, 0.6, 'soft'),      # quick double
        (1.0, 0.8, 'normal'),
        (1.75, 0.5, 'soft'),      # ghost
        (2.0, 0.85, 'normal'),
        (2.5, 0.7, 'normal'),
        (3.0, 0.9, 'hard'),
        (3.5, 0.8, 'normal'),
        # Bar 1: locked
        (4.0, 0.9, 'hard'),
        (5.0, 0.85, 'normal'),
        (6.0, 0.85, 'normal'),
        (7.0, 0.85, 'normal'),
    ]
    return kicks

def drop_rolling():
    """Bass-led: kick comes back with rolling energy"""
    kicks = [
        # Bar 0: kick comes back with increasing density
        (0.0, 0.7, 'normal'),
        (1.0, 0.75, 'normal'),
        (2.0, 0.8, 'normal'),
        (2.5, 0.7, 'soft'),       # starts filling in
        (3.0, 0.85, 'normal'),
        (3.25, 0.6, 'soft'),      # more fills
        (3.5, 0.9, 'hard'),
        (3.75, 0.7, 'soft'),
        # Bar 1: full groove
        (4.0, 0.95, 'hard'),
        (5.0, 0.9, 'normal'),
        (6.0, 0.9, 'normal'),
        (7.0, 0.85, 'normal'),
    ]
    return kicks

def drop_triplet_resolve():
    """Triplet rhythm that resolves into 4/4"""
    trip = BEAT  # triplet grid
    kicks = [
        # Bar 0: triplet feel
        (0.0, 0.8, 'hard'),
        (0.667, 0.6, 'soft'),     # triplet
        (1.333, 0.7, 'normal'),   # triplet
        (2.0, 0.85, 'hard'),
        (2.667, 0.65, 'soft'),
        (3.333, 0.8, 'normal'),
        (3.667, 0.7, 'soft'),     # resolving...
        # Bar 1: resolved to 4/4
        (4.0, 0.95, 'hard'),      # LOCKED
        (5.0, 0.9, 'normal'),
        (6.0, 0.9, 'normal'),
        (7.0, 0.85, 'normal'),
    ]
    return kicks

DROP_TYPES = [drop_gradual, drop_dramatic, drop_stutter, drop_rolling, drop_triplet_resolve]


# ============================================================
# SECTION MAP
# ============================================================
smap = {}
def ss(start, end, typ):
    for b in range(start, min(end, TOTAL_BARS)):
        smap[b] = typ

# Track structure with musical drops
# intro
ss(0, 10, 'intro')

# ORDER 1 — establish groove (20 bars of pure dance)
ss(10, 30, 'order')

# Moment 1: first silence + musical drop
ss(30, 31, 'silence')
ss(31, 33, 'drop')  # 2 bars of musical re-entry
ss(33, 42, 'chaos')

# Return to order
ss(42, 43, 'silence')
ss(43, 45, 'drop')
ss(45, 70, 'order')  # long dance section

# Moment 2: bigger
ss(70, 71, 'silence')
ss(71, 73, 'drop')
ss(73, 88, 'chaos')  # longer chaos

# ORDER 3 — the big groove, lead enters
ss(88, 89, 'silence')
ss(89, 91, 'drop')
ss(91, 120, 'order')

# Moment 3: CLIMAX drop
ss(120, 122, 'silence')  # 2 bars silence — HUGE tension
ss(122, 124, 'drop')
ss(124, 148, 'chaos')   # peak madness

# Breakdown — breathing
ss(148, 149, 'silence')
ss(149, 165, 'break')

# Build
ss(165, 175, 'build')

# ORDER 4 — resolution
ss(175, 176, 'silence')
ss(176, 178, 'drop')
ss(178, 210, 'order')

# Final chaos
ss(210, 211, 'silence')
ss(211, 213, 'drop')
ss(213, 240, 'chaos')

# Final return
ss(240, 241, 'silence')
ss(241, 243, 'drop')
ss(243, 268, 'order')  # wind down

ss(268, TOTAL_BARS, 'outro')

for b in range(TOTAL_BARS):
    if b not in smap: smap[b] = 'order'

def sec(b): return smap.get(b,'order')

# Track which drop type to use for each drop moment
drop_moments = {}
drop_idx = 0
for b in range(TOTAL_BARS):
    if sec(b) == 'drop' and (b == 0 or sec(b-1) != 'drop'):
        drop_moments[b] = DROP_TYPES[drop_idx % len(DROP_TYPES)]
        drop_idx += 1

def ca(b):
    s=sec(b)
    if s=='order': return 0.0
    if s=='chaos': return 1.0
    if s=='drop': return 0.4
    if s=='silence': return 0.0
    if s=='break': return 0.1
    if s=='build':
        bs=b
        while bs>0 and sec(bs-1)=='build': bs-=1
        be=b
        while be<TOTAL_BARS and sec(be)=='build': be+=1
        return 0.1+0.6*(b-bs)/max(be-bs,1)
    if s=='intro': return 0.05
    if s=='outro': return 0.05
    return 0.3

# Print structure
print("\nESTRUCTURA:")
prev=''
for b in range(TOTAL_BARS):
    s=sec(b)
    if s!=prev:
        e=b
        while e<TOTAL_BARS and sec(e)==s: e+=1
        labels={'intro':'INTRO','order':'>>> ORDER (DANCE)','chaos':'*** CHAOS (MIND)',
                'silence':'[SILENCE]','drop':'>> DROP (musical re-entry)',
                'break':'... BREAKDOWN','build':'^^ BUILD','outro':'OUTRO'}
        ts=b*BAR/60; te=e*BAR/60
        print(f"  {b:3d}-{e-1:3d} ({ts:.1f}-{te:.1f}m): {labels.get(s,s)}")
        prev=s


# ============================================================
# KICK
# ============================================================
def gen_kick():
    print("\n  [1/9] Kick...")
    L=np.zeros(TOTAL_SAMPLES); R=np.zeros(TOTAL_SAMPLES)

    def mk(vel=.85, char='normal'):
        t=ta(0.2); n=len(t)
        var = {'soft':0, 'normal':1, 'hard':2}[char]
        click_vol = {'soft':.2, 'normal':.4, 'hard':.7}[char]
        click_freq = {'soft':2000, 'normal':3000, 'hard':4500}[char]

        cl=_bp(rng.randn(n), click_freq, click_freq+4000, o=2)*2.5
        cl*=np.exp(-t*100)*click_vol
        d=int(SR*.002)
        pitch=ROOT_F+(200+var*60)*np.exp(-t*(50+var*8))
        body=np.sin(2*np.pi*np.cumsum(pitch)/SR)*np.exp(-t*(11+var*2))*.8
        k=body.copy()
        if d<n: k[d:]+=cl[:n-d]*.6
        k=_notch(k,300,q=8); k=_hp(k,28)
        return ws(k*vel*1.3, 1.8+var*.4)*.9

    for bar in range(TOTAL_BARS):
        s=sec(bar)

        if s=='silence': continue
        if s in ('break','intro','outro') and s!='outro': continue

        # MUSICAL DROP — use the pre-designed pattern
        if s == 'drop':
            # Find which drop moment this belongs to
            db = bar
            while db > 0 and sec(db-1) == 'drop': db -= 1
            bar_in_drop = bar - db

            if db in drop_moments:
                pattern = drop_moments[db]()
                for beat_pos, vel, char in pattern:
                    # beat_pos is in beats, bars 0-1 mapped to bar_in_drop
                    target_bar = int(beat_pos // 4)
                    if target_bar != bar_in_drop: continue
                    beat_in_bar = beat_pos - target_bar * 4

                    timing = rng.normal(0, 0.003)
                    kick = mk(vel=vel, char=char)
                    pos = int((bar*BAR + beat_in_bar*BEAT + timing)*SR)
                    ast(L, R, kick, max(0,pos), p=rng.uniform(-.03,.03))
            continue

        # ORDER — locked 4/4
        if s == 'order':
            for beat in range(4):
                if beat!=0 and rng.random()<.02: continue
                vel=.80+rng.random()*.15
                kick=mk(vel=vel, char='normal')
                pos=int((bar*BAR+beat*BEAT+rng.normal(0,.002))*SR)
                ast(L,R,kick,max(0,pos),p=rng.uniform(-.03,.03))

            # Fill on last bar before silence: accelerating musical fill
            if bar+1<TOTAL_BARS and sec(bar+1)=='silence':
                # Musical fill: starts normal, gets denser toward end
                fills = [
                    (2.25, .6, 'soft'), (2.75, .7, 'normal'),
                    (3.25, .75, 'normal'), (3.5, .8, 'hard'),
                    (3.625, .7, 'soft'), (3.75, .85, 'hard'),
                    (3.875, .9, 'hard'),
                ]
                for fp, fv, fc in fills:
                    kick=mk(vel=fv, char=fc)
                    pos=int((bar*BAR+fp*BEAT)*SR)
                    ast(L,R,kick,max(0,pos),p=rng.uniform(-.04,.04))
            continue

        # CHAOS — irregular but musical
        if s == 'chaos':
            # Not random positions — musical irregular patterns
            chaos_patterns = [
                [0, 1.5, 2, 3, 3.5],
                [0, 0.75, 2, 2.75, 3.5],
                [0, 1, 2, 2.5, 3, 3.75],
                [0, 0.5, 1.5, 2, 3],
                [0, 1, 1.75, 2.5, 3, 3.25, 3.75],
                [0, 2, 2.25, 3, 3.5, 3.75],
            ]
            pat = chaos_patterns[bar % len(chaos_patterns)]
            for bp_pos in pat:
                vel = .6 + rng.random()*.35
                char = 'hard' if rng.random() > .6 else 'normal'
                kick = mk(vel=vel, char=char)
                pos = int((bar*BAR + bp_pos*BEAT + rng.normal(0,.004))*SR)
                ast(L,R,kick,max(0,pos),p=rng.uniform(-.05,.05))
            continue

        # BUILD
        if s == 'build':
            progress = ca(bar)
            # Start 2-beat, transition to 4-beat, then add pickups
            if progress < .3:
                beats = [0, 2]
            elif progress < .6:
                beats = [0, 1, 2, 3]
            else:
                beats = [0, 1, 2, 2.5, 3, 3.5]
            for bp_pos in beats:
                vel = .6 + progress * .3
                kick = mk(vel=vel, char='normal' if progress < .7 else 'hard')
                pos = int((bar*BAR + bp_pos*BEAT + rng.normal(0,.003))*SR)
                ast(L,R,kick,max(0,pos),p=rng.uniform(-.03,.03))

        # OUTRO
        if s == 'outro':
            bar_in_outro = bar - 268
            if bar_in_outro < 4:
                beats = [0,1,2,3]
            elif bar_in_outro < 8:
                beats = [0,2]
            else:
                beats = [0] if bar_in_outro % 2 == 0 else []
            for beat in beats:
                kick = mk(vel=.7-.03*bar_in_outro, char='soft')
                pos = int((bar*BAR+beat*BEAT)*SR)
                ast(L,R,kick,max(0,pos),p=0)

    return L, R


# ============================================================
# BASS — musical re-entry on drops
# ============================================================
def gen_bass():
    print("  [2/9] Bass...")
    L=np.zeros(TOTAL_SAMPLES); R=np.zeros(TOTAL_SAMPLES)
    kick_tail=.05
    order_pats=[[0]*16,[0,0,4,0,0,0,4,0,0,0,0,0,0,0,4,0],[0,0,0,0,0,0,4,0,0,0,0,0,0,0,7,0]]
    chaos_pats=[[0,1,4,7,5,0,1,4,7,5,0,1,4,7,5,0],[7,0,4,1,0,5,7,0,4,1,0,5,7,0,4,1],
                [0,4,0,7,0,1,0,5,0,4,0,7,0,1,0,5]]

    def bn(freq,dur,vel,chaos_lvl):
        t=ta(dur); n=len(t)
        saw=sawtooth(2*np.pi*freq*(1+rng.uniform(-.003,.003))*t)
        sub=np.sin(2*np.pi*freq*.5*t)*.4
        raw=saw*.6+sub*.4
        cutoff=45+20*(vel>.8)+chaos_lvl*1500
        raw=_lp(raw,cutoff)
        mid=_bp(raw,150,800)
        raw+=ws(mid*3,4)*.3
        raw=ws(raw*1.5*vel,2.5+chaos_lvl*1.5)
        amp=np.ones(n)
        atk=min(int(rng.uniform(10,35)),n)
        amp[:atk]=np.linspace(0,1,atk)
        dec=int(n*(.65+rng.random()*.15))
        if dec<n: amp[dec:]=np.linspace(1,.1,n-dec)
        return raw*amp*.65

    for bar in range(TOTAL_BARS):
        s=sec(bar)
        if s=='silence': continue
        if s in ('break','intro'): continue
        if bar < 6: continue
        c=ca(bar)

        # DROP — bass also re-enters musically
        if s=='drop':
            db=bar
            while db>0 and sec(db-1)=='drop': db-=1
            bar_in_drop=bar-db

            if bar_in_drop==0:
                # First bar: sparse bass, just root, following kick
                sparse_steps=[0,4,8,12]  # on the beats only
                for step in sparse_steps:
                    if rng.random()<.3: continue  # some missing
                    freq=nf(ROOT)
                    b=bn(freq,S16*.8,.5+bar_in_drop*.2,0)
                    pos=int((bar*BAR+step*S16+kick_tail*.6)*SR)
                    ast(L,R,b,max(0,pos),p=0)
            else:
                # Second bar: full rolling bass
                pat=order_pats[1]
                for step in range(16):
                    freq=nf(ROOT+pat[step])
                    vel=.7+.2*(step%4==0)
                    b=bn(freq,S16*.82,vel,0)
                    pos=int((bar*BAR+step*S16+kick_tail*.4)*SR)
                    ast(L,R,b,max(0,pos),p=np.sin(step*.25)*.08)
            continue

        # ORDER
        if s=='order':
            pat=order_pats[bar%len(order_pats)]
        elif s=='chaos':
            pat=chaos_pats[bar%len(chaos_pats)]
            # Mutate
            pat=list(pat)
            for i in range(16):
                if rng.random()<.12: pat[i]=rng.choice([0,1,4,5,7])
        elif s=='build':
            pat=order_pats[0]
        elif s=='outro':
            pat=order_pats[0]
        else:
            pat=order_pats[0]

        for step in range(16):
            if s=='chaos' and rng.random()<.12: continue
            if s=='outro':
                bar_in_outro=bar-268
                if bar_in_outro > 8 and step%4!=0: continue

            note=ROOT+pat[step%len(pat)]
            freq=nf(note)
            is_on=step%4==0
            delay=kick_tail*.6 if is_on and c<.5 else 0
            vel=.7+.25*(is_on)+rng.uniform(-.05,.05)
            b=bn(freq,S16*.82,vel,c)
            pos=int((bar*BAR+step*S16+delay+rng.normal(0,.002+c*.004))*SR)
            ast(L,R,b,max(0,pos),p=np.sin(step*.25+bar*.07)*(.08+c*.15))

    return L, R


# ============================================================
# FM TEXTURES
# ============================================================
def gen_fm():
    print("  [3/9] FM textures...")
    L=np.zeros(TOTAL_SAMPLES); R=np.zeros(TOTAL_SAMPLES)
    scale=[40,41,44,45,47,48,50,52,53,56,57,59,60,62,64,65,68]

    for bar in range(TOTAL_BARS):
        c=ca(bar)
        if c<.15 or sec(bar)=='silence': continue
        if rng.random()>c*.85: continue

        n_notes=rng.randint(1,int(2+c*10))
        t_off=rng.uniform(0,BAR*.3)

        for _ in range(n_notes):
            note=scale[rng.randint(len(scale))]
            freq=nf(note+rng.choice([0,12,24]))
            dur=rng.uniform(.03,.1+c*.6)
            t=ta(dur)
            mr=rng.choice([1,1.5,2,3,4,5.33,7,11])
            mi=rng.uniform(.5,2)+c*12
            fm=fm_s(t,freq,freq*mr,mi)
            amp=adsr(t,a=.002,d=rng.uniform(.02,.15),s=.3,r=.05,dur=dur)
            fm=ws(fm*amp*.3*c,2)*c
            pos=int((bar*BAR+t_off)*SR)
            ast(L,R,fm,max(0,pos),p=rng.uniform(-.7,.7))
            t_off+=dur+rng.uniform(0,S16*2)

    return L*.55, R*.55


# ============================================================
# ELECTRICITY
# ============================================================
def gen_elec():
    print("  [4/9] Electricity...")
    L=np.zeros(TOTAL_SAMPLES); R=np.zeros(TOTAL_SAMPLES)

    for bar in range(TOTAL_BARS):
        c=ca(bar)
        if c<.4 or sec(bar)=='silence': continue
        if rng.random()>c*.65: continue

        dur=rng.uniform(.3,1+c*2.5)
        t=ta(dur)
        bf=nf(ROOT+rng.choice([0,12,7,5,24]))
        raw=ws(sawtooth(2*np.pi*bf*t)*2,3)
        n=len(t)
        ch=max(1,n//512); cs=n//ch
        out=np.zeros(n)
        for i in range(ch):
            s,e=i*cs,min((i+1)*cs,n)
            sw=np.sin(2*np.pi*rng.uniform(.5,4)*i/ch*dur)*.5+.5
            fc=200+rng.random()*500+(5000+rng.random()*8000)*sw
            fc=np.clip(fc,30,SR/2-100)
            bw=fc*(1-rng.uniform(.85,.97)*.95)
            lo,hi=max(fc-bw/2,20),min(fc+bw/2,SR/2-100)
            cc=raw[s:e]
            if lo<hi and len(cc)>20: out[s:e]=_bp(cc,lo,hi,o=2)*4
            else: out[s:e]=cc
        amp=adsr(t,a=.01,d=.1,s=.6,r=.15,dur=dur)
        out=out*amp*.2*c
        pos=int((bar*BAR+rng.uniform(0,BAR*.5))*SR)
        ast(L,R,out,max(0,pos),p=rng.uniform(-.5,.5))

    return L*.55, R*.55


# ============================================================
# DRUMS
# ============================================================
def gen_drums():
    print("  [5/9] Drums...")
    L=np.zeros(TOTAL_SAMPLES); R=np.zeros(TOTAL_SAMPLES)

    for bar in range(TOTAL_BARS):
        s=sec(bar)
        if s in ('silence','break','intro'): continue
        if bar<10: continue
        c=ca(bar)

        # Drop drums: minimal, just a few hats
        if s=='drop':
            db=bar
            while db>0 and sec(db-1)=='drop': db-=1
            bar_in_drop=bar-db
            if bar_in_drop==1:
                # Second bar: hats come back
                for step in range(16):
                    if step%4==2 and rng.random()<.7:
                        t=ta(S16*.5)
                        hat=_hp(rng.randn(len(t)),7000)
                        hat*=np.exp(-t*30)*.2
                        pos=int((bar*BAR+step*S16)*SR)
                        ast(L,R,hat,max(0,pos),p=.15)
            continue

        for step in range(16):
            timing=rng.normal(0,.003+c*.005)

            if step%4==2:
                prob=.95 if c<.3 else max(.3,.95-c*.6)
                if rng.random()<prob:
                    dur=S16*rng.uniform(.4,.7)
                    t=ta(dur)
                    hat=_hp(rng.randn(len(t)),6000+rng.random()*3000)
                    hat*=np.exp(-t*(25+rng.random()*20))*rng.uniform(.18,.28)
                    pos=int((bar*BAR+step*S16+timing)*SR)
                    ast(L,R,hat,max(0,pos),p=.15+rng.uniform(-.1,.1))

            elif step%2==1 and rng.random()<(.5-c*.2):
                dur=S16*rng.uniform(.2,.35)
                t=ta(dur)
                hat=_hp(rng.randn(len(t)),8000+rng.random()*3000)
                hat*=np.exp(-t*(40+rng.random()*25))*rng.uniform(.06,.12)
                pos=int((bar*BAR+step*S16+timing)*SR)
                ast(L,R,hat,max(0,pos),p=rng.uniform(-.5,.5))

        if c<.5 and bar>=12:
            for beat in [1,3]:
                t=ta(rng.uniform(.06,.1))
                clap=np.zeros(len(t))
                for i in range(rng.randint(2,5)):
                    d=int(i*SR*rng.uniform(.003,.007))
                    b=_bp(rng.randn(len(t)),700+rng.random()*500,4000+rng.random()*1500)
                    b*=np.exp(-t*(25+rng.random()*15))
                    if d<len(clap): clap[d:]+=b[:len(clap)-d]*(.7**i)
                clap*=rng.uniform(.2,.35)
                pos=int((bar*BAR+beat*BEAT+rng.normal(0,.003))*SR)
                ast(L,R,clap,max(0,pos),p=rng.uniform(-.08,.08))

        if bar%2==1 and bar>=16 and rng.random()<(.55 if c<.3 else .25):
            t=ta(rng.uniform(.08,.15))
            freq=rng.uniform(70,150)
            tom=np.sin(2*np.pi*freq*t*np.exp(-t*(3+rng.random()*4)))
            tom*=np.exp(-t*(8+rng.random()*6))*.3
            pos=int((bar*BAR+rng.uniform(2.5,3.8)*BEAT)*SR)
            ast(L,R,ws(tom,1.5),max(0,pos),p=rng.uniform(-.4,.4))

    return L, R


# ============================================================
# LEAD
# ============================================================
def gen_lead():
    print("  [6/9] Lead...")
    L=np.zeros(TOTAL_SAMPLES); R=np.zeros(TOTAL_SAMPLES)
    phrases=[
        [(64,.5,.8),(68,.75,1),(69,.25,.7),(71,1,1),(68,.5,.8)],
        [(76,.5,.9),(72,.5,.8),(71,.5,.7),(68,1.5,1)],
        [(80,1,.6),(76,.5,.7),(72,1,.9),(71,.5,.8),(68,1,1)],
        [(64,.5,.9),(62,.5,.8),(60,.5,.7),(64,.5,.8),(68,1,1),(72,1,.9)],
        [(71,.5,.9),(72,.5,1),(76,1,.8),(72,.5,.7),(68,1.5,1)],
    ]
    def mut(ph):
        p=list(ph)
        for i in range(len(p)):
            n,d,v=p[i]
            if rng.random()<.2: n+=rng.choice([-3,-2,-1,1,2,3,4])
            if rng.random()<.12: d*=rng.uniform(.7,1.4)
            p[i]=(max(52,min(84,n)),d,np.clip(v*rng.uniform(.85,1.1),.3,1))
        return p

    pidx=0
    for bar in range(TOTAL_BARS):
        show=False
        if sec(bar)=='order' and bar>=91: show=True
        if sec(bar)=='break': show=True
        if sec(bar)=='silence': continue
        if not show: continue
        if rng.random()<.12: continue

        ph=mut(phrases[pidx%len(phrases)]) if rng.random()>.3 else phrases[pidx%len(phrases)]
        t_off=0
        for note,dur,vel in ph:
            freq=nf(note)
            nd=dur*BEAT*rng.uniform(.88,1.08)
            t=ta(nd); n=len(t)
            sp=rng.uniform(.003,.008)
            sm=np.zeros(n)
            for dt in [1-sp*2,1-sp,1,1+sp,1+sp*2]:
                sm+=sawtooth(2*np.pi*freq*dt*t)
            sm/=5
            fc=fm_s(t,freq,freq*rng.choice([2,3,4]),rng.uniform(.5,2))
            lead=sm*.7+fc*.3
            lead=_bp(lead,300,min(freq*8,SR/2-100))
            amp=adsr(t,a=rng.uniform(.008,.025),d=.08,s=.7,r=.1,dur=nd)
            lead=ws(lead*1.2,1.5)*amp*vel*.3
            pos=int((bar*BAR+t_off+rng.normal(0,.004))*SR)
            ast(L,R,lead,max(0,pos),p=.2+rng.uniform(-.1,.1))
            t_off+=dur*BEAT
        pidx+=1

    dt=int(BEAT*.75*SR)
    for i in range(5):
        d=dt*(i+1); dc=.28**(i+1)
        if d<TOTAL_SAMPLES:
            if i%2==0: L[d:]+=R[:TOTAL_SAMPLES-d]*dc*.35
            else: R[d:]+=L[:TOTAL_SAMPLES-d]*dc*.35
    return L*.5, R*.5


# ============================================================
# ATMOSPHERE
# ============================================================
def gen_atmo():
    print("  [7/9] Atmosphere...")
    L=np.zeros(TOTAL_SAMPLES); R=np.zeros(TOTAL_SAMPLES)
    chords=[[52,56,59],[53,57,60],[57,60,64],[50,53,57],
            [56,59,62],[52,56,59],[48,52,56],[52,56,59]]
    for ci in range(TOTAL_BARS//4+1):
        sb=ci*4
        if sb>=TOTAL_BARS: break
        if sec(sb)=='silence': continue
        ch=chords[ci%len(chords)]
        dur=min(4*BAR,(TOTAL_BARS-sb)*BAR)
        t=ta(dur); n=len(t)
        pL,pR=np.zeros(n),np.zeros(n)
        for i,note in enumerate(ch):
            freq=nf(note); det=rng.uniform(.002,.005)
            oL=np.sin(2*np.pi*freq*(1-det)*t)*.35
            oR=np.sin(2*np.pi*freq*(1+det)*t)*.35
            saw=_lp(sawtooth(2*np.pi*freq*t)*.2,min(freq*2.5,SR/2-100))
            lfo=.5+.5*np.sin(2*np.pi*(.06+i*.04)*t+rng.random()*6.28)
            pL+=(oL+saw*.5)*lfo; pR+=(oR+saw*.5)*lfo
        pL/=len(ch); pR/=len(ch)
        fade=min(int(3*SR),n//3)
        pL[:fade]*=np.linspace(0,1,fade); pL[-fade:]*=np.linspace(1,0,fade)
        pR[:fade]*=np.linspace(0,1,fade); pR[-fade:]*=np.linspace(1,0,fade)
        vol=.45 if sec(sb)=='break' else .3
        pos=int(sb*BAR*SR); end=min(pos+n,TOTAL_SAMPLES); nn=end-pos
        L[pos:end]+=pL[:nn]*vol; R[pos:end]+=pR[:nn]*vol
    return L, R


# ============================================================
# GRANULAR
# ============================================================
def gen_gran(bm, fm_m):
    print("  [8/9] Granular...")
    L=np.zeros(TOTAL_SAMPLES); R=np.zeros(TOTAL_SAMPLES)
    sources=[]
    for _ in range(10):
        s=int(rng.uniform(.1,.8)*len(bm)); cl=int(SR*rng.uniform(1,4))
        e=min(s+cl,len(bm))
        if e-s>SR: sources.append(bm[s:e])
    for _ in range(5):
        s=int(rng.uniform(.2,.9)*len(fm_m)); cl=int(SR*rng.uniform(.5,2))
        e=min(s+cl,len(fm_m))
        if e-s>SR//2: sources.append(fm_m[s:e])
    if not sources: sources=[rng.randn(SR*2)]

    for bar in range(TOTAL_BARS):
        c=ca(bar)
        if c<.3 or sec(bar)=='silence': continue
        dens=5+c*25; src=sources[rng.randint(len(sources))]
        no=int(BAR*SR); oL,oR=np.zeros(no),np.zeros(no)
        ng=int(BAR*dens)
        for _ in range(ng):
            gd=rng.uniform(.008,.06); gs=int(gd*SR)
            if gs<10 or gs>len(src): continue
            sp=rng.randint(0,max(1,len(src)-gs))
            g=src[sp:sp+gs].copy()
            p=rng.uniform(.3,2.5); nl=max(10,int(len(g)/p))
            g=resample(g,nl); g*=np.hanning(len(g))
            op=rng.randint(0,max(1,no-len(g)))
            sc=.1+c*.4; pan=rng.uniform(-.8,.8)
            gL,gR=ps(g*sc,pan)
            end=min(op+len(gL),no); nn=end-op
            if nn>0: oL[op:end]+=gL[:nn]; oR[op:end]+=gR[:nn]
        pos=int(bar*BAR*SR); end=min(pos+no,TOTAL_SAMPLES); nn=end-pos
        if nn>0: L[pos:end]+=oL[:nn]; R[pos:end]+=oR[:nn]
    return L*.45, R*.45


# ============================================================
# FX
# ============================================================
def gen_fx():
    print("  [9/9] FX...")
    L=np.zeros(TOTAL_SAMPLES); R=np.zeros(TOTAL_SAMPLES)

    def riser(dur):
        t=ta(dur); n=len(t); noise=rng.randn(n); r=np.zeros(n)
        ch=80; cs=n//ch
        for i in range(ch):
            s,e=i*cs,min((i+1)*cs,n)
            fc=min(60+(16000*(i/ch)**2.5),SR/2-100)
            c=noise[s:e]
            if len(c)>20: r[s:e]=_lp(c,fc)
        r*=np.linspace(0,1,n)**2
        return r*.3

    def impact():
        t=ta(1.5); noise=_lp(rng.randn(len(t)),2500)*.3
        sub=np.sin(2*np.pi*ROOT_F*.5*t)*np.exp(-t*2.5)
        return (noise+sub*.8)*np.exp(-t*3)*.8

    # Risers: 2 bars before each silence
    for bar in range(TOTAL_BARS):
        if sec(bar)=='order' and bar+1<TOTAL_BARS and sec(bar+1)=='silence':
            r=riser(2*BAR)
            pos=int((bar-1)*BAR*SR)
            if pos >= 0:
                ast(L,R,r,max(0,pos),p=0)
                r2=riser(2*BAR)*.35
                ast(L,R,r2,max(0,pos),p=rng.uniform(-.5,.5))

    # Impacts on drop entries
    imp=impact()
    for bar in range(TOTAL_BARS):
        if sec(bar)=='drop' and (bar==0 or sec(bar-1)!='drop'):
            pos=int(bar*BAR*SR)
            ast(L,R,imp,max(0,pos),p=0)

    return L, R


# ============================================================
# RENDER
# ============================================================
print("\nSintetizando...")
kick_L,kick_R=gen_kick()
bass_L,bass_R=gen_bass()
fm_L,fm_R=gen_fm()
elec_L,elec_R=gen_elec()
drums_L,drums_R=gen_drums()
lead_L,lead_R=gen_lead()
atmo_L,atmo_R=gen_atmo()
gran_L,gran_R=gen_gran(bass_L+bass_R, fm_L+fm_R)
fx_L,fx_R=gen_fx()

print("\nMezclando...")
mL=np.zeros(TOTAL_SAMPLES); mR=np.zeros(TOTAL_SAMPLES)
mL+=kick_L*.90;mR+=kick_R*.90
mL+=bass_L*.85;mR+=bass_R*.85
mL+=fm_L*.52;mR+=fm_R*.52
mL+=elec_L*.48;mR+=elec_R*.48
mL+=drums_L*.55;mR+=drums_R*.55
mL+=lead_L*.52;mR+=lead_R*.52
mL+=atmo_L*.40;mR+=atmo_R*.40
mL+=gran_L*.42;mR+=gran_R*.42
mL+=fx_L*.50;mR+=fx_R*.50

# Sidechain
print("Sidechain...")
km=(kick_L+kick_R)/2; ke=np.abs(km)
w=int(.03*SR); ks=np.convolve(ke,np.ones(w)/w,mode='same')
ks/=(np.max(ks)+1e-10); sc=1-ks*.15
nkL=mL-kick_L*.90; nkR=mR-kick_R*.90
mL=kick_L*.90+nkL*sc; mR=kick_R*.90+nkR*sc

# MASTER
print("Masterizando...")
mL=_hp(mL,25); mR=_hp(mR,25)
sL=_lp(mL,60); sR=_lp(mR,60)
mL-=sL*.35; mR-=sR*.35
m1L=_bp(mL,200,600); m1R=_bp(mR,200,600)
mL+=m1L*.4; mR+=m1R*.4
m2L=_bp(mL,600,2000); m2R=_bp(mR,600,2000)
mL+=m2L*.35; mR+=m2R*.35
pL=_bp(mL,2000,6000); pR=_bp(mR,2000,6000)
mL+=pL*.25; mR+=pR*.25
aL=_bp(mL,6000,16000); aR=_bp(mR,6000,16000)
mL+=aL*.15; mR+=aR*.15

mL=ws(mL,1.8); mR=ws(mR,1.8)
pk=max(np.max(np.abs(mL)),np.max(np.abs(mR)))
if pk>0: mL/=pk; mR/=pk
rms=np.sqrt(np.mean(mL**2+mR**2)/2)
tgt=10**(-9/20)
if rms>0:
    g=min(tgt/rms,3); mL*=g; mR*=g
mL=np.clip(mL,-.98,.98); mR=np.clip(mR,-.98,.98)

# SAVE
print("Guardando...")
stereo=np.column_stack([(mL*32767).astype(np.int16),(mR*32767).astype(np.int16)])
output=os.path.join(OUTPUT_DIR,"DarkPsy_v7_MUSICAL_DROPS.wav")
wavfile.write(output,SR,stereo)
import shutil
desktop="C:/Users/Juan/Desktop/DarkPsy_v7_MUSICAL_DROPS.wav"
shutil.copy2(output,desktop)

# Verify
print("\n--- Verificacion ---")
mc=(mL+mR)/2
fft_c=np.abs(np.fft.rfft(mc)); freqs_c=np.fft.rfftfreq(len(mc),1/SR)
te=np.sum(fft_c**2)
for nm,lo,hi in [('Sub',20,60),('Bass',60,200),('LowMid',200,600),('Mid',600,2000),
                  ('HiMid',2000,6000),('Pres',6000,10000),('Air',10000,20000)]:
    mask=(freqs_c>=lo)&(freqs_c<hi)
    print(f'  {nm:8s}: {np.sum(fft_c[mask]**2)/te*100:5.1f}%')
rms_f=np.sqrt(np.mean(mc**2))
print(f'  RMS: {20*np.log10(rms_f+1e-10):.1f} dB')

ents_o,ents_c=[],[]
for i in range(0,len(mc)-SR,SR):
    f=mc[i:i+SR]; ff=np.abs(np.fft.rfft(f))
    ff=ff/(np.sum(ff)+1e-10); ff=ff[ff>0]
    ent=-np.sum(ff*np.log2(ff))
    ba=int(i/(BAR*SR))
    if ba<TOTAL_BARS:
        if sec(ba)=='order': ents_o.append(ent)
        elif sec(ba)=='chaos': ents_c.append(ent)
if ents_o: print(f'  Entropy ORDER: {np.mean(ents_o):.2f}')
if ents_c: print(f'  Entropy CHAOS: {np.mean(ents_c):.2f}')
if ents_o and ents_c: print(f'  Contrast: {np.mean(ents_c)-np.mean(ents_o):+.2f}')

n_sil=sum(1 for b in range(TOTAL_BARS) if sec(b)=='silence')
n_drop=sum(1 for b in range(TOTAL_BARS) if sec(b)=='drop')
print(f'  Silencios: {n_sil} bars | Drops: {n_drop} bars')

print(f"\n{'='*60}")
print(f" TRACK: {desktop}")
print(f" {TOTAL_TIME/60:.1f} min | Musical drops con 5 variaciones")
print(f" ORDER -> fill -> [SILENCE] -> re-entry gradual -> CHAOS")
print(f"{'='*60}")
