# -*- coding: utf-8 -*-
"""
ALS-EXTRACT — radiografía de un proyecto de Ableton Live (.als).

Un .als es XML comprimido con gzip. De ahí extraemos CONOCIMIENTO (números y
patrones), nunca sonidos: tempo, tracks con sus faders/pan/sends, dispositivos
por cadena (EQ, compresores, saturadores y sus parámetros clave), notas MIDI
por clip (el groove real de un pro), envolventes de automatización, y parámetros
de Operator (FM nativo de Ableton) si los hay.

REGLA: los .als de terceros son material PRIVADO de análisis. Nunca se commitean
ni se redistribuyen. La salida JSON tampoco incluye samples ni audio embebido.

Uso:
  python forja/als_extract.py "ruta/al/proyecto.als" [salida.json]
  python forja/als_extract.py "ruta" --summary        # solo resumen en consola
"""
import gzip
import json
import os
import sys
import xml.etree.ElementTree as ET


def load_als(path):
    """Un .als es gzip(XML). Algunos exports viejos vienen sin comprimir."""
    with open(path, "rb") as f:
        raw = f.read()
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    return ET.fromstring(raw)


def _val(el, attr="Value"):
    return el.get(attr) if el is not None else None


def _fval(el, default=None):
    v = _val(el)
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _manual(parent, tag):
    """Ableton guarda el valor de un parámetro en <Tag><Manual Value="..."/></Tag>."""
    el = parent.find(f"./{tag}/Manual")
    return _fval(el)


def extract_tempo(root):
    el = root.find(".//Tempo/Manual")
    return _fval(el)


def extract_mixer(track):
    mx = track.find(".//DeviceChain/Mixer")
    if mx is None:
        return {}
    return {
        "volume": _manual(mx, "Volume"),
        "pan": _manual(mx, "Pan"),
        "sends": [_fval(s.find("./Send/Manual")) for s in mx.findall(".//Sends/TrackSendHolder")],
        "speaker_on": _val(mx.find("./Speaker/Manual")) != "false",
    }


# Dispositivos nativos cuyo nombre de tag nos interesa reportar con parámetros.
INTERESTING_PARAMS = {
    "Eq8": ["Bands"],            # tratado aparte
    "Compressor2": ["Threshold", "Ratio", "Attack", "Release", "Knee", "Model"],
    "GlueCompressor": ["Threshold", "Ratio", "Attack", "Release", "Makeup"],
    "Saturator": ["Drive", "Type", "Output"],
    "Overdrive": ["Drive", "Tone", "DryWet"],
    "FilterEQ3": ["GainLo", "GainMid", "GainHi", "FreqLo", "FreqHi"],
    "AutoFilter": ["Cutoff", "Resonance", "FilterType"],
    "Reverb": ["DecayTime", "PreDelay", "DryWet", "RoomSize"],
    "Delay": ["DryWet", "Feedback"],
    "Limiter": ["Gain", "Ceiling"],
    "MultibandDynamics": [],
    "Gate": ["Threshold", "Attack", "Release"],
}


def extract_eq8(dev):
    bands = []
    for b in dev.findall(".//Bands.0") + [e for e in dev.iter() if e.tag.startswith("Bands.")]:
        pass
    # Eq8 guarda ParameterA/ParameterB por banda; recorremos los hijos directos
    for child in dev:
        if not child.tag.startswith("Bands."):
            continue
        pa = child.find("./ParameterA")
        if pa is None:
            continue
        on = _val(pa.find("./IsOn/Manual"))
        bands.append({
            "band": child.tag,
            "on": on != "false",
            "mode": _fval(pa.find("./Mode/Manual")),
            "freq": _manual(pa, "Freq"),
            "gain": _manual(pa, "Gain"),
            "q": _manual(pa, "Q"),
        })
    return bands


def extract_operator(dev):
    """Operator = FM nativo de Ableton. Oro puro para nuestro motor: ratios,
    niveles y envolventes por oscilador."""
    ops = []
    for child in dev:
        if not child.tag.startswith("Operator."):
            continue
        ops.append({
            "op": child.tag,
            "on": _val(child.find("./IsOn/Manual")) != "false",
            "coarse": _manual(child, "Tune/Coarse") or _fval(child.find("./Tune/Coarse/Manual")),
            "fine": _fval(child.find("./Tune/Fine/Manual")),
            "volume": _manual(child, "Volume"),
            "envelope": {
                "attack": _fval(child.find("./Envelope/AttackTime/Manual")),
                "decay": _fval(child.find("./Envelope/DecayTime/Manual")),
                "sustain": _fval(child.find("./Envelope/SustainLevel/Manual")),
                "release": _fval(child.find("./Envelope/ReleaseTime/Manual")),
            },
            "wave": _val(child.find("./WaveForm/Manual")),
        })
    glob = {
        "algorithm": _fval(dev.find("./GlobalParameters/Algorithm/Manual")),
        "filter_freq": _fval(dev.find("./FilterFreq/Manual")),
    }
    return {"operators": ops, "global": glob}


