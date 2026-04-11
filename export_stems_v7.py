"""
Export individual stems from v7 engine for Reaper live tweaking.
Each stem saved as separate stereo WAV.
"""
import numpy as np
from scipy.io import wavfile
import os, sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stems_v7")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# We need to re-run v7's synthesis but capture each stem individually.
# Import the v7 module by executing it with modifications.
# Instead, let's just exec the v7 file up to the render section and grab the arrays.

print("=" * 60)
print(" Exportando stems individuales de v7")
print("=" * 60)

# Execute v7 engine
v7_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "synth_darkpsy_v7.py")
print(f"\nEjecutando engine v7...")

# We'll capture the stem variables by exec-ing the v7 script
v7_globals = {'__file__': v7_path, '__name__': '__main__'}
with open(v7_path, 'r') as f:
    code = f.read()

# Remove the shutil copy and desktop save to avoid issues
code = code.replace("shutil.copy2(output, desktop)", "pass")

exec(code, v7_globals)

# Now extract stems from v7's namespace
stems = [
    ("01_kick", v7_globals.get('kick_L'), v7_globals.get('kick_R')),
    ("02_bass", v7_globals.get('bass_L'), v7_globals.get('bass_R')),
    ("03_fm_textures", v7_globals.get('fm_L'), v7_globals.get('fm_R')),
    ("04_electricity", v7_globals.get('elec_L'), v7_globals.get('elec_R')),
    ("05_drums", v7_globals.get('drums_L'), v7_globals.get('drums_R')),
    ("06_lead", v7_globals.get('lead_L'), v7_globals.get('lead_R')),
    ("07_atmosphere", v7_globals.get('atmo_L'), v7_globals.get('atmo_R')),
    ("08_granular", v7_globals.get('gran_L'), v7_globals.get('gran_R')),
    ("09_fx", v7_globals.get('fx_L'), v7_globals.get('fx_R')),
]

SR = 44100
print(f"\nGuardando stems en: {OUTPUT_DIR}")

for name, L, R in stems:
    if L is None or R is None:
        print(f"  SKIP {name} (not found)")
        continue

    # Normalize
    pk = max(np.max(np.abs(L)), np.max(np.abs(R)), 1e-10)
    L_norm = L / pk * 0.9
    R_norm = R / pk * 0.9

    stereo = np.column_stack([
        (L_norm * 32767).astype(np.int16),
        (R_norm * 32767).astype(np.int16)
    ])

    path = os.path.join(OUTPUT_DIR, f"{name}.wav")
    wavfile.write(path, SR, stereo)
    dur = len(L) / SR
    print(f"  {name}.wav ({dur:.1f}s)")

print(f"\n{len([s for s in stems if s[1] is not None])} stems exportados")
print("Listo!")
