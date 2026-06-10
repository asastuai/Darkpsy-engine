# -*- coding: utf-8 -*-
"""
AUTOMIX — solve stem faders mathematically instead of guessing by ear.

Model: each stem i contributes band power g_i^2 * B[i][band] (stems ~uncorrelated),
so the mix profile is p_b(g) = sum_i g_i^2 B_ib / total. We minimize the squared
error against a measured reference profile from grammar.json (e.g. the real
Glosolalia Blueprints numbers) with the KICK LOCKED (genre anchor: the kick is
the loudest single element — we balance everything else around it).

Also provides growl_saturate(): multiband saturation on the bass growl band
(150-300 Hz) that generates harmonics into the hollow lowmid — the
grammar-sanctioned way to add 250-800 Hz body without touching the sub.

Used by render_full_fm.py; runnable standalone to just print the solution:
  python forja/automix.py
"""
import os, sys
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt, welch
from scipy.optimize import minimize

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import grammar
from grammar import G

SR = 44100
BANDS = G["verify"]["bands_hz"]


def read_mono(path):
    sr, d = wavfile.read(path)
    if d.ndim == 2:
        d = d.mean(axis=1)
    if d.dtype == np.int16:
        d = d.astype(np.float32) / 32768.0
    elif d.dtype == np.int32:
        d = d.astype(np.float32) / 2147483648.0
    return d.astype(np.float32)


def band_powers(mono):
    """Raw power per grammar band (not normalized) at gain=1."""
    f, pxx = welch(mono, fs=SR, nperseg=8192)
    return np.array([pxx[(f >= lo) & (f < hi)].sum() for lo, hi in BANDS.values()])


def solve_gains(stem_powers, ref_profile, locked=None, x0=None, bounds=(0.05, 1.4)):
    """stem_powers: dict name -> band power vector. locked: dict name -> fixed gain.
    Returns dict name -> gain minimizing the profile error vs ref_profile."""
    locked = locked or {}
    names = list(stem_powers.keys())
    free = [n for n in names if n not in locked]
    Bm = np.array([stem_powers[n] for n in names])           # (n_stems, n_bands)
    ref = np.array([ref_profile[b] for b in BANDS])

    def gains_vec(x):
        g = np.empty(len(names))
        xi = 0
        for j, n in enumerate(names):
            if n in locked:
                g[j] = locked[n]
            else:
                g[j] = x[xi]; xi += 1
        return g

    def loss(x):
        g = gains_vec(x)
        p = (g[:, None] ** 2 * Bm).sum(axis=0)
        p = p / (p.sum() + 1e-18)
        return float(((p - ref) ** 2).sum())

    x0v = np.array(x0 if x0 is not None else [0.6] * len(free))
    res = minimize(loss, x0v, method="L-BFGS-B",
                   bounds=[bounds] * len(free), options={"maxiter": 500})
    g = gains_vec(res.x)
    p = (g[:, None] ** 2 * Bm).sum(axis=0); p = p / p.sum()
    sol = {n: round(float(g[j]), 3) for j, n in enumerate(names)}
    pred = {b: round(float(p[k]), 4) for k, b in enumerate(BANDS)}
    return sol, pred, float(res.fun)


def smooth_spectrum(mono, n_points=120, f_lo=30.0, f_hi=20000.0):
    """Smoothed log-spaced power spectrum (dB, normalized to 0 dB mean).
    Small enough to store as NUMBERS in grammar.json — never the audio."""
    f, pxx = welch(mono, fs=SR, nperseg=16384)
    fr = np.geomspace(f_lo, f_hi, n_points)
    p = np.interp(fr, f, pxx)
    # ~1/6-octave smoothing in log domain
    k = 5
    p = np.convolve(np.pad(p, k, mode="edge"), np.ones(2 * k + 1) / (2 * k + 1), mode="same")[k:-k]
    db = 10 * np.log10(p + 1e-18)
    return fr, db - db.mean()


