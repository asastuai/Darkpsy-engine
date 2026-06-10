# -*- coding: utf-8 -*-
"""
VERIFY — quantitative quality gates for every render (the checks we should have
had from day one: the NaN bass and the wrong volumes would never have reached
Juan's ears). All thresholds live in grammar.json["verify"].

Gates:
  finite     no NaN/inf anywhere
  peak       peak dB inside [min, max]
  rms        overall RMS dB inside [min, max]
  dc         DC offset below threshold
  holes      no unintended silence longer than max_silence_s (inside the piece)
  monolow    below mono_below_hz the channels are effectively mono (correlation)
  bands      band energy profile within tolerance of a measured reference profile
  bpm        detected tempo matches the declared one (also checks half/double)

Usage:
  python forja/verify.py track.wav [--bpm 150] [--ref <profile>] [--stem]
  python forja/verify.py --learn-ref <profile> "path\\to\\reference.wav"

--stem relaxes master-only gates (rms range, bands).
--learn-ref measures a band profile from a real track and stores ONLY the
numbers in grammar.json (audio is never copied or committed).
"""
import os
import sys
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt, welch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import grammar
from grammar import G

V = G["verify"]


def load_wav(path):
    sr, d = wavfile.read(path)
    if d.ndim == 1:
        d = np.column_stack([d, d])
    if d.dtype == np.int16:
        d = d.astype(np.float64) / 32768.0
    elif d.dtype == np.int32:
        d = d.astype(np.float64) / 2147483648.0
    else:
        d = d.astype(np.float64)
    return sr, d


def band_profile(mono, sr):
    """Energy fraction per grammar band (sums to 1 over the defined bands)."""
    f, pxx = welch(mono, fs=sr, nperseg=8192)
    out = {}
    for name, (lo, hi) in V["bands_hz"].items():
        out[name] = float(pxx[(f >= lo) & (f < hi)].sum())
    tot = sum(out.values()) + 1e-18
    return {k: round(v / tot, 4) for k, v in out.items()}


def _db(x):
    return 20 * np.log10(x + 1e-12)


