# -*- coding: utf-8 -*-
"""
Full track with the chaos-driven FM wired in.

Reuses the existing Surge-rendered stems (stems_v9: kick/bass/lead/acid/pad/fx/drums)
and REPLACES the old static fm_texture with the new chaos-driven FM (fm_chaos.py),
then mixes + masters. Fast (no Surge re-render) — so you can hear the FM morph
ORDER->CHAOS across the whole track.

Run:  python forja/render_full_fm.py
"""
import os, sys
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fm_chaos
import automix
import arrangement
from grammar import G

if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STEMS = os.path.join(REPO, "stems_v9")
OUT = os.path.join(REPO, "forja", "recreation_out", "DarkPsy_chaosFM.wav")
os.makedirs(os.path.dirname(OUT), exist_ok=True)
SR = 44100

REF = "glosolalia_blueprints"
if "--ref" in sys.argv:
    REF = sys.argv[sys.argv.index("--ref") + 1]   # e.g. --ref darkpsy_consensus
GROWL_AMOUNT = 2.0   # bass growl-band saturation -> harmonics fill the lowmid
STEM_ORDER = ["kick", "bass", "acid", "drums", "lead", "pad", "fx"]
FM_CACHE = os.path.join(REPO, "forja", "recreation_out", "fm_stem_cache.npy")

def read(path):
    sr, d = wavfile.read(path)
    if d.ndim == 1: d = np.column_stack([d, d])
    if d.dtype == np.int16: d = d.astype(np.float64) / 32768.0
    elif d.dtype == np.int32: d = d.astype(np.float64) / 2147483648.0
    return d

print("=" * 56); print(" FULL TRACK + chaos-driven FM  (automix vs referencia)"); print("=" * 56)

# length from kick stem
ref = read(os.path.join(STEMS, "kick.wav"))
N = len(ref)

# chaos FM stem first (the solver needs to see it); cached for fast iteration
nbars = int(N / SR / fm_chaos.BAR)
if os.path.exists(FM_CACHE) and "--fresh-fm" not in sys.argv:
    print(f"  FM chaos-driven: cache ({FM_CACHE})")
    fm = np.load(FM_CACHE); fL, fR = fm[0].astype(np.float64), fm[1].astype(np.float64)
else:
    print(f"  generando FM chaos-driven ({nbars} bars)...")
    fL, fR = fm_chaos.render_fm_stem(nbars, gate=True)
    fpk = max(np.max(np.abs(fL)), np.max(np.abs(fR))) + 1e-9
    fL = fL / fpk; fR = fR / fpk
    np.save(FM_CACHE, np.stack([fL, fR]).astype(np.float32))

# solve faders vs the measured reference profile (kick locked = genre anchor)
print("  automix: resolviendo faders vs perfil de referencia...")
gains, pred, err = automix.calibrate(STEMS, fm_lr=(fL, fR), ref_name=REF, save=True)
print("    " + "  ".join(f"{k}:{v}" for k, v in gains.items()))

# the variation engine: fills, energy staircase, build sweeps, impacts, micro-silence
plan = arrangement.make_plan(nbars, fm_chaos.sec, seed=4)
ht_bars = [b for b in range(nbars) if fm_chaos.hitech_at(b) > 0.02]
print(f"  arrangement: {len(plan['fill_bars'])} fills, {len(plan['impact_bars'])} impactos, "
      f"{len(plan['build_hp'])} bars de build, {len(plan['micro_silence'])} micro-silencios")
if ht_bars:
    print(f"  momento hitech: bars {ht_bars[0]}-{ht_bars[-1]} "
          f"(peak {max(fm_chaos.hitech_at(b) for b in ht_bars):.2f})")

