"""
Generate Reaper project with v7 stems loaded, ready for live tweaking.
"""
import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
STEMS_DIR = os.path.join(OUTPUT_DIR, "stems_v7").replace("/", "\\")
PROJECT_FILE = os.path.join(OUTPUT_DIR, "DarkPsy_LIVE.RPP")

BPM = 150

TRACKS = [
    ("Kick",        "01_kick.wav",        200, 50, 50),
    ("Bass",        "02_bass.wav",        180, 30, 180),
    ("FM Textures", "03_fm_textures.wav",  0, 200, 100),
    ("Electricity", "04_electricity.wav",  200, 200, 0),
    ("Drums",       "05_drums.wav",       200, 200, 50),
    ("Lead",        "06_lead.wav",        50, 150, 255),
    ("Atmosphere",  "07_atmosphere.wav",  100, 50, 200),
    ("Granular",    "08_granular.wav",    150, 100, 50),
    ("FX",          "09_fx.wav",          200, 100, 0),
]

def color(r,g,b):
    return (b<<16)|(g<<8)|r|0x1000000

def track_block(name, wav, r, g, b, idx):
    c = color(r,g,b)
    path = os.path.join(STEMS_DIR, wav)
    # 448 seconds = 7.5 min
    length = 448.0
    return f'''    <TRACK
      NAME "{name}"
      PEAKCOL {c}
      VOLPAN 1 0 -1 -1 1
      MUTESOLO 0 0 0
      IPHASE 0
      ISBUS 0 0
      BUSCOMP 0 0 0 0 0
      SHOWINMIX 1 0.6667 0.5 1 0.5 0 0 0
      REC 0 0 1 0 0 0 0 0
      TRACKHEIGHT 80 0 0 0 0 0
      INQ 0 0 0 0.5 100 0 0 100
      FX 1
      TRACKID {{{idx+1}}}
      MAINSEND 1 0
      <ITEM
        POSITION 0
        LENGTH {length}
        LOOP 0
        NAME "{name}"
        COLOR {c}
        SOFFS 0
        PLAYRATE 1 1 0 -1 0 0.0025
        CHANMODE 0
        GUID {{{idx+100}}}
        <SOURCE WAVE
          FILE "{path}"
        >
      >
    >
'''

tracks = ""
for i, (name, wav, r, g, b) in enumerate(TRACKS):
    tracks += track_block(name, wav, r, g, b, i)

project = f'''<REAPER_PROJECT 0.1 "7.0" 1
  RIPPLE 0
  GROUPOVERRIDE 0 0 0
  AUTOXFADE 129
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
  ZOOM 30 0 0
  VZOOM2 -1
  VZOOMEX 0 0
  USE_REC_CFG 0
  RECMODE 1
  LOOP 0
  LOOPGRAN 0 4
  RECORD_PATH "" ""
  <RECORD_CFG
  >
  <APPLYFX_CFG
  >
  RENDER_FILE ""
  SAMPLERATE 44100 0 0
  <RENDER_CFG
  >
{tracks}</REAPER_PROJECT>
'''

with open(PROJECT_FILE, 'w') as f:
    f.write(project)

print(f"Proyecto creado: {PROJECT_FILE}")
print(f"9 tracks con stems de v7")
print(f"BPM: {BPM}")
print(f"Listo para abrir en Reaper")
