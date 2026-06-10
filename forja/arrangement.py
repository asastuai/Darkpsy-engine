# -*- coding: utf-8 -*-
"""
ARRANGEMENT — the variation engine, mined from the 46k arrangement transcript
(grammar.json["arrangement"]). Operates on STEM AUDIO at bar level, driven by
the same section map as the composition (fm_chaos.sec).

What it encodes:
  * 16-bar segments ending in a FILL: kick+bass drop out for the back half of
    the fill bar, drums roll, a riser sweeps INTO the next downbeat (with
    intentional skips — perfection is anti-groove).
  * ENERGY STAIRCASE: every drop run starts low and gains per segment — the
    listener climbs stairs, not a ramp.
  * BUILDS: kick+bass keep rolling but high-passed progressively while a snare
    roll accelerates underneath.
  * IMPACTS at drop starts (thump + crash, the "we have arrived" marker).
  * MICRO-SILENCE: one 1/16 of total nothing right before each drop — the
    silence-as-weapon at the smallest scale.

Used by render_full_fm.py:
    plan = arrangement.make_plan(nbars, fm_chaos.sec, seed=4)
    d    = arrangement.process_stem(name, d, plan)        # per stem
    mix  = arrangement.apply_mix_events(mix, plan)        # after summing
"""
import os, sys
import numpy as np
from scipy.signal import butter, sosfilt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from grammar import G, lerp, lerp_axis

SR = 44100
A = G["arrangement"]
KICKBASS = ("kick", "bass")
HITECH_GATED = ("acid", "lead", "fx", "fm")   # gating NEVER touches kick/bass (grammar law)


def _hp(x, fc):
    return sosfilt(butter(2, max(10.0, fc), btype="high", fs=SR, output="sos"), x)


# ---------------- one-shot synths (sweeps into / impacts out of the line) ----------------
def riser(dur, f0=400.0, f1=4000.0):
    """Noise sweep INTO a division line: rises in pitch + volume, ends AT the line."""
    n = int(dur * SR); t = np.linspace(0, 1, n)
    rng = np.random.RandomState(int(dur * 1000) % 9973)
    noise = rng.randn(n)
    out = np.zeros(n)
    # time-varying bandpass via segmented filtering (cheap + good enough)
    segs = 24
    for s in range(segs):
        a, b = int(n * s / segs), int(n * (s + 1) / segs)
        fc = f0 * (f1 / f0) ** (s / (segs - 1))
        sos = butter(2, [fc * 0.7, min(fc * 1.4, SR / 2 - 100)], btype="band", fs=SR, output="sos")
        out[a:b] = sosfilt(sos, noise[max(0, a - 256):b])[-(b - a):]
    return out * (t ** 2.2)   # volume swells into the line


def impact(thump_hz=55.0):
    """Impact OUT of the line: low thump + noise crash with a long decaying tail."""
    dur = 1.8; n = int(dur * SR); t = np.linspace(0, dur, n)
    thump = np.sin(2 * np.pi * thump_hz * t * np.exp(-t * 0.8)) * np.exp(-t * 5.0)
    rng = np.random.RandomState(99)
    crash = _hp(rng.randn(n), 2500) * np.exp(-t * 3.2) * 0.5
    return thump + crash


def snare_hit(dur=0.12):
    n = int(dur * SR); t = np.linspace(0, dur, n)
    rng = np.random.RandomState(7)
    body = np.sin(2 * np.pi * 190 * t) * np.exp(-t * 35) * 0.6
    noise = _hp(rng.randn(n), 1200) * np.exp(-t * 28)
    return (body + noise) * 0.8


def snare_roll(dur, accel=True):
    """Accelerating roll: 1/8 -> 1/16 -> 1/32 with rising volume (build energy)."""
    n = int(dur * SR); out = np.zeros(n)
    hit = snare_hit()
    t = 0.0
    while t < dur:
        frac = t / dur
        step = lerp(0.25, 0.0625, frac ** 1.5) if accel else 0.125   # seconds-ish at 150
        pos = int(t * SR); e = min(pos + len(hit), n)
        out[pos:e] += hit[:e - pos] * lerp(0.3, 1.0, frac)
        t += step
    return out


