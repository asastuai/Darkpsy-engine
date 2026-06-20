# Recetas Serum 2 — darkpsy / hitech

> Documento de referencia para construir un set de techno oscuro / darkpsy con **Serum 2 + Reaper**.

---

## Intro — qué es esto y cómo usarlo

Esto es un recetario de patches verificados para Serum 2, traducidos a partir de recetas originales hechas en otros sintes (Z3ta+, Albino3, Phase Plant) y de walkthroughs conceptuales (IDM Mag). Cada hoja te dice, dial por dial, cómo armar un sonido del palo darkpsy / hitech en Serum 2: bajo growl, leads metálicos, leads squelchy alien y bichos forest.

**Cómo usarlo:**

- Cada hoja arranca con una nota de fidelidad: qué es **verbatim** de la fuente original, qué está **traducido** de otro sinte a Serum 2, y qué es **(default sugerido)** porque la fuente era vaga. Respetá lo verbatim, movés a gusto lo demás.
- Los números marcados **(default sugerido)** son puntos de partida sensatos, no dogma. Arrancá ahí y afiná de oído con los macros.
- Empezás por el **bajo growl** (es el ancla del groove), después vas a los leads.
- La sección final **"Kick + bass: la ley del género"** es la que más impacta en que el track suene a club y no a demo. Leéla aunque te saltees el resto.

**Nota sobre Serum 2:** Serum 2 mantiene el oscilador de wavetable (WT) y le suma **warp / FM real** por oscilador. Donde acá decimos `FM (from B)`, en Serum 2 eso es **FM verdadera de audio-rate** (en Serum 1 ese mismo nombre hacía en realidad Phase Distortion). El ruteo osc→filtro se hace en el **Mixer**, los dos filtros nativos se conmutan serie/paralelo con un **dial de routing**, y el FX rack es reordenable por drag-and-drop. Todo eso está aprovechado en las hojas.

---

# HOJA DE PATCH — Serum 2

## "Bajo growl / electricidad (darkpsy)"

> Traducción a Serum 2 de la receta de Cybernetika para **Z3ta+** (KVR t=204363).
> El concepto original: **FM** (Osc1 triangle grave modula a Osc2 saw) → **dos filtros en serie** (BP resonante + LP) → **distorsión brutal** → limpieza con EQ → overdrive final.
> **Nota de fidelidad:** Z3ta+ y Serum 2 no son idénticos. Donde la receta usa cosas de Z3ta+ que Serum hace distinto (modo "FM" del oscilador, "step envelope" del LFO, distorsión con destino "filtros 1-2", render "Draft") lo traduzco al equivalente Serum 2 y lo marco. Donde la fuente era vaga (ADSR exacto, rate del LFO, delay/EQ) pongo **(default sugerido)**.
> **Verificado contra Serum 2 (2025):** en Serum 2 el warp **`FM (from B)` es FM verdadera** (en Serum 1 ese modo era en realidad Phase Distortion). El ruteo osc→filtro se hace en el **Mixer**, y la conmutación serie/paralelo entre los dos filtros es por un **control de routing (dial)**, no por cableado fijo "A→B".

---

### 1. Osciladores

#### OSC A — Carrier / portador (lo que SUENA)
En Z3ta+ el "Osc2 carrier" es el que se oye. En Serum lo natural es que el **carrier sea Osc A** y el modulador sea Osc B (porque el warp mode "FM (from B)" hace que B module a A). Por eso **invierto el orden respecto a Z3ta+**: el saw va en A.

| Parámetro | Valor |
|---|---|
| Wavetable | **`Analog > Saw`** (o `Basic Shapes` con la posición en diente de sierra). El "Vintage Saw 1" de Z3ta+ = un saw con un pelín de carácter analógico; `Analog/Saw` o un saw "vintage" clona eso |
| Octava (Oct) | **‑1** (verbatim de la receta) |
| Semitonos / Fine | 0 |
| **Warp** | **`FM (from B)`** ← acá es donde A recibe la FM de B (ver sección 2). En Serum 2 este modo es **FM real**, no Phase Distortion |
| Warp amount | **35–55 %** para arrancar. Este knob = **índice/profundidad de FM = el "nivel de Osc1" de Z3ta+** (el control de carácter/suciedad). Mapealo a Macro 1 (ver sección 8) |
| Unison | **1 voice** (es un bajo mono, no querés ancho) |
| Detune | 0 |
| Level | **full** (~75–100 %) |
| Phase | **fija**, retrig ON (fase fija, no random) — para que el ataque del bajo sea consistente nota a nota |

#### OSC B — Modulator / modulador (NO se oye solo; modula a A)

| Parámetro | Valor |
|---|---|
| Wavetable | **`Basic Shapes`** con la posición en **Triangle** (o `Analog > Triangle`). Verbatim: triangle |
| Octava (Oct) | **‑3** (verbatim — la triangular grave a sub-frecuencia es la que da el growl eléctrico) |
| Semitonos / Fine | 0 |
| Warp | None |
| Unison | 1 |
| **Level (output) en el Mixer** | **Importante:** con warp `FM (from B)`, A toma la forma de onda de B como moduladora **independientemente del nivel de salida de B en el Mixer**, así que podés bajar el output de B a 0 si no querés que suene en paralelo. Dejá **B Level = 0 en el Mixer** (el modulador no debe sonar audible, igual que en la receta). B sigue modulando a A aunque su salida esté en 0 |
| Phase | fija, retrig ON |

> **Sub Osc:** la receta no pide sub. **(default sugerido)** Si querés más cuerpo abajo para club, activá **Sub = Sine, ‑1 oct, level bajo (~15–20 %)**. Opcional; el growl del FM ya ocupa graves.
> **Noise:** no va. Off.

#### Polifonía
- **Poly = 1** (verbatim "poly 1"). En Serum 2: panel **Global / Voicing → `Mono`** (o el contador de voces en 1).
- **Mono mode** con **Legato OFF** y **Glide/Portamento ~0** (subilo a gusto si querés slides entre notas, muy darkpsy).

---

### 2. FM / Warp — el corazón del patch

**Z3ta+ original:** el grupo del Osc1 se setea en modo "FM" y el Osc1 (triangle ‑3) modula la frecuencia del Osc2 (saw ‑1).

**Serum 2 — dos formas, elegí UNA:**

**Opción A (recomendada, fiel y simple):**
- En **OSC A**, Warp Mode = **`FM (from B)`**.
- El **Warp knob de A** = índice/profundidad de FM. **35–55 %** de base.
- B (triangle ‑3) ya está actuando como operador modulador. No hace falta mod matrix.
- En Serum 2 esto es **FM verdadera de audio-rate** (operador B → frecuencia de A), no el Phase Distortion que hacía Serum 1 con el mismo nombre.

**Opción B (modular el ÍNDICE de FM con curvas, si querés automatizarlo):**
- Source = **`LFO`** o **`Macro`**, Dest = **`A : Warp`**, Amount = a gusto.
- Esto NO crea FM por sí solo: la FM la sigue generando el warp `FM (from B)`; lo que hacés acá es **modular dinámicamente la profundidad** de esa FM (índice), para que el growl crezca/decrezca.
- **Aclaración:** no uses un LFO sobre `A : Coarse/Pitch` creyendo que eso es "FM real lineal" — modular el pitch con un LFO/env es vibrato/pitch-mod, no FM de audio-rate. La FM real ya la da el warp.

> **Carácter = profundidad de FM.** Subir el Warp de A = más índice = más sucio/ruidoso (exactamente el "subí el nivel del Osc1" de Z3ta+). Por eso va a **Macro 1** para tocarlo en vivo.

---

### 3. Filtros (dos, en serie)

Serum 2 tiene **dos filtros** (Filter 1 y Filter 2) y permite ponerlos en **serie o en paralelo** con un **control de routing (dial)** en la sección de filtros. La receta pide BP resonante → LP, así que: **ruteá ambos osciladores al filtro en el Mixer** y poné el routing en **serie** (la señal pasa por Filter 1 y de ahí a Filter 2).

> **Ruteo osc→filtro:** en Serum 2 esto se controla en el **Mixer** (cada fuente de sonido tiene su envío a Filter 1 / Filter 2). Mandá **OSC A al filtro a full**. (En Serum 1 era un "botoncito" en el osc; en Serum 2 es el Mixer.)

#### Filtro 1 — Bandpass resonante (el del formante nasal + destino del LFO)

| Parámetro | Valor |
|---|---|
| Tipo | **`BP12`** (Bandpass 12 dB/oct — verbatim "bandpass 12 dB/oct") |
| Cutoff | **~800 Hz–1.2 kHz** de base **(default sugerido)** — pero esto lo BARRE el LFO (sección 5). Ponelo en la zona media-grave donde el formante suena nasal/vocal |
| **Resonancia** | **~66 % (2/3 del recorrido)** — verbatim "resonancia a 2/3". Alta, para que cante el formante |
| Drive | bajo (la distorsión brutal viene del FX, no de acá). ~10–20 % |
| Mix | 100 % |

#### Filtro 2 — Lowpass

| Parámetro | Valor |
|---|---|
| Tipo | **`LP12`** (Lowpass 12 dB/oct — verbatim) |
| Cutoff | **~50 %** del recorrido (verbatim "cutoff ~1/2") |
| Resonancia | **~50 %** (verbatim "res ~1/2") |
| Drive | 0–15 % |
| Mix | 100 % |
| Ruteo | **Routing en SERIE** (Filter 1 → Filter 2, vía el dial de routing de la sección de filtros) |

