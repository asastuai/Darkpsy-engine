"""
DARK PSYTRANCE v2 — Calibrado contra Glosolalia
Correcciones: más mids, menos sub, stereo, más loudness, 7 minutos
"""

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt, sawtooth, square
import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
SR = 44100
BPM = 148  # closer to Glosolalia range
BEAT = 60.0 / BPM
BAR = BEAT * 4
TOTAL_BARS = 112  # ~7 minutes
TOTAL_TIME = TOTAL_BARS * BAR
TOTAL_SAMPLES = int(TOTAL_TIME * SR)

print("=" * 60)
print(" DARK PSYTRANCE v2 — Calibrado contra Glosolalia")
print(f" BPM: {BPM} | Bars: {TOTAL_BARS} | Duration: {TOTAL_TIME:.0f}s ({TOTAL_TIME/60:.1f} min)")
print("=" * 60)

np.random.seed(42)


def t_arr(duration):
    return np.linspace(0, duration, int(duration * SR), endpoint=False)


def lp(sig, cutoff, order=4):
    cutoff = min(cutoff, SR/2 - 100)
    return sosfilt(butter(order, cutoff, btype='low', fs=SR, output='sos'), sig)


def hp(sig, cutoff, order=2):
    cutoff = max(cutoff, 20)
    return sosfilt(butter(order, cutoff, btype='high', fs=SR, output='sos'), sig)


def bp(sig, lo, hi, order=2):
    lo = max(lo, 20)
    hi = min(hi, SR/2 - 100)
    if lo >= hi:
        return sig
    return sosfilt(butter(order, [lo, hi], btype='band', fs=SR, output='sos'), sig)


def note_freq(note):
    return 440.0 * (2.0 ** ((note - 69) / 12.0))


def adsr(t, a=0.01, d=0.1, s=0.7, r=0.2, dur=None):
    if dur is None:
        dur = t[-1] if len(t) > 0 else 1.0
    env = np.zeros_like(t)
    for i, ti in enumerate(t):
        if ti < a:
            env[i] = ti / a if a > 0 else 1.0
        elif ti < a + d:
            env[i] = 1.0 - (1.0 - s) * (ti - a) / d
        elif ti < dur - r:
            env[i] = s
        else:
            env[i] = s * max(0, (dur - ti) / r) if r > 0 else 0
    return env


def soft_clip(sig, thresh=0.8):
    return np.tanh(sig / thresh) * thresh


def waveshape(sig, amount=2.0):
    """Tube-style saturation — adds harmonics in the mids"""
    return np.tanh(sig * amount) / np.tanh(amount)


def pan_stereo(mono, pan=0.0):
    """Pan: -1=left, 0=center, 1=right. Returns (L, R)"""
    l_gain = np.cos((pan + 1) / 2 * np.pi / 2)
    r_gain = np.sin((pan + 1) / 2 * np.pi / 2)
    return mono * l_gain, mono * r_gain


def add_stereo(out_L, out_R, mono, pos, pan=0.0):
    L, R = pan_stereo(mono, pan)
    end = min(pos + len(L), len(out_L))
    n = end - pos
    if n > 0:
        out_L[pos:end] += L[:n]
        out_R[pos:end] += R[:n]


# ============================================================
# STRUCTURE MAP
# ============================================================
# Bars   0-7:   INTRO (kick + minimal bass, building)
# Bars   8-15:  BUILD (acid enters, hats, energy rising)
# Bars  16-39:  DROP 1 (full energy, lead melody)
# Bars  40-47:  TRANSITION (elements dropping, filter sweep)
# Bars  48-63:  BREAKDOWN (pads + ethereal lead = matices de luz)
# Bars  64-71:  BUILD 2 (riser, energy returning)
# Bars  72-95:  DROP 2 (full energy, variation, climax)
# Bars  96-103: TRANSITION 2
# Bars 104-111: OUTRO (elements dropping out)

