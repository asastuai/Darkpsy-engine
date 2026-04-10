"""
DARK PSYTRANCE — Full Audio Synthesis
Genera WAV completo: kick, bass rolling, acid, hats, perc, lead, pads, FX
Todo sintetizado desde cero. BPM 150, E Phrygian Dominant.
"""

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt, sawtooth, square
import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
SR = 44100
BPM = 150
BEAT = 60.0 / BPM  # seconds per beat
BAR = BEAT * 4
TOTAL_BARS = 64  # full track
TOTAL_TIME = TOTAL_BARS * BAR
TOTAL_SAMPLES = int(TOTAL_TIME * SR)

print("=" * 55)
print(" DARK PSYTRANCE — Full Audio Synthesis Engine")
print(f" BPM: {BPM} | Bars: {TOTAL_BARS} | Duration: {TOTAL_TIME:.0f}s")
print("=" * 55)


def make_time(duration):
    return np.linspace(0, duration, int(duration * SR), endpoint=False)


def lowpass(signal, cutoff, sr=SR, order=4):
    sos = butter(order, cutoff, btype='low', fs=sr, output='sos')
    return sosfilt(sos, signal)


def highpass(signal, cutoff, sr=SR, order=2):
    sos = butter(order, cutoff, btype='high', fs=sr, output='sos')
    return sosfilt(sos, signal)


def bandpass(signal, low, high, sr=SR, order=2):
    sos = butter(order, [low, high], btype='band', fs=sr, output='sos')
    return sosfilt(sos, signal)


def note_to_freq(note):
    return 440.0 * (2.0 ** ((note - 69) / 12.0))


def env_adsr(t, a=0.01, d=0.1, s=0.7, r=0.2, total=None):
    if total is None:
        total = len(t) / SR
    env = np.zeros_like(t, dtype=np.float64)
    for i, ti in enumerate(t):
        if ti < a:
            env[i] = ti / a
        elif ti < a + d:
            env[i] = 1.0 - (1.0 - s) * (ti - a) / d
        elif ti < total - r:
            env[i] = s
        else:
            env[i] = s * max(0, (total - ti) / r)
    return env


def soft_clip(signal, threshold=0.8):
    return np.tanh(signal / threshold) * threshold


# ============================================================
# KICK DRUM — Psy kick with pitch envelope
# ============================================================
def gen_kick_sound(duration=0.25):
    t = make_time(duration)
    # Pitch drops from 150Hz to 45Hz
    pitch_env = 45 + 105 * np.exp(-t * 40)
    phase = 2 * np.pi * np.cumsum(pitch_env) / SR
    kick = np.sin(phase)
    # Amp envelope
    amp = np.exp(-t * 12)
    # Add click
    click = np.random.randn(len(t)) * np.exp(-t * 200) * 0.3
    return soft_clip((kick * amp + click) * 0.9)


def gen_kick_track():
    print("  [1/8] Kick drum...")
    out = np.zeros(TOTAL_SAMPLES)
    kick = gen_kick_sound(0.25)

    for bar in range(TOTAL_BARS):
        # Kick enters at bar 0, full track
        # Drops out in breakdown (bars 32-39)
        if 32 <= bar < 36:
            continue
        for beat in range(4):
            pos = int((bar * BAR + beat * BEAT) * SR)
            end = min(pos + len(kick), TOTAL_SAMPLES)
            out[pos:end] += kick[:end - pos]
    return out


