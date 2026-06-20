# -*- coding: utf-8 -*-
"""
VITAL-SETUPS — genera variantes del bajo growl como archivos .vital, tomando el
patch base (Growl_Darkpsy.vital, que ya carga OK) y cambiando SOLO valores
numericos de claves que ya existen (no toca estructura ni wavetables = no rompe).

Cada setup explora una direccion sonora distinta para que Juan los escuche uno
a uno y diga cual pega.

Uso: python forja/vital_setups.py <setup>     (profundo | gruñon | electrico)
"""
import json
import os
import sys

DESKTOP = os.path.join(os.path.expanduser("~"), "Desktop")
BASE = os.path.join(DESKTOP, "Growl_Darkpsy.vital")
if not os.path.isfile(BASE):
    BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "docs", "Growl_Darkpsy.vital")

# cada setup = overrides sobre settings (claves que YA existen en el base)
SETUPS = {
    "profundo": {
        "_desc": "Profundo y calido: menos FM, filtro oscuro, sub con cuerpo, drive moderado, sin tic, con aire",
        "distortion_drive": 14.0,         # menos mugre (era 30)
        "osc_1_distortion_amount": 0.30,  # menos FM = menos aspero (era 0.45)
        "filter_1_cutoff": 58.0,          # mas oscuro/grave (era 83)
        "filter_2_cutoff": 50.0,          # (era 72)
        "filter_1_resonance": 0.52,       # menos chillon (era 0.66)
        "env_1_attack": 0.10,             # un pelin de ataque = mata el click de inicio (era 0)
        "env_1_release": 0.12,            # release corto = mata el click de final (era 0)
        "osc_3_on": 1.0,                  # SUB para cuerpo/presencia (estaba off)
        "osc_3_level": 0.45,
        "osc_3_transpose": -24.0,         # una octava bajo el osc1 = sub profundo
        "reverb_on": 1.0,                 # aire (mata el "seco")
        "reverb_dry_wet": 0.20,
    },
    "gruñon": {
        "_desc": "Mas gruñon/alien: mas FM, bandpass resonante, drive medio-alto",
        "distortion_drive": 20.0,
        "osc_1_distortion_amount": 0.62,  # mas FM = mas inarmonico/gruñon
        "filter_1_cutoff": 75.0,
        "filter_1_resonance": 0.74,       # bandpass mas resonante = mas vocal
        "filter_2_cutoff": 65.0,
        "env_1_attack": 0.05,
        "env_1_release": 0.10,
        "reverb_on": 1.0,
        "reverb_dry_wet": 0.12,
    },
    "electrico": {
        "_desc": "Mas electrico: el LFO escalonado protagonista, movimiento fuerte",
        "distortion_drive": 16.0,
        "osc_1_distortion_amount": 0.40,
        "filter_1_cutoff": 66.0,
        "filter_1_resonance": 0.60,
        "filter_2_cutoff": 58.0,
        "env_1_attack": 0.06,
        "env_1_release": 0.10,
        "osc_3_on": 1.0,
        "osc_3_level": 0.35,
        "osc_3_transpose": -24.0,
    },
}


def main(name):
    if name not in SETUPS:
        print(f"  setup desconocido: {name}. disponibles: {list(SETUPS)}")
        return 1
    data = json.load(open(BASE, encoding="utf-8"))
    s = data["settings"]
    overrides = SETUPS[name]
    applied = []
    for k, v in overrides.items():
        if k.startswith("_"):
            continue
        old = s.get(k, "AUSENTE")
        s[k] = v
        applied.append(f"{k}: {old} -> {v}")
    data["preset_name"] = f"Growl {name.capitalize()}"
    data["comments"] = overrides.get("_desc", "")
    out = os.path.join(DESKTOP, f"Growl_{name.capitalize()}.vital")
    # sin BOM (critico para que cargue en Vital)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    print(f"  setup '{name}': {overrides['_desc']}")
    for a in applied:
        print("   ", a)
    print(f"  -> {out}")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    name = sys.argv[1] if len(sys.argv) > 1 else "profundo"
    sys.exit(main(name))
