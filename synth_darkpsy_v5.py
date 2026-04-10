"""
DARK PSYTRANCE v5 — ORDER vs CHAOS
The fundamental principle: locked groove → entropic chaos → back to groove
People need ORDER to dance, CHAOS to lose their minds, and the CONTRAST
between them is what makes dark psy magical.

Structure philosophy:
- LOCKED sections: kick nailed, bass rolling clean, minimal textures. DANCE.
- CHAOS sections: FM explosions, granular storms, filter madness. HEAD.
- TRANSITIONS: where order becomes chaos and vice versa. THE MAGIC.
"""

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt, sawtooth, square, resample
import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
SR = 44100
BPM = 150
BEAT = 60.0 / BPM
BAR = BEAT * 4
S16 = BEAT / 4
TOTAL_BARS = 224  # ~10 min — proper track length
TOTAL_TIME = TOTAL_BARS * BAR
TOTAL_SAMPLES = int(TOTAL_TIME * SR)

print("=" * 60)
print(" DARK PSYTRANCE v5 — ORDER vs CHAOS")
print(f" BPM: {BPM} | Bars: {TOTAL_BARS} | Duration: {TOTAL_TIME/60:.1f} min")
print("=" * 60)

rng = np.random.RandomState(666)

# ============================================================
# DSP
# ============================================================
def t_arr(dur):
    return np.linspace(0, dur, int(dur * SR), endpoint=False)

def lp(sig, fc, order=4):
    fc = np.clip(fc, 20, SR/2-100)
    return sosfilt(butter(order, fc, btype='low', fs=SR, output='sos'), sig)

def hp(sig, fc, order=2):
    fc = np.clip(fc, 20, SR/2-100)
    return sosfilt(butter(order, fc, btype='high', fs=SR, output='sos'), sig)

def bp(sig, lo, hi, order=2):
    lo, hi = max(lo,20), min(hi, SR/2-100)
    if lo >= hi: return sig
    return sosfilt(butter(order, [lo,hi], btype='band', fs=SR, output='sos'), sig)

def notch(sig, fc, q=8):
    lo = max(fc - fc/q, 20)
    hi = min(fc + fc/q, SR/2-100)
    if lo >= hi: return sig
    return sig - bp(sig, lo, hi, order=2) * 0.85

def nf(n): return 440.0 * (2.0 ** ((n-69)/12.0))

def ws(sig, a=2.0): return np.tanh(sig*a)/np.tanh(a)

def adsr(t, a=.01, d=.1, s=.7, r=.2, dur=None):
    if dur is None: dur = t[-1] if len(t) else 1
    env = np.zeros_like(t)
    for i, ti in enumerate(t):
        if ti < a: env[i] = ti/a if a > 0 else 1
        elif ti < a+d: env[i] = 1-(1-s)*(ti-a)/d
        elif ti < dur-r: env[i] = s
        else: env[i] = s*max(0,(dur-ti)/r) if r > 0 else 0
    return env

def pan_st(m, p=0):
    l = np.cos((p+1)/2*np.pi/2)
    r = np.sin((p+1)/2*np.pi/2)
    return m*l, m*r

def add_st(oL, oR, m, pos, p=0):
    L, R = pan_st(m, p)
    end = min(pos+len(L), len(oL))
    nn = end-pos
    if nn > 0 and pos >= 0:
        oL[pos:end] += L[:nn]
        oR[pos:end] += R[:nn]

def fm_synth(t, cf, mf, mi):
    mod = np.sin(2*np.pi*mf*t) * mi
    return np.sin(2*np.pi*cf*t + mod)

