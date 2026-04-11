"""
Surge XT Presets for Dark Psytrance
Uses raw_value (0.0-1.0) for numeric params, strings for enum params.
"""

def _set_raw(surge, param_name, raw_value):
    """Set a parameter by raw_value (0.0 to 1.0)"""
    if param_name in surge.parameters:
        surge.parameters[param_name].raw_value = raw_value


def configure_bass(surge):
    """Warm deep bass: round, fat, musical — Pink Floyd warmth meets dark psy"""
    surge.a_osc_1_type = 'Classic'
    _set_raw(surge, 'a_osc_1_octave', 0.333)  # -1 octave
    _set_raw(surge, 'a_osc_1_shape', 0.4)  # rounder, less harsh
    surge.a_osc_1_unison_voices = '1 voice'  # clean, no detune
    _set_raw(surge, 'a_osc_1_sub_mix', 0.6)  # MORE sub = warmth

    # LP 12dB — gentler slope, warmer
    surge.a_filter_1_type = 'LP 12 dB'
    _set_raw(surge, 'a_filter_1_cutoff', 0.30)  # lets warmth through
    _set_raw(surge, 'a_filter_1_resonance', 0.05)  # almost none = smooth
    _set_raw(surge, 'a_filter_1_feg_mod_amount', 0.25)  # subtle sweep

    _set_raw(surge, 'a_filter_eg_attack', 0.02)
    _set_raw(surge, 'a_filter_eg_decay', 0.30)
    _set_raw(surge, 'a_filter_eg_sustain', 0.20)
    _set_raw(surge, 'a_filter_eg_release', 0.10)

    _set_raw(surge, 'a_amp_eg_attack', 0.02)  # slight softness
    _set_raw(surge, 'a_amp_eg_decay', 0.40)
    _set_raw(surge, 'a_amp_eg_sustain', 0.6)  # fuller sustain
    _set_raw(surge, 'a_amp_eg_release', 0.08)

    surge.a_play_mode = 'Mono'
    _set_raw(surge, 'a_pre_filter_gain', 0.52)  # less drive = cleaner

    try: surge.fx_a1_fx_type = 'Off'  # no distortion, keep it warm
    except: pass

    return surge


def configure_lead(surge):
    """Ethereal supersaw lead — one octave lower, gentler"""
    surge.a_osc_1_type = 'Modern'
    _set_raw(surge, 'a_osc_1_octave', 0.333)  # -1 octave — sit below, not above
    surge.a_osc_1_unison_voices = '5 voices'
    surge.a_osc_1_unison_detune = '12.00 cents'  # tighter detune

    surge.a_filter_1_type = 'LP 12 dB'  # LP instead of BP — warmer
    _set_raw(surge, 'a_filter_1_cutoff', 0.40)  # lower cutoff — less bright
    _set_raw(surge, 'a_filter_1_resonance', 0.1)  # less resonance

    _set_raw(surge, 'a_amp_eg_attack', 0.25)  # slower attack — fades in
    _set_raw(surge, 'a_amp_eg_decay', 0.45)
    _set_raw(surge, 'a_amp_eg_sustain', 0.55)  # lower sustain — sits back
    _set_raw(surge, 'a_amp_eg_release', 0.40)

    try: surge.fx_a1_fx_type = 'Reverb 2'
    except: pass

    surge.a_play_mode = 'Poly'
    return surge


