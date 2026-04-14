"""
Surge XT Presets for Dark Psytrance v11
Diseñados con técnicas reales de producción darkpsy.
Referencias: Glosolalia, Kindzadza, Psykovsky, Frantic Noise.

Cada preset tiene su filosofía documentada y parámetros justificados.
"""


def _set_raw(surge, param_name, raw_value):
    """Set a parameter by raw_value (0.0 to 1.0)"""
    if param_name in surge.parameters:
        surge.parameters[param_name].raw_value = raw_value


def _set_safe(surge, attr, value):
    """Set attribute with error handling"""
    try:
        setattr(surge, attr, value)
    except Exception:
        pass


def configure_bass(surge):
    """Rolling bass darkpsy — gomoso, elástico, con movimiento.

    Técnica: Saw → LP resonante con envelope moderado → mono.
    El "gomoso" viene del FEG mod más alto (el filtro se abre y cierra por nota)
    y la resonancia que hace que el filtro "cante" en cada nota.
    KranchDD se aplica después con wet BAJO (0.25) para carácter sin destruir.
    """
    surge.a_osc_1_type = 'Classic'
    _set_raw(surge, 'a_osc_1_octave', 0.333)      # -1 octave (bass range)
    _set_raw(surge, 'a_osc_1_shape', 0.55)         # Saw-ish — más armónicos que 0.4
    surge.a_osc_1_unison_voices = '1 voice'         # Mono, limpio
    _set_raw(surge, 'a_osc_1_sub_mix', 0.45)       # Sub moderado (no tanto como 0.6)

    # LP 12dB — cutoff más abierto, resonancia que canta
    surge.a_filter_1_type = 'LP 12 dB'
    _set_raw(surge, 'a_filter_1_cutoff', 0.48)     # MÁS ABIERTO (antes 0.30 = ahogado)
    _set_raw(surge, 'a_filter_1_resonance', 0.18)  # Resonancia sutil (el filtro "canta")
    _set_raw(surge, 'a_filter_1_feg_mod_amount', 0.45)  # MÁS movimiento por nota (gomoso)
    _set_raw(surge, 'a_filter_1_keytrack', 0.5)    # Sigue la nota = consistente

    # Filter envelope: rápido arriba, decay medio = "plop" elástico por nota
    _set_raw(surge, 'a_filter_eg_attack', 0.01)
    _set_raw(surge, 'a_filter_eg_decay', 0.20)     # Decay medio = bounce
    _set_raw(surge, 'a_filter_eg_sustain', 0.15)
    _set_raw(surge, 'a_filter_eg_release', 0.08)

    # Amp: ataque snappy, release limpio (sin clicks)
    _set_raw(surge, 'a_amp_eg_attack', 0.01)
    _set_raw(surge, 'a_amp_eg_decay', 0.35)
    _set_raw(surge, 'a_amp_eg_sustain', 0.55)
    _set_raw(surge, 'a_amp_eg_release', 0.06)      # Release corto = notas separadas

    surge.a_play_mode = 'Mono'
    _set_raw(surge, 'a_pre_filter_gain', 0.72)     # Drive alto = nivel + carácter
    _set_raw(surge, 'a_volume', 1.0)               # Volume al máximo

    _set_safe(surge, 'fx_a1_fx_type', 'Off')       # Sin FX internos (KranchDD hace esto)

    return surge


