import { useEffect, useState } from "react";
import type { AudioEngine } from "../engine";
import type { Level } from "../types";
import ChannelStrip from "../components/ChannelStrip";
import Macro from "../components/Macro";
import Spectrogram from "../components/Spectrogram";

export interface TabView {
  id: string;
  name: string;
  instructions: string;
}

interface Props {
  engine: AudioEngine;
  tabs: TabView[];
  activeId: string;
  level: Level;
  playing: boolean;
  chaos: number;
  bpm: number;
  onSwitch: (id: string) => void;
  onClose: (id: string) => void;
  onNew: () => void;
  onToggleTransport: () => void;
  onChaos: (v: number) => void;
}

const NOVATO_TIPS = [
  "PROBÁ: apretá M en el KICK y escuchá cómo se cae el piso.",
  "Apretá S en un módulo para escucharlo solo.",
  "Girá la perilla central ORDEN→CAOS y sentí el track volverse salvaje.",
  "Bajá la perilla CUT de un módulo y se va tapando.",
];

export default function Workspace(props: Props) {
  const { engine, tabs, activeId, level, playing, chaos, bpm } = props;
  const [tip, setTip] = useState(0);
  const active = tabs.find((t) => t.id === activeId);
  const specs = engine.stems.map((s) => s.spec);

  useEffect(() => {
    if (level !== "novato") return;
    const id = setInterval(() => setTip((t) => (t + 1) % NOVATO_TIPS.length), 6500);
    return () => clearInterval(id);
  }, [level]);

  return (
    <div className="machine">
      {/* top rail: brand + patch tabs */}
      <div className="rail">
        <div className="brand-plate">DARK<span>PSY</span></div>
        <div className="tabs">
          {tabs.map((t) => (
            <button key={t.id} className={`ptab ${t.id === activeId ? "on" : ""}`} onClick={() => props.onSwitch(t.id)} title={t.instructions}>
              <span className="ptab-led" />
              <span className="ptab-name">{t.name}</span>
              {tabs.length > 1 && <span className="ptab-x" onClick={(e) => { e.stopPropagation(); props.onClose(t.id); }}>×</span>}
            </button>
          ))}
          <button className="ptab new" onClick={props.onNew}>+ NUEVO</button>
        </div>
      </div>

      {/* LCD screen */}
      <div className="screen-bezel">
        <div className="lcd">
          <Spectrogram key={activeId} analyser={engine.analyser} active={true} />
          <div className="lcd-scan" />
          <div className="lcd-hud">
            <span>{bpm} BPM</span>
            <span className="lcd-name">{active?.name}</span>
            {active?.instructions && <span className="lcd-instr">“{active.instructions}”</span>}
          </div>
        </div>
      </div>

      {level === "novato" && <div className="ticker">{NOVATO_TIPS[tip]}</div>}

      {/* hero macro */}
      <div className="macro-zone">
        <Macro value={chaos} onChange={props.onChaos} />
      </div>

      {/* channel modules */}
      <div className="rack">
        {specs.map((s) => (
          <ChannelStrip
            key={`${activeId}-${s.name}`}
            spec={s}
            onVolume={(v) => engine.setVolume(s.name, v)}
            onMute={() => engine.toggleMute(s.name)}
            onSolo={() => engine.toggleSolo(s.name)}
            onCutoff={(k) => engine.setCutoff(s.name, k)}
          />
        ))}
      </div>

      {/* transport */}
      <div className="deck">
        <button className={`transport-btn ${playing ? "playing" : ""}`} onClick={props.onToggleTransport}>
          <span className="t-led" />
          {playing ? "■ STOP" : "▶ PLAY"}
        </button>
      </div>
    </div>
  );
}
