import type { Level } from "../types";

interface Props {
  onPick: (level: Level) => void;
}

const LEVELS: { id: Level; title: string; blurb: string; detail: string }[] = [
  {
    id: "novato",
    title: "Novato",
    blurb: "Nunca hice música",
    detail: "Te llevo de la mano. Generás tu primera canción con un botón y te voy mostrando qué hace cada cosa.",
  },
  {
    id: "intermedio",
    title: "Intermedio",
    blurb: "Algo de experiencia",
    detail: "Vas directo a generar y tweakear, con la galería de vibes a mano y tips cuando los necesites.",
  },
  {
    id: "pro",
    title: "Pro",
    blurb: "Hago mi música",
    detail: "Todas las herramientas a la vista. Generá, o traé tu propia pista y empezá a modificarla.",
  },
];

export default function LevelScreen({ onPick }: Props) {
  return (
    <div className="screen level">
      <h2 className="screen-title">¿Cómo venís con la música?</h2>
      <p className="screen-sub">Elegí tu nivel. Después podés cambiarlo cuando quieras.</p>
      <div className="level-cards">
        {LEVELS.map((l) => (
          <button key={l.id} className={`level-card ${l.id}`} onClick={() => onPick(l.id)}>
            <h3>{l.title}</h3>
            <span className="blurb">{l.blurb}</span>
            <p>{l.detail}</p>
            <span className="go">elegir →</span>
          </button>
        ))}
      </div>
    </div>
  );
}