> **"Subir el bus del Osc2" (Z3ta+):** en la receta se sube el nivel del carrier hacia el Filtro 1 para que la resonancia trabaje más fuerte. En Serum 2 eso = **subir el Level de OSC A** y/o **subir el envío de A al filtro en el Mixer**. Asegurate de que **A esté enviado al filtro** (en el Mixer) y a **full level**.

---

### 4. Envolventes

#### ENV 1 — Amp (verbatim: Attack min, Sustain max, Decay max, Release 0)

| Stage | Valor | Notas |
|---|---|---|
| **Attack** | **0 ms** (mínimo) | arranque instantáneo, seco — no es pluck |
| **Hold** | 0 | |
| **Decay** | **máximo** (full a la derecha) | irrelevante porque el sustain está a tope; lo dejás full igual que la receta |
| **Sustain** | **100 % (máximo)** | bajo sostenido y plano mientras se mantiene la nota |
| **Release** | **0 ms (nulo)** | corta SECO al soltar |

Resultado: bajo que entra instantáneo, se sostiene agresivo a tope, y muere en seco. **No es un pluck.**

#### ENV 2 — (opcional) **(default sugerido)**
No requerida por la receta. Si querés, una **Env de pitch corta** (Attack 0, Decay ~30 ms, ruteada en la mod matrix a `A : Coarse` con amount chico) da un "click/punch" extra al ataque del bajo. Opcional.

---

### 5. LFO — el "step envelope" = la electricidad

**Z3ta+ original:** un LFO ruteado al cutoff del Filtro 1, pero **NO con onda normal sino con un "step envelope" / sequencer steps** — eso da el barrido escalonado/secuenciado, la "sick modulation".

**Serum 2 — cómo se logra el equivalente exacto:**
- Serum **no usa el nombre "step envelope"**, pero el **editor de LFO sí hace steps**: con **Shift+click** dibujás escalones en la grilla (igual que un step-sequencer). Cada nodo se puede setear como **Flat** (plano), **Ramp Up** o **Ramp Down** con **click derecho**. Patrón irregular = más "eléctrico". Funcionalmente idéntico al de Z3ta+.

| Parámetro | Valor |
|---|---|
| LFO usado | **LFO 1** |
| Forma | **Curva de STEPS** — activá el **grid** (poné 8 ó 16 divisiones horizontales) y con **Shift+click** dibujá los escalones a alturas distintas. Click derecho sobre cada step → **Flat** (para saltos duros). Mantené **Alt/Option + Shift** para snapear al grid |
| Rate | **Sync ON**, **1/8 ó 1/16** para que los saltos vayan a tempo **(default sugerido — la fuente no da rate)**. Probá también 1/8T (tresillo) para groove darkpsy |
| Trigger | **Trig / Retrig** (que reinicie con cada nota) o **Env** si querés que arranque siempre desde el primer step |
| Smoothing / Rise | **0** (que los saltos sean DUROS, escalonados — nada de interpolación, esa dureza es la electricidad). En Serum 2 esto es el control de **Smoothing** del LFO; ponelo al mínimo |

> La fuente **no especifica rate ni forma exacta de los pasos** — programá los steps a gusto para que el cutoff salte y arme el patrón de "electricidad".

---

### 6. Mod Matrix

| # | Source | Destination | Amount | Notas |
|---|---|---|---|---|
| 1 | **LFO 1** | **Filter 1 : Cutoff** | **+40 a +70 %** | El barrido escalonado del BP = la electricidad. Este es EL ruteo clave |
| 2 | (implícito) **B modula a A vía warp `FM (from B)`** | — | — | Ya resuelto por el warp; no necesita slot. Solo usá un slot si querés modular el ÍNDICE de FM (`A : Warp`, ver Opción B sección 2) |
| 3 *(opcional)* | **Macro 1** | **Filter 1 : Cutoff** | + | offset manual del barrido para tocar en vivo |
| 4 *(opcional)* | **Velocity** | **Filter 2 : Cutoff** | +20 % | dinámica: tocar fuerte abre más. Default sugerido |

---

### 7. FX Rack (en ESTE orden)

Serum 2 tiene rack de FX reordenable. La receta de Z3ta+ inserta la distorsión "sobre los filtros 1-2"; en Serum el FX rack va **después** de los filtros, así que el equivalente es **Distortion como primer FX del rack** (justo después de la sección de filtros). Mismo resultado audible.

| Orden | FX | Settings |
|---|---|---|
| **1** | **Distortion** | Para "distorsión brutal" usá un modo **duro**: **`Hard Clip`** o el **`Overdrive`** del módulo (Serum 2 agregó/actualizó el modo Overdrive y permite **stackear** el circuito de overdrive para sonidos muy agresivos). **NO** uses `Soft Clip` para esto: Soft Clip es el modo *más suave*. El "Smart Shaper" de Z3ta+ no existe por nombre → el equivalente Serum es un **waveshaper/clip duro** con **Drive al MÁXIMO** (verbatim "máximo amount"). Mix 100 % |
| **2** | **Delay** | **Muy leve** (verbatim "slight bit"). **(default sugerido):** Mix/Feedback ~10–15 %, time 1/8 sync, solo para cola/aire. NO querés delay protagonista en un bajo |
| **3** | **EQ** | **Cortá un poco los medios molestos** (verbatim "cut a bit of the nasty mids"). **(default sugerido):** banda campana en **~400–800 Hz, ‑3 a ‑6 dB, Q medio (~1.0)**. Limpia el barro que deja la distorsión |
| **4** | **Distortion #2 (overdrive)** | El **"CamelPhat overdrive"** de Z3ta+ es un plugin externo → en Serum el equivalente es **un segundo módulo Distortion en modo `Overdrive`**, **drive bajo-medio (~20–30 %)**, solo para calentar y engordar el final. Mix ~50 % |

> **Sobre el render "Draft" de Z3ta+:** Z3ta+ baja la calidad a "Draft" a propósito para más aliasing/suciedad. **Serum 2 no tiene un "Draft mode" idéntico**, pero el equivalente es:
> - En el **menú Global**, bajar la **Quality / oversampling** (es un ajuste **GLOBAL del plugin**, no por-oscilador; por defecto está en **High = 2x**). Bajarlo reintroduce más aliasing crudo, deseable en darkpsy. Ojo que afecta a TODO el patch.
> - Y/o subir el Warp de FM (la FM cruda ya alias-ea naturalmente).

---

### 8. Macros (Macro 1-4)

| Macro | Destino | Por qué |
|---|---|---|
| **Macro 1 — "GROWL / dirt"** | **OSC A : Warp (FM amount)** | El control estrella: es el "nivel de Osc1" de Z3ta+. Subirlo en vivo = más sucio/ruidoso. **Mapealo y tocalo en vivo.** |
| **Macro 2 — "Electricity"** | **LFO 1 : Rate** (o depth del ruteo LFO 1→Cutoff en la mod matrix) | acelera/intensifica el barrido escalonado |
| **Macro 3 — "Tone / BP"** | **Filter 1 : Cutoff** | mueve el formante nasal del bandpass a mano |
| **Macro 4 — "Squelch"** | **Filter 2 : Cutoff + Reso** (dos slots de mod matrix desde el mismo Macro) | abre/cierra el lowpass para dinámica del bajo |

---

### 9. Cómo tocarlo

- **Registro:** zona de **bajo, C1–C2** (con A en ‑1 oct y B en ‑3, ya estás bien grave). Es un bajo, no un lead.
- **Articulación:** **monofónico (poly 1)**, notas **sostenidas** — gracias a Attack 0 + Sustain 100 + Release 0, cada nota entra seca, se sostiene agresiva, y corta en seco al soltar.
- **El movimiento de "electricidad"** viene de **sostener notas largas** mientras el **step-LFO barre el cutoff del bandpass (Filter 1)** — dejá que la nota dure para que el sequencer de steps se exprese.
- **Tip de groove darkpsy:** sincronizá el LFO en **1/16** y tocá en **offbeat/rolling 16ths**; o usá **1/8T** para el feel tresillado típico. Activá **glide corto** para slides sucios entre notas.
- **En vivo:** **Macro 1 (GROWL)** es tu mano derecha — subilo en los drops para que el growl se vuelva ruido eléctrico, bajalo para que respire.

---

#### Resumen de fidelidad
- **Verbatim respetado:** triangle ‑3 / saw ‑1, FM (modulador→carrier), BP12 + LP12 en serie, reso 2/3 en el BP, cutoff/res 1/2 en el LP, poly 1, ADSR (A min / S max / D max / R 0), LFO en steps al cutoff del BP, distorsión al máximo, EQ cortando medios, delay leve, overdrive final.
- **Traducido de Z3ta+ → Serum 2 (marcado en el cuerpo):** modo "FM" del osc → Warp `FM (from B)` (FM real en v2); "step envelope" del LFO → steps dibujados con Shift+click en el LFO editor (shape Flat); "Smart Shaper" → waveshaper/clip duro (Hard Clip / Overdrive) al máximo; "CamelPhat" → segundo Distortion en Overdrive; render "Draft" → bajar Quality/oversampling GLOBAL; "subir bus Osc2" → Level de OSC A a full + envío al filtro en el Mixer; ruteo osc→filtro y serie/paralelo → Mixer + dial de routing de la sección de filtros.
- **Defaults sugeridos (la fuente era vaga):** Hz de cutoff exactos, rate/forma de los steps, ms del delay, dB/Hz del EQ, drive del overdrive, sub opcional.

