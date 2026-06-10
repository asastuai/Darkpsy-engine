# DarkPsy Production Grammar

Knowledge base from multi-agent research (10 agents) on dark psy / psytrance /
experimental production + Kindzadza & Psykovsky, verified (myth stripped) and
made actionable for the engine + Reaper agent.

> Sourced from public material (interviews, free tutorials, KVR/Psynews forums,
> course previews, written guides). Paid courses are mapped, not pirated.

---

## The two masters (distilled essence)

**Kindzadza** (Lev Greshilov, Moscow — physicist). VERIFIED: Bitwig Studio
(certified trainer), builds synths from first principles in **The Grid** rather
than presets, makes his own plugins (DDZynth, KranchDD, DDKick) because commercial
tools can't hit his timbre. Aesthetic: *crystal clear, razor sharp* — high dynamic
resolution, NOT muddy lo-fi; clinical production wrapped around disorienting
harmonic/rhythmic content. Workflow: **synthesis-first** (kick+bass as immovable
foundation before leads), then arrange, then mix — *mix-ready by design*.
Arrangement: non-linear metamorphosis (the track transforms several times yet stays
coherent); percussion can be the structural backbone; resample-cherry-pick to keep
leads alive.

**Psykovsky** (Vasily Markelov, Moscow — the abstract pole). CAVEAT: his gear/DAW
is forum-sourced and contradictory — don't hardcode it. Real, decodable
contributions: (1) **deep psychedelia away from forms** — rejects verse/chorus/drop;
moves by internal psychedelic logic for sustained altered states. (2) **Layers of
psychedelic information** — many simultaneous non-redundant layers, real spectral
depth, complexity that stays hypnotic. (3) "Nano-synthesis" = branding; the useful
kernel is **tempo-synced modulation** (quantize LFO/delay/arp to subdivisions) +
deliberate **scale-based pitch placement** + **micro-rhythm breaks** that disrupt
the 4/4 lock. (4) Tempo as a compositional variable (145-200+). *Strip the
numerology, keep the kernel.*

---

## Production grammar (per element, concrete)

**Kick — body:** pitch-enveloped sine sweeping from a few hundred Hz into a 40-55 Hz
fundamental tuned to root, shaped by a **multi-stage MSEG** (fast click → short body
dip → sub boom), not a plain ADSR. Length ~1/8 note (200 ms @150; tail done by
~180 ms so it clears the first 16th bass note). Expose root_freq, total_len,
transient_ms, body_decay, fundamental.

**Kick — click:** separate transient layer (bandpassed ~2.5-7 kHz noise or HP sine),
hard-clipped, offset 0-3 ms, mixed ~0.6 under body. Keep separable.

**Kick — mud notch:** parametric notch in 200-500 Hz. NOT a hardcoded -13 dB @300 Hz;
sweep per kick, default 250-400 Hz, cut -6 to -12 dB (soften our current 0.85 → 0.5-0.7).
HPF 5-10 Hz below fundamental. Mono, rendered to sample before arrangement.

**Bass — osc & phase:** single saw (+optional sub sine 1 oct down), **phase retrigger
ON** so every 16th starts at the same phase (consistent attack + predictable kick
interaction). Raise keytrack → ~1.0 for consistent timbre. Resonance low (~0.18).

**Bass — the roll:** LP24 (tight) or LP12 (smooth), fast filter env for the pluck.
Amp: attack 0, decay tuned for an **audible inter-note gap**, sustain low (0.15-0.30 —
our 0.55 sustains too much for a tight roll), short release. Note length ~0.75-0.82×S16.
Multiband saturation on the 150-300 Hz growl band; protect the sub. Mono below ~100 Hz.

**Acid (303):** saw → resonant LP24 → fast HIGH env-mod filter; **slide** (portamento)
on overlapping notes, **accent** boosts filter-env depth + velocity. Resonance
controlled (~0.5), not screeching. ~7/12 note length. Light post saturation.

**FM lead (THE core dark-psy timbre):** two-operator FM, modulator ~2 oct below
carrier. **Integer C:M (2:1, 3:1) + low index = ORDER/clean; non-integer C:M
(1:2.73, 1:3.14) + high index = CHAOS/alien.** This is the single most
physics-grounded lever (Chowning FM). Automate modulation index low→high as the
primary "gnarliness" control.

**FM/lead FX (metallic edge):** switchable filter/distortion ORDER (pre vs post) —
matches KranchDD's own chain switch. ORDER = post / low dst / low feedback;
CHAOS = pre / high dst / feedback up / Pmod up. Keep wet LOW on bass (~0.4),
higher on acid/lead.

**FM/lead — alien motion:** Sample-and-Hold / random stepped modulation to pitch
and/or filter cutoff; modulate the LFO RATE with a second random source for endless
variation. Audio-rate filter FM = the "electricity" sound (saw + triangle mod 2 oct
lower, HP + overdrive on the filter, step env on cutoff).