def in_section(bar, sections):
    """Check if bar is in any of the given section ranges"""
    for s, e in sections:
        if s <= bar < e:
            return True
    return False


# ============================================================
# KICK — Punchier, less sub, more click
# ============================================================
def gen_kick():
    print("  [1/8] Kick...")
    L = np.zeros(TOTAL_SAMPLES)
    R = np.zeros(TOTAL_SAMPLES)

    def make_kick():
        t = t_arr(0.22)
        # Pitch: higher start for more click, controlled sub
        pitch = 50 + 180 * np.exp(-t * 50)
        phase = 2 * np.pi * np.cumsum(pitch) / SR
        body = np.sin(phase)
        # Amp envelope — tighter
        amp = np.exp(-t * 15)
        # Click layer — band-passed noise
        click = bp(np.random.randn(len(t)), 2000, 6000) * np.exp(-t * 150) * 0.5
        # Sub control — high-pass at 35Hz to tame excessive sub
        kick = body * amp + click
        kick = hp(kick, 35)
        # Saturation for harmonics
        kick = waveshape(kick * 1.3, 2.5)
        return kick * 0.85

    kick = make_kick()

    active_sections = [(0, 40), (64, 104)]
    silent_sections = [(48, 64)]  # breakdown

    for bar in range(TOTAL_BARS):
        if in_section(bar, silent_sections):
            continue
        if not in_section(bar, active_sections) and bar < 104:
            # Outro: every other beat
            for beat in [0, 2]:
                pos = int((bar * BAR + beat * BEAT) * SR)
                end = min(pos + len(kick), TOTAL_SAMPLES)
                L[pos:end] += kick[:end-pos]
                R[pos:end] += kick[:end-pos]
            continue

        for beat in range(4):
            pos = int((bar * BAR + beat * BEAT) * SR)
            end = min(pos + len(kick), TOTAL_SAMPLES)
            L[pos:end] += kick[:end-pos]
            R[pos:end] += kick[:end-pos]

    return L, R