---
---

# Hoja de patch — "Lead hitech FM metálico" (Serum 2)

> Traducción dial por dial de la receta de PurpleSunray (preset Albino3, hilo KVR). Sigo el **preset real** (el que NO usa FM entre osciladores, sino ARP 1/64 + mod-env al pitch), porque es el que da el carácter. Al final dejo una variante con FM real de Serum por si querés el otro camino.
>
> **Aviso de honestidad:** Albino3 no es Serum. Dos cosas de la receta original son trucos de Albino3 que en Serum 2 se logran distinto:
> 1. La "spectral wave" → en Serum 2 usás un oscilador en modo **Spectral** (tipo de oscilador nativo desde Serum 2). Ojo: el modo Spectral hace resíntesis armónica/espectral de un audio o de contenido espectral; **no carga "wavetables"** como el modo Wavetable. No esperes un menú de tablas tipo "Basic Shapes" ahí.
> 2. El "ARP 1/64 con mod-env por re-trigger que baja el pitch" → Albino3 lo hacía con su arpegiador. El equivalente fiel y más controlable en Serum 2 es un **LFO retriggereado (modo Env / one-shot) ruteado al pitch, en sync a 1/64**. Eso reproduce el "decay baja el pitch en cada re-trigger". Lo explico abajo.
>
> Donde la fuente no dio número (ADSR, rates, cutoffs Hz), pongo **(default sugerido)** y queda claro que es mío, no de PurpleSunray.

---

### 1) Osciladores

#### OSC A — el "brillo" (spectral)
- **Modo:** Spectral (botón de tipo de oscilador → **Spectral**).
- **Contenido:** una fuente con armónicos altos densos. En modo Spectral **cargás/usás contenido espectral** (un sample brillante o el contenido espectral de fábrica) y manipulás los armónicos; no hay tabla "Spectral Saw" para elegir. Arrancá con un sample de armónicos brillantes o el preset espectral más filoso que tengas. *(default sugerido)*
- **Octave/Semi:** 0 / 0 (la octava real la dan tus dedos: tocás en octava 3-4 sobre el bajo, ver §8).
- **Detune de la receta (−2/−3/−4 oct):** ese detune era para el OSC1 del **método genérico** (los dos saws). En el **preset real** no va detune de octava acá. Si querés cuerpo grave de respaldo, usá el Sub (§1 Sub), no bajes este OSC.
- **Unison:** 1 voz (limpio) o **3 voces, detune ~8-12%** si lo querés más gordo *(default sugerido)*. PurpleSunray no pide unison, así que por defecto **Unison 1**.
- **Phase / Rand:** Rand ON (default de Serum) para que cada nota no arranque idéntica.
- **Warp:** **None** (la "FM" la hacemos por pitch-mod, no por warp — ver §2).
- **Level:** 100%.

#### OSC B — refuerzo de cuerpo medio (opcional)
- PurpleSunray solo menciona OSC1 spectral para el brillo. OSC B es opcional para llenar.
- **Modo:** Wavetable, **"Basic Shapes"** en posición **Saw** (pos ~0%). *(default sugerido)*
- **Octave:** −1 respecto a OSC A, para anclar el cuerpo.
- **Level:** 40-60% o **Off** si querés el sonido más fino/filoso. Empezá en Off y subilo a gusto.

#### Sub
- **Forma:** Saw o Square.
- **Octave:** −1 / −2 (queda casi todo recortado por el highpass de §3, pero ayuda a la mod de pitch a tener fundamental que masticar).
- **Level:** bajo, 15-25%. En hitech el grave lo come el highpass igual.

#### Noise
- **Off.** La receta no lo pide y ensucia la metálica del filtro. (Si querés un "fizz" arriba, un noise tipo white a 5-10% con highpass propio, pero **default Off**.)

---

### 2) "FM" metálica — el corazón del patch (ARP 1/64 + mod-env al pitch)

La receta NO es FM entre osciladores. Es **re-disparo de pitch rapidísimo**: cada 1/64 algo baja el pitch con un decay corto. En Serum 2 esto se arma así.

#### Vía recomendada en Serum 2: LFO retriggereado al pitch
- **LFO1 → destino: Master Tune** (en el mod matrix; "Master Tune" es el nombre real del destino de pitch global de Serum, calibrado en **semitonos / st**). También sirve "OSC A Coarse" si lo querés solo en ese oscilador.
- **Modo LFO1:** **Env** (one-shot). Los modos de LFO en Serum son **Off / Trig / Env**: en Env la curva se reproduce una vez por disparo de nota (con opción de loop point si lo querés cíclico). NO uses loop acá.
- **Forma:** un solo punto alto a la izquierda cayendo a cero a la derecha = **rampa descendente** (sube el pitch al disparo y cae). Esto = "decay baja el pitch".
- **Rate / sync:** **1/64** (BPM sync ON). Eso da el "re-trigger cada 1/64" de la fuente.
- **Trigger:** con el LFO en modo **Env**, cada nota dispara la curva de nuevo; ese es el re-trigger por nota que querés.
- **Cantidad (en mod matrix, LFO1 → Master Tune):** Serum 2 muestra la profundidad de pitch directo en **semitonos (st)**. Doble-click en el slider del matrix y escribí el valor (ej. `12st`, `24st`). Empezá en **+12 st** y subí hasta que suene metálico-mecánico. *(default sugerido — la fuente no dio el rango)*

> Por qué LFO-en-Env-mode y no el arp interno: el arpegiador de Serum 2 cambia notas, pero no te da una **envelope de decay por step a 1/64 ruteada al pitch** tan limpia como un LFO synced en Env mode. Resultado audible idéntico al truco de Albino3.

> **Alternativa con el ARP/sequencer de Serum 2:** activá el modo Arp del LFO o el sequencer, división **1/64**, y ruteá **Env2 → Master Tune** con Env2 en decay corto (Env de Serum ya retriggea por nota). Más fiel al texto, menos cómodo de afinar. Las dos llegan al mismo lugar.

#### Capa de variación: LFO2 y LFO3 free-run al pitch
La fuente: "LFO1+3 are free-run and mod the pitch as well to bring more variation into the FM".
- **LFO2 → Master Tune**, modo **Off** (free-run: corre con el transport del DAW, sin retrigger por nota), forma random/sine, rate lento. Cantidad **±0.1 a ±0.5 st** (microvariación). *(default sugerido)*
- **LFO3 → Master Tune**, modo **Off** también, otra forma (otro random o triangle), rate distinto al de LFO2, cantidad **±0.2 a ±0.6 st**. *(default sugerido)*

> "Free-run" en Serum = modo **Off** del LFO (no Trig, no Env): la fase no reinicia con cada nota. Si además querés que deambule sin engancharse al tempo, desactivá el BPM sync y usá rate en Hz lento. Nota: hay 4+ LFOs disponibles (Serum 2 amplió el set), así que LFO2/3/4 conviven sin problema.

---

### 3) Filtros

PurpleSunray usa **dos** filtros en cadena: primero lowpass con resonancia + overdrive, después highpass con saturación al máximo. **Serum 2 tiene DOS slots de filtro nativos e independientes, con ruteo serie/paralelo integrado** — así que NO hace falta meter el HP en el FX rack. Poné LP en el Filtro 1 y HP en el Filtro 2, ruteo en **serie**, orden **LP → HP**.

#### Filtro 1 — Lowpass (el del filo metálico)
- **Tipo:** **MG Low 12** (ladder estilo Moog 12 dB/oct, suena gordo con resonancia) o **Low 12/24** estándar. *(MG Low 12 sugerido por el carácter)*
- **Cutoff:** parcial-abierto, buscá el sweet spot como dice la fuente. Default **~1.5-3 kHz**. *(default sugerido — "play with cutoff to find a sweet spot")*
- **Resonance:** media-alta, **~25-40%**. *(default sugerido — la receta pide "some resonance")*
- **Drive (overdrive DENTRO del filtro):** ESTO es clave. Subí el **Drive del filtro** a **40-70%**. La receta dice explícitamente que la metálica viene del **overdrive digital dentro del LP**, no de un FX externo. En Serum 2 ese es el knob **Drive** del módulo de filtro. *(rango sugerido; la fuente dice "con overdrive" sin número)*
- **Mix:** 100% (todo pasa por el filtro).

#### Filtro 2 — Highpass (saturación al máximo)
- **Tipo:** **High 12** o **High 24**.
- **Cutoff:** subilo hasta sacar todo el grave que no querés ("get rid of the low-frequency stuff"). Default **~200-500 Hz**, barrelo con oído. *(default sugerido)*
- **Resonance:** baja, 0-15%.
- **Saturación / Drive:** **AL MÁXIMO (100%).** La fuente lo remarca como *"very important!"*. En Serum 2 el equivalente es el **Drive del filtro HP al tope**. Si querés MÁS suciedad de la que da ese Drive, sumá un **Distortion** justo después en el FX rack (ver §6).

