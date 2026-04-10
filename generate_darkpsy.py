"""
Dark Psytrance Generator — Experimental con matices de luz
BPM: 150 | Scale: E Phrygian Dominant | Structure: full track layout
"""

import mido
import os
import random

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
BPM = 150
TICKS = 480  # ticks per beat
BAR = TICKS * 4  # one bar = 4 beats

# E Phrygian Dominant: E F G# A B C D
# MIDI notes - E scale across octaves
SCALE = {
    'E2': 40, 'F2': 41, 'G#2': 44, 'A2': 45, 'B2': 47, 'C3': 48, 'D3': 50,
    'E3': 52, 'F3': 53, 'G#3': 56, 'A3': 57, 'B3': 59, 'C4': 60, 'D4': 62,
    'E4': 64, 'F4': 65, 'G#4': 68, 'A4': 69, 'B4': 71, 'C5': 72, 'D5': 74,
    'E5': 76, 'F5': 77, 'G#5': 80,
}

# Scale degrees as MIDI values (octave 3-4 range for melodies)
SCALE_NOTES = [40, 41, 44, 45, 47, 48, 50, 52, 53, 56, 57, 59, 60, 62, 64, 65, 68, 69, 71, 72, 74, 76]

random.seed(42)  # reproducible


def save_midi(filename, tracks_data, channel=0):
    mid = mido.MidiFile(ticks_per_beat=TICKS)
    mid.tracks.append(mido.MidiTrack())  # tempo track
    mid.tracks[0].append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(BPM)))
    mid.tracks[0].append(mido.MetaMessage('end_of_track'))

    for track_name, notes in tracks_data:
        track = mido.MidiTrack()
        track.append(mido.MetaMessage('track_name', name=track_name))
        abs_events = []
        for note, vel, start, duration in notes:
            abs_events.append((start, 'note_on', note, vel, channel))
            abs_events.append((start + duration, 'note_off', note, 0, channel))
        abs_events.sort(key=lambda x: x[0])
        current = 0
        for evt in abs_events:
            delta = evt[0] - current
            track.append(mido.Message(evt[1], note=evt[2], velocity=evt[3], channel=evt[4], time=delta))
            current = evt[0]
        track.append(mido.MetaMessage('end_of_track'))
        mid.tracks.append(track)

    path = os.path.join(OUTPUT_DIR, filename)
    mid.save(path)
    print(f"  -> {filename}")


