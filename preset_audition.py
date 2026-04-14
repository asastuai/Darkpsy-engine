"""
PRESET AUDITION — Test factory presets for each dark psy element.
Renders short demos through each preset so Juan can pick the best ones.
"""

import numpy as np
from scipy.io import wavfile
from pedalboard import load_plugin
import os, sys, glob

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

SR = 44100
BPM = 150
BEAT = 60.0 / BPM
S16 = BEAT / 4

SURGE_PATH = 'C:/Program Files/Common Files/VST3/Surge Synth Team/Surge XT.vst3/Contents/x86_64-win/Surge XT.vst3'
PRESETS_BASE = 'C:/ProgramData/Surge XT'
OUTPUT_DIR = 'C:/Users/Juan/.openclaw/darkpsy-project/auditions'
os.makedirs(OUTPUT_DIR, exist_ok=True)

ROOT = 40  # E2


def render_preset(preset_path, midi_events, duration, name):
    """Load a preset and render MIDI through it"""
    try:
        surge = load_plugin(SURGE_PATH)
        with open(preset_path, 'rb') as f:
            surge.raw_state = f.read()

        result = surge(midi_events, duration=duration, sample_rate=SR, num_channels=2)
        rms = np.sqrt(np.mean(result**2))

        if rms < 0.0005:
            return None  # silent preset, skip

        # Normalize
        peak = np.max(np.abs(result))
        if peak > 0:
            result = result / peak * 0.85

        return result
    except Exception as e:
        return None


def save_demo(result, filename):
    if result is None:
        return
    stereo = (result.T * 32767).astype(np.int16)
    wavfile.write(os.path.join(OUTPUT_DIR, filename), SR, stereo)


# ============================================================
# BASS AUDITION — rolling 1/16 pattern in E
# ============================================================
def make_bass_midi():
    """4 bars of rolling bass at 1/16"""
    events = []
    for bar in range(4):
        for step in range(16):
            note = ROOT  # stay on root for fair comparison
            if step in [4, 12]:
                note = ROOT + 4  # G# accent
            vel = 90 + 20 * (step % 4 == 0)
            t = bar * BEAT * 4 + step * S16
            events.append((bytes([0x90, note, vel]), t))
            events.append((bytes([0x80, note, 0]), t + S16 * 0.8))
    return events

# ============================================================
# LEAD AUDITION — melodic phrase
# ============================================================
def make_lead_midi():
    """Melodic phrase repeated"""
    events = []
    phrase = [(64, 0.5), (68, 0.75), (69, 0.25), (71, 1.0), (68, 0.5),
              (76, 0.5), (72, 0.5), (71, 0.5), (68, 1.5)]
    for rep in range(2):
        t = rep * 6 * BEAT
        for note, dur in phrase:
            events.append((bytes([0x90, note, 100]), t))
            events.append((bytes([0x80, note, 0]), t + dur * BEAT * 0.9))
            t += dur * BEAT
    return events

# ============================================================
# ACID AUDITION — fast squelchy line
# ============================================================
def make_acid_midi():
    """Acid sequence"""
    events = []
    seq = [(52,2,110),(53,1,80),(56,3,110),(52,1,80),(50,2,100),(48,1,70),(52,2,110)]
    t = 0
    for rep in range(3):
        for note, dur, vel in seq:
            d = dur * S16
            events.append((bytes([0x90, note, vel]), t))
            events.append((bytes([0x80, note, 0]), t + d * 0.85))
            t += d
    return events

# ============================================================
# PAD AUDITION — sustained chord
# ============================================================
def make_pad_midi():
    """Long chord"""
    events = []
    chord = [52, 56, 59]  # E-G#-B
    for note in chord:
        events.append((bytes([0x90, note, 80]), 0.0))
        events.append((bytes([0x80, note, 0]), 5.0))
    # Second chord
    chord2 = [53, 57, 60]  # F-A-C
    for note in chord2:
        events.append((bytes([0x90, note, 80]), 5.5))
        events.append((bytes([0x80, note, 0]), 10.0))
    return events

# ============================================================
# FX AUDITION — single long note (riser)
# ============================================================
def make_fx_midi():
    events = [
        (bytes([0x90, 60, 100]), 0.0),
        (bytes([0x80, 60, 0]), 4.0),
    ]
    return events


# ============================================================
# SEARCH AND RENDER
# ============================================================

def find_presets(categories, subfolder='patches_factory'):
    """Find all .fxp presets in given categories"""
    presets = []
    for cat in categories:
        path = os.path.join(PRESETS_BASE, subfolder, cat)
        if os.path.exists(path):
            for f in sorted(glob.glob(os.path.join(path, '**', '*.fxp'), recursive=True)):
                presets.append(f)
    return presets


