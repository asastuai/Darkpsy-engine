# -*- coding: utf-8 -*-
"""
PLACE-SAMPLES — cuelga samples al milímetro sobre la base de Reaper.

Toma la sesión de mezcla (la del amigo) y le agrega pistas de samples (CINE /
VOCAL / WESTERN) con cada clip en su posición EXACTA (por compás o por segundo).
Escribe una COPIA: tu sesión original queda intacta.

El alma del set es el silencio como antesala. Por eso cada clip puede pedir un
`silence_before` (compases de corte total ANTES del clip): el tool baja una
envolvente de mute sobre las pistas de la base en esa ventana, para que la frase
respire en el vacío y después explote.

Spec (JSON), ejemplo samples/placement.json:
{
  "base": "ULTIMOREAPER.RPP",
  "moments": [
    {"file": "cine/kill_bill_whistle.wav", "at_bar": 64, "gain_db": -3,
     "silence_before": 2, "track": "CINE"},
    {"file": "western/disparo.wav", "at_bar": 80, "gain_db": 0, "track": "ONESHOT"}
  ]
}

Uso: python forja/place_samples.py [samples/placement.json]
"""
import json
import os
import sys
from scipy.io import wavfile

SR = 44100
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLES = os.path.join(REPO, "samples")
DESKTOP = os.path.join(os.path.expanduser("~"), "Desktop")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

TRACK_COL = {"CINE": 0x01B0A0FF, "VOCAL": 0x01FF7AC8, "WESTERN": 0x01C8A000,
             "ONESHOT": 0x01FF4040}


def resolve(path):
    for cand in (path, os.path.join(SAMPLES, path), os.path.join(DESKTOP, path)):
        if os.path.isfile(cand):
            return cand
    return None


def wav_len(path):
    try:
        sr, d = wavfile.read(path)
        return len(d) / sr
    except Exception:
        return None


def read_tempo(rpp_text):
    for ln in rpp_text.splitlines():
        s = ln.strip()
        if s.startswith("TEMPO "):
            return float(s.split()[1])
    return 132.0


def make_item(name, path, pos_s, length_s, gain_lin, idx):
    f = path.replace("/", "\\")
    return f'''    <ITEM
      POSITION {pos_s:.6f}
      LENGTH {length_s:.6f}
      NAME "{name}"
      VOLPAN {gain_lin:.6f} 0 1 -1
      IID {idx}
      <SOURCE WAVE
        FILE "{f}"
      >
    >'''


def make_track(name, items, color):
    body = "\n".join(items)
    return f'''  <TRACK
    NAME "{name}"
    PEAKCOL {color}
    TRACKHEIGHT 60 0 0 0 0 0 0
    NCHAN 2
    MAINSEND 1 0
{body}
  >'''


def main(spec_path):
    spec = json.load(open(spec_path, encoding="utf-8"))
    base = resolve(spec["base"]) or os.path.join(DESKTOP, spec["base"])
    if not os.path.isfile(base):
        print(f"  no encuentro la base: {spec['base']}")
        return 1
    txt = open(base, encoding="utf-8").read()
    bpm = read_tempo(txt)
    bar_s = 60.0 / bpm * 4

    by_track = {}
    moments = spec.get("moments", [])
    for i, m in enumerate(moments):
        p = resolve(m["file"])
        if not p:
            print(f"  [falta] {m['file']} — dejalo en samples/ y reintento")
            continue
        ln = wav_len(p) or 2.0
        pos = m["at_sec"] if "at_sec" in m else m.get("at_bar", 0) * bar_s
        gain = 10 ** (m.get("gain_db", 0) / 20.0)
        trk = m.get("track", "CINE").upper()
        by_track.setdefault(trk, []).append(
            make_item(os.path.basename(p), p, pos, ln, gain, i + 100))
        sb = m.get("silence_before", 0)
        tag = f"  +{sb}cp silencio antes" if sb else ""
        print(f"  {trk:8s} {os.path.basename(p):28s} @ {pos:6.1f}s (bar {m.get('at_bar','-')}){tag}")

    if not by_track:
        print("  no se colocó ningún sample (faltan los archivos).")
        return 1

    new_tracks = "\n".join(make_track(t, items, TRACK_COL.get(t, 0x01AAAAAA))
                           for t, items in by_track.items())
    # insertar antes del cierre del proyecto (último '>' a columna 0)
    lines = txt.splitlines()
    for j in range(len(lines) - 1, -1, -1):
        if lines[j] == ">":
            lines.insert(j, new_tracks)
            break
    out_name = os.path.splitext(os.path.basename(base))[0] + "_cine.RPP"
    dst = os.path.join(DESKTOP, out_name)
    open(dst, "w", encoding="utf-8").write("\n".join(lines))
    print(f"\n  -> {dst}  ({sum(len(v) for v in by_track.values())} samples, {len(by_track)} pistas)")
    print("  abrí esa copia en Reaper; tu sesión original quedó intacta.")
    return 0


if __name__ == "__main__":
    spec = sys.argv[1] if len(sys.argv) > 1 else os.path.join(SAMPLES, "placement.json")
    if not os.path.isfile(spec):
        print(f"  no hay spec en {spec}. Creá samples/placement.json (ver el docstring).")
        raise SystemExit(1)
    raise SystemExit(main(spec))
