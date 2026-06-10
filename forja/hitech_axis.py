# -*- coding: utf-8 -*-
"""
HITECH-AXIS — the 2nd style axis (DARKPSY <-> HITECH), from HITECH_FORMULA.md.

A single scalar `hitech_pos` in [0,1] drives the whole "hitech moment":
  tempo 148->185 | fm_index up | lp_overdrive up (metallic zing) | gating 0->70%
  (leads/FX only) | brightness up | density up | decay tighter.
Orthogonal to Axis A (ORDER<->CHAOS = FM C:M character, in fm_chaos.py).

Demo: render a section where hitech_pos ramps 0->1 so you HEAR dark psy accelerate
and metallize into hitech (with a kick to feel the tempo ramp).

  python forja/hitech_axis.py [bars] [chaos]
"""
import os, sys
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fm_chaos as fmc
from grammar import lerp_axis, StyleState
SR = fmc.SR
ROOT = fmc.ROOT
rng = np.random.RandomState(11)

def hp_filt(x, fc): return sosfilt(butter(2, fc, btype="high", fs=SR, output="sos"), x)

# ---- hitech_pos -> sub-params (the lerp table now lives in grammar.json) ----
def tempo_bpm(hp):     return lerp_axis("hitech", "tempo_bpm", hp)
def fm_index_combo(chaos, hp): return StyleState(chaos, hp).fm_index_combo  # drives fm_voice index/energy
def lp_overdrive(hp):  return lerp_axis("hitech", "lp_overdrive", hp)       # tanh drive (metallic)
def gating_density(hp): return lerp_axis("hitech", "gating_density", hp)    # fraction of 1/16 steps ON
def brightness(hp):    return lerp_axis("hitech", "brightness", hp)         # high-shelf-ish blend
def n_notes_for(chaos, hp): return int(2 + round(hp * 6 + chaos * 1))

# ---- simple kick to feel the tempo ----
def kick_oneshot():
    dur = 0.18; n = int(dur * SR); t = np.linspace(0, dur, n)
    f = 50 + 320 * np.exp(-t * 42)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 13)
    cl = np.random.RandomState(1).randn(n) * np.exp(-t * 120) * 0.4
    cl = hp_filt(cl, 2500)
    k = np.tanh((body + cl * 0.5) * 2) / np.tanh(2) * 0.9
    return k
KICK = kick_oneshot()

def apply_gate(buf, s16, density):
    """Trance-gate at 1/16 on a (samples,) buffer. Density = fraction of steps ON.
    Encodes DENSITY (random-within-bounds), not a fixed pattern (per the grammar)."""
    if density < 0.02:
        return buf
    step = int(s16 * SR)
    ramp = max(8, int(0.001 * SR))
    nsteps = int(np.ceil(len(buf) / step))
    g = np.zeros(len(buf))
    for s in range(nsteps):
        on = rng.random() < density or (s % 4 == 0 and density > 0.3)  # keep some downbeats
        a, b = s * step, min((s + 1) * step, len(buf))
        if on:
            seg = np.ones(b - a)
            seg[:ramp] = np.linspace(0, 1, ramp)
            seg[-ramp:] = np.linspace(1, 0, ramp)
            g[a:b] = seg
    return buf * g

def render_hitech_moment(bars=32, chaos=0.5, hp0=0.0, hp1=1.0):
    hps = [hp0 + (hp1 - hp0) * (b / max(bars - 1, 1)) for b in range(bars)]
    bar_durs = [(60.0 / tempo_bpm(hp)) * 4 for hp in hps]
    starts = np.concatenate([[0.0], np.cumsum(bar_durs)])
    total = int(starts[-1] * SR) + SR
    L = np.zeros(total); R = np.zeros(total)
    print(f"  bar  hitech  bpm   notes  gate%  drive")
    for b in range(bars):
        hp = hps[b]; bpm = tempo_bpm(hp); bardur = bar_durs[b]
        s16 = bardur / 16; beat = bardur / 4; t_bar = starts[b]
        # kick on each beat
        for bt in range(4):
            pos = int((t_bar + bt * beat) * SR); e = min(pos + len(KICK), total)
            L[pos:e] += KICK[:e - pos] * 0.9; R[pos:e] += KICK[:e - pos] * 0.9
        # FM lead into a per-bar buffer (so we can gate/overdrive/brighten it)
        barlen = int(bardur * SR) + int(0.3 * SR)
        fL = np.zeros(barlen); fR = np.zeros(barlen)
        c_idx = fm_index_combo(chaos, hp)
        ratio = fmc.ratio_for_chaos(chaos)
        nn = n_notes_for(chaos, hp); stepn = 16 // max(1, nn)
        for k in range(nn):
            off = fmc.PHRASE[(b * nn + k) % len(fmc.PHRASE)]
            if hp > 0.5 and rng.random() < 0.4: off += rng.choice([-1, 1, 2, 12])
            carrier = fmc.nf(ROOT + off)
            dur = s16 * (1.4 if hp < 0.3 else (0.5 + rng.random() * 0.6))  # tighter at hitech
            lt = k * stepn * s16 + (rng.normal(0, 0.003))
            pan = rng.uniform(-0.4, 0.4) * (0.3 + hp)
            l, r = fmc.fm_voice(carrier, ratio, c_idx, dur, pan)
            pos = int(lt * SR); e = min(pos + len(l), barlen)
            if pos >= 0 and e > pos:
                fL[pos:e] += l[:e - pos]; fR[pos:e] += r[:e - pos]
        # gating (leads only), overdrive (metallic), brightness
        dens = gating_density(hp)
        fL = apply_gate(fL, s16, dens); fR = apply_gate(fR, s16, dens)
        dr = lp_overdrive(hp)
        fL = np.tanh(fL * dr) / np.tanh(dr); fR = np.tanh(fR * dr) / np.tanh(dr)
        bz = brightness(hp)
        if bz > 0.02:
            fL = fL + bz * hp_filt(fL, 3000); fR = fR + bz * hp_filt(fR, 3000)
        # mix the FM bar in
        pos = int(t_bar * SR); e = min(pos + barlen, total)
        L[pos:e] += fL[:e - pos] * 0.5; R[pos:e] += fR[:e - pos] * 0.5
        print(f"  {b:3d}  {hp:.2f}   {bpm:3.0f}   {nn:2d}    {dens*100:3.0f}    {dr:.1f}")
    # master
    L = hp_filt(L, 28); R = hp_filt(R, 28)
    pk = max(np.max(np.abs(L)), np.max(np.abs(R))) + 1e-9
    return np.column_stack([(L / pk * 0.95 * 32767).astype(np.int16),
                            (R / pk * 0.95 * 32767).astype(np.int16)])

if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")
    bars = int(sys.argv[1]) if len(sys.argv) > 1 else 32
    chaos = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "forja", "recreation_out", "sampler", "hitech_moment.wav")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    print("=" * 56)
    print(f" HITECH-MOMENT demo  {bars} bars, chaos {chaos}  (DARKPSY -> HITECH)")
    print("=" * 56)
    stereo = render_hitech_moment(bars, chaos)
    wavfile.write(out, SR, stereo)
    print(f"\n  -> {out}  ({len(stereo)/SR:.0f}s)")
    print("  Escuchá: acelera + se vuelve metálico + entra el gating = momento hitech.")
