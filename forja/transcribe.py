# -*- coding: utf-8 -*-
"""
TRANSCRIBE — turn YouTube videos (interviews/tutorials/masterclasses) into text
to learn from.

Captions-first (instant, no download): pulls auto/manual subtitles via yt-dlp and
cleans them to plain text. Falls back to audio + Whisper only if a video has no
captions (requires: pip install faster-whisper + ffmpeg).

PRIVATE learning use. Public videos only — don't transcribe pirated paid courses.

  python forja/transcribe.py <url> [<url> ...]
  python forja/transcribe.py --file urls.txt
Outputs to forja/research_transcripts/<id>.txt
"""
import os, sys, glob, re, subprocess, tempfile, shutil

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "forja", "research_transcripts")
os.makedirs(OUT, exist_ok=True)
PY = sys.executable

def urls_from_args():
    a = sys.argv[1:]
    if not a:
        print(__doc__); sys.exit(0)
    if a[0] == "--file":
        with open(a[1], encoding="utf-8") as f:
            return [l.strip() for l in f if l.strip() and not l.startswith("#")]
    return a

def clean_vtt(path):
    lines = open(path, encoding="utf-8", errors="ignore").read().splitlines()
    out, seen = [], None
    for ln in lines:
        if "-->" in ln or ln.strip().upper().startswith("WEBVTT") or re.match(r"^\d+$", ln.strip()):
            continue
        if ln.startswith(("Kind:", "Language:", "NOTE")):
            continue
        t = re.sub(r"<[^>]+>", "", ln).strip()          # strip <c>/<timestamp> tags
        t = re.sub(r"\[.*?\]", "", t).strip()
        if t and t != seen:                              # dedupe consecutive (auto-caption rolling)
            out.append(t); seen = t
    return " ".join(out)

def get_captions(url, work):
    subprocess.run([PY, "-m", "yt_dlp", "--write-auto-subs", "--write-subs",
                    "--sub-langs", "en.*,ru.*,es.*", "--skip-download", "--sub-format", "vtt",
                    "-o", os.path.join(work, "%(id)s.%(ext)s"), url],
                   check=False, capture_output=True, text=True)
    vtts = glob.glob(os.path.join(work, "*.vtt"))
    # prefer manual over auto, en/es over ru
    def rank(p):
        n = os.path.basename(p).lower()
        return (("auto" in n), not any(f".{l}." in n for l in ("en", "es")))
    vtts.sort(key=rank)
    return clean_vtt(vtts[0]) if vtts else None

def title_of(url, work):
    r = subprocess.run([PY, "-m", "yt_dlp", "--print", "%(id)s|%(title)s", "--skip-download", url],
                       capture_output=True, text=True)
    line = (r.stdout or "").strip().splitlines()[-1] if r.stdout.strip() else "|"
    vid, _, title = line.partition("|")
    return vid.strip() or "video", title.strip()

WHISPER_SIZE = os.environ.get("WHISPER_SIZE", "small")
_MODEL = None
def _get_model():
    global _MODEL
    if _MODEL is None:
        from faster_whisper import WhisperModel
        print(f"  cargando Whisper '{WHISPER_SIZE}' (CPU int8, 1ra vez baja el modelo)...")
        _MODEL = WhisperModel(WHISPER_SIZE, device="cpu", compute_type="int8")
    return _MODEL

def whisper_fallback(url, work):
    try:
        import faster_whisper  # noqa: F401
    except Exception:
        return None  # not installed
    # audio-only, NO conversion (no ffmpeg needed; faster-whisper/PyAV decodes it)
    subprocess.run([PY, "-m", "yt_dlp", "-f", "bestaudio", "--no-playlist",
                    "-o", os.path.join(work, "a.%(ext)s"), url], check=False, capture_output=True)
    auds = glob.glob(os.path.join(work, "a.*"))
    if not auds:
        return None
    try:
        model = _get_model()
        # task="translate" -> always English (handles Russian interviews too)
        segs, _info = model.transcribe(auds[0], task="translate", vad_filter=True)
        return " ".join(s.text.strip() for s in segs)
    except Exception as e:
        print("  whisper error:", e)
        return None

def main():
    for url in urls_from_args():
        work = tempfile.mkdtemp(prefix="tx_")
        try:
            vid, title = title_of(url, work)
            print(f"\n[{vid}] {title}")
            text = get_captions(url, work)
            how = "captions"
            if not text or len(text) < 80:
                print("  sin captions -> probando Whisper...")
                text = whisper_fallback(url, work); how = "whisper"
            if not text:
                print("  no pude transcribir (sin captions y Whisper/ffmpeg no disponible)")
                continue
            safe = re.sub(r"[^\w\-]", "_", title)[:50] or vid
            p = os.path.join(OUT, f"{vid}_{safe}.txt")
            with open(p, "w", encoding="utf-8") as f:
                f.write(f"# {title}\n# {url}\n# fuente: {how}\n\n{text}\n")
            print(f"  -> {p}  ({len(text)} chars, {how})")
        finally:
            shutil.rmtree(work, ignore_errors=True)

if __name__ == "__main__":
    main()
