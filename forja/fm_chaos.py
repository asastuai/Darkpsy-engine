# -*- coding: utf-8 -*-
"""
FM-CHAOS — the core dark-psy timbre lever, encoded (from PRODUCTION_GRAMMAR.md).

Per-bar CHAOS (0..1) derived from the section map drives a 2-operator FM voice:
  ORDER (chaos->0): INTEGER C:M ratio + LOW index            -> clean, harmonic
  CHAOS (chaos->1): NON-INTEGER C:M ratio + HIGH index sweep -> metallic, alien
(Chowning FM — the single most physics-grounded gnarliness control.)

This is a reusable engine module: chaos_at(bar) + fm_voice() + render_fm_lead().
Standalone run renders a demo so you HEAR the ORDER->CHAOS morph.

  python forja/fm_chaos.py [start_bar] [end_bar]
"""
import os, sys
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from grammar import G, lerp, lerp_axis   # the genre law lives in grammar.json

SR = 44100
BPM = 150
BEAT = 60.0 / BPM
BAR = BEAT * 4
S16 = BEAT / 4
ROOT = 40  # E2
TOTAL_BARS = 280

def nf(m): return 440.0 * (2 ** ((m - 69) / 12.0))

# ---------------- section map -> per-bar chaos (first-class param) ----------------
_smap = {}
def _ss(s, e, t):
    for b in range(s, min(e, TOTAL_BARS)): _smap[b] = t
_ss(0,10,'intro'); _ss(10,30,'order'); _ss(30,31,'silence'); _ss(31,33,'drop')
_ss(33,42,'chaos'); _ss(42,43,'silence'); _ss(43,45,'drop'); _ss(45,70,'order')
_ss(70,71,'silence'); _ss(71,73,'drop'); _ss(73,88,'chaos'); _ss(88,89,'silence')
_ss(89,91,'drop'); _ss(91,120,'order'); _ss(120,122,'silence'); _ss(122,124,'drop')
_ss(124,148,'chaos'); _ss(148,149,'silence'); _ss(149,165,'break'); _ss(165,175,'build')
_ss(175,176,'silence'); _ss(176,178,'drop'); _ss(178,210,'order'); _ss(210,211,'silence')
_ss(211,213,'drop'); _ss(213,240,'chaos'); _ss(240,241,'silence'); _ss(241,243,'drop')
_ss(243,268,'order'); _ss(268,TOTAL_BARS,'outro')
for b in range(TOTAL_BARS): _smap.setdefault(b, 'order')
def sec(b): return _smap.get(b, 'order')

_CA = G["sections"]["chaos_levels"]
_BUILD = G["sections"]["build_ramp"]
def chaos_at(bar):
    """Per-bar CHAOS 0..1. Build sections ramp; others map by section type."""
    s = sec(bar)
    if s == 'build':
        bs = bar
        while bs > 0 and sec(bs-1) == 'build': bs -= 1
        be = bar
        while be < TOTAL_BARS and sec(be) == 'build': be += 1
        return lerp(_BUILD["from"], _BUILD["to"], (bar - bs) / max(be - bs, 1))
    return _CA.get(s, 0.0)

_HM = G["sections"].get("hitech_moment")
def hitech_at(bar):
    """Per-bar HITECH 0..peak: trapezoid over the hitech_moment window (Axis B)."""
    if not _HM:
        return 0.0
    s0, s1 = _HM["bars"]
    if not (s0 <= bar < s1):
        return 0.0
    ri, ro, pk = _HM["ramp_in_bars"], _HM["ramp_out_bars"], _HM["peak"]
    if bar < s0 + ri:
        return pk * (bar - s0 + 1) / ri
    if bar >= s1 - ro:
        return pk * (s1 - bar) / ro
    return pk

# ---------------- 2-operator FM voice (Chowning) ----------------
def ratio_for_chaos(c):
    """Integer (harmonic) at ORDER -> non-integer (inharmonic) at CHAOS."""
    return lerp_axis("chaos", "fm_ratio", c)

def index_env_for_chaos(c, n):
    """Modulation index over the note: low at ORDER, high + upward sweep at CHAOS."""
    i0 = lerp_axis("chaos", "fm_index_start", c)
    i1 = lerp_axis("chaos", "fm_index_end", c)   # the schwang sweep upward
    return np.linspace(i0, i1, n)

