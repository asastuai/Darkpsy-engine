import { useRef, useState } from "react";
import type { Level, Preset } from "../types";

export interface SessionRequest {
  instructions: string;
  file?: File;
  presetId?: string;
}

interface Props {
  level: Level;
  presets: Preset[];
  onSubmit: (req: SessionRequest) => void;
  onBack: () => void;
}

const COPY: Record<Level, { greet: string; placeholder: string }> = {
  pro: {
    greet: "Dejame la canción con la que querés arrancar y unas instrucciones de qué querés hacerle. Adjuntá tu pista y empezamos.",
    placeholder: "ej: bajá los agudos del bajo, más caos en el dro p, dejalo más oscuro…",
  },
  intermedio: {
    greet: "¿Con qué tema arrancamos? Subí una canción y contame qué te gustaría tocar. Si querés, agarrá una de las mías.",
    placeholder: "ej: quiero un groove más hipnótico y filtrar el lead…",
  },
  novato: {
    greet: "¡Dale! ¿Con qué canción querés arrancar? Subí una tuya. Y si no tenés ninguna, agarrá una de las mías acá abajo y yo te voy guiando 😉",
    placeholder: "contame qué querés (o dejalo vacío, no pasa nada)…",
  },
};

export default function ChatScreen({ level, presets, onSubmit, onBack }: Props) {
  const [text, setText] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [presetId, setPresetId] = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);
  const copy = COPY[level];
  const canSend = !!file || !!presetId;

  const send = () => {
    if (!canSend) return;
    onSubmit({ instructions: text.trim(), file: file ?? undefined, presetId: presetId ?? undefined });
  };

  return (
    <div className="chat-screen">
      <header className="rail-top">
        <h1 className="brand-plate">DARK<span>PSY</span></h1>
        <button className="ghost-btn" onClick={onBack}>← nivel: {level}</button>
      </header>

      <div className="chat-window">
        <div className="bubble system">{copy.greet}</div>
        {(file || presetId) && (
          <div className="bubble user">
            📎 {file ? file.name : presets.find((p) => p.id === presetId)?.label}
            {text && <> — “{text}”</>}
          </div>
        )}
      </div>

      {level === "novato" || level === "intermedio" ? (
        <div className="preset-chips">
          <span className="chips-label">o usá una mía:</span>
          {presets.map((p) => (
            <button
              key={p.id}
              className={`chip ${presetId === p.id ? "on" : ""}`}
              onClick={() => { setPresetId(p.id); setFile(null); }}
              title={p.desc}
            >{p.label}</button>
          ))}
        </div>
      ) : null}

      <div className="chat-input">
        <button
          className="attach"
          title="adjuntar canción"
          onClick={() => fileRef.current?.click()}
        >📎</button>
        <input
          ref={fileRef} type="file" accept="audio/*" hidden
          onChange={(e) => { const f = e.target.files?.[0]; if (f) { setFile(f); setPresetId(null); } }}
        />
        <textarea
          className="chat-text"
          rows={1}
          placeholder={copy.placeholder}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } }}
        />
        <button className={`send ${canSend ? "ready" : ""}`} onClick={send} disabled={!canSend}>➤</button>
      </div>
      <p className="chat-foot">
        {file ? `listo: ${file.name}` : presetId ? "listo: usás una pista mía" : "adjuntá una canción para empezar"}
      </p>
    </div>
  );
}