def extract_devices(track):
    devs = []
    chain = track.find(".//DeviceChain/DeviceChain/Devices")
    if chain is None:
        return devs
    for dev in chain:
        tag = dev.tag
        entry = {"device": tag, "on": _val(dev.find("./On/Manual")) != "false"}
        if tag == "Eq8":
            entry["bands"] = extract_eq8(dev)
        elif tag == "Operator":
            entry["operator"] = extract_operator(dev)
        elif tag in ("PluginDevice", "AuPluginDevice", "Vst3PluginDevice"):
            nm = dev.find(".//PluginDesc//PlugName")
            if nm is None:
                nm = dev.find(".//PluginDesc//Name")
            entry["plugin_name"] = _val(nm) or "?"
            entry["note"] = "preset binario opaco (VST de terceros): solo sabemos QUE esta, no como suena"
        else:
            params = {}
            for p in INTERESTING_PARAMS.get(tag, []):
                v = _manual(dev, p)
                if v is not None:
                    params[p] = v
            if params:
                entry["params"] = params
        devs.append(entry)
    return devs


def extract_midi_clips(track):
    clips = []
    for clip in track.findall(".//MidiClip"):
        notes = []
        for kt in clip.findall(".//KeyTracks/KeyTrack"):
            midi = _fval(kt.find("./MidiKey"), None)
            if midi is None:
                midi = _fval(kt.find("./MidiKey/Manual"))
            for ne in kt.findall(".//Notes/MidiNoteEvent"):
                notes.append({
                    "key": midi,
                    "time": float(ne.get("Time", 0)),
                    "dur": float(ne.get("Duration", 0)),
                    "vel": float(ne.get("Velocity", 100)),
                })
        notes.sort(key=lambda x: x["time"])
        clips.append({
            "name": _val(clip.find("./Name")),
            "start": _fval(clip.find("./CurrentStart")),
            "end": _fval(clip.find("./CurrentEnd")),
            "loop_len": _fval(clip.find("./Loop/LoopEnd")),
            "n_notes": len(notes),
            "notes": notes,
        })
    return clips


def extract_automation(track):
    envs = []
    for env in track.findall(".//AutomationEnvelope"):
        pts = [{"time": float(e.get("Time", 0)), "value": float(e.get("Value", 0))}
               for e in env.findall(".//FloatEvent")]
        if len(pts) > 1:   # 1 punto = valor estático, no es automatización real
            envs.append({"target_id": _val(env.find(".//PointeeId"), "Value"), "points": pts})
    return envs


def extract(path):
    root = load_als(path)
    out = {
        "source": os.path.basename(path),
        "_regla": "material privado de analisis; no commitear ni redistribuir",
        "tempo": extract_tempo(root),
        "tracks": [],
    }
    for kind in ("MidiTrack", "AudioTrack", "ReturnTrack", "GroupTrack"):
        for tr in root.iter(kind):
            name = _val(tr.find(".//Name/EffectiveName")) or _val(tr.find(".//Name/UserName"))
            out["tracks"].append({
                "kind": kind,
                "name": name,
                "mixer": extract_mixer(tr),
                "devices": extract_devices(tr),
                "midi_clips": extract_midi_clips(tr) if kind == "MidiTrack" else [],
                "automation": extract_automation(tr),
            })
    # master
    master = root.find(".//MasterTrack")
    if master is not None:
        out["master"] = {"mixer": extract_mixer(master), "devices": extract_devices(master)}
    return out


def summary(data):
    print(f"  proyecto: {data['source']}   tempo: {data['tempo']} BPM")
    print(f"  tracks: {len(data['tracks'])}")
    for t in data["tracks"]:
        devs = ", ".join(d.get("plugin_name", d["device"]) for d in t["devices"]) or "-"
        nclips = sum(c["n_notes"] for c in t["midi_clips"])
        nauto = len(t["automation"])
        print(f"   [{t['kind'][:5]:5s}] {str(t['name']):24.24s} vol={t['mixer'].get('volume')} "
              f"notas={nclips:4d} autom={nauto:2d}  | {devs}")


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    src = sys.argv[1]
    data = extract(src)
    summary(data)
    if "--summary" not in sys.argv:
        dst = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else \
            os.path.splitext(src)[0] + "_xray.json"
        with open(dst, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=1, ensure_ascii=False)
        print(f"\n  -> {dst}")