def fm_voice(carrier_hz, ratio, c, dur, pan=0.0):
    n = max(1, int(dur * SR))
    t = np.arange(n) / SR
    idx = index_env_for_chaos(c, n)
    mod = np.sin(2 * np.pi * carrier_hz * ratio * t)
    sig = np.sin(2 * np.pi * carrier_hz * t + idx * mod)
    # amp env: fast attack, exp-ish decay (more sustained when chaos high)
    a = max(1, int(0.005 * SR))
    env = np.ones(n)
    env[:a] = np.linspace(0, 1, a)
    rel = int(min(n, (0.04 + 0.10 * (1 - c)) * SR))
    env[-rel:] *= np.linspace(1, 0, rel)
    env *= np.exp(-t * lerp_axis("chaos", "note_decay_rate", c))   # ORDER plucky, CHAOS sustains
    sig *= env * 0.7
    l = sig * np.cos((pan + 1) / 2 * np.pi / 2)
    r = sig * np.sin((pan + 1) / 2 * np.pi / 2)
    return l, r

def _hp(x, fc): return sosfilt(butter(2, fc, btype='high', fs=SR, output='sos'), x)

# ---------------- atmosphere voice (elongated notes + volume gradients) ----------------
# Juan's direction: where the FM voice + chaos sound, notes should be ELONGATED with
# volume gradients so they form an "atmosphere" — not a machine-gun of stabs.
_ATMO = G["atmosphere"]
PAD_CHAOS = _ATMO["pad_chaos_threshold"]   # chaos level at/above which the voice becomes atmospheric
PAD_BARS = _ATMO["pad_bars"]               # each atmosphere note overlaps the next

def pad_env(n, rise=0.45):
    """The volume gradient: raised-cosine swell up to the peak (at `rise` of the
    note), then a slow fade — the breathing shape of the atmosphere."""
    p = min(n - 1, max(1, int(n * rise)))
    up = 0.5 - 0.5 * np.cos(np.pi * np.arange(p) / p)
    dn = 0.5 + 0.5 * np.cos(np.pi * np.arange(n - p) / max(n - p, 1))
    return np.concatenate([up, dn])[:n]

def fm_pad(carrier_hz, ratio, c, dur, pan=0.0, rise=0.45):
    """Elongated FM note with a gradient envelope. The mod index BREATHES with the
    volume (more alien at the swell's peak) instead of the fast schwang sweep, and
    the note drifts slowly in stereo so the long tone moves in space."""
    n = max(1, int(dur * SR))
    t = np.arange(n) / SR
    env = pad_env(n, rise)
    idx = (0.8 + 2.5 * c) + (1.5 + 4.0 * c) * env
    mod = np.sin(2 * np.pi * carrier_hz * ratio * t)
    sig = np.sin(2 * np.pi * carrier_hz * t + idx * mod)
    sig *= env * _ATMO["level"]
    drift = 0.25 * np.sin(2 * np.pi * _ATMO["drift_hz"] * t + pan * 3)
    theta = (np.clip(pan + drift, -1, 1) + 1) / 2 * np.pi / 2
    return sig * np.cos(theta), sig * np.sin(theta)

# ---------------- render an FM lead across bars, chaos-driven ----------------
# E Phrygian dominant-ish degrees as MIDI offsets from ROOT (up an octave for lead)
PHRASE = [12, 13, 16, 17, 19, 17, 16, 13]   # melodic offsets (semitones from ROOT)

def _mix(L, R, l, r, t0, total):
    pos = int(t0 * SR); e = min(pos + len(l), total); nn = e - pos
    if nn > 0 and pos >= 0:
        L[pos:e] += l[:nn]; R[pos:e] += r[:nn]

