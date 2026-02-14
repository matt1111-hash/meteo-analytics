#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Color Palette Factory Module
Factory functions ColorPalette instance-ok létrehozásához.
"""

from src.presentation.gui.color_palette.core import ColorPalette
from src.presentation.gui.color_palette.generators import MaterialColorGenerator
from src.presentation.gui.types import ThemeType


def create_color_palette(
    preset_name: str = "red", theme_type: ThemeType = ThemeType.LIGHT
) -> ColorPalette:
    """
    🎨 KRITIKUS JAVÍTÁS: ColorPalette factory function - "red" preset alapértelmezett!

    Args:
        preset_name: Preset neve (alapértelmezett: "red" - #C43939)
        theme_type: Téma típusa

    Returns:
        Konfigurált ColorPalette instance
    """
    palette = ColorPalette()
    palette.set_theme_type(theme_type)
    palette.load_semantic_preset(preset_name)

    print(f"🎨 FACTORY: ColorPalette created with preset: {preset_name}")
    return palette


def create_material_palette(theme_type: ThemeType = ThemeType.LIGHT) -> ColorPalette:
    """
    Material Design ColorPalette létrehozása.

    Args:
        theme_type: Téma típusa

    Returns:
        Material Design ColorPalette
    """
    material_generator = MaterialColorGenerator()
    palette = ColorPalette(material_generator)
    palette.set_theme_type(theme_type)
    palette.load_semantic_preset("material")

    return palette


def create_weather_palette(
    base_temperature: str = "#C43939", theme_type: ThemeType = ThemeType.LIGHT
) -> ColorPalette:
    """
    🎨 KRITIKUS JAVÍTÁS: Weather-specific ColorPalette - piros (#C43939) alapértelmezett!

    Args:
        base_temperature: Base hőmérséklet szín (alapértelmezett: #C43939)
        theme_type: Téma típusa

    Returns:
        Weather-optimized ColorPalette
    """
    palette = ColorPalette()
    palette.set_theme_type(theme_type)
    palette.load_semantic_preset("red")  # 🎨 KRITIKUS JAVÍTÁS: "red" preset használata

    # Weather-specific colors generálása
    weather_colors = palette.generate_weather_palette(base_temperature)
    for weather_type, color in weather_colors.items():
        palette.set_base_color(f"weather_{weather_type}", color)

    print(
        f"🌦️ FACTORY: Weather palette created with base temperature: {base_temperature}"
    )
    return palette
