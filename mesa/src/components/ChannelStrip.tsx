import { useState } from "react";
import type { StemSpec } from "../types";
import Knob from "./Knob";

interface Props {
  spec: StemSpec;
  onVolume: (linear: number) => void;
  onMute: () => boolean;
  onSolo: () => boolean;
  onCutoff: (knob: number) => void;
}

export default function ChannelStrip({ spec, onVolume, onMute, onSolo, onCutoff }: Props) {
  const [vol, setVol] = useState(spec.defaultGain);
  const [cutoff, setCutoff] = useState(1);
  const [muted, setMuted] = useState(false);
  const [solo, setSolo] = useState(false);
  const accent = spec.color;

  return (
    <div className={`module ${muted ? "off" : ""}`} style={{ ["--accent" as string]: accent }} title={spec.tip}>
      <div className="module-plate">
        <span className="led" style={{ background: muted ? "#2a2d34" : accent, boxShadow: muted ? "none" : `0 0 6px ${accent}` }} />
        <span className="module-name">{spec.label}</span>
      </div>

      <Knob value={cutoff} color={accent} size={50} label="CUT"
        onChange={(v) => { setCutoff(v); onCutoff(v); }} />

      <div className="hfader">
        <input
          type="range" min={0} max={1.5} step={0.01} value={vol}
          onChange={(e) => { const v = +e.target.value; setVol(v); onVolume(v); }}
          style={{ ["--accent" as string]: accent }}
        />
      </div>

      <div className="module-btns">
        <button className={`hbtn ${solo ? "on solo" : ""}`} onClick={() => setSolo(onSolo())}>S</button>
        <button className={`hbtn ${muted ? "on mute" : ""}`} onClick={() => setMuted(onMute())}>M</button>
      </div>
    </div>
  );
}
