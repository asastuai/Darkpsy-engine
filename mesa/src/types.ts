// The FORJA -> MESA contract. Mirror of forja/build_manifest.py (schemaVersion 2).
export interface StemSpec {
  name: string;
  label: string;
  url: string;
  defaultGain: number; // linear mix fader baked by FORJA
  band: string;
  color: string;
  tip: string;
  rmsDb: number;
}

export interface SectionBlock {
  label: string; // order | chaos | drop | silence | break | build | intro | outro
  startBar: number;
  endBar: number;
  chaos: number; // 0..1
}

export interface Preset {
  id: string;
  label: string;
  desc: string;
  loop: { bars: number; durationSec: number; sourceBars: [number, number] };
  smap: SectionBlock[];
  stems: StemSpec[];
}

export interface Library {
  schemaVersion: number;
  seed: number;
  bpm: number;
  root: string;
  presets: Preset[];
}

export type Level = "novato" | "intermedio" | "pro";
