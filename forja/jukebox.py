# -*- coding: utf-8 -*-
"""
JUKEBOX — seamless infinite extension of a track (Eternal-Jukebox-style).

Decomposes a track into beats, builds a beat-similarity graph, and walks it to
any target length: at beats whose *next* beat sounds like some other beat, it can
JUMP there. Every sample is the original audio, so the result is indistinguishable
from the source — it just never ends and never repeats the same way.

CORE of the whole vision (extend 1 track -> fuse N -> 2h live). Exposes functions
so the backend can build ONE shared path from the mix and stitch every stem with
it (keeping all stems perfectly in sync).

Standalone:  python forja/jukebox.py [input.wav] [target_seconds]
"""
import os, sys
import numpy as np
import librosa
from scipy.io import wavfile
from scipy.spatial.distance import cdist

SR = 44100


def _to_stereo_float(raw, sr):
    if raw.dtype == np.int16:
        raw = raw.astype(np.float64) / 32768.0
    elif raw.dtype == np.int32:
        raw = raw.astype(np.float64) / 2147483648.0
    else:
        raw = raw.astype(np.float64)
    if raw.ndim == 1:
        raw = np.column_stack([raw, raw])
    if sr != SR:
        raw = np.column_stack([
            librosa.resample(raw[:, 0].astype(np.float32), orig_sr=sr, target_sr=SR),
            librosa.resample(raw[:, 1].astype(np.float32), orig_sr=sr, target_sr=SR),
        ]).astype(np.float64)
    return raw


def analyze(ymono):
    """Beat grid + per-beat feature vectors (timbre+pitch+loudness, z-normed)."""
    _, beats = librosa.beat.beat_track(y=ymono, sr=SR, start_bpm=145, units="frames")
    beat_samp = librosa.frames_to_samples(beats).tolist()
    if not beat_samp or beat_samp[0] > 0:
        beat_samp = [0] + beat_samp
    if beat_samp[-1] < len(ymono):
        beat_samp.append(len(ymono))
    B = len(beat_samp) - 1
    chroma = librosa.feature.chroma_cqt(y=ymono, sr=SR)
    mfcc = librosa.feature.mfcc(y=ymono, sr=SR, n_mfcc=13)
    rms = librosa.feature.rms(y=ymono)
    feats = []
    for k in range(B):
        f0 = librosa.samples_to_frames(beat_samp[k])
        f1 = max(f0 + 1, librosa.samples_to_frames(beat_samp[k + 1]))
        feats.append(np.concatenate([
            chroma[:, f0:f1].mean(axis=1), mfcc[:, f0:f1].mean(axis=1), rms[:, f0:f1].mean(axis=1)]))
    F = np.array(feats)
    F = (F - F.mean(axis=0)) / (F.std(axis=0) + 1e-9)
    return beat_samp, F


def jump_edges(F, pct=8.0):
    """edge i->j : after beat i, jump to j (good if j sounds like beat i+1)."""
    B = len(F)
    D = cdist(F, F)
    thr = np.percentile(D[D > 0], pct)
    edges = {}
    for i in range(B - 1):
        cand = [(D[i + 1, j], j) for j in range(B) if abs(j - (i + 1)) >= 4 and D[i + 1, j] < thr]
        cand.sort()
        if cand:
            edges[i] = [j for _, j in cand[:6]]
    return edges


def make_path(beat_samp, edges, target_sec, seed=7, jump_prob=0.22):
    """Walk the graph to target_sec. Returns (path beat indices, jumps flags)."""
    rng = np.random.RandomState(seed)
    B = len(beat_samp) - 1
    bdur = [(beat_samp[k + 1] - beat_samp[k]) / SR for k in range(B)]
    path, jumps = [0], [False]
    cur, dur, guard = 0, 0.0, 0
    while dur < target_sec and guard < 500000:
        guard += 1
        dur += bdur[cur]
        cands = edges.get(cur)
        near_end = cur >= B - 2
        if cands and (near_end or rng.random() < jump_prob):
            nxt, vj = int(rng.choice(cands)), True
        elif near_end:
            nxt, vj = (int(rng.choice(list(edges.keys()))), True) if edges else (0, True)
        else:
            nxt, vj = cur + 1, False
        path.append(nxt); jumps.append(vj); cur = nxt
    return path, jumps


def stitch(stereo, beat_samp, path, jumps, xfade_ms=18):
    """Rebuild audio following `path`, crossfading at jumps to hide seams."""
    xf = int(xfade_ms / 1000 * SR)
    fin = np.sqrt(np.linspace(0, 1, xf))[:, None]
    fout = np.sqrt(np.linspace(1, 0, xf))[:, None]
    chunks = []
    for idx, k in enumerate(path):
        seg = stereo[beat_samp[k]:beat_samp[k + 1]].copy()
        if idx > 0 and jumps[idx] and len(seg) > xf and chunks and len(chunks[-1]) > xf:
            prev = chunks[-1]
            head = seg[:xf] * fin + prev[-xf:] * fout
            chunks[-1] = prev[:-xf]
            seg = np.vstack([head, seg[xf:]])
        chunks.append(seg)
    out = np.vstack(chunks)
    pk = np.max(np.abs(out)) + 1e-9
    return np.clip(out / pk * 0.97, -1, 1)


def extend_file(in_path, target_sec):
    sr, raw = wavfile.read(in_path)
    stereo = _to_stereo_float(raw, sr)
    ymono = stereo.mean(axis=1).astype(np.float32)
    beat_samp, F = analyze(ymono)
    edges = jump_edges(F)
    if not edges:
        return stereo, {"beats": len(beat_samp) - 1, "jumps": 0, "note": "sin saltos"}
    path, jumps = make_path(beat_samp, edges, target_sec)
    out = stitch(stereo, beat_samp, path, jumps)
    return out, {"beats": len(beat_samp) - 1, "edges": len(edges),
                 "pathBeats": len(path), "jumps": int(sum(jumps)), "outSec": len(out) / SR}


if __name__ == "__main__":
    REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    IN = sys.argv[1] if len(sys.argv) > 1 else os.path.join(REPO, "forja", "recreation_out", "phase0", "00_clip.wav")
    TARGET = float(sys.argv[2]) if len(sys.argv) > 2 else 150.0
    OUT_DIR = os.path.join(REPO, "forja", "recreation_out", "jukebox")
    os.makedirs(OUT_DIR, exist_ok=True)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(f"JUKEBOX  in={os.path.basename(IN)}  target={TARGET:.0f}s")
    out, info = extend_file(IN, TARGET)
    print(" ", info)
    op = os.path.join(OUT_DIR, "extended.wav")
    wavfile.write(op, SR, (out * 32767).astype(np.int16))
    print(f"  -> {op}")
