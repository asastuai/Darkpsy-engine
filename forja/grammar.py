# -*- coding: utf-8 -*-
"""
GRAMMAR — loader for grammar.json, the genre law as data.

Every renderer pulls its constants from here instead of hardcoding them, so the
research docs, the Python bake and (later) the browser engine can never drift
apart. Keys starting with "_" are inline documentation, not parameters.

    from grammar import G, lerp_axis, StyleState
    ratio = lerp_axis("chaos", "fm_ratio", c)
    st = StyleState(chaos=0.8, hitech=0.3); st.tempo_bpm
"""
import json
import os

_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "grammar.json")

with open(_PATH, encoding="utf-8") as _f:
    G = json.load(_f)


def save():
    """Persist G back to grammar.json (used by verify.py --learn-ref)."""
    with open(_PATH, "w", encoding="utf-8") as f:
        json.dump(G, f, indent=2, ensure_ascii=False)
        f.write("\n")


def lerp(a, b, t):
    return a + (b - a) * t


def lerp_axis(axis, param, t):
    """Resolve one axis parameter at position t in [0,1]."""
    node = G["axes"][axis][param]
    return lerp(node["from"], node["to"], min(1.0, max(0.0, t)))


def bass_max_decay_ms(bpm):
    """The verified hitech/darkpsy bass-gate law: 60% of a 16th."""
    return 60000.0 / bpm / 4 * 0.6


class StyleState:
    """A point in the 2D style space; resolves every sub-parameter from it."""

    def __init__(self, chaos=0.0, hitech=0.0):
        self.chaos = min(1.0, max(0.0, chaos))
        self.hitech = min(1.0, max(0.0, hitech))

    # ---- Axis A (chaos) ----
    @property
    def fm_ratio(self):        return lerp_axis("chaos", "fm_ratio", self.chaos)
    @property
    def fm_index_start(self):  return lerp_axis("chaos", "fm_index_start", self.chaos)
    @property
    def fm_index_end(self):    return lerp_axis("chaos", "fm_index_end", self.chaos)
    @property
    def note_decay_rate(self): return lerp_axis("chaos", "note_decay_rate", self.chaos)
    @property
    def stab_notes_per_bar(self):
        return int(round(lerp_axis("chaos", "stab_notes_per_bar", self.chaos)))

    # ---- Axis B (hitech) ----
    @property
    def tempo_bpm(self):       return lerp_axis("hitech", "tempo_bpm", self.hitech)
    @property
    def gating_density(self):  return lerp_axis("hitech", "gating_density", self.hitech)
    @property
    def lp_overdrive(self):    return lerp_axis("hitech", "lp_overdrive", self.hitech)
    @property
    def brightness(self):      return lerp_axis("hitech", "brightness", self.hitech)
    @property
    def reverb_decay_ms(self): return lerp_axis("hitech", "reverb_decay_ms", self.hitech)
    @property
    def fm_index_combo(self):
        w = G["axes"]["hitech"]["fm_index_combo_chaos_weight"]
        return min(1.0, w * self.chaos + self.hitech)

    def __repr__(self):
        return f"StyleState(chaos={self.chaos:.2f}, hitech={self.hitech:.2f})"
