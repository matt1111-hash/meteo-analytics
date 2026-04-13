# ruff: noqa: F403, F405,noqa: I001
# mypy: ignore-errors
"""Mixin part 2 for ProfessionalThemeManager."""

from __future__ import annotations

from .core_support import *


class ProfessionalThemeManagerPart2Mixin:  # noqa: D101
    def get_semantic_colors(self) -> Dict[str, Dict[str, str]]:
        """
        🎯 PROFESSIONAL SEMANTIC API - All semantic colors with variants.

        Returns:
            Semantic colors with all variants
        """
        return self._color_helper.get_semantic_colors()

    def generate_css_for_class(self, css_class: str) -> str:
        """
        🎨 PROFESSIONAL CSS GENERATION - Dynamic CSS from ColorPalette.

        Args:
            css_class: CSS class name (e.g., "QPushButton", "QTabWidget", "splitter")

        Returns:
            Professional CSS string with ColorPalette integration
        """
        return self._css_generator.generate_css_for_class(css_class)

    def toggle_theme(self) -> str:
        """Professional theme toggle with ColorPalette sync."""
        new_theme = "dark" if self.current_theme == "light" else "light"
        self.set_theme(new_theme)
        return new_theme

    def save_preferences(self) -> None:
        """Save professional theme preferences."""
        self._preferences.save()

    def save_theme_preferences(self, settings: QSettings) -> None:
        """
        🔄 BACKWARD COMPATIBILITY - save_theme_preferences alias.

        Args:
            settings: QSettings instance
        """
        self._preferences.save_to_settings(settings)

    def load_preferences(self) -> None:
        """Load professional theme preferences."""
        self._preferences.load()

    def create_weather_specific_palette(self, base_temperature_color: str = "#C43939") -> None:
        """
        🌦️ PROFESSIONAL WEATHER SETUP - PIROS (#C43939) BASE TEMPERATURE.

        Args:
            base_temperature_color: Base temperature color (default: #C43939)
        """
        self.weather_palette = create_weather_palette(
            base_temperature=base_temperature_color,
            theme_type=ThemeType.DARK if self.current_theme == "dark" else ThemeType.LIGHT,
        )

        print(f"🌦️ Professional weather palette created with RED base: {base_temperature_color}")

    def get_accessibility_info(self) -> Dict[str, Any]:
        """
        ♿ PROFESSIONAL ACCESSIBILITY - Get accessibility compliance info.

        Returns:
            Accessibility information for current theme
        """
        return self._accessibility.get_info()

    def get_debug_info(self) -> Dict[str, Any]:
        """Professional debug information."""
        debug_info = {
            "current_theme": self.current_theme,
            "qt6_native_available": self._qt6_native_available,
            "professional_themes_available": PROFESSIONAL_THEMES,
            "color_palette_info": self.color_palette.get_debug_info(),
            "css_cache_size": self._css_generator.get_cache_size(),
            "app_available": self.app is not None,
            "primary_color": self.color_palette.get_color("primary", "base"),
        }

        if hasattr(self, "weather_palette"):
            debug_info["weather_palette_info"] = self.weather_palette.get_debug_info()

        return debug_info
