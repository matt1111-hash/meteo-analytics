#!/usr/bin/env python3
# mypy: ignore-errors
# -*- coding: utf-8 -*-

"""
Color Palette - Utility Methods Module
Private utility metódusok ColorPalette osztályhoz.
"""

import colorsys
from typing import Any, Dict

from src.presentation.gui.color_palette.types import HSLColor


class UtilityMethodsMixin:
    """Private utility metódusok ColorPalette osztályhoz."""

    def _hex_to_hsl(self, hex_color: str) -> HSLColor:
        """Hex szín konvertálása HSLColor-ra."""
        hex_color = hex_color.lstrip("#")
        r, g, b = [int(hex_color[i : i + 2], 16) / 255.0 for i in (0, 2, 4)]
        h, light, s = colorsys.rgb_to_hls(r, g, b)

        return HSLColor(hue=h * 360, saturation=s * 100, lightness=light * 100)

    def _generate_variants_for_color(self, semantic_name: str) -> None:
        """Variánsok generálása egy semantic színhez."""
        base_color = self._base_colors.get(semantic_name)
        if not base_color:
            return

        variants = self.generator.generate_variants(base_color, self._theme_type)
        self._generated_variants[semantic_name] = variants

        print(f"🎨 DEBUG: Generated {len(variants)} variants for {semantic_name}")

    def get_debug_info(self) -> Dict[str, Any]:
        """Debug információk lekérdezése."""
        return {
            "theme_type": self._theme_type.value,
            "generator_type": self.generator.__class__.__name__,
            "base_colors_count": len(self._base_colors),
            "generated_variants_count": sum(
                len(variants) for variants in self._generated_variants.values()
            ),
            "semantic_names": list(self._base_colors.keys()),
        }
