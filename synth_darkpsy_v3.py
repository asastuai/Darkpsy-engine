"""
DARK PSYTRANCE v3 — HUMANIZED
Groove extraído de Glosolalia, micro-timing, swing, mutación,
fills, probabilidad, dinámica orgánica.
"""

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt, sawtooth, square, find_peaks
import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
SR = 44100
BPM = 148
BEAT = 60.0 / BPM
BAR = BEAT * 4
SIXTEENTH = BEAT / 4
TOTAL_BARS = 160  # ~7 min
TOTAL_TIME = TOTAL_BARS * BAR
TOTAL_SAMPLES = int(TOTAL_TIME * SR)

print("=" * 60)
print(" DARK PSYTRANCE v3 — HUMANIZED")
print(f" BPM: {BPM} | Bars: {TOTAL_BARS} | Duration: {TOTAL_TIME/60:.1f} min")
print("=" * 60)


# ============================================================
# STEP 0: Extract groove from Glosolalia
# ============================================================
print()
print("Extrayendo groove de Glosolalia...")

def extract_groove(filepath):
    """Extract micro-timing deviations from a reference track's kick pattern"""
    try:
        sr_ref, data = wavfile.read(filepath)
        if len(data.shape) > 1:
            mono = data.mean(axis=1).astype(np.float64)
        else:
            mono = data.astype(np.float64)
        mono /= (np.max(np.abs(mono)) + 1e-10)

        # Low-pass to isolate kick
        sos = butter(4, 100, btype='low', fs=sr_ref, output='sos')
        bass = np.abs(sosfilt(sos, mono))

        # Find peaks (kick hits)
        beat_samples = int(60.0 / BPM * sr_ref)
        peaks, props = find_peaks(bass, distance=int(beat_samples * 0.7),
                                   height=np.max(bass) * 0.15)

        if len(peaks) < 8:
            return None, None

        # Calculate expected positions (perfect grid)
        first_peak = peaks[0]
        expected = np.array([first_peak + i * beat_samples for i in range(len(peaks))])

        # Micro-timing deviations (in seconds)
        deviations = (peaks[:len(expected)] - expected[:len(peaks)]) / sr_ref

        # Also extract velocity pattern from peak heights
        velocities = props['peak_heights'][:len(peaks)]
        velocities /= np.max(velocities)

        print(f"  Encontré {len(peaks)} kicks")
        print(f"  Desvío promedio: {np.mean(np.abs(deviations))*1000:.1f}ms")
        print(f"  Desvío máximo: {np.max(np.abs(deviations))*1000:.1f}ms")
        print(f"  Rango de velocidad: {np.min(velocities):.2f} - {np.max(velocities):.2f}")

        return deviations, velocities

    except Exception as e:
        print(f"  Error: {e}")
        return None, None

# Try extracting from Glosolalia tracks
ref_files = [
    "C:/Users/Juan/Desktop/Musica/Glosolalia - Blueprints.wav",
    "C:/Users/Juan/Desktop/Musica/Glosolalia - Strange Chaotic Attractor.wav",
]

groove_devs = None
groove_vels = None
for ref in ref_files:
    groove_devs, groove_vels = extract_groove(ref)
    if groove_devs is not None and len(groove_devs) > 20:
        print(f"  Groove extraído de: {os.path.basename(ref)}")
        break

if groove_devs is None:
    print("  No se pudo extraer groove, usando modelo sintético")
    groove_devs = np.random.normal(0, 0.006, 500)  # ~6ms std dev
    groove_vels = np.ones(500)


# ============================================================
# HUMANIZATION ENGINE
# ============================================================
class HumanGroove:
    """Applies human-like timing and dynamics"""

    def __init__(self, groove_deviations, groove_velocities):
        self.devs = groove_deviations
        self.vels = groove_velocities
        self.swing_amount = 0.02  # 20ms swing on offbeats
        self.rng = np.random.RandomState(42)
        self._counter = 0

    def get_timing_offset(self, bar, beat, sixteenth=0):
        """Get micro-timing offset in seconds, based on real groove"""
        # Use groove data cyclically
        idx = self._counter % len(self.devs)
        self._counter += 1
        base_dev = self.devs[idx]

        # Add swing: offbeat 16ths pushed slightly late
        swing = 0
        if sixteenth % 2 == 1:
            swing = self.swing_amount * (0.7 + self.rng.random() * 0.6)

        # Slight rush before drops (human excitement)
        rush = 0
        if bar % 16 == 15:  # bar before a section change
            rush = -0.003 * (beat / 4)  # progressively earlier

        # Random human jitter
        jitter = self.rng.normal(0, 0.004)  # 4ms std dev

        total = base_dev * 0.5 + swing + rush + jitter
        return np.clip(total, -0.025, 0.025)  # max 25ms

    def get_velocity(self, bar, beat, sixteenth=0, base_vel=0.8):
        """Organic velocity with musical intent"""
        idx = self._counter % len(self.vels)

        # Base from groove
        groove_v = self.vels[idx % len(self.vels)]

        # Musical accents: beat 1 slightly stronger
        accent = 1.0
        if beat == 0:
            accent = 1.05
        elif beat == 2:
            accent = 1.02

        # Gradual intensity build within 4-bar phrases
        phrase_pos = (bar % 4) / 4
        phrase_curve = 0.92 + 0.08 * phrase_pos

        # 8-bar arc: builds to bar 7 then resets
        arc_pos = (bar % 8) / 8
        arc_curve = 0.9 + 0.15 * np.sin(arc_pos * np.pi)

        # Random organic variation
        human_var = self.rng.normal(0, 0.05)

        vel = base_vel * groove_v * accent * phrase_curve * arc_curve + human_var
        return np.clip(vel, 0.3, 1.0)

    def should_play(self, probability=0.95):
        """Probabilistic triggering — not every note plays"""
        return self.rng.random() < probability

    def get_fill_pattern(self, fill_type='buildup'):
        """Generate drum fill patterns"""
        if fill_type == 'buildup':
            # Accelerating hits
            return [(0, 0.9), (0.5, 0.85), (0.75, 0.9), (0.875, 0.95),
                    (0.9375, 1.0), (0.96875, 1.0)]
        elif fill_type == 'break':
            # Syncopated break
            return [(0, 1.0), (0.375, 0.8), (0.625, 0.9), (0.875, 1.0)]
        elif fill_type == 'tribal':
            # Triplet fill
            return [(i/6, 0.7 + 0.3*(i/6)) for i in range(6)]
        elif fill_type == 'stutter':
            # Machine gun
            return [(i/8, 0.6 + 0.4*(i/8)) for i in range(8)]


