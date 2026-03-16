#!/usr/bin/env python3
# mypy: ignore-errors
# -*- coding: utf-8 -*-

"""
Color Palette Generators Module
Színgeneráló stratégiák - StandardColorGenerator és MaterialColorGenerator.
"""

from abc import ABC, abstractmethod
from typing import Dict

from src.presentation.gui.color_palette.types import HSLColor
from src.presentation.gui.types import ThemeType


class ColorGenerator(ABC):
    """Absztrakt base class különböző színgeneráló stratégiákhoz."""

    @abstractmethod
    def generate_variants(
        self, base_color: HSLColor, theme_type: ThemeType
    ) -> Dict[str, HSLColor]:
        """
        Színvariánsok generálása base színből.

        Args:
            base_color: Alapszín HSL formátumban
            theme_type: Téma típusa (light/dark)

        Returns:
            Színvariánsok dictionary-je
        """


class StandardColorGenerator(ColorGenerator):
    """Standard színvariáns generátor - light/dark adaptive."""

    def generate_variants(
        self, base_color: HSLColor, theme_type: ThemeType
    ) -> Dict[str, HSLColor]:
        """Standard variánsok: light, dark, hover, pressed, disabled."""
        variants = {}

        if theme_type == ThemeType.LIGHT:
            # Light theme variánsok
            variants["light"] = base_color.lighten(20)
            variants["dark"] = base_color.darken(20)
            variants["hover"] = base_color.darken(10)
            variants["pressed"] = base_color.darken(30)
            variants["disabled"] = base_color.desaturate(50).lighten(30)
        else:
            # Dark theme variánsok - inverz logika
            variants["light"] = base_color.lighten(30)
            variants["dark"] = base_color.darken(15)
            variants["hover"] = base_color.lighten(15)
            variants["pressed"] = base_color.lighten(25)
            variants["disabled"] = base_color.desaturate(60).darken(20)

        return variants


class MaterialColorGenerator(ColorGenerator):
    """Material Design inspirált színgenerátor."""

    def generate_variants(
        self, base_color: HSLColor, theme_type: ThemeType
    ) -> Dict[str, HSLColor]:
        """Material Design 50-900 színskála generálása."""
        variants = {}

        # Material Design világossági szintek
        lightness_stops = {
            "50": 95,
            "100": 90,
            "200": 80,
            "300": 70,
            "400": 60,
            "500": 50,  # Base color
            "600": 40,
            "700": 30,
            "800": 20,
            "900": 10,
        }

        for stop, target_lightness in lightness_stops.items():
            # Telítettség adaptálása világosság alapján
            saturation_factor = 1.0
            if target_lightness > 80:  # Very light colors
                saturation_factor = 0.6
            elif target_lightness < 20:  # Very dark colors
                saturation_factor = 0.8

            adjusted_saturation = base_color.saturation * saturation_factor
            variants[f"material_{stop}"] = HSLColor(
                base_color.hue, adjusted_saturation, target_lightness, base_color.alpha
            )

        # Standard variánsok hozzáadása
        variants["light"] = variants["material_200"]
        variants["dark"] = variants["material_700"]
        variants["hover"] = (
            variants["material_400"]
            if theme_type == ThemeType.LIGHT
            else variants["material_300"]
        )
        variants["pressed"] = (
            variants["material_800"]
            if theme_type == ThemeType.LIGHT
            else variants["material_200"]
        )
        variants["disabled"] = (
            variants["material_100"]
            if theme_type == ThemeType.LIGHT
            else variants["material_800"]
        )

        return variants
