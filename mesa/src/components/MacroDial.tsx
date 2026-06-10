import { useCallback, useRef } from "react";

interface Props {
  value: number; // 0 = ORDER, 1 = CHAOS
  onChange: (v: number) => void;
}

// The hero control. A wide horizontal lever ORDER <-> CHAOS.
export default function MacroDial({ value, onChange }: Props) {
  const ref = useRef<HTMLDivElement>(null);
  const dragging = useRef(false);

  const setFromX = useCallback(
    (clientX: number) => {
      const el = ref.current;
      if (!el) return;
      const r = el.getBoundingClientRect();
      onChange(Math.min(1, Math.max(0, (clientX - r.left) / r.width)));
    },
    [onChange]
  );

  return (
    <div className="macro">
      <span className="macro-side order">ORDER</span>
      <div
        ref={ref}
        className="macro-track"
        onPointerDown={(e) => { dragging.current = true; (e.target as Element).setPointerCapture(e.pointerId); setFromX(e.clientX); }}
        onPointerMove={(e) => { if (dragging.current) setFromX(e.clientX); }}
        onPointerUp={(e) => { dragging.current = false; try { (e.target as Element).releasePointerCapture(e.pointerId); } catch { /* noop */ } }}
        style={{ touchAction: "none" }}
      >
        <div className="macro-fill" style={{ width: `${value * 100}%` }} />
        <div className="macro-thumb" style={{ left: `${value * 100}%` }} />
      </div>
      <span className="macro-side chaos">CHAOS</span>
    </div>
  );
}
