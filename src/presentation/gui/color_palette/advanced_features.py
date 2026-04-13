#!/usr/bin/env python3
# mypy: ignore-errors
# -*- coding: utf-8 -*-

"""
Color Palette - Advanced Features Module
Color harmony, accessibility, és weather-specifikus metódusok.
"""

from src.presentation.gui.color_palette.accessibility import (
    calculate_contrast_ratio,
    get_color_metrics,
    simulate_color_blindness,
    suggest_accessible_variants,
)
from src.presentation.gui.color_palette.harmony import generate_harmony
from src.presentation.gui.color_palette.types import (
    ColorBlindnessType,
    ColorHarmony,
    ColorMetrics,
    HSLColor,
)
from src.presentation.gui.color_palette.weather import (
    generate_alert_gradient,
    generate_weather_palette,
)


class AdvancedFeaturesMixin:
    """Advanced features metódusok ColorPalette osztályhoz."""

    # === COLOR HARMONY GENERATION ===

    def generate_harmony_colors(
        self, base_semantic: str, harmony_type: ColorHarmony
    ) -> dict[str, str]:
        """
        Színharmónia generálása base szín alapján.

        Args:
            base_semantic: Base semantic szín neve
            harmony_type: Harmónia típusa

        Returns:
            Harmónia színek {name: hex_color} formátumban
        """
        base_color = self._base_colors.get(base_semantic)
        if not base_color:
            return {}

        harmony_colors = generate_harmony(base_color, harmony_type)
        print(f"🎨 DEBUG: {harmony_type.value} harmony generated from {base_semantic}")
        return harmony_colors

    # === ACCESSIBILITY FUNCTIONS ===

    def calculate_contrast_ratio(self, color1: str | HSLColor, color2: str | HSLColor) -> float:
        """
        WCAG kontraszt arány számítása két szín között.

        Args:
            color1: Első szín
            color2: Második szín

        Returns:
            Kontraszt arány (1.0-21.0)
        """
        return calculate_contrast_ratio(color1, color2, self._hex_to_hsl)

    def get_color_metrics(self, semantic_name: str, variant: str = "base") -> ColorMetrics | None:
        """
        Szín accessibility metrikáinak lekérdezése.

        Args:
            semantic_name: Semantic név
            variant: Variáns neve

        Returns:
            ColorMetrics vagy None ha szín nem található
        """
        color = self.get_color_hsl(semantic_name, variant)
        if not color:
            return None

        return get_color_metrics(color, lambda c1, c2: self.calculate_contrast_ratio(c1, c2))

    def suggest_accessible_variants(
        self, semantic_name: str, target_background: str
    ) -> dict[str, str]:
        """
        Accessible variánsok javaslása adott háttérszínhez.

        Args:
            semantic_name: Semantic név
            target_background: Cél háttérszín hex formátumban

        Returns:
            Javasolt variánsok {variant_name: hex_color}
        """
        base_color = self._base_colors.get(semantic_name)
        if not base_color:
            return {}

        return suggest_accessible_variants(
            base_color,
            target_background,
            lambda c1, c2: self.calculate_contrast_ratio(c1, c2),
            self._hex_to_hsl,
        )

    # === COLOR BLINDNESS SIMULATION ===

    def simulate_color_blindness(
        self,
        semantic_name: str,
        blindness_type: ColorBlindnessType,
        variant: str = "base",
    ) -> str | None:
        """
        Színvakság szimuláció adott színre.

        Args:
            semantic_name: Semantic név
            blindness_type: Színvakság típusa
            variant: Variáns neve

        Returns:
            Szimulált szín hex formátumban
        """
        color = self.get_color_hsl(semantic_name, variant)
        if not color:
            return None

        return simulate_color_blindness(color, blindness_type)

    # === WEATHER-SPECIFIC COLOR METHODS ===

    def generate_weather_palette(self, base_temperature: str) -> dict[str, str]:
        """
        Időjárás-specifikus színpaletta generálása hőmérséklet base színből.

        Args:
            base_temperature: Base hőmérséklet szín hex formátumban

        Returns:
            Weather színpaletta {weather_type: hex_color}
        """
        weather_palette = generate_weather_palette(base_temperature, self._hex_to_hsl)
        print(f"🌦️ DEBUG: Weather palette generated from {base_temperature}")
        return weather_palette

    def generate_alert_gradient(self, base_alert: str, levels: int = 5) -> list[str]:
        """
        Alert szintek gradiens generálása.

        Args:
            base_alert: Base alert szín
            levels: Alert szintek száma

        Returns:
            Alert színek listája (enyhe → súlyos)
        """
        gradient = generate_alert_gradient(base_alert, self._hex_to_hsl, levels)
        print(f"🚨 DEBUG: Alert gradient generated: {levels} levels")
        return gradient
