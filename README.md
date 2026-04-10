# DarkPsy Engine — AI-Generated Dark Psytrance

An experimental dark psytrance music generation engine built entirely in Python, calibrated against professional reference tracks (Glosolalia) and informed by production research on Psykovsky, Kindzadza, Frantic Noise, Will O Wisp, Zik, and Orestis.

## The Concept

This project explores the limits of AI-generated music by iterating through increasingly sophisticated synthesis and composition techniques, guided by human creative direction.

The core philosophy discovered through iteration:

```
ORDER (dance) <-> SILENCE (anticipation) <-> CHAOS (mind-bending)
```

- **ORDER**: Locked 4/4 kick, rolling bass at 1/16, clean groove. People dance.
- **SILENCE**: 1-2 bars of nothing. The brain expects the next beat. Tension builds.
- **CHAOS**: FM synthesis, granular textures, filter FM. Everything explodes.
- **THE DROP**: Re-entry after silence is NOT a machine gun burst. It's a shy kick, then bass joins, rhythm tightens, and by beat 4 you're back in the groove but HARDER.

## Version History

### v1 — Basic Structure
- First attempt: MIDI generation with `mido`
- Basic kick, bass, acid, hats, lead, pads
- 150 BPM, E Phrygian Dominant scale
- **Result**: Correct structure, no soul

### v2 — Calibrated Against Glosolalia
- Spectral analysis of 4 Glosolalia tracks
- Frequency band calibration (sub, bass, mids, presence)
- Stereo output, loudness matching (-9 dB RMS)
- Low-mid boost (6% -> 15%)
- **Result**: Better spectrum, still mechanical

### v3 — Humanization
- Groove extraction from Glosolalia kick patterns
- Micro-timing offsets, swing, velocity curves
- Pattern mutation (patterns evolve, never repeat exactly)
- Probabilistic note triggering
- Drum fills before section changes
- **Result**: More alive, but not enough contrast

### v4 — Genre-Accurate Techniques
- 300Hz notch on kick (dark psy signature)
- 2-layer kick (click/mallet + sub body), tuned to E
- Phase-designed bass (no sidechain, kick and bass interlock naturally)
- FM synthesis for alien textures
- Filter FM for "electricity" sound (HP with high resonance sweep)
- Granular resynthesis from bass and FM material
- Multiband saturation for mid harmonics
- **Result**: Closer to genre, but missing the ORDER vs CHAOS contrast

### v5 — Order vs Chaos
- Explicit section tagging: order, chaos, transition, breakdown
- Chaos amount parameter (0-1) controlling every element
- ORDER: locked groove, clean. CHAOS: entropic explosion
- Per-element behavior changes based on section type
- **Result**: Good concept, entropy contrast inverted

### v6 — The Drop (Machine Gun)
- Silence bars (absolute nothing before drops)
- Re-entry at 1/32 note speed
- Triplet drops
- Accelerating fills before silences
- **Result**: Correct concept, WRONG execution. 32 kicks per bar = assault, not music

### v7 — Musical Drops
- 5 different drop types that rotate:
  1. **Gradual**: shy kick alone, then builds
  2. **Dramatic**: big impact, space, then groove
  3. **Stutter**: quick musical doubles, not machine gun
  4. **Rolling**: bass-led re-entry
  5. **Triplet resolve**: starts in 3, resolves to 4/4
- Musical chaos patterns (not random positions)
- Musical fills (accelerating phrase, not linear density)
- 7.5 minutes, proper track length
- **Result**: Structure and drops work well. Sound design still basic.

