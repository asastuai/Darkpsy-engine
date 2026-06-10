interface Props {
  onStart: () => void;
}

export default function IntroScreen({ onStart }: Props) {
  return (
    <div className="screen intro">
      <h1 className="brand">DARK<span>PSY</span></h1>
      <p className="tagline">tu motor de dark psytrance, vivo en el navegador</p>

      <div className="intro-cols">
        <div className="intro-card">
          <span className="ic">◆</span>
          <h3>Generá</h3>
          <p>El motor compone la pista: orden, caos, silencio y drops. Timbre real de Surge XT.</p>
        </div>
        <div className="intro-card">
          <span className="ic">◆</span>
          <h3>Separá</h3>
          <p>Cada elemento es un stem propio. Muteá, soleá, filtrá. Escuchá la anatomía del track.</p>
        </div>
        <div className="intro-card">
          <span className="ic">◆</span>
          <h3>Tweakeá en vivo</h3>
          <p>Una sola perilla ORDEN↔CAOS mueve la energía de todo el track. Sin latencia.</p>
        </div>
      </div>

      <button className="play-big" onClick={onStart}>EMPEZAR →</button>
      <p className="sub">hecho artesanal · J. &amp; C.</p>
    </div>
  );
}