> **Cómo encadenar los dos filtros en Serum 2:** usá los **dos slots de filtro nativos** (Filtro 1 = LP, Filtro 2 = HP) y poné el **ruteo en serie** (Serum 2 tiene toggle serie/paralelo entre los dos filtros). La señal pasa LP → HP. No necesitás el FX rack para esto. Mantené el **orden LP → HP** como la receta.

---

### 4) Mod sources adicionales: LFO4 → cutoff del HP
La fuente: "LFO4 modulates the HP filter cutoff".
- **LFO4 → Cutoff del Filtro 2 (HP)** (en mod matrix, dest = el cutoff del HP del slot de filtro 2).
- **Forma:** sine o triangle.
- **Rate:** lento, **1/2 o 1/1 en sync**, o ~0.2-1 Hz en modo Off. *(default sugerido)*
- **Cantidad:** moderada, que el HP respire abriendo/cerrando el grave sin perder el cuerpo. **±15-30%.** *(default sugerido)*

---

### 5) Envolventes

#### Env1 — Amp (siempre Env1 = volumen en Serum)
Hitech lead = ataque rápido, sostenido mientras mantenés la tecla.
- **Attack:** 0-3 ms (instantáneo). *(default sugerido)*
- **Decay:** 80-150 ms. *(default sugerido)*
- **Sustain:** 80-100%. *(default sugerido)*
- **Release:** 20-60 ms (corto, para que stacatee con el groove). *(default sugerido)*

> La fuente NO dio ADSR. Todo lo de arriba es default sensato para un lead percusivo-sostenido.

#### Env2 — (solo si usás la alternativa de ARP del §2)
- Decay corto **20-50 ms**, sustain 0, ruteada a Master Tune. *(default sugerido)*

---

### 6) FX rack (en orden de señal)

1. **Distortion** — para empujar más el filo metálico si el Drive de los filtros no alcanza.
   - **Tipo:** Tube o Diode/Hard Clip (el clip duro suma armónicos altos, coherente con "digital overdrive"). *(Tube/Hard Clip sugerido)*
   - **Drive:** 25-50%. *(default sugerido — secundario al drive del filtro, que es el primario según la receta)*
   - **Posición:** después de los dos filtros (LP → HP → Distortion).
2. **EQ** — quitá un poco de 200-400 Hz si embarra, realzá suave en 3-6 kHz para la presencia metálica. *(default sugerido)*
3. **Delay** — opcional para el contexto de track, no para el patch base. Si va: sync 1/8 o 3/16, feedback 25-35%, mix 15-20%, con HP en el delay para que las repeticiones no embarren. *(default sugerido, opcional)*
4. **Reverb** — muy poco o nada en hitech. Si va, plate corto, mix <10%. *(opcional)*

> El HP NO va acá: usá el segundo slot de filtro nativo (§3). El compresor/limiter final dejalo para el mix bus, no en el patch.

---

### 7) Macros (mapeo sugerido)

- **Macro 1 — "FM amount":** → cantidad de LFO1 → Master Tune (el §2). Es el dial que más cambia el carácter metálico. **El más importante.**
- **Macro 2 — "Bite":** → Drive del Filtro 1 (LP) (+ opcional Drive del Distortion en paralelo). Sube la agresión metálica.
- **Macro 3 — "Cutoff LP":** → Cutoff del Filtro 1. Para barridos en vivo / automatización.
- **Macro 4 — "HP sweep":** → Cutoff del Filtro 2 (HP) (suma a lo que hace LFO4). Para ir abriendo/cerrando el grave a mano.

---

### 8) Cómo tocarlo

- **Registro:** en la **3ra o 4ta octava por encima de la nota del bajo** (textual de la fuente). Si el kick/bass está en C1-C2, tocá el lead alrededor de **C4-C5**.
- **Escala:** PurpleSunray lo dice claro — *"musical scales are kind of guidelines, no strict rules"*. En hitech/darkpsy los intervalos disonantes y cromáticos son bienvenidos; no te encierres en la escala.
- **Articulación:** notas cortas y repetidas, stacatto, dejando que el re-trigger de 1/64 haga el "gargareo" metálico. Probá rolls de 1/16 y 1/32 con la mano y dejá que el LFO de pitch a 1/64 module por debajo.
- **Groove tip:** si automatizás Macro 1 ("FM amount") por arriba durante un fill, el lead pasa de tonal a ruido metálico — clásico de hitech para transiciones. Y bajá Macro 4 (HP) en los drops para dejar entrar más cuerpo, subilo en los climax para que quede solo el filo.

---

### 9) Resumen de la cadena (orden de señal, igual que la fuente)

`OSC A Spectral (brillo)` → `pitch re-disparado: LFO1 modo Env 1/64 → Master Tune (+12..24 st, decay baja el pitch)` + `LFO2/3 modo Off (free-run) → Master Tune (microvariación)` → `Filtro 1 LP (MG Low 12, resonancia ~30%, DRIVE interno 40-70% = filo metálico)` → `Filtro 2 HP (High 24, DRIVE/SATURACIÓN al MÁXIMO, cutoff barrido por LFO4, ruteo serie)` → `Distortion (refuerzo) → EQ → (Delay/Reverb opcionales)` → tocado en **octava 3-4 sobre el bajo**.

---

### Apéndice — Variante con FM REAL de Serum (el "método genérico" del primer post)
Si en vez del preset Albino3 querés el **método de los dos saws con FM** que PurpleSunray describió primero:
- **OSC A:** Wavetable "Basic Shapes" → Saw. **Detune −2/−3/−4 octavas** (Octave knob a −2/−3/−4), este es el **modulador**.
- **OSC B:** Wavetable Saw, octava 0, es el **portador**.
- **FM:** en OSC B, elegí el **warp mode de FM verdadera** y subí el knob de warp (FM depth). En Serum la convención de nombre es "FM (from A)" cuando el modulador es el OSC A — el warp toma el otro oscilador como fuente de modulación. **Importante:** en Serum 1 el viejo "FM from B" era en realidad Phase Distortion (PD); **Serum 2 agregó FM modular verdadera** como warp, que es la que querés acá para el carácter más áspero/metálico. (Equivalente directo a "module frequency of OSC2 with OSC1".)
  - La **profundidad de FM se controla con el knob de warp del oscilador**, no es un destino "FM A→B" del mod matrix. Lo que SÍ podés hacer en el matrix es rutear un LFO/Env **al knob de warp (FM depth)** para modular la cantidad de FM. Además, si querés usar el Sub o el Noise como modulador alternativo, en Serum 2 podés tomarlos como fuente.
- Filtros y FX igual que arriba (LP con drive interno → HP con saturación al máximo, en los dos slots nativos).
- Esta vía NO usa el truco de pitch a 1/64; el carácter sale de la FM saw→saw + el clipping del filtro.

---

#### Qué quedó como (default sugerido) y no de la fuente
PurpleSunray **nunca** dio: valores de ADSR, rates exactos de LFOs, frecuencias de cutoff en Hz, ni cantidades de drive. Sí especificó: spectral en OSC1, "FM" vía ARP 1/64 + mod-env de decay al pitch, LFO1+3 free-run al pitch, LFO4 → cutoff HP, **saturación HP al máximo**, detunes −2/−3/−4 oct (solo en el método de dos saws), y octava 3-4 sobre el bajo. Esos son firmes; el resto son mis defaults para que arranques sin adivinar y afines de oído.

---
---

# Lead alien squelchy (hitech) — "Dash Glitch" en Serum 2

> **De dónde viene esto y qué cambia.** La receta original está hecha en **Phase Plant** (motor modular). Serum 2 NO es modular, así que algunas cosas se logran distinto:
> - La **phase modulation (PM)** de Phase Plant se hace en Serum 2 con el **warp mode `FM (from B)` del oscilador** (en Serum, ese modo "from B" históricamente produce el carácter de modulación de fase / distorsión de fase) o, si querés FM modular verdadera, con el nuevo motor FM de Serum 2. No es idéntico bit a bit, pero el resultado tímbrico (saw limpio → metálico digital) es equivalente.
> - El **"LFO con rate controlado por un random generator"** de Phase Plant se arma en Serum 2 con **un LFO en modo Random/S&H** + **un segundo LFO Random arrastrado sobre el knob Rate del primero**. En Serum sí se puede modular el Rate de un LFO arrastrando la cruz (crosshair) de otra fuente sobre el knob Rate, así que se reproduce bien.
> - El **Frequency Shifter** existe nativo en el FX rack de Serum 2 (es el módulo **Frequency Shifter**, basado en el clásico Bode/Echobode). Lo usamos ahí.
>
> **Honestidad sobre números:** la fuente escrita NO publica ni una sola cifra (ni octavas, ni detune, ni cutoff, ni ADSR, ni rate, ni Hz de shift). Todo lo numérico de abajo marcado **(default sugerido)** es un valor sensato de Serum 2 que reproduce el carácter descripto, NO un dato de la fuente. Arrancá de ahí y movelo con los macros, que es justamente el espíritu del patch.

---

### 1. Osciladores

#### OSC A — el cuerpo (saw)
- **Wavetable:** `Basic Shapes` posición **Saw**, o directamente la tabla `Saw` (single-cycle). La fuente pide "simple saw wave".
- **Warp Mode:** `FM (from B)` — **clave del patch.** Esto hace que OSC B module a OSC A (la "phase modulation" de Phase Plant; en Serum el modo "from B" da ese carácter inarmónico/metálico).
  - **Warp amount: 0% en reposo**, ruteado a **Macro 1** (ver Mod Matrix). Con el macro a fondo, **~45-65%** te da el timbre metálico/digital agresivo *(default sugerido)*.
