"""
DARK PSYTRANCE v8 — KINDZADZA PROCESSED
Takes v7 stems and processes them through KranchDD (Kindzadza's plugin)
with different settings per element for authentic dark psy character.
"""

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt
from pedalboard import load_plugin
import os, sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
SR = 44100

print("=" * 60)
print(" DARK PSYTRANCE v8 - KINDZADZA PROCESSED")
print("=" * 60)

# Load KranchDD
print("\nCargando KranchDD...")
kranchdd_path = "C:/Program Files/Common Files/VST3/KINDZAudio/KranchDD.vst3"
kranchdd = load_plugin(kranchdd_path)
print(f"  Loaded: {kranchdd.name} ({len(kranchdd.parameters)} params)")

# Load Surge XT
print("Cargando Surge XT...")
surge_path = "C:/Program Files/Common Files/VST3/Surge Synth Team/Surge XT.vst3/Contents/x86_64-win/Surge XT.vst3"
surge = load_plugin(surge_path)
print(f"  Loaded: {surge.name}")


def configure_kranchdd(plugin, preset):
    """Configure KranchDD with a preset dict"""
    for key, val in preset.items():
        if hasattr(plugin, key):
            setattr(plugin, key, val)


def process_stem(audio_L, audio_R, plugin, preset, name=""):
    """Process a stereo stem through KranchDD"""
    print(f"  Procesando {name}...")
    configure_kranchdd(plugin, preset)

    # Pedalboard expects (channels, samples) float32
    stereo = np.array([audio_L, audio_R], dtype=np.float32)

    # Normalize input to prevent clipping
    peak = np.max(np.abs(stereo))
    if peak > 0:
        stereo = stereo / peak * 0.8

    processed = plugin(stereo, SR)

    # If output is silent (plugin might need different settings), blend with dry
    out_peak = np.max(np.abs(processed))
    if out_peak < 0.001:
        print(f"    Warning: output very quiet, blending with dry signal")
        processed = stereo * 0.5  # fallback to dry

    return processed[0], processed[1]


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

def ws(s, a=2):
    return np.tanh(s*a)/np.tanh(a)


# ============================================================
# STEP 1: Generate v7 stems (run the engine)
# ============================================================
print("\n--- Generando stems v7 ---")
print("Ejecutando engine v7...")

# Import and run v7 engine by executing the script and capturing the arrays
# Instead, let's read the existing v7 output and also generate fresh stems
# Actually, let's re-generate from v7 but save individual stems

# Check if v7 stems exist, if not we'll work with the full mix
v7_path = os.path.join(OUTPUT_DIR, "DarkPsy_v7_MUSICAL_DROPS.wav")
if not os.path.exists(v7_path):
    print("ERROR: v7 no encontrado. Ejecuta synth_darkpsy_v7.py primero.")
    sys.exit(1)

sr, data = wavfile.read(v7_path)
full_L = data[:, 0].astype(np.float64) / 32767.0
full_R = data[:, 1].astype(np.float64) / 32767.0
total_samples = len(full_L)
duration = total_samples / sr

print(f"  v7 cargado: {duration:.1f}s, stereo")

# ============================================================
# STEP 2: Split into frequency bands for targeted processing
# ============================================================
print("\n--- Separando por bandas de frecuencia ---")

# Sub/Kick band (20-100Hz)
sub_L = _lp(full_L, 100)
sub_R = _lp(full_R, 100)
print("  Sub (20-100Hz) extracted")

# Bass band (100-400Hz)
bass_L = _bp(full_L, 100, 400)
bass_R = _bp(full_R, 100, 400)
print("  Bass (100-400Hz) extracted")

# Low-Mid band (400-1500Hz)
lowmid_L = _bp(full_L, 400, 1500)
lowmid_R = _bp(full_R, 400, 1500)
print("  Low-Mid (400-1500Hz) extracted")

# Mid band (1500-5000Hz)
mid_L = _bp(full_L, 1500, 5000)
mid_R = _bp(full_R, 1500, 5000)
print("  Mid (1500-5000Hz) extracted")

# High band (5000-20000Hz)
high_L = _hp(full_L, 5000)
high_R = _hp(full_R, 5000)
print("  High (5000+Hz) extracted")


# ============================================================
# STEP 3: KranchDD presets per band
# ============================================================
print("\n--- Procesando cada banda con KranchDD ---")

