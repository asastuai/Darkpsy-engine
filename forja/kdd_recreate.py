# -*- coding: utf-8 -*-
"""
KDD-RECREATE — clona el kick y el bajo de KindzaDza con las recetas EXACTAS
leidas de su pantalla en el curso (ver docs/kdd_course_extract.md).

Kick (DDKick 2.3, frame 0:01:49):
  pitch env: 8265.1 -> 1690.6 -> 227.3 -> 44.9 -> 20 Hz
  tiempos:   0 -> 4.25 -> 24.5 -> 145.25 -> 150 -> 160 ms
  curvas:    0 / -0.820 / -1.165 / 0 / 0     base C1 (32.70 Hz)

Bass (grid_Bass2020_1, frame 0:04:51):
  2x Sawtooth (1:1) + Sine con Skew/Fold (1:2 = suboctava)
  mixer: saw1 -21.8 dB, saw2 -46.5 dB, sine -5.9 dB (el sine DOMINA)
  filtro Sallen-Key LP 3er orden @ 125 Hz (keytrack), Q limit +4.8 dB
  patron: offbeat "um-pa" (kick en el beat, bajo en los 16avos restantes)

Salida: Desktop/KDD_kick.wav, KDD_bass.wav, KDD_kickbass_161_demo.wav
"""
import numpy as np
from scipy.io import wavfile
from scipy.signal import lfilter
import os

SR = 44100
DESK = os.path.join(os.path.expanduser("~"), "Desktop")


def _db(x):
    return 10 ** (x / 20)


# ---------------- KICK ----------------
def kdd_kick(dur=0.35, base_mult=1.0):
    """Pitch-sweep exacto de DDKick. base_mult escala la base (1.0 = receta)."""
    n = int(SR * dur)
    t = np.arange(n) / SR
    # puntos (tiempo_s, freq_hz)
    pts_t = np.array([0.0, 0.00425, 0.0245, 0.14525, 0.150, 0.160])
    pts_f = np.array([8265.1, 1690.6, 227.3, 44.9, 20.0, 20.0]) * base_mult
    curvas = [0.0, -0.820, -1.165, 0.0, 0.0]   # curvatura por segmento

    logf = np.zeros(n)
    for i in range(len(pts_t) - 1):
        m = (t >= pts_t[i]) & (t < pts_t[i + 1])
        if not m.any():
            continue
        x = (t[m] - pts_t[i]) / (pts_t[i + 1] - pts_t[i])
        c = curvas[i]
        if abs(c) > 1e-6:               # curva exponencial estilo DDKick
            x = (1 - np.exp(c * 4 * x)) / (1 - np.exp(c * 4))
        logf[m] = np.log(pts_f[i]) + x * (np.log(pts_f[i + 1]) - np.log(pts_f[i]))
    logf[t >= pts_t[-1]] = np.log(pts_f[-1])
    freq = np.exp(logf)

    phase = 2 * np.pi * np.cumsum(freq) / SR
    x = np.sin(phase)

    # amp: ataque instantaneo, cuerpo ~160ms, cola corta
    amp = np.ones(n)
    amp *= np.exp(-t * 6.5)
    fade = int(0.02 * SR)
    amp[-fade:] *= np.linspace(1, 0, fade)
    x *= amp

    # clipper suave (AmpFX de DDKick) + normalizar
    x = np.tanh(x * 1.8) / np.tanh(1.8)
    return (x / np.abs(x).max() * 0.95).astype(np.float32)


# ---------------- BASS ----------------
def _saw(f, n, detune=1.0):
    t = np.arange(n) / SR
    ph = (t * f * detune) % 1.0
    return 2 * ph - 1


def _sine_fold(f, n, skew=0.35, fold=1.6):
    """Sine con skew (asimetria de fase) + wavefold suave, una octava abajo."""
    t = np.arange(n) / SR
    ph = (t * f) % 1.0
    ph = ph ** (1 + skew)                    # skew
    s = np.sin(2 * np.pi * ph)
    return np.sin(s * fold * np.pi / 2)      # fold


def _lp3(x, cutoff, q_db=4.8):
    """Sallen-Key LP 3er orden aprox: 3 one-poles + realce de resonancia."""
    w = np.exp(-2 * np.pi * cutoff / SR)
    b, a = [1 - w], [1, -w]
    y = x
    for _ in range(3):
        y = lfilter(b, a, y)
    # resonancia: banda estrecha alrededor del cutoff sumada
    bw = cutoff * 0.3
    w0 = 2 * np.pi * cutoff / SR
    r = 1 - (2 * np.pi * bw / SR) / 2
    a_bp = [1, -2 * r * np.cos(w0), r * r]
    b_bp = [(1 - r * r) / 2, 0, -(1 - r * r) / 2]
    y = y + lfilter(b_bp, a_bp, y) * (_db(q_db) - 1) * 0.5
    return y


def kdd_bass_note(f, dur=0.11):
    """Una nota del bajo grid_Bass2020. f = frecuencia de la nota (saws)."""
    n = int(SR * dur)
    saw1 = _saw(f, n, 1.0) * _db(-21.8)
    saw2 = _saw(f, n, 1.007) * _db(-46.5)
    sine = _sine_fold(f / 2, n) * _db(-5.9)          # 1:2 = suboctava, domina
    x = saw1 + saw2 + sine
    x = _lp3(x, max(125.0, f * 2.2))                  # keytrack aprox
    # AD: ataque 2ms, release al final (mata clicks como KDD con el env)
    a = int(0.002 * SR)
    r = int(0.02 * SR)
    env = np.ones(n)
    env[:a] = np.linspace(0, 1, a)
    env[-r:] *= np.linspace(1, 0, r)
    x *= env
    return (x / (np.abs(x).max() + 1e-9) * 0.9).astype(np.float32)


# ---------------- DEMO 161 BPM ----------------
def demo(bars=8, bpm=161.0, note_hz=43.65):    # F1, la nota de test de KDD
    beat = 60.0 / bpm
    step = beat / 4                             # 16avos
    total = int(SR * beat * 4 * bars) + SR
    out = np.zeros(total, dtype=np.float64)
    kick = kdd_kick().astype(np.float64)
    bass = kdd_bass_note(note_hz, dur=step * 0.92).astype(np.float64) * 0.85

    pos = 0.0
    for bar in range(bars):
        for b in range(4):
            t0 = (bar * 4 + b) * beat
            i = int(t0 * SR)
            out[i:i + len(kick)] += kick                     # kick en el beat
            for s in (1, 2, 3):                              # bajo en 2-3-4 (um-pa-pa-pa)
                j = int((t0 + s * step) * SR)
                out[j:j + len(bass)] += bass
    out = np.tanh(out * 1.1)                                 # glue clipper suave
    return (out / np.abs(out).max() * 0.95).astype(np.float32)


def save(name, mono):
    stereo = np.stack([mono, mono], axis=1)
    path = os.path.join(DESK, name)
    wavfile.write(path, SR, stereo)
    print(f"  -> {path}  ({len(mono)/SR:.2f}s)")


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print("KDD kick (receta exacta DDKick):")
    save("KDD_kick.wav", kdd_kick())
    print("KDD bass (grid_Bass2020, nota F1):")
    save("KDD_bass.wav", np.tile(kdd_bass_note(43.65, 0.5), 2))
    print("Demo kick+bass um-pa @ 161 BPM:")
    save("KDD_kickbass_161_demo.wav", demo())
    print("listo.")