def audition_element(name, midi_events, duration, categories_factory, categories_3rd=None, max_per_source=15):
    """Render demos for an element across multiple preset categories"""
    print(f"\n{'='*50}")
    print(f" AUDITION: {name}")
    print(f"{'='*50}")

    element_dir = os.path.join(OUTPUT_DIR, name)
    os.makedirs(element_dir, exist_ok=True)

    # Factory presets
    factory = find_presets(categories_factory, 'patches_factory')
    print(f"  Factory presets found: {len(factory)}")

    # 3rd party presets
    third = []
    if categories_3rd:
        for author in os.listdir(os.path.join(PRESETS_BASE, 'patches_3rdparty')):
            for cat in categories_3rd:
                path = os.path.join(PRESETS_BASE, 'patches_3rdparty', author, cat)
                if os.path.exists(path):
                    for f in sorted(glob.glob(os.path.join(path, '*.fxp'))):
                        third.append(f)
    print(f"  3rd party presets found: {len(third)}")

    all_presets = factory[:max_per_source] + third[:max_per_source]
    print(f"  Testing: {len(all_presets)} presets")

    results = []
    for i, preset_path in enumerate(all_presets):
        preset_name = os.path.splitext(os.path.basename(preset_path))[0]
        # Clean name for filename
        safe_name = "".join(c if c.isalnum() or c in '-_ ' else '_' for c in preset_name)

        result = render_preset(preset_path, midi_events, duration, preset_name)
        if result is not None:
            rms = np.sqrt(np.mean(result**2))
            filename = f"{i+1:02d}_{safe_name}.wav"
            save_demo(result, os.path.join(name, filename))
            results.append((filename, preset_name, rms))
            print(f"    [{i+1:02d}] {preset_name} (RMS: {rms:.4f})")
        else:
            pass  # silent or error, skip silently

    # Create index file
    with open(os.path.join(element_dir, '_INDEX.txt'), 'w') as f:
        f.write(f"AUDITION: {name}\n")
        f.write(f"{'='*40}\n\n")
        for filename, preset_name, rms in results:
            f.write(f"  {filename} <- {preset_name}\n")
        f.write(f"\nTotal: {len(results)} presets que suenan\n")

    print(f"  Resultado: {len(results)} presets guardados en auditions/{name}/")
    return results


# ============================================================
# RUN ALL AUDITIONS
# ============================================================

print("=" * 60)
print(" PRESET AUDITION SESSION")
print(" Buscando los mejores sonidos entre 3008 presets")
print("=" * 60)

# BASS — the most important one
bass_results = audition_element(
    "bass",
    make_bass_midi(),
    duration=4 * BEAT * 4 + 1,  # 4 bars + tail
    categories_factory=['Basses', 'Sequences'],
    categories_3rd=['Basses', 'Bass'],
    max_per_source=20
)

# LEAD
lead_results = audition_element(
    "lead",
    make_lead_midi(),
    duration=13.0,
    categories_factory=['Leads', 'Polysynths'],
    categories_3rd=['Leads'],
    max_per_source=20
)

# ACID
acid_results = audition_element(
    "acid",
    make_acid_midi(),
    duration=8.0,
    categories_factory=['Leads', 'Sequences'],
    categories_3rd=['Leads', 'Sequences'],
    max_per_source=15
)

# PADS
pad_results = audition_element(
    "pad",
    make_pad_midi(),
    duration=11.0,
    categories_factory=['Pads'],
    categories_3rd=['Pads', 'Atmospheres'],
    max_per_source=20
)

# FX
fx_results = audition_element(
    "fx",
    make_fx_midi(),
    duration=5.0,
    categories_factory=['FX'],
    categories_3rd=['FX'],
    max_per_source=15
)

# PERCUSSION
perc_results = audition_element(
    "perc",
    [(bytes([0x90, 36+i*2, 100]), i*0.4) for i in range(8)] +
    [(bytes([0x80, 36+i*2, 0]), i*0.4+0.3) for i in range(8)],
    duration=4.0,
    categories_factory=['Percussion'],
    categories_3rd=['Drums', 'Percussion'],
    max_per_source=15
)

# Summary
print(f"\n{'='*60}")
print(f" AUDITION COMPLETE")
print(f"{'='*60}")
print(f"  Bass:  {len(bass_results)} opciones")
print(f"  Lead:  {len(lead_results)} opciones")
print(f"  Acid:  {len(acid_results)} opciones")
print(f"  Pads:  {len(pad_results)} opciones")
print(f"  FX:    {len(fx_results)} opciones")
print(f"  Perc:  {len(perc_results)} opciones")
print(f"\n  Todo en: {OUTPUT_DIR}")
print(f"  Escucha cada carpeta y decime cual te gusta por elemento")
