"""
DARK PSYTRANCE v4 — GENRE-ACCURATE
Based on Psykovsky/Kindzadza/Frantic Noise/Will O Wisp production research
+ Glosolalia spectral analysis calibration.

Techniques:
- Kick: 300Hz notch, 2-layer (click+sub), tuned to E
- Bass: Phase-designed to interlock with kick, no sidechain
- FM synthesis: Alien textures, metallic leads
- Filter FM: HP resonance sweeps (the "electricity" sound)
- Granular: Micro-particle textures
- Resampling: Process → re-process chains
- Wall of sound: New layer every 4-8 bars
- Entropy target: ~12.5 bits (Glosolalia calibrated)
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
S16 = BEAT / 4  # sixteenth
TOTAL_BARS = 180  # ~8 min
TOTAL_TIME = TOTAL_BARS * BAR
TOTAL_SAMPLES = int(TOTAL_TIME * SR)

print("=" * 60)
print(" DARK PSYTRANCE v4 — GENRE-ACCURATE ENGINE")
print(f" BPM: {BPM} | Bars: {TOTAL_BARS} | Duration: {TOTAL_TIME/60:.1f} min")
print("=" * 60)

rng = np.random.RandomState(666)  # dark seed


# ============================================================
# DSP ENGINE
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
    lo, hi = max(lo, 20), min(hi, SR/2-100)
    if lo >= hi: return sig
    return sosfilt(butter(order, [lo, hi], btype='band', fs=SR, output='sos'), sig)

def notch(sig, fc, q=30):
    """Notch filter — key for the 300Hz kick cut"""
    fc = np.clip(fc, 20, SR/2-100)
    w0 = fc / (SR/2)
    bw = w0 / q
    lo = max(fc - fc/q, 20)
    hi = min(fc + fc/q, SR/2-100)
    if lo >= hi: return sig
    # Simple notch via subtracting bandpass
    band = bp(sig, lo, hi, order=2)
    return sig - band * 0.85

def note_freq(n):
    return 440.0 * (2.0 ** ((n - 69) / 12.0))

def waveshape(sig, amt=2.0):
    return np.tanh(sig * amt) / np.tanh(amt)

def adsr(t, a=0.01, d=0.1, s=0.7, r=0.2, dur=None):
    if dur is None: dur = t[-1] if len(t) else 1.0
    env = np.zeros_like(t)
    for i, ti in enumerate(t):
        if ti < a: env[i] = ti/a if a > 0 else 1.0
        elif ti < a+d: env[i] = 1.0 - (1.0-s)*(ti-a)/d
        elif ti < dur-r: env[i] = s
        else: env[i] = s * max(0, (dur-ti)/r) if r > 0 else 0
    return env

def pan_st(mono, pan=0.0):
    l = np.cos((pan+1)/2*np.pi/2)
    r = np.sin((pan+1)/2*np.pi/2)
    return mono*l, mono*r

def add_st(oL, oR, mono, pos, pan=0.0):
    L, R = pan_st(mono, pan)
    end = min(pos+len(L), len(oL))
    n = end-pos
    if n > 0 and pos >= 0:
        oL[pos:end] += L[:n]
        oR[pos:end] += R[:n]

def in_sec(bar, secs):
    for s, e in secs:
        if s <= bar < e: return True
    return False


# ============================================================
# FM SYNTHESIS ENGINE
# ============================================================
def fm_synth(t, carrier_freq, mod_freq, mod_index, carrier_wave='sine'):
    """FM synthesis: carrier modulated by modulator"""
    modulator = np.sin(2 * np.pi * mod_freq * t) * mod_index
    phase = 2 * np.pi * carrier_freq * t + modulator
    if carrier_wave == 'sine':
        return np.sin(phase)
    elif carrier_wave == 'saw':
        return sawtooth(phase)
    return np.sin(phase)


def filter_fm(t, base_freq, mod_rate, resonance=0.9, sweep_range=(200, 8000)):
    """Filter FM — HP with high resonance sweeping = 'electricity' sound"""
    # Generate raw harmonics
    raw = sawtooth(2 * np.pi * base_freq * t)
    # Add harmonics via waveshaping
    raw = waveshape(raw * 2.0, 3.0)

    # Sweep filter via chunked processing
    n = len(t)
    chunks = max(1, n // 512)
    chunk_size = n // chunks
    out = np.zeros(n)

    for i in range(chunks):
        s = i * chunk_size
        e = min(s + chunk_size, n)
        # Sweep position
        pos = i / chunks
        sweep = np.sin(2 * np.pi * mod_rate * pos * t[-1]) * 0.5 + 0.5
        fc = sweep_range[0] + (sweep_range[1] - sweep_range[0]) * sweep
        fc = np.clip(fc, 30, SR/2-100)

        chunk = raw[s:e]
        if len(chunk) > 20:
            # BP with high resonance simulates resonant filter
            bw = fc * (1 - resonance * 0.95)
            lo = max(fc - bw/2, 20)
            hi = min(fc + bw/2, SR/2-100)
            if lo < hi:
                out[s:e] = bp(chunk, lo, hi, order=2) * 4  # boost for resonance
            else:
                out[s:e] = chunk

    return out


# ============================================================
# GRANULAR ENGINE
# ============================================================
def granular_texture(source, duration, grain_size_range=(0.01, 0.08),
                     density=15, pitch_range=(0.5, 2.0), scatter=0.3):
    """Granular resynthesis — break source into micro-grains and scatter"""
    n_out = int(duration * SR)
    out_L = np.zeros(n_out)
    out_R = np.zeros(n_out)
    n_grains = int(duration * density)

    for _ in range(n_grains):
        # Random grain from source
        grain_dur = rng.uniform(*grain_size_range)
        grain_samples = int(grain_dur * SR)
        if grain_samples < 10 or grain_samples > len(source):
            continue

        src_pos = rng.randint(0, max(1, len(source) - grain_samples))
        grain = source[src_pos:src_pos + grain_samples].copy()

        # Pitch shift via resampling
        pitch = rng.uniform(*pitch_range)
        new_len = max(10, int(len(grain) / pitch))
        grain = resample(grain, new_len)

        # Window
        window = np.hanning(len(grain))
        grain *= window

        # Scatter position
        out_pos = rng.randint(0, max(1, n_out - len(grain)))
        pan = rng.uniform(-0.8, 0.8)

        gL, gR = pan_st(grain * scatter, pan)
        end = min(out_pos + len(gL), n_out)
        nn = end - out_pos
        if nn > 0:
            out_L[out_pos:end] += gL[:nn]
            out_R[out_pos:end] += gR[:nn]

    return out_L, out_R


# ============================================================
# STRUCTURE (180 bars ≈ 8 min)
# ============================================================
# 0-11:    INTRO (atmosphere, textures building)
# 12-15:   BUILD 1 (kick enters sparse, bass fades in)
# 16-47:   DROP 1 (full dark energy, 32 bars)
# 48-55:   TRANSITION (strip down, filter sweep)
# 56-71:   BREAKDOWN 1 (ethereal, matices de luz, granular)
# 72-79:   BUILD 2 (riser, elements returning)
# 80-127:  DROP 2 (climax, wall of sound, max density)
# 128-139: TRANSITION 2 (evolving textures)
# 140-155: BREAKDOWN 2 (deep, experimental)
# 156-163: BUILD 3 (final rise)
# 164-175: DROP 3 (outro drop, resolving)
# 176-179: OUTRO

SEC_INTRO = [(0, 12)]
SEC_BUILD = [(12, 16), (72, 80), (156, 164)]
SEC_DROP = [(16, 48), (80, 128), (164, 176)]
SEC_BREAK = [(56, 72), (140, 156)]
SEC_TRANS = [(48, 56), (128, 140)]
SEC_OUTRO = [(176, 180)]

ROOT = 40  # E2
ROOT_FREQ = note_freq(ROOT)  # ~82.4 Hz


# ============================================================
# KICK — 2-layer, 300Hz notch, tuned to E
# ============================================================
def gen_kick():
    print("  [1/9] Kick (dark psy, 300Hz notch)...")
    L = np.zeros(TOTAL_SAMPLES)
    R = np.zeros(TOTAL_SAMPLES)

    def make_kick(vel=0.85, variation=0):
        t = t_arr(0.2)
        n = len(t)

        # LAYER 1: Click/Mallet — noise + resonant HP
        click_noise = rng.randn(n)
        click = hp(click_noise, 3000 + variation * 500) * np.exp(-t * (120 + variation * 30))
        # Resonant character
        click = bp(click, 2500 + variation * 300, 7000 + variation * 500, order=2) * 2.5
        click *= np.exp(-t * 100) * 0.5

        # LAYER 2: Deep punch — sine with pitch env, tuned to E
        target_freq = ROOT_FREQ  # E2 = 82.4 Hz
        pitch = target_freq + (250 + variation * 50) * np.exp(-t * (55 + variation * 10))
        phase = 2 * np.pi * np.cumsum(pitch) / SR
        body = np.sin(phase)
        body_amp = np.exp(-t * (12 + variation * 2))

        # Combine layers (click slightly delayed for punch)
        delay_samples = int(SR * 0.002)  # 2ms delay on click
        kick = body * body_amp * 0.8
        if delay_samples < n:
            kick[delay_samples:] += click[:n - delay_samples] * 0.6

        # THE 300Hz NOTCH — signature dark psy technique
        kick = notch(kick, 300, q=8)

        # Sub HP to remove DC
        kick = hp(kick, 28)

        # Character distortion
        kick = waveshape(kick * vel * 1.3, 2.0 + variation * 0.5)

        return kick * 0.9

    for bar in range(TOTAL_BARS):
        if in_sec(bar, SEC_BREAK + SEC_INTRO[:1]):
            continue
        if in_sec(bar, [(0, 4)]):
            continue

        # Fills before transitions
        is_fill = bar in [15, 47, 55, 79, 127, 139, 163, 175]

        if is_fill:
            # Accelerating fill
            positions = [0, 0.5, 0.75, 0.875, 0.9375]
            for p in positions:
                v = 0.7 + p * 0.3
                kick = make_kick(vel=v, variation=rng.randint(0, 3))
                pos = int((bar * BAR + p * BAR) * SR)
                add_st(L, R, kick, max(0, pos), pan=rng.uniform(-0.04, 0.04))
            continue

        # Build sections: sparse kick
        if in_sec(bar, SEC_BUILD):
            beats = [0, 2] if bar % 2 == 0 else [0, 1, 2, 3]
        else:
            beats = [0, 1, 2, 3]

        for beat in beats:
            # Skip occasionally (not beat 1)
            if beat != 0 and rng.random() > 0.96:
                continue

            vel = 0.78 + rng.random() * 0.18
            # Micro-timing
            timing = rng.normal(0, 0.003)
            variation = rng.randint(0, 4)
            kick = make_kick(vel=vel, variation=variation)

            pos = int((bar * BAR + beat * BEAT + timing) * SR)
            add_st(L, R, kick, max(0, pos), pan=rng.uniform(-0.03, 0.03))

    return L, R


# ============================================================
# ROLLING BASS — Phase-designed, no sidechain
# ============================================================
def gen_bass():
    print("  [2/9] Rolling bass (phase-interlocked)...")
    L = np.zeros(TOTAL_SAMPLES)
    R = np.zeros(TOTAL_SAMPLES)

    # Kick tail duration ≈ 60ms. Bass starts AFTER kick tail.
    kick_tail = 0.055  # seconds — bass onset delayed to avoid phase clash

    base_patterns = [
        [0]*16,
        [0,0,4,0, 0,0,4,0, 0,0,0,0, 0,0,4,0],
        [0,0,1,0, 0,0,1,0, 0,0,0,0, 0,1,0,0],
        [0,0,4,5, 0,0,4,0, 0,0,0,7, 0,0,4,0],
        [0,0,7,4, 0,0,1,0, 0,4,0,0, 0,0,7,5],
        [0,0,0,4, 0,7,0,4, 0,0,5,0, 7,0,4,0],
        [0,4,0,7, 0,0,5,0, 0,4,0,1, 0,0,7,4],  # chromatic madness
    ]

    def mutate(pat, rate=0.12):
        p = list(pat)
        for i in range(len(p)):
            if rng.random() < rate and i > 0:
                p[i] = rng.choice([0, 1, 4, 5, 7])
        return p

    for bar in range(TOTAL_BARS):
        if in_sec(bar, SEC_BREAK + SEC_INTRO):
            continue
        if bar < 8:
            continue

        # Pattern selection with mutation
        base = base_patterns[(bar // 4) % len(base_patterns)]
        pat = mutate(base, 0.08 if in_sec(bar, SEC_DROP) else 0.03)

        # More wild patterns in later drops
        if in_sec(bar, [(80, 128)]) and bar % 8 > 5:
            pat = mutate(base_patterns[rng.randint(len(base_patterns))], 0.2)

        for step in range(16):
            note = ROOT + pat[step]
            freq = note_freq(note)

            # Phase-designed timing: on beat 1, delay bass after kick tail
            is_on_beat = step % 4 == 0
            bass_delay = kick_tail * 0.6 if is_on_beat else 0

            timing = bass_delay + rng.normal(0, 0.002)
            vel = 0.7 + 0.25 * (step % 4 == 0) + rng.uniform(-0.05, 0.05)

            # Ghost note probability
            if step % 4 != 0 and rng.random() > 0.9:
                continue

            dur = S16 * (0.78 + rng.random() * 0.15)
            t = t_arr(dur)
            n = len(t)

            # Oscillator: saw (primary) + phase-synced reset
            phase_offset = rng.uniform(0, 0.1)  # slight phase variation
            saw = sawtooth(2 * np.pi * freq * t + phase_offset)

            # Sub layer
            sub = np.sin(2 * np.pi * freq * 0.5 * t) * 0.4

            # Mix
            raw = saw * 0.6 + sub * 0.4

            # LP filter at 40-60Hz range, envelope opens it
            cutoff_base = 45 + 20 * (step % 4 == 0)
            # Filter envelope: opens quickly then closes
            cutoff_peak = cutoff_base + 2000 * vel
            cutoff_env = cutoff_base + (cutoff_peak - cutoff_base) * np.exp(-t * 18)
            avg_cutoff = float(np.mean(cutoff_env))
            raw = lp(raw, avg_cutoff)

            # MULTIBAND SATURATION — key for harmonic content in 200-600Hz
            # Saturate mids separately
            mid_content = bp(raw, 150, 800)
            mid_sat = waveshape(mid_content * 3.0, 4.0)
            raw = raw + mid_sat * 0.3

            # Overall saturation
            raw = waveshape(raw * 1.5 * vel, 2.5 + rng.random())

            # Amp envelope
            amp = np.ones(n)
            atk = min(int(rng.uniform(10, 35)), n)
            amp[:atk] = np.linspace(0, 1, atk)
            dec = int(n * (0.65 + rng.random() * 0.15))
            if dec < n:
                amp[dec:] = np.linspace(1, 0.1, n - dec)

            bass = raw * amp * 0.65

            pos = int((bar * BAR + step * S16 + timing) * SR)
            p = np.sin(step * 0.25 + bar * 0.07) * 0.08
            add_st(L, R, bass, max(0, pos), pan=p)

    return L, R


# ============================================================
# FM TEXTURES — Alien leads, metallic sounds
# ============================================================
def gen_fm_textures():
    print("  [3/9] FM textures (alien, metallic)...")
    L = np.zeros(TOTAL_SAMPLES)
    R = np.zeros(TOTAL_SAMPLES)

    # FM patches that evolve over the track
    for bar in range(TOTAL_BARS):
        if bar < 16: continue
        if in_sec(bar, SEC_BREAK):
            continue

        # FM lead phrases — sporadic, unpredictable
        if rng.random() > 0.6:
            continue

        n_notes = rng.randint(2, 6)
        t_off = rng.uniform(0, BAR * 0.3)

        for _ in range(n_notes):
            # Scale notes: E phrygian dominant
            scale = [40, 41, 44, 45, 47, 48, 50, 52, 53, 56, 57, 59, 60, 62, 64, 65, 68]
            note = scale[rng.randint(len(scale))]
            freq = note_freq(note + 12)  # one octave up

            dur = rng.uniform(0.05, 0.4)
            t = t_arr(dur)

            # FM params — evolve over track
            mod_ratio = rng.choice([1, 1.5, 2, 3, 4, 5.33, 7])
            mod_freq_val = freq * mod_ratio
            # Mod index increases through track = more complex later
            track_progress = bar / TOTAL_BARS
            mod_index = rng.uniform(1, 4) + track_progress * 6

            # FM synthesis
            fm = fm_synth(t, freq, mod_freq_val, mod_index)

            # Envelope: sharp attack, variable decay
            amp = adsr(t, a=0.002, d=rng.uniform(0.02, 0.15), s=0.3, r=0.05, dur=dur)
            fm = fm * amp * 0.25

            # Saturation for edge
            fm = waveshape(fm * 1.5, 2.0)

            pos = int((bar * BAR + t_off) * SR)
            pan = rng.uniform(-0.6, 0.6)
            add_st(L, R, fm, max(0, pos), pan=pan)

            t_off += dur + rng.uniform(0, S16 * 2)

    return L * 0.45, R * 0.45


# ============================================================
# FILTER FM — The "electricity" sound of dark psy
# ============================================================
def gen_electricity():
    print("  [4/9] Filter FM (electricity)...")
    L = np.zeros(TOTAL_SAMPLES)
    R = np.zeros(TOTAL_SAMPLES)

    for bar in range(TOTAL_BARS):
        if bar < 20: continue

        # Appears in drops, sporadic
        if not in_sec(bar, SEC_DROP): continue
        if rng.random() > 0.4: continue

        dur = rng.uniform(0.5, 2.0)
        t = t_arr(dur)

        base_freq = note_freq(ROOT + rng.choice([0, 12, 7, 5]))
        mod_rate = rng.uniform(0.5, 4.0)

        elec = filter_fm(t, base_freq, mod_rate,
                         resonance=0.85 + rng.random() * 0.12,
                         sweep_range=(200 + rng.random()*500, 5000 + rng.random()*6000))

        # Amp envelope
        amp = adsr(t, a=0.01, d=0.1, s=0.6, r=0.15, dur=dur)
        elec = elec * amp * 0.2

        pos = int((bar * BAR + rng.uniform(0, BAR * 0.5)) * SR)
        pan = rng.uniform(-0.5, 0.5)
        add_st(L, R, elec, max(0, pos), pan=pan)

    return L * 0.5, R * 0.5


# ============================================================
# HI-HATS + PERCUSSION (combined, organic)
# ============================================================
def gen_drums():
    print("  [5/9] Hats + Percussion (organic)...")
    L = np.zeros(TOTAL_SAMPLES)
    R = np.zeros(TOTAL_SAMPLES)

    for bar in range(TOTAL_BARS):
        if bar < 8: continue
        if in_sec(bar, SEC_BREAK[:1]): continue

        for step in range(16):
            timing = rng.normal(0, 0.004)

            # Offbeat hat
            if step % 4 == 2 and rng.random() < 0.92:
                dur = S16 * rng.uniform(0.4, 0.7)
                t = t_arr(dur)
                hat = hp(rng.randn(len(t)), 6000 + rng.random()*3000)
                hat *= np.exp(-t * (25 + rng.random()*20)) * rng.uniform(0.18, 0.3)
                pos = int((bar*BAR + step*S16 + timing)*SR)
                add_st(L, R, hat, max(0, pos), pan=0.15 + rng.uniform(-0.1, 0.1))

            # Ghost hats
            elif step % 2 == 1 and rng.random() < 0.5:
                dur = S16 * rng.uniform(0.2, 0.35)
                t = t_arr(dur)
                hat = hp(rng.randn(len(t)), 8000+rng.random()*3000)
                hat *= np.exp(-t * (40+rng.random()*25)) * rng.uniform(0.06, 0.12)
                pos = int((bar*BAR + step*S16 + timing)*SR)
                add_st(L, R, hat, max(0, pos), pan=rng.uniform(-0.5, 0.5))

            # Open hat
            if step == 12 and bar % 4 == 3 and rng.random() < 0.75:
                dur = S16 * rng.uniform(1.5, 3.0)
                t = t_arr(dur)
                hat = bp(rng.randn(len(t)), 4000+rng.random()*2000, 14000)
                hat *= np.exp(-t * (5+rng.random()*4)) * 0.25
                pos = int((bar*BAR + step*S16 + timing)*SR)
                add_st(L, R, hat, max(0, pos), pan=0.3+rng.uniform(-0.15, 0.15))

        # Clap on 2 and 4
        if bar >= 12:
            for beat in [1, 3]:
                if rng.random() > 0.04:
                    t = t_arr(rng.uniform(0.06, 0.1))
                    clap = np.zeros(len(t))
                    for i in range(rng.randint(2, 5)):
                        d = int(i * SR * rng.uniform(0.003, 0.007))
                        b = bp(rng.randn(len(t)), 700+rng.random()*500, 4000+rng.random()*1500)
                        b *= np.exp(-t * (25+rng.random()*15))
                        if d < len(clap):
                            clap[d:] += b[:len(clap)-d] * (0.7**i)
                    clap *= rng.uniform(0.2, 0.35)
                    pos = int((bar*BAR + beat*BEAT + rng.normal(0,0.003))*SR)
                    add_st(L, R, clap, max(0, pos), pan=rng.uniform(-0.08, 0.08))

        # Tribal elements
        if bar >= 16 and bar % 2 == 1 and rng.random() < 0.55:
            hit_t = rng.uniform(2.5, 3.8)
            t = t_arr(rng.uniform(0.08, 0.15))
            freq = rng.uniform(70, 150)
            tom = np.sin(2*np.pi*freq*t*np.exp(-t*(3+rng.random()*4)))
            tom *= np.exp(-t*(8+rng.random()*6)) * 0.3
            tom = waveshape(tom, 1.5)
            pos = int((bar*BAR + hit_t*BEAT)*SR)
            add_st(L, R, tom, max(0, pos), pan=rng.uniform(-0.4, 0.4))

    return L, R


# ============================================================
# LEAD — Supersaw + FM hybrid, matices de luz
# ============================================================
def gen_lead():
    print("  [6/9] Lead (matices de luz)...")
    L = np.zeros(TOTAL_SAMPLES)
    R = np.zeros(TOTAL_SAMPLES)

    scale = [52,53,56,57,59,60,62,64,65,68,69,71,72,74,76,77,80]

    phrases = [
        [(64,0.5,0.8),(68,0.75,1.0),(69,0.25,0.7),(71,1.0,1.0),(68,0.5,0.8)],
        [(76,0.5,0.9),(72,0.5,0.8),(71,0.5,0.7),(68,1.5,1.0)],
        [(80,1.0,0.6),(76,0.5,0.7),(72,1.0,0.9),(71,0.5,0.8),(68,1.0,1.0)],
        [(64,0.5,0.9),(62,0.5,0.8),(60,0.5,0.7),(64,0.5,0.8),(68,1.0,1.0),(72,1.0,0.9)],
        [(71,0.5,0.9),(72,0.5,1.0),(76,1.0,0.8),(72,0.5,0.7),(68,1.5,1.0)],
    ]

    def mutate_phrase(ph):
        p = list(ph)
        for i in range(len(p)):
            n, d, v = p[i]
            if rng.random() < 0.25:
                n += rng.choice([-3,-2,-1,1,2,3,4])
                n = max(52, min(84, n))
            if rng.random() < 0.15:
                d *= rng.uniform(0.7, 1.4)
            p[i] = (n, d, np.clip(v * rng.uniform(0.8, 1.1), 0.3, 1.0))
        return p

    melody_bars = list(range(20, 48)) + list(range(56, 72)) + list(range(84, 128)) + list(range(140, 156)) + list(range(168, 176))
    pidx = 0

    for bar in melody_bars:
        if bar >= TOTAL_BARS: break
        if rng.random() < 0.15: continue  # breathing

        ph = mutate_phrase(phrases[pidx % len(phrases)]) if rng.random() > 0.25 else phrases[pidx % len(phrases)]
        t_off = 0

        for note, dur, vel in ph:
            freq = note_freq(note)
            note_dur = dur * BEAT * rng.uniform(0.88, 1.08)
            t = t_arr(note_dur)
            n = len(t)

            # HYBRID: Supersaw + FM for richness
            spread = rng.uniform(0.003, 0.008)
            saw_mix = np.zeros(n)
            for dt in [1-spread*2, 1-spread, 1.0, 1+spread, 1+spread*2]:
                saw_mix += sawtooth(2*np.pi*freq*dt*t)
            saw_mix /= 5

            # FM component
            fm_comp = fm_synth(t, freq, freq * rng.choice([2, 3, 4]), rng.uniform(0.5, 2.0))

            # Mix saw + FM
            lead = saw_mix * 0.7 + fm_comp * 0.3

            # Filter
            lead = bp(lead, 300, min(freq*8, SR/2-100))

            # Vibrato
            vib = 1.0 + rng.uniform(0.002, 0.006) * np.sin(2*np.pi*rng.uniform(4, 7)*t) * np.clip((t-0.08)*5, 0, 1)
            # (applied as subtle pitch mod via amplitude modulation)

            amp = adsr(t, a=rng.uniform(0.008, 0.025), d=0.08, s=0.7, r=0.1, dur=note_dur)
            lead = waveshape(lead * 1.2, 1.5) * amp * vel * 0.3

            pos = int((bar*BAR + t_off + rng.normal(0, 0.004))*SR)
            add_st(L, R, lead, max(0, pos), pan=0.2+rng.uniform(-0.1, 0.1))
            t_off += dur * BEAT

        pidx += 1

    # Ping-pong delay
    dt = int(BEAT * 0.75 * SR)
    for i in range(5):
        d = dt*(i+1)
        decay = 0.28**(i+1)
        if d < TOTAL_SAMPLES:
            if i % 2 == 0:
                L[d:] += R[:TOTAL_SAMPLES-d]*decay*0.35
            else:
                R[d:] += L[:TOTAL_SAMPLES-d]*decay*0.35

    return L * 0.5, R * 0.5


# ============================================================
# ATMOSPHERE — Deep pads + granular textures
# ============================================================
def gen_atmosphere():
    print("  [7/9] Atmosphere (pads + granular)...")
    L = np.zeros(TOTAL_SAMPLES)
    R = np.zeros(TOTAL_SAMPLES)

    chords = [
        [52,56,59],[53,57,60],[57,60,64],[50,53,57],
        [56,59,62],[52,56,59],[48,52,56],[52,56,59],
    ]

    bpc = 4
    for ci in range(TOTAL_BARS // bpc + 1):
        sb = ci * bpc
        if sb >= TOTAL_BARS: break

        chord = chords[ci % len(chords)]
        if rng.random() < 0.25:
            chord = chord + [chord[0] + rng.choice([14, 17, 21])]

        dur = min(bpc * BAR, (TOTAL_BARS - sb) * BAR)
        t = t_arr(dur)
        n = len(t)

        pL = np.zeros(n)
        pR = np.zeros(n)

        for i, note in enumerate(chord):
            freq = note_freq(note)
            det = rng.uniform(0.002, 0.005)
            oL = np.sin(2*np.pi*freq*(1-det)*t)
            oR = np.sin(2*np.pi*freq*(1+det)*t)
            saw = sawtooth(2*np.pi*freq*t) * 0.2
            saw_f = lp(saw, min(freq*2.5, SR/2-100))

            lfo_r = 0.06 + i*0.04 + rng.random()*0.05
            lfo_ph = rng.random()*2*np.pi
            lfo = 0.5 + 0.5*np.sin(2*np.pi*lfo_r*t + lfo_ph)

            pL += (oL*0.35 + saw_f*0.5) * lfo
            pR += (oR*0.35 + saw_f*0.5) * lfo

        pL /= len(chord)
        pR /= len(chord)

        fade = min(int(3*SR), n//3)
        pL[:fade] *= np.linspace(0,1,fade)
        pL[-fade:] *= np.linspace(1,0,fade)
        pR[:fade] *= np.linspace(0,1,fade)
        pR[-fade:] *= np.linspace(1,0,fade)

        pos = int(sb*BAR*SR)
        end = min(pos+n, TOTAL_SAMPLES)
        nn = end-pos
        L[pos:end] += pL[:nn]
        R[pos:end] += pR[:nn]

    return L * 0.32, R * 0.32


# ============================================================
# GRANULAR LAYER — Micro-particle textures
# ============================================================
def gen_granular(bass_L, fm_L):
    print("  [8/9] Granular textures (resampled)...")
    L = np.zeros(TOTAL_SAMPLES)
    R = np.zeros(TOTAL_SAMPLES)

    # Source material: resample from bass and FM
    sources = []
    # Grab chunks from bass
    for i in range(8):
        start = int(rng.uniform(0.1, 0.8) * TOTAL_SAMPLES)
        chunk_len = int(SR * rng.uniform(1, 4))
        end = min(start + chunk_len, TOTAL_SAMPLES)
        if end - start > SR:
            sources.append(bass_L[start:end])
    # Grab chunks from FM
    for i in range(4):
        start = int(rng.uniform(0.2, 0.9) * TOTAL_SAMPLES)
        chunk_len = int(SR * rng.uniform(0.5, 2))
        end = min(start + chunk_len, TOTAL_SAMPLES)
        if end - start > SR // 2:
            sources.append(fm_L[start:end])

    if not sources:
        # Fallback: generate noise source
        sources = [rng.randn(SR * 2)]

    # Scatter granular textures across track, heavier in drops and breakdowns
    for bar in range(TOTAL_BARS):
        if bar < 16: continue

        if in_sec(bar, SEC_DROP):
            density = rng.uniform(8, 20)
            scatter = rng.uniform(0.15, 0.3)
        elif in_sec(bar, SEC_BREAK):
            density = rng.uniform(5, 12)
            scatter = rng.uniform(0.2, 0.4)
        elif in_sec(bar, SEC_TRANS):
            density = rng.uniform(10, 25)
            scatter = rng.uniform(0.2, 0.35)
        else:
            continue

        source = sources[rng.randint(len(sources))]
        gL, gR = granular_texture(
            source, BAR,
            grain_size_range=(0.008 + rng.random()*0.02, 0.05 + rng.random()*0.06),
            density=density,
            pitch_range=(0.3 + rng.random()*0.5, 1.5 + rng.random()*1.5),
            scatter=scatter
        )

        pos = int(bar * BAR * SR)
        end = min(pos + len(gL), TOTAL_SAMPLES)
        nn = end - pos
        if nn > 0:
            L[pos:end] += gL[:nn]
            R[pos:end] += gR[:nn]

    return L * 0.4, R * 0.4


# ============================================================
# FX — Risers, impacts, sweeps
# ============================================================
def gen_fx():
    print("  [9/9] FX (risers, impacts)...")
    L = np.zeros(TOTAL_SAMPLES)
    R = np.zeros(TOTAL_SAMPLES)

    def make_riser(duration):
        t = t_arr(duration)
        n = len(t)
        noise = rng.randn(n)
        riser = np.zeros(n)
        chunks = 80
        cs = n // chunks
        for i in range(chunks):
            s, e = i*cs, min((i+1)*cs, n)
            fc = 60 + (16000*(i/chunks)**2.5)
            fc = min(fc, SR/2-100)
            c = noise[s:e]
            if len(c) > 20:
                riser[s:e] = lp(c, fc)
        riser *= np.linspace(0, 1, n)**2.0
        return riser * 0.3

    def make_impact():
        t = t_arr(1.2)
        noise = lp(rng.randn(len(t)), 2000) * 0.3
        sub = np.sin(2*np.pi*ROOT_FREQ*0.5*t) * np.exp(-t*3)
        return (noise + sub*0.7) * np.exp(-t*3.5) * 0.7

    # Risers
    for bar, dur in [(12,4),(70,8),(154,8)]:
        if bar >= TOTAL_BARS: continue
        r = make_riser(dur*BAR)
        pos = int(bar*BAR*SR)
        add_st(L, R, r, max(0, pos), pan=0.0)
        r2 = make_riser(dur*BAR) * 0.4
        add_st(L, R, r2, max(0, pos), pan=rng.uniform(-0.6, 0.6))

    # Impacts
    imp = make_impact()
    for db in [16, 80, 164]:
        if db >= TOTAL_BARS: continue
        pos = int(db*BAR*SR)
        add_st(L, R, imp, max(0, pos), pan=0.0)

    # Downlifters
    for bar in [48, 128]:
        if bar >= TOTAL_BARS: continue
        t = t_arr(3*BAR)
        n = len(t)
        noise = rng.randn(n)
        dl = np.zeros(n)
        chunks = 40
        cs = n // chunks
        for i in range(chunks):
            s, e = i*cs, min((i+1)*cs, n)
            fc = 14000 - 13500*(i/chunks)
            fc = max(min(fc, SR/2-100), 30)
            c = noise[s:e]
            if len(c) > 20:
                dl[s:e] = lp(c, fc)
        dl *= np.linspace(1, 0, n)**1.2 * 0.2
        pos = int(bar*BAR*SR)
        add_st(L, R, dl, max(0, pos), pan=rng.uniform(-0.3, 0.3))

    return L, R


# ============================================================
# RENDER
# ============================================================
print()
print("Sintetizando...")

kick_L, kick_R = gen_kick()
bass_L, bass_R = gen_bass()
fm_L, fm_R = gen_fm_textures()
elec_L, elec_R = gen_electricity()
drums_L, drums_R = gen_drums()
lead_L, lead_R = gen_lead()
atmo_L, atmo_R = gen_atmosphere()
# Granular needs bass and FM as source material
gran_L, gran_R = gen_granular(bass_L + bass_R, fm_L + fm_R)
fx_L, fx_R = gen_fx()

print()
print("Mezclando (wall of sound)...")

mix_L = np.zeros(TOTAL_SAMPLES)
mix_R = np.zeros(TOTAL_SAMPLES)

mix_L += kick_L * 0.90;    mix_R += kick_R * 0.90
mix_L += bass_L * 0.85;    mix_R += bass_R * 0.85
mix_L += fm_L * 0.50;      mix_R += fm_R * 0.50
mix_L += elec_L * 0.45;    mix_R += elec_R * 0.45
mix_L += drums_L * 0.55;   mix_R += drums_R * 0.55
mix_L += lead_L * 0.52;    mix_R += lead_R * 0.52
mix_L += atmo_L * 0.40;    mix_R += atmo_R * 0.40
mix_L += gran_L * 0.38;    mix_R += gran_R * 0.38
mix_L += fx_L * 0.48;      mix_R += fx_R * 0.48

# Phase-designed bass/kick — minimal sidechain, just 15% duck
print("Sidechain (light, phase-designed)...")
k_mono = (kick_L + kick_R) / 2
k_env = np.abs(k_mono)
win = int(0.03 * SR)
k_sm = np.convolve(k_env, np.ones(win)/win, mode='same')
k_sm /= (np.max(k_sm) + 1e-10)
sc = 1.0 - k_sm * 0.15  # only 15% — phase design handles the rest

nk_L = mix_L - kick_L * 0.90
nk_R = mix_R - kick_R * 0.90
mix_L = kick_L * 0.90 + nk_L * sc
mix_R = kick_R * 0.90 + nk_R * sc

# MASTERING
print("Masterizando...")

# HPF
mix_L = hp(mix_L, 25)
mix_R = hp(mix_R, 25)

# Tame sub (target: ~13% like Glosolalia, not 25%+)
sub_L = lp(mix_L, 60)
sub_R = lp(mix_R, 60)
mix_L -= sub_L * 0.35
mix_R -= sub_R * 0.35

# Boost low-mids (200-600Hz, target: ~17%)
mid_L = bp(mix_L, 200, 600)
mid_R = bp(mix_R, 200, 600)
mix_L += mid_L * 0.4
mix_R += mid_R * 0.4

# Boost mids (600-2kHz, target: ~9%)
mid2_L = bp(mix_L, 600, 2000)
mid2_R = bp(mix_R, 600, 2000)
mix_L += mid2_L * 0.35
mix_R += mid2_R * 0.35

# Boost presence (2k-6k, target: ~3.8%)
pres_L = bp(mix_L, 2000, 6000)
pres_R = bp(mix_R, 2000, 6000)
mix_L += pres_L * 0.25
mix_R += pres_R * 0.25

# Air (6k-16k)
air_L = bp(mix_L, 6000, 16000)
air_R = bp(mix_R, 6000, 16000)
mix_L += air_L * 0.15
mix_R += air_R * 0.15

# Multiband saturation
mix_L = waveshape(mix_L, 1.8)
mix_R = waveshape(mix_R, 1.8)

# Normalize
peak = max(np.max(np.abs(mix_L)), np.max(np.abs(mix_R)))
if peak > 0:
    mix_L /= peak
    mix_R /= peak

# Target RMS: -9 dB
rms = np.sqrt(np.mean(mix_L**2 + mix_R**2)/2)
target = 10**(-9.0/20)
if rms > 0:
    gain = min(target/rms, 3.0)
    mix_L *= gain
    mix_R *= gain

mix_L = np.clip(mix_L, -0.98, 0.98)
mix_R = np.clip(mix_R, -0.98, 0.98)

# SAVE
print("Guardando...")
stereo = np.column_stack([
    (mix_L*32767).astype(np.int16),
    (mix_R*32767).astype(np.int16)
])

output = os.path.join(OUTPUT_DIR, "DarkPsy_v4_GENRE_ACCURATE.wav")
wavfile.write(output, SR, stereo)

import shutil
desktop = "C:/Users/Juan/Desktop/DarkPsy_v4_GENRE_ACCURATE.wav"
shutil.copy2(output, desktop)

# Verification
print()
print("--- Verificación espectral ---")
mc = (mix_L+mix_R)/2
fft_c = np.abs(np.fft.rfft(mc))
freqs_c = np.fft.rfftfreq(len(mc), 1/SR)
te = np.sum(fft_c**2)
for nm, lo, hi in [('Sub 20-60',20,60),('Bass 60-200',60,200),('LowMid 200-600',200,600),
                    ('Mid 600-2k',600,2000),('HiMid 2k-6k',2000,6000),('Pres 6k-10k',6000,10000),
                    ('Air 10k-20k',10000,20000)]:
    mask = (freqs_c >= lo) & (freqs_c < hi)
    pct = np.sum(fft_c[mask]**2)/te*100
    bar = '#'*int(pct/2)
    print(f'  {nm:18s}: {pct:5.1f}%  {bar}')
rms_f = np.sqrt(np.mean(mc**2))
print(f'  RMS: {20*np.log10(rms_f+1e-10):.1f} dB')

# Entropy check
entropies = []
fs = SR
for i in range(0, len(mc)-fs, fs):
    frame = mc[i:i+fs]
    ff = np.abs(np.fft.rfft(frame))
    ff = ff/(np.sum(ff)+1e-10)
    ff = ff[ff > 0]
    entropies.append(-np.sum(ff*np.log2(ff)))
print(f'  Entropía media: {np.mean(entropies):.2f} bits (target: ~12.5)')

print()
print("=" * 60)
print(f" TRACK: {desktop}")
print(f" Duración: {TOTAL_TIME/60:.1f} min | STEREO")
print(f" Técnicas: FM synthesis, Filter FM, Granular, 300Hz notch kick")
print(f" Calibrado contra: Glosolalia spectral profile")
print("=" * 60)
