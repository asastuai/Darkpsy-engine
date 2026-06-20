# -*- coding: utf-8 -*-
"""
BUILD-WHISTLE-MOMENT-RPP — arma el proyecto de Reaper con la consigna de Juan:

  el silbido (CINE) suena SOLO hasta el segundo 21, y en ese instante entra la
  base de Reaper TAL CUAL, desde su primer kick (su "bar 10.5"). El kick, el
  bajo y lo demás arrancan en 0:21. FM y lead muteados (la "base perfecta").

Detecta el primer kick del stem y lo alinea exactamente al segundo 21 (SOFFS),
así el drop cae sobre un kick de verdad, no sobre el intro vacío.

Uso: python forja/build_whistle_moment_rpp.py [t_drop]   (default 21)
"""
import os
import re
import sys
import numpy as np
from scipy.io import wavfile

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

DESKTOP = os.path.join(os.path.expanduser("~"), "Desktop")
BASE_RPP = os.path.join(DESKTOP, "ULTIMOREAPER.RPP")
STEMS = os.path.join(DESKTOP, "DarkPsy_techno132_stems")
WHISTLE = os.path.join(DESKTOP, "twisted_nerve.wav")
OUT = os.path.join(DESKTOP, "ULTIMOREAPER_cine.RPP")
SR = 44100
T_DROP = float(sys.argv[1]) if len(sys.argv) > 1 else 21.0
MUTE = {"FM", "LEAD"}     # la base perfecta de Juan: fm + lead muteados


def first_kick_offset():
    sr, d = wavfile.read(os.path.join(STEMS, "kick.wav"))
    m = np.abs((d.mean(axis=1) if d.ndim > 1 else d).astype(np.float64) / 32768.0)
    w = int(0.005 * sr)
    env = np.convolve(m, np.ones(w) / w, mode="same")
    thr = 0.4 * env.max()
    i = int(1.0 * sr)
    while i < len(env):
        if env[i] > thr:
            return i / sr
        i += 1
    return 19.09   # fallback: bar 10.5 @ 132


def whistle_len():
    sr, d = wavfile.read(WHISTLE)
    return len(d) / sr


def cine_track(length):
    return f'''  <TRACK
    NAME CINE
    PEAKCOL 16776960
    TRACKHEIGHT 110 0 0 0 0 0 0
    NCHAN 2
    VOLPAN 1 0 -1 -1 1
    MAINSEND 1 0
    <ITEM
      POSITION 0
      LENGTH {length:.4f}
      FADEOUT 1 0.40 0 1 0 0 0
      NAME "twisted_nerve (silbido solo -> 0:{int(T_DROP)})"
      VOLPAN 1 0 1 -1
      SOFFS 0
      <SOURCE WAVE
        FILE "{WHISTLE}"
      >
    >
  >'''


def main():
    koff = first_kick_offset()
    print(f"  primer kick del stem en {koff:.2f}s  ->  lo alineo al segundo {T_DROP:.0f}")
    txt = open(BASE_RPP, encoding="utf-8").read().splitlines()

    out = []
    depth = 0
    curname = None
    pending_name = False
    item_active = False
    item_depth = 0
    base_items = 0
    muted = []
    for line in txt:
        st = line.strip()
        opening = st.startswith("<")
        closing = (st == ">")
        if opening:
            depth += 1
            if st.startswith("<TRACK"):
                curname = None
                pending_name = True
            if st.startswith("<ITEM") and curname and curname not in ("CINE",):
                item_active = True
                item_depth = depth
        if pending_name and st.startswith("NAME "):
            curname = st[5:].strip().strip('"')
            pending_name = False
        # mute FM/lead a nivel pista
        if curname in MUTE and st.startswith("MUTESOLO ") and depth == item_depth_track(depth):
            pass  # (no-op; el mute real se hace abajo por regex simple)
        if curname in MUTE and re.match(r"\s*MUTESOLO ", line):
            line = re.sub(r"MUTESOLO \S+ \S+ \S+", "MUTESOLO 1 0 0", line)
            if curname not in muted:
                muted.append(curname)
        # mover los items de la base: arrancan en T_DROP, desde el primer kick
        if item_active:
            if re.match(r"\s*POSITION ", line):
                line = re.sub(r"POSITION \S+", f"POSITION {T_DROP:.6f}", line)
            elif re.match(r"\s*LENGTH ", line):
                ol = float(st.split()[1])
                line = re.sub(r"LENGTH \S+", f"LENGTH {max(10.0, ol - koff):.6f}", line)
            elif re.match(r"\s*SOFFS ", line):
                line = re.sub(r"SOFFS \S+", f"SOFFS {koff:.6f}", line)
                base_items += 1
        out.append(line)
        if closing:
            if item_active and depth == item_depth:
                item_active = False
            depth -= 1

    # insertar la pista CINE antes del cierre del proyecto
    cine = cine_track(T_DROP + 0.3)
    for j in range(len(out) - 1, -1, -1):
        if out[j] == ">":
            out.insert(j, cine)
            break

    open(OUT, "w", encoding="utf-8").write("\n".join(out) + "\n")
    print(f"  base movida a 0:{int(T_DROP)} ({base_items} stems, desde su primer kick), muteados: {muted}")
    print(f"  -> {OUT}")


def item_depth_track(d):
    return d  # helper trivial


if __name__ == "__main__":
    main()
