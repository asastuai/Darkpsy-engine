# Setup Dark Psytrance — Guía paso a paso

## Paso 1: Instalar Reaper

1. Ir a https://www.reaper.fm/download.php
2. Descargar **Windows 64-bit** 
3. Instalar con opciones por defecto
4. Al abrir te pide licencia → click "Still Evaluating" (funciona igual)

## Paso 2: Instalar Synths gratuitos

### Vital (leads, pads, bass)
1. Ir a https://vital.audio
2. Crear cuenta → descargar la versión **Free**
3. Instalar con opciones por defecto (instala VST3 automáticamente)

### Surge XT (acid, texturas psy)
1. Ir a https://surge-synthesizer.github.io
2. Descargar **Surge XT** Windows installer
3. Instalar con opciones por defecto

## Paso 3: Configurar Reaper

1. Abrir Reaper
2. Ir a **Options → Preferences → VST** (en el panel izquierdo bajo "Plug-ins")
3. En "VST plug-in paths" verificar que estén:
   - `C:\Program Files\Common Files\VST3`
   - `C:\Program Files\VSTPlugins` (si existe)
4. Click **Re-scan** → OK
5. Ir a **File → Project Settings** (o Alt+Enter):
   - BPM: **150**
   - Time signature: **4/4**

## Paso 4: Importar los MIDIs

1. En Reaper, click derecho en el área vacía de tracks → **Insert new track**
2. Crear **8 tracks** y nombrarlos:
   - Track 1: Kick
   - Track 2: Rolling Bass
   - Track 3: Acid Line
   - Track 4: HiHats
   - Track 5: Perc
   - Track 6: Lead Light
   - Track 7: Atmosphere
   - Track 8: FX Risers
3. Abrir la carpeta `C:\Users\Juan\.openclaw\darkpsy-project\` en el Explorer
4. Arrastrar cada archivo .mid al track correspondiente:
   - `01_Kick.mid` → Track 1
   - `02_Rolling_Bass.mid` → Track 2
   - etc.

## Paso 5: Asignar instrumentos a cada track

### Para tracks de DRUMS (Kick, HiHats, Perc):
- Click en el botón **FX** del track
- Buscar **ReaSynth** o mejor: descargar samples gratis de kicks psy
- Opción pro: descargar **Sitala** (drum sampler gratis) desde https://decomposer.de/sitala

### Para Rolling Bass (Track 2):
1. Click en **FX** del track
2. Add → **Vital** (o Surge XT)
3. En Vital: Init patch → Oscillator 1 → forma **Saw**
4. Bajar el pitch 1 octava
5. Agregar distortion en FX → Drive alto
6. Filter: Low-pass, cutoff medio, resonance media

### Para Acid Line (Track 3):
1. FX → Add → **Surge XT**
2. Buscar preset: Categories → Leads → algo con "acid" o "303"
3. O en Vital: Saw wave + filter LP con mucha resonance + envelope rápido

### Para Lead Light (Track 6):
1. FX → Add → **Vital**
2. Buscar preset: Presets → Leads → algo brillante/trance
3. O custom: Osc1 Saw + Osc2 Square, detuned, con reverb largo

### Para Atmosphere (Track 7):
1. FX → Add → **Vital**
2. Buscar preset: Presets → Pads → algo atmosférico
3. Agregar mucho reverb (FX → ReaVerbate en Reaper)

### Para FX Risers (Track 8):
1. FX → Add → **Vital** o **Surge XT**
2. Usar noise oscillator con filter sweep automático
3. O buscar samples gratis de risers/impacts

## Paso 6: Mezcla básica

1. **Kick**: más fuerte, centrado. -3 a 0 dB
2. **Bass**: justo debajo del kick. -6 dB. Centrado.
3. **Acid**: -9 dB. Leve pan izquierda.
4. **HiHats**: -12 dB. Leve pan derecha.
5. **Perc**: -10 dB. Distribuir en stereo.
6. **Lead**: -6 dB. Centrado con reverb.
7. **Atmosphere**: -12 dB. Full stereo (wide).
8. **FX**: -6 dB en los risers, 0 dB en los impacts.

## Tips Dark Psy

- El **bass** es el rey. Tiene que ser agresivo, distorsionado, con movimiento en el filter.
- Los **hats** son offbeat — clásico del psy. No los muevas a on-beat.
- El **lead** es tu "matiz de luz" — que suene etéreo, con delay y reverb.
- Los **pads** dan la atmósfera — no necesitan estar fuerte, solo llenar espacio.
- **Sidechain** el bass al kick para que no choquen (en Reaper: ReaComp con sidechain input).
