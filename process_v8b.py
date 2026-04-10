"""
v8b — KranchDD processing with corrected settings.
Issue in v8: KranchDD was filtering too aggressively, killing the signal.
Fix: higher filter, more dry signal, compensate gain, parallel processing.
"""
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt
from pedalboard import load_plugin
import os, sys, shutil

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
SR = 44100

print("=" * 60)
print(" DARK PSYTRANCE v8b - KINDZADZA PROCESSED (corrected)")
print("=" * 60)

kranchdd = load_plugin("C:/Program Files/Common Files/VST3/KINDZAudio/KranchDD.vst3")
print(f"  KranchDD loaded")

def _lp(s,fc,o=4):
    return sosfilt(butter(o,np.clip(fc,20,SR/2-100),btype='low',fs=SR,output='sos'),s)
def _hp(s,fc,o=2):
    return sosfilt(butter(o,np.clip(fc,20,SR/2-100),btype='high',fs=SR,output='sos'),s)
def _bp(s,lo,hi,o=2):
    lo,hi=max(lo,20),min(hi,SR/2-100)
    if lo>=hi: return s
    return sosfilt(butter(o,[lo,hi],btype='band',fs=SR,output='sos'),s)
def ws(s,a=2): return np.tanh(s*a)/np.tanh(a)

def process_parallel(audio_L, audio_R, plugin, preset, wet_amount=0.5, name=""):
    """Parallel processing: blend dry + wet to preserve signal"""
    print(f"  {name}...")

    # Configure
    for key, val in preset.items():
        if hasattr(plugin, key):
            setattr(plugin, key, val)

    # Prepare input
    stereo = np.array([audio_L.astype(np.float32), audio_R.astype(np.float32)])
    peak = np.max(np.abs(stereo))
    if peak > 0:
        stereo_norm = stereo / peak * 0.7
    else:
        return audio_L, audio_R

    # Process
    wet = plugin(stereo_norm, SR)

    # Compensate wet gain
    wet_peak = np.max(np.abs(wet))
    if wet_peak > 0.001:
        wet = wet / wet_peak * peak * 0.7
    else:
        print(f"    Wet signal too quiet, using dry only")
        return audio_L, audio_R

    # Parallel blend: dry + wet
    dry = stereo_norm * peak / 0.7  # restore original level
    out = dry * (1 - wet_amount) + wet * wet_amount

    return out[0].astype(np.float64), out[1].astype(np.float64)


# Load v7
print("\nCargando v7...")
sr, data = wavfile.read(os.path.join(OUTPUT_DIR, "DarkPsy_v7_MUSICAL_DROPS.wav"))
full_L = data[:, 0].astype(np.float64) / 32767.0
full_R = data[:, 1].astype(np.float64) / 32767.0
print(f"  {len(full_L)/sr:.1f}s stereo")

# Split into bands
print("\nSeparando bandas...")
sub_L, sub_R = _lp(full_L, 100), _lp(full_R, 100)
bass_L, bass_R = _bp(full_L, 100, 500), _bp(full_R, 100, 500)
mid_L, mid_R = _bp(full_L, 500, 4000), _bp(full_R, 500, 4000)
high_L, high_R = _hp(full_L, 4000), _hp(full_R, 4000)

# Process each band through KranchDD with PARALLEL blending
print("\nProcesando con KranchDD (parallel blend)...")

# SUB: barely touch it — keep the kick clean
sub_proc_L, sub_proc_R = process_parallel(
    sub_L, sub_R, kranchdd,
    {'flt': 15000.0, 'dst': 0.08, 'mix': 1.0, 'qm': 1.0, 'morph': 0.0,
     'feedback': 0.0, 'inn': 1.0, 'ouu': 1.0, 'wtf': 0.0, 'type': 0.0,
     'chain': 0.0, 'clip': 0.1, 'overx': 1.0, 'bypass': False},
    wet_amount=0.15, name="Sub (light saturation)")

# BASS: the star — distortion + resonance for dark psy character
bass_proc_L, bass_proc_R = process_parallel(
    bass_L, bass_R, kranchdd,
    {'flt': 4000.0, 'dst': 0.55, 'mix': 1.0, 'qm': 6.0, 'morph': 0.3,
     'feedback': 0.15, 'inn': 2.0, 'ouu': 1.0, 'wtf': 0.05, 'type': 4.0,
     'chain': 1.0, 'clip': 0.4, 'overx': 1.0, 'bypass': False},
    wet_amount=0.45, name="Bass (heavy character)")

# MIDS: aggressive for FM/acid textures
mid_proc_L, mid_proc_R = process_parallel(
    mid_L, mid_R, kranchdd,
    {'flt': 8000.0, 'dst': 0.65, 'mix': 1.0, 'qm': 10.0, 'morph': 0.6,
     'feedback': 0.25, 'inn': 2.5, 'ouu': 0.9, 'wtf': 0.2, 'type': 7.0,
     'chain': 2.0, 'clip': 0.5, 'overx': 1.0, 'bypass': False},
    wet_amount=0.5, name="Mids (aggressive alien)")

# HIGHS: gentle presence boost
high_proc_L, high_proc_R = process_parallel(
    high_L, high_R, kranchdd,
    {'flt': 16000.0, 'dst': 0.15, 'mix': 1.0, 'qm': 2.0, 'morph': 0.1,
     'feedback': 0.0, 'inn': 1.3, 'ouu': 1.0, 'wtf': 0.0, 'type': 1.0,
     'chain': 0.0, 'clip': 0.15, 'overx': 1.0, 'bypass': False},
    wet_amount=0.2, name="Highs (gentle)")