# ============================================================
# ROLLING BASS — More harmonics, body in 200-600Hz
# ============================================================
def gen_bass():
    print("  [2/8] Rolling bass...")
    L = np.zeros(TOTAL_SAMPLES)
    R = np.zeros(TOTAL_SAMPLES)
    sixteenth = BEAT / 4
    root = 40  # E2

    patterns = [
        [0]*16,
        [0,0,4,0, 0,0,4,0, 0,0,0,0, 0,0,4,0],
        [0,0,1,0, 0,0,1,0, 0,0,0,0, 0,1,0,0],
        [0,0,4,5, 0,0,4,0, 0,0,0,7, 0,0,4,0],
        [0,0,7,4, 0,0,1,0, 0,4,0,0, 0,0,7,5],  # new: more melodic
    ]

    for bar in range(TOTAL_BARS):
        if in_section(bar, [(48, 64)]):
            continue
        if bar < 1:
            continue

        # Progressive pattern selection
        if bar < 8:
            pat = patterns[0]
        elif bar < 16:
            pat = patterns[1]
        elif bar < 40:
            pat = patterns[(bar // 4) % 4]
        elif bar < 48:
            pat = patterns[1]  # simpler transition
        elif bar < 72:
            pat = patterns[2]
        elif bar < 96:
            pat = patterns[(bar // 4) % 5]  # all patterns
        else:
            pat = patterns[0]  # outro: simple

        for step in range(16):
            note = root + pat[step]
            freq = note_freq(note)
            t = t_arr(sixteenth * 0.88)
            n = len(t)

            # Multi-oscillator: saw + square + sub sine
            saw = sawtooth(2 * np.pi * freq * t)
            sq = square(2 * np.pi * freq * t, duty=0.3) * 0.4
            sub = np.sin(2 * np.pi * freq * 0.5 * t) * 0.5

            # Mix oscillators
            raw = saw * 0.5 + sq * 0.3 + sub * 0.2

            # Filter envelope
            accent = 1.0 if step % 4 == 0 else 0.5
            cutoff_base = 600 + 2500 * accent
            # Dynamic filter per-sample approximation
            raw_filtered = lp(raw, min(cutoff_base, SR/2-100))

            # HEAVY saturation for mid harmonics (key fix!)
            raw_sat = waveshape(raw_filtered * 2.0, 3.0)

            # Amp envelope
            amp = np.ones(n)
            attack = min(30, n)
            amp[:attack] = np.linspace(0, 1, attack)
            decay_start = int(n * 0.7)
            amp[decay_start:] = np.linspace(1, 0.2, n - decay_start)

            # Velocity
            vel = 0.75 + 0.25 * accent
            bass_note = raw_sat * amp * vel * 0.7

            pos = int((bar * BAR + step * sixteenth) * SR)
            # Bass: mostly center, slight movement
            p = np.sin(step * 0.3) * 0.1
            add_stereo(L, R, bass_note, pos, pan=p)

    return L, R


# ============================================================
# ACID LINE — More resonance, presence in mids
# ============================================================
def gen_acid():
    print("  [3/8] Acid line...")
    L = np.zeros(TOTAL_SAMPLES)
    R = np.zeros(TOTAL_SAMPLES)
    sixteenth = BEAT / 4

    sequences = [
        [(52,2,1),(53,1,0),(56,3,1),(52,1,0),(50,2,1),(48,1,0),(52,2,1),(41,1,0),(56,2,1),(57,1,0)],
        [(52,1,1),(56,1,0),(59,1,1),(60,2,1),(57,1,0),(53,2,1),(52,1,0),(50,1,0),(48,2,1),(52,2,1)],
        [(64,1,1),(62,1,0),(60,2,1),(56,1,0),(52,2,1),(53,1,0),(56,2,1),(59,1,1),(57,1,0),(52,2,1)],
        [(56,2,1),(59,1,0),(62,1,1),(60,2,0),(57,2,1),(53,1,0),(52,3,1),(48,1,0),(50,2,0),(52,1,1)],
    ]

    for bar in range(TOTAL_BARS):
        if bar < 8:
            continue
        if in_section(bar, [(48, 64), (104, 112)]):
            continue

        seq = sequences[bar % len(sequences)]
        t_offset = 0

        for note, dur, accent in seq:
            freq = note_freq(note)
            note_dur = dur * sixteenth
            t = t_arr(note_dur * 0.92)
            n = len(t)

            # Saw osc + slight detuned for thickness
            saw1 = sawtooth(2 * np.pi * freq * t)
            saw2 = sawtooth(2 * np.pi * freq * 1.008 * t)
            raw = (saw1 + saw2 * 0.5) / 1.5

            # Resonant filter — KEY for acid sound
            cutoff = 500 + 3500 * accent
            raw = lp(raw, cutoff)

            # Filter envelope (fast decay = squelchy)
            env_f = np.exp(-t * (8 if accent else 15))
            raw = raw * (0.3 + 0.7 * env_f)

            # Saturation for mid presence
            raw = waveshape(raw * 1.8, 2.5)

            # Amp envelope
            amp = adsr(t, a=0.003, d=0.05, s=0.65, r=0.03, dur=note_dur)
            acid = raw * amp * (0.6 if accent else 0.4)

            pos = int((bar * BAR + t_offset) * SR)
            # Pan acid slightly left
            add_stereo(L, R, acid, pos, pan=-0.25)
            t_offset += note_dur

    return L, R


# ============================================================
# HI-HATS — More definition, stereo placement
# ============================================================
def gen_hats():
    print("  [4/8] Hi-hats...")
    L = np.zeros(TOTAL_SAMPLES)
    R = np.zeros(TOTAL_SAMPLES)
    sixteenth = BEAT / 4

    for bar in range(TOTAL_BARS):
        if bar < 4:
            continue
        if in_section(bar, [(48, 60)]):
            continue

        for step in range(16):
            is_offbeat = step % 4 == 2
            is_ghost = step % 2 == 1
            is_open = step == 12 and bar % 4 == 3

            if is_open:
                dur = sixteenth * 2.5
                t = t_arr(dur)
                noise = bp(np.random.randn(len(t)), 5000, 15000)
                amp = np.exp(-t * 6)
                hat = noise * amp * 0.3
                pan = 0.3
            elif is_offbeat:
                dur = sixteenth * 0.6
                t = t_arr(dur)
                noise = hp(np.random.randn(len(t)), 7000)
                amp = np.exp(-t * 35)
                hat = noise * amp * 0.28
                pan = 0.15
            elif is_ghost and np.random.random() > 0.25:
                dur = sixteenth * 0.35
                t = t_arr(dur)
                noise = hp(np.random.randn(len(t)), 9000)
                amp = np.exp(-t * 55)
                hat = noise * amp * 0.12
                pan = -0.1 + np.random.random() * 0.5  # spread ghosts
            else:
                continue

            pos = int((bar * BAR + step * sixteenth) * SR)
            add_stereo(L, R, hat, pos, pan=pan)

    return L, R


# ============================================================
# PERCUSSION — Richer, more tribal, stereo spread
# ============================================================
def gen_perc():
    print("  [5/8] Percussion...")
    L = np.zeros(TOTAL_SAMPLES)
    R = np.zeros(TOTAL_SAMPLES)
    sixteenth = BEAT / 4

    for bar in range(TOTAL_BARS):
        if bar < 8:
            continue
        if in_section(bar, [(48, 64)]):
            continue

        # Layered clap on 2 and 4
        for beat in [1, 3]:
            t = t_arr(0.1)
            # Multiple noise bursts for realistic clap
            clap = np.zeros(len(t))
            for i in range(3):
                delay = int(i * SR * 0.005)
                burst = bp(np.random.randn(len(t)), 800, 5000) * np.exp(-t * 30)
                if delay < len(clap):
                    clap[delay:] += burst[:len(clap)-delay] * (0.8 ** i)
            clap *= 0.3
            pos = int((bar * BAR + beat * BEAT) * SR)
            add_stereo(L, R, clap, pos, pan=0.05)

        # Ride — triplet pattern, panned right
        if bar >= 16:
            for step in range(16):
                if step % 3 == 0:
                    t = t_arr(0.06)
                    ride = hp(np.random.randn(len(t)), 8000) * np.exp(-t * 40) * 0.1
                    pos = int((bar * BAR + step * sixteenth) * SR)
                    add_stereo(L, R, ride, pos, pan=0.4)

        # Tribal tom every 2 bars
        if bar % 2 == 1 and bar >= 16:
            for hit_pos in [3.5]:
                t = t_arr(0.15)
                freq = 100 + np.random.random() * 50
                tom = np.sin(2 * np.pi * freq * t * np.exp(-t * 5))
                tom *= np.exp(-t * 12) * 0.3
                tom = waveshape(tom, 1.5)
                pos = int((bar * BAR + hit_pos * BEAT) * SR)
                add_stereo(L, R, tom, pos, pan=-0.35)

        # Shaker — 16th pattern, wide stereo
        if bar >= 24 and not in_section(bar, [(40, 48)]):
            for step in range(16):
                if step % 2 == 0:
                    t = t_arr(sixteenth * 0.3)
                    shaker = bp(np.random.randn(len(t)), 6000, 14000) * np.exp(-t * 60) * 0.06
                    pos = int((bar * BAR + step * sixteenth) * SR)
                    add_stereo(L, R, shaker, pos, pan=-0.5 + (step % 4) * 0.33)

    return L, R


# ============================================================
# LEAD — Supersaw with presence, delay, the LIGHT
# ============================================================
def gen_lead():
    print("  [6/8] Lead melody (matices de luz)...")
    L = np.zeros(TOTAL_SAMPLES)
    R = np.zeros(TOTAL_SAMPLES)

    phrases = [
        [(64,0.5,0.8),(68,0.75,1.0),(69,0.25,0.7),(71,1.0,1.0),(68,0.5,0.8)],
        [(76,0.5,0.9),(72,0.5,0.8),(71,0.5,0.7),(68,1.5,1.0)],
        [(64,0.25,0.7),(65,0.25,0.6),(68,1.0,1.0),(72,0.5,0.9),(71,0.75,0.8)],
        [(80,1.0,0.6),(76,0.5,0.7),(72,1.0,0.9),(71,0.5,0.8),(68,1.0,1.0)],
        [(64,0.5,0.9),(62,0.5,0.8),(60,0.5,0.7),(64,0.5,0.8),(68,1.0,1.0),(72,1.0,0.9)],
        # New phrases for variation
        [(71,0.5,0.9),(72,0.5,1.0),(76,1.0,0.8),(72,0.5,0.7),(68,1.5,1.0)],
        [(68,0.25,0.8),(71,0.25,0.9),(72,0.5,1.0),(76,1.0,0.8),(80,0.5,0.7),(76,1.5,1.0)],
    ]

    # Lead in: drops and breakdowns
    melody_bars = list(range(16, 40)) + list(range(48, 64)) + list(range(72, 96))

    phrase_idx = 0
    for bar in melody_bars:
        if bar >= TOTAL_BARS:
            break
        phrase = phrases[phrase_idx % len(phrases)]
        t_offset = 0

        for note, dur, vel in phrase:
            freq = note_freq(note)
            note_dur = dur * BEAT
            t = t_arr(note_dur)
            n = len(t)

            # 5 detuned saws = supersaw
            detune = [0.993, 0.997, 1.0, 1.003, 1.007]
            saw_mix = np.zeros(n)
            for dt in detune:
                saw_mix += sawtooth(2 * np.pi * freq * dt * t)
            saw_mix /= len(detune)

            # Band-pass for presence in mids
            lead = bp(saw_mix, 400, min(freq * 8, SR/2-100))

            # Saturation
            lead = waveshape(lead * 1.3, 1.8)

            # Envelope
            amp = adsr(t, a=0.015, d=0.1, s=0.75, r=0.1, dur=note_dur)
            lead = lead * amp * vel * 0.35

            pos = int((bar * BAR + t_offset) * SR)

            # Lead slightly right to balance acid left
            add_stereo(L, R, lead, pos, pan=0.2)
            t_offset += note_dur

        phrase_idx += 1

    # Stereo ping-pong delay
    delay_time = int(BEAT * 0.75 * SR)  # dotted 8th
    for i in range(6):
        d = delay_time * (i + 1)
        decay = 0.35 ** (i + 1)
        if d < TOTAL_SAMPLES:
            p = 0.4 if i % 2 == 0 else -0.4  # ping pong
            if i % 2 == 0:
                L[d:] += R[:TOTAL_SAMPLES-d] * decay * 0.5
            else:
                R[d:] += L[:TOTAL_SAMPLES-d] * decay * 0.5

    return L * 0.55, R * 0.55


# ============================================================
# ATMOSPHERE — Wider, more movement, psychedelic
# ============================================================
def gen_atmo():
    print("  [7/8] Atmosphere pads...")
    L = np.zeros(TOTAL_SAMPLES)
    R = np.zeros(TOTAL_SAMPLES)

    chords = [
        [52, 56, 59],    # E-G#-B
        [53, 57, 60],    # F-A-C (dark)
        [57, 60, 64],    # A-C-E
        [50, 53, 57],    # D-F-A (warm)
        [56, 59, 62],    # G#-B-D (light!)
        [52, 56, 59],    # E-G#-B
        [48, 52, 56],    # C-E-G# (augmented = psychedelic)
        [52, 56, 59],    # resolve
    ]

    bars_per_chord = 4

    for chord_idx in range(TOTAL_BARS // bars_per_chord + 1):
        start_bar = chord_idx * bars_per_chord
        if start_bar >= TOTAL_BARS:
            break

        chord = chords[chord_idx % len(chords)]
        chord_dur = min(bars_per_chord * BAR, (TOTAL_BARS - start_bar) * BAR)
        t = t_arr(chord_dur)
        n = len(t)

        pad_L = np.zeros(n)
        pad_R = np.zeros(n)

        for i, note in enumerate(chord):
            freq = note_freq(note)
            # Detuned pair for width
            osc_L = np.sin(2 * np.pi * freq * 0.998 * t) * 0.4
            osc_R = np.sin(2 * np.pi * freq * 1.002 * t) * 0.4
            # Filtered saw for texture
            saw = sawtooth(2 * np.pi * freq * t) * 0.2
            saw_f = lp(saw, min(freq * 3, SR/2-100))

            # LFO per note (different rates for movement)
            lfo_rate = 0.1 + i * 0.07
            lfo = 0.6 + 0.4 * np.sin(2 * np.pi * lfo_rate * t + i * 1.5)

            pad_L += (osc_L + saw_f * 0.7) * lfo
            pad_R += (osc_R + saw_f * 0.7) * lfo

        pad_L /= len(chord)
        pad_R /= len(chord)

        # Long fade in/out
        fade = min(int(2.5 * SR), n // 3)
        pad_L[:fade] *= np.linspace(0, 1, fade)
        pad_L[-fade:] *= np.linspace(1, 0, fade)
        pad_R[:fade] *= np.linspace(0, 1, fade)
        pad_R[-fade:] *= np.linspace(1, 0, fade)

        pos = int(start_bar * BAR * SR)
        end = min(pos + n, TOTAL_SAMPLES)
        nn = end - pos
        L[pos:end] += pad_L[:nn]
        R[pos:end] += pad_R[:nn]

    return L * 0.35, R * 0.35


# ============================================================
# FX — Risers, impacts, noise sweeps
# ============================================================
def gen_fx():
    print("  [8/8] FX risers & impacts...")
    L = np.zeros(TOTAL_SAMPLES)
    R = np.zeros(TOTAL_SAMPLES)

    def make_riser(duration):
        t = t_arr(duration)
        n = len(t)
        noise = np.random.randn(n)
        riser = np.zeros(n)
        chunks = 64
        chunk_size = n // chunks
        for i in range(chunks):
            s = i * chunk_size
            e = min(s + chunk_size, n)
            cutoff = 100 + (14000 * (i / chunks) ** 2)
            cutoff = min(cutoff, SR/2-100)
            c = noise[s:e]
            if len(c) > 20:
                riser[s:e] = lp(c, cutoff)
        riser *= np.linspace(0, 1, n) ** 1.5
        return riser * 0.35

    def make_impact():
        t = t_arr(0.8)
        noise = lp(np.random.randn(len(t)), 3000) * 0.4
        sub = np.sin(2 * np.pi * 35 * t) * np.exp(-t * 4)
        amp = np.exp(-t * 5)
        return (noise + sub) * amp * 0.7

    def make_downlifter(duration):
        t = t_arr(duration)
        n = len(t)
        noise = np.random.randn(n)
        dl = np.zeros(n)
        chunks = 32
        chunk_size = n // chunks
        for i in range(chunks):
            s = i * chunk_size
            e = min(s + chunk_size, n)
            cutoff = 12000 - (11000 * (i / chunks))
            cutoff = max(min(cutoff, SR/2-100), 100)
            c = noise[s:e]
            if len(c) > 20:
                dl[s:e] = lp(c, cutoff)
        dl *= np.linspace(1, 0, n) ** 0.8
        return dl * 0.2

    # Risers before drops
    riser_points = [(12, 4), (66, 6), (94, 2)]
    for bar, dur_bars in riser_points:
        if bar >= TOTAL_BARS:
            continue
        riser = make_riser(dur_bars * BAR)
        pos = int(bar * BAR * SR)
        add_stereo(L, R, riser, pos, pan=0.0)
        # Stereo noise sweep
        riser_r = make_riser(dur_bars * BAR) * 0.5
        add_stereo(L, R, riser_r, pos, pan=0.6)

    # Impacts
    impact = make_impact()
    for drop_bar in [16, 72]:
        if drop_bar >= TOTAL_BARS:
            continue
        pos = int(drop_bar * BAR * SR)
        add_stereo(L, R, impact, pos, pan=0.0)

    # Downlifters into breakdowns
    for bar in [40, 96]:
        if bar >= TOTAL_BARS:
            continue
        dl = make_downlifter(2 * BAR)
        pos = int(bar * BAR * SR)
        add_stereo(L, R, dl, pos, pan=-0.3)

    return L, R


# ============================================================
# SYNTHESIS
# ============================================================
print()
print("Sintetizando...")

kick_L, kick_R = gen_kick()
bass_L, bass_R = gen_bass()
acid_L, acid_R = gen_acid()
hats_L, hats_R = gen_hats()
perc_L, perc_R = gen_perc()
lead_L, lead_R = gen_lead()
atmo_L, atmo_R = gen_atmo()
fx_L, fx_R = gen_fx()

print()
print("Mezclando...")

mix_L = np.zeros(TOTAL_SAMPLES)
mix_R = np.zeros(TOTAL_SAMPLES)

# Mix levels (calibrated against Glosolalia spectrum)
mix_L += kick_L * 0.95
mix_R += kick_R * 0.95
mix_L += bass_L * 0.90
mix_R += bass_R * 0.90
mix_L += acid_L * 0.65
mix_R += acid_R * 0.65
mix_L += hats_L * 0.55
mix_R += hats_R * 0.55
mix_L += perc_L * 0.50
mix_R += perc_R * 0.50
mix_L += lead_L * 0.60
mix_R += lead_R * 0.60
mix_L += atmo_L * 0.45
mix_R += atmo_R * 0.45
mix_L += fx_L * 0.55
mix_R += fx_R * 0.55

# Sidechain compression (duck on kick)
print("Sidechain...")
kick_mono = (kick_L + kick_R) / 2
kick_env = np.abs(kick_mono)
window = int(0.04 * SR)
kernel = np.ones(window) / window
kick_smooth = np.convolve(kick_env, kernel, mode='same')
kick_smooth /= (np.max(kick_smooth) + 1e-10)
sidechain = 1.0 - kick_smooth * 0.35

# Apply sidechain to everything except kick
non_kick_L = mix_L - kick_L * 0.95
non_kick_R = mix_R - kick_R * 0.95
mix_L = kick_L * 0.95 + non_kick_L * sidechain
mix_R = kick_R * 0.95 + non_kick_R * sidechain

# ============================================================
# MASTERING CHAIN
# ============================================================
print("Masterizando...")

# 1. EQ correction: cut sub below 30Hz, boost low-mids
mix_L = hp(mix_L, 30)
mix_R = hp(mix_R, 30)

# Boost 200-600Hz area (where Glosolalia has 17% vs our 6%)
mid_boost_L = bp(mix_L, 200, 600)
mid_boost_R = bp(mix_R, 200, 600)
mix_L += mid_boost_L * 0.3
mix_R += mid_boost_R * 0.3

# Boost presence 2k-6k
pres_boost_L = bp(mix_L, 2000, 6000)
pres_boost_R = bp(mix_R, 2000, 6000)
mix_L += pres_boost_L * 0.2
mix_R += pres_boost_R * 0.2

# 2. Multiband-ish compression (simple: soft clip per band)
mix_L = waveshape(mix_L, 1.5)
mix_R = waveshape(mix_R, 1.5)

# 3. Stereo limiter
print("Limitando...")
# Target: RMS around -9 dB (matching Glosolalia)
peak = max(np.max(np.abs(mix_L)), np.max(np.abs(mix_R)))
if peak > 0:
    mix_L /= peak
    mix_R /= peak

# Brick wall limiter
mix_L = np.clip(mix_L, -0.98, 0.98)
mix_R = np.clip(mix_R, -0.98, 0.98)

# Makeup gain to target loudness
current_rms = np.sqrt(np.mean(mix_L**2 + mix_R**2) / 2)
target_rms = 10 ** (-9.0 / 20)  # -9 dB
if current_rms > 0:
    gain = target_rms / current_rms
    gain = min(gain, 3.0)  # safety limit
    mix_L *= gain
    mix_R *= gain

# Final clip
mix_L = np.clip(mix_L, -0.98, 0.98)
mix_R = np.clip(mix_R, -0.98, 0.98)

# ============================================================
# SAVE
# ============================================================
print("Guardando...")

stereo = np.column_stack([
    (mix_L * 32767).astype(np.int16),
    (mix_R * 32767).astype(np.int16)
])

output_path = os.path.join(OUTPUT_DIR, "DarkPsy_v2_Glosolalia_Cal.wav")
wavfile.write(output_path, SR, stereo)

# Save stems
stems = [
    ("stem_v2_kick.wav", kick_L, kick_R),
    ("stem_v2_bass.wav", bass_L, bass_R),
    ("stem_v2_acid.wav", acid_L, acid_R),
    ("stem_v2_hats.wav", hats_L, hats_R),
    ("stem_v2_perc.wav", perc_L, perc_R),
    ("stem_v2_lead.wav", lead_L, lead_R),
    ("stem_v2_atmo.wav", atmo_L, atmo_R),
    ("stem_v2_fx.wav", fx_L, fx_R),
]
for name, sL, sR in stems:
    peak_s = max(np.max(np.abs(sL)), np.max(np.abs(sR)), 1e-10)
    s_out = np.column_stack([
        (sL / peak_s * 0.9 * 32767).astype(np.int16),
        (sR / peak_s * 0.9 * 32767).astype(np.int16)
    ])
    wavfile.write(os.path.join(OUTPUT_DIR, name), SR, s_out)

# Quick spectrum check
print()
print("--- Verificación de espectro ---")
mono_check = (mix_L + mix_R) / 2
fft_c = np.abs(np.fft.rfft(mono_check))
freqs_c = np.fft.rfftfreq(len(mono_check), 1/SR)
total_e = np.sum(fft_c**2)
bands_check = [
    ('Sub 20-60Hz', 20, 60),
    ('Bass 60-200Hz', 60, 200),
    ('Low-Mid 200-600Hz', 200, 600),
    ('Mid 600-2kHz', 600, 2000),
    ('Hi-Mid 2k-6kHz', 2000, 6000),
    ('Presence 6k-10k', 6000, 10000),
    ('Air 10k-20k', 10000, 20000),
]
for name, lo, hi in bands_check:
    mask = (freqs_c >= lo) & (freqs_c < hi)
    pct = np.sum(fft_c[mask]**2) / total_e * 100
    bar = '#' * int(pct / 2)
    print(f'  {name:20s}: {pct:5.1f}%  {bar}')

rms_check = np.sqrt(np.mean(mono_check**2))
print(f'  RMS: {20*np.log10(rms_check+1e-10):.1f} dB')

print()
print("=" * 60)
print(f" TRACK: {output_path}")
print(f" Duración: {TOTAL_TIME:.0f}s ({TOTAL_TIME/60:.1f} min) | STEREO")
print(f" + 8 stems stereo")
print("=" * 60)
