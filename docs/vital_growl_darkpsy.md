# Bajo growl / electricidad (darkpsy) — VITAL

> Traducción dial por dial de la receta de Serum 2 a los controles **reales** de Vital. Donde Vital hace las cosas distinto a Serum, lo marco con **[DIFERENCIA]**. Donde la fuente es vaga, marco **(default sugerido)**.
>
> Lectura previa de honestidad: Vital NO es un FM operator synth ni un clon de Serum. El "growl" se arma igual de bien, pero el ruteo de FM y los filtros LP/BP/HP funcionan diferente. Seguí los pasos textuales, no la intuición de Serum.

---

## 0) Layout general antes de tocar nada

- **OSC 1** = carrier (el que suena y recibe la FM) → en Serum era "OSC A".
- **OSC 2** = modulador (modula a OSC1, no querés que suene solo) → en Serum era "OSC B".
- **OSC 3** = libre (reservado por si querés un sub; ver punto 9).
- Filtros: **Filter 1 → Filter 2 en SERIE**.
- LFO 1 = escalonado → barre el cutoff de Filter 1 = "la electricidad".
- FX rack reordenable: Distortion → Delay → EQ → Distortion #2.
- Macro 1 = cantidad de FM (el growl en la mano).

---

## 1) OSC 1 — carrier (ex OSC A)

| Control Vital | Valor | Notas |
|---|---|---|
| **On** | sí | encendido |
| **Wavetable** | Saw (carpeta Basic Shapes → Saw) | wavetable de diente de sierra |
| **Transpose** | **-12 semitonos (= octava abajo)** | en Vital la octava se baja con **Transpose** en pasos de 12 |
| **Unison Voices** | **1** | sin unison (igual que la receta) |
| **Phase** | fija + **Retrig ON** | abrí el control de **Phase** del osc (knob de fase), fijá una fase de arranque y activá el reinicio de fase por nota (equivalente al "fase fija + retrig" de Serum). **[NOTA]** En Vital esto es el knob de Phase del osc + opción de random/retrigger de fase, no un toggle "Retrig" separado tipo Serum |
| **Level** | full (100%) | suena a tope |
| **Destination (routing)** | **Filter 1** | ver punto 5 (serie) |

### La FM OSC2 → OSC1 (el "growl") — **[DIFERENCIA grande vs Serum]**

En Serum girabas el knob "Warp = FM (from B)" en OSC A. **En Vital NO existe un knob FM dedicado.** El FM cross-oscilador vive en el **Wave Morph (Waveshape)** del carrier:

1. Parado en **OSC 1** (el carrier), abrí el **dropdown del Wave Morph** (el selector de tipo de morph del oscilador, al lado del knob de morph).
2. Elegí la opción **`FM <- Osc 2`** (nombre verbatim del menú).
   - Esto hace que **OSC 2 module a OSC 1** a audio-rate (true cross-osc FM). Es exactamente el growl que buscás.
   - **[DIFERENCIA]** El ruteo es **invertido respecto a Serum**: parás en el **carrier** (OSC1) y elegís la fuente "<- Osc 2", no al revés.
3. **La CANTIDAD de FM = el knob del Wave Morph** que está pegado a ese dropdown (el mismo que normalmente hace warp del waveshape). 
   - **Subir ese morph = más índice de FM = más dirt/growl.**
   - Equivalente al "35–55%" de Serum: arrancá el knob de Wave Morph en **~40–55% del recorrido** y ajustá a oído. **(default sugerido: ~45%)**.
4. Ese knob de Wave Morph es **el destino del Macro 1** (ver punto 8) y es modulable como cualquier otro.

---

## 2) OSC 2 — modulador (ex OSC B)

| Control Vital | Valor | Notas |
|---|---|---|
| **On** | sí | tiene que estar encendido para poder modular |
| **Wavetable** | Triangle (carpeta Basic Shapes → Triangle) | forma de onda triangular |
| **Transpose** | **-36 semitonos (= tres octavas abajo)** | tres octavas abajo |
| **Unison Voices** | 1 | |
| **Level** | **0** | que NO se escuche su salida directa |

### Cómo silenciar OSC2 pero que SIGA modulando — **[DIFERENCIA vs Serum]**

