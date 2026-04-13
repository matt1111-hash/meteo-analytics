#!/usr/bin/env python3
# mypy: ignore-errors
# -*- coding: utf-8 -*-

"""
Color Palette Utilities Module
Globális convenience függvények színműveletekhez.
"""

from src.presentation.gui.color_palette.core import ColorPalette
from src.presentation.gui.color_palette.types import HSLColor
from src.presentation.gui.types import ThemeType


def hex_to_hsl(hex_color: str) -> HSLColor:
    """Convenience function hex → HSL konverzióhoz."""
    palette = ColorPalette()
    return palette._hex_to_hsl(hex_color)


def calculate_color_contrast(color1: str, color2: str) -> float:
    """Convenience function kontraszt számításhoz."""
    palette = ColorPalette()
    return palette.calculate_contrast_ratio(color1, color2)


def generate_color_variants(
    base_hex: str, theme_type: ThemeType = ThemeType.LIGHT
) -> dict[str, str]:
    """
    Convenience function színvariánsok generálásához.

    Args:
        base_hex: Base szín hex formátumban
        theme_type: Téma típusa

    Returns:
        Variánsok {variant_name: hex_color}
    """
    palette = ColorPalette()
    palette.set_theme_type(theme_type)
    palette.set_base_color("temp", base_hex)

    return palette.get_all_variants("temp")


def generate_weather_color_scheme(base_temp: str = "#C43939") -> dict[str, str]:
    """
    🎨 KRITIKUS JAVÍTÁS: Weather color scheme - piros (#C43939) alapértelmezett!

    Args:
        base_temp: Base hőmérséklet szín (alapértelmezett: #C43939)

    Returns:
        Weather színséma
    """
    palette = ColorPalette()
    return palette.generate_weather_palette(base_temp)
