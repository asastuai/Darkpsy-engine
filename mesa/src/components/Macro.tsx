import { useRef } from "react";

interface Props {
  value: number; // 0 = ORDER, 1 = CHAOS
  onChange: (v: number) => void;
}

const lerp = (a: number, b: number, t: number) => Math.round(a + (b - a) * t);
const mix = (t: number) =>
  `rgb(${lerp(0x21, 0xff, t)}, ${lerp(0xe6, 0x2b, t)}, ${lerp(0xff, 0xd0, t)})`; // cyan -> magenta

// The hero: a big hardware rotary. ORDER (cyan) on the left, CHAOS (magenta) on the right.
export default function Macro({ value, onChange }: Props) {
  const dragging = useRef(false);
  const lastY = useRef(0);
  const size = 150;

  const down = (e: React.PointerEvent) => { dragging.current = true; lastY.current = e.clientY; (e.target as Element).setPointerCapture(e.pointerId); };
  const move = (e: React.PointerEvent) => { if (!dragging.current) return; const dy = lastY.current - e.clientY; lastY.current = e.clientY; onChange(Math.min(1, Math.max(0, value + dy / 220))); };
  const up = (e: React.PointerEvent) => { dragging.current = false; try { (e.target as Element).releasePointerCapture(e.pointerId); } catch { /* noop */ } };
  const wheel = (e: React.WheelEvent) => onChange(Math.min(1, Math.max(0, value - Math.sign(e.deltaY) * 0.02)));

  const A0 = -135, SWEEP = 270;
  const ang = A0 + SWEEP * value;
  const cx = size / 2, cy = size / 2, r = size / 2 - 6;
  const rad = (d: number) => (d - 90) * (Math.PI / 180);
  const arc = (from: number, to: number) => {
    const large = to - from > 180 ? 1 : 0;
    const x1 = cx + r * Math.cos(rad(from)), y1 = cy + r * Math.sin(rad(from));
    const x2 = cx + r * Math.cos(rad(to)), y2 = cy + r * Math.sin(rad(to));
    return `M ${x1} ${y1} A ${r} ${r} 0 ${large} 1 ${x2} ${y2}`;
  };
  const col = mix(value);
  const ticks = Array.from({ length: 21 }, (_, i) => A0 + (SWEEP / 20) * i);

  return (
    <div className="macro2">
      <span className="macro2-side order">ORDEN</span>
      <div className="macro2-dial" style={{ width: size, height: size }}
        onPointerDown={down} onPointerMove={move} onPointerUp={up} onWheel={wheel}>
        <svg width={size} height={size} style={{ position: "absolute", inset: 0, touchAction: "none" }}>
          <defs>
            <linearGradient id="macroArc" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stopColor="#21e6ff" />
              <stop offset="100%" stopColor="#ff2bd0" />
            </linearGradient>
          </defs>
          {ticks.map((t, i) => {
            const lit = (i / 20) <= value;
            const x1 = cx + r * Math.cos(rad(t)), y1 = cy + r * Math.sin(rad(t));
            const x2 = cx + (r - 6) * Math.cos(rad(t)), y2 = cy + (r - 6) * Math.sin(rad(t));
            return <line key={i} x1={x1} y1={y1} x2={x2} y2={y2}
              stroke={lit ? mix(i / 20) : "#33373f"} strokeWidth={lit ? 2 : 1.4}
              style={lit ? { filter: `drop-shadow(0 0 2px ${mix(i / 20)})` } : undefined} />;
          })}
          <path d={arc(A0, A0 + SWEEP)} stroke="#1c1f25" strokeWidth={4} fill="none" strokeLinecap="round" />
          <path d={arc(A0, ang)} stroke="url(#macroArc)" strokeWidth={4} fill="none" strokeLinecap="round"
            style={{ filter: `drop-shadow(0 0 6px ${col})` }} />
        </svg>
        <div className="macro2-cap" />
        <div className="macro2-rot" style={{ transform: `rotate(${ang}deg)` }}>
          <span className="macro2-ind" style={{ background: col, boxShadow: `0 0 10px ${col}` }} />
        </div>
        <div className="macro2-readout" style={{ color: col }}>
          {Math.round(value * 100)}
        </div>
      </div>
      <span className="macro2-side chaos">CAOS</span>
    </div>
  );
}
