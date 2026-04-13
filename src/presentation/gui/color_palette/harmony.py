#!/usr/bin/env python3
# mypy: ignore-errors
# -*- coding: utf-8 -*-

"""
Color Palette Harmony Module
Színharmónia generálás - complementary, triadic, analogous, stb.
"""

from src.presentation.gui.color_palette.types import ColorHarmony, HSLColor


def _build_rotated_harmony(base_color: HSLColor, rotations: dict[str, int]) -> dict[str, str]:
    """Build harmony colors from hue rotations."""
    return {name: base_color.rotate_hue(rotation).to_hex() for name, rotation in rotations.items()}


def _build_monochromatic_harmony(base_color: HSLColor) -> dict[str, str]:
    """Build monochromatic harmony variants."""
    return {
        "monochromatic_light": base_color.lighten(30).to_hex(),
        "monochromatic_dark": base_color.darken(30).to_hex(),
        "monochromatic_muted": base_color.desaturate(40).to_hex(),
    }


def generate_harmony(base_color: HSLColor, harmony_type: ColorHarmony) -> dict[str, str]:
    """
    Színharmónia generálása base szín alapján.

    Args:
        base_color: Base szín HSLColor formátumban
        harmony_type: Harmónia típusa

    Returns:
        Harmónia színek {name: hex_color} formátumban
    """
    harmony_builders = {
        ColorHarmony.COMPLEMENTARY: lambda: _build_rotated_harmony(
            base_color, {"complementary": 180}
        ),
        ColorHarmony.TRIADIC: lambda: _build_rotated_harmony(
            base_color, {"triadic_1": 120, "triadic_2": 240}
        ),
        ColorHarmony.ANALOGOUS: lambda: _build_rotated_harmony(
            base_color, {"analogous_1": 30, "analogous_2": -30}
        ),
        ColorHarmony.SPLIT_COMPLEMENTARY: lambda: _build_rotated_harmony(
            base_color, {"split_comp_1": 150, "split_comp_2": 210}
        ),
        ColorHarmony.TETRADIC: lambda: _build_rotated_harmony(
            base_color, {"tetradic_1": 90, "tetradic_2": 180, "tetradic_3": 270}
        ),
        ColorHarmony.MONOCHROMATIC: lambda: _build_monochromatic_harmony(base_color),
    }
    builder = harmony_builders.get(harmony_type)
    return builder() if builder else {}