# KICK/SUB: Light saturation, keep it clean but add harmonics
kick_preset = {
    'flt': 200.0,       # filter at 200Hz
    'dst': 0.15,        # light distortion
    'mix': 0.3,         # 30% wet
    'qm': 2.0,          # low resonance
    'morph': 0.1,
    'feedback': 0.0,
    'inn': 1.5,          # input gain
    'ouu': 1.0,          # output
    'wtf': 0.0,          # no chaos on kick
    'type': 2.0,         # distortion type 2
    'chain': 0.0,
    'clip': 0.3,         # light clipping
    'overx': 1.0,        # oversampling on
    'bypass': False,
}
sub_proc_L, sub_proc_R = process_stem(sub_L, sub_R, kranchdd, kick_preset, "Kick/Sub")

# BASS: Heavy distortion + filter resonance — the dark psy character
bass_preset = {
    'flt': 800.0,        # filter at 800Hz — lets harmonics through
    'dst': 0.6,          # heavy distortion!
    'mix': 0.5,          # 50% wet
    'qm': 8.0,           # high resonance!
    'morph': 0.4,
    'feedback': 0.2,     # some feedback for grit
    'inn': 2.5,          # drive the input
    'ouu': 0.8,
    'wtf': 0.1,          # tiny bit of chaos
    'type': 4.0,         # different distortion character
    'chain': 1.0,        # filter before distortion
    'clip': 0.5,
    'overx': 1.0,
    'bypass': False,
}
bass_proc_L, bass_proc_R = process_stem(bass_L, bass_R, kranchdd, bass_preset, "Bass")

# LOW-MIDS: Medium distortion + morphing — adds body and movement
lowmid_preset = {
    'flt': 2000.0,
    'dst': 0.4,
    'mix': 0.45,
    'qm': 5.0,
    'morph': 0.6,        # more morphing for movement
    'feedback': 0.15,
    'inn': 2.0,
    'ouu': 0.9,
    'wtf': 0.15,
    'type': 6.0,
    'chain': 1.0,
    'clip': 0.3,
    'overx': 1.0,
    'bypass': False,
}
lowmid_proc_L, lowmid_proc_R = process_stem(lowmid_L, lowmid_R, kranchdd, lowmid_preset, "Low-Mid")

# MIDS: Aggressive — FM textures, acid, electricity. This is where dark psy lives
mid_preset = {
    'flt': 5000.0,
    'dst': 0.7,          # aggressive!
    'mix': 0.55,
    'qm': 12.0,          # very resonant!
    'morph': 0.8,
    'feedback': 0.3,     # feedback for alien character
    'inn': 3.0,          # hot input
    'ouu': 0.7,
    'wtf': 0.3,          # chaos in the mids
    'type': 8.0,         # different distortion mode
    'chain': 2.0,        # different chain order
    'clip': 0.6,
    'overx': 1.0,
    'bypass': False,
}
mid_proc_L, mid_proc_R = process_stem(mid_L, mid_R, kranchdd, mid_preset, "Mid (FM/Acid/Electricity)")

# HIGHS: Moderate — hats, presence. Don't destroy them
high_preset = {
    'flt': 12000.0,
    'dst': 0.2,
    'mix': 0.25,
    'qm': 3.0,
    'morph': 0.2,
    'feedback': 0.05,
    'inn': 1.2,
    'ouu': 1.0,
    'wtf': 0.05,
    'type': 1.0,
    'chain': 0.0,
    'clip': 0.2,
    'overx': 1.0,
    'bypass': False,
}
high_proc_L, high_proc_R = process_stem(high_L, high_R, kranchdd, high_preset, "Highs")


# ============================================================
# STEP 4: Second pass — process the full mix through KranchDD
# with subtle settings for overall "glue"
# ============================================================
print("\n--- Recombinando bandas ---")

mix_L = (sub_proc_L * 0.90 +
         bass_proc_L * 0.85 +
         lowmid_proc_L * 0.80 +
         mid_proc_L * 0.70 +
         high_proc_L * 0.65).astype(np.float64)

mix_R = (sub_proc_R * 0.90 +
         bass_proc_R * 0.85 +
         lowmid_proc_R * 0.80 +
         mid_proc_R * 0.70 +
         high_proc_R * 0.65).astype(np.float64)

# GLUE pass: very subtle KranchDD on the full mix
print("\n--- Glue pass (KranchDD sutil en full mix) ---")
glue_preset = {
    'flt': 8000.0,
    'dst': 0.12,
    'mix': 0.2,
    'qm': 2.0,
    'morph': 0.1,
    'feedback': 0.0,
    'inn': 1.2,
    'ouu': 1.0,
    'wtf': 0.02,
    'type': 3.0,
    'chain': 0.0,
    'clip': 0.15,
    'overx': 1.0,
    'bypass': False,
}
mix_L, mix_R = process_stem(mix_L, mix_R, kranchdd, glue_preset, "Glue pass")