- **Octava:** 0 *(default sugerido — la fuente no especifica)*. Para lead hitech chillón podés probar +1 oct.
- **Unison:** **1 voz** (sin unison). Esto es un lead glitchero monofónico, no un supersaw; el movimiento lo da el LFO+random, no el detune *(default sugerido)*.
- **Detune:** 0.
- **Fase / Rand:** **Phase fija** (no Rand) para que la modulación sea consistente y el pitch-LFO mande el carácter. Poné `Phase` ~0, `Rand` 0 *(default sugerido)*.
- **Level:** 100%.

#### OSC B — el modulador (sine)
- **Wavetable:** `Basic Shapes` posición **Sine**. La fuente dice que el segundo osc es sine y "no suena por sí mismo": es modulador puro.
- **Output / Level del B a la salida:** **0% (mute audible)**. En Serum 2, cuando A usa `FM (from B)`, B aporta su forma de onda como modulador a partir del routing "from B", independientemente de su nivel de salida audible. Bajalo a silencio para que sea solo modulación y no una capa que suene.
- **Octava / Pitch ratio:** **+1 o +2 octavas** respecto de A para timbre más brillante/metálico, o mismo pitch para algo más hueco *(default sugerido: +1 oct)*. La fuente no da ratio.
- **Unison:** 1, **Detune:** 0.

#### Sub / Noise
- **Sub:** **OFF.** La fuente no lo menciona y el sonido es agudo/chillón, no necesita peso de sub.
- **Noise:** **OFF** *(default — la fuente no incluye noise)*. Si querés ensuciar el ataque, un toque de noise a 5-10% es opcional, pero no es de la fuente.

---

### 2. FM / Warp (el ruteo exacto de la "phase modulation")

La fuente dice explícitamente: **es PM (phase modulation), NO FM clásica**, con el sine modulando la fase del saw. En Serum la forma idiomática de lograr ese carácter es el warp `FM (from B)` (que en el motor de Serum produce justamente esa coloración tipo modulación de fase, inarmónica/metálica).

**En Serum 2, ruteo exacto:**
1. En **OSC A** seleccioná **Warp Mode = `FM (from B)`**.
2. El **Warp knob de OSC A** = cantidad de modulación. Ese knob es lo que mapeás a **Macro 1**.
3. OSC B en sine, **silenciado a la salida**, actúa solo como fuente de modulación vía el routing "from B".

> Variantes según el carácter que busques:
> - **`FM (from B)`** (recomendado): el match más directo del "sine modula al saw" de la receta; carácter metálico/inarmónico.
> - **Modo `PD` (Phase Distortion)** de Serum 2: si querés el sabor más clásico de distorsión de fase / PM, probalo; es la opción más cercana conceptualmente a la "phase modulation" pura.
> - **FM modular verdadera** de Serum 2 (motor FM nuevo): más limpio/cristalino que el viejo "from B"; probalo si querés más definición en los armónicos.
> En single-cycle sine, FM (from B), PD y FM modular suenan emparentados; cualquiera de los tres reproduce el saw→metálico de la receta. **No existe un warp llamado literalmente "PM (from B)" en Serum** — el nombre real del modo "from B" es `FM (from B)`.

- **Cantidad de modulación en reposo:** 0%.
- **Cantidad de modulación a fondo (Macro 1 = 100%):** **~55%** *(default sugerido)*.

---

### 3. Filtro

> La fuente **no menciona filtro** (tipo, modo, cutoff ni reso — lo delega al video). Default sensato para un lead hitech que tiene que cortar en la mezcla:

- **Tipo:** `MG Low 24` (ladder Moog-style lowpass 24 dB / 4 polos) — carácter cremoso y resonante típico de leads *(default sugerido)*.
- **Cutoff:** **~70-80%** (abierto, casi full; es un lead brillante). En Hz, arrancá ~**3-4 kHz** y subí *(default sugerido)*.
- **Resonancia:** **~20-30%** — algo de reso para enfatizar el squelch sin chillar de más *(default sugerido)*.
- **Drive (dentro del filtro):** **~15-20%** para saturar un poco y engordar *(default sugerido)*.
- **Routing:** OSC A → filtro (OSC B no va al filtro porque está muteado/modulando).

---

### 4. Envolventes (ADSR)

> La fuente **no da ningún valor de ADSR** (lo delega al video). Defaults para un lead glitchero que se toca en pasadas largas:

#### ENV 1 (Amp) — *(todos default sugerido)*
- **Attack:** 1-5 ms (ataque rápido, percusivo/inmediato).
- **Decay:** ~200 ms.
- **Sustain:** **~80-90%** (necesitás que sostenga notas largas porque el método es "grabar pasadas largas").
- **Release:** ~100-150 ms (corto, para que los glitches no se emborronen).

#### ENV 2 (opcional → filtro)
- Si querés acento al ataque: Attack 0 ms, Decay 150 ms, Sustain 50%, ruteá ENV 2 → Filter Cutoff con depth +15% *(default sugerido, opcional, no está en la fuente)*.

---

### 5. LFOs (acá vive el "squelch")

La fuente: **un LFO al pitch del osc principal, y un random generator controlando la VELOCIDAD (rate) de ese LFO.** Más un Frequency Shifter con **modulación random**.

#### LFO 1 — "pitch squelch" (el LFO chillón)
- **Forma:** triangular/sine suave para barrido de pitch tipo squeak, o algo más quebrado si querés glitch *(default sugerido: triangle)*. La fuente no da forma.
- **Rate base:** sync a **1/8** como punto de partida, PERO **clave: este rate va a ser modulado** (ver abajo), así que su valor "fijo" es solo el centro *(default sugerido)*.
- **Modo:** podés ponerlo en **Trigger/Env** o **Free**; Free ayuda a que no quede cuantizado.
- **Destino:** **Osc A Pitch** (arrastrá la cruz del LFO 1 al pitch de OSC A, o usá la matrix), depth **±2 a ±7 semitonos** según cuánto chillido quieras *(default sugerido)*.

#### LFO 2 — el "random generator" que controla la velocidad del LFO 1
- **Forma:** `Random` (Sample & Hold) — Serum 2 trae presets/modos de LFO Random/Stepped. Esto es el "random generator" de la receta.
- **Rate:** sync **1/4** o **1/2** (lento, para que el "cambio de velocidad" del LFO 1 sea esporádico y orgánico) *(default sugerido)*.
- **Destino:** **LFO 1 — knob Rate.** En Serum se modula el Rate arrastrando la cruz (crosshair) del LFO 2 directamente sobre el knob **Rate del LFO 1**, y ajustás el amount. **Este es el ruteo que hace que el pitch suba y baje a un ritmo aleatorio** — el corazón del squelch impredecible.

> Esto reproduce con fidelidad el "random generator controlando la speed del LFO" de Phase Plant: en Serum el knob Rate de un LFO sí acepta modulación arrastrada desde otra fuente (otro LFO, macro, etc.).

#### LFO 3 — random para el Frequency Shifter
- **Forma:** `Random` (S&H), **Rate:** sync 1/2 o más lento *(default sugerido)*.
- **Destino:** cantidad de shift del Frequency Shifter (arrastrá la cruz del LFO 3 al control de Shift del FX, o usá la matrix; ver FX). Esto es la "random modulation" sobre el frequency shifter que la fuente pide.

---

### 6. Mod Matrix (conexiones exactas)

> En Serum muchas de estas conexiones se crean arrastrando la cruz (crosshair) de la fuente directamente sobre el knob destino; después afinás amount/curve en la pestaña Matrix. La tabla las resume:

| # | Source | Destination | Amount | Para qué |
|---|--------|-------------|--------|----------|
| 1 | **Macro 1** | OSC A — Warp (FM amount) | **0 → +55%** *(default)* | Profundidad de modulación (saw → metálico) |
| 2 | **Macro 2** | FX: Frequency Shifter — Shift amount | **0 → +100%** *(default)* | Dosifica lo "alien" en vivo |
| 3 | **LFO 1** | OSC A — Pitch (Coarse/Fine) | **±4 semitonos** *(default)* | El barrido de pitch chillón |
| 4 | **LFO 2 (Random)** | **LFO 1 — Rate (knob)** | **+60%** *(default)* | Random controla la velocidad del LFO de pitch → squelch impredecible |
| 5 | **LFO 3 (Random)** | FX: Frequency Shifter — Shift | **±40%** *(default)* | Random sobre el frequency shifter (lo psicodélico) |

> Conexiones 3 + 4 juntas = el "squelch alien" exacto de la receta. Conexión 5 = lo psicodélico inarmónico.

---

### 7. FX Rack (en orden)

La fuente: después del Frequency Shifter, "una variedad de efectos en distintos canales — de delays a reverbs". Serum 2 tiene routing de FX con buses duales y módulos splitter, pero NO replica canales paralelos arbitrarios como un DAW, así que el split en "channels" se hace mejor **fuera de Serum, en el DAW** (ver nota de workflow). Dentro del rack de Serum:

1. **Frequency Shifter** *(nativo en el FX rack de Serum 2, basado en Bode/Echobode)*
   - **Shift base:** **~+150 a +300 Hz** *(default sugerido — la fuente no da Hz)*. Cualquier valor que rompa la relación armónica sirve; el carácter inarmónico/campanoso aparece apenas te corrés de 0.
   - **Mix:** ~50-70% para que se note pero no tape el saw.
   - Modulado por **LFO 3 (random)** y mapeado a **Macro 2**.

