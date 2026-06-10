# Hitech Formula + the 2D Style Space

Multi-agent research (8 agents) on the hitech psytrance "formula", verified.
Companion to `PRODUCTION_GRAMMAR.md`. Goal: encode a second style axis
(DARKPSY↔HITECH↔FOREST) alongside ORDER↔CHAOS, + a live "hitech moment" macro.

## Is hitech "a formula"? — honest verdict
**The SKELETON (chassis) is a formula; the FLESH is craft.** Juan's intuition is
right in *direction*, overstated in *degree*. Hitech's grid/timing/mix layer is
genuinely deterministic and encodable (tempo, 4/4 kick, 16th KBBB bass, decay-vs-BPM
math, phase-reset, mono-below, kick-over-bass, sidechain math, short breaks). But its
IDENTITY — the metallic zing, the FM patch, the gating patterns, bar-to-bar morphing —
is taste-driven sound design. **Encode the chassis as hard rules; encode timbre as
parameterized-random-within-bounds. "The formula" is a strong prior, not a closed
solution.** Without the flesh layer it sounds like a tech demo.

## The 2D style space (two orthogonal axes)

```
        CHAOS  (Axis A: FM C:M character — the psychedelic weirdness)
          │
  forest ─┼─ darkpsy ────────────► hitech   (Axis B: hitech_pos)
  (organic│   ~150, murky,           ~180, clinical,
   branch)│    wet, hypnotic          dry, gated, metallic)
          │
        ORDER
```

- **Axis A — ORDER↔CHAOS** (already encoded in `fm_chaos.py`): FM C:M integer↔non-integer
  + mod chaos. Controls harmonic↔inharmonic psychedelic character.
- **Axis B — DARKPSY↔HITECH** (new): a single tempo-anchored scalar **`hitech_pos` ∈ [0,1]**
  that everything lerps off. The two axes MULTIPLY (high-chaos+high-hitech = chaotic-metallic;
  low-chaos+high-hitech = clean robotic melodic-hitech).
- **FOREST = a perpendicular lever** (not a point on the darkpsy↔hitech line): low tempo +
  low gating + high reverb + low metallicity + an active ORGANIC foley layer.

