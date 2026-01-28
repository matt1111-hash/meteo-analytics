#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ThemeManager Core - ProfessionalThemeManager main class.
🎨 PIROS (#C43939) PRIMARY TÉMA - Core initialization and theme switching.
"""

from typing import Any, Dict, Optional

from PySide6.QtCore import QObject, QSettings, Signal
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication, QWidget

from src.presentation.gui.color_palette import (
    ColorPalette,
    create_color_palette,
    create_weather_palette,
)
from src.presentation.gui.types import ThemeType

# Professional theme library - optional
try:
    import qdarktheme
    PROFESSIONAL_THEMES = True
except ImportError:
    PROFESSIONAL_THEMES = False

from .theme_appliers import apply_qdarktheme_theme, apply_qt6_native_theme, apply_color_palette_theme
from .css_generator import CSSGenerator
from .color_helpers import ColorHelper
from .accessibility import AccessibilityHelper
from .preferences import PreferencesManager


class ProfessionalThemeManager(QObject):
    """
    🎨 PROFESSZIONÁLIS ThemeManager - PIROS (#C43939) TÉMA VERZIÓ.

    PROFESSIONAL FEATURES:
    - Dynamic HSL color generation via ColorPalette
    - Native Qt6.5+ dark mode with fallback
    - Material Design color variants
    - Weather-specific color schemes
    - CSS class generation for complex widgets
    - Real-time theme switching
    - Cross-platform consistency
    - WCAG accessibility compliance
    """

    # Professional Signals
    theme_changed = Signal(str)  # theme_name: "light" | "dark"
    color_scheme_updated = Signal(object)  # ColorPalette instance

    _instance: Optional['ProfessionalThemeManager'] = None

    def __new__(cls) -> 'ProfessionalThemeManager':
        """Singleton pattern - professional implementation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized'):
            return

        super().__init__()

        # Core state
        self.current_theme = "light"
        self.app = QApplication.instance()

        # 🎨 PIROS (#C43939) TÉMA INTEGRÁCIÓ
        self.color_palette = create_color_palette(preset_name="red", theme_type=ThemeType.LIGHT)
        self.weather_palette = create_weather_palette(base_temperature="#C43939", theme_type=ThemeType.LIGHT)

        # Qt6.5+ native dark mode detection
        self._qt6_native_available = self._setup_qt6_professional_theming()

        # Helper components
        self._css_generator = CSSGenerator(self)
        self._color_helper = ColorHelper(self)
        self._accessibility = AccessibilityHelper(self)
        self._preferences = PreferencesManager(self)

        self._initialized = True
        print("✅ ProfessionalThemeManager initialized with RED (#C43939) theme")

    def _setup_qt6_professional_theming(self) -> bool:
        """Professional Qt6.5+ native dark mode setup."""
        try:
            from PySide6.QtGui import QGuiApplication, Qt

            if hasattr(Qt, 'ColorScheme') and hasattr(QGuiApplication.styleHints(), 'setColorScheme'):
                print("✅ Qt6.5+ Professional ColorScheme API available")
                return True
            else:
                print("⚠️ Qt6.5+ ColorScheme API not available - professional fallback")
                return False

        except (ImportError, AttributeError):
            print("⚠️ Qt6 native theming not available - professional fallback")
            return False

        # Professional Fusion style - cross-platform consistency
        if self.app:
            self.app.setStyle('Fusion')
            print("✅ Professional Fusion style applied")

    def set_theme(self, theme_name: str) -> bool:
        """
        Professional theme switching with ColorPalette integration.

        Args:
            theme_name: "light" vagy "dark"

        Returns:
            Professional theme applied successfully
        """
        if theme_name not in ["light", "dark"]:
            print(f"❌ Invalid theme: {theme_name}. Professional themes: 'light' or 'dark'")
            return False

        old_theme = self.current_theme
        self.current_theme = theme_name

        print(f"🎨 Professional theme changing: {old_theme} → {theme_name}")

        # Update ColorPalette theme type
        theme_type = ThemeType.DARK if theme_name == "dark" else ThemeType.LIGHT
        self.color_palette.set_theme_type(theme_type)
        self.weather_palette.set_theme_type(theme_type)

        # Clear CSS cache for regeneration
        self._css_generator.clear_cache()

        success = self._apply_professional_theme(theme_name)

        if success:
            self.theme_changed.emit(theme_name)
            self.color_scheme_updated.emit(self.color_palette)
            print(f"✅ Professional RED (#C43939) theme successfully applied: {theme_name}")
        else:
            # Professional rollback
            self.current_theme = old_theme
            old_theme_type = ThemeType.DARK if old_theme == "dark" else ThemeType.LIGHT
            self.color_palette.set_theme_type(old_theme_type)
            self.weather_palette.set_theme_type(old_theme_type)
            print(f"❌ Professional theme failed, rolled back to: {old_theme}")

        return success

    def _apply_professional_theme(self, theme_name: str) -> bool:
        """Professional theme application with multiple fallbacks."""

        # PRIORITY 1: Professional qdarktheme
        if PROFESSIONAL_THEMES:
            try:
                apply_qdarktheme_theme(theme_name, self)
                print(f"✅ Professional qdarktheme applied: {theme_name}")
                return True
            except Exception as e:
                print(f"⚠️ Professional qdarktheme failed: {e}, trying Qt6 native...")

        # PRIORITY 2: Qt6.5+ native ColorScheme
        if self._qt6_native_available:
            try:
                apply_qt6_native_theme(theme_name, self)
                print(f"✅ Qt6.5+ native ColorScheme applied: {theme_name}")
                return True
            except Exception as e:
                print(f"⚠️ Qt6 native failed: {e}, trying ColorPalette fallback...")

        # PRIORITY 3: Professional ColorPalette fallback
        try:
            apply_color_palette_theme(theme_name, self)
            print(f"✅ Professional ColorPalette RED (#C43939) theme applied: {theme_name}")
            return True
        except Exception as e:
            print(f"❌ All professional theme methods failed: {e}")
            return False

    def get_current_theme(self) -> str:
        """Current professional theme name."""
        return self.current_theme

    def get_color_scheme(self) -> ColorPalette:
        """
        🎨 PROFESSIONAL API - ColorPalette objektum visszaadása.

        Returns:
            ColorPalette instance with full professional capabilities
        """
        return self.color_palette

    def get_current_colors(self) -> Dict[str, str]:
        """
        🎯 PROFESSIONAL CHART API - Dynamic colors from ColorPalette.

        Returns:
            Professional color dictionary with all variants
        """
        return self._color_helper.get_current_colors()

    def get_weather_colors(self) -> Dict[str, str]:
        """
        🌦️ PROFESSIONAL WEATHER API - Weather-specific colors.

        Returns:
            Weather color dictionary with all variants
        """
        return self._color_helper.get_weather_colors()

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
            theme_type=ThemeType.DARK if self.current_theme == "dark" else ThemeType.LIGHT
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

        if hasattr(self, 'weather_palette'):
            debug_info["weather_palette_info"] = self.weather_palette.get_debug_info()

        return debug_info