2. **Distortion** *(opcional, default sugerido — no en la fuente):* el módulo Distortion de Serum 2 tiene varios modos de saturación (tube/diode/etc.); drive ~20%, para morder el hitech. Ponelo si te queda fino.

3. **EQ** *(default sugerido):* high-pass suave ~80-100 Hz para sacar barro (es un lead agudo), y un realce en 2-4 kHz para presencia.

4. **Delay:** la fuente pide delay pero **no da tiempos.** *(Defaults sugeridos):* sync **1/8 dotted** (ping-pong), **Feedback ~30-40%**, **Mix ~25%**. Para hitech, delays cortos y rítmicos.

5. **Reverb:** *(defaults sugeridos):* algoritmo **Hall/Plate** (o alguno de los nuevos de Serum 2 como Vintage/Basin), **Decay ~2-3 s**, **Mix ~15-20%**, con **low-cut en el reverb ~300 Hz** para que la cola no embarre.

> **Orden:** Freq Shifter → (Dist) → EQ → Delay → Reverb. Distorsión antes de los tiempo-based para que delay/reverb no amplifiquen el fizz.

---

### 8. Macros (asignaciones)

| Macro | Destino | Rango | Rol |
|-------|---------|-------|-----|
| **Macro 1** | OSC A Warp (FM amount) | 0 → 55% *(default)* | **Profundidad de modulación** — saw limpio ↔ metálico digital. (de la fuente) |
| **Macro 2** | Frequency Shifter — Shift amount | 0 → 100% *(default)* | **Cantidad de Frequency Shifter** — dosifica lo alien en vivo. (de la fuente) |
| **Macro 3** | Filtro Cutoff *(default sugerido, no en la fuente)* | 30% → 90% | Abrir/cerrar el lead en performance |
| **Macro 4** | LFO 1 Pitch depth (±) *(default sugerido)* | 0 → ±7 st | Intensidad del squelch en vivo |

> Los **únicos dos macros que la fuente nombra explícitamente** son Macro 1 (depth de modulación) y Macro 2 (Freq Shifter). Macro 3 y 4 son extras útiles para el método de "volverse loco moviendo controles".

---

### 9. Cómo tocarlo (workflow de la fuente)

- **Registro:** lead agudo. Tocá en octava media-alta; las notas sostenidas largas dejan que el LFO+random hagan los squeaks. **Monofónico**, articulado a mano.
- **Articulación:** no "programes" una nota perfecta. **Grabá pasadas LARGAS** sosteniendo notas mientras suena el track, y **movés a mano**: Macro 1 (modulación), Macro 2 (Freq Shifter), y el depth del pitch-LFO (Macro 4). El random generator hace que cada pasada sea única e irrepetible.
- **"Go wild":** probá todas las variaciones, sin miedo a las partes feas. El método es **cosechar, no diseñar**: grabás material crudo de sobra.
- **Edición (scissor tool):** después, en el DAW, cortás con la herramienta de tijera y **descartás lo malo, te quedás con los mejores glitches/squelches** (cherry-picking).
- **Procesamiento final / "different channels":** sobre los recortes ya elegidos, **repartís los FX en canales separados del DAW** (un bus de delay, otro de reverb), no todo dentro de Serum. Eso es lo que la fuente llama "effects on different channels".
- **Tip de groove:** como el squelch es no cuantizado, dejá que choque contra un kick/percusión rígidos — el contraste entre la grilla dura y el pitch random orgánico es lo que da el sello hitech.

---

#### Resumen de qué es de la fuente vs. qué es default

- **De la fuente (firme):** 2 osc en modulación de fase (saw + sine modulador), LFO al pitch con rate controlado por random, Frequency Shifter con modulación random, Macro1=modulación / Macro2=FreqShifter, FX delays+reverbs en canales separados, workflow grabar-largo + tijera.
- **Default sugerido (yo, para Serum 2):** todos los números — octavas, detune, cutoff/reso, ADSR, rates de LFO, semitonos de pitch depth, Hz de shift, settings de delay/reverb/EQ/distorsión, y Macros 3-4. La fuente los omite a propósito y los manda al video.

---
---

# HOJA DE PATCH — Serum 2

## "Lead/bicho forest randomizado (en Serum)" (forest psytrance)

> **Aviso de honestidad sobre la fuente:** la receta original (IDM Mag) es un walkthrough conceptual, **no publica un solo número**: nada de ADSR, cutoff, resonancia, rate de LFO ni amounts. Lo único concreto es la técnica "Dash Glitch" (Método 1) y una variante por filtro resonante (Método 2). Todo lo que abajo lleva **(default sugerido)** es elección mía para que esto suene en Serum 2 sin que adivines; el esqueleto (sine + modulación tipo Chaos/S&H → pitch + Noise como refuerzo/FM → delay + reverb) sí es textual de la fuente. Donde la fuente hablaba de cosas que en Serum 2 cambiaron de nombre o lugar, lo aclaro.
>
> **Nota de versión (corregida):** el artículo describe el Serum **original**. En Serum 2 NO hace falta "emular" nada: el motor trae **LFOs con modo Chaos real (atractores Lorenz/Rössler)** y un modo **Sample & Hold** nativo (escalones random). Cualquiera de los dos sirve de "corazón" del Dash Glitch. Usaremos un **LFO en modo Sample & Hold** (o Chaos) ruteado al pitch. Esto reemplaza al "Chaos oscillator + S&H" del Serum viejo de forma directa, sin trucos.
>
> **Aviso clave sobre la FM con ruido:** en Serum 2 el warp **FM** de un oscilador modula desde **OTRO oscilador** (aparece como **`FM (from B)`** / `FM (from C)`, según cuál uses como moduladora), no desde el Noise. **No existe un modo de warp "FM From Noise" con el ruido como fuente seleccionable.** Para conseguir el grano "insecto" con ruido hay dos caminos reales que detallo en la sección FM/Warp.

---

### 1. Osciladores

> Serum 2 tiene **3 osciladores principales** (A, B, C) además de Sub y Noise. Usamos A como tono y, si querés FM real, B como moduladora.

#### OSC A — fuente del tono (sine puro)
- **Wavetable:** `Basic Shapes` → mover la **posición de wavetable (WT Pos)** hasta la **onda sine** (en `Basic Shapes` la sine está en un extremo del barrido; si no la encontrás limpia, cargá una tabla `Sine` directa). Sin armónicos, como pide la fuente.
- **Octava:** 0 (registro medio). Para "bicho" agudo subí a **+1** (default sugerido).
- **Semitonos / Fine:** 0 / 0.
- **Unison:** **1 voz** (default sugerido — la fuente no menciona unison; el glitch viene del pitch saltarín, no del coro). Si querés más cuerpo: 3 voces, detune ~8%.
- **Fase / Rand:** Phase 0°, **Rand 0** (default sugerido — fase fija para que cada nota empiece igual y los saltos se escuchen "secos").
- **Level:** 100%.

#### OSC B — moduladora de FM (opcional, ver sección 2)
- **Off por default.** Solo se enciende si elegís hacer **FM real** sobre OSC A (Método B de la sección 2). En ese caso: tabla `Sine` o algo brillante, **Level 0%** (no suena directo, solo modula), ajustando ratio con Semitonos.

#### OSC C — apagado
- Off (no lo necesita esta receta).

#### Sub
- **Off** (default sugerido). Es un lead/bicho, no necesita sub. Si lo querés con peso en graves, Sub `Sine` a **-1 oct**, level ~15%.

#### Noise — segunda fuente / textura
- **Activado.**
- **Sample:** `White` o cualquier ruido neutro (default sugerido).
- **Pitch del Noise:** el oscilador Noise de Serum **sí tiene control de Pitch** → **bajalo a aprox −24 a −36 semitonos** (default sugerido) tal como pide la fuente, para que aporte movimiento grave y granuloso, no siseo agudo.
- **Level:** ~25–40% (default sugerido — "refuerzo", no protagonista).

---

### 2. FM / Warp (el grano "insecto")

> Recordá: en Serum 2 **no hay un warp "FM From Noise"**. Tenés DOS caminos reales para meter el carácter FM/metálico. Elegí UNO (o combiná).

#### Camino A — Noise como moduladora vía Mod Matrix (lo más cercano a la fuente)
En Serum 2 el **Noise puede usarse como FUENTE de modulación en la Mod Matrix a audio-rate**. Eso te da el "FM con ruido" que buscaba la fuente:
- En la Mod Matrix, **Source = Noise**, **Destination = OSC A → Pitch** (o → Warp/WT Pos), **Amount alto**.
- A audio-rate, modular el pitch de A con ruido produce ese grano metálico/inarmónico tipo insecto. Subí amount de a poco: poco = aspereza sutil, mucho = chillido de bicho.
- Es el reemplazo honesto del "FM Noise Osc" del Serum viejo: la moduladora ruidosa entra **por la matriz**, no por un warp dedicado.