# Recombine
print("\nRecombinando...")
mix_L = sub_proc_L + bass_proc_L + mid_proc_L + high_proc_L
mix_R = sub_proc_R + bass_proc_R + mid_proc_R + high_proc_R

# SECOND PASS: full mix through KranchDD for "glue"
print("\nGlue pass...")
mix_L, mix_R = process_parallel(
    mix_L, mix_R, kranchdd,
    {'flt': 12000.0, 'dst': 0.1, 'mix': 1.0, 'qm': 1.5, 'morph': 0.05,
     'feedback': 0.0, 'inn': 1.1, 'ouu': 1.0, 'wtf': 0.01, 'type': 2.0,
     'chain': 0.0, 'clip': 0.1, 'overx': 1.0, 'bypass': False},
    wet_amount=0.15, name="Glue (cohesion)")

# THIRD PASS: process just the mids of the full mix for extra presence
print("\nMid presence boost...")
mix_mid_L = _bp(mix_L, 600, 3000)
mix_mid_R = _bp(mix_R, 600, 3000)
mid_boost_L, mid_boost_R = process_parallel(
    mix_mid_L, mix_mid_R, kranchdd,
    {'flt': 6000.0, 'dst': 0.4, 'mix': 1.0, 'qm': 4.0, 'morph': 0.3,
     'feedback': 0.1, 'inn': 2.0, 'ouu': 1.0, 'wtf': 0.1, 'type': 5.0,
     'chain': 1.0, 'clip': 0.3, 'overx': 1.0, 'bypass': False},
    wet_amount=0.6, name="Mid presence")
mix_L += mid_boost_L * 0.3
mix_R += mid_boost_R * 0.3

# Master
print("\nMasterizando...")
mix_L = _hp(mix_L, 25); mix_R = _hp(mix_R, 25)

# Tame sub
sL = _lp(mix_L, 60); sR = _lp(mix_R, 60)
mix_L -= sL * 0.2; mix_R -= sR * 0.2

# Final saturation
mix_L = ws(mix_L, 1.6); mix_R = ws(mix_R, 1.6)

# Normalize
pk = max(np.max(np.abs(mix_L)), np.max(np.abs(mix_R)))
if pk > 0: mix_L /= pk; mix_R /= pk

# Target RMS
rms = np.sqrt(np.mean(mix_L**2 + mix_R**2) / 2)
tgt = 10**(-9.0/20)
if rms > 0:
    g = min(tgt/rms, 3.0)
    mix_L *= g; mix_R *= g

mix_L = np.clip(mix_L, -0.98, 0.98)
mix_R = np.clip(mix_R, -0.98, 0.98)

# Save
print("\nGuardando...")
stereo = np.column_stack([(mix_L*32767).astype(np.int16), (mix_R*32767).astype(np.int16)])
output = os.path.join(OUTPUT_DIR, "DarkPsy_v8_KINDZADZA.wav")
wavfile.write(output, SR, stereo)
desktop = "C:/Users/Juan/Desktop/DarkPsy_v8_KINDZADZA.wav"
shutil.copy2(output, desktop)

# Verify
print("\n--- Verificacion ---")
mc = (mix_L + mix_R) / 2
fft_c = np.abs(np.fft.rfft(mc)); freqs_c = np.fft.rfftfreq(len(mc), 1/SR)
te = np.sum(fft_c**2)

# Compare v7 vs v8
v7_mono = (full_L + full_R) / 2
fft_v7 = np.abs(np.fft.rfft(v7_mono)); freqs_v7 = np.fft.rfftfreq(len(v7_mono), 1/SR)
te_v7 = np.sum(fft_v7**2)

print(f"  {'Banda':8s}  {'v7':>6s}  {'v8':>6s}  {'Gloso':>6s}")
gloso_targets = {'Sub':13,'Bass':54,'LowMid':17,'Mid':9,'HiMid':3.8,'Pres':1.5,'Air':0.8}
for nm,lo,hi in [('Sub',20,60),('Bass',60,200),('LowMid',200,600),('Mid',600,2000),
                  ('HiMid',2000,6000),('Pres',6000,10000),('Air',10000,20000)]:
    m7 = (freqs_v7>=lo)&(freqs_v7<hi)
    m8 = (freqs_c>=lo)&(freqs_c<hi)
    p7 = np.sum(fft_v7[m7]**2)/te_v7*100
    p8 = np.sum(fft_c[m8]**2)/te*100
    gt = gloso_targets[nm]
    print(f'  {nm:8s}  {p7:5.1f}%  {p8:5.1f}%  {gt:5.1f}%')

rms_f = np.sqrt(np.mean(mc**2))
print(f'\n  RMS: {20*np.log10(rms_f+1e-10):.1f} dB')

ents = []
for i in range(0, len(mc)-SR, SR):
    f = mc[i:i+SR]; ff = np.abs(np.fft.rfft(f))
    ff = ff/(np.sum(ff)+1e-10); ff = ff[ff>0]
    ents.append(-np.sum(ff*np.log2(ff)))
print(f'  Entropia: {np.mean(ents):.2f} bits')

print(f"\n{'='*60}")
print(f" TRACK: {desktop}")
print(f" v7 + KranchDD parallel processing")
print(f"{'='*60}")