# ---------------- the plan: per-bar directives from the section map ----------------
def make_plan(n_bars, sec_fn, seed=4):
    """Walk the section map and produce bar-level directives."""
    rng = np.random.RandomState(seed)
    seg = A["segment_bars"]
    plan = {
        "fill_bars": {},        # bar -> {"roll": bool, "riser": bool}
        "staircase": {},        # bar -> gain for staircase stems
        "build_hp": {},         # bar -> hp cutoff for kick/bass
        "build_roll_bars": set(),
        "impact_bars": set(),   # first bar of a drop
        "micro_silence": [],    # (bar, n_s16) cut everything, last s16 before bar
        "n_bars": n_bars,
    }
    runs = []   # contiguous (start, end, kind) runs of playable sections
    b = 0
    while b < n_bars:
        s = sec_fn(b)
        e = b
        while e < n_bars and sec_fn(e) == s:
            e += 1
        runs.append((b, e, s))
        b = e

    for (s0, s1, kind) in runs:
        ln = s1 - s0
        if kind in ("order", "chaos"):
            # ENERGY STAIRCASE: gain steps up per segment across the run
            nseg = max(1, int(np.ceil(ln / seg)))
            st = A["energy_staircase"]
            for i in range(nseg):
                g = lerp(st["start_gain"], st["end_gain"], i / max(nseg - 1, 1))
                for bb in range(s0 + i * seg, min(s0 + (i + 1) * seg, s1)):
                    plan["staircase"][bb] = g
            # FILL at the end of each full segment (15+1), with intentional skips
            for i in range(nseg):
                fb = s0 + (i + 1) * seg - 1
                if fb >= s1 - 1:
                    continue   # the run's own boundary handles the transition
                if rng.random() < A["fill"]["skip_prob"]:
                    continue
                plan["fill_bars"][fb] = {"roll": A["fill"]["drum_roll"],
                                         "riser": A["fill"]["riser_into_next"]}
        elif kind == "build":
            # high-pass sweep on kick/bass across the build + roll at the end
            h0, h1 = A["build"]["hp_sweep_hz"]
            for bb in range(s0, s1):
                plan["build_hp"][bb] = lerp(h0, h1, (bb - s0) / max(ln - 1, 1))
            for bb in range(max(s0, s1 - A["build"]["snare_roll_last_bars"]), s1):
                plan["build_roll_bars"].add(bb)
        elif kind == "drop":
            if A["impact"]["at_drop_start"]:
                plan["impact_bars"].add(s0)
            plan["micro_silence"].append((s0, A["micro_silence"]["s16_before_drop"]))
    return plan


# ---------------- application ----------------
def _bar_slice(bar, BAR, n):
    a = int(bar * BAR * SR)
    return a, min(int((bar + 1) * BAR * SR), n)


def process_stem(name, stereo, plan, BAR):
    """Per-stem bar-level automation: staircase gains, fill mutes, build HP."""
    n = len(stereo)
    out = stereo
    st_stems = A["energy_staircase"]["stems"]

    if name in st_stems and plan["staircase"]:
        env = np.ones(n)
        for bar, g in plan["staircase"].items():
            a, b = _bar_slice(bar, BAR, n)
            env[a:b] = g
        # soften staircase steps (10 ms) so they're musical, not clicks
        k = int(0.01 * SR)
        if k > 1:
            env = np.convolve(env, np.ones(k) / k, mode="same")
        out = out * env[:, None]

    if name in KICKBASS:
        if plan["fill_bars"]:
            env = np.ones(n)
            frac = A["fill"]["kickbass_out_frac"]
            for bar in plan["fill_bars"]:
                a, b = _bar_slice(bar, BAR, n)
                cut = b - int((b - a) * frac)
                env[cut:b] = 0.0
                r = int(0.008 * SR)
                if cut - r > 0:
                    env[cut - r:cut] = np.linspace(1, 0, r)
            out = out * env[:, None]
        for bar, fc in plan["build_hp"].items():
            a, b = _bar_slice(bar, BAR, n)
            for ch in range(2):
                out[a:b, ch] = _hp(out[a:b, ch], fc)

    if name == "drums" and plan["fill_bars"]:
        env = np.ones(n)
        for bar, info in plan["fill_bars"].items():
            if info["roll"]:
                a, b = _bar_slice(bar, BAR, n)
                cut = b - int((b - a) * 0.5)
                env[cut:b] = 0.25   # duck drums under the roll
        out = out * env[:, None]
    return out