#### Camino B — FM real con OSC B (warp `FM (from B)`)
Si querés FM tonal/metálica más estable:
- En **OSC A** abrí el **menú Warp** y elegí **`FM (from B)`**. Esto modula la frecuencia de A con la salida de OSC B (NO con el ruido). Asegurate de tener **OSC B encendido** (Level 0% para que solo module).
- **Cantidad de Warp/FM:** empezá en **~25–35%** (default sugerido) y subí hasta que aparezca el grano metálico sin tapar el tono.
- Nota: en Serum 2 esto es **FM verdadera** (frequency modulation modular), distinta del "FM from B" del Serum 1 que era en realidad Phase Distortion.

> **Recomendación para "forest bicho":** usá **Camino A** (Noise → Pitch en matriz) porque es el que da el carácter ruidoso-inarmónico de la fuente. El Camino B es para un grano más afinado/campana.

---

### 3. Filtro

> La fuente da DOS caminos. Te dejo el filtro armado para el **Método 2 (resonante que "canta")**, que es el que pide drive/reso explícitos, y lo dejo enrutado para que sirva también al Método 1.

- **Tipo:** **`MG Low 12`** (Moog-ladder lowpass, 12 dB/oct — el "analog" más cercano de Serum 2; el número es la pendiente en dB/oct). Si querés que auto-oscile más fácil, subí a **`MG Low 24`** (24 dB/oct).
- **Cutoff:** **~600 Hz – 1.2 kHz** de arranque (aprox **30–40%**) (default sugerido) — bajo, para que el barrido por modulación tenga recorrido hacia arriba.
- **Resonance:** **90–100%** (al tope, como pide la fuente, para que el filtro casi auto-oscile y "cante").
- **Drive (input al filtro):** **bajo**, tal como dice la fuente ("bajar el input") → **~10–20%** (default sugerido). Drive bajo deja respirar la resonancia.
- **Routing:** OSC A y Noise → **Filter ON** (chequeá que el botón de filtro esté activado en cada fuente).

---

### 4. Envolventes

> Serum 2 tiene **4 envolventes** (Env 1–4). La fuente NO da ADSR. Defaults sugeridos para lead/bicho percusivo-melódico:

#### ENV 1 — Amp (obligatoria, va a Volume / ENV-AMP por default)
- **Attack:** 1–5 ms (ataque rápido, "pluck").
- **Decay:** ~200 ms.
- **Sustain:** ~70% (default sugerido — si lo querés más staccato/glitch, bajá a 40%).
- **Release:** ~150 ms.

#### ENV 2 — extra (default sugerido) → al Cutoff
- **Attack:** 0 ms · **Decay:** ~120 ms · **Sustain:** 0% · **Release:** ~100 ms.
- Genera un "pluck" de filtro en cada nota que ayuda al carácter percutido del bicho.

---

### 5. LFOs

> Serum 2 trae hasta **10 LFOs** con modos **Sample & Hold**, **Chaos (Lorenz/Rössler)** y **Path (2D)**, además del dibujo libre.

#### LFO 1 — el "Chaos" escalonado (corazón del Dash Glitch)
Reemplazo directo y nativo del Chaos + S&H del original (no hay que falsearlo).
- **Forma:** poné el LFO en **modo `Sample & Hold`** (escalones random) o en un **modo Chaos** (Lorenz/Rössler) si querés caos más orgánico. Ambos son nativos de Serum 2.
  - Alternativa dibujada a mano: varios puntos a distinta altura con **Smooth/Curve en 0** (transición instantánea = escalón). Sirve igual.
- **Rate:** **sync `1/8` o `1/16`** (default sugerido) para saltos rítmicos. Para caos más libre, **modo Hz a ~4–8 Hz**.
- **Trigger / Mode:** **`Trigger`** (reinicia con cada nota) para que los saltos caigan alineados, o **`Free`/`Envelope`** si querés que el random siga corriendo entre notas. Default sugerido: **Trigger**.

#### LFO 2 — movimiento del cutoff (Método 2)
- **Forma:** Triangle o Sine (dibujo suave, Smooth alto).
- **Rate:** sync `1/4` o `1/2` (default sugerido), o libre lento ~0.5–2 Hz.
- Destino: cutoff (ver mod matrix).

---

### 6. Mod Matrix

| # | Source | Destination | Amount | Nota |
|---|--------|-------------|--------|------|
| 1 | **ENV 1** | **OSC A Level / Amp** | 100% | amp básica (en Serum suele estar implícita por la asignación ENV-AMP; agregala explícita si la moviste) |
| 2 | **LFO 1 (S&H / Chaos)** | **OSC A → Pitch** | **±3 a ±7 semitonos** (probá empezar en ±5) | **EL saltarín del Dash Glitch.** Más amount = saltos de afinación más salvajes |
| 3 | **LFO 1** | **OSC A → WT Pos** (o → Warp) | ~15% (default sugerido) | opcional: mueve también el timbre en cada salto |
| 4 | **ENV 2** | **Filter → Cutoff** | +40% (default sugerido) | pluck de filtro por nota |
| 5 | **LFO 2** | **Filter → Cutoff** | +25 a +40% | barrido del filtro resonante (Método 2) |
| 6 | **Noise** | **OSC A → Pitch** (audio-rate) | a gusto | **el "FM con ruido"** (Camino A de la sección 2). Si usaste el Camino B con `FM (from B)`, esta fila no hace falta |

> **Tip clave:** el "bicho randomizado" vive en la **fila 2**. Si suena demasiado caótico, bajá amount o pasá LFO 1 a `1/16` sync para que los saltos caigan en grilla. Si suena poco, subí a ±7/±12.

---

### 7. FX Rack (en orden — la fuente solo nombra Delay → Reverb, "liberalmente")

> Todos estos efectos existen en el FX rack de Serum 2 y son reordenables por drag-and-drop.

1. **Distortion** *(default sugerido, NO está en la fuente — pero el grano forest casi siempre lleva)*
   - Modo: `Tube` o un soft-clip suave (la Distortion de Serum 2 trae ~14 modos), drive **~20%**. Suave, para pegamento. Si te alcanza con el drive del filtro, omitilo.
2. **EQ** *(default sugerido)*
   - High-pass suave ~80–120 Hz para sacar barro; pequeño realce ~3–5 kHz para presencia del bicho.
3. **Delay** *(de la fuente)*
   - Modo: **Ping-Pong**, sync **`1/4` dotted (punteado)** (default sugerido — el delay clásico psy).
   - Feedback: ~35–45% · Mix: ~25–35% · usá el **HP/LP propio del Delay de Serum** para que los repes no tapen.
4. **Reverb** *(de la fuente)*
   - Modo: un reverb grande tipo `Hall`/`Plate` (Serum 2 suma Nitrous/Basin/Vintage y un Convolve si querés algo más específico), **Size grande**, Decay ~3–5 s, Mix ~20–30%, **pre-delay ~20–40 ms** para que el ataque siga claro.

> Orden recomendado: Dist → EQ → **Delay → Reverb** (la fuente exige delay antes que reverb; lo respeto).

---

### 8. Macros (mapeo sugerido — la fuente no los define)

- **Macro 1 — "Locura / Glitch amount":** controla el **Amount de la fila 2 (LFO 1 → Pitch)**. Es el dial estrella: de 0 (nota limpia) a full bicho.
- **Macro 2 — "Cutoff / Brillo":** al **Filter Cutoff** (rango ~30→80%).
- **Macro 3 — "FM / Grano":** al **Amount de la fila 6 (Noise → Pitch)** si usaste el Camino A, o al **Warp amount de `FM (from B)`** si usaste el Camino B.
- **Macro 4 — "Espacio":** sube simultáneamente **Delay Mix + Reverb Mix** (dry→wet).

---

### 9. Cómo tocarlo

- **Registro:** notas medias-agudas (C3–C5). El bicho luce mejor entre **C4 y C5**; abajo se vuelve drone.
- **Articulación:** **notas cortas y staccato**, dejando que el LFO 1 escupa los saltos de pitch dentro de cada nota. No necesitás glides: el movimiento ya lo pone la modulación (la fuente lo dice: "el pitch ya salta solo").
- **Groove:** disparalo en **16avos sincopados** sobre el offbeat del kick (típico forest ~145–155 BPM). Probá automatizar **Macro 1** subiendo en los breaks para que el bicho "se vuelva loco" y bajándolo en las partes melódicas.
- **Tip de mezcla:** sidechain suave al kick + el HP del EQ mantienen al bicho fuera del low-end.
- **Una sola voz / mono:** poné el sintetizador en **Mono + Legato** (default sugerido) para que se sienta como una criatura única correteando, no un acorde.

---

#### Resumen del esqueleto textual de la fuente (lo verificable)
- OSC sine puro ✔ · modulación escalonada (Chaos+S&H → en Serum 2 = **LFO en modo Sample & Hold o Chaos nativo**) al **pitch** ✔ · Noise con **pitch bajado** + **"FM con ruido" vía Noise como fuente en la Mod Matrix** (no vía un warp inexistente) ✔ · variante con **filtro Moog-ladder, input bajo, reso al máximo, mod al cutoff** ✔ · FX **Delay → Reverb** generosos ✔.
- Todo lo numérico (ADSR, Hz, %, rate, amounts, Dist, EQ, macros, articulación) es **default sugerido mío** — la fuente no trae un solo número.

---
---

# Kick + bass: la ley del género

> Esta sección NO es una hoja de patch: son los **principios verificados del recon** sobre cómo conviven kick y bass en darkpsy / techno oscuro, traducidos a **cómo se hacen con Serum 2 + Reaper**. Si el growl de la primera hoja no pega en el club, el problema casi siempre está acá, no en el patch.

