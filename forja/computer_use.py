# -*- coding: utf-8 -*-
"""
COMPUTER-USE — harness para que Claude OPERE la GUI: captura de pantalla + mouse
+ teclado. Sin dependencias nuevas (ctypes nativo + PIL ya instalado).

El bucle: Claude saca un screenshot -> lo ve -> calcula el target -> mueve/clickea
-> vuelve a capturar para verificar. Para valores finos en knobs, el método
PRECISO es doble-clic + escribir el número (setknob), no arrastrar a ojo.

Uso:
  python computer_use.py shot [out.png] [x y w h]    # captura (todo o una región)
  python computer_use.py pos                          # posición del mouse
  python computer_use.py move X Y
  python computer_use.py click X Y [left|right]
  python computer_use.py dblclick X Y
  python computer_use.py drag X1 Y1 X2 Y2             # arrastre (knobs: vertical = valor)
  python computer_use.py scroll AMT                   # rueda (muchos knobs responden)
  python computer_use.py type "texto"
  python computer_use.py key enter|esc|tab|up|down|...
  python computer_use.py setknob X Y VALOR           # dblclick -> escribe VALOR -> Enter (preciso)
"""
import ctypes
import sys
import time

user32 = ctypes.windll.user32
try:
    user32.SetProcessDPIAware()   # coords físicas reales en pantallas con escalado
except Exception:
    pass

# ---- mouse (mouse_event) ----
_LD, _LU, _RD, _RU, _WHEEL = 0x0002, 0x0004, 0x0008, 0x0010, 0x0800


def move(x, y):
    user32.SetCursorPos(int(x), int(y))


def pos():
    p = ctypes.wintypes.POINT() if hasattr(ctypes, "wintypes") else None
    pt = _POINT()
    user32.GetCursorPos(ctypes.byref(pt))
    return (pt.x, pt.y)


class _POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


def click(x, y, button="left"):
    move(x, y)
    time.sleep(0.03)
    d, u = (_LD, _LU) if button == "left" else (_RD, _RU)
    user32.mouse_event(d, 0, 0, 0, 0)
    time.sleep(0.02)
    user32.mouse_event(u, 0, 0, 0, 0)


def dblclick(x, y):
    click(x, y)
    time.sleep(0.05)
    click(x, y)


def drag(x1, y1, x2, y2, steps=24):
    move(x1, y1)
    time.sleep(0.03)
    user32.mouse_event(_LD, 0, 0, 0, 0)
    time.sleep(0.02)
    for i in range(1, steps + 1):
        move(x1 + (x2 - x1) * i / steps, y1 + (y2 - y1) * i / steps)
        time.sleep(0.008)
    time.sleep(0.02)
    user32.mouse_event(_LU, 0, 0, 0, 0)


def scroll(amount):
    user32.mouse_event(_WHEEL, 0, 0, int(amount) * 120, 0)


# ---- teclado ----
_VK = {"enter": 0x0D, "return": 0x0D, "esc": 0x1B, "escape": 0x1B, "tab": 0x09,
       "up": 0x26, "down": 0x28, "left": 0x25, "right": 0x27, "backspace": 0x08,
       "delete": 0x2E, "home": 0x24, "end": 0x23, "space": 0x20}


def key(name):
    vk = _VK.get(name.lower())
    if vk is None:
        return
    user32.keybd_event(vk, 0, 0, 0)
    time.sleep(0.02)
    user32.keybd_event(vk, 0, 2, 0)


# SendInput unicode para escribir texto arbitrario
PUL = ctypes.POINTER(ctypes.c_ulong)


class _KBD(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort), ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong), ("time", ctypes.c_ulong), ("dwExtraInfo", PUL)]


class _II(ctypes.Union):
    _fields_ = [("ki", _KBD)]


class _INPUT(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong), ("ii", _II)]


def _unichar(ch):
    KEYEVENTF_UNICODE, KEYEVENTF_KEYUP = 0x0004, 0x0002
    for up in (0, KEYEVENTF_KEYUP):
        inp = _INPUT(type=1, ii=_II(ki=_KBD(0, ord(ch), KEYEVENTF_UNICODE | up, 0, None)))
        user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))
        time.sleep(0.005)


def type_text(text):
    for ch in text:
        _unichar(ch)


def setknob(x, y, value):
    """El método PRECISO para un knob: doble-clic abre el campo de valor, se
    selecciona todo, se escribe el número y Enter. (Vital y muchos plugins.)"""
    dblclick(x, y)
    time.sleep(0.12)
    key("home")
    # seleccionar todo y reemplazar
    user32.keybd_event(0x11, 0, 0, 0)  # Ctrl down
    user32.keybd_event(0x41, 0, 0, 0)  # A
    user32.keybd_event(0x41, 0, 2, 0)
    user32.keybd_event(0x11, 0, 2, 0)  # Ctrl up
    time.sleep(0.04)
    type_text(str(value))
    time.sleep(0.04)
    key("enter")


def shot(out="C:\\Users\\Juan\\Desktop\\_cu_shot.png", region=None):
    from PIL import ImageGrab
    img = ImageGrab.grab(bbox=region)  # region=(x,y,x2,y2) o None=todo
    img.save(out)
    return out, img.size


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        sys.exit(0)
    cmd = a[0]
    if cmd == "shot":
        out = a[1] if len(a) > 1 and not a[1].isdigit() else "C:\\Users\\Juan\\Desktop\\_cu_shot.png"
        region = None
        nums = [int(x) for x in a if x.lstrip("-").isdigit()]
        if len(nums) == 4:
            region = (nums[0], nums[1], nums[0] + nums[2], nums[1] + nums[3])
        p, size = shot(out, region)
        print(f"captura: {p} {size}")
    elif cmd == "pos":
        print(pos())
    elif cmd == "move":
        move(int(a[1]), int(a[2])); print("mouse:", pos())
    elif cmd == "click":
        click(int(a[1]), int(a[2]), a[3] if len(a) > 3 else "left"); print("click en", a[1], a[2])
    elif cmd == "dblclick":
        dblclick(int(a[1]), int(a[2])); print("dblclick en", a[1], a[2])
    elif cmd == "drag":
        drag(int(a[1]), int(a[2]), int(a[3]), int(a[4])); print("drag", a[1:5])
    elif cmd == "scroll":
        scroll(int(a[1])); print("scroll", a[1])
    elif cmd == "type":
        type_text(a[1]); print("typed:", a[1])
    elif cmd == "key":
        key(a[1]); print("key:", a[1])
    elif cmd == "setknob":
        setknob(int(a[1]), int(a[2]), a[3]); print(f"setknob ({a[1]},{a[2]}) = {a[3]}")
    else:
        print("comando desconocido:", cmd)
