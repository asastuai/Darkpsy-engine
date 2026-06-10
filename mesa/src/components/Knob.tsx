import { useCallback, useRef } from "react";

interface KnobProps {
  value: number; // 0..1
  onChange: (v: number) => void;
  color?: string;
  size?: number;
  label?: string;
}

// Chunky skeuomorphic hardware knob: metal cap, tick ring, lit value arc, indicator.
export default function Knob({ value, onChange, color = "#21e6ff", size = 56, label }: KnobProps) {
  const dragging = useRef(false);
  const lastY = useRef(0);

  const onPointerDown = useCallback((e: React.PointerEvent) => {
    dragging.current = true; lastY.current = e.clientY;
    (e.target as Element).setPointerCapture(e.pointerId);
  }, []);
  const onPointerMove = useCallback((e: React.PointerEvent) => {
    if (!dragging.current) return;
    const dy = lastY.current - e.clientY; lastY.current = e.clientY;
    onChange(Math.min(1, Math.max(0, value + dy / 160)));
  }, [value, onChange]);
  const onPointerUp = useCallback((e: React.PointerEvent) => {
    dragging.current = false;
    try { (e.target as Element).releasePointerCapture(e.pointerId); } catch { /* noop */ }
  }, []);
  const onWheel = useCallback((e: React.WheelEvent) => {
    onChange(Math.min(1, Math.max(0, value - Math.sign(e.deltaY) * 0.03)));
  }, [value, onChange]);

  const A0 = -135, SWEEP = 270;
  const ang = A0 + SWEEP * value;
  const cx = size / 2, cy = size / 2, r = size / 2 - 3;
  const rad = (d: number) => (d - 90) * (Math.PI / 180);
  const arc = (from: number, to: number) => {
    const large = to - from > 180 ? 1 : 0;
    const x1 = cx + r * Math.cos(rad(from)), y1 = cy + r * Math.sin(rad(from));
    const x2 = cx + r * Math.cos(rad(to)), y2 = cy + r * Math.sin(rad(to));
    return `M ${x1} ${y1} A ${r} ${r} 0 ${large} 1 ${x2} ${y2}`;
  };
  const ticks = Array.from({ length: 11 }, (_, i) => A0 + (SWEEP / 10) * i);

  return (
    <div className="hknob" style={{ width: size }}
      onPointerDown={onPointerDown} onPointerMove={onPointerMove} onPointerUp={onPointerUp} onWheel={onWheel}>
      <div className="hknob-dial" style={{ width: size, height: size }}>
        <svg width={size} height={size} style={{ position: "absolute", inset: 0, touchAction: "none" }}>
          {ticks.map((t, i) => {
            const x1 = cx + (r) * Math.cos(rad(t)), y1 = cy + (r) * Math.sin(rad(t));
            const x2 = cx + (r - 4) * Math.cos(rad(t)), y2 = cy + (r - 4) * Math.sin(rad(t));
            return <line key={i} x1={x1} y1={y1} x2={x2} y2={y2} stroke="#3a3e47" strokeWidth={1.5} />;
          })}
          <path d={arc(A0, A0 + SWEEP)} stroke="#202329" strokeWidth={2.5} fill="none" strokeLinecap="round" />
          <path d={arc(A0, ang)} stroke={color} strokeWidth={2.5} fill="none" strokeLinecap="round"
            style={{ filter: `drop-shadow(0 0 4px ${color})` }} />
        </svg>
        <div className="hknob-cap" />
        <div className="hknob-rot" style={{ transform: `rotate(${ang}deg)` }}>
          <span className="hknob-ind" style={{ background: color, boxShadow: `0 0 6px ${color}` }} />
        </div>
      </div>
      {label && <span className="hknob-label">{label}</span>}
    </div>
  );
}
