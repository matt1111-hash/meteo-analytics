#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ThemeManager Color Helpers - Color-related helper methods.
"""

from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from .core import ProfessionalThemeManager


class ColorHelper:
    """Professional color helper methods."""

    def __init__(self, manager: 'ProfessionalThemeManager'):
        """
        Initialize color helper.

        Args:
            manager: ThemeManager instance
        """
        self._manager = manager

    def get_current_colors(self) -> Dict[str, str]:
        """
        🎯 PROFESSIONAL CHART API - Dynamic colors from ColorPalette.

        Returns:
            Professional color dictionary with all variants
        """
        # Base semantic colors from ColorPalette
        base_colors = {
            "surface": self._manager.color_palette.get_color("surface", "base") or "#ffffff",
            "on_surface": self._manager.color_palette.get_color("primary", "base") or "#000000",
            "surface_variant": self._manager.color_palette.get_color("surface", "light") or "#f5f5f5",
            "on_surface_variant": self._manager.color_palette.get_color("info", "base") or "#6b7280",
            "primary": self._manager.color_palette.get_color("primary", "base") or "#C43939",  # 🎨 PIROS FALLBACK
            "success": self._manager.color_palette.get_color("success", "base") or "#10b981",
            "warning": self._manager.color_palette.get_color("warning", "base") or "#f59e0b",
            "error": self._manager.color_palette.get_color("error", "base") or "#dc2626",
            "info": self._manager.color_palette.get_color("info", "base") or "#6b7280",
        }

        # Professional hover overlay from ColorPalette
        hover_overlay = self._manager.color_palette.get_color("primary", "hover") or base_colors["primary"]

        # Border calculation from ColorPalette
        border_color = self._manager.color_palette.get_color("info", "light") or "#d1d5db"

        # Professional weather colors
        weather_colors = self._get_weather_colors_dict(base_colors)

        # Combine all professional colors
        professional_colors = {
            **base_colors,
            **weather_colors,
            "border": border_color,
            "hover_overlay": hover_overlay,
        }

        return professional_colors

    def _get_weather_colors_dict(self, base_colors: Dict[str, str]) -> Dict[str, str]:
        """Get weather-specific colors dictionary."""
        if not hasattr(self._manager, 'weather_palette'):
            return {}

        return {
            "weather_temperature": self._manager.weather_palette.get_color("weather_temperature", "base") or "#C43939",
            "weather_humidity": self._manager.weather_palette.get_color("weather_humidity", "base") or "#42a5f5",
            "weather_wind": self._manager.weather_palette.get_color("weather_wind", "base") or "#66bb6a",
            "weather_pressure": self._manager.weather_palette.get_color("weather_pressure", "base") or "#ab47bc",
            "weather_precipitation": self._manager.weather_palette.get_color("weather_precipitation", "base") or "#29b6f6",
            "weather_clouds": self._manager.weather_palette.get_color("weather_clouds", "base") or "#bdbdbd",
        }

    def get_weather_colors(self) -> Dict[str, str]:
        """
        🌦️ PROFESSIONAL WEATHER API - Weather-specific colors.

        Returns:
            Weather color dictionary with all variants
        """
        if not hasattr(self._manager, 'weather_palette'):
            return {}

        weather_colors = {}
        weather_types = ["temperature", "humidity", "wind", "pressure", "precipitation", "clouds"]

        for weather_type in weather_types:
            weather_key = f"weather_{weather_type}"
            weather_colors[weather_key] = self._manager.weather_palette.get_color(weather_key, "base") or "#6b7280"

            # Add variants
            for variant in ["light", "dark", "hover", "pressed"]:
                variant_key = f"{weather_key}_{variant}"
                weather_colors[variant_key] = self._manager.weather_palette.get_color(weather_key, variant) or "#6b7280"

        return weather_colors

    def get_semantic_colors(self) -> Dict[str, Dict[str, str]]:
        """
        🎯 PROFESSIONAL SEMANTIC API - All semantic colors with variants.

        Returns:
            Semantic colors with all variants
        """
        semantic_colors = {}
        semantic_types = ["primary", "success", "warning", "error", "info", "surface"]

        for semantic_type in semantic_types:
            semantic_colors[semantic_type] = self._manager.color_palette.get_all_variants(semantic_type)

        return semantic_colors