def run_gates(path, bpm=None, ref=None, stem=False):
    sr, d = load_wav(path)
    mono = d.mean(axis=1)
    n = len(mono)
    results = []  # (gate, ok, detail)

    def gate(name, ok, detail):
        results.append((name, bool(ok), detail))

    # finite
    finite = np.isfinite(d).all()
    gate("finite", finite, "sin NaN/inf" if finite else "HAY NaN/inf — render roto")
    if not finite:
        d = np.nan_to_num(d); mono = d.mean(axis=1)

    # peak
    pk = _db(np.abs(d).max())
    lo, hi = V["peak_db"]
    gate("peak", lo <= pk <= hi, f"{pk:.1f} dB (rango {lo}..{hi})")

    # rms
    rms = _db(np.sqrt((mono ** 2).mean()))
    lo, hi = V["rms_db"]
    gate("rms", (lo <= rms <= hi) or stem, f"{rms:.1f} dB (rango {lo}..{hi})" + (" [stem: informativo]" if stem else ""))

    # dc
    dc = float(np.abs(d.mean(axis=0)).max())
    gate("dc", dc <= V["dc_max"], f"{dc:.4f} (max {V['dc_max']})")

    # holes — longest sub--60dB run strictly inside the piece (lead-in/out excluded)
    win = max(1, sr // 10)
    env = np.array([np.abs(mono[i:i + win]).mean() for i in range(0, n - win, win)])
    on = env > 10 ** (-60 / 20)
    if on.any():
        first, last = np.argmax(on), len(on) - 1 - np.argmax(on[::-1])
        inner = on[first:last + 1]
        longest = run = 0
        for v in inner:
            run = 0 if v else run + 1
            longest = max(longest, run)
        hole_s = longest * win / sr
        gate("holes", hole_s <= V["max_silence_s"],
             f"hueco max {hole_s:.1f}s (max {V['max_silence_s']}s)")
    else:
        gate("holes", False, "el archivo entero es silencio")

    # monolow — correlation of the lowpassed channels
    sos = butter(4, G["mix"]["mono_below_hz"], btype="low", fs=sr, output="sos")
    bl, br = sosfilt(sos, d[:, 0]), sosfilt(sos, d[:, 1])
    denom = np.sqrt((bl ** 2).sum() * (br ** 2).sum()) + 1e-18
    corr = float((bl * br).sum() / denom)
    gate("monolow", corr >= V["mono_below_corr_min"],
         f"corr {corr:.3f} bajo {G['mix']['mono_below_hz']} Hz (min {V['mono_below_corr_min']})")

    # bands vs reference profile
    prof = band_profile(mono, sr)
    if ref:
        rp = G["reference_profiles"].get(ref)
        if not rp:
            gate("bands", False, f"perfil '{ref}' no existe — corré --learn-ref primero")
        else:
            tol = V["band_tolerance"]
            deltas = {k: prof[k] - rp["bands"][k] for k in prof}
            worst = max(deltas, key=lambda k: abs(deltas[k]))
            ok = all(abs(v) <= tol for v in deltas.values()) or stem
            detail = "  ".join(f"{k}:{prof[k]*100:.0f}%({deltas[k]*100:+.0f})" for k in prof)
            gate("bands", ok, f"vs '{ref}' tol ±{tol*100:.0f}%  peor: {worst}  | {detail}")
    else:
        gate("bands", True, "[sin ref] " + "  ".join(f"{k}:{v*100:.0f}%" for k, v in prof.items()))

    # bpm
    if bpm:
        import librosa
        tempo, _ = librosa.beat.beat_track(y=mono.astype(np.float32), sr=sr, start_bpm=bpm)
        det = float(np.atleast_1d(tempo)[0])
        tol = V["bpm_tolerance"]
        ok = any(abs(det * m - bpm) <= tol for m in (1, 2, 0.5))
        gate("bpm", ok, f"detectado {det:.1f} vs declarado {bpm} (tol ±{tol})")

    return results


def learn_ref(name, path):
    sr, d = load_wav(path)
    mono = d.mean(axis=1)
    prof = {
        "bands": band_profile(mono, sr),
        "rms_db": round(float(_db(np.sqrt((mono ** 2).mean()))), 1),
        "peak_db": round(float(_db(np.abs(d).max())), 1),
        "source": os.path.basename(path),
    }
    G["reference_profiles"][name] = prof
    grammar.save()
    print(f"perfil '{name}' guardado en grammar.json (solo numeros, no audio):")
    for k, v in prof["bands"].items():
        print(f"  {k:7s} {v*100:5.1f}%")
    print(f"  rms {prof['rms_db']} dB | peak {prof['peak_db']} dB | fuente: {prof['source']}")


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = sys.argv[1:]
    if not args:
        print(__doc__); sys.exit(2)

    if args[0] == "--learn-ref":
        learn_ref(args[1], args[2]); sys.exit(0)

    path = args[0]
    bpm = ref = None
    stem = "--stem" in args
    if "--bpm" in args: bpm = float(args[args.index("--bpm") + 1])
    if "--ref" in args: ref = args[args.index("--ref") + 1]

    print("=" * 64)
    print(f" VERIFY  {os.path.basename(path)}")
    print("=" * 64)
    results = run_gates(path, bpm=bpm, ref=ref, stem=stem)
    failed = 0
    for name, ok, detail in results:
        mark = "PASS" if ok else "FAIL"
        if not ok: failed += 1
        print(f"  [{mark}]  {name:8s} {detail}")
    print("-" * 64)
    print(f"  {'TODO VERDE' if failed == 0 else f'{failed} GATE(S) ROJOS'}")
    sys.exit(0 if failed == 0 else 1)