**Texture / atmosphere (Psykovsky "layers"):** granular/resample bed on its OWN slow
timescale (not snapped to the 8-bar grid). ORDER = tight/sparse/static grains;
CHAOS = large/dense/random grains. Build via iterative **resample→process→resample**
(freeze-and-re-feed) — genuinely compounds nonlinear texture. Run as a TEXTURE BUS.

**Tempo bias:** at ≥170 BPM bias toward FM timbre (motion in operator ratios, no
filter movement needed). A bias, not a rule.

---

## Arrangement

- **ORDER vs CHAOS is the macro skeleton**, not verse/chorus/drop. ORDER = locked
  kick+bass, on-grid, stable center, hypnotic repetition. CHAOS = off-grid FM stabs,
  polyrhythm, dissonant accumulation, glitch/cut-outs. Energy cycles MANY times
  (mini-peak → strip → rebuild → bigger peak → breakdown → climax → outro).
- **Typed timeline:** INTRO 32-64 → DROP → BRIDGE → DEVELOP (ORDER/CHAOS alternation)
  → BREAKDOWN 16-32 → BUILD 16-32 → CLIMAX → OUTRO. ~300-450 bars @148-155 (~7-9 min).
- **8/16-bar grid rule:** element add/remove snaps to 8- or 16-bar boundaries; only FX
  automation goes sub-8-bar. Strategic OMISSION of an expected change = micro-tension.
- **Silence as a weapon** (verified psychology): pull EVERYTHING ~1 bar before a
  drop/climax (2-4 bars for rare shock). Pre-silence dip at ELEMENT level, not master
  fader. Use sparingly (1-2 per track).
- **Breakdown:** remove kick + heavy perc + bass; keep filtered pads (LP ~400 Hz),
  drone/foley, reverb tails 16-32 bars. Removing the bass makes its re-entry hit.
- **Build (work backwards from the drop):** filtered kick returns → snare roll vel
  50→100 → noise riser + lead filtering in → full intensity → STOP 1 bar short → DROP.
  Build energy must NEVER exceed drop energy.
- **Two MODES:** DARK-PSY = strip/rebuild cycles + breakdowns + silences. FOREST =
  near-continuous rolling groove, tension via timbral evolution + filter "breathing"
  (LP sweep down over 32 bars then up), zero silence events. Expose as a switch.
- **Energy map 1-9 per 8-bar block, generated BEFORE notes:** INTRO 1→4, DROP 6-7,
  BREAKDOWN 2-3, BUILD 3→9, CLIMAX 8-9 held, OUTRO 9→1. Place notes against the curve.
- **Harmony:** minor / harmonic minor / **Phrygian (b2 = instant dark)**, pedal tones,
  sparse motion (change every 32-64 bars). Non-Western modes (Phrygian dominant,
  Hungarian minor) for the avant color.

---

## Mix / master

- **Mono below ~100-120 Hz** (physics-mandatory) via M/S; width only above. Kick+bass
  mono; FM/granular/FX wide.
- **Kick is the loudest single element** (~2-3 dB above bass). Leave 3-6 dB headroom.
- **Kick/bass interlock — two valid strategies** (the "no-sidechain = authentic"
  framing is scene ideology): (a) sidechain duck bass under kick (2:1, ~-20 dB thr,
  GR 3-6 dB, release ~80-100 ms @150); (b) no-sidechain phase/time separation (kick
  tail < gap + KBBB + phase-retrigger bass). Expose both.
- **Mud carving:** parametric notches 200-500 Hz on dense mids; keep 150-300 Hz growl
  on bass; HP every non-bass element.
- **Mastering chain:** Multiband Saturator → Digital EQ (cut 300-500 Hz mud) →
  Analog-style EQ → Multiband Comp (tighten sub) → true-peak Limiter at **-1.0 dBTP**.
- **Dual masters:** club ~-8 to -7 LUFS, streaming ~-14 LUFS, both -1.0 dBTP.
- **Reference-match against a real Glosolalia WAV** — do NOT use invented band-%
  targets.

## ⚠️ Myths our engine had (corrected)

- ❌ "Sub 13% / Bass 54% / ..." band-percentage targets = myth from a single dubious
  source → replace with real reference-spectrum diff vs a Glosolalia WAV.
- ❌ "No-sidechain = authentic" → both methods are valid engineering; expose a switch.
- ❌ "2nd+4th harmonics smear phase" → bogus; symmetric saturation = ODD harmonics.
- ❌ Fixed -13 dB @300 Hz kick notch dogma → parametrize (sweep per kick).
- ❌ "Nano-synthesis" frequency numerology → keep only tempo-synced modulation kernel.

---

## Where to learn (curated)

