# DarkPsy Engine — Paquete para Productor

## Que es esto

Un track de dark psytrance experimental generado por IA (composicion, estructura, drops) que necesita un productor humano para el sound design final y la mezcla.

La composicion esta lista. La estructura funciona. Los drops son musicales. Falta vestir los sonidos con caracter profesional y mezclar con oido.

## Specs

- **BPM**: 150
- **Key**: E Phrygian Dominant (E-F-G#-A-B-C-D)
- **Duracion**: 7.5 minutos
- **Formato**: Stems WAV 44.1kHz 16-bit stereo

## Estructura del track

```
0:00 - 0:16   INTRO
0:16 - 0:48   ORDER 1 (groove establecido)
0:48 - 0:51   [SILENCIO] + DROP musical
0:51 - 1:07   CHAOS 1
1:07 - 1:10   [SILENCIO] + DROP
1:10 - 1:52   ORDER 2 (groove largo)
1:52 - 1:55   [SILENCIO] + DROP
1:55 - 2:21   CHAOS 2
2:21 - 2:24   [SILENCIO] + DROP
2:24 - 3:12   ORDER 3 (groove principal + lead)
3:12 - 3:17   [SILENCIO] + DROP (CLIMAX)
3:17 - 3:57   CHAOS 3 (pico de intensidad)
3:57 - 4:00   [SILENCIO]
4:00 - 4:24   BREAKDOWN (pads + lead, matices de luz)
4:24 - 4:40   BUILD
4:40 - 4:43   [SILENCIO] + DROP
4:43 - 5:36   ORDER 4 (resolucion)
5:36 - 5:39   [SILENCIO] + DROP
5:39 - 6:24   CHAOS 4
6:24 - 6:27   [SILENCIO] + DROP
6:27 - 7:09   ORDER 5 (cierre)
7:09 - 7:28   OUTRO
```

Los silencios son de 1 bar (1.6 segundos). Los drops tienen 5 variaciones que rotan: gradual, dramatico, stutter, rolling, y triplet-resolve.

## Stems

| Stem | Contenido | Sound design sugerido |
|------|-----------|----------------------|
| `kick.wav` | 4/4 psy kick con fills | Buscar/disenar kick dark psy real. 300Hz notch, 2 capas. |
| `bass.wav` | Rolling bass E2 a 1/16 | Saw + sub, LP filter con envelope. Calidez tipo Pink Floyd pero con drive dark psy. |
| `acid.wav` | Linea acid tipo 303 | Saw, LP resonante, filter envelope rapido. Distorsion. |
| `lead.wav` | Melodia (matices de luz) | Supersaw o wavetable, reverb largo, delay ping-pong. Etereo. |
| `pad.wav` | Acordes atmosfericos | Pads amplios, chorus, reverb. Movimiento con LFO. |
| `fm_texture.wav` | Texturas FM alien | FM synthesis, metalico, delay. Solo en secciones CHAOS. |
| `drums.wav` | Hats, claps, perc | Reemplazar con samples reales de dark psy. |
| `fx.wav` | Risers e impacts | Noise sweeps, sub impacts en los drops. |

## Como trabajar con esto

### Opcion A: Reemplazar sonidos
1. Abrir los stems en tu DAW
2. Usar los stems como guia de timing
3. Crear nuevos tracks con los mismos patterns pero mejores sonidos
4. Los MIDI files estan en la carpeta del proyecto si preferis re-tocar desde MIDI

### Opcion B: Procesar los stems
1. Cargar los stems tal cual
2. Agregar FX chains por track (EQ, compression, distortion, reverb, delay)
3. Mezclar y masterizar

### Opcion C: Hibrido
1. Reemplazar kick y drums con samples
2. Re-sintetizar bass y acid con tu synth preferido (Vital, Serum, Surge XT)
3. Mantener pads y lead procesandolos con FX
4. Agregar tus propias texturas en las secciones CHAOS

## Referencia de sonido

Calibrado contra **Glosolalia** (Dark Prisma Records). Artistas de referencia:
- Psykovsky
- Kindzadza
- Frantic Noise
- Will O Wisp

## Filosofia del track

**ORDER vs CHAOS**: la gente necesita orden para bailar y caos para perder la cabeza. El contraste entre ambos es lo que define al dark psy.

**El silencio es un arma**: despues de una seccion intensa, cuando el cerebro espera el proximo beat, le das silencio. Cuando vuelve, no vuelve igual — vuelve con mas fuerza.

**Los drops son musicales**: no son una explosion de 32 kicks. Son una re-entrada gradual — un kick timido, despues el bass se suma, y en 4 beats estas de vuelta pero HARDER.

## Creditos

- Composicion y estructura: IA (Claude, Anthropic)
- Direccion creativa: Juan (@asastuai)
- Sound design y mezcla: [TU NOMBRE]
- Repo: github.com/asastuai/Darkpsy-engine