def configure_lead(surge):
    """Lead darkpsy — etéreo, detrás del mix, con profundidad.

    Supersaw con reverb. Se sienta atrás, no compite con bass/acid.
    Octave normal (no -1) para estar en rango melódico correcto.
    """
    surge.a_osc_1_type = 'Modern'
    _set_raw(surge, 'a_osc_1_octave', 0.333)       # -1 octave (como v9, funciona mejor)
    surge.a_osc_1_unison_voices = '3 voices'        # Menos voces = más definido
    surge.a_osc_1_unison_detune = '8.00 cents'      # Tighter
    _set_raw(surge, 'a_pre_filter_gain', 0.65)     # Drive

    surge.a_filter_1_type = 'LP 12 dB'
    _set_raw(surge, 'a_filter_1_cutoff', 0.38)
    _set_raw(surge, 'a_filter_1_resonance', 0.08)
    _set_raw(surge, 'a_filter_1_feg_mod_amount', 0.15)  # Sutil sweep

    _set_raw(surge, 'a_filter_eg_attack', 0.05)
    _set_raw(surge, 'a_filter_eg_decay', 0.3)
    _set_raw(surge, 'a_filter_eg_sustain', 0.4)
    _set_raw(surge, 'a_filter_eg_release', 0.3)

    _set_raw(surge, 'a_amp_eg_attack', 0.15)       # Fade in suave
    _set_raw(surge, 'a_amp_eg_decay', 0.4)
    _set_raw(surge, 'a_amp_eg_sustain', 0.5)
    _set_raw(surge, 'a_amp_eg_release', 0.35)       # Release largo = etéreo

    surge.a_play_mode = 'Poly'
    _set_raw(surge, 'a_volume', 1.0)               # Volume máximo

    # Reverb para profundidad
    _set_safe(surge, 'fx_a1_fx_type', 'Reverb 2')
    _set_raw(surge, 'fx_a1_param_1', 0.5)          # Mix moderado
    _set_raw(surge, 'fx_a1_param_2', 0.6)          # Decay largo

    return surge


def configure_acid(surge):
    """Acid darkpsy — squelchy pero controlado, no gritado.

    Técnica 303: Saw → LP 24dB resonante → fast envelope.
    La clave es que la resonancia hace el squelch pero NO al máximo.
    Drive moderado. KranchDD se aplica SUAVE después (wet 0.2).
    """
    surge.a_osc_1_type = 'Classic'
    _set_raw(surge, 'a_osc_1_octave', 0.5)
    _set_raw(surge, 'a_osc_1_shape', 0.85)         # Saw (ligeramente menos que 0.9)

    # LP 24dB — steep slope, resonancia CONTROLADA
    surge.a_filter_1_type = 'LP 24 dB'
    _set_raw(surge, 'a_filter_1_cutoff', 0.25)     # Más abierto que 0.2
    _set_raw(surge, 'a_filter_1_resonance', 0.50)  # BAJADO de 0.7 — squelch sin screech
    _set_raw(surge, 'a_filter_1_feg_mod_amount', 0.60)  # BAJADO de 0.85 — sweep controlado
    _set_raw(surge, 'a_filter_1_keytrack', 0.6)    # Sigue la nota

    # Filter env rápido pero no instantáneo
    _set_raw(surge, 'a_filter_eg_attack', 0.01)    # Casi instantáneo
    _set_raw(surge, 'a_filter_eg_decay', 0.12)     # Un poco más lento
    _set_raw(surge, 'a_filter_eg_sustain', 0.08)
    _set_raw(surge, 'a_filter_eg_release', 0.06)

    # Amp env con release limpio
    _set_raw(surge, 'a_amp_eg_attack', 0.005)
    _set_raw(surge, 'a_amp_eg_decay', 0.2)
    _set_raw(surge, 'a_amp_eg_sustain', 0.3)
    _set_raw(surge, 'a_amp_eg_release', 0.10)      # Release más largo = menos clicks

    surge.a_play_mode = 'Mono'
    _set_raw(surge, 'a_pre_filter_gain', 0.65)     # Drive moderado
    _set_raw(surge, 'a_volume', 1.0)               # Volume máximo

    # Distortion LEVE interna
    _set_safe(surge, 'fx_a1_fx_type', 'Distortion')
    _set_raw(surge, 'fx_a1_param_1', 0.3)          # Drive bajo
    _set_raw(surge, 'fx_a1_param_2', 0.5)          # Mix 50%

    return surge