# ============================================================
# ROLLING BASS — The psytrance signature
# ============================================================
def gen_bass_track():
    print("  [2/8] Rolling bass...")
    out = np.zeros(TOTAL_SAMPLES)
    sixteenth = BEAT / 4
    root = 40  # E2

    # Bass pattern per bar: note offsets from root
    patterns = [
        [0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,0],  # straight root
        [0,0,4,0, 0,0,4,0, 0,0,0,0, 0,0,4,0],   # with G# accents (light)
        [0,0,1,0, 0,0,1,0, 0,0,0,0, 0,1,0,0],   # with F tension (dark)
        [0,0,4,5, 0,0,4,0, 0,0,0,7, 0,0,4,0],   # melodic variation
    ]

    for bar in range(TOTAL_BARS):
        if 32 <= bar < 38:  # breakdown: bass drops
            continue

        pat = patterns[bar % len(patterns)]
        if bar >= 48:  # last section: more melodic
            pat = patterns[3]

        for step in range(16):
            note = root + pat[step]
            freq = note_to_freq(note)
            t = make_time(sixteenth * 0.9)

            # Saw wave + square sub
            saw = sawtooth(2 * np.pi * freq * t)
            sub = np.sin(2 * np.pi * freq * 0.5 * t)

            # Filter envelope — quick attack, medium decay
            cutoff_start = 2000 + 1500 * (step % 4 == 0)
            cutoff_end = 400
            n = len(t)
            cutoff_env = cutoff_end + (cutoff_start - cutoff_end) * np.exp(-t * 20)

            # Apply dynamic filter (simplified: use average cutoff)
            avg_cutoff = min(float(np.mean(cutoff_env)), SR/2 - 100)
            bass = lowpass(saw * 0.6 + sub * 0.4, avg_cutoff)

            # Amp envelope
            amp = np.exp(-t * 8) * 0.8
            amp[:min(50, n)] *= np.linspace(0, 1, min(50, n))  # click removal

            # Distortion
            bass = soft_clip(bass * amp * 1.5)

            # Velocity variation
            vel = 0.7 + 0.3 * (step % 4 == 0)

            pos = int((bar * BAR + step * sixteenth) * SR)
            end = min(pos + len(bass), TOTAL_SAMPLES)
            out[pos:end] += bass[:end - pos] * vel

    return out * 0.85


# ============================================================
# ACID LINE — 303 style
# ============================================================
def gen_acid_track():
    print("  [3/8] Acid line...")
    out = np.zeros(TOTAL_SAMPLES)
    sixteenth = BEAT / 4

    # Acid sequence: (midi_note, duration_16ths, accent, slide)
    sequences = [
        [(52,2,1,0),(53,1,0,1),(56,3,1,0),(52,1,0,0),(50,2,1,0),(48,1,0,1),(52,2,1,0),(41,1,0,0),(56,2,1,0),(57,1,0,0)],
        [(52,1,1,0),(56,1,0,1),(59,1,1,0),(60,2,1,0),(57,1,0,0),(53,2,1,0),(52,1,0,1),(50,1,0,0),(48,2,1,0),(52,2,1,0)],
        [(64,1,1,0),(62,1,0,1),(60,2,1,0),(56,1,0,0),(52,2,1,0),(53,1,0,1),(56,2,1,0),(59,1,1,0),(57,1,0,0),(52,2,1,0)],
    ]

    for bar in range(TOTAL_BARS):
        # Acid enters at bar 4
        if bar < 4:
            continue
        if 32 <= bar < 40:  # breakdown: acid goes ambient
            continue

        seq = sequences[bar % len(sequences)]
        t_offset = 0

        for note, dur, accent, slide in seq:
            freq = note_to_freq(note)
            note_dur = dur * sixteenth
            t = make_time(note_dur * 0.95)

            # Saw oscillator
            saw = sawtooth(2 * np.pi * freq * t)

            # Resonant filter (acid character)
            cutoff = 800 + 2000 * accent
            filt = lowpass(saw, min(cutoff, SR/2 - 100))

            # Filter envelope
            env_t = np.linspace(0, 1, len(t))
            filt_env = np.exp(-env_t * (3 if accent else 6))

            # Apply
            acid = filt * filt_env

            # Amp envelope
            amp = env_adsr(t, a=0.005, d=0.05, s=0.6, r=0.05, total=note_dur)
            acid = soft_clip(acid * amp * (1.2 if accent else 0.8))

            pos = int((bar * BAR + t_offset) * SR)
            end = min(pos + len(acid), TOTAL_SAMPLES)
            if pos < TOTAL_SAMPLES:
                out[pos:end] += acid[:end - pos]

            t_offset += note_dur

    return out * 0.5


