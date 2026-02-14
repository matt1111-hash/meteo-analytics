#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Color Palette Harmony Module
Színharmónia generálás - complementary, triadic, analogous, stb.
"""

from typing import Dict

from src.presentation.gui.color_palette.types import ColorHarmony, HSLColor


def generate_harmony(
    base_color: HSLColor, harmony_type: ColorHarmony
) -> Dict[str, str]:
    """
    Színharmónia generálása base szín alapján.

    Args:
        base_color: Base szín HSLColor formátumban
        harmony_type: Harmónia típusa

    Returns:
        Harmónia színek {name: hex_color} formátumban
    """
    harmony_colors = {}

    if harmony_type == ColorHarmony.COMPLEMENTARY:
        # Complementary (180° eltérés)
        comp_color = base_color.rotate_hue(180)
        harmony_colors["complementary"] = comp_color.to_hex()

    elif harmony_type == ColorHarmony.TRIADIC:
        # Triadic (120° eltérések)
        triadic_1 = base_color.rotate_hue(120)
        triadic_2 = base_color.rotate_hue(240)
        harmony_colors["triadic_1"] = triadic_1.to_hex()
        harmony_colors["triadic_2"] = triadic_2.to_hex()

    elif harmony_type == ColorHarmony.ANALOGOUS:
        # Analogous (30° eltérések)
        analog_1 = base_color.rotate_hue(30)
        analog_2 = base_color.rotate_hue(-30)
        harmony_colors["analogous_1"] = analog_1.to_hex()
        harmony_colors["analogous_2"] = analog_2.to_hex()

    elif harmony_type == ColorHarmony.SPLIT_COMPLEMENTARY:
        # Split complementary (150° és 210°)
        split_1 = base_color.rotate_hue(150)
        split_2 = base_color.rotate_hue(210)
        harmony_colors["split_comp_1"] = split_1.to_hex()
        harmony_colors["split_comp_2"] = split_2.to_hex()

    elif harmony_type == ColorHarmony.TETRADIC:
        # Tetradic/Square (90° eltérések)
        tetra_1 = base_color.rotate_hue(90)
        tetra_2 = base_color.rotate_hue(180)
        tetra_3 = base_color.rotate_hue(270)
        harmony_colors["tetradic_1"] = tetra_1.to_hex()
        harmony_colors["tetradic_2"] = tetra_2.to_hex()
        harmony_colors["tetradic_3"] = tetra_3.to_hex()

    elif harmony_type == ColorHarmony.MONOCHROMATIC:
        # Monochromatic (lightness variációk)
        mono_light = base_color.lighten(30)
        mono_dark = base_color.darken(30)
        mono_desat = base_color.desaturate(40)
        harmony_colors["monochromatic_light"] = mono_light.to_hex()
        harmony_colors["monochromatic_dark"] = mono_dark.to_hex()
        harmony_colors["monochromatic_muted"] = mono_desat.to_hex()

    return harmony_colors