def filter_fm(t, bf, mr, res=0.88, sr=(200,8000)):
    raw = ws(sawtooth(2*np.pi*bf*t)*2, 3)
    n = len(t)
    ch = max(1, n//512)
    cs = n//ch
    out = np.zeros(n)
    for i in range(ch):
        s, e = i*cs, min((i+1)*cs, n)
        sw = np.sin(2*np.pi*mr*i/ch*t[-1])*0.5+0.5
        fc = sr[0]+(sr[1]-sr[0])*sw
        fc = np.clip(fc, 30, SR/2-100)
        bw = fc*(1-res*0.95)
        lo, hi = max(fc-bw/2,20), min(fc+bw/2, SR/2-100)
        c = raw[s:e]
        if lo < hi and len(c) > 20:
            out[s:e] = bp(c, lo, hi, order=2)*4
        else:
            out[s:e] = c
    return out

def granular(src, dur, gs=(.01,.08), dens=15, pr=(.5,2), sc=.3):
    no = int(dur*SR)
    oL, oR = np.zeros(no), np.zeros(no)
    ng = int(dur*dens)
    for _ in range(ng):
        gd = rng.uniform(*gs)
        gsamp = int(gd*SR)
        if gsamp < 10 or gsamp > len(src): continue
        sp = rng.randint(0, max(1, len(src)-gsamp))
        g = src[sp:sp+gsamp].copy()
        pitch = rng.uniform(*pr)
        nl = max(10, int(len(g)/pitch))
        g = resample(g, nl)
        g *= np.hanning(len(g))
        op = rng.randint(0, max(1, no-len(g)))
        pan = rng.uniform(-.8,.8)
        gL, gR = pan_st(g*sc, pan)
        end = min(op+len(gL), no)
        nn = end-op
        if nn > 0:
            oL[op:end] += gL[:nn]
            oR[op:end] += gR[:nn]
    return oL, oR

ROOT = 40
ROOT_F = nf(ROOT)


# ============================================================
# SECTION MAP — ORDER vs CHAOS
# ============================================================
# Each bar tagged as: 'order', 'chaos', 'trans_to_chaos', 'trans_to_order', 'intro', 'outro'
section_map = {}

# 0-7:     INTRO (ambient build)
# 8-15:    ORDER 1 — kick + bass locked in, minimal. DANCE.
# 16-23:   ORDER 1 continued — hats + perc enter. Groove deepens.
# 24-27:   TRANS → CHAOS — elements start glitching, FM creeps in
# 28-35:   CHAOS 1 — full entropic explosion. FM, granular, filter madness.
# 36-39:   TRANS → ORDER — chaos recedes, kick re-emerges clean
# 40-55:   ORDER 2 — longer locked groove, deeper bass, more hypnotic. DANCE.
# 56-59:   TRANS → CHAOS
# 60-71:   CHAOS 2 — bigger, wilder, more layers. Peak madness.
# 72-75:   TRANS → ORDER
# 76-99:   ORDER 3 — the big groove. Full band, lead enters. Longest dance section.
# 100-103: TRANS → CHAOS
# 104-119: CHAOS 3 — CLIMAX. Maximum entropy. Everything at once.
# 120-123: TRANS → ORDER
# 124-139: ORDER 4 — resolution groove. Lead melody shining (matices de luz)
# 140-147: BREAKDOWN — stripped back, atmospheric, breathing space
# 148-155: BUILD — energy returning
# 156-175: ORDER 5 — final groove, elements dropping one by one
# 176-183: TRANS → CHAOS
# 184-199: CHAOS 4 — final madness
# 200-207: TRANS → ORDER
# 208-219: ORDER 6 — OUTRO groove, winding down
# 220-223: OUTRO

for b in range(0, 8): section_map[b] = 'intro'
for b in range(8, 24): section_map[b] = 'order'
for b in range(24, 28): section_map[b] = 'trans_to_chaos'
for b in range(28, 36): section_map[b] = 'chaos'
for b in range(36, 40): section_map[b] = 'trans_to_order'
for b in range(40, 56): section_map[b] = 'order'
for b in range(56, 60): section_map[b] = 'trans_to_chaos'
for b in range(60, 72): section_map[b] = 'chaos'
for b in range(72, 76): section_map[b] = 'trans_to_order'
for b in range(76, 100): section_map[b] = 'order'
for b in range(100, 104): section_map[b] = 'trans_to_chaos'
for b in range(104, 120): section_map[b] = 'chaos'
for b in range(120, 124): section_map[b] = 'trans_to_order'
for b in range(124, 140): section_map[b] = 'order'
for b in range(140, 148): section_map[b] = 'breakdown'
for b in range(148, 156): section_map[b] = 'build'
for b in range(156, 176): section_map[b] = 'order'
for b in range(176, 180): section_map[b] = 'trans_to_chaos'
for b in range(180, 200): section_map[b] = 'chaos'
for b in range(200, 204): section_map[b] = 'trans_to_order'
for b in range(204, 220): section_map[b] = 'order'
for b in range(220, TOTAL_BARS): section_map[b] = 'outro'

def sec(bar):
    return section_map.get(bar, 'order')

def is_order(bar): return sec(bar) == 'order'
def is_chaos(bar): return sec(bar) == 'chaos'
def is_trans(bar): return sec(bar).startswith('trans')
def is_break(bar): return sec(bar) in ('breakdown', 'intro', 'outro')
def is_build(bar): return sec(bar) == 'build'

# Calculate chaos intensity (0-1) for transitions
def chaos_amount(bar):
    s = sec(bar)
    if s == 'order': return 0.0
    if s == 'chaos': return 1.0
    if s == 'breakdown': return 0.1
    if s == 'build': return 0.3
    if s == 'intro': return 0.05
    if s == 'outro': return 0.05
    if s == 'trans_to_chaos':
        # Find how far into the transition we are
        b = bar
        while b > 0 and section_map.get(b-1) == 'trans_to_chaos': b -= 1
        start = b
        while b < TOTAL_BARS and section_map.get(b) == 'trans_to_chaos': b += 1
        length = b - start
        pos = (bar - start) / max(length, 1)
        return pos  # 0 → 1
    if s == 'trans_to_order':
        b = bar
        while b > 0 and section_map.get(b-1) == 'trans_to_order': b -= 1
        start = b
        while b < TOTAL_BARS and section_map.get(b) == 'trans_to_order': b += 1
        length = b - start
        pos = (bar - start) / max(length, 1)
        return 1.0 - pos  # 1 → 0
    return 0.5

# Print structure
print()
print("ESTRUCTURA:")
prev = ''
for b in range(TOTAL_BARS):
    s = sec(b)
    if s != prev:
        label = {
            'intro': 'INTRO',
            'order': '>>> ORDER (DANCE)',
            'chaos': '*** CHAOS (MIND)',
            'trans_to_chaos': '~~~ ORDER -> CHAOS',
            'trans_to_order': '~~~ CHAOS -> ORDER',
            'breakdown': '... BREAKDOWN',
            'build': '^^ BUILD',
            'outro': 'OUTRO'
        }.get(s, s)
        # Find end of this section
        e = b
        while e < TOTAL_BARS and sec(e) == s: e += 1
        t_start = b * BAR
        t_end = e * BAR
        print(f"  Bar {b:3d}-{e-1:3d} ({t_start/60:.1f}-{t_end/60:.1f} min): {label}")
        prev = s


# ============================================================
# KICK — Locked in ORDER, disappears in CHAOS
# ============================================================
def gen_kick():
    print()
    print("  [1/9] Kick...")
    L = np.zeros(TOTAL_SAMPLES)
    R = np.zeros(TOTAL_SAMPLES)

    def make_kick(vel=.85, var=0):
        t = t_arr(0.2)
        n = len(t)
        click = bp(rng.randn(n), 2500+var*300, 7000+var*500, order=2)*2.5
        click *= np.exp(-t*100)*0.5
        d = int(SR*0.002)
        pitch = ROOT_F + (250+var*50)*np.exp(-t*(55+var*10))
        body = np.sin(2*np.pi*np.cumsum(pitch)/SR)*np.exp(-t*(12+var*2))*0.8
        kick = body.copy()
        if d < n: kick[d:] += click[:n-d]*0.6
        kick = notch(kick, 300, q=8)
        kick = hp(kick, 28)
        return ws(kick*vel*1.3, 2+var*0.5)*0.9

    for bar in range(TOTAL_BARS):
        if is_break(bar) and sec(bar) in ('breakdown', 'intro'):
            continue

        ca = chaos_amount(bar)

        # In ORDER: kick is LOCKED. Perfect 4/4. tak tak tak tak.
        # In CHAOS: kick becomes sparse, irregular, or disappears
        # In TRANSITION: gradual change

        if ca < 0.3:
            # ORDER — locked kick, solid
            beats = [0, 1, 2, 3]
            skip_prob = 0.02  # almost never skip
        elif ca < 0.7:
            # TRANSITION — starting to glitch
            beats = [0, 1, 2, 3]
            skip_prob = 0.1 + ca * 0.3
        else:
            # CHAOS — sparse, irregular
            beats = [0, 1, 2, 3]
            skip_prob = 0.4 + ca * 0.2

        # Fill bars before chaos
        if sec(bar) == 'trans_to_chaos' and chaos_amount(bar) > 0.7:
            positions = [0, 0.5, 0.75, 0.875, 0.9375]
            for p in positions:
                kick = make_kick(vel=0.7+p*0.3, var=rng.randint(0,3))
                pos = int((bar*BAR + p*BAR)*SR)
                add_st(L, R, kick, max(0,pos), p=rng.uniform(-.04,.04))
            continue

        for beat in beats:
            if beat != 0 and rng.random() < skip_prob:
                continue

            vel = 0.80 + rng.random()*0.15
            # In ORDER: tight timing. In CHAOS: looser.
            timing_spread = 0.002 if ca < 0.3 else 0.002 + ca * 0.008
            timing = rng.normal(0, timing_spread)

            kick = make_kick(vel=vel, var=rng.randint(0, 2+int(ca*3)))
            pos = int((bar*BAR + beat*BEAT + timing)*SR)
            add_st(L, R, kick, max(0,pos), p=rng.uniform(-.03,.03))

    return L, R


# ============================================================
# ROLLING BASS — Hypnotic in ORDER, mutating in CHAOS
# ============================================================
def gen_bass():
    print("  [2/9] Rolling bass...")
    L = np.zeros(TOTAL_SAMPLES)
    R = np.zeros(TOTAL_SAMPLES)

    kick_tail = 0.05

    # ORDER patterns: repetitive, hypnotic, groovy
    order_pats = [
        [0]*16,
        [0,0,4,0, 0,0,4,0, 0,0,0,0, 0,0,4,0],
        [0,0,0,0, 0,0,4,0, 0,0,0,0, 0,0,7,0],
    ]
    # CHAOS patterns: chromatic, unpredictable, wild
    chaos_pats = [
        [0,1,4,7, 5,0,1,4, 7,5,0,1, 4,7,5,0],
        [7,0,4,1, 0,5,7,0, 4,1,0,5, 7,0,4,1],
        [0,4,7,12, 7,4,0,1, 5,0,7,4, 1,0,5,7],
        [rng.randint(0,8) for _ in range(16)],
    ]

    for bar in range(TOTAL_BARS):
        if is_break(bar) and sec(bar) == 'breakdown':
            continue
        if bar < 6: continue

        ca = chaos_amount(bar)

        # Select pattern based on chaos amount
        if ca < 0.2:
            pat = order_pats[bar % len(order_pats)]
        elif ca < 0.5:
            # Blend: mostly order with occasional chaos note
            pat = list(order_pats[bar % len(order_pats)])
            for i in range(16):
                if rng.random() < ca * 0.5:
                    pat[i] = rng.choice([0,1,4,5,7])
        elif ca < 0.8:
            pat = chaos_pats[bar % len(chaos_pats)]
        else:
            # Full chaos: generate random
            scale_opts = [0,1,4,5,7,0,0,4]  # weighted toward root
            pat = [rng.choice(scale_opts) for _ in range(16)]

        for step in range(16):
            note = ROOT + pat[step]
            freq = nf(note)

            is_on = step % 4 == 0
            bass_delay = kick_tail * 0.6 if is_on and ca < 0.5 else 0
            timing = bass_delay + rng.normal(0, 0.002 + ca*0.004)

            # In chaos: some notes randomly skip
            if ca > 0.5 and rng.random() < (ca-0.5)*0.3:
                continue

            dur = S16 * (0.78 + rng.random()*0.15)
            t = t_arr(dur)
            n = len(t)

            saw = sawtooth(2*np.pi*freq*(1+rng.uniform(-.003,.003))*t)
            sub = np.sin(2*np.pi*freq*0.5*t) * 0.4
            raw = saw*0.6 + sub*0.4

            # Filter: tighter in order, wilder in chaos
            cutoff = 45 + 20*(step%4==0) + ca*1500
            raw = lp(raw, cutoff)

            # More saturation in chaos
            mid = bp(raw, 150, 800)
            raw = raw + ws(mid*3, 4)*0.3
            raw = ws(raw * 1.5 * (0.7 + 0.25*(step%4==0)), 2.5+ca*1.5)

            amp = np.ones(n)
            atk = min(int(rng.uniform(10,35)), n)
            amp[:atk] = np.linspace(0,1,atk)
            dec = int(n*(0.65+rng.random()*0.15))
            if dec < n: amp[dec:] = np.linspace(1,.1,n-dec)

            pos = int((bar*BAR + step*S16 + timing)*SR)
            pan = np.sin(step*0.25+bar*0.07) * (0.08+ca*0.2)
            add_st(L, R, raw*amp*0.65, max(0,pos), p=pan)

    return L, R


# ============================================================
# FM TEXTURES — Only in CHAOS and transitions
# ============================================================
def gen_fm():
    print("  [3/9] FM textures...")
    L = np.zeros(TOTAL_SAMPLES)
    R = np.zeros(TOTAL_SAMPLES)

    scale = [40,41,44,45,47,48,50,52,53,56,57,59,60,62,64,65,68]

    for bar in range(TOTAL_BARS):
        ca = chaos_amount(bar)
        if ca < 0.15: continue  # FM only when chaos creeps in

        # Density scales with chaos
        if rng.random() > ca * 0.8: continue

        n_notes = rng.randint(1, int(2 + ca*6))
        t_off = rng.uniform(0, BAR*0.3)

        for _ in range(n_notes):
            note = scale[rng.randint(len(scale))]
            freq = nf(note + rng.choice([0,12,24]))
            dur = rng.uniform(0.03, 0.1 + ca*0.5)
            t = t_arr(dur)

            mr = rng.choice([1,1.5,2,3,4,5.33,7,11])
            mi = rng.uniform(0.5, 2) + ca * 8  # more chaos = more modulation

            fm = fm_synth(t, freq, freq*mr, mi)
            amp = adsr(t, a=.002, d=rng.uniform(.02,.15), s=.3, r=.05, dur=dur)
            fm = ws(fm*amp*0.25*ca, 2) * ca  # volume scales with chaos

            pos = int((bar*BAR + t_off)*SR)
            add_st(L, R, fm, max(0,pos), p=rng.uniform(-.7,.7))
            t_off += dur + rng.uniform(0, S16*2)

    return L * 0.5, R * 0.5


# ============================================================
# FILTER FM (Electricity) — CHAOS signature sound
# ============================================================
def gen_electricity():
    print("  [4/9] Filter FM electricity...")
    L = np.zeros(TOTAL_SAMPLES)
    R = np.zeros(TOTAL_SAMPLES)

    for bar in range(TOTAL_BARS):
        ca = chaos_amount(bar)
        if ca < 0.4: continue
        if rng.random() > ca * 0.6: continue

        dur = rng.uniform(0.3, 1.0 + ca*2)
        t = t_arr(dur)
        bf = nf(ROOT + rng.choice([0,12,7,5,24]))
        mr = rng.uniform(0.3, 3+ca*3)

        elec = filter_fm(t, bf, mr, res=0.85+rng.random()*.12,
                         sr=(150+rng.random()*500, 4000+rng.random()*8000))
        amp = adsr(t, a=.01, d=.1, s=.6, r=.15, dur=dur)
        elec = elec * amp * 0.2 * ca

        pos = int((bar*BAR + rng.uniform(0, BAR*0.5))*SR)
        add_st(L, R, elec, max(0,pos), p=rng.uniform(-.5,.5))

    return L * 0.5, R * 0.5


# ============================================================
# DRUMS — Tight in ORDER, organic/sparse in CHAOS
# ============================================================
def gen_drums():
    print("  [5/9] Drums...")
    L = np.zeros(TOTAL_SAMPLES)
    R = np.zeros(TOTAL_SAMPLES)

    for bar in range(TOTAL_BARS):
        if bar < 8: continue
        if sec(bar) == 'breakdown': continue

        ca = chaos_amount(bar)

        for step in range(16):
            timing = rng.normal(0, 0.003 + ca*0.005)

            # Offbeat hat — present in ORDER, sporadic in CHAOS
            if step % 4 == 2:
                hat_prob = 0.95 if ca < 0.3 else max(0.3, 0.95 - ca*0.6)
                if rng.random() < hat_prob:
                    dur = S16 * rng.uniform(0.4, 0.7)
                    t = t_arr(dur)
                    hat = hp(rng.randn(len(t)), 6000+rng.random()*3000)
                    hat *= np.exp(-t*(25+rng.random()*20)) * rng.uniform(.18,.28)
                    pos = int((bar*BAR + step*S16 + timing)*SR)
                    add_st(L, R, hat, max(0,pos), p=0.15+rng.uniform(-.1,.1))

            # Ghost hats
            elif step % 2 == 1 and rng.random() < (0.5 - ca*0.2):
                dur = S16 * rng.uniform(.2,.35)
                t = t_arr(dur)
                hat = hp(rng.randn(len(t)), 8000+rng.random()*3000)
                hat *= np.exp(-t*(40+rng.random()*25)) * rng.uniform(.06,.12)
                pos = int((bar*BAR + step*S16 + timing)*SR)
                add_st(L, R, hat, max(0,pos), p=rng.uniform(-.5,.5))

            # Open hat
            if step == 12 and bar % 4 == 3 and rng.random() < (0.75 if ca < 0.3 else 0.4):
                dur = S16 * rng.uniform(1.5, 3)
                t = t_arr(dur)
                hat = bp(rng.randn(len(t)), 4000+rng.random()*2000, 14000)
                hat *= np.exp(-t*(5+rng.random()*4))*0.25
                pos = int((bar*BAR + step*S16 + timing)*SR)
                add_st(L, R, hat, max(0,pos), p=0.3+rng.uniform(-.15,.15))

        # Clap — ORDER only
        if ca < 0.5 and bar >= 12:
            for beat in [1,3]:
                if rng.random() > 0.04:
                    t = t_arr(rng.uniform(.06,.1))
                    clap = np.zeros(len(t))
                    for i in range(rng.randint(2,5)):
                        d = int(i*SR*rng.uniform(.003,.007))
                        b = bp(rng.randn(len(t)), 700+rng.random()*500, 4000+rng.random()*1500)
                        b *= np.exp(-t*(25+rng.random()*15))
                        if d < len(clap): clap[d:] += b[:len(clap)-d]*(0.7**i)
                    clap *= rng.uniform(.2,.35)
                    pos = int((bar*BAR + beat*BEAT + rng.normal(0,.003))*SR)
                    add_st(L, R, clap, max(0,pos), p=rng.uniform(-.08,.08))

        # Tribal — more in ORDER
        if bar % 2 == 1 and bar >= 16 and rng.random() < (0.55 if ca < 0.3 else 0.2):
            ht = rng.uniform(2.5, 3.8)
            t = t_arr(rng.uniform(.08,.15))
            freq = rng.uniform(70,150)
            tom = np.sin(2*np.pi*freq*t*np.exp(-t*(3+rng.random()*4)))
            tom *= np.exp(-t*(8+rng.random()*6))*0.3
            pos = int((bar*BAR + ht*BEAT)*SR)
            add_st(L, R, ws(tom,1.5), max(0,pos), p=rng.uniform(-.4,.4))

    return L, R


# ============================================================
# LEAD — Matices de luz, mostly in ORDER sections
# ============================================================
def gen_lead():
    print("  [6/9] Lead (matices de luz)...")
    L = np.zeros(TOTAL_SAMPLES)
    R = np.zeros(TOTAL_SAMPLES)

    phrases = [
        [(64,.5,.8),(68,.75,1),(69,.25,.7),(71,1,1),(68,.5,.8)],
        [(76,.5,.9),(72,.5,.8),(71,.5,.7),(68,1.5,1)],
        [(80,1,.6),(76,.5,.7),(72,1,.9),(71,.5,.8),(68,1,1)],
        [(64,.5,.9),(62,.5,.8),(60,.5,.7),(64,.5,.8),(68,1,1),(72,1,.9)],
        [(71,.5,.9),(72,.5,1),(76,1,.8),(72,.5,.7),(68,1.5,1)],
    ]

    def mutate_ph(ph):
        p = list(ph)
        for i in range(len(p)):
            n,d,v = p[i]
            if rng.random() < .2: n += rng.choice([-3,-2,-1,1,2,3,4])
            if rng.random() < .12: d *= rng.uniform(.7,1.4)
            p[i] = (max(52,min(84,n)), d, np.clip(v*rng.uniform(.85,1.1),.3,1))
        return p

    # Lead appears in ORDER sections after bar 76 (third groove section)
    # and in breakdowns (matices de luz moments)
    pidx = 0
    for bar in range(TOTAL_BARS):
        show_lead = False
        if is_order(bar) and bar >= 76: show_lead = True
        if sec(bar) == 'breakdown': show_lead = True
        if is_order(bar) and bar >= 124 and bar < 140: show_lead = True  # resolution

        if not show_lead: continue
        if rng.random() < 0.12: continue  # breathing

        ph = mutate_ph(phrases[pidx%len(phrases)]) if rng.random() > .3 else phrases[pidx%len(phrases)]
        t_off = 0

        for note, dur, vel in ph:
            freq = nf(note)
            nd = dur*BEAT*rng.uniform(.88,1.08)
            t = t_arr(nd)
            n = len(t)

            sp = rng.uniform(.003,.008)
            sm = np.zeros(n)
            for dt in [1-sp*2, 1-sp, 1, 1+sp, 1+sp*2]:
                sm += sawtooth(2*np.pi*freq*dt*t)
            sm /= 5

            fm_c = fm_synth(t, freq, freq*rng.choice([2,3,4]), rng.uniform(.5,2))
            lead = sm*.7 + fm_c*.3
            lead = bp(lead, 300, min(freq*8, SR/2-100))

            amp = adsr(t, a=rng.uniform(.008,.025), d=.08, s=.7, r=.1, dur=nd)
            lead = ws(lead*1.2, 1.5) * amp * vel * .3

            pos = int((bar*BAR + t_off + rng.normal(0,.004))*SR)
            add_st(L, R, lead, max(0,pos), p=.2+rng.uniform(-.1,.1))
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
# ATMOSPHERE — Always present, evolving
# ============================================================
def gen_atmo():
    print("  [7/9] Atmosphere...")
    L = np.zeros(TOTAL_SAMPLES)
    R = np.zeros(TOTAL_SAMPLES)

    chords = [[52,56,59],[53,57,60],[57,60,64],[50,53,57],
              [56,59,62],[52,56,59],[48,52,56],[52,56,59]]

    bpc = 4
    for ci in range(TOTAL_BARS//bpc + 1):
        sb = ci*bpc
        if sb >= TOTAL_BARS: break
        ch = chords[ci%len(chords)]
        if rng.random() < .25: ch = ch + [ch[0]+rng.choice([14,17,21])]

        dur = min(bpc*BAR, (TOTAL_BARS-sb)*BAR)
        t = t_arr(dur)
        n = len(t)
        pL, pR = np.zeros(n), np.zeros(n)

        for i, note in enumerate(ch):
            freq = nf(note)
            det = rng.uniform(.002,.005)
            oL = np.sin(2*np.pi*freq*(1-det)*t)*.35
            oR = np.sin(2*np.pi*freq*(1+det)*t)*.35
            saw = lp(sawtooth(2*np.pi*freq*t)*.2, min(freq*2.5,SR/2-100))
            lfo = .5+.5*np.sin(2*np.pi*(.06+i*.04+rng.random()*.05)*t + rng.random()*6.28)
            pL += (oL+saw*.5)*lfo
            pR += (oR+saw*.5)*lfo

        pL /= len(ch); pR /= len(ch)
        fade = min(int(3*SR), n//3)
        pL[:fade] *= np.linspace(0,1,fade)
        pL[-fade:] *= np.linspace(1,0,fade)
        pR[:fade] *= np.linspace(0,1,fade)
        pR[-fade:] *= np.linspace(1,0,fade)

        # Louder in breakdowns
        vol = 0.45 if sec(sb) == 'breakdown' else 0.3
        pos = int(sb*BAR*SR)
        end = min(pos+n, TOTAL_SAMPLES)
        nn = end-pos
        L[pos:end] += pL[:nn]*vol
        R[pos:end] += pR[:nn]*vol

    return L, R


# ============================================================
# GRANULAR — CHAOS texture layer
# ============================================================
def gen_granular_layer(bass_L, fm_L):
    print("  [8/9] Granular (chaos textures)...")
    L = np.zeros(TOTAL_SAMPLES)
    R = np.zeros(TOTAL_SAMPLES)

    # Build source pool
    sources = []
    for i in range(10):
        s = int(rng.uniform(.1,.8)*TOTAL_SAMPLES)
        cl = int(SR*rng.uniform(1,4))
        e = min(s+cl, TOTAL_SAMPLES)
        if e-s > SR: sources.append(bass_L[s:e])
    for i in range(5):
        s = int(rng.uniform(.2,.9)*TOTAL_SAMPLES)
        cl = int(SR*rng.uniform(.5,2))
        e = min(s+cl, TOTAL_SAMPLES)
        if e-s > SR//2: sources.append(fm_L[s:e])
    if not sources: sources = [rng.randn(SR*2)]

    for bar in range(TOTAL_BARS):
        ca = chaos_amount(bar)
        if ca < 0.25: continue  # Only in chaos and transitions

        dens = 5 + ca * 20
        sc = 0.1 + ca * 0.35

        src = sources[rng.randint(len(sources))]
        gL, gR = granular(
            src, BAR,
            gs=(.008+rng.random()*.02, .04+rng.random()*.06),
            dens=dens, pr=(.3+rng.random()*.5, 1.5+rng.random()*1.5),
            sc=sc
        )

        pos = int(bar*BAR*SR)
        end = min(pos+len(gL), TOTAL_SAMPLES)
        nn = end-pos
        if nn > 0:
            L[pos:end] += gL[:nn]
            R[pos:end] += gR[:nn]

    return L * 0.4, R * 0.4


# ============================================================
# FX — Risers before chaos, impacts on drops, downlifters
# ============================================================
def gen_fx():
    print("  [9/9] FX...")
    L = np.zeros(TOTAL_SAMPLES)
    R = np.zeros(TOTAL_SAMPLES)

    def make_riser(duration):
        t = t_arr(duration)
        n = len(t)
        noise = rng.randn(n)
        riser = np.zeros(n)
        ch = 80
        cs = n//ch
        for i in range(ch):
            s, e = i*cs, min((i+1)*cs, n)
            fc = min(60+(16000*(i/ch)**2.5), SR/2-100)
            c = noise[s:e]
            if len(c) > 20: riser[s:e] = lp(c, fc)
        riser *= np.linspace(0,1,n)**2
        return riser*.3

    def make_impact():
        t = t_arr(1.2)
        noise = lp(rng.randn(len(t)), 2000)*.3
        sub = np.sin(2*np.pi*ROOT_F*.5*t)*np.exp(-t*3)
        return (noise+sub*.7)*np.exp(-t*3.5)*.7

    # Risers before each chaos section
    for bar in range(TOTAL_BARS):
        if sec(bar) == 'trans_to_chaos':
            # Check if this is the start of the transition
            if bar == 0 or sec(bar-1) != 'trans_to_chaos':
                # Find transition length
                b = bar
                while b < TOTAL_BARS and sec(b) == 'trans_to_chaos': b += 1
                dur = (b - bar) * BAR
                r = make_riser(dur)
                pos = int(bar*BAR*SR)
                add_st(L, R, r, max(0,pos), p=0)
                r2 = make_riser(dur)*.4
                add_st(L, R, r2, max(0,pos), p=rng.uniform(-.6,.6))

    # Impacts at chaos starts
    imp = make_impact()
    for bar in range(TOTAL_BARS):
        if is_chaos(bar) and (bar == 0 or not is_chaos(bar-1)):
            pos = int(bar*BAR*SR)
            add_st(L, R, imp, max(0,pos), p=0)

    # Downlifters at chaos → order transitions
    for bar in range(TOTAL_BARS):
        if sec(bar) == 'trans_to_order' and (bar == 0 or sec(bar-1) != 'trans_to_order'):
            b = bar
            while b < TOTAL_BARS and sec(b) == 'trans_to_order': b += 1
            dur = (b-bar)*BAR
            t = t_arr(dur)
            n = len(t)
            noise = rng.randn(n)
            dl = np.zeros(n)
            chs = 40
            cs = n//chs
            for i in range(chs):
                s, e = i*cs, min((i+1)*cs, n)
                fc = max(min(14000-13500*(i/chs), SR/2-100), 30)
                c = noise[s:e]
                if len(c) > 20: dl[s:e] = lp(c, fc)
            dl *= np.linspace(1,0,n)**1.2*.2
            pos = int(bar*BAR*SR)
            add_st(L, R, dl, max(0,pos), p=rng.uniform(-.3,.3))

    return L, R


# ============================================================
# RENDER
# ============================================================
print()
print("Sintetizando...")

kick_L, kick_R = gen_kick()
bass_L, bass_R = gen_bass()
fm_L, fm_R = gen_fm()
elec_L, elec_R = gen_electricity()
drums_L, drums_R = gen_drums()
lead_L, lead_R = gen_lead()
atmo_L, atmo_R = gen_atmo()
gran_L, gran_R = gen_granular_layer(bass_L+bass_R, fm_L+fm_R)
fx_L, fx_R = gen_fx()

print()
print("Mezclando...")

mix_L = np.zeros(TOTAL_SAMPLES)
mix_R = np.zeros(TOTAL_SAMPLES)

mix_L += kick_L*.90;   mix_R += kick_R*.90
mix_L += bass_L*.85;   mix_R += bass_R*.85
mix_L += fm_L*.50;     mix_R += fm_R*.50
mix_L += elec_L*.45;   mix_R += elec_R*.45
mix_L += drums_L*.55;  mix_R += drums_R*.55
mix_L += lead_L*.52;   mix_R += lead_R*.52
mix_L += atmo_L*.40;   mix_R += atmo_R*.40
mix_L += gran_L*.38;   mix_R += gran_R*.38
mix_L += fx_L*.48;     mix_R += fx_R*.48

# Light sidechain (phase design handles most of it)
print("Sidechain (light)...")
k_m = (kick_L+kick_R)/2
k_e = np.abs(k_m)
w = int(.03*SR)
k_s = np.convolve(k_e, np.ones(w)/w, mode='same')
k_s /= (np.max(k_s)+1e-10)
sc = 1 - k_s*.15
nk_L = mix_L - kick_L*.90
nk_R = mix_R - kick_R*.90
mix_L = kick_L*.90 + nk_L*sc
mix_R = kick_R*.90 + nk_R*sc

# MASTERING
print("Masterizando...")
mix_L = hp(mix_L, 25); mix_R = hp(mix_R, 25)

# Tame sub
sL = lp(mix_L, 60); sR = lp(mix_R, 60)
mix_L -= sL*.35; mix_R -= sR*.35

# Boost low-mids
m1L = bp(mix_L,200,600); m1R = bp(mix_R,200,600)
mix_L += m1L*.4; mix_R += m1R*.4

# Boost mids
m2L = bp(mix_L,600,2000); m2R = bp(mix_R,600,2000)
mix_L += m2L*.35; mix_R += m2R*.35

# Presence
pL = bp(mix_L,2000,6000); pR = bp(mix_R,2000,6000)
mix_L += pL*.25; mix_R += pR*.25

# Air
aL = bp(mix_L,6000,16000); aR = bp(mix_R,6000,16000)
mix_L += aL*.15; mix_R += aR*.15

# Saturation
mix_L = ws(mix_L, 1.8); mix_R = ws(mix_R, 1.8)

# Normalize + limit
pk = max(np.max(np.abs(mix_L)), np.max(np.abs(mix_R)))
if pk > 0: mix_L /= pk; mix_R /= pk

rms = np.sqrt(np.mean(mix_L**2+mix_R**2)/2)
tgt = 10**(-9/20)
if rms > 0:
    g = min(tgt/rms, 3)
    mix_L *= g; mix_R *= g

mix_L = np.clip(mix_L, -.98, .98)
mix_R = np.clip(mix_R, -.98, .98)

# SAVE
print("Guardando...")
stereo = np.column_stack([(mix_L*32767).astype(np.int16), (mix_R*32767).astype(np.int16)])

output = os.path.join(OUTPUT_DIR, "DarkPsy_v5_ORDER_vs_CHAOS.wav")
wavfile.write(output, SR, stereo)

import shutil
desktop = "C:/Users/Juan/Desktop/DarkPsy_v5_ORDER_vs_CHAOS.wav"
shutil.copy2(output, desktop)

# Verification
print()
print("--- Verificación ---")
mc = (mix_L+mix_R)/2
fft_c = np.abs(np.fft.rfft(mc))
freqs_c = np.fft.rfftfreq(len(mc), 1/SR)
te = np.sum(fft_c**2)
for nm, lo, hi in [('Sub 20-60',20,60),('Bass 60-200',60,200),('LowMid 200-600',200,600),
                    ('Mid 600-2k',600,2000),('HiMid 2k-6k',2000,6000),('Pres 6k-10k',6000,10000),('Air 10k-20k',10000,20000)]:
    mask = (freqs_c>=lo)&(freqs_c<hi)
    pct = np.sum(fft_c[mask]**2)/te*100
    print(f'  {nm:18s}: {pct:5.1f}%')

rms_f = np.sqrt(np.mean(mc**2))
print(f'  RMS: {20*np.log10(rms_f+1e-10):.1f} dB')

# Entropy
ents = []
for i in range(0, len(mc)-SR, SR):
    f = mc[i:i+SR]
    ff = np.abs(np.fft.rfft(f))
    ff = ff/(np.sum(ff)+1e-10)
    ff = ff[ff>0]
    ents.append(-np.sum(ff*np.log2(ff)))
print(f'  Entropía media: {np.mean(ents):.2f} bits')

# ORDER vs CHAOS entropy comparison
order_ents = []
chaos_ents = []
for i, e in enumerate(ents):
    bar_approx = int(i * SR / (BAR * SR))
    if bar_approx < TOTAL_BARS:
        if is_order(bar_approx): order_ents.append(e)
        elif is_chaos(bar_approx): chaos_ents.append(e)

if order_ents and chaos_ents:
    print(f'  Entropía ORDER:  {np.mean(order_ents):.2f} bits')
    print(f'  Entropía CHAOS:  {np.mean(chaos_ents):.2f} bits')
    print(f'  Contraste:       {np.mean(chaos_ents)-np.mean(order_ents):.2f} bits')

print()
print("=" * 60)
print(f" TRACK: {desktop}")
print(f" Duración: {TOTAL_TIME/60:.1f} min | STEREO")
print(f" Filosofia: ORDER (dance) <-> CHAOS (mind)")
print("=" * 60)
