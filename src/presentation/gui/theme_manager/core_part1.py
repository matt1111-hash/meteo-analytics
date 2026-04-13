# ruff: noqa: F403, F405,noqa: I001
# mypy: ignore-errors
"""Mixin part 1 for ProfessionalThemeManager."""

from __future__ import annotations

from .core_support import *


class ProfessionalThemeManagerPart1Mixin:  # noqa: D101
    def __new__(cls) -> ProfessionalThemeManager:
        """Singleton pattern - professional implementation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):  # noqa: D107
        if hasattr(self, "_initialized"):
            return

        super().__init__()

        # Core state
        self.current_theme = "light"
        self.app = QApplication.instance()

        # 🎨 PIROS (#C43939) TÉMA INTEGRÁCIÓ
        self.color_palette = create_color_palette(preset_name="red", theme_type=ThemeType.LIGHT)
        self.weather_palette = create_weather_palette(
            base_temperature="#C43939", theme_type=ThemeType.LIGHT
        )

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
            from PySide6.QtGui import QGuiApplication, Qt  # noqa: PLC0415

            if self.app:
                self.app.setStyle("Fusion")
                print("✅ Professional Fusion style applied")

            if hasattr(Qt, "ColorScheme") and hasattr(
                QGuiApplication.styleHints(), "setColorScheme"
            ):
                print("✅ Qt6.5+ Professional ColorScheme API available")
                return True
            else:
                print("⚠️ Qt6.5+ ColorScheme API not available - professional fallback")
                return False

        except (ImportError, AttributeError):
            print("⚠️ Qt6 native theming not available - professional fallback")
            return False

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
