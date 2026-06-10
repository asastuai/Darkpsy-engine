import { useEffect, useRef } from "react";
import type * as Tone from "tone";

interface Props {
  analyser: Tone.Analyser | null;
  active: boolean;
}

// Full-width hardware spectrum analyzer (fills the LCD immediately, pulses live).
export default function Spectrogram({ analyser, active }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const raf = useRef(0);
  const peaks = useRef<number[]>([]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !analyser) return;
    const ctx = canvas.getContext("2d")!;
    const dpr = devicePixelRatio || 1;
    const resize = () => { canvas.width = canvas.clientWidth * dpr; canvas.height = canvas.clientHeight * dpr; };
    resize();
    const ro = new ResizeObserver(resize);
    ro.observe(canvas);

    const BARS = 72;
    if (peaks.current.length !== BARS) peaks.current = new Array(BARS).fill(0);

    const draw = () => {
      raf.current = requestAnimationFrame(draw);
      const W = canvas.width, H = canvas.height;
      const data = analyser.getValue() as Float32Array;
      const n = data.length;
      ctx.fillStyle = "#04080a";
      ctx.fillRect(0, 0, W, H);

      const gap = 2 * dpr;
      const bw = (W - (BARS + 1) * gap) / BARS;
      for (let i = 0; i < BARS; i++) {
        const f0 = Math.floor(Math.pow(i / BARS, 1.9) * n);
        const f1 = Math.max(f0 + 1, Math.floor(Math.pow((i + 1) / BARS, 1.9) * n));
        let m = -200;
        for (let b = f0; b < Math.min(n, f1); b++) m = Math.max(m, data[b]);
        const mag = Math.min(1, Math.max(0, (m + 92) / 84));
        const h = mag * H * 0.9;
        const x = gap + i * (bw + gap);
        const hue = 185 + (i / BARS) * 150; // cyan -> magenta
        const grad = ctx.createLinearGradient(0, H, 0, H - h);
        grad.addColorStop(0, `hsla(${hue}, 100%, 50%, 0.95)`);
        grad.addColorStop(1, `hsla(${hue}, 100%, 72%, 0.95)`);
        ctx.fillStyle = grad;
        ctx.shadowColor = `hsl(${hue}, 100%, 60%)`;
        ctx.shadowBlur = 7 * dpr;
        ctx.fillRect(x, H - h, bw, h);

        // peak-hold cap
        const p = (peaks.current[i] = Math.max(h, peaks.current[i] * 0.92));
        ctx.shadowBlur = 0;
        ctx.fillStyle = `hsla(${hue}, 100%, 80%, 0.9)`;
        ctx.fillRect(x, H - p - 2 * dpr, bw, 2 * dpr);
      }
      ctx.shadowBlur = 0;
    };

    if (active) draw();
    return () => { cancelAnimationFrame(raf.current); ro.disconnect(); };
  }, [analyser, active]);

  return <canvas ref={canvasRef} className="spectrogram" />;
}
