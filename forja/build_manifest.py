# -*- coding: utf-8 -*-
"""
FORJA -> MESA bridge.

Slices several musically-distinct WINDOWS out of the full Surge-rendered track
and emits a PRESET LIBRARY (library.json) + per-preset stem folders. The browser
MESA reads library.json and lets the user "generate" (pick a preset) and tweak it.

Each preset only lists stems that actually have content in that window (the engine
gates elements by section: lead lives in ORDER, fm in CHAOS, etc.), so a preset is
an honest set of active stems.

No ffmpeg: writes 16-bit WAV. webm/opus transcode comes with the Vercel deploy.
"""
import os, json
import numpy as np
from scipy.io import wavfile

SR = 44100
BPM = 150
ROOT = "E"
SEED = 666
BEAT = 60.0 / BPM
BAR = BEAT * 4
NEAR_SILENT_DB = -50.0

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
STEMS_IN = os.path.join(REPO, "stems_v9")
PUBLIC = os.path.join(REPO, "mesa", "public")
STEMS_OUT_ROOT = os.path.join(PUBLIC, "stems")
LIBRARY_OUT = os.path.join(PUBLIC, "library.json")

# Musically-distinct windows. (start_bar, end_bar) exclusive end.
WINDOWS = [
    ("orden",   "Orden",   "Groove hipnotico 4/4. Bass rodante, acid y lead. Para bailar.",        (91, 120)),
    ("caos",    "Caos",    "Tormenta FM, patrones irregulares. Para perder la cabeza.",            (124, 148)),
    ("tension", "Tension", "Build que sube: el kick se densifica antes del estallido.",            (165, 175)),
]

# stem -> (file in stems_v9, label, default mix gain from render_v9, band, color, tip)
STEMS = [
    ("kick",  "kick.wav",       "Kick",  0.90, "sub",      "#ff2d55", "El thud grave que maneja el ritmo. 40-80 Hz."),
    ("bass",  "bass.wav",       "Bass",  0.85, "bass",     "#ff7a00", "El bajo rodante. La columna del dark psy. 60-200 Hz."),
    ("drums", "drums.wav",      "Drums", 0.55, "high",     "#00e5ff", "Hi-hats y claps. El shuffle que respira. 6-12 kHz."),
    ("acid",  "acid.wav",       "Acid",  0.55, "mid",      "#00ff88", "La linea acida squelchy (estilo 303). 300 Hz-2 kHz."),
    ("lead",  "lead.wav",       "Lead",  0.50, "mid-high", "#b388ff", "La melodia etereal, atras en el mix. 1-4 kHz."),
    ("pad",   "pad.wav",        "Pad",   0.40, "low-mid",  "#4488ff", "El colchon atmosferico que da espacio. 200-600 Hz."),
    ("fm",    "fm_texture.wav", "FM",    0.45, "high",     "#ff00bb", "Texturas FM alienigenas (caos). Esparcidas."),
    ("fx",    "fx.wav",         "FX",    0.48, "full",     "#ffffff", "Risers e impactos. Tension y transiciones."),
]

# section map replica (render_v9) + chaos amount per section
TOTAL_BARS = 280
_smap = {}
def _ss(s, e, t):
    for b in range(s, min(e, TOTAL_BARS)): _smap[b] = t
_ss(0,10,'intro'); _ss(10,30,'order'); _ss(30,31,'silence'); _ss(31,33,'drop')
_ss(33,42,'chaos'); _ss(42,43,'silence'); _ss(43,45,'drop'); _ss(45,70,'order')
_ss(70,71,'silence'); _ss(71,73,'drop'); _ss(73,88,'chaos'); _ss(88,89,'silence')
_ss(89,91,'drop'); _ss(91,120,'order'); _ss(120,122,'silence'); _ss(122,124,'drop')
_ss(124,148,'chaos'); _ss(148,149,'silence'); _ss(149,165,'break')
_ss(165,175,'build'); _ss(175,176,'silence'); _ss(176,178,'drop')
_ss(178,210,'order'); _ss(210,211,'silence'); _ss(211,213,'drop')
_ss(213,240,'chaos'); _ss(240,241,'silence'); _ss(241,243,'drop')
_ss(243,268,'order'); _ss(268,TOTAL_BARS,'outro')
for b in range(TOTAL_BARS):
    _smap.setdefault(b, 'order')