En Serum poníais "Level 0 en el Mixer" y listo. En Vital el oscilador modulador **sigue siendo escuchable salvo que lo saques del path de salida**. Dos formas confirmadas:

- **Método simple (suele bastar):** bajá el **Level de OSC2 a 0**. En la mayoría de los casos esto lo saca del output pero mantiene su rol de modulador.
- **Método a prueba de balas (caso borde):** si igual se cuela algo de OSC2 en la salida, ruteá **OSC2 a Filter 2** (su Destination) y cerrá ese filtro / matalo en Mix, así su salida directa muere pero su señal de modulación sigue viva. *(Truco del foro oficial de Vital; usalo solo si bajar Level no alcanza.)*

---

## 3) Voicing — Mono / Poly 1 — **[DIFERENCIA vs Serum]**

Vital **no tiene un toggle "Mono" ni "Legato" explícito**. En el tab **Advanced**:

| Control Vital | Valor | Notas |
|---|---|---|
| **Voices** | **1** | esto da el comportamiento mono efectivo |
| **Note Priority** | Newest **(default sugerido)** | newest/oldest/highest/lowest/round robin |
| **Note Track** (por osc) | ON en OSC1; **OFF en OSC2 si querés ratio de FM fijo** | OSC2 con Note Track off = índice de FM constante por toda la tecla **(default sugerido: probá las dos)** |
| Glide / portamento | **~0** | sin glide |

> Honestidad: con Voices=1 hay un comportamiento conocido/discutido sobre el restart de osciladores en legato. El legato puro no es tan directo como en Serum; para darkpsy de notas largas sostenidas no te va a molestar.

---

## 4) Amp Envelope (ENV 1) — ADSR

Pegado a la receta de Serum (entra seco, sostiene a tope, corta seco):

| Etapa | Valor |
|---|---|
| **Attack** | 0 |
| **Decay** | full / largo |
| **Sustain** | **100%** |
| **Release** | 0 |

> ENV 1 está cableado por default al amp/volumen en Vital, no hace falta rutearlo a mano.

---

## 5) Filtros en SERIE — **[DIFERENCIA vs Serum: LP/BP/HP no son "tipos"]**

En Serum elegías "Bandpass 12dB" y "Lowpass 12dB" como tipos. **En Vital elegís un TIPO/MODELO de filtro (Analog/Dirty/Ladder/Digital/Diode/Formant/Comb/Phaser) y un SUB-MODO de pendiente/respuesta (12dB / 24dB / Notch Blend / Notch Spread / B/P/N), y el knob `Blend` (rango 0 a 2) morfea de forma continua entre las respuestas (p. ej. en 12dB: LP → BP → HP).**

### Filter 1 = "Bandpass 12dB"

| Control Vital | Valor | Notas |
|---|---|---|
| **Tipo/Modelo** | **Analog** | **(default sugerido)** — emula circuito clásico |
| **Sub-modo** | **12dB** | en 12dB el Blend morfea **LP → BP → HP** |
| **Blend** | **al MEDIO (≈1.0 de 0–2)** | el centro = **Bandpass**. Acá conseguís el bandpass real |
| **Cutoff** | **~800 Hz – 1.2 kHz** | **[NOTA]** el control de Cutoff de Vital está en **semitonos** (-52 a 76); no hay campo en Hz directo, pero al arrastrar te muestra la frecuencia equivalente. Apuntá a la zona de medios |
| **Resonance** | **~66% (dos tercios)** | |
| **Drive** | 0–small **(default sugerido: 0)** | 0–20 dB, suma saturación |
| **Mix** | 100% | full wet |

### Filter 2 = "Lowpass 12dB"

| Control Vital | Valor | Notas |
|---|---|---|
| **Tipo/Modelo** | **Analog** | **(default sugerido)** |
| **Sub-modo** | **12dB** | |
| **Blend** | **0 (mínimo) = Lowpass** | en 12dB, Blend a 0 = LP puro |
| **Cutoff** | **~50% del recorrido** | "cutoff ~50%" de la receta |
| **Resonance** | **~50%** | |
| **Mix** | 100% | |

### Cómo armar la SERIE (el punto clave) — **[DIFERENCIA vs Serum]**

Por default los dos filtros van en **paralelo**. Para ponerlos en serie:

