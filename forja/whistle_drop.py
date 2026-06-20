# -*- coding: utf-8 -*-
"""
WHISTLE-DROP — el momento de Juan: el silbido suena solo (antesala) y en el
segundo 21 entra el beat Y el silbido se DESINTEGRA — distorsión creciente +
granular que lo rompe en pedazos + reverb que se lo lleva. No se corta: se
consume, tragado por el drop.

Uso: python forja/whistle_drop.py [t_drop_seg]  (default 21)
"""
import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cine
from audio_io import load

SR = 44100
WHISTLE = os.path.join(os.path.expanduser("~"), "Desktop", "twisted_nerve.wav")
T_DROP = float(sys.argv[1]) if len(sys.argv) > 1 else 21.0
USE_REAPER = "--synth" not in sys.argv   # default: la base de Reaper de Juan
STEMS = os.path.join(os.path.expanduser("~"), "Desktop", "DarkPsy_techno132_stems")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def reverb_tail(x, decay=0.8, mix=0.4):
    """Reverb barato (convolución con ruido decayente) — el 'yéndose'."""
    n = int(decay * SR)
    ir = np.random.RandomState(3).randn(n) * np.exp(-np.arange(n) / (0.18 * SR))
    wet = np.convolve(x, ir, mode="full")[:len(x) + n]
    wet = wet / (np.max(np.abs(wet)) + 1e-9) * np.max(np.abs(x))
    out = np.zeros(len(wet))
    out[:len(x)] += x * (1 - mix)
    out += wet * mix
    return out


def disintegrate(x, dur=3.4):
    """Distorsión creciente + granular que se rompe + bitcrush + fade. El silbido
    yéndose distorsionado y rompiéndose."""
    n = int(dur * SR)
    src = x[:n] if len(x) >= n else np.pad(x, (0, n - len(x)))
    t = np.arange(n) / SR
    prog = t / dur

    # 1) distorsión que sube
    drive = 1 + 12 * prog
    y = np.tanh(src * drive) / np.tanh(13.0)

    # 2) granular: grains cada vez más cortos, dispersos y con huecos = rompiéndose
    rng = np.random.RandomState(7)
    out = np.zeros(n)
    oc = 0
    while oc < n:
        p = oc / n
        glen = max(int((0.09 - 0.07 * p) * SR), int(0.012 * SR))
        rp = int(rng.uniform(0, max(1, n - glen))) if p > 0.45 else oc  # scatter al final
        w = np.hanning(glen)
        grain = y[rp:rp + glen] * w
        if rng.random() > p * 0.6:                      # los huecos crecen
            e = min(oc + glen, n)
            out[oc:e] += grain[:e - oc]
        oc += glen if rng.random() > p * 0.45 else int(glen * 0.5)  # stutter

    # 3) bitcrush que sube = ruptura digital
    bits = np.clip(14 - 11 * prog, 2, 16)
    lv = 2 ** bits
    out = np.round(out * lv) / lv

    # 4) se lo lleva: reverb + fade
    out *= (1 - prog) ** 1.6
    out = reverb_tail(out, decay=1.0, mix=0.5)
    return out


def reaper_base_beat(nbars):
    """La base que viene haciendo Juan en Reaper: stems techno132 + mezcla del
    amigo (volúmenes + high-pass + drive Kranch en bass), FM y lead MUTEADOS.
    Devuelve el tramo de nbars más energético (para que el drop entre arriba)."""
    from scipy.io import wavfile
    from scipy.signal import butter, sosfilt
    vols = {"kick": 0.478, "bass": 0.508, "drums": 0.145, "acid": 0.962,
            "pad": 1.048, "fx": 0.229}                 # del mix_template del amigo
    hpf = {"acid": 221, "pad": 479, "fx": 891}         # disciplina high-pass
    mix = None
    N = 0
    for name, v in vols.items():
        sr, d = wavfile.read(os.path.join(STEMS, name + ".wav"))
        x = (d.mean(axis=1) if d.ndim > 1 else d).astype(np.float64) / 32768.0
        if name in hpf:
            x = sosfilt(butter(2, hpf[name], btype="high", fs=SR, output="sos"), x)
        if name == "bass":
            x = np.tanh(x * 2.0) / np.tanh(2.0)         # drive tipo Kranch
        if mix is None:
            mix = np.zeros(len(x)); N = len(x)
        n = min(N, len(x)); mix[:n] += x[:n] * v
    barlen = int(cine.BAR * SR); win = nbars * barlen
    best_e, best_s = 0.0, 0
    for s in range(0, max(1, len(mix) - win), barlen * 2):
        e = float(np.sum(mix[s:s + win] ** 2))
        if e > best_e:
            best_e, best_s = e, s
    chunk = mix[best_s:best_s + win].copy()
    r = int(0.004 * SR); chunk[:r] *= np.linspace(0, 1, r)   # anti-click
    print(f"  base Reaper: tramo más energético en {best_s/SR:.0f}s ({nbars} compases)")
    return chunk


def main():
    w, sr = load(WHISTLE)
    wm = w.mean(axis=1)
    print(f"  silbido: {len(wm)/SR:.1f}s; drop en {T_DROP:.0f}s")

    nbeat_bars = 6
    beat_dur = nbeat_bars * cine.BAR
    total = int((T_DROP + beat_dur + 1.5) * SR)
    M = np.zeros(total)

    # 1) silbido solo, la antesala (0 -> T_DROP)
    a = int(T_DROP * SR)
    clean = wm[:a].copy()
    if len(clean) < a:
        clean = np.pad(clean, (0, a - len(clean)))
    # pequeño swell de tensión al final de la antesala
    pre = int(1.5 * SR)
    clean[a - pre:a] *= np.linspace(1.0, 1.25, pre)
    M[:a] += clean * 0.7

    # 2) en T_DROP: impacto + beat + el silbido se desintegra
    cine.add(M, cine.impact(), T_DROP, 0.9)
    if USE_REAPER:
        beatbuf = reaper_base_beat(nbeat_bars)
        beatbuf = beatbuf / (np.max(np.abs(beatbuf)) + 1e-9) * 0.95
    else:
        beatbuf = np.zeros(int(beat_dur * SR) + SR)
        cine.groove(beatbuf, 0, nbeat_bars, level=1.0)
    e = min(a + len(beatbuf), total)
    M[a:e] += beatbuf[:e - a]

    tail = wm[a:a + int(3.4 * SR)]
    if len(tail) < int(3.4 * SR):
        tail = np.pad(tail, (0, int(3.4 * SR) - len(tail)))
    dis = disintegrate(tail)
    e = min(a + len(dis), total)
    M[a:e] += dis[:e - a] * 0.8

    # cierre
    fade = int(0.6 * SR)
    M[-fade:] *= np.linspace(1, 0, fade)
    M = np.tanh(M * 1.1) / np.tanh(1.1)
    pk = np.max(np.abs(M)) + 1e-9
    M = M / pk * 0.97

    from scipy.io import wavfile
    out = np.column_stack([(M * 32767).astype(np.int16), (M * 32767).astype(np.int16)])
    dst = os.path.join(os.path.expanduser("~"), "Desktop", "DarkPsy_whistle_drop.wav")
    wavfile.write(dst, SR, out)
    print(f"  -> {dst}  ({total/SR:.0f}s)")
    print(f"  silbido solo -> [{T_DROP:.0f}s] impacto + beat + el silbido se rompe y se va")


if __name__ == "__main__":
    main()
