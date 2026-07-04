# -*- coding: utf-8 -*-
"""
KDD-TRANSCRIBE — transcribe el video del curso de KindzaDza localmente
(faster-whisper, todo offline). Genera:
  samples/kdd_course/transcript.json   (segmentos con timestamps, para procesar)
  samples/kdd_course/transcript.md     (legible, timestamps cada segmento)

Uso: python forja/kdd_transcribe.py [modelo]     (default: small)
"""
import json
import os
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COURSE = os.path.join(REPO, "samples", "kdd_course")


def find_audio():
    for f in os.listdir(COURSE):
        if f.startswith("kdd_audio."):
            return os.path.join(COURSE, f)
    raise SystemExit("no hay kdd_audio.* en samples/kdd_course")


def hms(t):
    h, r = divmod(int(t), 3600)
    m, s = divmod(r, 60)
    return f"{h}:{m:02d}:{s:02d}"


def main(model_size="medium", language="ru"):
    from faster_whisper import WhisperModel
    audio = find_audio()
    print(f"audio: {audio}")
    print(f"modelo: {model_size} (int8, CPU), idioma forzado: {language}")
    t0 = time.time()
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    segments, info = model.transcribe(audio, language=language, beam_size=5,
                                      vad_filter=True)
    print(f"idioma detectado: {info.language} (p={info.language_probability:.2f})")
    print(f"duracion: {hms(info.duration)}")

    segs = []
    md = [f"# KDD curso — transcript (idioma: {info.language})\n"]
    for s in segments:
        segs.append({"start": round(s.start, 2), "end": round(s.end, 2),
                     "text": s.text.strip()})
        md.append(f"**[{hms(s.start)}]** {s.text.strip()}")
        # progreso cada ~5 min de audio
        if len(segs) % 100 == 0:
            done = s.end / info.duration * 100
            print(f"  {hms(s.end)} / {hms(info.duration)}  ({done:.0f}%)  "
                  f"[{(time.time()-t0)/60:.1f} min transcurridos]", flush=True)

    with open(os.path.join(COURSE, "transcript.json"), "w", encoding="utf-8") as f:
        json.dump({"language": info.language, "duration": info.duration,
                   "segments": segs}, f, ensure_ascii=False, indent=1)
    with open(os.path.join(COURSE, "transcript.md"), "w", encoding="utf-8") as f:
        f.write("\n\n".join(md))
    print(f"listo: {len(segs)} segmentos en {(time.time()-t0)/60:.1f} min")
    print(f"  -> {COURSE}\\transcript.json / transcript.md")


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main(sys.argv[1] if len(sys.argv) > 1 else "medium",
         sys.argv[2] if len(sys.argv) > 2 else "ru")
