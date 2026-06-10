# MESA — el instrumento vivo de DarkPsy (F1)

La mitad-navegador de la arquitectura **FORJA + MESA**. FORJA (Python) hornea
los stems con Surge XT; MESA los toca y los tweakeás en vivo en el browser.

## Correr en local

```bash
# 1. (FORJA) hornear stems con Surge XT  — desde la raiz del repo
python render_v9.py                  # genera stems_v9/*.wav (full track, ~7.5 min)
python forja/rerender_bass.py        # re-render del bass con KranchDD sanitizado
python forja/build_manifest.py       # recorta el loop -> mesa/public/{manifest.json,stems/}

# 2. (MESA) levantar el instrumento
cd mesa
npm install
npm run dev                          # http://localhost:5173
```

## Qué hace F1

- Carga 8 stems (kick, bass, drums, acid, lead, pad, fm, fx) y los toca en loop
  **sample-accurate** (todos arrancan en el mismo tick, mismo largo → sin drift).
- Por stem: **volumen, mute, solo, filtro** (lowpass, instantáneo, sin zipper).
- Macro **ORDER↔CHAOS** (mix-law): suma drive + reverb + delay y trae las texturas
  (fm/fx) al frente a medida que vas hacia CHAOS.
- **Spectrograma neón** en vivo (AnalyserNode → Canvas).

## Contrato FORJA → MESA

`public/manifest.json` (ver `forja/build_manifest.py` y `src/types.ts`) es la única
frontera: `{seed, bpm, root, loop, smap[], stems[]}`. Cambiá la ventana de loop con
`START_BAR`/`END_BAR` en `build_manifest.py`.

## Límites conocidos de F1 (siguiente: F2)

- La ventana es una sección `order` (bars 91-120), así que **fm queda en silencio**
  (es elemento de caos). El macro real "sumá capas de caos" necesita hornear varias
  ventanas y crossfadear → F2.
- Stems servidos como **WAV** (sin transcode). Para Vercel: webm/opus.
- Sin mastering/export todavía (Voxengo Elephant + LUFS) → F3.
- Macro = mix-law en stems horneados, no re-genera la música (eso es el COOK, F2/F3).