# ============================================================
# HI-HATS — Noise-based, offbeat psy pattern
# ============================================================
def gen_hihat_track():
    print("  [4/8] Hi-hats...")
    out = np.zeros(TOTAL_SAMPLES)
    sixteenth = BEAT / 4

    for bar in range(TOTAL_BARS):
        if bar < 2:
            continue
        if 32 <= bar < 36:
            continue

        for step in range(16):
            t_pos = bar * BAR + step * sixteenth

            is_offbeat = step % 4 == 2
            is_ghost = step % 2 == 1
            is_open = step == 12 and bar % 4 == 3

            if is_open:
                dur = sixteenth * 2
                t = make_time(dur)
                noise = bandpass(np.random.randn(len(t)), 6000, 16000)
                amp = np.exp(-t * 8)
                hat = noise * amp * 0.35
            elif is_offbeat:
                dur = sixteenth * 0.7
                t = make_time(dur)
                noise = highpass(np.random.randn(len(t)), 8000)
                amp = np.exp(-t * 30)
                hat = noise * amp * 0.3
            elif is_ghost and np.random.random() > 0.3:
                dur = sixteenth * 0.4
                t = make_time(dur)
                noise = highpass(np.random.randn(len(t)), 9000)
                amp = np.exp(-t * 50)
                hat = noise * amp * 0.12
            else:
                continue

            pos = int(t_pos * SR)
            end = min(pos + len(hat), TOTAL_SAMPLES)
            out[pos:end] += hat[:end - pos]

    return out


# ============================================================
# PERCUSSION — Claps, rides, tribal hits
# ============================================================
def gen_perc_track():
    print("  [5/8] Percussion...")
    out = np.zeros(TOTAL_SAMPLES)

    for bar in range(TOTAL_BARS):
        if bar < 4:
            continue
        if 32 <= bar < 38:
            continue

        # Clap on 2 and 4
        for beat in [1, 3]:
            t = make_time(0.08)
            noise = bandpass(np.random.randn(len(t)), 1000, 4000)
            amp = np.exp(-t * 35)
            clap = noise * amp * 0.35

            pos = int((bar * BAR + beat * BEAT) * SR)
            end = min(pos + len(clap), TOTAL_SAMPLES)
            out[pos:end] += clap[:end - pos]

        # Ride — triplet feel
        if bar >= 8:
            sixteenth = BEAT / 4
            for step in range(16):
                if step % 3 == 0:
                    t = make_time(0.05)
                    noise = highpass(np.random.randn(len(t)), 10000)
                    amp = np.exp(-t * 40)
                    ride = noise * amp * 0.08

                    pos = int((bar * BAR + step * sixteenth) * SR)
                    end = min(pos + len(ride), TOTAL_SAMPLES)
                    out[pos:end] += ride[:end - pos]

    return out


# ============================================================
# LEAD MELODY — The light within darkness
# ============================================================
def gen_lead_track():
    print("  [6/8] Lead melody (matices de luz)...")
    out = np.zeros(TOTAL_SAMPLES)

    # Melodic phrases: (midi_note, duration_beats, velocity)
    phrases = [
        [(64,0.5,0.8),(68,0.75,1.0),(69,0.25,0.7),(71,1.0,1.0),(68,0.5,0.8)],
        [(76,0.5,0.9),(72,0.5,0.8),(71,0.5,0.7),(68,1.5,1.0)],
        [(64,0.25,0.7),(65,0.25,0.6),(68,1.0,1.0),(72,0.5,0.9),(71,0.75,0.8)],
        [(80,1.0,0.6),(76,0.5,0.7),(72,1.0,0.9),(71,0.5,0.8),(68,1.0,1.0)],
        [(64,0.5,0.9),(62,0.5,0.8),(60,0.5,0.7),(64,0.5,0.8),(68,1.0,1.0),(72,1.0,0.9)],
    ]

    # Lead appears: bars 8-24, 40-56 (drops + transitions)
    melody_bars = list(range(8, 24)) + list(range(40, 56))

    phrase_idx = 0
    for bar in melody_bars:
        phrase = phrases[phrase_idx % len(phrases)]
        t_offset = 0

        for note, dur, vel in phrase:
            freq = note_to_freq(note)
            note_dur = dur * BEAT
            t = make_time(note_dur)

            # Supersaw-ish: 3 detuned saws
            saw1 = sawtooth(2 * np.pi * freq * t)
            saw2 = sawtooth(2 * np.pi * freq * 1.005 * t)
            saw3 = sawtooth(2 * np.pi * freq * 0.995 * t)
            lead = (saw1 + saw2 + saw3) / 3

            # Filter
            lead = lowpass(lead, min(freq * 6, SR/2 - 100))

            # Envelope
            amp = env_adsr(t, a=0.02, d=0.1, s=0.7, r=0.15, total=note_dur)
            lead = lead * amp * vel * 0.4

            pos = int((bar * BAR + t_offset) * SR)
            end = min(pos + len(lead), TOTAL_SAMPLES)
            if pos < TOTAL_SAMPLES:
                out[pos:end] += lead[:end - pos]

            t_offset += note_dur

        phrase_idx += 1

    # Add reverb-like effect (simple delay feedback)
    delay_samples = int(BEAT * SR * 0.375)  # dotted 8th
    reverb = np.zeros(TOTAL_SAMPLES)
    for i in range(4):
        d = delay_samples * (i + 1)
        decay = 0.3 ** (i + 1)
        if d < TOTAL_SAMPLES:
            reverb[d:] += out[:TOTAL_SAMPLES - d] * decay

    return (out + reverb) * 0.6


