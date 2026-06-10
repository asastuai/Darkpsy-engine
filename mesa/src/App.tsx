import { useEffect, useRef, useState, type ReactNode } from "react";
import type { Library, Level, Preset } from "./types";
import { AudioEngine } from "./engine";
import DeviceFrame from "./components/DeviceFrame";
import IntroScreen from "./screens/IntroScreen";
import LevelScreen from "./screens/LevelScreen";
import ChatScreen, { type SessionRequest } from "./screens/ChatScreen";
import CookOverlay from "./screens/CookOverlay";
import Workspace from "./screens/Workspace";

type Screen = "loading" | "intro" | "level" | "chat" | "generating" | "workspace" | "error";

interface Tab {
  id: string;
  name: string;
  preset: Preset;
  instructions: string;
  chaos: number;
  bpm: number;
}

const RECREATE_URL = "http://localhost:8000/recreate";
const delay = (ms: number) => new Promise((r) => setTimeout(r, ms));
let TAB_SEQ = 0;

// Tiny instruction reader: map keywords to a starting ORDER<->CHAOS position.
function chaosFromText(t: string): number {
  const s = t.toLowerCase();
  let c = 0.15;
  if (/(caos|oscur|duro|agres|wild|salvaj|fuerte|intens|sucio|distors)/.test(s)) c = 0.7;
  if (/(orden|limpio|suave|tranq|bail|hipn|groov|minimal|claro)/.test(s)) c = Math.max(0, c - 0.4);
  return Math.min(1, c);
}

