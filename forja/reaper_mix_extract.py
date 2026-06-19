# -*- coding: utf-8 -*-
"""
REAPER-MIX-EXTRACT — convierte el template de mezcla de un .RPP en NÚMEROS.

Un amigo de Juan ecualizó/procesó nuestros stems en Reaper. Sus cadenas son la
mejor referencia que tenemos de "cómo suena ameno". Esto lee el .RPP y extrae,
por canal:
  - volumen / pan
  - ReaEQ  -> bandas decodificadas (freq Hz, ganancia dB, ancho en octavas)
  - KranchDD (KINDZAudio) -> parámetros de distorsión (XML embebido, legible)
  - ReaComp / ReaVerb / ReaDelay -> nombre de preset
  - efectos JS -> su línea de parámetros (texto plano)

Salida: forja/mix_template_<tag>.json + resumen en consola. Material de
referencia (nuestros stems, settings del amigo): no es audio, son números.

Uso: python forja/reaper_mix_extract.py [ruta.RPP]
"""
import base64
import json
import math
import os
import re
import struct
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

DEFAULT_RPP = os.path.join(os.path.expanduser("~"), "Desktop", "ULTIMOREAPER.RPP")


def seg1(lines):
    """Primera corriente base64 (hasta la línea que cierra con '='): el chunk real."""
    buf = ""
    for ln in lines:
        buf += ln
        if ln.endswith("="):
            break
    buf = buf.rstrip("=")
    try:
        return base64.b64decode(buf + "=" * (-len(buf) % 4))
    except Exception:
        return b""


def all_b64(lines):
    """Decodifica todo lo decodificable (para buscar XML embebido)."""
    buf = "".join(lines).rstrip("=")
    try:
        return base64.b64decode(buf + "=" * (-len(buf) % 4))
    except Exception:
        return b""


def reaeq_bands(blob):
    """Decodifica bandas de ReaEQ. Layout (verificado contra valores sensatos):
    header constante de 57 bytes, luego int32 size, int32 nbands, y por banda:
    int32 type, int32 enabled, double freq_hz, double gain_lineal, double bw_oct."""
    bands = []
    if len(blob) < 72:
        return bands
    try:
        nb = struct.unpack_from("<i", blob, 64)[0]
    except Exception:
        return bands
    if not (0 < nb <= 16):
        return bands
    off = 68
    for _ in range(nb):
        if off + 32 > len(blob):
            break
        btype, en = struct.unpack_from("<ii", blob, off)
        freq, gain, bw = struct.unpack_from("<ddd", blob, off + 8)
        off += 32
        if not (10.0 <= freq <= 22000.0):
            continue
        gain_db = 20.0 * (0 if gain <= 0 else math.log10(gain))
        bands.append({
            "type": btype, "on": bool(en),
            "freq_hz": round(freq, 1), "gain_db": round(gain_db, 2),
            "bw_oct": round(bw, 2),
        })
    return bands


_EQ_TYPE = {0: "lowshelf", 1: "band", 2: "hishelf", 3: "lopass", 4: "hipass", 5: "notch", 6: "bandpass"}


def kranch_params(blob):
    """KranchDD es Cabbage: trae un XML ASCII con los parámetros. Lo rescatamos."""
    m = re.search(rb"<CABBAGE_PRESETS[^>]*/>", blob)
    if not m:
        return None
    xml = m.group(0).decode("ascii", "ignore")
    keys = ["flt", "dst", "mix", "qm", "morph", "feedback", "type", "chain", "clip", "overx"]
    out = {}
    for k in keys:
        mm = re.search(rf'\b{k}="([-0-9.]+)"', xml)
        if mm:
            out[k] = round(float(mm.group(1)), 4)
    return out or None