def configure_pad(surge):
    """Pad atmosférico — oscuro, suave, sin raspado.

    Sine puro con poco unison (sin chorus = sin pixelado).
    LPF bajo corta todo lo rasposo desde la fuente.
    Reverb larga para espacio.
    """
    surge.a_osc_1_type = 'Sine'
    _set_raw(surge, 'a_osc_1_octave', 0.5)
    surge.a_osc_1_unison_voices = '2 voices'        # MENOS voces (era 3)
    surge.a_osc_1_unison_detune = '4.00 cents'      # MENOS detune (era 8)

    # LPF MÁS CERRADO — corta raspado desde la fuente
    surge.a_filter_1_type = 'LP 12 dB'
    _set_raw(surge, 'a_filter_1_cutoff', 0.32)     # BAJADO de 0.45
    _set_raw(surge, 'a_filter_1_resonance', 0.05)  # Mínima

    # Envelope lento = pad atmosférico
    _set_raw(surge, 'a_amp_eg_attack', 0.65)       # Fade in largo
    _set_raw(surge, 'a_amp_eg_decay', 0.5)
    _set_raw(surge, 'a_amp_eg_sustain', 0.75)
    _set_raw(surge, 'a_amp_eg_release', 0.70)      # Release largo

    surge.a_play_mode = 'Poly'
    _set_raw(surge, 'a_volume', 1.0)

    # SIN CHORUS (causaba el pixelado) — solo reverb
    _set_safe(surge, 'fx_a1_fx_type', 'Reverb 2')
    _set_raw(surge, 'fx_a1_param_1', 0.45)         # Mix
    _set_raw(surge, 'fx_a1_param_2', 0.7)          # Decay largo
    _set_safe(surge, 'fx_a2_fx_type', 'Off')       # Sin segundo FX

    return surge


def configure_fm_texture(surge):
    """FM texture alienígena — sin picos de graves.

    FM3 con profundidad REDUCIDA y HPF para cortar sub-armónicos.
    El BP filter está más abierto y menos resonante.
    """
    surge.a_osc_1_type = 'FM3'
    _set_raw(surge, 'a_osc_1_octave', 0.5)

    # FM routing con depth REDUCIDA
    _set_safe(surge, 'a_fm_routing', 'Osc 2 > Osc 1')
    _set_raw(surge, 'a_fm_depth', 0.45)            # BAJADO de 0.65

    surge.a_osc_2_type = 'Sine'
    _set_raw(surge, 'a_osc_2_octave', 0.667)       # +1 octave

    # HP filter en vez de BP — elimina sub-armónicos desde la fuente
    surge.a_filter_1_type = 'HP 12 dB'
    _set_raw(surge, 'a_filter_1_cutoff', 0.35)     # Corta graves
    _set_raw(surge, 'a_filter_1_resonance', 0.20)  # BAJADO de 0.4

    # Segundo filtro LP para controlar agudos extremos
    surge.a_filter_2_type = 'LP 12 dB'
    _set_raw(surge, 'a_filter_2_cutoff', 0.65)
    _set_raw(surge, 'a_filter_2_resonance', 0.10)

    # Envelope percusivo
    _set_raw(surge, 'a_amp_eg_attack', 0.005)
    _set_raw(surge, 'a_amp_eg_decay', 0.18)
    _set_raw(surge, 'a_amp_eg_sustain', 0.15)
    _set_raw(surge, 'a_amp_eg_release', 0.12)

    surge.a_play_mode = 'Poly'
    _set_raw(surge, 'a_pre_filter_gain', 0.70)
    _set_raw(surge, 'a_volume', 1.0)

    # Delay para espacio
    _set_safe(surge, 'fx_a1_fx_type', 'Delay')
    _set_raw(surge, 'fx_a1_param_1', 0.3)          # Mix bajo
    _set_raw(surge, 'fx_a1_param_2', 0.4)          # Feedback moderado

    return surge