La idea madre: en este género el **kick y el bass son un solo cuerpo rítmico**, no dos elementos que conviven. Para que suenen como uno, hay cuatro leyes.

---

### Ley 1 — Phase retrigger del oscilador del bass: OBLIGATORIO

**Principio:** el oscilador del bajo tiene que arrancar **siempre en la misma fase** en cada nota. Si la fase es random, cada nota del bajo pega distinto contra el kick (a veces suma, a veces cancela) y el low-end "respira" de forma inconsistente — el enemigo número uno de un groove apretado.

**En Serum 2:**
- En **OSC A** (y en el Sub si lo usás), poné la **fase fija** y **Retrig ON** (no Random). En la hoja del growl ya está marcado así: *Phase fija, retrig ON*.
- Verificá que **Rand = 0** en el oscilador. Si ves el indicador de fase saltar a un lugar distinto cada vez que disparás una nota, todavía está en random.
- Esto hace que el transiente de ataque del bajo sea **idéntico nota a nota**, que es la precondición para poder alinearlo con el kick (Ley 2).

---

### Ley 2 — Alineación de fase MANUAL entre kick y bass (en Reaper)

**Principio:** aunque el bass arranque siempre en la misma fase, esa fase tiene que estar **alineada con la del kick** para que las fundamentales sumen en vez de cancelarse. Esto NO se resuelve solo: se hace a mano, mirando la forma de onda.

**En Reaper:**
1. Poné el **kick y el bass en pistas separadas**, alineados al mismo punto de inicio (mismo tiempo de grilla).
2. Renderizá/congelá un golpe de cada uno y **mirá las formas de onda con zoom**. Fijate hacia dónde empuja el primer ciclo de cada uno (arriba o abajo).
3. Si los primeros ciclos van **en contra** (uno sube mientras el otro baja en la fundamental), tenés cancelación. Corregí con una de estas:
   - **Nudge de la pista de bass** unos pocos samples (con el item seleccionado, movelo en sample-mode con zoom máximo) hasta que las fundamentales empujen en la misma dirección.
   - O **invertí la polaridad** de la pista de bass (botón de phase/polarity invert del track, o un JS `Invert Phase` en la cadena) y comparás cuál de las dos versiones tiene más cuerpo en graves.
4. **Criterio de "está bien":** cuando el sub-bajo de la suma kick+bass **sube de nivel** (no baja) respecto a cada uno por separado, y el low-end se siente sólido en mono. Chequealo en **mono** (Reaper: monitor en mono o un JS `Mono`), porque la cancelación de fase se escucha más brutal en mono.

> Tip Reaper: usá un analizador de fase/correlación (el **ReaEQ** no lo da, pero el medidor de correlación de un plugin de metering, o simplemente el oído en mono) para confirmar que no estás en correlación negativa en los graves.

---

### Ley 3 — EQ notcheando los armónicos del bajo donde vive el kick

**Principio:** el kick y el bajo pelean por el mismo espacio de frecuencias graves. La solución NO es solo sidechain: es **hacerle lugar al kick** notcheando (cortando con un EQ angosto) las frecuencias del **bajo** justo donde el kick tiene su energía. Así el kick "perfora" sin que el bajo lo tape.

**En Reaper (con ReaEQ o el growl ya saliendo de Serum):**
1. Identificá **dónde vive el cuerpo del kick** (típicamente la fundamental del kick, ~50–60 Hz, y su punch en ~80–120 Hz). Solo-eá el kick y barré con un EQ en boost angosto hasta encontrar el pico.
2. En la **pista del bass**, poné un **ReaEQ con una banda en notch** (campana angosta, Q alto ~3–6) **en esa misma frecuencia** y **cortá ‑3 a ‑8 dB**. Eso le abre el hueco al kick en el armónico exacto donde colisionan.
3. Repetí si hay un segundo punto de choque (a veces el kick tiene cuerpo en dos zonas). Notcheá el bass en cada una.
4. Esto se combina con el sidechain, no lo reemplaza: el notch resuelve el choque **espectral fijo**, el sidechain resuelve el choque **temporal** (duck del bass en el ataque del kick).

> Importante: el notch va en el **BASS**, no en el kick. El kick manda en los graves; el bass se aparta.

---

### Ley 4 — Sub sine una octava abajo

**Principio:** el growl con FM tiene mucha energía en medios-graves pero el **sub real** (la fundamental que sentís en el pecho/sistema) conviene generarlo con una **sine limpia una octava por debajo** del bajo. Una sine no tiene armónicos que ensucien ni peleen con el kick: es puro fundamento.

**En Serum 2 (o como capa aparte en Reaper):**
- **Opción A (dentro de Serum):** activá el **Sub osc = Sine**, **‑1 octava** respecto del growl, **level bajo (~15–20 %)**, fase fija + retrig ON (igual que la Ley 1). Eso te da la fundamental limpia debajo del growl sin tocar el carácter del FM.
- **Opción B (capa separada en Reaper):** duplicá la pista de bass, dejá una con el growl (con un HP que le saque el sub) y otra **solo con una sine sub** una octava abajo (puede ser otra instancia de Serum con un patch de pura sine, o un sub-bass dedicado). Esto te da **control independiente** del nivel del sub y de su fase contra el kick (volvés a aplicar la Ley 2 sobre la capa sub).
- **Por qué sine y no saw/triangle abajo:** abajo de ~60–80 Hz cualquier armónico de más solo agrega barro y choca con el kick. La sine es la única que da peso sin ensuciar.
- **Mono el sub:** mantené el sub **100 % mono** (en Reaper, un JS `Mono` o un utility solo en la banda baja). El estéreo en el sub causa cancelaciones de fase en sistemas grandes.

---

### Resumen operativo (el orden en que lo hacés)

1. **En Serum:** fase fija + retrig ON en todos los osciladores del bass (Ley 1). Sub sine ‑1 oct a nivel bajo (Ley 4).
2. **En Reaper:** kick y bass en pistas separadas, alineás fase a mano mirando la forma de onda hasta que el sub sume (Ley 2).
3. **EQ:** notch en el bass en la(s) frecuencia(s) del kick, ‑3 a ‑8 dB, Q alto (Ley 3).
4. **Sidechain** suave del bass al kick para el choque temporal (complementa la Ley 3).
5. **Chequeo final en mono:** si el low-end se mantiene sólido en mono, está alineado. Si se adelgaza, volvé a la Ley 2.

---
---

# Quick start: armá el growl en 10 pasos

Receta exprés para tener el **bajo growl / electricidad** sonando desde cero en Serum 2. Cada paso remite a la hoja completa de arriba si querés el detalle.

1. **Init patch.** Poné Serum 2 en **Mono / Poly 1** (Global → Voicing → Mono), Legato OFF, Glide ~0.

2. **OSC A = carrier.** Cargá **`Analog > Saw`** (o `Basic Shapes` en saw). Octava **‑1**. Unison 1, Detune 0. **Phase fija + Retrig ON, Rand 0.** Level full.

3. **OSC B = modulador.** Cargá **`Basic Shapes` en Triangle** (o `Analog > Triangle`). Octava **‑3**. En el **Mixer bajá el Level de B a 0** (solo modula, no suena). Phase fija + retrig ON.

4. **FM real.** En **OSC A**, Warp Mode = **`FM (from B)`**. Subí el **Warp knob a ~35–55 %**. Ya tenés el growl base.

5. **Dos filtros en serie.** En el **Mixer**, mandá OSC A a los filtros a full. Routing de filtros en **SERIE**.
   - **Filter 1 = `BP12`**, cutoff ~800 Hz–1.2 kHz, **Reso ~66 % (2/3)**.
   - **Filter 2 = `LP12`**, cutoff ~50 %, reso ~50 %.

6. **Amp envelope.** ENV 1: **Attack 0, Decay full, Sustain 100 %, Release 0.** (Entra seco, sostiene a tope, corta seco.)

7. **El step-LFO (la electricidad).** En **LFO 1**, activá el grid (8 ó 16 divisiones) y con **Shift+click** dibujá escalones a distintas alturas. Click derecho en cada step → **Flat**. **Smoothing al mínimo.** Sync ON, **1/16** (o 1/8T para tresillo).

8. **Ruteo clave.** Mod Matrix: **LFO 1 → Filter 1 : Cutoff, +40 a +70 %.** Ese barrido escalonado del bandpass ES la electricidad.

9. **FX en orden:** **Distortion (`Hard Clip` u `Overdrive`, Drive al MÁXIMO)** → **Delay leve (~10–15 %)** → **EQ (campana ‑3 a ‑6 dB en ~400–800 Hz)** → **Distortion #2 (`Overdrive`, drive ~20–30 %)**.

10. **Macros y tocá.** **Macro 1 → OSC A : Warp (GROWL/dirt)** — tu mano derecha en vivo. Tocá en **C1–C2**, notas sostenidas largas para que el step-LFO se exprese. Subí Macro 1 en los drops para que el growl se vuelva ruido eléctrico.

> Después de esto, pasá a **"Kick + bass: la ley del género"** para que el growl pegue contra el kick en vez de pelearse con él. Ese paso es lo que separa un patch lindo de un low-end de club.

---

*Recetas verificadas para Serum 2 + Reaper · darkpsy / hitech*