export default function App() {
  const [library, setLibrary] = useState<Library | null>(null);
  const [screen, setScreen] = useState<Screen>("loading");
  const [level, setLevel] = useState<Level>("intermedio");
  const [tabs, setTabs] = useState<Tab[]>([]);
  const [activeId, setActiveId] = useState<string>("");
  const [playing, setPlaying] = useState(false);
  const [chaos, setChaos] = useState(0);
  const [cookStems, setCookStems] = useState<{ label: string; color: string }[]>([]);
  const [cookTitle, setCookTitle] = useState("Cocinando…");
  const [errorMsg, setErrorMsg] = useState("");
  const engineRef = useRef<AudioEngine | null>(null);

  useEffect(() => {
    fetch("library.json")
      .then((r) => r.json())
      .then((lib: Library) => { setLibrary(lib); setScreen("intro"); })
      .catch(() => setScreen("loading"));
  }, []);

  const buildEngineFor = async (tab: Tab, dramaMs: number) => {
    setCookStems(tab.preset.stems.map((s) => ({ label: s.label, color: s.color })));
    setCookTitle(`Cocinando "${tab.name}"…`);
    setScreen("generating");

    const work = (async () => {
      engineRef.current?.dispose();
      const eng = new AudioEngine(tab.bpm);
      await eng.init();
      await eng.loadPreset(tab.preset);
      eng.setChaos(tab.chaos);
      eng.play();
      engineRef.current = eng;
      setPlaying(true);
      setChaos(tab.chaos);
    })();

    try {
      await Promise.all([work, delay(dramaMs)]);
      setActiveId(tab.id);
      setScreen("workspace");
    } catch (e) {
      console.error("[app] failed to build session", e);
      setErrorMsg(e instanceof Error ? e.message : String(e));
      setScreen("error");
    }
  };

  // Send a dropped/attached track to the local backend, separate it into stems,
  // and load each stem as its own tweakable module.
  const recreateFile = async (file: File, instructions: string) => {
    if (!library) return;
    setCookStems([
      { label: "bass", color: "#ff7a00" },
      { label: "drums", color: "#00e5ff" },
      { label: "synths", color: "#ff00bb" },
    ]);
    setCookTitle(`Separando "${file.name}" con Demucs…`);
    setScreen("generating");
    try {
      const form = new FormData();
      form.append("file", file);
      const res = await fetch(RECREATE_URL, { method: "POST", body: form });
      if (!res.ok) throw new Error("el backend respondió " + res.status);
      const data = await res.json();
      if (!data.stems?.length) throw new Error("no se pudieron separar stems de esta pista");
      const preset: Preset = {
        id: data.id, label: file.name.replace(/\.[^.]+$/, ""), desc: "tu pista, separada",
        loop: { bars: 0, durationSec: data.durationSec, sourceBars: [0, 0] },
        smap: [], stems: data.stems,
      };
      const tab: Tab = {
        id: `t${++TAB_SEQ}`, name: preset.label, preset,
        instructions, chaos: chaosFromText(instructions), bpm: data.bpm,
      };
      setTabs((prev) => [...prev, tab]);
      await buildEngineFor(tab, 300);
    } catch (e) {
      console.error("[recreate] backend falló", e);
      setErrorMsg(
        "No pude separar la pista. ¿Está corriendo el backend?\n\nEn C:/Users/Juan/Desktop/Darkpsy-engine corré:  python forja/server.py\n\nDetalle: " +
          (e instanceof Error ? e.message : String(e))
      );
      setScreen("error");
    }
  };

  const createSession = async (req: SessionRequest) => {
    if (!library) return;
    if (req.file) { await recreateFile(req.file, req.instructions); return; }
    const preset = library.presets.find((p) => p.id === req.presetId) ?? library.presets[0];
    const tab: Tab = {
      id: `t${++TAB_SEQ}`, name: preset.label, preset,
      instructions: req.instructions, chaos: chaosFromText(req.instructions), bpm: library.bpm,
    };
    setTabs((prev) => [...prev, tab]);
    await buildEngineFor(tab, level === "novato" ? 2600 : 1300);
  };

  const switchTab = async (id: string) => {
    if (id === activeId) return;
    const tab = tabs.find((t) => t.id === id);
    if (tab) await buildEngineFor(tab, 600);
  };

  const closeTab = (id: string) => {
    const remaining = tabs.filter((t) => t.id !== id);
    setTabs(remaining);
    if (id === activeId) {
      if (remaining.length) buildEngineFor(remaining[0], 400);
      else { engineRef.current?.dispose(); engineRef.current = null; setPlaying(false); setScreen("chat"); }
    }
  };

  const toggleTransport = () => {
    const eng = engineRef.current;
    if (!eng) return;
    if (eng.playing) { eng.stop(); setPlaying(false); }
    else { eng.play(); setPlaying(true); }
  };

  const onChaos = (v: number) => {
    setChaos(v);
    engineRef.current?.setChaos(v);
    setTabs((prev) => prev.map((t) => (t.id === activeId ? { ...t, chaos: v } : t)));
  };

  const eng = engineRef.current;
  let content: ReactNode;
  if (screen === "loading") content = <div className="screen center">cargando…</div>;
  else if (screen === "intro" && library) content = <IntroScreen onStart={() => setScreen("level")} />;
  else if (screen === "level") content = <LevelScreen onPick={(l) => { setLevel(l); setScreen("chat"); }} />;
  else if (screen === "chat" && library)
    content = (
      <ChatScreen level={level} presets={library.presets} onSubmit={createSession} onBack={() => setScreen("level")} />
    );
  else if (screen === "generating") content = <CookOverlay title={cookTitle} stems={cookStems} />;
  else if (screen === "error")
    content = (
      <div className="screen center" style={{ gap: 18 }}>
        <h2 className="screen-title">Algo falló al cargar</h2>
        <p className="screen-sub" style={{ maxWidth: 480 }}>{errorMsg || "Error desconocido."}</p>
        <button className="play-big" onClick={() => setScreen("chat")}>← volver a empezar</button>
      </div>
    );
  else if (screen === "workspace" && eng && library)
    content = (
      <Workspace
        engine={eng}
        tabs={tabs.map((t) => ({ id: t.id, name: t.name, instructions: t.instructions }))}
        activeId={activeId}
        level={level}
        playing={playing}
        chaos={chaos}
        bpm={tabs.find((t) => t.id === activeId)?.bpm ?? library.bpm}
        onSwitch={switchTab}
        onClose={closeTab}
        onNew={() => setScreen("chat")}
        onToggleTransport={toggleTransport}
        onChaos={onChaos}
      />
    );
  else content = <div className="screen center">…</div>;

  return <DeviceFrame>{content}</DeviceFrame>;
}
