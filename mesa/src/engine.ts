import * as Tone from "tone";
import type { Preset, StemSpec } from "./types";

// Stems whose distortion swells as the ORDER->CHAOS macro is pushed.
// "user" = an imported full track, so the macro dirties it too.
const CHAOS_DRIVE = new Set(["bass", "acid", "lead", "fm", "user"]);
// Stems whose level rises with chaos (texture/risers come forward).
const CHAOS_BOOST: Record<string, number> = { fm: 3.0, fx: 1.0 };

interface StemNodes {
  spec: StemSpec;
  player: Tone.Player;
  filter: Tone.Filter;
  dist: Tone.Distortion;
  gain: Tone.Gain;
  userGain: number;
  cutoff: number;
  muted: boolean;
  solo: boolean;
}

const wait = (ms: number) => new Promise<void>((r) => setTimeout(r, ms));

const KNOB_MIN_HZ = 120;
const KNOB_MAX_HZ = 18000;
export function knobToHz(k: number): number {
  return KNOB_MIN_HZ * Math.pow(KNOB_MAX_HZ / KNOB_MIN_HZ, Math.min(1, Math.max(0, k)));
}

export class AudioEngine {
  bpm: number;
  stems: StemNodes[] = [];
  private masterBus!: Tone.Gain;
  private out!: Tone.Gain;
  private reverb!: Tone.Reverb;
  private revWet!: Tone.Gain;
  private delay!: Tone.FeedbackDelay;
  private delWet!: Tone.Gain;
  analyser!: Tone.Analyser;
  chaos = 0;
  playing = false;
  loaded = false;

  constructor(bpm: number) {
    this.bpm = bpm;
  }

  // Set up Tone + the master bus graph (no stems yet).
  async init() {
    await Tone.start();
    Tone.getTransport().bpm.value = this.bpm;

    this.masterBus = new Tone.Gain(1);
    this.out = new Tone.Gain(0.9).toDestination();
    this.analyser = new Tone.Analyser("fft", 1024);
    this.analyser.smoothing = 0.7;

    this.reverb = new Tone.Reverb({ decay: 3.2, preDelay: 0.02, wet: 1 });
    this.revWet = new Tone.Gain(0).toDestination();
    this.delay = new Tone.FeedbackDelay({ delayTime: "8n", feedback: 0.34, wet: 1 });
    this.delWet = new Tone.Gain(0).toDestination();

    this.masterBus.connect(this.out);
    this.masterBus.connect(this.analyser);
    this.masterBus.connect(this.reverb);
    this.reverb.connect(this.revWet);
    this.masterBus.connect(this.delay);
    this.delay.connect(this.delWet);
    // never hang on impulse generation
    await Promise.race([this.reverb.ready, wait(2500)]);
    console.info("[engine] init done");
  }

  private addStem(spec: StemSpec, player: Tone.Player) {
    const filter = new Tone.Filter({ type: "lowpass", frequency: KNOB_MAX_HZ, rolloff: -24, Q: 0.7 });
    const dist = new Tone.Distortion({ distortion: 0.65, wet: 0 });
    const gain = new Tone.Gain(spec.defaultGain);
    player.chain(filter, dist, gain, this.masterBus);
    this.stems.push({ spec, player, filter, dist, gain, userGain: spec.defaultGain, cutoff: 1, muted: false, solo: false });
  }

  async loadPreset(preset: Preset) {
    for (const spec of preset.stems) {
      const player = new Tone.Player({
        url: spec.url,
        loop: true,
        onerror: (e) => console.error(`[engine] failed to load ${spec.url}`, e),
      });
      this.addStem(spec, player);
    }
    // never hang: if a buffer 404s or stalls, proceed after a cap and play what loaded
    await Promise.race([Tone.loaded(), wait(8000)]);
    this.loaded = true;
    console.info(`[engine] loaded ${this.stems.length} stems`);
  }

  // Pro path: load the user's own decoded track as a single tweakable stem.
  loadUserBuffer(buffer: AudioBuffer, label = "Tu pista") {
    const spec: StemSpec = {
      name: "user", label, url: "", defaultGain: 0.9,
      band: "full", color: "#ffd23f", tip: "Tu pista importada.", rmsDb: 0,
    };
    const player = new Tone.Player(buffer);
    player.loop = true;
    this.addStem(spec, player);
    this.loaded = true;
  }

  play() {
    if (this.playing || !this.loaded) return;
    const t = Tone.now() + 0.08; // one shared, sample-accurate start time
    for (const s of this.stems) s.player.start(t);
    this.playing = true;
  }

  stop() {
    if (!this.playing) return;
    for (const s of this.stems) s.player.stop();
    this.playing = false;
  }

  private anySolo(): boolean {
    return this.stems.some((s) => s.solo);
  }

  private applyGain(s: StemNodes) {
    const solo = this.anySolo();
    const audible = !s.muted && (!solo || s.solo);
    const boost = 1 + this.chaos * (CHAOS_BOOST[s.spec.name] ?? 0);
    s.gain.gain.rampTo(audible ? s.userGain * boost : 0, 0.02);
  }

  private applyAllGains() {
    for (const s of this.stems) this.applyGain(s);
  }

  setVolume(name: string, linear: number) {
    const s = this.stems.find((x) => x.spec.name === name);
    if (!s) return;
    s.userGain = linear;
    this.applyGain(s);
  }

  toggleMute(name: string): boolean {
    const s = this.stems.find((x) => x.spec.name === name);
    if (!s) return false;
    s.muted = !s.muted;
    this.applyAllGains();
    return s.muted;
  }

  toggleSolo(name: string): boolean {
    const s = this.stems.find((x) => x.spec.name === name);
    if (!s) return false;
    s.solo = !s.solo;
    this.applyAllGains();
    return s.solo;
  }

  setCutoff(name: string, knob: number) {
    const s = this.stems.find((x) => x.spec.name === name);
    if (!s) return;
    s.cutoff = knob;
    s.filter.frequency.rampTo(knobToHz(knob), 0.015);
  }

  // The hero macro. c in [0,1]: 0 = ORDER (tight, clean, dry), 1 = CHAOS (dirty, wide, alive).
  setChaos(c: number) {
    this.chaos = Math.min(1, Math.max(0, c));
    for (const s of this.stems) {
      const w = CHAOS_DRIVE.has(s.spec.name) ? this.chaos * 0.5 : 0;
      s.dist.wet.rampTo(w, 0.08);
    }
    this.revWet.gain.rampTo(this.chaos * 0.32, 0.1);
    this.delWet.gain.rampTo(this.chaos * 0.28, 0.1);
    this.applyAllGains();
  }

  dispose() {
    this.stop();
    for (const s of this.stems) {
      s.player.dispose(); s.filter.dispose(); s.dist.dispose(); s.gain.dispose();
    }
    this.stems = [];
    this.masterBus?.dispose(); this.out?.dispose(); this.analyser?.dispose();
    this.reverb?.dispose(); this.revWet?.dispose(); this.delay?.dispose(); this.delWet?.dispose();
  }
}