# ============================================================
# STEP 5: Mastering
# ============================================================
print("\n--- Masterizando ---")

mix_L = mix_L.astype(np.float64)
mix_R = mix_R.astype(np.float64)

# HPF
mix_L = _hp(mix_L, 25)
mix_R = _hp(mix_R, 25)

# Tame sub
sL = _lp(mix_L, 60)
sR = _lp(mix_R, 60)
mix_L -= sL * 0.25
mix_R -= sR * 0.25

# Boost low-mids slightly (KranchDD may have altered the balance)
m1L = _bp(mix_L, 200, 600)
m1R = _bp(mix_R, 200, 600)
mix_L += m1L * 0.2
mix_R += m1R * 0.2

# Boost presence
pL = _bp(mix_L, 2000, 6000)
pR = _bp(mix_R, 2000, 6000)
mix_L += pL * 0.15
mix_R += pR * 0.15

# Soft saturation
mix_L = ws(mix_L, 1.5)
mix_R = ws(mix_R, 1.5)

# Normalize
pk = max(np.max(np.abs(mix_L)), np.max(np.abs(mix_R)))
if pk > 0:
    mix_L /= pk
    mix_R /= pk

# Target RMS
rms = np.sqrt(np.mean(mix_L**2 + mix_R**2) / 2)
tgt = 10**(-9.0/20)
if rms > 0:
    g = min(tgt/rms, 3.0)
    mix_L *= g
    mix_R *= g

mix_L = np.clip(mix_L, -0.98, 0.98)
mix_R = np.clip(mix_R, -0.98, 0.98)

# ============================================================
# SAVE
# ============================================================
print("\nGuardando...")
stereo = np.column_stack([
    (mix_L * 32767).astype(np.int16),
    (mix_R * 32767).astype(np.int16)
])

output = os.path.join(OUTPUT_DIR, "DarkPsy_v8_KINDZADZA.wav")
wavfile.write(output, SR, stereo)

import shutil
desktop = "C:/Users/Juan/Desktop/DarkPsy_v8_KINDZADZA.wav"
shutil.copy2(output, desktop)

# Verification
print("\n--- Verificacion ---")
mc = (mix_L + mix_R) / 2
fft_c = np.abs(np.fft.rfft(mc))
freqs_c = np.fft.rfftfreq(len(mc), 1/SR)
te = np.sum(fft_c**2)
for nm, lo, hi in [('Sub',20,60),('Bass',60,200),('LowMid',200,600),('Mid',600,2000),
                    ('HiMid',2000,6000),('Pres',6000,10000),('Air',10000,20000)]:
    mask = (freqs_c>=lo) & (freqs_c<hi)
    pct = np.sum(fft_c[mask]**2)/te*100
    print(f'  {nm:8s}: {pct:5.1f}%')

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
print(f'  Entropia: {np.mean(ents):.2f} bits (target: ~12.5)')

# Compare with v7
print("\n--- Comparacion v7 vs v8 ---")
v7_mono = (full_L + full_R) / 2
fft_v7 = np.abs(np.fft.rfft(v7_mono))
freqs_v7 = np.fft.rfftfreq(len(v7_mono), 1/SR)
te_v7 = np.sum(fft_v7**2)
print(f"  {'Banda':8s}  {'v7':>6s}  {'v8':>6s}  {'Diff':>6s}")
for nm, lo, hi in [('Sub',20,60),('Bass',60,200),('LowMid',200,600),('Mid',600,2000),
                    ('HiMid',2000,6000),('Pres',6000,10000),('Air',10000,20000)]:
    mask7 = (freqs_v7>=lo) & (freqs_v7<hi)
    mask8 = (freqs_c>=lo) & (freqs_c<hi)
    p7 = np.sum(fft_v7[mask7]**2)/te_v7*100
    p8 = np.sum(fft_c[mask8]**2)/te*100
    diff = p8 - p7
    arrow = "+" if diff > 0 else ""
    print(f'  {nm:8s}  {p7:5.1f}%  {p8:5.1f}%  {arrow}{diff:5.1f}%')

print(f"\n{'='*60}")
print(f" TRACK: {desktop}")
print(f" Procesado con KranchDD de Kindzadza")
print(f" Bass: heavy dist + resonance | Mids: aggressive + chaos")
print(f" Highs: clean | Glue: sutil cohesion")
print(f"{'='*60}")