groove = HumanGroove(groove_devs, groove_vels)


# ============================================================
# DSP UTILS
# ============================================================
def t_arr(duration):
    return np.linspace(0, duration, int(duration * SR), endpoint=False)

def lp(sig, cutoff, order=4):
    cutoff = min(max(cutoff, 20), SR/2-100)
    return sosfilt(butter(order, cutoff, btype='low', fs=SR, output='sos'), sig)

def hp(sig, cutoff, order=2):
    cutoff = min(max(cutoff, 20), SR/2-100)
    return sosfilt(butter(order, cutoff, btype='high', fs=SR, output='sos'), sig)

def bp(sig, lo, hi, order=2):
    lo, hi = max(lo, 20), min(hi, SR/2-100)
    if lo >= hi: return sig
    return sosfilt(butter(order, [lo, hi], btype='band', fs=SR, output='sos'), sig)

def note_freq(note):
    return 440.0 * (2.0 ** ((note - 69) / 12.0))

def adsr(t, a=0.01, d=0.1, s=0.7, r=0.2, dur=None):
    if dur is None: dur = t[-1] if len(t) > 0 else 1.0
    env = np.zeros_like(t)
    for i, ti in enumerate(t):
        if ti < a: env[i] = ti / a if a > 0 else 1.0
        elif ti < a+d: env[i] = 1.0 - (1.0-s)*(ti-a)/d
        elif ti < dur-r: env[i] = s
        else: env[i] = s * max(0, (dur-ti)/r) if r > 0 else 0
    return env

def soft_clip(sig, thresh=0.8):
    return np.tanh(sig / thresh) * thresh

def waveshape(sig, amount=2.0):
    return np.tanh(sig * amount) / np.tanh(amount)

def pan_stereo(mono, pan=0.0):
    l = np.cos((pan+1)/2 * np.pi/2)
    r = np.sin((pan+1)/2 * np.pi/2)
    return mono * l, mono * r

def add_stereo(oL, oR, mono, pos, pan=0.0):
    L, R = pan_stereo(mono, pan)
    end = min(pos + len(L), len(oL))
    n = end - pos
    if n > 0 and pos >= 0:
        oL[pos:end] += L[:n]
        oR[pos:end] += R[:n]

def in_section(bar, sections):
    for s, e in sections:
        if s <= bar < e: return True
    return False

rng = np.random.RandomState(42)


# ============================================================
# STRUCTURE MAP (160 bars ≈ 7 min)
# ============================================================
# 0-7:     INTRO (minimal, building atmosphere)
# 8-15:    BUILD (elements entering one by one)
# 16-47:   DROP 1 (full energy, 32 bars)
# 48-55:   TRANSITION (stripping down)
# 56-71:   BREAKDOWN (pads + ethereal lead, matices de luz)
# 72-79:   BUILD 2 (riser, energy returning)
# 80-127:  DROP 2 (48 bars, climax, most variation)
# 128-143: TRANSITION + BREAKDOWN 2
# 144-159: OUTRO

SECTION_DROPS = [(16, 48), (80, 128)]
SECTION_BREAKDOWNS = [(56, 72), (128, 144)]
SECTION_BUILDS = [(8, 16), (72, 80)]
SECTION_INTROS = [(0, 8), (144, 160)]