_CA = {'order':0.0, 'chaos':1.0, 'drop':0.4, 'silence':0.0,
       'break':0.1, 'intro':0.05, 'outro':0.05, 'build':0.5}

def window_smap(start_bar, end_bar):
    blocks = []
    for b in range(start_bar, end_bar):
        lab = _smap.get(b, 'order')
        rb = b - start_bar
        if blocks and blocks[-1]["label"] == lab and blocks[-1]["endBar"] == rb:
            blocks[-1]["endBar"] = rb + 1
        else:
            blocks.append({"label": lab, "startBar": rb, "endBar": rb + 1, "chaos": _CA.get(lab, 0.0)})
    return blocks

def read_stereo(path):
    _, data = wavfile.read(path)
    if data.ndim == 1:
        data = np.column_stack([data, data])
    if data.dtype == np.int16:
        data = data.astype(np.float64) / 32768.0
    elif data.dtype == np.int32:
        data = data.astype(np.float64) / 2147483648.0
    else:
        data = data.astype(np.float64)
    return data

def main():
    # cache full stems in memory once
    cache = {}
    for name, fname, *_ in STEMS:
        p = os.path.join(STEMS_IN, fname)
        cache[name] = read_stereo(p) if os.path.exists(p) else None

    presets = []
    print("=" * 60)
    print(" FORJA -> MESA  preset library builder")
    print("=" * 60)
    for pid, plabel, pdesc, (sb, eb) in WINDOWS:
        start_s = int(sb * BAR * SR)
        end_s = int(eb * BAR * SR)
        dur = (end_s - start_s) / SR
        out_dir = os.path.join(STEMS_OUT_ROOT, pid)
        os.makedirs(out_dir, exist_ok=True)
        print(f"\n[{plabel}]  bars {sb}-{eb}  ({eb-sb} bars, {dur:.1f}s)")
        stem_entries = []
        for name, fname, label, gain, band, color, tip in STEMS:
            data = cache.get(name)
            if data is None:
                continue
            seg = data[start_s:end_s] if end_s <= len(data) else np.pad(
                data, ((0, max(0, end_s - len(data))), (0, 0)))[start_s:end_s]
            rms = float(np.sqrt(np.mean(seg ** 2)) + 1e-12)
            rms_db = 20 * np.log10(rms)
            if rms_db < NEAR_SILENT_DB:
                print(f"   - {label:6s} {rms_db:6.1f} dB  (silent in this section, skipped)")
                continue
            out_i16 = (np.clip(seg, -1.0, 1.0) * 32767).astype(np.int16)
            wavfile.write(os.path.join(out_dir, f"{name}.wav"), SR, out_i16)
            print(f"     {label:6s} {rms_db:6.1f} dB")
            stem_entries.append({
                "name": name, "label": label, "url": f"stems/{pid}/{name}.wav",
                "defaultGain": gain, "band": band, "color": color, "tip": tip,
                "rmsDb": round(rms_db, 1),
            })
        presets.append({
            "id": pid, "label": plabel, "desc": pdesc,
            "loop": {"bars": eb - sb, "durationSec": round(dur, 4), "sourceBars": [sb, eb]},
            "smap": window_smap(sb, eb),
            "stems": stem_entries,
        })

    library = {"schemaVersion": 2, "seed": SEED, "bpm": BPM, "root": ROOT, "presets": presets}
    os.makedirs(PUBLIC, exist_ok=True)
    with open(LIBRARY_OUT, "w", encoding="utf-8") as f:
        json.dump(library, f, indent=2, ensure_ascii=False)
    print(f"\n  Wrote {len(presets)} presets -> {LIBRARY_OUT}")
    print("  Done.")

if __name__ == "__main__":
    main()
