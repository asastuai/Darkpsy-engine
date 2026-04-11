"""
LIVE CONTROL — OSC controller for Reaper
Sends real-time parameter changes to Reaper while it plays.

Usage: call functions from this module to tweak sounds in real-time.
Reaper must have OSC enabled on port 8000.
"""

from pythonosc import udp_client
import time

# OSC client — connects to Reaper
client = udp_client.SimpleUDPClient("127.0.0.1", 8000)

# Track indices (0-based in Reaper)
TRACKS = {
    'kick': 0,
    'bass': 1,
    'fm': 2,
    'electricity': 3,
    'drums': 4,
    'lead': 5,
    'atmosphere': 6,
    'granular': 7,
    'fx': 8,
}


def play():
    """Start playback"""
    client.send_message("/action/1007", 1)  # Transport: Play
    print(">> PLAY")

def stop():
    """Stop playback"""
    client.send_message("/action/1016", 1)  # Transport: Stop
    print(">> STOP")

def rewind():
    """Go to start"""
    client.send_message("/action/40042", 1)  # Go to start
    print(">> REWIND")


def set_volume(track_name, db):
    """Set track volume in dB (-inf to +12)"""
    idx = TRACKS.get(track_name)
    if idx is None:
        print(f"  Track '{track_name}' not found")
        return
    # Convert dB to 0-1 range (approximate)
    val = max(0, min(1, (db + 60) / 72))
    client.send_message(f"/track/{idx+1}/volume", val)
    print(f"  {track_name} volume: {db} dB")


def set_pan(track_name, pan):
    """Set track pan (-1 left, 0 center, 1 right)"""
    idx = TRACKS.get(track_name)
    if idx is None: return
    val = (pan + 1) / 2  # convert -1..1 to 0..1
    client.send_message(f"/track/{idx+1}/pan", val)
    print(f"  {track_name} pan: {pan}")


def mute(track_name):
    """Mute a track"""
    idx = TRACKS.get(track_name)
    if idx is None: return
    client.send_message(f"/track/{idx+1}/mute", 1)
    print(f"  {track_name} MUTED")


def unmute(track_name):
    """Unmute a track"""
    idx = TRACKS.get(track_name)
    if idx is None: return
    client.send_message(f"/track/{idx+1}/mute", 0)
    print(f"  {track_name} UNMUTED")


def solo(track_name):
    """Solo a track"""
    idx = TRACKS.get(track_name)
    if idx is None: return
    client.send_message(f"/track/{idx+1}/solo", 1)
    print(f"  {track_name} SOLO")


def unsolo(track_name):
    """Unsolo a track"""
    idx = TRACKS.get(track_name)
    if idx is None: return
    client.send_message(f"/track/{idx+1}/solo", 0)
    print(f"  {track_name} unsolo")


def set_fx_param(track_name, fx_idx, param_idx, value):
    """Set an FX parameter on a track.
    fx_idx: 0-based FX index on the track
    param_idx: 0-based parameter index
    value: 0.0 to 1.0
    """
    idx = TRACKS.get(track_name)
    if idx is None: return
    client.send_message(f"/track/{idx+1}/fx/{fx_idx+1}/fxparam/{param_idx+1}/value", float(value))
    print(f"  {track_name} FX{fx_idx} param{param_idx}: {value:.3f}")


def set_send_level(track_name, send_idx, db):
    """Set send level"""
    idx = TRACKS.get(track_name)
    if idx is None: return
    val = max(0, min(1, (db + 60) / 72))
    client.send_message(f"/track/{idx+1}/send/{send_idx+1}/volume", val)


# ============================================================
# HIGH-LEVEL COMMANDS — for conversational use
# ============================================================

def bass_darker():
    """Make bass darker: lower filter cutoff"""
    set_fx_param('bass', 0, 0, 0.3)  # filter down
    set_fx_param('bass', 0, 1, 0.6)  # more drive
    print("  >> Bass: mas oscuro")

def bass_brighter():
    """Make bass brighter: open filter"""
    set_fx_param('bass', 0, 0, 0.7)
    set_fx_param('bass', 0, 1, 0.3)
    print("  >> Bass: mas brillante")

def bass_aggressive():
    """More distortion on bass"""
    set_fx_param('bass', 0, 1, 0.8)  # heavy drive
    set_fx_param('bass', 0, 3, 0.7)  # resonance up
    print("  >> Bass: agresivo")

def lead_ethereal():
    """Make lead more atmospheric"""
    set_fx_param('lead', 0, 0, 0.5)
    set_volume('lead', -6)
    print("  >> Lead: etereo")

def lead_present():
    """Make lead cut through"""
    set_fx_param('lead', 0, 0, 0.8)
    set_volume('lead', -2)
    print("  >> Lead: presente")

def more_chaos():
    """Bring up chaos elements"""
    set_volume('fm', -4)
    set_volume('electricity', -4)
    set_volume('granular', -4)
    print("  >> Mas caos")

def less_chaos():
    """Pull back chaos"""
    set_volume('fm', -15)
    set_volume('electricity', -15)
    set_volume('granular', -15)
    print("  >> Menos caos")

def more_groove():
    """Emphasize groove elements"""
    set_volume('kick', -2)
    set_volume('bass', -3)
    set_volume('drums', -4)
    print("  >> Mas groove")

def strip_down():
    """Just kick and bass"""
    for t in ['fm','electricity','lead','atmosphere','granular','fx']:
        mute(t)
    print("  >> Solo kick + bass")

def full_band():
    """Unmute everything"""
    for t in TRACKS:
        unmute(t)
    print("  >> Todos los elementos")


if __name__ == "__main__":
    print("=" * 50)
    print(" LIVE CONTROL - Dark Psy Tweaker")
    print(" Conectado a Reaper via OSC (127.0.0.1:8000)")
    print("=" * 50)
    print()
    print("Comandos disponibles:")
    print("  play() / stop() / rewind()")
    print("  solo('bass') / mute('kick') / unmute('lead')")
    print("  set_volume('bass', -6)")
    print("  bass_darker() / bass_aggressive()")
    print("  more_chaos() / less_chaos()")
    print("  strip_down() / full_band()")
    print()
    print("Tracks:", list(TRACKS.keys()))
