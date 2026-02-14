#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Color Palette - Theme Management Module
Theme management és semantic preset kezelő metódusok.
"""

from src.presentation.gui.color_palette.presets import get_preset
from src.presentation.gui.types import ThemeType


class ThemeManagementMixin:
    """Theme management metódusok ColorPalette osztályhoz."""

    def set_theme_type(self, theme_type: ThemeType) -> None:
        """
        Téma típus beállítása és variánsok újragenerálása.

        Args:
            theme_type: Téma típusa
        """
        if self._theme_type != theme_type:
            self._theme_type = theme_type

            # Összes variáns újragenerálása új téma típussal
            for semantic_name in self._base_colors.keys():
                self._generate_variants_for_color(semantic_name)

            print(
                f"🎨 DEBUG: Theme type changed to {theme_type.value}, variants regenerated"
            )

    def get_theme_type(self) -> ThemeType:
        """Jelenlegi téma típus lekérdezése."""
        return self._theme_type

    def load_semantic_preset(self, preset_name: str) -> None:
        """
        Előre definiált semantic színkészlet betöltése.
        🎨 KRITIKUS JAVÍTÁS: "red" preset hozzáadva - primary: #C43939

        Args:
            preset_name: Preset neve ("default", "material", "bootstrap", "weather", "red")
        """
        preset_colors = get_preset(preset_name, self._theme_type)

        if preset_colors:
            self.set_multiple_base_colors(preset_colors)
            print(f"🎨 DEBUG: Semantic preset loaded: {preset_name}")

            # 🎨 KRITIKUS JAVÍTÁS: Piros téma alkalmazás logolása
            if preset_name == "red":
                print("🎨 PIROS TÉMA AKTIVÁLVA: primary = #C43939 (user request)")
        else:
            print(f"❌ DEBUG: Unknown preset: {preset_name}")