# ============================================================
# KICK — Humanized, with fills and variation
# ============================================================
def gen_kick():
    print("  [1/8] Kick (humanized)...")
    L = np.zeros(TOTAL_SAMPLES)
    R = np.zeros(TOTAL_SAMPLES)

    def make_kick(vel=0.85, character='normal'):
        t = t_arr(0.22)
        if character == 'hard':
            pitch = 52 + 200 * np.exp(-t * 55)
            click_amt = 0.6
        elif character == 'soft':
            pitch = 48 + 120 * np.exp(-t * 40)
            click_amt = 0.2
        else:
            pitch = 50 + 160 * np.exp(-t * 48)
            click_amt = 0.4

        phase = 2 * np.pi * np.cumsum(pitch) / SR
        body = np.sin(phase)
        amp = np.exp(-t * 14)
        click = bp(rng.randn(len(t)), 2500, 7000) * np.exp(-t * 150) * click_amt
        kick = hp(body * amp + click, 32)
        kick = waveshape(kick * 1.2 * vel, 2.5)
        return kick * 0.85

    for bar in range(TOTAL_BARS):
        # Breakdowns: no kick
        if in_section(bar, SECTION_BREAKDOWNS):
            continue

        # Check if this is a fill bar (last bar before section change)
        is_fill_bar = (bar in [15, 47, 55, 79, 127, 143])

        if is_fill_bar:
            # DRUM FILL!
            fill_types = ['buildup', 'tribal', 'stutter', 'break']
            fill = groove.get_fill_pattern(fill_types[bar % len(fill_types)])
            for beat_pos, fill_vel in fill:
                timing = groove.get_timing_offset(bar, 0)
                pos = int((bar * BAR + beat_pos * BAR + timing) * SR)
                character = 'hard' if fill_vel > 0.9 else 'normal'
                kick = make_kick(vel=fill_vel, character=character)
                add_stereo(L, R, kick, pos, pan=rng.uniform(-0.05, 0.05))
            continue

        # Intro/outro: half-time or sparse
        if in_section(bar, SECTION_INTROS):
            beats = [0, 2] if bar < 4 else [0, 1, 2, 3]
        else:
            beats = [0, 1, 2, 3]

        for beat in beats:
            # Probabilistic skip (very rare, ~3%)
            if not groove.should_play(0.97) and beat != 0:
                continue

            vel = groove.get_velocity(bar, beat, base_vel=0.85)
            timing = groove.get_timing_offset(bar, beat)

            # Vary kick character
            if vel > 0.9:
                character = 'hard'
            elif vel < 0.7:
                character = 'soft'
            else:
                character = 'normal'

            kick = make_kick(vel=vel, character=character)
            pos = int((bar * BAR + beat * BEAT + timing) * SR)
            pos = max(0, pos)
            # Tiny stereo variation (like a mic'd drum)
            add_stereo(L, R, kick, pos, pan=rng.uniform(-0.03, 0.03))

    return L, R