### The lerp table (Axis B — drive everything from `hitech_pos`)
| param | darkpsy (0.0) → hitech (1.0) |
|---|---|
| `tempo_bpm` | lerp(148, 185) |
| `cleanliness` | lerp(0.2, 0.9) — low-mid cut depth, mono cutoff, SPAN-flatness |
| `gating_density` | lerp(0.0, 0.7) — fraction of lead-time gated (leads/FX ONLY) |
| `fm_index` | lerp(3.0, 8.0) — combines with Axis-A C:M |
| `lp_overdrive` | lerp(0.1, 0.9) — metallic digital clipping on the LP filter |
| `brightness` | lerp(0, +2 dB @10 kHz) + spectral centroid up |
| `reverb_decay_ms` | lerp(2000, 400) — wet/atmospheric → dry/clinical |
| `sidechain_release` | lerp(1/4-note, 1/8-note) |
| `kick_tail_ms` | scales DOWN with BPM (engineering, not lerp) |
| `max_bass_decay_ms` | **(60000/BPM/4)·0.6** ≈ 60ms@150, 50ms@180 |
| `break_length` | shrinks (16-32 bars vs darkpsy's 1-3 min) |
| `variation_rate` | new layer/timbral change every 2-4 bars (vs 8-16) |
| `bass_patch_variation_rate` | lerp(0.1, 0.7) — higher prior, CAPPED (not every bar) |

## The chassis (hard deterministic rules)
- **TEMPO is the primary dial** + most audience-perceptible marker. Zones: darkpsy 148-160,
  bridge 160-170, hitech 172-200+ (core 180, psycore 200-220). Grid math @180: 1/16=83.3ms,
  1/8=166.7ms, beat=333.3ms, bar=1333ms. `ms_per_div(BPM,div)=60000/BPM/div_factor`.
- **KICK = hard 4/4, no swing, no humanization** (the precision IS the genre). Same fishtail
  sine kick as darkpsy; only the envelope differs: shorter tail, harder transient, less sub,
  sits 2-3 dB above bass and 2-3 dB lower absolute at high BPM. Tuned to root or +7 semitones.
- **BASS = KBBB 16th rolling** (kick on each quarter downbeat, bass on the other three 16ths) —
  SHARED with darkpsy. Hitech delta = gate LENGTH not grid: `max_bass_decay_ms=(60000/BPM/4)·0.6`,
  note length 70-80% of a 16th. **Deterministic phase-reset on note-on** (osc phase=0) — real
  and mandatory for a repeatable transient.
- **SIDECHAIN = tempo-synced drawn volume-duck** (not a compressor; can't track <2ms @180+).
  Depth 3-6 dB, release tied to 1/8 or 1/4 note.
- **MIX:** mono below ~120-200 Hz, cut 300-500 Hz mud, high-shelf air on leads, linear-phase EQ
  for sub cuts, ceiling -0.3..-1 dBTP.
- **ARRANGEMENT:** lower entropy than darkpsy — short functional breaks (16-32 bars, not
  atmospheric journeys), new element/timbral change every 2-4 bars, relentless pulse (never breathes).

## The flesh (parameterized-random-within-bounds, NOT hardcoded)
- FM lead patch micro-design (C:M ratios are TUNABLE RANGES: 2:1, 4:1, non-integer — never magic).
- **GATING** = the clearest "we just went hitech" cue. Leads/FX ONLY, never kick/bass. Encode
  DENSITY/rate (0-10% darkpsy → 40-80% hitech), generate the step PATTERN random-within-bounds
  or from a curated bank — never one hardcoded rhythm. Gate 1/16 (staccato) → 1/32 (max), attack
  <1ms / variable hold / release <5ms, evolve every ~16 bars.
- Bar-to-bar morphing, fills (stutters, tape-stop, reverse sweeps, glitch) at 2-4 bar boundaries.

## ⚠️ Myths to discard (verified)
- ❌ "Waveform can't complete its cycle at 180 BPM" — physically FALSE (55 Hz runs ~4.6 cycles in
  an 83 ms 16th). Keep the FIX (phase-reset + short kick tail); discard the rationale.
- ❌ "Bass decay shouldn't exceed 1 ms" — typo/misread; use the BPM-derived decay formula.
- ❌ Specific C:M ratios / "Hive filter decay = 27" / exact plugin-chain orders (Saturn→ProQ3→SSL→L3)
  — folklore/brand-worship. Encode operations, not brands.
- ❌ "It's ALL FM, subtractive won't work at tempo" — overstated; saw→24dB-LP works fine with
  phase-reset + tight envelopes. FM is favored for the metallic LEAD, not mandatory everywhere.
- ❌ LUFS target wars (-6/-8/-9) — loudness politics, not a formula. Pick -8 club and move on.

## Live "HITECH MOMENT" macro (Reaper agent)
A single reversible trigger that ramps `hitech_pos` 0→1 over N bars, firing 8 lanes in sequence
(ideally into a SHORT break so the +25-30 BPM jump lands without jarring):
1. **TEMPO RAMP** ~150→175-185 (gradual +2-3 BPM/16bars w/ key-lock off, OR hard-cut at a stripped break).
2. **KICK TIGHTEN** (shorten tail, raise click, drop gain 2-3 dB, keep 2-3 dB over bass).
3. **BASS TIGHTEN** (note → 70-80% of 16th, decay formula, phase-reset, raise patch variation capped).
4. **FM METALLIZE** (fm_index 3→8, lp_overdrive 0.1→0.9, retrigger/arp at 1/64).
5. **GATE ENGAGE** (lead/FX bus trance-gate 1/16→1/32, density 0→0.6; core stays ungated).
6. **SIDECHAIN TIGHTEN** (release 1/4→1/8, depth 3-6 dB).
7. **MIX BRIGHTEN/DRY** (high-shelf +1-2 dB @10k, cut 300-500 Hz, reverb 2000→400 ms, mono→120 Hz).
8. **ARRANGEMENT SWITCH** (short breaks 16-32 bars, variation every 2-4 bars).

Exposed knobs: `ramp_bars, target_bpm, gate_resolution, gate_density, fm_index_target,
overdrive_target, brightness_db, reverb_target_ms, sidechain_div`. REVERSE = lanes inverted →
back to darkpsy. FOREST EXIT = drop tempo + kill gating + restore long reverb + drop metallicity
+ fade in organic_sample layer.

## Videos to transcribe (concrete URLs)
- Parandroid Masterclass EP1 (free preview): youtube.com/watch?v=sPslzfYpoak
- Hitech Kick & Bass in Serum: TzlBxieX-QA · Old-school kick+bass: -kGYmc0QPyI
- FM synthesis 5 ways (psy/hitech/darkpsy): V2RARuCkVDQ · Hitech FM lead in Serum: RgjcevP0yF4
- OREMETOS Hitech Masterclass — Operator leads: co6k5flUnEA
- Randomized Gater Lead (Vital): 4Zhtpiy-0TI · Random Gating SFX: vUbrFee7Rro
- THE PERFECT KICK by Crazy Astronaut: L7rrgcilEyM · Kick+Bass phase sweet spot: Bc3pI-JeYE8
- Rules of Psytrance Arrangement: OYzU5VXekpM · Alien Chaos @178 live border-zone: Ejw7VCDQ_Qs
- (have: Kindzadza kick+bass r2IWFmtbu34, break LUnGA2YkwgE)

## Where to learn
- **Paralocks interview** (Alien Chaos) — primary source on the formula claim, 170 BPM threshold,
  flat-SPAN mix: alienchaosmusic.com
- **dsokolovskiy.com** + **CineTrance** + **arteculturatrance** — free concrete chassis params.
- **IDM Mag** — Phase Plant PM robotic lead recipe.
- Paid: **Parandroid Masterclass** (Instinct Learning, EP1 free), **Paralocks courses** (Alien Chaos),
  **Frantic Noise Hitech w/ Ableton**, **Eplex7 HBS1** (dedicated hitech bass synth).
- Reference listening: **ektoplazm.com/style/hi-tech**.

---
*Research: Claude (multi-agent). Direction: Juan. For the DarkPsy engine.*
