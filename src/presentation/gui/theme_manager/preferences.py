#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mypy: ignore-errors

"""
ThemeManager Preferences - Save/load theme preferences.
"""

from typing import TYPE_CHECKING

from PySide6.QtCore import QSettings

if TYPE_CHECKING:
    from .core import ProfessionalThemeManager


class PreferencesManager:
    """Professional preferences management."""

    def __init__(self, manager: "ProfessionalThemeManager"):
        """
        Initialize preferences manager.

        Args:
            manager: ThemeManager instance
        """
        self._manager = manager

    def save(self) -> None:
        """Save professional theme preferences."""
        settings = QSettings("Weather Analytics", "GlobalWeatherAnalyzer")
        settings.setValue("theme/current", self._manager.current_theme)

        # Save ColorPalette configuration
        palette_config = self._manager.color_palette.export_palette()
        settings.setValue("theme/color_palette", palette_config)

        print(f"💾 Professional theme preferences saved: {self._manager.current_theme}")

    def save_to_settings(self, settings: QSettings) -> None:
        """
        Save preferences to specific QSettings instance.

        Args:
            settings: QSettings instance
        """
        settings.setValue("theme/current", self._manager.current_theme)

        # Save ColorPalette configuration
        palette_config = self._manager.color_palette.export_palette()
        settings.setValue("theme/color_palette", palette_config)

        print(
            f"💾 Professional theme preferences saved via compatibility API: {self._manager.current_theme}"
        )

    def load(self) -> None:
        """Load professional theme preferences."""
        settings = QSettings("Weather Analytics", "GlobalWeatherAnalyzer")
        saved_theme = settings.value("theme/current", "light")

        # Load ColorPalette configuration
        palette_config = settings.value("theme/color_palette", None)
        if palette_config:
            self._manager.color_palette.import_palette(palette_config)

        self._manager.set_theme(saved_theme)
        print(f"📂 Professional theme preferences loaded: {saved_theme}")