def gen_kick():
    """Classic psytrance 4-on-the-floor kick — 32 bars"""
    notes = []
    for bar in range(32):
        for beat in range(4):
            t = bar * BAR + beat * TICKS
            notes.append((36, 110, t, TICKS // 3))
    return notes


def gen_rolling_bass():
    """
    Psytrance rolling bassline — E root with 16th note patterns.
    Dark base with occasional G# (the 'light' note in phrygian dominant).
    """
    notes = []
    sixteenth = TICKS // 4
    root = 40  # E2
    light = 44  # G#2
    dark_alt = 41  # F2 (the dark tension)

    patterns = [
        # pattern: (note_offset_from_root, velocity)
        # Dark rolling pattern
        [(0,100),(0,80),(0,90),(0,70)] * 4,
        # With light accent
        [(0,100),(0,80),(4,90),(0,70)] * 2 + [(0,100),(0,80),(0,90),(0,70)] * 2,
        # Tension pattern
        [(0,100),(1,75),(0,90),(1,65)] * 4,
        # Ascending light
        [(0,100),(0,80),(4,85),(5,75)] * 2 + [(0,100),(0,80),(0,90),(0,70)] * 2,
    ]

    for bar in range(32):
        pattern = patterns[bar % len(patterns)]
        if bar >= 24:  # last 8 bars: more light notes for buildup
            pattern = patterns[1]
        for i, (offset, vel) in enumerate(pattern):
            t = bar * BAR + i * sixteenth
            note = root + offset
            # humanize velocity slightly
            v = max(40, min(127, vel + random.randint(-5, 5)))
            notes.append((note, v, t, sixteenth - 10))
    return notes


def gen_acid_line():
    """
    Acid/303-style line — the experimental dark texture.
    Uses slides (overlapping notes) and accent patterns.
    """
    notes = []
    sixteenth = TICKS // 4

    # Acid sequence: mix of dark and light intervals
    acid_sequence = [
        # (note, duration_in_16ths, velocity, rest_after)
        (52, 2, 100, 0),  # E3
        (53, 1, 80, 1),   # F3 (dark)
        (56, 3, 95, 0),   # G#3 (light!)
        (52, 1, 85, 1),   # E3
        (50, 2, 90, 0),   # D3
        (48, 1, 75, 0),   # C3
        (52, 2, 100, 0),  # E3
        (41, 1, 70, 1),   # F2 low (dark growl)
        (56, 2, 95, 0),   # G#3 (light again)
        (57, 1, 85, 0),   # A3
        (52, 3, 100, 1),  # E3 resolve
    ]

    # Second pattern — more experimental, triplet feel
    acid_sequence_2 = [
        (52, 1, 100, 0), (56, 1, 90, 0), (59, 1, 85, 0),  # ascending light
        (60, 2, 95, 0),  # C4
        (57, 1, 80, 1),  # A3
        (53, 2, 100, 0), (52, 1, 90, 0),  # dark descent
        (50, 1, 75, 0), (48, 2, 85, 1),   # deep
        (52, 2, 100, 0), (56, 2, 95, 0),  # resolve to light
    ]

    sequences = [acid_sequence, acid_sequence_2]
    t = 0
    target = 32 * BAR

    seq_idx = 0
    while t < target:
        seq = sequences[seq_idx % 2]
        for note, dur, vel, rest in seq:
            if t >= target:
                break
            d = dur * sixteenth
            v = max(40, min(127, vel + random.randint(-8, 8)))
            notes.append((note, v, t, d - 5))
            t += d
            if rest:
                t += sixteenth
        seq_idx += 1

    return notes


def gen_hihat():
    """Psytrance hi-hats: offbeat 8ths with ghost 16ths"""
    notes = []
    sixteenth = TICKS // 4

    for bar in range(32):
        for step in range(16):
            t = bar * BAR + step * sixteenth
            if step % 4 == 2:  # offbeat 8ths — main hat
                notes.append((42, 95 + random.randint(-5, 5), t, sixteenth - 10))
            elif step % 2 == 1:  # ghost 16ths
                vel = 45 + random.randint(-10, 15)
                if random.random() > 0.3:
                    notes.append((42, vel, t, sixteenth // 2))
            # open hat on beat 4 occasionally
            if step == 12 and bar % 4 == 3:
                notes.append((46, 80, t, sixteenth * 2))
    return notes


def gen_perc():
    """Percusion layers: claps, rides, tribal-ish hits"""
    notes = []
    sixteenth = TICKS // 4

    for bar in range(32):
        # Clap on 2 and 4
        for beat in [1, 3]:
            t = bar * BAR + beat * TICKS
            notes.append((39, 90 + random.randint(-5, 5), t, TICKS // 4))

        # Ride pattern — varies per section
        if bar >= 8:  # kicks in after intro
            for step in range(16):
                t = bar * BAR + step * sixteenth
                if step % 3 == 0:  # triplet feel ride
                    notes.append((51, 55 + random.randint(-10, 10), t, sixteenth - 10))

        # Tribal tom hit every 2 bars
        if bar % 2 == 1:
            t = bar * BAR + 3 * TICKS + 2 * sixteenth
            notes.append((47, 75, t, sixteenth * 2))
    return notes


def gen_lead_melody():
    """
    Lead melody — the 'light' element. Appears in breakdowns and drops.
    Phrygian dominant melodic phrases with emphasis on G# and B (bright intervals).
    """
    notes = []

    # Melodic phrases — designed for light/hope within darkness
    # Each phrase = list of (note, duration_beats, velocity)
    phrases = [
        # Phrase 1: ascending hope
        [(64, 0.5, 85), (68, 0.75, 95), (69, 0.25, 80), (71, 1.0, 100), (68, 0.5, 85)],
        # Phrase 2: call and response
        [(76, 0.5, 90), (72, 0.5, 85), (71, 0.5, 80), (68, 1.5, 95)],
        # Phrase 3: tension and release
        [(64, 0.25, 80), (65, 0.25, 75), (68, 1.0, 100), (72, 0.5, 90), (71, 0.75, 85)],
        # Phrase 4: ethereal float
        [(80, 1.0, 75), (76, 0.5, 80), (72, 1.0, 90), (71, 0.5, 85), (68, 1.0, 95)],
        # Phrase 5: dark dip then rise
        [(64, 0.5, 90), (62, 0.5, 85), (60, 0.5, 80), (64, 0.5, 85), (68, 1.0, 100), (72, 1.0, 95)],
    ]

    # Melody appears in bars 8-15 (first drop) and 20-31 (breakdown + second drop)
    melody_bars = list(range(8, 16)) + list(range(20, 32))

    t = 0
    phrase_idx = 0
    for bar in melody_bars:
        phrase = phrases[phrase_idx % len(phrases)]
        t = bar * BAR
        for note, dur, vel in phrase:
            d = int(dur * TICKS)
            v = max(40, min(127, vel + random.randint(-5, 5)))
            notes.append((note, v, t, d - 10))
            t += d
        phrase_idx += 1

    return notes


def gen_atmosphere():
    """
    Atmospheric pads — long sustained chords for the 'matices de luz' moments.
    Dark base chords with bright extensions.
    """
    notes = []

    # Chord progression: each chord = list of notes, lasting 4 bars
    chords = [
        # Em(add9) — dark root, bright 9th
        [40, 47, 52, 59, 66],  # E B E B F#(add color)... using scale: E B E B
        # Actually let's use proper phrygian dominant chords
        # i: E-G#-B (bright minor with major 3rd feel from phrygian dominant)
        [52, 56, 59],
        # bII: F-A-C (neapolitan, dreamy)
        [53, 57, 60],
        # iv: A-C-E (minor, melancholic)
        [57, 60, 64],
        # bVII: D-F-A (resolution, warmth)
        [50, 53, 57],
        # V: B-D#-F# but in phrygian dominant context -> use G#-B-D (light!)
        [56, 59, 62],
        # i again
        [52, 56, 59],
        # vi dim feel -> C-E-G# (augmented = psychedelic!)
        [48, 52, 56],
        # back to root
        [52, 56, 59],
    ]

    bar = 0
    chord_idx = 0
    while bar < 32:
        chord = chords[chord_idx % len(chords)]
        for note in chord:
            vel = 60 + random.randint(-5, 5)
            notes.append((note, vel, bar * BAR, BAR * 4 - TICKS))  # hold 3.75 bars
        bar += 4
        chord_idx += 1

    return notes


def gen_fx_riser():
    """
    FX risers / sweeps before drops — represented as ascending note sequences.
    Use as trigger for noise sweeps in Ableton.
    """
    notes = []
    sixteenth = TICKS // 4

    # Riser before bar 8 (first drop): bars 6-7
    for step in range(32):  # 2 bars of 16ths
        t = 6 * BAR + step * sixteenth
        note = 60 + (step // 2)  # ascending
        vel = 50 + step * 2
        notes.append((min(note, 84), min(vel, 120), t, sixteenth - 5))

    # Riser before bar 20 (second drop): bars 18-19
    for step in range(32):
        t = 18 * BAR + step * sixteenth
        note = 55 + (step // 2)
        vel = 45 + step * 2
        notes.append((min(note, 84), min(vel, 120), t, sixteenth - 5))

    # Impact hits on drop bars
    for drop_bar in [8, 20]:
        notes.append((36, 127, drop_bar * BAR, TICKS))

    return notes


# ============================================================
# GENERATE ALL MIDI FILES
# ============================================================

print("=" * 50)
print(" DARK PSYTRANCE — Experimental con matices de luz")
print(" BPM: 150 | Key: E Phrygian Dominant")
print("=" * 50)
print()

# 1. Kick
print("[DRUMS]")
save_midi("01_Kick.mid", [("Kick", gen_kick())], channel=9)

# 2. Rolling Bass
print("[BASS]")
save_midi("02_Rolling_Bass.mid", [("Rolling Bass", gen_rolling_bass())])

# 3. Acid Line
print("[SYNTH]")
save_midi("03_Acid_Line.mid", [("Acid 303", gen_acid_line())])

# 4. Hi-hats
print("[DRUMS]")
save_midi("04_HiHats.mid", [("Hi-Hats", gen_hihat())], channel=9)

# 5. Percussion
save_midi("05_Perc.mid", [("Percussion", gen_perc())], channel=9)

# 6. Lead Melody (the light)
print("[MELODY]")
save_midi("06_Lead_Light.mid", [("Lead - Light", gen_lead_melody())])

# 7. Atmosphere Pads
print("[PADS]")
save_midi("07_Atmosphere.mid", [("Atmo Pads", gen_atmosphere())])

# 8. FX Risers
print("[FX]")
save_midi("08_FX_Risers.mid", [("FX Risers", gen_fx_riser())])

# 9. Full arrangement (all non-drum elements together)
print()
print("[FULL ARRANGEMENT]")
save_midi("09_Full_Arrangement.mid", [
    ("Kick", gen_kick()),
    ("Rolling Bass", gen_rolling_bass()),
    ("Acid 303", gen_acid_line()),
    ("Hi-Hats", gen_hihat()),
    ("Percussion", gen_perc()),
    ("Lead - Light", gen_lead_melody()),
    ("Atmo Pads", gen_atmosphere()),
    ("FX Risers", gen_fx_riser()),
])

print()
print("=" * 50)
print(" ESTRUCTURA DEL TRACK (32 bars):")
print("=" * 50)
print(" Bars 1-4:   INTRO — Kick + Bass minimal")
print(" Bars 5-7:   BUILD — Acid enters + hats")
print(" Bars 6-7:   RISER — FX sweep")
print(" Bars 8-15:  DROP 1 — Full energy + Lead melody")
print(" Bars 16-19: BREAKDOWN — Pads + Lead (matices de luz)")
print(" Bars 18-19: RISER 2 — Build to second drop")
print(" Bars 20-27: DROP 2 — Full energy + melodic variation")
print(" Bars 28-31: OUTRO — Elements dropping out")
print("=" * 50)
print()
print(f"Archivos guardados en: {OUTPUT_DIR}")