| Resource | Type | Link |
|---|---|---|
| **Dark Psy Track Production** (Glosolalia/Will O'Wisp + Frantic Noise) | paid ⭐ | future-media.academy/online/dark-psy-track-production |
| **Nano-Synthesis w/ Psykovsky** (~€44, only place he teaches) | paid | future-media.academy/online/nano-synthesis-psykovsky |
| **Storytelling in a Dark Forest** (Onionbrain/Atropp, Parvati) | paid | future-media.academy/online/storytelling-onionbrain-atropp |
| **Powerful Dance Music Production w/ KinDzaDza** (~€950, full Bitwig/Grid) | paid | future-media.academy/online/powerful-dance-music-production |
| KinDzaDza free YouTube extracts (break + kick/bass synthesis) | free | youtube.com/watch?v=LUnGA2YkwgE |
| KINDZAudio — KranchDD (free, in engine) + DDZynth Lite (free) | free | kindza.net |
| KVR forum recipes (FM leads, electricity, basslines) | forum | kvraudio.com/forum (t=432360) |
| dsokolovskiy.com — bassline synthesis + EQ values | free | dsokolovskiy.com/blog |
| arteculturatrance — no-sidechain Kick&Bass Gel method | free | arteculturatrance.wordpress.com |
| Projektor — free dark-psy YouTube + Vital presets | free | projektorsound.com |
| Ektoplazm dark psy WAV catalog (reference listening) | free | ektoplazm.com/style/darkpsy |

---

## How to encode it (engine + agent roadmap)

1. **Kick** (`render_v9.py` render_kick_hybrid): parametrize root_freq/total_len/
   transient_ms/body_decay/notch_freq/notch_depth; soften the 300 Hz notch; separable click.
2. **Bass** (`surge_presets.py` configure_bass): phase retrigger + phase_start_offset;
   keytrack → ~1.0; amp sustain 0.55 → ~0.25 (tighter roll); optional LP24; note-length param.
3. **ORDER/CHAOS as a first-class per-bar `chaos` float (0..1)** that ALL renderers read,
   driving: FM index (a_fm_depth), FM C:M ratio (integer→non-integer via osc2 fine pitch),
   KranchDD dst/feedback/Pmod/chain, filter resonance, S&H depth, grain size/density.
4. **FM lead** (configure_fm_texture / new configure_lead_fm): integer C:M+low index for
   ORDER, non-integer+high for CHAOS, index-automation LFO; S&H → pitch+cutoff.
5. **KranchDD presets chaos-dependent**; expose `chain` (pre/post) per element.
6. **Sidechain rework:** replace the crude 15% full-mix duck with (a) kick-triggered
   bass-only sidechain (release ~80-100 ms) OR (b) no-sidechain phase method; selectable.
7. **Mix/master rework:** M/S mono-below-~100 Hz; chain = multiband sat → EQ (mud cut) →
   multiband comp → true-peak limiter -1.0 dBTP; DUAL LUFS masters; reference-spectrum
   diff vs a Glosolalia WAV (drop the invented band-%).
8. **Texture bus (Psykovsky):** events NOT snapped to the 8-bar grid; iterative
   resample→process→resample helper.
9. **Arrangement engine:** parametric section lengths; generate the 1-9 energy curve
   BEFORE note placement; top-level MODE switch darkpsy vs forest; element-level pre-drop dip.
10. **Reaper agent** (`build_session.py`): emit a MASTER bus with the mastering chain
    order + a TEXTURE bus + a low-end group (kick+bass). `live_control.py`: macros that
    drive FM index / KranchDD / S&H (not just volume) + silence_drop / order_lock /
    chaos_burst / breathe (forest) + interlock_mode toggle.
11. **Tempo as first-class** (currently fixed 150): BPM≥170 → bias FM weight up.

---

## Verified from Kindzadza's own tutorials (transcripts in `forja/research_transcripts/`)

**Kick & Bass Synthesis (Bitwig Grid)** — directly from KinDzaDza:
- Works at **150 BPM**; kick + bass **always grouped** so he can see them together.
- Bass = **sawtooth ("softest") osc → ladder filter**, **two oscillators** (one an octave down).
- **TWO filter envelopes (AD):** one shapes *"the very first part of the bassline"* (punch/attack),
  the other shapes *"the body"*. → richer than a single filter env; encode as attack-env + body-env.
- **PHASE LOCK (his emphasis):** *"the wave starts from a different position every time… we lock
  the phase so every note starts from the same position… very nice especially on fast 16th
  basslines."* He routes a value (~100%) into the **phase input** of both oscillators. → CONFIRMS
  the bass phase-retrigger grammar, from the source. Make phase-start a controllable param.
- **Kick/bass interlock = visual:** uses an **oscilloscope** to align kick+bass waveforms on the low
  end (*"very important to see this waveform… how they mix on low frequencies"*). → the
  no-sidechain phase/time method, done by eye. Engine: align kick tail vs bass phase, verify by
  low-band correlation, not a blind duck.
- **Resampling for breaks** (other tutorial): bounce the master section → drop into a **sampler** →
  **granular** (grain size + speed; speed 0 = single grain) → **automate grain pitch up** →
  filter on the break. → confirms our granular/texture bus + the resample→process→resample loop.

*Research: Claude (multi-agent + video transcripts). Direction: Juan. For the DarkPsy engine.*