def parse_rpp(path):
    with open(path, encoding="utf-8") as f:
        lines = [l.rstrip("\n") for l in f]
    tracks = []
    tempo = None
    cur = None
    i = 0
    while i < len(lines):
        s = lines[i].strip()
        if s.startswith("TEMPO ") and tempo is None:
            tempo = float(s.split()[1])
        if s.startswith("NAME ") and lines[i].startswith("  NAME") and (cur is None or cur.get("_closed")):
            pass
        if re.match(r"<TRACK\b", s):
            cur = {"name": None, "vol": None, "pan": None, "fx": []}
            tracks.append(cur)
        elif cur is not None and s.startswith("NAME ") and cur["name"] is None:
            cur["name"] = s[5:].strip().strip('"')
        elif cur is not None and s.startswith("VOLPAN ") and cur["vol"] is None:
            parts = s.split()
            cur["vol"] = round(float(parts[1]), 4)
            cur["pan"] = round(float(parts[2]), 3)
        elif cur is not None and s.startswith("<VST "):
            m = re.search(r'<VST "([^"]+)"', s)
            disp = m.group(1) if m else "VST"
            # juntar líneas base64 indentadas hasta el cierre del bloque
            b64 = []
            j = i + 1
            preset = None
            while j < len(lines):
                t = lines[j].strip()
                if t.startswith("PRESETNAME "):
                    preset = t[len("PRESETNAME "):].strip().strip('"')
                    j += 1
                    continue
                if re.match(r"^[A-Za-z0-9+/=]+$", t):
                    b64.append(t)
                    j += 1
                    continue
                break
            fx = {"plugin": disp, "preset": preset}
            if "ReaEQ" in disp:
                fx["eq_bands"] = [b for b in reaeq_bands(seg1(b64)) if b["on"]]
            elif "Kranch" in disp:
                fx["distortion"] = kranch_params(all_b64(b64))
            cur["fx"].append(fx)
            i = j - 1
        elif cur is not None and s.startswith("<JS "):
            m = re.search(r"<JS (\S+)", s)
            jsname = m.group(1) if m else "JS"
            params = lines[i + 1].strip() if i + 1 < len(lines) else ""
            params = params.split(" - ")[0].strip()  # los '-' son slots vacíos
            cur["fx"].append({"plugin": f"JS:{jsname}", "params": params})
        i += 1
    return tempo, [t for t in tracks if t["name"]]


def fmt_track(t):
    out = [f"  ● {t['name']:6s}  vol {t['vol']}  pan {t['pan']}"]
    for fx in t["fx"]:
        if "eq_bands" in fx and fx["eq_bands"]:
            shown = 0
            for b in fx["eq_bands"]:
                ty = _EQ_TYPE.get(b["type"], b["type"])
                is_filter = ty in ("hipass", "lopass", "notch", "bandpass")
                if is_filter:
                    out.append(f"      EQ {ty:8s} corte {b['freq_hz']:7.0f} Hz  bw {b['bw_oct']}")
                    shown += 1
                elif -40.0 < b["gain_db"] < 40.0:   # shelf/band real (no placeholder)
                    out.append(f"      EQ {ty:8s} {b['freq_hz']:7.0f} Hz  {b['gain_db']:+5.1f} dB  bw {b['bw_oct']}")
                    shown += 1
            if not shown:
                out.append("      EQ (sin banda activa significativa)")
        elif "distortion" in fx and fx["distortion"]:
            d = fx["distortion"]
            out.append(f"      KRANCH dist  filtro {d.get('flt')} Hz  drive {d.get('dst')}  "
                       f"mix {d.get('mix')}  Q {d.get('qm')}  morph {d.get('morph')}  type {d.get('type')}")
        elif fx.get("preset"):
            out.append(f"      {fx['plugin'].split(':')[-1].strip():16s} preset: {fx['preset']}")
        elif fx["plugin"].startswith("JS:"):
            out.append(f"      {fx['plugin']:24s} {fx.get('params','')}")
        else:
            out.append(f"      {fx['plugin']}")
    return "\n".join(out)


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_RPP
    tempo, tracks = parse_rpp(path)
    print("=" * 60)
    print(f"  TEMPLATE DE MEZCLA — {os.path.basename(path)}  ({tempo} BPM)")
    print("=" * 60)
    for t in tracks:
        print(fmt_track(t))
    tag = re.sub(r"\W+", "_", os.path.splitext(os.path.basename(path))[0]).lower()
    dst = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"mix_template_{tag}.json")
    with open(dst, "w", encoding="utf-8") as f:
        json.dump({"source": os.path.basename(path), "tempo": tempo, "tracks": tracks}, f, indent=1, ensure_ascii=False)
    print(f"\n  -> {dst}")
