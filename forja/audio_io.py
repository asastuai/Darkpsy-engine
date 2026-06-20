# -*- coding: utf-8 -*-
"""
AUDIO-IO — leer/escribir audio de cualquier formato SIN ffmpeg, vía PyAV.

No tenemos ffmpeg CLI en esta máquina, pero PyAV trae las libs de decodificación.
Esto nos deja meter samples en cualquier formato (m4a/webm/mp3/wav/flac/aac) al
pipeline: los samples del set vienen de mil lados, y todos terminan en numpy.

    from audio_io import load, to_wav
    x, sr = load("samples/cine/twisted_nerve.m4a")   # x: float32 (N, 2)
    to_wav("samples/cine/twisted_nerve.wav", x, sr)
"""
import os
import sys
import numpy as np

SR = 44100


def load(path, sr=SR):
    """Decodifica a float32 (N, 2) re-muestreado a `sr` (estéreo)."""
    import av
    container = av.open(path)
    astream = container.streams.audio[0]
    resampler = av.AudioResampler(format="fltp", layout="stereo", rate=sr)
    chunks = []

    def _pull(frame):
        res = resampler.resample(frame)
        if res is None:
            return
        if not isinstance(res, (list, tuple)):
            res = [res]
        for rf in res:
            chunks.append(rf.to_ndarray())   # fltp -> (channels, samples)

    for frame in container.decode(astream):
        _pull(frame)
    _pull(None)   # flush
    container.close()
    if not chunks:
        return np.zeros((0, 2), dtype=np.float32), sr
    data = np.concatenate(chunks, axis=1)     # (2, N)
    return np.ascontiguousarray(data.T.astype(np.float32)), sr


def to_wav(path, x, sr=SR):
    """Escribe WAV int16. x: (N,) o (N, ch) float en [-1, 1] aprox."""
    from scipy.io import wavfile
    x = np.asarray(x, dtype=np.float64)
    if x.ndim == 1:
        x = np.column_stack([x, x])
    pk = np.max(np.abs(x)) + 1e-9
    if pk > 1.0:
        x = x / pk * 0.98
    wavfile.write(path, sr, (np.clip(x, -1, 1) * 32767).astype(np.int16))
    return path


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) < 2:
        print("uso: python forja/audio_io.py <archivo> [salida.wav]")
        raise SystemExit(1)
    src = sys.argv[1]
    x, sr = load(src)
    dur = len(x) / sr
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(src)[0] + ".wav"
    to_wav(out, x, sr)
    print(f"  {os.path.basename(src)}: {dur:.1f}s @ {sr} Hz -> {out}")