mL = np.zeros(N); mR = np.zeros(N)
kpL = np.zeros(N); kpR = np.zeros(N)   # PROCESSED kick (fills/build-HP applied) for the sidechain
for name in STEM_ORDER:
    p = os.path.join(STEMS, name + ".wav")
    if not os.path.exists(p): print(f"  falta {name}"); continue
    d = read(p)
    hp_fc = G["mix"].get("highpass_hz", {}).get(name)
    if hp_fc:   # disciplina del amigo: low-end solo para kick+bass = mezcla amena
        sos = butter(2, hp_fc, btype="high", fs=SR, output="sos")
        d = np.column_stack([sosfilt(sos, d[:, 0]), sosfilt(sos, d[:, 1])])
        print(f"  hp {name} @ {hp_fc} Hz")
    if name == "bass" and GROWL_AMOUNT > 0:
        d = automix.growl_saturate(d, GROWL_AMOUNT)   # harmonics 150-300 -> lowmid body
        print(f"  + growl saturation en bass x{GROWL_AMOUNT}")
    d = arrangement.process_stem(name, d, plan, fm_chaos.BAR)
    d = arrangement.apply_hitech(name, d, fm_chaos.BAR, fm_chaos.hitech_at)
    fad = gains.get(name, 0.5)
    n = min(N, len(d))
    mL[:n] += d[:n, 0] * fad; mR[:n] += d[:n, 1] * fad
    if name == "kick":
        kpL[:n] = d[:n, 0] * fad; kpR[:n] = d[:n, 1] * fad
    print(f"  + {name:6s} x{fad}")
fmst = arrangement.process_stem("fm", np.column_stack([fL, fR]), plan, fm_chaos.BAR)
fmst = arrangement.apply_hitech("fm", fmst, fm_chaos.BAR, fm_chaos.hitech_at)
n = min(N, len(fmst))
mL[:n] += fmst[:n, 0] * gains.get("fm", 0.5); mR[:n] += fmst[:n, 1] * gains.get("fm", 0.5)
print(f"  + fm     x{gains.get('fm', 0.5)} (chaos-driven)")

# sidechain (kick-env duck, parity with v9)
kick = read(os.path.join(STEMS, "kick.wav"))
km = (kick[:N, 0] + kick[:N, 1]) / 2
ke = np.abs(km); w = int(0.03 * SR)
ks = np.convolve(ke, np.ones(w) / w, mode="same"); ks /= (ks.max() + 1e-9)
sc = 1 - ks * 0.15
# duck everything EXCEPT the processed kick (raw kick only feeds the envelope)
mL = kpL + (mL - kpL) * sc; mR = kpR + (mR - kpR) * sc

# mix-level arrangement events (rolls, risers, impacts, the micro-silence weapon)
mix_ev = arrangement.apply_mix_events(np.column_stack([mL, mR]), plan, fm_chaos.BAR)
mL, mR = mix_ev[:, 0], mix_ev[:, 1]

# master: HP -> soft sat -> matching EQ LAST (linear phase; the saturator can't
# undo it) -> normalize. The EQ is the grammar-sanctioned reference-spectrum diff.
def hp(x, fc): return sosfilt(butter(2, fc, btype="high", fs=SR, output="sos"), x)
def ws(x, a=1.4): return np.tanh(x * a) / np.tanh(a)
mL = hp(mL, 28); mR = hp(mR, 28)
mL = ws(mL); mR = ws(mR)
print("  matching EQ vs espectro de referencia...")
mix = np.column_stack([mL, mR])
mix, (frq, corr) = automix.match_eq(mix, REF, alpha=1.0, max_db=12.0)
print(f"    correccion: {corr.min():+.1f}..{corr.max():+.1f} dB")
arrangement.apply_micro_silence(mix, plan, fm_chaos.BAR)   # the weapon survives the EQ
mL, mR = mix[:, 0], mix[:, 1]
pk = max(np.max(np.abs(mL)), np.max(np.abs(mR)))
if pk > 0: mL /= pk; mR /= pk
rms = np.sqrt(np.mean(mL ** 2 + mR ** 2) / 2)
g = min((10 ** (-9.0 / 20)) / (rms + 1e-9), 3.0)
mL = np.clip(mL * g, -0.98, 0.98); mR = np.clip(mR * g, -0.98, 0.98)

wavfile.write(OUT, SR, np.column_stack([(mL * 32767).astype(np.int16), (mR * 32767).astype(np.int16)]))
print(f"\n  -> {OUT}  ({N/SR:.0f}s)")
# versioned listening copy (the player locks files; never overwrite what Juan has open)
if "--listen" in sys.argv:
    tag = sys.argv[sys.argv.index("--listen") + 1]
    import shutil
    dst = os.path.join(os.path.expanduser("~"), "Desktop", f"DarkPsy_{tag}.wav")
    shutil.copy2(OUT, dst)
    print(f"  -> copia para escuchar: {dst}")

# the gates judge the render before Juan's ears do
import verify
results = verify.run_gates(OUT, bpm=G["tempo"]["default_bpm"], ref=REF)
for name, ok, detail in results:
    print(f"  [{'PASS' if ok else 'FAIL'}]  {name:8s} {detail}")
