# -*- coding: utf-8 -*-
"""
DarkPsy COOK backend (localhost only).

POST /recreate  (multipart: file=<audio>)  ->  separates the track with Demucs +
analyzes BPM/key, writes per-stem WAVs into mesa/public/recreations/<id>/, and
returns a manifest MESA loads as editable stem modules.

SECURITY: bind to 127.0.0.1 only. Runs Surge/Demucs with filesystem access.
LEGAL: the separated stems are derived from copyrighted audio — kept local,
never committed (mesa/public/recreations is gitignored), never distributed.

Run:  python forja/server.py
"""
import os, sys, uuid, shutil, subprocess, tempfile
import numpy as np
from scipy.io import wavfile

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLIC = os.path.join(REPO, "mesa", "public")
REC_DIR = os.path.join(PUBLIC, "recreations")
os.makedirs(REC_DIR, exist_ok=True)
SR = 44100
MAX_SEC_DEFAULT = 90  # cap excerpt so CPU separation + browser decode stay snappy

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import librosa
import jukebox

app = FastAPI(title="DarkPsy COOK")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"], allow_headers=["*"],
)

# demucs stem -> (display label, default gain, band, neon color, plain tip)
STEM_META = {
    "drums": ("Drums", 0.9, "high", "#00e5ff", "Batería: kick + percusión, separada de tu pista."),
    "bass":  ("Bass",  0.9, "bass", "#ff7a00", "El bajo aislado de tu pista."),
    "other": ("Synths", 0.8, "full", "#ff00bb", "Todos los sintes/leads/pads fusionados (no se pueden separar entre sí)."),
    "vocals": ("Voz",   0.9, "mid", "#b388ff", "Voz / elementos melódicos aislados."),
}
ORDER = ["drums", "bass", "other", "vocals"]


def _read(path):
    sr, d = wavfile.read(path)
    if d.ndim == 1:
        d = np.column_stack([d, d])
    if d.dtype == np.int16:
        d = d.astype(np.float64) / 32768.0
    elif d.dtype == np.int32:
        d = d.astype(np.float64) / 2147483648.0
    return sr, d.astype(np.float64)


def _write16(path, stereo):
    wavfile.write(path, SR, (np.clip(stereo, -1, 1) * 32767).astype(np.int16))


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/recreate")
async def recreate(file: UploadFile = File(...), maxSec: int = Form(MAX_SEC_DEFAULT),
                   targetSec: int = Form(240)):
    rid = uuid.uuid4().hex[:8]
    work = tempfile.mkdtemp(prefix="darkpsy_")
    try:
        # 1) save upload
        raw = os.path.join(work, "input" + os.path.splitext(file.filename or "")[1])
        with open(raw, "wb") as f:
            f.write(await file.read())

        # 2) load (librosa handles mp3/wav/flac via audioread/soundfile), trim, write a clean wav for demucs
        y, _sr = librosa.load(raw, sr=SR, mono=False)
        if y.ndim == 1:
            y = np.vstack([y, y])
        y = y[:, : int(maxSec * SR)]
        clip = os.path.join(work, "clip.wav")
        _write16(clip, y.T)
        dur = y.shape[1] / SR
        print(f"[recreate {rid}] {file.filename} -> {dur:.1f}s")

        # 3) BPM + key
        ymono = y.mean(axis=0).astype(np.float32)
        tempo, _ = librosa.beat.beat_track(y=ymono, sr=SR, start_bpm=145)
        bpm = round(float(np.atleast_1d(tempo)[0]), 1)
        chroma = librosa.feature.chroma_cqt(y=ymono, sr=SR).mean(axis=1)
        pcs = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        root = pcs[int(np.argmax(chroma))]
        print(f"[recreate {rid}] bpm={bpm} root={root}")

        # 4) demucs separation (CLI subprocess — stable)
        print(f"[recreate {rid}] separando con Demucs (CPU)...")
        subprocess.run(
            [sys.executable, "-m", "demucs", "-n", "htdemucs", "-d", "cpu",
             "-o", work, "--filename", "{stem}.wav", clip],
            check=True,
        )
        demux = os.path.join(work, "htdemucs")

        # 4b) build ONE shared jukebox path from the mix so every stem stays in sync
        path = jumps = beat_samp = None
        final_dur = dur
        if targetSec and targetSec > dur + 5:
            try:
                beat_samp, F = jukebox.analyze(ymono)
                edges = jukebox.jump_edges(F)
                if edges:
                    path, jumps = jukebox.make_path(beat_samp, edges, float(targetSec))
                    print(f"[recreate {rid}] jukebox: {len(beat_samp)-1} beats, "
                          f"{sum(jumps)} saltos -> {len(path)} beats")
            except Exception as e:
                print(f"[recreate {rid}] jukebox falló (sin extensión): {e}")
                path = None

        # 5) extend (shared path) + write non-empty stems into mesa/public/recreations/<id>/
        out_dir = os.path.join(REC_DIR, rid)
        os.makedirs(out_dir, exist_ok=True)
        stems = []
        for name in ORDER:
            src = os.path.join(demux, f"{name}.wav")
            if not os.path.exists(src):
                continue
            _, d = _read(src)
            rms = float(np.sqrt(np.mean(d ** 2)) + 1e-12)
            rms_db = 20 * np.log10(rms)
            if rms_db < -45:  # skip silent stems (e.g. vocals in psy)
                print(f"[recreate {rid}] skip {name} ({rms_db:.0f} dB)")
                continue
            if path is not None:
                d = jukebox.stitch(d, beat_samp, path, jumps)
                final_dur = len(d) / SR
            _write16(os.path.join(out_dir, f"{name}.wav"), d)
            label, gain, band, color, tip = STEM_META[name]
            stems.append({
                "name": name, "label": label, "url": f"recreations/{rid}/{name}.wav",
                "defaultGain": gain, "band": band, "color": color, "tip": tip,
                "rmsDb": round(rms_db, 1),
            })

        print(f"[recreate {rid}] listo — {len(stems)} stems, {final_dur:.0f}s")
        return {
            "id": rid, "bpm": bpm, "root": root,
            "durationSec": round(final_dur, 2), "stems": stems,
        }
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    print("DarkPsy COOK backend  ->  http://127.0.0.1:8000  (POST /recreate)")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")
