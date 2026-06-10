# -*- coding: utf-8 -*-
"""
REAPER AGENT — build a producible Reaper session from ANY set of stems.

Each .wav in --stems becomes its own named/colored track. Double-click the .RPP
to open in Reaper and produce with your ears + plugins.

  python reaper_agent/build_session.py [--stems DIR] [--out file.RPP] [--bpm 150]
Examples:
  --stems stems_v9                                  (our engine track)
  --stems forja/recreation_out/Glosolalia_Blueprint_stems   (real Glosolalia, separated)
"""
import os, glob, argparse
from scipy.io import wavfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# nice colors + sensible volume by element name (substring match)
PALETTE = {
    "kick": (255, 45, 85, 0.95), "drum": (0, 229, 255, 0.6), "bass": (255, 122, 0, 0.85),
    "acid": (0, 255, 136, 0.55), "lead": (179, 136, 255, 0.5), "pad": (68, 136, 255, 0.4),
    "fm": (255, 0, 187, 0.45), "fx": (220, 220, 220, 0.48), "other": (255, 0, 187, 0.7),
    "synth": (255, 0, 187, 0.7), "voc": (120, 200, 120, 0.6),
}
FALLBACK = [(255, 80, 80, 0.7), (80, 200, 255, 0.7), (255, 200, 80, 0.7), (160, 120, 255, 0.7)]

ap = argparse.ArgumentParser()
ap.add_argument("--stems", default=os.path.join(REPO, "stems_v9"))
ap.add_argument("--out", default="")
ap.add_argument("--bpm", type=float, default=150)
A = ap.parse_args()
A.stems = A.stems if os.path.isabs(A.stems) else os.path.join(REPO, A.stems)
if not os.path.isdir(A.stems):
    print(f"  no existe: {A.stems}"); raise SystemExit(1)
tag = os.path.basename(A.stems.rstrip("\\/")).replace("_stems", "")
OUT = A.out or os.path.join(REPO, "reaper_agent", f"DarkPsy_{tag}.RPP")

def col(r, g, b): return (b << 16) | (g << 8) | r | 0x1000000
def style(name):
    n = name.lower()
    for k, v in PALETTE.items():
        if k in n: return v
    return None

def wav_len(p):
    sr, d = wavfile.read(p); return len(d) / sr

def track(name, path, r, g, b, vol, idx):
    length = wav_len(path); p = path.replace("/", "\\"); c = col(r, g, b)
    return f'''  <TRACK
    NAME "{name}"
    PEAKCOL {c}
    VOLPAN {vol} 0 -1 -1 1
    MUTESOLO 0 0 0
    ISBUS 0 0
    TRACKHEIGHT 60 0 0 0 0 0
    TRACKID {{{idx + 10}}}
    MAINSEND 1 0
    <ITEM
      POSITION 0
      LENGTH {length:.4f}
      LOOP 0
      NAME "{name}"
      COLOR {c}
      SOFFS 0
      PLAYRATE 1 1 0 -1 0 0.0025
      GUID {{{idx + 200}}}
      IGUID {{{idx + 300}}}
      <SOURCE WAVE
        FILE "{p}"
      >
    >
  >
'''

def main():
    wavs = sorted(w for w in glob.glob(os.path.join(A.stems, "*.wav"))
                  if not os.path.basename(w).startswith("_"))
    if not wavs:
        print(f"  sin .wav en {A.stems}"); return
    tracks, n, fbi = "", 0, 0
    for w in wavs:
        name = os.path.splitext(os.path.basename(w))[0].upper()
        st = style(name)
        if st is None:
            st = FALLBACK[fbi % len(FALLBACK)]; fbi += 1
        r, g, b, vol = st
        tracks += track(name, w, r, g, b, vol, n)
        print(f"  + {name:8s} ({wav_len(w):.0f}s)")
        n += 1
    project = f'''<REAPER_PROJECT 0.1 "7.24" 1
  TEMPO {A.bpm} 4 4
  PLAYRATE 1 0 0.25 4
  SAMPLERATE 44100 0 0
  MASTER_VOLUME 1 0 -1 -1 1
  MASTER_NCH 2 2
  GRID 4 8 1 8 1 0 0 0
  CURSOR 0
  ZOOM 8 0 0
{tracks}>
'''
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(project)
    print(f"\n  Sesión ({n} tracks) -> {OUT}\n  Doble-click para abrir en Reaper.")

if __name__ == "__main__":
    main()