def learn_ref_spectrum(path, ref_name="glosolalia_blueprints"):
    """Measure the reference's smoothed spectrum into grammar.json."""
    fr, db = smooth_spectrum(read_mono(path))
    G["reference_profiles"][ref_name]["spectrum"] = {
        "freqs": [round(float(x), 1) for x in fr],
        "db": [round(float(x), 2) for x in db],
    }
    grammar.save()
    return fr, db


def match_eq(stereo, ref_name="glosolalia_blueprints", alpha=0.8, max_db=9.0):
    """Linear-phase matching EQ: pull the mix's smoothed spectrum toward the
    measured reference curve (the grammar-sanctioned master move). alpha scales
    the correction; max_db caps it so it stays an EQ, not surgery."""
    spec = G["reference_profiles"][ref_name].get("spectrum")
    if not spec:
        raise RuntimeError("falta el espectro de referencia — corré learn_ref_spectrum")
    fr_ref = np.array(spec["freqs"]); db_ref = np.array(spec["db"])
    fr_mix, db_mix = smooth_spectrum(((stereo[:, 0] + stereo[:, 1]) / 2).astype(np.float32))
    corr_db = np.clip((np.interp(fr_mix, fr_ref, db_ref) - db_mix) * alpha, -max_db, max_db)
    n = stereo.shape[0]
    f_bins = np.fft.rfftfreq(n, 1.0 / SR)
    gain = 10 ** (np.interp(f_bins, fr_mix, corr_db, left=corr_db[0], right=corr_db[-1]) / 20)
    out = np.empty_like(stereo)
    for ch in range(stereo.shape[1]):
        out[:, ch] = np.fft.irfft(np.fft.rfft(stereo[:, ch]) * gain, n)
    return out, (fr_mix, corr_db)


def growl_saturate(stereo, amount, lo=150, hi=300, drive=4.0):
    """Saturate ONLY the growl band and mix the generated harmonics back in.
    Harmonics of 150-300 Hz land at 300-900+ Hz -> fills the lowmid body."""
    if amount <= 0:
        return stereo
    sos = butter(2, [lo, hi], btype="band", fs=SR, output="sos")
    out = stereo.copy()
    for ch in range(stereo.shape[1]):
        band = sosfilt(sos, stereo[:, ch])
        sat = np.tanh(band * drive) / np.tanh(drive)
        out[:, ch] += amount * (sat - band)   # add only the NEW harmonics
    return out


def calibrate(stems_dir, fm_lr=None, ref_name="glosolalia_blueprints",
              locked_kick=0.9, save=True):
    """Measure all stems, solve faders vs the reference, optionally persist the
    solution into grammar.json mix.stem_gains. fm_lr: (L, R) float arrays of the
    generated FM stem (normalized) so the solver sees it too."""
    ref = G["reference_profiles"][ref_name]["bands"]
    files = ["kick.wav", "bass.wav", "acid.wav", "drums.wav",
             "lead.wav", "pad.wav", "fx.wav"]
    powers = {}
    for f in files:
        p = os.path.join(stems_dir, f)
        if os.path.exists(p):
            powers[f.replace(".wav", "")] = band_powers(read_mono(p))
    if fm_lr is not None:
        powers["fm"] = band_powers(((fm_lr[0] + fm_lr[1]) / 2).astype(np.float32))
    sol, pred, err = solve_gains(powers, ref, locked={"kick": locked_kick})
    if save:
        G["mix"]["stem_gains"] = sol
        G["mix"]["stem_gains_ref"] = ref_name
        grammar.save()
    return sol, pred, err


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")
    REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("midiendo stems + resolviendo faders vs referencia...")
    sol, pred, err = calibrate(os.path.join(REPO, "stems_v9"), save="--save" in sys.argv)
    ref = G["reference_profiles"]["glosolalia_blueprints"]["bands"]
    print("\n  faders resueltos:")
    for n, g in sol.items():
        print(f"    {n:6s} {g}")
    print("\n  banda    objetivo  predicho")
    for b in BANDS:
        print(f"    {b:7s} {ref[b]*100:5.1f}%    {pred[b]*100:5.1f}%")
    print(f"\n  error: {err:.5f}  (--save para escribirlo en grammar.json)")