def apply_hitech(name, stereo, BAR, hitech_fn, seed=23):
    """Momento hitech (Axis B) over baked stems: per-bar trance-gate on leads/FX
    (density from grammar, downbeats kept) + overdrive/brightness on the fm stem.
    Tempo does NOT ramp here (stems are baked) — that arrives with Fase C."""
    if name not in HITECH_GATED:
        return stereo
    n = len(stereo)
    rng = np.random.RandomState(seed + sum(ord(ch) for ch in name))
    out = stereo
    n_bars = int(np.ceil(n / (BAR * SR)))
    env = None
    for bar in range(n_bars):
        hp = hitech_fn(bar)
        if hp <= 0.02:
            continue
        a, b = _bar_slice(bar, BAR, n)
        dens = lerp_axis("hitech", "gating_density", hp)
        if dens > 0.02:
            if env is None:
                env = np.ones(n)
            step = int(BAR / 16 * SR)
            ramp = max(8, int(0.001 * SR))
            for s in range((b - a) // step + 1):
                sa, sb = a + s * step, min(a + (s + 1) * step, b)
                if sb <= sa:
                    continue
                # dens = fraccion CORTADA (sube con hitech); downbeats siempre quedan
                on = rng.random() >= dens or s % 4 == 0
                if not on:
                    env[sa:sb] = 0.0
                    if sa - ramp > 0:
                        env[sa - ramp:sa] = np.minimum(env[sa - ramp:sa], np.linspace(1, 0, ramp))
                    if sb + ramp < n:
                        env[sb:sb + ramp] = np.minimum(env[sb:sb + ramp], np.linspace(0, 1, ramp))
        if name == "fm":
            dr = lerp_axis("hitech", "lp_overdrive", hp)
            bz = lerp_axis("hitech", "brightness", hp)
            seg = out[a:b].copy()
            seg = np.tanh(seg * dr) / np.tanh(dr)            # metallic zing
            if bz > 0.02:
                for ch in range(2):
                    seg[:, ch] += bz * _hp(seg[:, ch], 3000)  # brightness blend
            out = out.copy() if out is stereo else out
            out[a:b] = seg
    if env is not None:
        out = out * env[:, None]
    return out


def apply_mix_events(mix, plan, BAR):
    """Mix-level one-shots: fills' rolls + risers, build rolls, impacts, micro-silence."""
    n = len(mix)
    half = BAR / 2

    for bar, info in plan["fill_bars"].items():
        a, b = _bar_slice(bar, BAR, n)
        mid = b - int(half * SR)
        if info["roll"]:
            roll = snare_roll(half) * 0.5
            e = min(mid + len(roll), n)
            mix[mid:e] += roll[:e - mid, None]
        if info["riser"]:
            rs = riser(BAR * 1.0) * A["oneshots"]["riser_level"]
            s = max(0, b - len(rs))
            mix[s:b] += rs[-(b - s):, None]

    for bar in plan["build_roll_bars"]:
        a, b = _bar_slice(bar, BAR, n)
        roll = snare_roll(BAR) * 0.45
        e = min(a + len(roll), n)
        mix[a:e] += roll[:e - a, None]

    for bar in plan["impact_bars"]:
        a, _ = _bar_slice(bar, BAR, n)
        imp = impact(A["impact"]["thump_hz"]) * A["impact"]["level"]
        e = min(a + len(imp), n)
        mix[a:e] += imp[:e - a, None]

    apply_micro_silence(mix, plan, BAR)
    return mix


def apply_micro_silence(mix, plan, BAR):
    """One 1/16 of ABSOLUTE nothing before each drop. Called again after the
    matching EQ: its linear-phase ringing smears neighbors into the gap, so the
    weapon must be re-applied as the LAST operation."""
    n = len(mix); s16 = BAR / 16
    for bar, n16 in plan["micro_silence"]:
        a, _ = _bar_slice(bar, BAR, n)
        cut0 = max(0, a - int(n16 * s16 * SR))
        r = int(0.004 * SR)
        if cut0 - r > 0:
            mix[cut0 - r:cut0] *= np.linspace(1, 0, r)[:, None]
        mix[cut0:a] = 0.0
    return mix