1. En **OSC1 y OSC2**, poné su **Destination = Filter 1** (ambos osciladores entran a Filter 1). *(Si usaste el truco del filtro para silenciar OSC2, ese es un caso aparte — para el path de audio principal querés todo a Filter 1.)*
2. En **Filter 2**, abrí su sección **"Routing"** (los toggles de entrada del filtro) y **activá el toggle de entrada "Filter 1"** (y dejá OFF los toggles de Osc 1/2/3 en Filter 2).
3. Resultado: **OSC1(+2) → Filter 1 → Filter 2 → salida.** Cadena en serie, bandpass primero, lowpass después.

---

## 6) LFO 1 = STEPS escalonados — **[DIFERENCIA vs Serum: no hay "Sequencer mode"]**

En Serum tenías un toggle LFO/Sequencer. En Vital **todo es el mismo editor de LFO dibujable**; el escalón se logra así:

**Dibujar los steps (Método A — paintbrush "Step"):**
1. Abrí el editor de **LFO 1**.
2. En el **menú de patrones (paint mode)**, ícono de pincel, elegí el patrón **"Step"** ("Creates a stepped waveform").
3. Pintá sobre el grid → te genera los escalones. Variá las alturas para el patrón random/escalonado del darkpsy.

**Alternativa (Método B — manual):** poné **Open points** (movés en X e Y) a distintas alturas; los **Closed points** entre cada par de open points controlan el slope del segmento. Para saltos duros, dejá los segmentos casi verticales.

**Grilla y sync:**
| Control Vital | Valor |
|---|---|
| **Tempo (sync)** | **1/16** (dropdown va de 32/1 a 1/64) |
| **X grid** | **16** (16 pasos en el ciclo) |
| **Y grid** | a gusto, ej. 8, para cuantizar alturas **(default sugerido)** |

**Saltos DUROS (sin smoothing) — esto es lo crítico:**
- **Smooth = 0** (mínimo). El Smooth (0–16 s) suaviza la salida exponencialmente; en 0 los escalones quedan secos.
- En cada punto de slope (closed point): clic derecho → **"Reset Power"** para que el segmento no curve y mantenga el valor hasta el próximo paso (escalón perfecto).

### Ruteo LFO 1 → Filter 1 Cutoff ("la electricidad")

- Arrastrá la fuente **LFO 1** y solta sobre el knob **Cutoff de Filter 1** (aparece un anillo de modulación alrededor del knob).
- **Amount: +40 a +70%** (positivo, hacia arriba). Ajustá el anillo. **(default sugerido: +55%)**.
- Este barrido escalonado del bandpass = la "electricidad" del patch.

---

## 7) FX Rack — cadena reordenable — **[Vital permite varias instancias de Distortion]**

El rack de Vital es una cadena reordenable. Ordená así:

### FX 1 — Distortion (Hard Clip, drive al máximo)
| Control | Valor |
|---|---|
| **Modo** | **Hard Clip** (corta recto, agresivo; equivalente al Hard Clip/Overdrive de la receta) |
| **Drive** | **al MÁXIMO** |
| **Mix** | 100% |

### FX 2 — Delay (leve)
| Control | Valor |
|---|---|
| **Mix / Wet** | **~10–15%** |
| Sync | 1/8 o dotted **(default sugerido)** |
| Feedback | bajo **(default sugerido)** |

### FX 3 — EQ (campana en los medios)
- Banda **campana (bell)** en **~400–800 Hz**, ganancia **-3 a -6 dB** (limpia el barro de los medios). El EQ de Vital es gráfico, arrastrás el punto de la banda.

### FX 4 — Distortion #2 (overdrive suave para engordar)
| Control | Valor |
|---|---|
| **Modo** | **Soft Clip** (redondea picos, cálido — el "overdrive suave" para engordar) |
| **Drive** | **~20–30%** |
| **Mix** | 100% |

> **[DIFERENCIA / ventaja]** Vital deja tener **dos instancias de Distortion** en la misma cadena, así que esta receta de "distorsión dura adelante + soft engorde atrás" se arma tal cual. Si querés bitcrush adicional, el mismo módulo Distortion tiene modos **Bit Crush** y **Down Sample** (además de Linear Fold y Sine Fold para wavefolding).