# ============================================================
# ATMOSPHERE — Dark pads with light moments
# ============================================================
def gen_atmosphere_track():
    print("  [7/8] Atmosphere pads...")
    out = np.zeros(TOTAL_SAMPLES)

    # Chord progression: each chord lasts 4 bars
    chords = [
        [52, 56, 59],    # E-G#-B (root, bright)
        [53, 57, 60],    # F-A-C (dark, neapolitan)
        [57, 60, 64],    # A-C-E (melancholic)
        [50, 53, 57],    # D-F-A (warm)
        [56, 59, 62],    # G#-B-D (light, hopeful)
        [52, 56, 59],    # E-G#-B (return)
        [48, 52, 56],    # C-E-G# (augmented, psychedelic!)
        [52, 56, 59],    # E-G#-B (resolve)
    ]

    for chord_idx, chord in enumerate(chords):
        start_bar = chord_idx * 4
        if start_bar >= TOTAL_BARS:
            break

        chord_dur = min(4 * BAR, (TOTAL_BARS - start_bar) * BAR)
        t = make_time(chord_dur)

        pad = np.zeros(len(t))
        for note in chord:
            freq = note_to_freq(note)
            # Slow-moving pad: sine + filtered saw
            sine = np.sin(2 * np.pi * freq * t) * 0.5
            saw_raw = sawtooth(2 * np.pi * freq * t) * 0.3
            # Very low cutoff for warmth
            saw_filt = lowpass(saw_raw, min(freq * 2, SR/2 - 100))
            # LFO on amplitude for movement
            lfo = 0.7 + 0.3 * np.sin(2 * np.pi * 0.15 * t)
            pad += (sine + saw_filt) * lfo

        pad /= len(chord)

        # Long fade in/out
        fade_len = min(int(2.0 * SR), len(t) // 4)
        pad[:fade_len] *= np.linspace(0, 1, fade_len)
        pad[-fade_len:] *= np.linspace(1, 0, fade_len)

        pos = int(start_bar * BAR * SR)
        end = min(pos + len(pad), TOTAL_SAMPLES)
        out[pos:end] += pad[:end - pos]

    # Repeat for second half
    half = TOTAL_SAMPLES // 2
    if half < TOTAL_SAMPLES:
        remaining = TOTAL_SAMPLES - half
        out[half:half + remaining] += out[:remaining] * 0.8

    return out * 0.35


# ============================================================
# FX — Risers, impacts, sweeps
# ============================================================
def gen_fx_track():
    print("  [8/8] FX risers & impacts...")
    out = np.zeros(TOTAL_SAMPLES)

    # Riser function: noise sweep upward
    def make_riser(duration=4.0):
        t = make_time(duration)
        noise = np.random.randn(len(t))
        # Sweep filter from low to high
        n = len(t)
        riser = np.zeros(n)
        chunks = 32
        chunk_size = n // chunks
        for i in range(chunks):
            start = i * chunk_size
            end_c = min(start + chunk_size, n)
            cutoff = 200 + (12000 * (i / chunks) ** 2)
            cutoff = min(cutoff, SR/2 - 100)
            chunk = noise[start:end_c]
            if len(chunk) > 20:
                riser[start:end_c] = lowpass(chunk, cutoff)
        # Volume ramp
        riser *= np.linspace(0, 1, n) ** 2
        return riser * 0.4

    # Impact: short burst
    def make_impact():
        t = make_time(0.5)
        noise = np.random.randn(len(t))
        filt = lowpass(noise, 2000)
        sub = np.sin(2 * np.pi * 40 * t)  # sub boom
        amp = np.exp(-t * 6)
        return (filt * 0.5 + sub * 0.8) * amp * 0.6

    # Riser positions (2 bars before each drop)
    riser_points = [
        (6, 2),    # bars 6-7, before drop at 8
        (22, 2),   # bars 22-23
        (38, 2),   # before bar 40
        (54, 2),   # before bar 56
    ]

    for bar, dur_bars in riser_points:
        if bar >= TOTAL_BARS:
            continue
        riser = make_riser(dur_bars * BAR)
        pos = int(bar * BAR * SR)
        end = min(pos + len(riser), TOTAL_SAMPLES)
        out[pos:end] += riser[:end - pos]

    # Impacts on drop bars
    impact = make_impact()
    for drop_bar in [8, 24, 40, 56]:
        if drop_bar >= TOTAL_BARS:
            continue
        pos = int(drop_bar * BAR * SR)
        end = min(pos + len(impact), TOTAL_SAMPLES)
        out[pos:end] += impact[:end - pos]

    return out


# ============================================================
# MIX & MASTER
# ============================================================
print()
print("Sintetizando elementos...")

kick = gen_kick_track()
bass = gen_bass_track()
acid = gen_acid_track()
hats = gen_hihat_track()
perc = gen_perc_track()
lead = gen_lead_track()
atmo = gen_atmosphere_track()
fx = gen_fx_track()

print()
print("Mezclando...")

# Mix levels
mix = np.zeros(TOTAL_SAMPLES)
mix += kick * 1.0      # Kick: loud
mix += bass * 0.85     # Bass: just under kick
mix += acid * 0.55     # Acid: present but not dominant
mix += hats * 0.60     # Hats: crispy
mix += perc * 0.50     # Perc: support
mix += lead * 0.55     # Lead: the light
mix += atmo * 0.40     # Atmo: background
mix += fx * 0.65       # FX: dramatic

# Simple sidechain: duck mix slightly on each kick hit
print("Aplicando sidechain...")
kick_env = np.abs(kick)
# Smooth the kick envelope
window = int(0.05 * SR)
kernel = np.ones(window) / window
kick_smooth = np.convolve(kick_env, kernel, mode='same')
kick_smooth = kick_smooth / (np.max(kick_smooth) + 1e-10)
# Duck everything except kick
sidechain = 1.0 - kick_smooth * 0.3
mix_no_kick = mix - kick * 1.0
mix = kick * 1.0 + mix_no_kick * sidechain

# Master: soft clip + normalize
print("Masterizando...")
mix = soft_clip(mix, 0.85)
peak = np.max(np.abs(mix))
if peak > 0:
    mix = mix / peak * 0.95

# Convert to 16-bit
mix_16 = (mix * 32767).astype(np.int16)

# Save
output_path = os.path.join(OUTPUT_DIR, "DarkPsy_Experimental_FULL.wav")
wavfile.write(output_path, SR, mix_16)

# Also save individual stems
print("Guardando stems individuales...")
stems = [
    ("stem_kick.wav", kick),
    ("stem_bass.wav", bass),
    ("stem_acid.wav", acid),
    ("stem_hats.wav", hats),
    ("stem_perc.wav", perc),
    ("stem_lead.wav", lead),
    ("stem_atmosphere.wav", atmo),
    ("stem_fx.wav", fx),
]
for name, stem in stems:
    s = stem / (np.max(np.abs(stem)) + 1e-10) * 0.9
    s_16 = (s * 32767).astype(np.int16)
    wavfile.write(os.path.join(OUTPUT_DIR, name), SR, s_16)

print()
print("=" * 55)
print(f" TRACK COMPLETO: {output_path}")
print(f" Duración: {TOTAL_TIME:.0f} segundos ({TOTAL_TIME/60:.1f} min)")
print(f" + 8 stems individuales para mezclar en Reaper")
print("=" * 55)
print()
print(" ESTRUCTURA:")
print(" Bars  1-7:   INTRO + BUILD (kick + bass + acid entra)")
print(" Bars  8-23:  DROP 1 (full energy + lead melody)")
print(" Bars 24-31:  TRANSICIÓN")
print(" Bars 32-39:  BREAKDOWN (pads + lead = matices de luz)")
print(" Bars 40-55:  DROP 2 (full energy + variación)")
print(" Bars 56-64:  OUTRO")
print()
print(" Abrí DarkPsy_Experimental_FULL.wav para escuchar!")
