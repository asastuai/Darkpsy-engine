# -*- coding: utf-8 -*-
"""
KDD-FRAMES — extrae frames del video del curso (PyAV, sin ffmpeg CLI) para
leer visualmente settings de plugins, EQs, arreglo del DAW, etc.

Modos:
  python forja/kdd_frames.py grid [paso_seg]      # 1 frame cada N seg (default 20)
  python forja/kdd_frames.py at t1 t2 t3 ...      # frames en segundos puntuales (full-res)

grid  -> samples/kdd_course/frames/f_HH-MM-SS.jpg (reescalado a 1280px ancho)
at    -> samples/kdd_course/frames_hi/f_HH-MM-SS.png (resolucion completa)
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COURSE = os.path.join(REPO, "samples", "kdd_course")


def find_video():
    for f in os.listdir(COURSE):
        if f.startswith("kdd_video."):
            return os.path.join(COURSE, f)
    raise SystemExit("no hay kdd_video.* en samples/kdd_course")


def hms(t):
    h, r = divmod(int(t), 3600)
    m, s = divmod(r, 60)
    return f"{h:d}-{m:02d}-{s:02d}"


def extract(times, outdir, width=None, fmt="jpg"):
    import av
    os.makedirs(outdir, exist_ok=True)
    path = find_video()
    n = 0
    with av.open(path) as c:
        stream = c.streams.video[0]
        tb = stream.time_base
        for t in times:
            c.seek(int(t / tb), stream=stream)
            for frame in c.decode(stream):
                if frame.time is None or frame.time < t - 0.5:
                    continue
                img = frame.to_image()
                if width and img.width > width:
                    img = img.resize((width, int(img.height * width / img.width)))
                out = os.path.join(outdir, f"f_{hms(frame.time)}.{fmt}")
                img.save(out, quality=88)
                n += 1
                if n % 50 == 0:
                    print(f"  {n} frames... ({hms(frame.time)})", flush=True)
                break
    print(f"listo: {n} frames -> {outdir}")


def main():
    a = sys.argv[1:]
    mode = a[0] if a else "grid"
    if mode == "grid":
        step = float(a[1]) if len(a) > 1 else 20.0
        import av
        with av.open(find_video()) as c:
            dur = float(c.duration / av.time_base)
        times = [t for t in _frange(1.0, dur, step)]
        print(f"video: {hms(dur)} -> {len(times)} frames cada {step}s")
        extract(times, os.path.join(COURSE, "frames"), width=1280, fmt="jpg")
    elif mode == "at":
        times = [float(x) for x in a[1:]]
        extract(times, os.path.join(COURSE, "frames_hi"), width=None, fmt="png")
    else:
        print(__doc__)


def _frange(start, stop, step):
    t = start
    while t < stop:
        yield t
        t += step


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