---

## 8) Macro 1 = índice de FM (el growl en vivo) — **[DIFERENCIA en el destino]**

En Serum el Macro iba a "OSC A Warp". En Vital:

1. Arrastrá la fuente **Macro 1** y soltala sobre **el knob del Wave Morph de OSC1** (el mismo knob que controla la cantidad de `FM <- Osc 2`).
2. Seteá el **Amount** del anillo de modulación para que Macro 1 barra de poco growl a mucho growl (de ~0 a ~80% del morph) **(default sugerido)**.
3. Renombrá Macro 1 = **"GROWL"**. Mapealo a MIDI CC para la mano en vivo.

> Verificá la conexión en el tab **Matrix** (vas a ver la fila Source: Macro 1 → Destination: Osc 1 Wave Morph, con Amount editable y polaridad bipolar). **[NOTA]** Esta fila SÍ aparece en el tab Matrix porque es una conexión de la mod matrix (Macro → parámetro). El FM en sí (`FM <- Osc 2`) NO aparece como fila de Matrix: es un ajuste interno del oscilador, no una conexión de modulación.

---

## 9) OSC 3 / Sub — **[DIFERENCIA: Vital NO tiene sub osc dedicado]**

Vital tiene **3 osciladores wavetable + 1 Sampler**, sin sub osc jerárquico. Si querés reforzar el fundamental del growl:
- Encendé **OSC 3**, wavetable **Sine** o **Triangle**, **Transpose -12 o -24**, **Note Track ON**, level moderado, ruteado a **Filter 1** (o **Direct Out** si lo querés limpio sin barrido). **(opcional / default sugerido: dejarlo apagado para empezar.)**

---

## 10) Mod Matrix — verificación final

Abrí el tab **Matrix** y confirmá estas filas (todo seteable también acá, con Amount en % del rango del destino y polaridad bipolar):

| Source | Destination | Amount | Notas |
|---|---|---|---|
| **Macro 1** | Osc 1 Wave Morph | 0 → ~80% | la mano en vivo (esta fila SÍ vive en la Matrix) |
| **LFO 1** | Filter 1 Cutoff | +40 a +70% | la electricidad escalonada |
| **Env 1** | Amp (cableado) | — | ADSR del punto 4 (conexión por default) |

> **[NOTA]** El FM `FM <- Osc 2` **NO es una fila de la Mod Matrix**. Es un parámetro del oscilador (el Wave Morph de OSC1 puesto en modo `FM <- Osc 2`). No lo busques en el tab Matrix como Source "Osc 2": no aparece ahí. La cantidad de FM se ajusta directo con el knob de Wave Morph del osc (o modulándolo con Macro 1, que sí es fila de Matrix).

---

## Resumen de divergencias vs Serum (para no quemarte)

1. **FM** → no hay knob FM. Elegís **`FM <- Osc 2`** en el **Wave Morph dropdown de OSC1 (el carrier)** y la **cantidad = el knob de Wave Morph**. Ruteo invertido (parás en el carrier). El FM **no aparece como fila en la Mod Matrix**.
2. **Silenciar el modulador** → Level 0 en OSC2; si se cuela, ruteo a Filter 2 y matalo ahí.
3. **LP/BP/HP** → no son tipos. Elegís Tipo/Modelo (Analog) + sub-modo (12dB) + **Blend** (0=LP, medio=BP, máx=HP).
4. **Serie de filtros** → osc a Filter 1, y en Filter 2 activás el toggle de entrada **"Filter 1"** en su sección Routing.
5. **LFO steps** → no hay Sequencer mode; es el editor con paint **"Step"** + **X grid 16** + **Smooth 0** + Reset Power.
6. **Mono/Legato** → no hay toggle; **Voices = 1** en Advanced.
7. **Sub osc** → no existe; usás OSC3 con sine/triangle bajada de octava.
8. **Dos distorsiones** → permitido; cadena de FX reordenable.

---

Tocá en **C1–C2**, notas largas sostenidas, y modulá el **Macro 1 (GROWL)** con la mano. La combinación FM (morph de OSC1) + barrido escalonado del bandpass (LFO1 → Filter 1 Cutoff) + doble distorsión es el "bajo growl / electricidad" darkpsy.
