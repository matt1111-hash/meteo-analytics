#!/usr/bin/env python3
# mypy: ignore-errors
# -*- coding: utf-8 -*-

"""
Color Palette - Data I/O Module
Import/export metódusok ColorPalette osztályhoz.
"""

from typing import Any

from src.presentation.gui.color_palette.types import HSLColor
from src.presentation.gui.types import ThemeType


def _serialize_hsl_color(hsl_color: HSLColor) -> dict[str, Any]:
    """Serialize one HSL color to export payload."""
    return {
        "hex": hsl_color.to_hex(),
        "hsl": {
            "hue": hsl_color.hue,
            "saturation": hsl_color.saturation,
            "lightness": hsl_color.lightness,
            "alpha": hsl_color.alpha,
        },
    }


def _build_hsl_color(hsl_data: dict[str, Any]) -> HSLColor:
    """Build HSLColor from serialized payload."""
    return HSLColor(
        hsl_data["hue"],
        hsl_data["saturation"],
        hsl_data["lightness"],
        hsl_data.get("alpha", 1.0),
    )


def _export_palette_variants(
    generated_variants: dict[str, dict[str, HSLColor]],
) -> dict[str, dict[str, str]]:
    """Export generated color variants to hex payload."""
    exported_variants: dict[str, dict[str, str]] = {}
    for semantic_name, variants in generated_variants.items():
        exported_variants[semantic_name] = {
            variant_name: variant_color.to_hex() for variant_name, variant_color in variants.items()
        }
    return exported_variants


def _import_base_colors(data_io_mixin: Any, base_colors: dict[str, dict[str, Any]]) -> None:
    """Import base colors from serialized payload."""
    for semantic_name, color_data in base_colors.items():
        if "hex" in color_data:
            data_io_mixin.set_base_color(semantic_name, color_data["hex"])
            continue
        if "hsl" in color_data:
            data_io_mixin.set_base_color(semantic_name, _build_hsl_color(color_data["hsl"]))


class DataIOMixin:
    """Import/export metódusok ColorPalette osztályhoz."""

    def export_palette(self, include_variants: bool = True) -> dict[str, Any]:
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
            export_data["base_colors"][semantic_name] = _serialize_hsl_color(hsl_color)

        # Variants export
        if include_variants:
            export_data["variants"] = _export_palette_variants(self._generated_variants)

        return export_data

    def import_palette(self, import_data: dict[str, Any]) -> bool:
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
                _import_base_colors(self, import_data["base_colors"])

            # Semantic mapping
            if "semantic_mapping" in import_data:
                self._semantic_mapping = import_data["semantic_mapping"]

            print("🎨 DEBUG: Palette imported successfully")
            return True

        except Exception as e:
            print(f"❌ DEBUG: Palette import failed: {e}")
            return False