def configure_acid(surge):
    """Acid 303-style: saw, resonant LP, fast env"""
    surge.a_osc_1_type = 'Classic'
    _set_raw(surge, 'a_osc_1_octave', 0.5)
    _set_raw(surge, 'a_osc_1_shape', 0.9)

    surge.a_filter_1_type = 'LP 24 dB'
    _set_raw(surge, 'a_filter_1_cutoff', 0.2)
    _set_raw(surge, 'a_filter_1_resonance', 0.7)
    _set_raw(surge, 'a_filter_1_feg_mod_amount', 0.85)

    _set_raw(surge, 'a_filter_eg_attack', 0.0)
    _set_raw(surge, 'a_filter_eg_decay', 0.1)
    _set_raw(surge, 'a_filter_eg_sustain', 0.05)
    _set_raw(surge, 'a_filter_eg_release', 0.05)

    _set_raw(surge, 'a_amp_eg_attack', 0.0)
    _set_raw(surge, 'a_amp_eg_decay', 0.2)
    _set_raw(surge, 'a_amp_eg_sustain', 0.3)
    _set_raw(surge, 'a_amp_eg_release', 0.08)

    surge.a_play_mode = 'Mono'
    _set_raw(surge, 'a_pre_filter_gain', 0.7)

    try: surge.fx_a1_fx_type = 'Distortion'
    except: pass

    return surge


def configure_pad(surge):
    """Dark atmospheric pad"""
    surge.a_osc_1_type = 'Sine'
    _set_raw(surge, 'a_osc_1_octave', 0.5)
    surge.a_osc_1_unison_voices = '3 voices'
    surge.a_osc_1_unison_detune = '8.00 cents'

    surge.a_filter_1_type = 'LP 12 dB'
    _set_raw(surge, 'a_filter_1_cutoff', 0.45)
    _set_raw(surge, 'a_filter_1_resonance', 0.1)

    _set_raw(surge, 'a_amp_eg_attack', 0.6)
    _set_raw(surge, 'a_amp_eg_decay', 0.5)
    _set_raw(surge, 'a_amp_eg_sustain', 0.8)
    _set_raw(surge, 'a_amp_eg_release', 0.7)

    surge.a_play_mode = 'Poly'

    try:
        surge.fx_a1_fx_type = 'Chorus'
        surge.fx_a2_fx_type = 'Reverb 2'
    except: pass

    return surge


def configure_fm_texture(surge):
    """Alien FM texture"""
    surge.a_osc_1_type = 'FM3'
    _set_raw(surge, 'a_osc_1_octave', 0.5)

    try:
        surge.a_fm_routing = 'Osc 2 > Osc 1'
        _set_raw(surge, 'a_fm_depth', 0.65)
    except: pass

    surge.a_osc_2_type = 'Sine'
    _set_raw(surge, 'a_osc_2_octave', 0.667)  # +1

    surge.a_filter_1_type = 'BP 12 dB'
    _set_raw(surge, 'a_filter_1_cutoff', 0.5)
    _set_raw(surge, 'a_filter_1_resonance', 0.4)

    _set_raw(surge, 'a_amp_eg_attack', 0.0)
    _set_raw(surge, 'a_amp_eg_decay', 0.15)
    _set_raw(surge, 'a_amp_eg_sustain', 0.2)
    _set_raw(surge, 'a_amp_eg_release', 0.1)

    surge.a_play_mode = 'Poly'

    try: surge.fx_a1_fx_type = 'Delay'
    except: pass

    return surge


def configure_fx_riser(surge):
    """Noise-based FX for risers"""
    surge.a_osc_1_type = 'S&H Noise'
    _set_raw(surge, 'a_osc_1_octave', 0.5)

    surge.a_filter_1_type = 'LP 12 dB'
    _set_raw(surge, 'a_filter_1_cutoff', 0.3)
    _set_raw(surge, 'a_filter_1_resonance', 0.3)
    _set_raw(surge, 'a_filter_1_feg_mod_amount', 0.9)

    _set_raw(surge, 'a_filter_eg_attack', 0.8)
    _set_raw(surge, 'a_filter_eg_decay', 0.3)
    _set_raw(surge, 'a_filter_eg_sustain', 0.9)
    _set_raw(surge, 'a_filter_eg_release', 0.2)

    _set_raw(surge, 'a_amp_eg_attack', 0.5)
    _set_raw(surge, 'a_amp_eg_decay', 0.3)
    _set_raw(surge, 'a_amp_eg_sustain', 0.8)
    _set_raw(surge, 'a_amp_eg_release', 0.3)

    surge.a_play_mode = 'Poly'

    try: surge.fx_a1_fx_type = 'Reverb 2'
    except: pass

    return surge