### v8 — Kindzadza Processing
- KranchDD (Kindzadza's VST plugin) loaded via Spotify's `pedalboard`
- Multiband parallel processing through KranchDD
- Bass: heavy distortion + resonance
- Mids: aggressive alien processing
- Glue pass on full mix
- **Result**: Proof of concept for VST processing from Python. Sound needs better source material.

## Technical Stack

- **Python 3.12** — core engine
- **numpy** — audio buffer manipulation, signal generation
- **scipy** — filters (Butterworth), spectrogram analysis, WAV I/O
- **mido** — MIDI file generation (v1)
- **pedalboard** (Spotify) — VST3 plugin hosting from Python
- **KranchDD** (KINDZAudio) — Kindzadza's distortion/filter VST
- **Surge XT** — open-source synthesizer (loaded via pedalboard)

## Spectral Analysis — Glosolalia Reference Profile

Derived from analyzing 4 tracks: Blueprints, Motion of Celestial Objects, Strange Chaotic Attractor, Solve Et Coagula.

| Band | Glosolalia Avg | Description |
|------|---------------|-------------|
| Sub (20-60Hz) | 13% | Controlled, not overwhelming |
| Bass (60-200Hz) | 54% | Dominant — the rolling bass lives here |
| Low-Mid (200-600Hz) | 17% | Body, warmth, bass harmonics |
| Mid (600-2kHz) | 9% | Presence, leads, acid |
| High-Mid (2k-6kHz) | 3.8% | Definition, air |
| Presence (6k-10kHz) | 1.5% | Sparkle |
| Air (10k-20kHz) | 0.8% | Top end |

Additional metrics:
- **Entropy**: ~12.5 bits (high complexity)
- **Active frequency bands**: 8/10 simultaneously
- **Dramatic spectral changes**: 18% of the time
- **Rhythmic irregularity coefficient**: 3.86 (very irregular)
- **Stereo correlation**: 0.69 (significant L/R independence)

## Production Research — Dark Psytrance Artists

### Synths & DAWs Used by the Pros

| Artist | DAW | Key Synths |
|--------|-----|-----------|
| Psykovsky | FL Studio + Ableton | Nord Rack 2, Access Virus, Surge |
| Kindzadza | Bitwig | DDZynth (his own!), Waldorf Largo, Eurorack |
| Frantic Noise | Ableton | Vital (500+ presets), Serum |
| Will O Wisp | Ableton | Eurorack, VCV Rack, Mutable Instruments |

### Key Genre Techniques

**Kick**: 2-layer (click + sub body), 300Hz notch, tuned to root note, tight pitch envelope

**Rolling Bass**: Sawtooth -> LP filter at 40-60Hz -> amplitude envelope at 1/16 -> multiband saturation. Phase-designed to interlock with kick (no sidechain preferred).

**FM Synthesis**: Carrier sine, modulator saw/square, ratio 2:1 or 3:1. Automate modulation index for evolving textures.

**Filter FM** ("electricity" sound): HP filter with very high resonance, swept back and forth.

**Granular**: Field recordings or synth output -> break into micro-particles -> reconstruct with pitch/time manipulation.

**Wall of Sound**: New musical idea every 4-8 bars, careful EQ per layer, parallel compression (8:1-10:1 ratio).

## Key Musical Insights (from human creative direction)

1. **Order vs Chaos is the soul of dark psy** — people need structure to dance, chaos to lose their minds. The contrast between them is everything.

2. **Silence is the most powerful sound** — after intense buildup, when the brain expects the next beat, give it nothing. Then bring it back with MORE energy.

3. **Acceleration is musical, not mathematical** — doubling the note density sounds like a drill. Musical acceleration means a phrase that builds: shy entry -> confidence -> full groove.

4. **Nothing should repeat exactly** — patterns mutate, velocities breathe, timing drifts. The only constant is the kick in ORDER sections.

5. **A live set tells a story** — 1-2 hours of narrative, hundreds of transitions, the listener is taken on a journey.

## Next Steps

- [ ] Source quality samples (dark psy kicks, hats, percussion)
- [ ] Render MIDI through Surge XT via pedalboard for real synth bass/leads
- [ ] Load Vital presets for wavetable synthesis
- [ ] Obtain DDZynth (Kindzadza's granular/FM synth)
- [ ] Wavetables from Frantic Noise (franticnoise.gumroad.com)
- [ ] Longer tracks (10-15 min, closer to live set segments)
- [ ] More drop variations and transition types
- [ ] Deeper granular textures from resampled material

## Files

| File | Description |
|------|-------------|
| `synth_darkpsy_v7.py` | Current best engine (musical drops, order/chaos) |
| `process_v8b.py` | KranchDD processing pipeline |
| `generate_darkpsy.py` | Original MIDI generator (v1) |
| `create_reaper_project.py` | Reaper project file generator |
| `GUIA_SETUP.md` | Setup guide (Spanish) |

## Credits

- **Creative Direction**: Juan
- **Engine & Research**: Claude (Anthropic)
- **Reference Material**: Glosolalia (Dark Prisma Records)
- **Production Research**: Psykovsky, Kindzadza, Frantic Noise, Will O Wisp, Zik, Orestis
- **Tools**: KranchDD by KINDZAudio (Kindzadza), Surge XT, Reaper

---

*"The silence before the drop is the loudest part of the track"*
