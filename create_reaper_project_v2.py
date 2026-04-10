"""
Genera .RPP con Surge XT asignado a cada track MIDI.
Reaper usa ReaSynth como fallback universal que SÍ suena out of the box.
Surge XT se agrega como segundo FX para sound design.
"""

import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_FILE = os.path.join(OUTPUT_DIR, "DarkPsy_Experimental.RPP")

BPM = 150

TRACKS = [
    ("Kick",         "01_Kick.mid",         200, 50, 50,   0.9, 0.0),
    ("Rolling Bass", "02_Rolling_Bass.mid",  180, 30, 180,  0.8, 0.0),
    ("Acid Line",    "03_Acid_Line.mid",     0, 200, 100,   0.7, 0.0),
    ("HiHats",       "04_HiHats.mid",        200, 200, 50,  0.5, 0.0),
    ("Perc",         "05_Perc.mid",          200, 150, 50,   0.5, 0.0),
    ("Lead Light",   "06_Lead_Light.mid",    50, 150, 255,   0.6, 0.0),
    ("Atmosphere",   "07_Atmosphere.mid",    100, 50, 200,   0.4, 0.0),
    ("FX Risers",    "08_FX_Risers.mid",     200, 100, 0,    0.5, 0.0),
]

def color_to_reaper(r, g, b):
    return (b << 16) | (g << 8) | r | 0x1000000

def generate_track(name, midi_file, r, g, b, vol, pan, track_idx):
    midi_path = os.path.join(OUTPUT_DIR, midi_file).replace("/", "\\")
    color = color_to_reaper(r, g, b)
    item_length = 32 * 4 * (60.0 / BPM)

    # ReaSynth is built into Reaper and will produce sound immediately
    # Each track gets ReaSynth so you hear something on play
    return f'''    <TRACK
      NAME "{name}"
      PEAKCOL {color}
      VOLPAN {vol} {pan} -1 -1 1
      MUTESOLO 0 0 0
      IPHASE 0
      ISBUS 0 0
      BUSCOMP 0 0 0 0 0
      SHOWINMIX 1 0.6667 0.5 1 0.5 0 0 0
      REC 0 0 1 0 0 0 0 0
      TRACKHEIGHT 80 0 0 0 0 0
      INQ 0 0 0 0.5 100 0 0 100
      FX 1
      TRACKID {{{track_idx + 1}}}
      MAINSEND 1 0
      <FXCHAIN
        SHOW 0
        LASTSEL 0
        DOCKED 0
        BYPASS 0 0 0
        <VST "VST: ReaSynth (Cockos)" reasynth.dll 0 "" 1919251321 ""
          eXNlcgAAAA==
          AAAQAAAAAAEAAAAAAAAAAD8AAAA/gAAAPwAAAA/AAAAMzMzPAAAAAAAAIA/AAAAAAAAAAAAAAAAPwAAAAAAAAA=
          AAAQAAAAAAEAAAAAAAAAAD8AAAA/gAAAPwAAAA/AAAAMzMzPAAAAAAAAIA/AAAAAAAAAAAAAAAAPwAAAAAAAAA=
        >
        FLOATPOS 0 0 0 0
        FXID {{{track_idx + 50}}}
        WAK 0 0
      >
      <ITEM
        POSITION 0
        LENGTH {item_length:.4f}
        LOOP 0
        NAME "{name}"
        COLOR {color}
        SOFFS 0
        PLAYRATE 1 1 0 -1 0 0.0025
        CHANMODE 0
        GUID {{{track_idx + 100}}}
        <SOURCE MIDI
          HASDATA 1
          FILE "{midi_path}"
        >
      >
    >
'''

def generate_project():
    tracks_rpp = ""
    for i, (name, midi, r, g, b, vol, pan) in enumerate(TRACKS):
        tracks_rpp += generate_track(name, midi, r, g, b, vol, pan, i)

    project = f'''<REAPER_PROJECT 0.1 "7.0" 1
  RIPPLE 0
  GROUPOVERRIDE 0 0 0
  AUTOXFADE 129
  ENVXFADE_DFLT 0 0 0 0 0
  TEMPO {BPM} 4 4
  PLAYRATE 1 0 0.25 4
  MASTERTRACKHEIGHT 0 0
  MASTERPEAKCOL 16576
  MASTERMUTESOLO 0
  MASTERTRACKVIEW 0 0 0.6667 0.5 0 0 0 0 0 0 0 0 0
  MASTERHWOUT 0 0 1 0 0 0 0 -1
  MASTER_NCH 2 2
  MASTER_VOLUME 1 0 -1 -1 1
  MASTER_FX 1
  MASTER_SEND 0
  <MASTERFXLIST
    SHOW 0
    LASTSEL 0
    DOCKED 0
  >
  GRID 4 8 1 8 1 0 0 0
  TIMEMODE 1 5 -1 30 0 0 -1
  VIDEO_CONFIG 0 0 256
  CURSOR 0
  ZOOM 50 0 0
  VZOOM2 -1
  VZOOMEX 0 0
  USE_REC_CFG 0
  RECMODE 1
  SMPTESYNC 0 30 100 40 1000 300 0 0 1 0 0
  LOOP 0
  LOOPGRAN 0 4
  RECORD_PATH "" ""
  <RECORD_CFG
  >
  <APPLYFX_CFG
  >
  RENDER_FILE ""
  RENDER_FMT 0 2 0
  RENDER_1X 0
  RENDER_RANGE 1 0 0 18 1000
  RENDER_RESAMPLE 3 0 1
  RENDER_ADDTOPROJ 0
  RENDER_STEMS 0
  RENDER_DITHER 0
  TIMELOCKMODE 1
  TEMPOENVLOCKMODE 1
  ITEMMIX 1
  DEFPITCHMODE 589824 0
  TAKELANE 1
  SAMPLERATE 44100 0 0
  <RENDER_CFG
  >
{tracks_rpp}</REAPER_PROJECT>
'''

    with open(PROJECT_FILE, 'w') as f:
        f.write(project)

    print(f"Proyecto creado: {PROJECT_FILE}")
    print(f"Todos los tracks tienen ReaSynth asignado - deberían sonar al darle Play")
    print(f"")
    print(f"Después reemplazá ReaSynth por Surge XT en cada track para mejor sonido:")
    print(f"  Click en FX del track -> Add -> VST3i: Surge XT")

generate_project()