def configure_fx_riser(surge):
    """FX riser — sweep controlado, no caótico.

    Noise filtrado con sweep de filtro más moderado.
    """
    surge.a_osc_1_type = 'S&H Noise'
    _set_raw(surge, 'a_osc_1_octave', 0.5)

    surge.a_filter_1_type = 'LP 12 dB'
    _set_raw(surge, 'a_filter_1_cutoff', 0.25)
    _set_raw(surge, 'a_filter_1_resonance', 0.25)  # Menos resonancia
    _set_raw(surge, 'a_filter_1_feg_mod_amount', 0.60)  # BAJADO de 0.9

    # Filter sweep más controlado
    _set_raw(surge, 'a_filter_eg_attack', 0.7)
    _set_raw(surge, 'a_filter_eg_decay', 0.3)
    _set_raw(surge, 'a_filter_eg_sustain', 0.7)    # Bajado de 0.9
    _set_raw(surge, 'a_filter_eg_release', 0.2)

    _set_raw(surge, 'a_amp_eg_attack', 0.5)
    _set_raw(surge, 'a_amp_eg_decay', 0.3)
    _set_raw(surge, 'a_amp_eg_sustain', 0.7)       # Bajado de 0.8
    _set_raw(surge, 'a_amp_eg_release', 0.25)

    surge.a_play_mode = 'Poly'

    _set_safe(surge, 'fx_a1_fx_type', 'Reverb 2')
    _set_raw(surge, 'fx_a1_param_1', 0.4)
    _set_raw(surge, 'fx_a1_param_2', 0.5)

    return surge


# ============================================================
# NUEVOS PRESETS: Drums en Surge XT (reemplazan numpy noise)
# ============================================================

def configure_hat(surge):
    """Hi-hat — S&H Noise con carácter metálico.

    S&H Noise oscilator → HP filter suave → envelope rápido pero audible.
    """
    surge.a_osc_1_type = 'S&H Noise'
    _set_raw(surge, 'a_osc_1_octave', 0.5)         # Octave normal
    _set_raw(surge, 'a_pre_filter_gain', 0.75)     # Drive para nivel
    _set_raw(surge, 'a_volume', 1.0)               # Volume máximo

    # HP filter — no tan alto, dejar pasar señal
    surge.a_filter_1_type = 'HP 12 dB'
    _set_raw(surge, 'a_filter_1_cutoff', 0.40)     # BAJADO de 0.55
    _set_raw(surge, 'a_filter_1_resonance', 0.18)  # Toque metálico

    # Envelope rápido pero no instantáneo
    _set_raw(surge, 'a_amp_eg_attack', 0.0)
    _set_raw(surge, 'a_amp_eg_decay', 0.10)        # SUBIDO de 0.06 — más audible
    _set_raw(surge, 'a_amp_eg_sustain', 0.02)
    _set_raw(surge, 'a_amp_eg_release', 0.06)      # SUBIDO de 0.04

    surge.a_play_mode = 'Poly'
    _set_safe(surge, 'fx_a1_fx_type', 'Off')

    return surge


def configure_clap(surge):
    """Clap/snare — FM con carácter orgánico.

    FM3 → BP filter → envelope percusivo con decay medio.
    FM le da más textura que noise puro (suena a "cuero").
    """
    surge.a_osc_1_type = 'FM3'
    _set_raw(surge, 'a_osc_1_octave', 0.5)

    _set_safe(surge, 'a_fm_routing', 'Osc 2 > Osc 1')
    _set_raw(surge, 'a_fm_depth', 0.8)             # Alta FM = ruido tímbrico

    surge.a_osc_2_type = 'Sine'
    _set_raw(surge, 'a_osc_2_octave', 0.667)

    # BP filter — da el "cuerpo" del clap
    surge.a_filter_1_type = 'BP 12 dB'
    _set_raw(surge, 'a_filter_1_cutoff', 0.45)
    _set_raw(surge, 'a_filter_1_resonance', 0.20)

    # Envelope percusivo medio
    _set_raw(surge, 'a_amp_eg_attack', 0.0)
    _set_raw(surge, 'a_amp_eg_decay', 0.12)
    _set_raw(surge, 'a_amp_eg_sustain', 0.05)
    _set_raw(surge, 'a_amp_eg_release', 0.10)

    surge.a_play_mode = 'Poly'
    _set_raw(surge, 'a_pre_filter_gain', 0.70)
    _set_raw(surge, 'a_volume', 1.0)

    # Reverb corto (room) — le da espacio sin lavar
    _set_safe(surge, 'fx_a1_fx_type', 'Reverb 2')
    _set_raw(surge, 'fx_a1_param_1', 0.25)         # Mix bajo
    _set_raw(surge, 'fx_a1_param_2', 0.2)          # Decay corto (room)

    return surge
