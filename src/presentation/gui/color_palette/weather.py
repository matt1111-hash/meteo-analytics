#!/usr/bin/env python3
# mypy: ignore-errors
# -*- coding: utf-8 -*-

"""
Color Palette Weather Module
Időjárás-specifikus színpaletta generálás.
"""

from src.presentation.gui.color_palette.types import HSLColor


def generate_weather_palette(base_temperature: str, hex_to_hsl_func) -> dict[str, str]:
    """
    Időjárás-specifikus színpaletta generálása hőmérséklet base színből.

    Args:
        base_temperature: Base hőmérséklet szín hex formátumban
        hex_to_hsl_func: Hex → HSLColor konvertáló függvény

    Returns:
        Weather színpaletta {weather_type: hex_color}
    """
    base_hsl = hex_to_hsl_func(base_temperature)

    weather_palette = {}

    # Triadic harmony alapján időjárás típusok
    weather_palette["temperature"] = base_hsl.to_hex()
    weather_palette["humidity"] = base_hsl.rotate_hue(120).to_hex()  # Kék irányba
    weather_palette["wind"] = base_hsl.rotate_hue(240).to_hex()  # Zöld irányba

    # Complementary alapján pressure
    weather_palette["pressure"] = base_hsl.rotate_hue(180).to_hex()

    # Analogous alapján precipitation
    weather_palette["precipitation"] = base_hsl.rotate_hue(60).to_hex()
    weather_palette["clouds"] = base_hsl.rotate_hue(-60).to_hex()

    return weather_palette


def generate_alert_gradient(base_alert: str, hex_to_hsl_func, levels: int = 5) -> list[str]:
    """
    Alert szintek gradiens generálása.

    Args:
        base_alert: Base alert szín
        hex_to_hsl_func: Hex → HSLColor konvertáló függvény
        levels: Alert szintek száma

    Returns:
        Alert színek listája (enyhe → súlyos)
    """
    base_hsl = hex_to_hsl_func(base_alert)

    gradient = []
    for i in range(levels):
        # Lightness és saturation fokozatos változtatása
        factor = i / (levels - 1)  # 0.0 → 1.0

        lightness = base_hsl.lightness + (30 * (1 - factor))  # 70% → 40%
        saturation = base_hsl.saturation + (20 * factor)  # 60% → 80%

        alert_color = HSLColor(base_hsl.hue, saturation, lightness)
        gradient.append(alert_color.to_hex())

    return gradient
