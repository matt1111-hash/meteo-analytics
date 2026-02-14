#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Color Palette - Data I/O Module
Import/export metódusok ColorPalette osztályhoz.
"""

from typing import Any, Dict

from src.presentation.gui.color_palette.types import HSLColor
from src.presentation.gui.types import ThemeType


class DataIOMixin:
    """Import/export metódusok ColorPalette osztályhoz."""

    def export_palette(self, include_variants: bool = True) -> Dict[str, Any]:
        """
        Színpaletta exportálása JSON-kompatibilis formátumban.

        Args:
            include_variants: Variánsok is exportálva legyenek-e

        Returns:
            Export adatok
        """
        export_data = {
            "theme_type": self._theme_type.value,
            "generator_type": self.generator.__class__.__name__,
            "base_colors": {},
            "semantic_mapping": self._semantic_mapping.copy(),
        }

        # Base colors export
        for semantic_name, hsl_color in self._base_colors.items():
            export_data["base_colors"][semantic_name] = {
                "hex": hsl_color.to_hex(),
                "hsl": {
                    "hue": hsl_color.hue,
                    "saturation": hsl_color.saturation,
                    "lightness": hsl_color.lightness,
                    "alpha": hsl_color.alpha,
                },
            }

        # Variants export
        if include_variants:
            export_data["variants"] = {}
            for semantic_name, variants in self._generated_variants.items():
                export_data["variants"][semantic_name] = {}
                for variant_name, variant_color in variants.items():
                    export_data["variants"][semantic_name][variant_name] = (
                        variant_color.to_hex()
                    )

        return export_data

    def import_palette(self, import_data: Dict[str, Any]) -> bool:
        """
        Színpaletta importálása JSON adatokból.

        Args:
            import_data: Import adatok

        Returns:
            Sikeresen importálva-e
        """
        try:
            # Theme type
            if "theme_type" in import_data:
                self._theme_type = ThemeType(import_data["theme_type"])

            # Base colors
            if "base_colors" in import_data:
                for semantic_name, color_data in import_data["base_colors"].items():
                    if "hex" in color_data:
                        self.set_base_color(semantic_name, color_data["hex"])
                    elif "hsl" in color_data:
                        hsl_data = color_data["hsl"]
                        hsl_color = HSLColor(
                            hsl_data["hue"],
                            hsl_data["saturation"],
                            hsl_data["lightness"],
                            hsl_data.get("alpha", 1.0),
                        )
                        self.set_base_color(semantic_name, hsl_color)

            # Semantic mapping
            if "semantic_mapping" in import_data:
                self._semantic_mapping = import_data["semantic_mapping"]

            print("🎨 DEBUG: Palette imported successfully")
            return True

        except Exception as e:
            print(f"❌ DEBUG: Palette import failed: {e}")
            return False