def _schedule_bar(L, R, total, ab, tbar, rng, verbose=False):
    """One bar of the FM voice. ORDER (<PAD_CHAOS): clean sparse stabs.
    CHAOS (>=PAD_CHAOS): ATMOSPHERE — elongated notes with volume gradients
    (every 2nd bar, two voices overlapping) + 2 sparse accent stabs for rhythm."""
    c = chaos_at(ab)
    hp = hitech_at(ab)
    # hitech pushes the stab index/energy up without touching the pad identity
    c_idx = max(c, min(1.0, 0.4 * c + hp)) if hp > 0 else c
    ratio = ratio_for_chaos(c)
    if c >= PAD_CHAOS:
        n_notes = _ATMO["accent_stabs_per_bar"]  # sparse accents; the atmosphere carries the bar
        run0 = ab    # first bar of this chaos run, so the atmosphere enters WITH the drop
        while run0 > 0 and chaos_at(run0 - 1) >= PAD_CHAOS:
            run0 -= 1
        if (ab - run0) % _ATMO["pad_every_bars"] == 0:  # a new elongated note, overlapping
            off = PHRASE[ab % len(PHRASE)]
            r0, r1 = _ATMO["rise_range"]
            for v in _ATMO["voices"]:                              # root + fifth, mirrored
                carrier = nf(ROOT + off + v["offset"])
                rise = r0 + rng.random() * (r1 - r0)               # each swell breathes differently
                l, r = fm_pad(carrier, ratio, c, PAD_BARS * BAR, v["pan"], rise)
                _mix(L, R, l, r, tbar, total)
    else:
        n_notes = int(round(lerp_axis("chaos", "stab_notes_per_bar", c)))
    n_notes = min(16, n_notes + int(round(hp * 4)))   # hitech = denser stabs
    step = 16 // max(1, n_notes)
    for k in range(n_notes):
        off = PHRASE[(ab * n_notes + k) % len(PHRASE)]
        if c > 0.5 and rng.random() < 0.4:
            off += rng.choice([-1, 1, 2])
        if hp > 0.5 and rng.random() < 0.3:
            off += 12   # the hitech octave-jump signature
        carrier = nf(ROOT + off)
        dur = S16 * (1.5 if c < 0.3 else (0.8 + rng.random() * 1.2))
        dur *= lerp(1.0, 0.55, hp)   # tighter notes as hitech rises
        t0 = tbar + k * step * S16 + (rng.normal(0, 0.004) if c > 0.4 else 0)
        pan = rng.uniform(-0.4, 0.4) * max(c, hp)
        l, r = fm_voice(carrier, ratio, c_idx, dur, pan)
        _mix(L, R, l, r, t0, total)
    if verbose:
        kind = "ATMOS+2" if c >= PAD_CHAOS else f"stabs:{n_notes}"
        print(f"  {ab:3d}  {c:.2f}   {ratio:.2f}   {kind}")

def render_fm_lead(start_bar, end_bar):
    bars = end_bar - start_bar
    total = int((bars + 2) * BAR * SR)  # tail room for the last elongated note
    L = np.zeros(total); R = np.zeros(total)
    rng = np.random.RandomState(7)
    print(f"  bar  chaos  ratio   voice")
    for b in range(bars):
        _schedule_bar(L, R, total, start_bar + b, b * BAR, rng, verbose=True)
    # cleanup + soft sat
    L = _hp(L, 120); R = _hp(R, 120)
    def ws(x, a=1.5): return np.tanh(x * a) / np.tanh(a)
    L = ws(L); R = ws(R)
    pk = max(np.max(np.abs(L)), np.max(np.abs(R))) + 1e-9
    return np.column_stack([(L/pk*0.95*32767).astype(np.int16), (R/pk*0.95*32767).astype(np.int16)])

def render_fm_stem(n_bars=TOTAL_BARS, gate=True, seed=7):
    """Full-length FM stem (absolute bar positions). Gated: silent where chaos<0.15
    so ORDER stays clean and FM appears as the chaos/drop/build element. Returns
    raw float (L, R) for the mixer to balance."""
    total = int((n_bars + 2) * BAR * SR)
    L = np.zeros(total); R = np.zeros(total)
    rng = np.random.RandomState(seed)
    for ab in range(n_bars):
        if gate and chaos_at(ab) < 0.15:
            continue
        _schedule_bar(L, R, total, ab, ab * BAR, rng)
    L = _hp(L, 120); R = _hp(R, 120)
    return L, R


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")
    sb = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    eb = int(sys.argv[2]) if len(sys.argv) > 2 else 42   # order(10-29)->silence->drop->chaos(33-41)
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "forja", "recreation_out", "sampler", "fm_lead_chaos.wav")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    print("=" * 56)
    print(f" FM-CHAOS demo  bars {sb}-{eb}  (escuchá el morph ORDEN->CAOS)")
    print("=" * 56)
    stereo = render_fm_lead(sb, eb)
    wavfile.write(out, SR, stereo)
    print(f"\n  -> {out}  ({len(stereo)/SR:.0f}s)")
    print("  ORDEN = C:M entero + indice bajo (limpio) | CAOS = no-entero + indice alto (alien)")
