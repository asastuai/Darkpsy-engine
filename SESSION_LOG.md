# DarkPsy Engine — Session Log Completo (13-14 Abril 2026)

## Resumen ejecutivo

Dos sesiones de trabajo intensivo sobre dark psytrance generado por IA. Se construyo un engine completo desde cero, se itero 9+ veces, se descubrio como cargar presets de fabrica de Surge XT desde Python, y se genero un catalogo de 15 tracks con diferentes combinaciones de sonidos para que Juan elija sus favoritos.

## Sesion 1 (esta sesion) — La principal

### Logros clave
1. **Engine de composicion v1-v7**: estructura completa de dark psy con ORDER/CHAOS/SILENCE/DROPS
2. **Analisis espectral de Glosolalia**: perfil de referencia calibrado (entropia 12.5 bits, 8/10 bandas activas)
3. **Investigacion de produccion**: Psykovsky, Kindzadza, Frantic Noise, Will O Wisp — tecnicas, synths, DAWs
4. **Pipeline Surge XT via pedalboard**: MIDI -> Surge XT -> WAV desde Python CLI
5. **KranchDD instalado y funcional** desde Python
6. **Control OSC a Reaper**: tweaking en tiempo real
7. **Descubrimiento: raw_state carga presets .fxp**: acceso a 3008 presets de fabrica
8. **15 tracks generados** con combinaciones random de presets — pendiente feedback de Juan

### Versiones del track
| Version | Que cambio | Resultado |
|---------|-----------|-----------|
| v1 | MIDI basico con mido | Sin alma, metronomico |
| v2 | Calibrado vs Glosolalia | Mejor espectro, mecanico |
| v3 | Humanizacion, groove | Mas vivo, falta contraste |
| v4 | 300Hz notch kick, FM, granular | Mas genero-accurate |
| v5 | ORDER vs CHAOS explicito | Buen concepto, entropia invertida |
| v6 | Silencios + drops 1/32 | Concepto correcto, ejecucion "asesinato auditivo" |
| v7 | 5 tipos de drops musicales | **Estructura funciona, Juan conecto con la musica** |
| v8 | KranchDD processing | Proof of concept VST desde Python |
| v9 | Surge XT rendering MIDI | Primer track con synth real |
| v9b-d | Bass warm, lead fix | Mejoras incrementales |

### Descubrimientos musicales (de Juan)
- **ORDER vs CHAOS**: la gente necesita orden para bailar, caos para perder la cabeza
- **El silencio es un arma**: despues de intensidad, silencio. Cuando vuelve, vuelve MAS FUERTE
- **Los drops son musicales**: no ametralladora (32 kicks/bar) sino re-entrada gradual
- **"pan pan pan [silencio] PANAPANAPAPANANPAN"**: aceleracion dentro de la frase, no matematica
- **La musica no es matematica con ritmo, es intencion con forma de sonido**

### Hallazgo tecnico clave: Preset loading
```python
surge = load_plugin(SURGE_PATH)
with open(preset_path, 'rb') as f:
    surge.raw_state = f.read()
result = surge(midi_events, duration=TOTAL_TIME, sample_rate=44100, num_channels=2)
```
Esto permite cargar CUALQUIER preset .fxp de Surge XT y renderizar MIDI a traves de el.

## Sesion 2 (otra instancia) — Audio Doctor

### Logros
- audio_doctor.py: diagnostico profesional (LUFS, THD, True Peak, colisiones)
- kick_lab.py: 5 variantes, Juan eligio v5_hibrido (industrial + gordo)
- Identifico problemas de calidad: THD 35%, clips, mud

### Reglas de audio descubiertas
- **NUNCA** manipular ganancia sample por sample (genera clicks)
- **NUNCA** filtrar por chunks sin estado (discontinuidades)
- **SEGURO**: filtros scipy, saturacion tanh global
- **Arreglar desde la fuente** (Surge XT presets), no post-procesar

### Parametros pro de dark psy bass (de foros)
- Saw, -2 octavas, LP 24dB, **resonancia casi cero**
- Amp ADSR: 0/0/0/0 (full gate)
- Filter env: +50%, decay ~500ms
- HPF output: 35-40Hz, >64dB/oct
- Mid dip: ~250Hz

## Proximo paso

**Juan escucha los 15 tracks** en Desktop/samples/ y dice:
- "el bajo del Track 05"
- "el lead del Track 12"
- "el pad del Track 03"

Con eso se arma el track final con la mejor combinacion de presets profesionales.

## Archivos del proyecto

### Core engine
| Archivo | Descripcion |
|---------|-------------|
| synth_darkpsy_v7.py | Engine principal (composicion, estructura, drops) |
| render_v9.py | Pipeline MIDI -> Surge XT -> WAV |
| surge_presets.py | Configuraciones de Surge XT por elemento |
| generate_samples.py | Generador de 15 tracks con presets random |
| preset_audition.py | Audicion de presets individuales |

### Herramientas
| Archivo | Descripcion |
|---------|-------------|
| audio_doctor.py | Diagnostico profesional de audio |
| stem_player.py | Player interactivo de stems |
| kick_lab.py | Laboratorio de kicks |
| live_control.py | Control OSC para Reaper en tiempo real |

### Documentacion
| Archivo | Descripcion |
|---------|-------------|
| README.md | Documentacion tecnica completa |
| LA_HISTORIA.md | Narrativa humanizada del proyecto |
| PARA_EL_PRODUCTOR.md | Guia para un productor humano |
| SESSION_LOG.md | Este archivo |

### Outputs
| Carpeta | Contenido |
|---------|-----------|
| Desktop/samples/ | 15 tracks con presets diferentes (PENDIENTE FEEDBACK) |
| auditions/ | Demos cortos por elemento (bass/, lead/, acid/, pad/, fx/) |
| stems_v9/ | Stems individuales de la v9 |
| presets/PsyWorld/ | Vital presets gratuitos descargados |

## Software instalado
- Reaper (DAW)
- Surge XT (synth VST3, 3008 presets de fabrica)
- KranchDD (distorsion/filtro de Kindzadza, VST3)
- Python: mido, numpy, scipy, pedalboard (Spotify), python-osc, sounddevice

## Repo
**github.com/asastuai/Darkpsy-engine** — publico

## Frase del proyecto
*"El silencio antes del drop es la parte mas fuerte del track"*