# ============================================================
# ROLLING BASS — Evolving, never exactly repeating
# ============================================================
def gen_bass():
    print("  [2/8] Rolling bass (mutating)...")
    L = np.zeros(TOTAL_SAMPLES)
    R = np.zeros(TOTAL_SAMPLES)
    root = 40  # E2

    # Base motifs that MUTATE over time
    base_motifs = [
        [0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,0],
        [0,0,4,0, 0,0,4,0, 0,0,0,0, 0,0,4,0],
        [0,0,1,0, 0,0,1,0, 0,0,0,0, 0,1,0,0],
        [0,0,4,5, 0,0,4,0, 0,0,0,7, 0,0,4,0],
        [0,0,7,4, 0,0,1,0, 0,4,0,0, 0,0,7,5],
        [0,0,0,4, 0,7,0,4, 0,0,5,0, 7,0,4,0],
    ]

    def mutate_pattern(pattern, amount=0.15):
        """Randomly alter some notes in the pattern"""
        p = list(pattern)
        for i in range(len(p)):
            if rng.random() < amount and i > 0:
                # Replace with a scale-valid interval
                options = [0, 1, 4, 5, 7]
                p[i] = options[rng.randint(len(options))]
        return p

    current_pattern = list(base_motifs[0])

    for bar in range(TOTAL_BARS):
        if in_section(bar, SECTION_BREAKDOWNS):
            continue
        if bar < 2:
            continue

        # Pattern evolution: mutate every 4 bars, bigger changes at sections
        if bar % 4 == 0:
            base_idx = (bar // 8) % len(base_motifs)
            mutation_rate = 0.1 if in_section(bar, SECTION_DROPS) else 0.05
            current_pattern = mutate_pattern(base_motifs[base_idx], mutation_rate)

        # Occasional bar where pattern is totally different (surprise)
        if bar % 16 == 13 and in_section(bar, SECTION_DROPS):
            current_pattern = mutate_pattern(base_motifs[rng.randint(len(base_motifs))], 0.3)

        for step in range(16):
            note = root + current_pattern[step]
            freq = note_freq(note)

            # Humanized timing
            timing = groove.get_timing_offset(bar, step // 4, step % 4)
            vel = groove.get_velocity(bar, step // 4, step, base_vel=0.8)

            # Probabilistic ghost notes
            if step % 4 != 0 and not groove.should_play(0.92):
                continue

            dur = SIXTEENTH * (0.82 + rng.random() * 0.12)  # variable note length
            t = t_arr(dur)
            n = len(t)

            # Oscillators with slight random detune per note
            detune = 1.0 + rng.uniform(-0.003, 0.003)
            saw = sawtooth(2 * np.pi * freq * detune * t)
            sq = square(2 * np.pi * freq * t, duty=0.25 + rng.random()*0.15) * 0.4
            sub = np.sin(2 * np.pi * freq * 0.5 * t) * 0.5
            raw = saw * 0.5 + sq * 0.3 + sub * 0.2

            # Filter with humanized cutoff
            accent = 1.0 if step % 4 == 0 else (0.6 + rng.random() * 0.3)
            cutoff = 500 + 3000 * accent * vel
            raw = lp(raw, cutoff)

            # Saturation (varies per note)
            sat_amt = 2.0 + rng.random() * 1.5
            raw = waveshape(raw * 1.8, sat_amt)

            # Amp envelope with human variation
            amp = np.ones(n)
            attack = int(rng.uniform(15, 45))
            attack = min(attack, n)
            amp[:attack] = np.linspace(0, 1, attack)
            decay_point = int(n * (0.65 + rng.random() * 0.15))
            if decay_point < n:
                amp[decay_point:] = np.linspace(1, 0.15, n - decay_point)

            bass_note = raw * amp * vel * 0.7

            pos = int((bar * BAR + step * SIXTEENTH + timing) * SR)
            pos = max(0, pos)
            p = np.sin(step * 0.3 + bar * 0.1) * 0.12
            add_stereo(L, R, bass_note, pos, pan=p)

    return L, R


# ============================================================
# ACID — Wilder, more expressive
# ============================================================
def gen_acid():
    print("  [3/8] Acid line (expressive)...")
    L = np.zeros(TOTAL_SAMPLES)
    R = np.zeros(TOTAL_SAMPLES)

    # More sequences + mutation
    base_seqs = [
        [(52,2,1),(53,1,0),(56,3,1),(52,1,0),(50,2,1),(48,1,0),(52,2,1),(41,1,0)],
        [(52,1,1),(56,1,0),(59,1,1),(60,2,1),(57,1,0),(53,2,1),(52,1,0),(50,1,0)],
        [(64,1,1),(62,1,0),(60,2,1),(56,1,0),(52,2,1),(53,1,0),(56,2,1)],
        [(56,2,1),(59,1,0),(62,1,1),(60,2,0),(57,2,1),(53,1,0),(52,3,1)],
        [(48,1,1),(50,2,0),(52,1,1),(56,1,0),(59,2,1),(56,1,0),(52,2,1)],
        [(64,1,1),(68,1,0),(65,2,1),(62,1,0),(60,1,1),(57,2,0),(53,1,1)],
    ]

    def mutate_seq(seq):
        """Mutate acid sequence"""
        s = list(seq)
        for i in range(len(s)):
            note, dur, acc = s[i]
            if rng.random() < 0.15:
                # Transpose note within scale
                offsets = [-2, -1, 0, 1, 2, 3, 4, 5]
                note = note + offsets[rng.randint(len(offsets))]
                note = max(41, min(76, note))
            if rng.random() < 0.1:
                dur = max(1, dur + rng.choice([-1, 1]))
            if rng.random() < 0.2:
                acc = 1 - acc
            s[i] = (note, dur, acc)
        return s

    for bar in range(TOTAL_BARS):
        if bar < 10: continue
        if in_section(bar, SECTION_BREAKDOWNS + [(144, 160)]): continue

        # Select and mutate sequence
        base = base_seqs[bar % len(base_seqs)]
        seq = mutate_seq(base) if bar % 2 == 0 else base

        t_offset = 0
        for note, dur, accent in seq:
            freq = note_freq(note)
            timing = groove.get_timing_offset(bar, 0)
            vel = groove.get_velocity(bar, 0, base_vel=0.7)

            note_dur = dur * SIXTEENTH * (0.88 + rng.random() * 0.1)
            t = t_arr(note_dur)
            n = len(t)

            saw1 = sawtooth(2 * np.pi * freq * t)
            saw2 = sawtooth(2 * np.pi * freq * (1.005 + rng.random()*0.005) * t)
            raw = (saw1 + saw2 * 0.5) / 1.5

            # Resonant filter with human variation
            cutoff = 400 + (2500 + rng.random()*1500) * accent
            raw = lp(raw, cutoff)

            env_f = np.exp(-t * (6 + rng.random()*8 if accent else 12 + rng.random()*6))
            raw = raw * (0.25 + 0.75 * env_f)
            raw = waveshape(raw * (1.5 + rng.random()*0.8), 2.0 + rng.random())

            amp = adsr(t, a=0.002+rng.random()*0.005, d=0.04, s=0.6, r=0.03, dur=note_dur)
            acid = raw * amp * vel * (0.55 if accent else 0.35)

            pos = int((bar * BAR + t_offset + timing) * SR)
            pos = max(0, pos)
            pan = -0.25 + rng.uniform(-0.1, 0.1)
            add_stereo(L, R, acid, pos, pan=pan)
            t_offset += dur * SIXTEENTH

    return L, R


# ============================================================
# HI-HATS — Groove-locked, probabilistic
# ============================================================
def gen_hats():
    print("  [4/8] Hi-hats (groovy)...")
    L = np.zeros(TOTAL_SAMPLES)
    R = np.zeros(TOTAL_SAMPLES)

    for bar in range(TOTAL_BARS):
        if bar < 4: continue
        if in_section(bar, SECTION_BREAKDOWNS[:1]): continue

        for step in range(16):
            is_offbeat = step % 4 == 2
            is_ghost = step % 2 == 1
            is_open = step == 12 and bar % 4 == 3

            timing = groove.get_timing_offset(bar, step//4, step)
            vel = groove.get_velocity(bar, step//4, step, base_vel=0.6)

            if is_open and groove.should_play(0.8):
                dur = SIXTEENTH * (2.0 + rng.random() * 1.0)
                t = t_arr(dur)
                noise = bp(rng.randn(len(t)), 4500+rng.random()*2000, 14000+rng.random()*2000)
                amp = np.exp(-t * (5 + rng.random()*4))
                hat = noise * amp * vel * 0.3
                pan = 0.25 + rng.uniform(-0.15, 0.15)
            elif is_offbeat and groove.should_play(0.93):
                dur = SIXTEENTH * (0.5 + rng.random()*0.2)
                t = t_arr(dur)
                noise = hp(rng.randn(len(t)), 6500 + rng.random()*2000)
                amp = np.exp(-t * (28 + rng.random()*15))
                hat = noise * amp * vel * 0.28
                pan = 0.12 + rng.uniform(-0.1, 0.1)
            elif is_ghost and groove.should_play(0.55):
                dur = SIXTEENTH * (0.25 + rng.random()*0.2)
                t = t_arr(dur)
                noise = hp(rng.randn(len(t)), 8000 + rng.random()*2000)
                amp = np.exp(-t * (40 + rng.random()*25))
                hat = noise * amp * vel * 0.10
                pan = rng.uniform(-0.5, 0.5)
            else:
                continue

            pos = int((bar * BAR + step * SIXTEENTH + timing) * SR)
            pos = max(0, pos)
            add_stereo(L, R, hat, pos, pan=pan)

    return L, R


# ============================================================
# PERCUSSION — Tribal, organic, evolving
# ============================================================
def gen_perc():
    print("  [5/8] Percussion (tribal)...")
    L = np.zeros(TOTAL_SAMPLES)
    R = np.zeros(TOTAL_SAMPLES)

    for bar in range(TOTAL_BARS):
        if bar < 8: continue
        if in_section(bar, SECTION_BREAKDOWNS): continue

        # Clap on 2 and 4 with humanization
        for beat in [1, 3]:
            if not groove.should_play(0.95): continue
            timing = groove.get_timing_offset(bar, beat)
            vel = groove.get_velocity(bar, beat, base_vel=0.7)

            t = t_arr(0.09 + rng.random()*0.03)
            clap = np.zeros(len(t))
            n_layers = rng.randint(2, 5)
            for i in range(n_layers):
                delay = int(i * SR * rng.uniform(0.003, 0.008))
                burst = bp(rng.randn(len(t)), 700+rng.random()*400, 4500+rng.random()*1000)
                burst *= np.exp(-t * (25 + rng.random()*15))
                if delay < len(clap):
                    clap[delay:] += burst[:len(clap)-delay] * (0.75 ** i)
            clap *= vel * 0.3

            pos = int((bar * BAR + beat * BEAT + timing) * SR)
            pos = max(0, pos)
            add_stereo(L, R, clap, pos, pan=rng.uniform(-0.08, 0.08))

        # Ride — not every bar, probability based
        if bar >= 16 and groove.should_play(0.7):
            for step in range(16):
                if step % 3 == 0 and groove.should_play(0.75):
                    t = t_arr(0.04 + rng.random()*0.03)
                    ride = hp(rng.randn(len(t)), 7000+rng.random()*3000)
                    ride *= np.exp(-t * (35+rng.random()*15))
                    vel_r = groove.get_velocity(bar, step//4, step, base_vel=0.3)
                    ride *= vel_r * 0.12

                    timing_r = groove.get_timing_offset(bar, step//4, step)
                    pos = int((bar * BAR + step * SIXTEENTH + timing_r) * SR)
                    pos = max(0, pos)
                    add_stereo(L, R, ride, pos, pan=0.35+rng.uniform(-0.1,0.1))

        # Tribal elements — more varied and organic
        if bar % 2 == 1 and bar >= 16 and groove.should_play(0.6):
            # Random tribal hit position
            hit_beat = rng.uniform(2.5, 3.8)
            t = t_arr(0.12 + rng.random()*0.08)
            freq = 80 + rng.random() * 80
            tom = np.sin(2 * np.pi * freq * t * np.exp(-t * (4+rng.random()*3)))
            tom *= np.exp(-t * (10+rng.random()*5)) * 0.3
            tom = waveshape(tom, 1.3 + rng.random()*0.5)

            pos = int((bar * BAR + hit_beat * BEAT) * SR)
            pos = max(0, pos)
            add_stereo(L, R, tom, pos, pan=-0.3+rng.uniform(-0.15,0.15))

        # Shaker — organic timing
        if bar >= 24 and in_section(bar, SECTION_DROPS) and groove.should_play(0.8):
            for step in range(16):
                if step % 2 == 0 and groove.should_play(0.65):
                    t = t_arr(SIXTEENTH * (0.2 + rng.random()*0.15))
                    shaker = bp(rng.randn(len(t)), 5000+rng.random()*2000, 13000+rng.random()*2000)
                    shaker *= np.exp(-t * (50+rng.random()*20)) * 0.055
                    timing_s = groove.get_timing_offset(bar, step//4, step)
                    pos = int((bar * BAR + step * SIXTEENTH + timing_s) * SR)
                    pos = max(0, pos)
                    add_stereo(L, R, shaker, pos, pan=-0.45+rng.uniform(0, 0.9))

    return L, R


# ============================================================
# LEAD — Melodic variation, breathing
# ============================================================
def gen_lead():
    print("  [6/8] Lead (breathing, expressive)...")
    L = np.zeros(TOTAL_SAMPLES)
    R = np.zeros(TOTAL_SAMPLES)

    phrases = [
        [(64,0.5,0.8),(68,0.75,1.0),(69,0.25,0.7),(71,1.0,1.0),(68,0.5,0.8)],
        [(76,0.5,0.9),(72,0.5,0.8),(71,0.5,0.7),(68,1.5,1.0)],
        [(64,0.25,0.7),(65,0.25,0.6),(68,1.0,1.0),(72,0.5,0.9),(71,0.75,0.8)],
        [(80,1.0,0.6),(76,0.5,0.7),(72,1.0,0.9),(71,0.5,0.8),(68,1.0,1.0)],
        [(64,0.5,0.9),(62,0.5,0.8),(60,0.5,0.7),(64,0.5,0.8),(68,1.0,1.0),(72,1.0,0.9)],
        [(71,0.5,0.9),(72,0.5,1.0),(76,1.0,0.8),(72,0.5,0.7),(68,1.5,1.0)],
        [(68,0.25,0.8),(71,0.25,0.9),(72,0.5,1.0),(76,1.0,0.8),(80,0.5,0.7),(76,1.5,1.0)],
    ]

    def mutate_phrase(phrase):
        p = list(phrase)
        for i in range(len(p)):
            note, dur, vel = p[i]
            if rng.random() < 0.2:
                note += rng.choice([-2,-1,0,1,2,3])
                note = max(56, min(84, note))
            if rng.random() < 0.15:
                dur *= (0.75 + rng.random() * 0.5)
            if rng.random() < 0.2:
                vel *= (0.8 + rng.random() * 0.4)
            p[i] = (note, dur, np.clip(vel, 0.3, 1.0))
        return p

    melody_bars = list(range(16, 48)) + list(range(56, 72)) + list(range(80, 128))
    phrase_idx = 0

    for bar in melody_bars:
        if bar >= TOTAL_BARS: break

        # Sometimes skip a bar (breathing room)
        if rng.random() < 0.12: continue

        base_phrase = phrases[phrase_idx % len(phrases)]
        phrase = mutate_phrase(base_phrase) if rng.random() > 0.3 else base_phrase
        t_offset = 0

        for note, dur, vel_base in phrase:
            freq = note_freq(note)
            vel = vel_base * groove.get_velocity(bar, 0, base_vel=0.9)
            timing = groove.get_timing_offset(bar, 0)

            note_dur = dur * BEAT * (0.9 + rng.random()*0.15)
            t = t_arr(note_dur)
            n = len(t)

            # Supersaw with random detune spread
            spread = 0.004 + rng.random() * 0.006
            detunes = [1-spread*2, 1-spread, 1.0, 1+spread, 1+spread*2]
            saw_mix = np.zeros(n)
            for dt in detunes:
                saw_mix += sawtooth(2 * np.pi * freq * dt * t)
            saw_mix /= len(detunes)

            lead = bp(saw_mix, 350, min(freq * 7, SR/2-100))
            lead = waveshape(lead * 1.2, 1.6 + rng.random()*0.5)

            # Expressive envelope with vibrato
            amp = adsr(t, a=0.01+rng.random()*0.02, d=0.08, s=0.7, r=0.12, dur=note_dur)
            # Vibrato kicks in after attack
            vib_depth = 0.003 + rng.random() * 0.005
            vib_rate = 4.5 + rng.random() * 2
            vib_onset = np.clip((t - 0.1) * 3, 0, 1)  # vibrato fades in
            vibrato = 1.0 + vib_depth * np.sin(2*np.pi*vib_rate*t) * vib_onset

            lead = lead * amp * vel * 0.35

            pos = int((bar * BAR + t_offset + timing) * SR)
            pos = max(0, pos)
            add_stereo(L, R, lead, pos, pan=0.18+rng.uniform(-0.08,0.08))
            t_offset += dur * BEAT

        phrase_idx += 1

    # Ping-pong delay
    delay_time = int(BEAT * 0.75 * SR)
    for i in range(6):
        d = delay_time * (i+1)
        decay = 0.3 ** (i+1)
        if d < TOTAL_SAMPLES:
            if i % 2 == 0:
                L[d:] += R[:TOTAL_SAMPLES-d] * decay * 0.4
            else:
                R[d:] += L[:TOTAL_SAMPLES-d] * decay * 0.4

    return L * 0.5, R * 0.5


# ============================================================
# ATMOSPHERE — Evolving, wider
# ============================================================
def gen_atmo():
    print("  [7/8] Atmosphere (evolving)...")
    L = np.zeros(TOTAL_SAMPLES)
    R = np.zeros(TOTAL_SAMPLES)

    chords = [
        [52,56,59],[53,57,60],[57,60,64],[50,53,57],
        [56,59,62],[52,56,59],[48,52,56],[52,56,59],
    ]

    bars_per_chord = 4
    for ci in range(TOTAL_BARS // bars_per_chord + 1):
        sb = ci * bars_per_chord
        if sb >= TOTAL_BARS: break

        chord = chords[ci % len(chords)]
        # Occasionally add an extension note (9th, 11th)
        if rng.random() < 0.3:
            ext = chord[0] + rng.choice([14, 17, 19])
            chord = chord + [ext]

        dur = min(bars_per_chord * BAR, (TOTAL_BARS - sb) * BAR)
        t = t_arr(dur)
        n = len(t)

        pad_L = np.zeros(n)
        pad_R = np.zeros(n)

        for i, note in enumerate(chord):
            freq = note_freq(note)
            # Detuned stereo pair
            det = 0.002 + rng.random() * 0.004
            osc_L = np.sin(2*np.pi*freq*(1-det)*t) * 0.35
            osc_R = np.sin(2*np.pi*freq*(1+det)*t) * 0.35
            saw = sawtooth(2*np.pi*freq*t) * 0.18
            saw_f = lp(saw, min(freq*2.5, SR/2-100))

            lfo_rate = 0.08 + i*0.05 + rng.random()*0.04
            lfo_phase = rng.random() * 2 * np.pi
            lfo = 0.55 + 0.45 * np.sin(2*np.pi*lfo_rate*t + lfo_phase)

            pad_L += (osc_L + saw_f*0.6) * lfo
            pad_R += (osc_R + saw_f*0.6) * lfo

        pad_L /= len(chord)
        pad_R /= len(chord)

        fade = min(int(3.0*SR), n//3)
        pad_L[:fade] *= np.linspace(0,1,fade)
        pad_L[-fade:] *= np.linspace(1,0,fade)
        pad_R[:fade] *= np.linspace(0,1,fade)
        pad_R[-fade:] *= np.linspace(1,0,fade)

        pos = int(sb * BAR * SR)
        end = min(pos+n, TOTAL_SAMPLES)
        nn = end-pos
        L[pos:end] += pad_L[:nn]
        R[pos:end] += pad_R[:nn]

    return L * 0.38, R * 0.38


# ============================================================
# FX — More varied, textural
# ============================================================
def gen_fx():
    print("  [8/8] FX & textures...")
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
            s,e = i*cs, min((i+1)*cs, n)
            cutoff = 80 + (15000*(i/chunks)**2.2)
            cutoff = min(cutoff, SR/2-100)
            c = noise[s:e]
            if len(c) > 20:
                riser[s:e] = lp(c, cutoff)
        riser *= np.linspace(0,1,n)**1.8
        return riser * 0.35

    def make_impact():
        t = t_arr(1.0)
        noise = lp(rng.randn(len(t)), 2500) * 0.35
        sub = np.sin(2*np.pi*32*t) * np.exp(-t*3.5)
        amp = np.exp(-t*4)
        return (noise + sub * 0.8) * amp * 0.7

    def make_texture(duration):
        """Granular-ish texture"""
        t = t_arr(duration)
        n = len(t)
        tex = np.zeros(n)
        n_grains = int(duration * 8)
        for _ in range(n_grains):
            pos_g = rng.randint(0, max(1, n-SR//4))
            grain_len = int(SR * rng.uniform(0.05, 0.3))
            grain_len = min(grain_len, n - pos_g)
            if grain_len < 100: continue
            tg = t_arr(grain_len/SR)
            freq = rng.uniform(200, 2000)
            grain = np.sin(2*np.pi*freq*tg) * rng.randn(len(tg)) * 0.1
            window = np.hanning(len(tg))
            tex[pos_g:pos_g+len(tg)] += grain * window
        return tex * 0.15

    # Risers
    for bar, dur_bars in [(12,4),(70,8),(126,2)]:
        if bar >= TOTAL_BARS: continue
        riser = make_riser(dur_bars*BAR)
        pos = int(bar*BAR*SR)
        add_stereo(L, R, riser, pos, pan=0.0)
        riser2 = make_riser(dur_bars*BAR) * 0.4
        add_stereo(L, R, riser2, pos, pan=0.5)

    # Impacts
    impact = make_impact()
    for db in [16, 80]:
        if db >= TOTAL_BARS: continue
        pos = int(db*BAR*SR)
        add_stereo(L, R, impact, pos, pan=0.0)

    # Textures in breakdowns
    for sb, eb in SECTION_BREAKDOWNS:
        if sb >= TOTAL_BARS: continue
        dur = (min(eb, TOTAL_BARS) - sb) * BAR
        tex = make_texture(dur)
        pos = int(sb*BAR*SR)
        add_stereo(L, R, tex, pos, pan=-0.4)
        tex2 = make_texture(dur)
        add_stereo(L, R, tex2, pos, pan=0.4)

    return L, R


# ============================================================
# SYNTHESIS + MIX + MASTER
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

mix_L += kick_L * 0.92;   mix_R += kick_R * 0.92
mix_L += bass_L * 0.88;   mix_R += bass_R * 0.88
mix_L += acid_L * 0.62;   mix_R += acid_R * 0.62
mix_L += hats_L * 0.52;   mix_R += hats_R * 0.52
mix_L += perc_L * 0.48;   mix_R += perc_R * 0.48
mix_L += lead_L * 0.58;   mix_R += lead_R * 0.58
mix_L += atmo_L * 0.42;   mix_R += atmo_R * 0.42
mix_L += fx_L * 0.50;     mix_R += fx_R * 0.50

# Sidechain
print("Sidechain...")
kick_mono = (kick_L + kick_R) / 2
kick_env = np.abs(kick_mono)
window = int(0.035 * SR)
kernel = np.ones(window) / window
kick_smooth = np.convolve(kick_env, kernel, mode='same')
kick_smooth /= (np.max(kick_smooth) + 1e-10)
sidechain = 1.0 - kick_smooth * 0.35

non_kick_L = mix_L - kick_L * 0.92
non_kick_R = mix_R - kick_R * 0.92
mix_L = kick_L * 0.92 + non_kick_L * sidechain
mix_R = kick_R * 0.92 + non_kick_R * sidechain

# MASTERING
print("Masterizando...")

# HPF
mix_L = hp(mix_L, 28)
mix_R = hp(mix_R, 28)

# Tame sub
sub_L = lp(mix_L, 60)
sub_R = lp(mix_R, 60)
mix_L -= sub_L * 0.25
mix_R -= sub_R * 0.25

# Boost mids
mid_L = bp(mix_L, 200, 800)
mid_R = bp(mix_R, 200, 800)
mix_L += mid_L * 0.35
mix_R += mid_R * 0.35

# Boost presence
pres_L = bp(mix_L, 2000, 7000)
pres_R = bp(mix_R, 2000, 7000)
mix_L += pres_L * 0.25
mix_R += pres_R * 0.25

# Saturation
mix_L = waveshape(mix_L, 1.6)
mix_R = waveshape(mix_R, 1.6)

# Normalize + limit
peak = max(np.max(np.abs(mix_L)), np.max(np.abs(mix_R)))
if peak > 0:
    mix_L /= peak; mix_R /= peak

# Target RMS
current_rms = np.sqrt(np.mean(mix_L**2 + mix_R**2) / 2)
target_rms = 10 ** (-9.0 / 20)
if current_rms > 0:
    gain = min(target_rms / current_rms, 3.0)
    mix_L *= gain; mix_R *= gain

mix_L = np.clip(mix_L, -0.98, 0.98)
mix_R = np.clip(mix_R, -0.98, 0.98)

# SAVE
print("Guardando...")
stereo = np.column_stack([
    (mix_L * 32767).astype(np.int16),
    (mix_R * 32767).astype(np.int16)
])

output_path = os.path.join(OUTPUT_DIR, "DarkPsy_v3_HUMANIZED.wav")
wavfile.write(output_path, SR, stereo)

# Copy to desktop
import shutil
desktop_path = "C:/Users/Juan/Desktop/DarkPsy_v3_HUMANIZED.wav"
shutil.copy2(output_path, desktop_path)

# Spectrum check
print()
print("--- Verificación ---")
mono_c = (mix_L+mix_R)/2
fft_c = np.abs(np.fft.rfft(mono_c))
freqs_c = np.fft.rfftfreq(len(mono_c), 1/SR)
total_e = np.sum(fft_c**2)
for name, lo, hi in [('Sub 20-60',20,60),('Bass 60-200',60,200),('LowMid 200-600',200,600),
                      ('Mid 600-2k',600,2000),('HiMid 2k-6k',2000,6000),('Pres 6k-10k',6000,10000),
                      ('Air 10k-20k',10000,20000)]:
    mask = (freqs_c >= lo) & (freqs_c < hi)
    pct = np.sum(fft_c[mask]**2)/total_e*100
    bar = '#'*int(pct/2)
    print(f'  {name:18s}: {pct:5.1f}%  {bar}')
rms_c = np.sqrt(np.mean(mono_c**2))
print(f'  RMS: {20*np.log10(rms_c+1e-10):.1f} dB')

print()
print("=" * 60)
print(f" TRACK: {output_path}")
print(f" También en escritorio: {desktop_path}")
print(f" Duración: {TOTAL_TIME/60:.1f} min | STEREO | HUMANIZED")
print("=" * 60)
