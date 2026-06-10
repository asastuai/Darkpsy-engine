interface Props {
  title: string;
  stems: { label: string; color: string }[];
}

// Shown while a preset's stems load. Neon "cooking" reveal — each stem fills in.
export default function CookOverlay({ title, stems }: Props) {
  return (
    <div className="screen cook">
      <h2 className="cook-title">{title}</h2>
      <div className="cook-stems">
        {stems.map((s, i) => (
          <div className="cook-row" key={s.label} style={{ animationDelay: `${i * 0.18}s` }}>
            <span className="cook-name" style={{ color: s.color }}>{s.label}</span>
            <div className="cook-bar">
              <div
                className="cook-fill"
                style={{ background: s.color, animationDelay: `${i * 0.18}s`, boxShadow: `0 0 10px ${s.color}` }}
              />
            </div>
          </div>
        ))}
      </div>
      <p className="cook-sub">cocinando con Surge XT…</p>
    </div>
  );
}
