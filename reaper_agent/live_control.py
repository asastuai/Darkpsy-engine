# -*- coding: utf-8 -*-
"""
REAPER AGENT — live control over OSC (standard Reaper OSC addresses).

Lets Claude drive Juan's Reaper in real time: transport, volume, mute/solo, and
high-level "performance" macros — conversationally.

ONE-TIME SETUP in Reaper:
  Options > Preferences > Control/OSC/web > Add > OSC (Open Sound Control)
  Mode: Local port    Receive on port: 8000    Pattern: Default.ReaperOSC
Then open a session (e.g. reaper_agent/DarkPsy_Reaper.RPP).

Track map matches DarkPsy_Reaper.RPP (8 audio-stem tracks, 1-based for OSC).

CLI:  python reaper_agent/live_control.py <command> [args]
  play | stop | demo
  mute <name> | unmute <name> | solo <name> | unsolo <name>
  vol <name> <0..1>
  more_chaos | less_chaos | strip_down | full_band | more_groove
"""
import sys, time
from pythonosc import udp_client

client = udp_client.SimpleUDPClient("127.0.0.1", 8000)

# DarkPsy_Reaper.RPP order (Reaper OSC tracks are 1-based)
TRACKS = {"kick": 1, "bass": 2, "drums": 3, "acid": 4, "lead": 5, "pad": 6, "fm": 7, "fx": 8}

def play():  client.send_message("/play", 1.0);  print(">> PLAY")
def stop():  client.send_message("/stop", 1.0);  print(">> STOP")

def vol(name, v):
    i = TRACKS.get(name)
    if i is None: print(f"  ? track {name}"); return
    client.send_message(f"/track/{i}/volume", float(max(0.0, min(1.0, v))))
    print(f"  {name} vol -> {v:.2f}")

def mute(name, m=1):
    i = TRACKS.get(name)
    if i is None: return
    client.send_message(f"/track/{i}/mute", float(m)); print(f"  {name} {'MUTE' if m else 'unmute'}")

def solo(name, s=1):
    i = TRACKS.get(name)
    if i is None: return
    client.send_message(f"/track/{i}/solo", float(s)); print(f"  {name} {'SOLO' if s else 'unsolo'}")

# ---- performance macros (volume/mute based — work on plain audio tracks) ----
def more_chaos():
    for t in ("fm", "fx", "acid"): vol(t, 0.75)
    print(">> MAS CAOS")
def less_chaos():
    for t in ("fm", "fx"): vol(t, 0.25)
    print(">> menos caos")
def strip_down():
    for t in ("fm", "fx", "lead", "pad", "acid", "drums"): mute(t, 1)
    print(">> SOLO kick + bass")
def full_band():
    for t in TRACKS: mute(t, 0)
    print(">> banda completa")
def more_groove():
    for t in ("kick", "bass", "drums"): vol(t, 0.72)
    print(">> mas groove")

def demo():
    """A short scripted live performance — watch Reaper respond."""
    print("== performance demo ==")
    play(); time.sleep(3)
    print("\n-- solo bass --"); solo("bass", 1); time.sleep(3); solo("bass", 0)
    print("\n-- strip down a kick+bass --"); strip_down(); time.sleep(4)
    print("\n-- vuelve la banda --"); full_band(); time.sleep(2)
    print("\n-- MAS CAOS --"); more_chaos(); time.sleep(4)
    print("\n-- menos caos --"); less_chaos(); time.sleep(3)
    print("\n-- stop --"); stop()

if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        print(__doc__); sys.exit(0)
    cmd = a[0]
    if cmd in ("play", "stop", "demo", "more_chaos", "less_chaos", "strip_down", "full_band", "more_groove"):
        globals()[cmd]()
    elif cmd in ("mute", "unmute", "solo", "unsolo") and len(a) >= 2:
        name = a[1]
        if cmd == "mute": mute(name, 1)
        elif cmd == "unmute": mute(name, 0)
        elif cmd == "solo": solo(name, 1)
        elif cmd == "unsolo": solo(name, 0)
    elif cmd == "vol" and len(a) >= 3:
        vol(a[1], float(a[2]))
    else:
        print(f"  comando desconocido: {a}")
