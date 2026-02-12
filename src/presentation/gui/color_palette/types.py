#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Color Palette Types Module
Enumok, NamedTuple és dataclass típusdefiníciók.
"""

import colorsys
from dataclasses import dataclass
from enum import Enum
from typing import NamedTuple, Tuple


class ColorFormat(Enum):
    """Szín formátumok."""

    HEX = "hex"
    RGB = "rgb"
    HSL = "hsl"
    HSV = "hsv"


class ColorHarmony(Enum):
    """Színharmónia típusok."""

    MONOCHROMATIC = "monochromatic"
    ANALOGOUS = "analogous"
    COMPLEMENTARY = "complementary"
    TRIADIC = "triadic"
    TETRADIC = "tetradic"
    SPLIT_COMPLEMENTARY = "split_complementary"


class ColorBlindnessType(Enum):
    """Színvakság típusok szimulációhoz."""

    PROTANOPIA = "protanopia"  # Red-blind
    DEUTERANOPIA = "deuteranopia"  # Green-blind
    TRITANOPIA = "tritanopia"  # Blue-blind
    ACHROMATOPSIA = "achromatopsia"  # Complete color blindness


class ColorMetrics(NamedTuple):
    """Szín metrikák accessibility ellenőrzéshez."""

    luminance: float
    contrast_ratio: float
    wcag_aa_compliant: bool
    wcag_aaa_compliant: bool
    readable_on_white: bool
    readable_on_black: bool


@dataclass
class HSLColor:
    """HSL színreprezentáció egyszerű manipulációhoz."""

    hue: float  # 0-360
    saturation: float  # 0-100
    lightness: float  # 0-100
    alpha: float = 1.0  # 0-1

    def to_hex(self) -> str:
        """HSL konvertálás hex formátumra."""
        h, s, light = self.hue / 360, self.saturation / 100, self.lightness / 100
        r, g, b = colorsys.hls_to_rgb(h, light, s)
        return f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"

    def to_rgb(self) -> Tuple[int, int, int]:
        """HSL konvertálás RGB-re."""
        h, s, light = self.hue / 360, self.saturation / 100, self.lightness / 100
        r, g, b = colorsys.hls_to_rgb(h, light, s)
        return int(r * 255), int(g * 255), int(b * 255)

    def lighten(self, amount: float) -> "HSLColor":
        """Szín világosítása amount értékkel."""
        new_lightness = min(100, self.lightness + amount)
        return HSLColor(self.hue, self.saturation, new_lightness, self.alpha)

    def darken(self, amount: float) -> "HSLColor":
        """Szín sötétítése amount értékkel."""
        new_lightness = max(0, self.lightness - amount)
        return HSLColor(self.hue, self.saturation, new_lightness, self.alpha)

    def saturate(self, amount: float) -> "HSLColor":
        """Szín telítettségének növelése."""
        new_saturation = min(100, self.saturation + amount)
        return HSLColor(self.hue, new_saturation, self.lightness, self.alpha)

    def desaturate(self, amount: float) -> "HSLColor":
        """Szín telítettségének csökkentése."""
        new_saturation = max(0, self.saturation - amount)
        return HSLColor(self.hue, new_saturation, self.lightness, self.alpha)

    def rotate_hue(self, degrees: float) -> "HSLColor":
        """Hue forgatása degrees értékkel."""
        new_hue = (self.hue + degrees) % 360
        return HSLColor(new_hue, self.saturation, self.lightness, self.alpha)
