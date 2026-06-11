# -*- coding: utf-8 -*-
"""
LEARN-CONSENSUS — perfil de consenso del género a partir de N tracks reales.

Hoy los gates y el matching EQ persiguen UNA referencia (Blueprints). Esto
mide muchos tracks darkpsy (audio CC de Ektoplazm, análisis legítimo) y guarda
en grammar.json el PROMEDIO + DESVÍO por banda y el espectro promedio:
  - bandas donde el desvío es chico  = ley del género (todos coinciden)
  - bandas donde el desvío es grande = gusto personal (hay libertad)

Como siempre: a grammar.json van NÚMEROS, jamás audio. La carpeta de FLACs
está gitignoreada.

Uso:
  python forja/learn_consensus.py [carpeta] [nombre_perfil]
  (default: forja/reference_audio -> reference_profiles.darkpsy_consensus)
"""
import os
import sys
import zipfile
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import soundfile as sf
import automix
import verify
from grammar import G, save

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def unzip_all(folder):
    for z in [f for f in os.listdir(folder) if f.lower().endswith(".zip")]:
        zp = os.path.join(folder, z)
        dst = os.path.join(folder, os.path.splitext(z)[0])
        if os.path.isdir(dst):
            continue
        print(f"  extrayendo {z}...")
        with zipfile.ZipFile(zp) as zf:
            zf.extractall(dst)


def find_flacs(folder):
    out = []
    for root, _, files in os.walk(folder):
        out += [os.path.join(root, f) for f in files if f.lower().endswith(".flac")]
    return sorted(out)


def measure(path):
    """Bandas + espectro suavizado + rms de un track (mono, float64)."""
    data, sr = sf.read(path, always_2d=True)
    mono = data.mean(axis=1)
    if sr != 44100:
        # resample lineal simple: para perfiles espectrales <20k alcanza
        n2 = int(len(mono) * 44100 / sr)
        mono = np.interp(np.linspace(0, len(mono) - 1, n2), np.arange(len(mono)), mono)
    bands = verify.band_profile(mono, 44100)
    freqs, db = automix.smooth_spectrum(mono)
    rms = 20 * np.log10(np.sqrt(np.mean(mono ** 2)) + 1e-12)
    return bands, freqs, db, rms


def main(folder, name):
    unzip_all(folder)
    flacs = find_flacs(folder)
    if not flacs:
        print("  no hay FLACs en", folder)
        return 1
    print(f"  midiendo {len(flacs)} tracks...")
    all_bands, all_db, all_rms = [], [], []
    freqs = None
    for p in flacs:
        try:
            bands, fr, db, rms = measure(p)
        except Exception as e:
            print(f"    [skip] {os.path.basename(p)}: {e}")
            continue
        freqs = fr
        all_bands.append(bands)
        all_db.append(db)
        all_rms.append(rms)
        bstr = " ".join(f"{k}:{v*100:.0f}%" for k, v in bands.items())
        print(f"    {os.path.basename(p)[:48]:48s} {bstr}")
    n = len(all_bands)
    keys = list(all_bands[0].keys())
    mean_b = {k: round(float(np.mean([b[k] for b in all_bands])), 4) for k in keys}
    std_b = {k: round(float(np.std([b[k] for b in all_bands])), 4) for k in keys}
    # smooth_spectrum ya normaliza (media 0 dB); promediar dB mantiene la escala
    mean_db = np.mean(np.array(all_db), axis=0)
    G["reference_profiles"][name] = {
        "bands": mean_b,
        "bands_std": std_b,
        "rms_db": round(float(np.mean(all_rms)), 1),
        "peak_db": -0.3,
        "n_tracks": n,
        "source": "Ektoplazm CC releases (analisis legitimo; solo numeros)",
        "spectrum": {
            "freqs": [round(float(f), 1) for f in freqs],
            "db": [round(float(d), 2) for d in mean_db],
        },
    }
    save()
    print(f"\n  consenso de {n} tracks -> grammar.json reference_profiles.{name}")
    print("  banda    media   desvio   veredicto")
    for k in keys:
        law = "LEY" if std_b[k] < 0.035 else ("tendencia" if std_b[k] < 0.07 else "gusto personal")
        print(f"  {k:7s}  {mean_b[k]*100:5.1f}%   ±{std_b[k]*100:4.1f}%   {law}")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    folder = sys.argv[1] if len(sys.argv) > 1 else os.path.join(REPO, "forja", "reference_audio")
    name = sys.argv[2] if len(sys.argv) > 2 else "darkpsy_consensus"
    sys.exit(main(folder, name))
