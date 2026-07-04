# -*- coding: utf-8 -*-
"""Trae una ventana al frente por substring del titulo. Uso: python focus_window.py "Bitwig Studio -" """
import ctypes
import sys
import time

u = ctypes.windll.user32
u.SetProcessDPIAware()


def focus(sub):
    hits = []

    @ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
    def cb(h, l):
        n = u.GetWindowTextLengthW(h)
        if n:
            b = ctypes.create_unicode_buffer(n + 1)
            u.GetWindowTextW(h, b, n + 1)
            if sub.lower() in b.value.lower():
                hits.append((h, b.value))
        return True

    u.EnumWindows(cb, 0)
    if hits:
        h, t = hits[0]
        u.ShowWindow(h, 9)
        u.SetForegroundWindow(h)
        time.sleep(0.3)
        return t
    return None


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    t = focus(sys.argv[1] if len(sys.argv) > 1 else "Bitwig Studio -")
    print(f"foco: {t}" if t else "no encontrada")
