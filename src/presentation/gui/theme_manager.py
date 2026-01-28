#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global Weather Analyzer - PROFESSIONAL ThemeManager - PIROS (#C43939) TÉMA
🎨 KRITIKUS JAVÍTÁS: Piros (#C43939) primary színnel - UNDORÍTÓ LILA ELTÁVOLÍTVA!

PROFESSZIONÁLIS FUNKCIÓK:
✅ ColorPalette integráció - HSL dinamikus színkezelés
✅ Native Qt6.5+ dark mode support + fallback
✅ Semantic color mapping - primary, success, warning, error, info
✅ Dynamic color variant generation - light, dark, hover, pressed
✅ Material Design color generator support
✅ Weather-specific color schemes
✅ WCAG accessibility compliance
✅ CSS class generation for complex widgets
✅ Real-time theme switching without restart
✅ Cross-platform consistency (Linux, Windows, macOS)
✅ 🎨 PIROS (#C43939) PRIMARY TÉMA - GYÖNYÖRŰ MEGJELENÍTÉS!

ARCHITEKTÚRA:
- SimplifiedThemeManager → ProfessionalThemeManager
- MockColorScheme → ColorPalette integration
- Static colors → Dynamic HSL color generation
- Manual CSS → Automated CSS class generation
- 🎨 PIROS (#C43939) alapértelmezett primary szín
"""

from typing import Any, Dict, Optional

from PySide6.QtCore import QObject, QSettings, Signal
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication, QWidget

# ColorPalette integration - ABSOLUTE IMPORTS
from src.presentation.gui.color_palette import (
    ColorPalette,
    create_color_palette,
    create_weather_palette,
)

# Import ThemeType from gui.types (breaks circular dependency)
from src.presentation.gui.types import ThemeType

# PROFESSIONAL THEME LIBRARY - opcionális
try:
    import qdarktheme
    PROFESSIONAL_THEMES = True
    print("✅ Professional theme engine: qdarktheme available")
except ImportError:
    PROFESSIONAL_THEMES = False
    print("⚠️ Basic Qt themes only (install: pip install qdarktheme)")


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
    - 🎨 PIROS (#C43939) PRIMARY TÉMA TÁMOGATÁS!
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

        # 🎨 KRITIKUS JAVÍTÁS: PIROS (#C43939) TÉMA INTEGRÁCIÓ
        self.color_palette = create_color_palette(preset_name="red", theme_type=ThemeType.LIGHT)
        self.weather_palette = create_weather_palette(base_temperature="#C43939", theme_type=ThemeType.LIGHT)

        # Qt6.5+ native dark mode detection
        self._setup_qt6_professional_theming()

        # CSS class cache for performance
        self._css_class_cache: Dict[str, str] = {}

        self._initialized = True
        print("✅ ProfessionalThemeManager initialized with RED (#C43939) theme")

    def _setup_qt6_professional_theming(self) -> None:
        """Professional Qt6.5+ native dark mode setup."""
        try:
            # Qt6.5+ ColorScheme API detection
            from PySide6.QtGui import QGuiApplication, Qt

            if hasattr(Qt, 'ColorScheme') and hasattr(QGuiApplication.styleHints(), 'setColorScheme'):
                print("✅ Qt6.5+ Professional ColorScheme API available")
                self._qt6_native_available = True
            else:
                print("⚠️ Qt6.5+ ColorScheme API not available - professional fallback")
                self._qt6_native_available = False

        except (ImportError, AttributeError):
            print("⚠️ Qt6 native theming not available - professional fallback")
            self._qt6_native_available = False

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

        # 🎨 KRITIKUS JAVÍTÁS: PIROS (#C43939) TÉMA ColorPalette update
        theme_type = ThemeType.DARK if theme_name == "dark" else ThemeType.LIGHT
        self.color_palette.set_theme_type(theme_type)
        self.weather_palette.set_theme_type(theme_type)

        # Clear CSS cache for regeneration
        self._css_class_cache.clear()

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
                qdarktheme.setup_theme(theme_name)
                self._enhance_with_color_palette()
                print(f"✅ Professional qdarktheme applied: {theme_name}")
                return True
            except Exception as e:
                print(f"⚠️ Professional qdarktheme failed: {e}, trying Qt6 native...")

        # PRIORITY 2: Qt6.5+ native ColorScheme
        if self._qt6_native_available:
            try:
                from PySide6.QtGui import QGuiApplication, Qt

                if theme_name == "dark":
                    QGuiApplication.styleHints().setColorScheme(Qt.ColorScheme.Dark)
                else:
                    QGuiApplication.styleHints().setColorScheme(Qt.ColorScheme.Light)

                self._enhance_with_color_palette()
                print(f"✅ Qt6.5+ native ColorScheme applied: {theme_name}")
                return True
            except Exception as e:
                print(f"⚠️ Qt6 native failed: {e}, trying ColorPalette fallback...")

        # PRIORITY 3: Professional ColorPalette fallback
        try:
            self._apply_color_palette_theme(theme_name)
            print(f"✅ Professional ColorPalette RED (#C43939) theme applied: {theme_name}")
            return True
        except Exception as e:
            print(f"❌ All professional theme methods failed: {e}")
            return False

    def _enhance_with_color_palette(self) -> None:
        """Enhance Qt theming with ColorPalette colors."""
        if not self.app:
            return

        palette = self.app.palette()
        colors = self.get_current_colors()

        # 🎨 KRITIKUS JAVÍTÁS: PIROS (#C43939) TÉMA enhancement
        palette.setColor(QPalette.ColorRole.Highlight, QColor(colors["primary"]))
        palette.setColor(QPalette.ColorRole.Link, QColor(colors["info"]))

        # Weather-specific enhancements
        if hasattr(self, 'weather_palette'):
            weather_colors = self.weather_palette.get_all_variants("primary")
            if "hover" in weather_colors:
                hover_color = QColor(weather_colors["hover"])
                palette.setColor(QPalette.ColorRole.Highlight, hover_color)

        self.app.setPalette(palette)

    def _apply_color_palette_theme(self, theme_name: str) -> None:
        """Professional ColorPalette-based theme application."""
        if not self.app:
            raise Exception("QApplication not available for professional theming")

        palette = QPalette()
        colors = self.get_current_colors()

        # Professional color mapping
        palette.setColor(QPalette.ColorRole.Window, QColor(colors["surface"]))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(colors["on_surface"]))
        palette.setColor(QPalette.ColorRole.Base, QColor(colors["surface_variant"]))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(colors["surface_variant"]))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(colors["surface"]))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(colors["on_surface"]))
        palette.setColor(QPalette.ColorRole.Text, QColor(colors["on_surface"]))
        palette.setColor(QPalette.ColorRole.Button, QColor(colors["surface_variant"]))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(colors["on_surface"]))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(colors["error"]))
        palette.setColor(QPalette.ColorRole.Link, QColor(colors["info"]))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(colors["primary"]))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(colors["on_surface"]))

        # Professional disabled state
        disabled_group = QPalette.ColorGroup.Disabled
        disabled_text = QColor(colors["on_surface"])
        disabled_text.setAlpha(100)  # 40% opacity
        palette.setColor(disabled_group, QPalette.ColorRole.WindowText, disabled_text)
        palette.setColor(disabled_group, QPalette.ColorRole.Text, disabled_text)
        palette.setColor(disabled_group, QPalette.ColorRole.ButtonText, disabled_text)

        self.app.setPalette(palette)

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
        # Base semantic colors from ColorPalette
        base_colors = {
            "surface": self.color_palette.get_color("surface", "base") or "#ffffff",
            "on_surface": self.color_palette.get_color("primary", "base") or "#000000",
            "surface_variant": self.color_palette.get_color("surface", "light") or "#f5f5f5",
            "on_surface_variant": self.color_palette.get_color("info", "base") or "#6b7280",
            "primary": self.color_palette.get_color("primary", "base") or "#C43939",  # 🎨 PIROS FALLBACK
            "success": self.color_palette.get_color("success", "base") or "#10b981",
            "warning": self.color_palette.get_color("warning", "base") or "#f59e0b",
            "error": self.color_palette.get_color("error", "base") or "#dc2626",
            "info": self.color_palette.get_color("info", "base") or "#6b7280",
        }

        # Professional hover overlay from ColorPalette
        hover_overlay = self.color_palette.get_color("primary", "hover") or base_colors["primary"]

        # Border calculation from ColorPalette
        border_color = self.color_palette.get_color("info", "light") or "#d1d5db"

        # Professional weather colors
        weather_colors = {}
        if hasattr(self, 'weather_palette'):
            weather_colors = {
                "weather_temperature": self.weather_palette.get_color("weather_temperature", "base") or "#C43939",  # 🎨 PIROS
                "weather_humidity": self.weather_palette.get_color("weather_humidity", "base") or "#42a5f5",
                "weather_wind": self.weather_palette.get_color("weather_wind", "base") or "#66bb6a",
                "weather_pressure": self.weather_palette.get_color("weather_pressure", "base") or "#ab47bc",
                "weather_precipitation": self.weather_palette.get_color("weather_precipitation", "base") or "#29b6f6",
                "weather_clouds": self.weather_palette.get_color("weather_clouds", "base") or "#bdbdbd",
            }

        # Combine all professional colors
        professional_colors = {
            **base_colors,
            **weather_colors,
            "border": border_color,
            "hover_overlay": hover_overlay,
        }

        return professional_colors

    def generate_css_for_class(self, css_class: str) -> str:
        """
        🎨 PROFESSIONAL CSS GENERATION - Dynamic CSS from ColorPalette.
        
        Args:
            css_class: CSS class name (e.g., "QPushButton", "QTabWidget", "splitter")
            
        Returns:
            Professional CSS string with ColorPalette integration
        """
        # Check cache first
        cache_key = f"{css_class}_{self.current_theme}"
        if cache_key in self._css_class_cache:
            return self._css_class_cache[cache_key]

        colors = self.get_current_colors()

        # Professional CSS templates
        css_templates = {
            "QPushButton": f"""
                QPushButton {{
                    background-color: {colors['surface_variant']};
                    color: {colors['on_surface']};
                    border: 1px solid {colors['border']};
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: {colors['hover_overlay']};
                }}
                QPushButton:pressed {{
                    background-color: {colors['primary']};
                    color: {colors['surface']};
                }}
                QPushButton:disabled {{
                    background-color: {colors['surface_variant']};
                    color: {colors['info']};
                    opacity: 0.6;
                }}
            """,

            "QTabWidget": f"""
                QTabWidget::pane {{
                    background-color: {colors['surface']};
                    border: 1px solid {colors['border']};
                    border-radius: 4px;
                }}
                QTabWidget::tab-bar {{
                    left: 5px;
                }}
                QTabBar::tab {{
                    background-color: {colors['surface_variant']};
                    color: {colors['on_surface']};
                    border: 1px solid {colors['border']};
                    border-bottom-color: transparent;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                    padding: 8px 16px;
                    margin-right: 2px;
                }}
                QTabBar::tab:selected {{
                    background-color: {colors['primary']};
                    color: {colors['surface']};
                }}
                QTabBar::tab:hover {{
                    background-color: {colors['hover_overlay']};
                }}
            """,

            "splitter": f"""
                QSplitter::handle {{
                    background-color: {colors['border']};
                    border: 1px solid {colors['surface_variant']};
                }}
                QSplitter::handle:horizontal {{
                    width: 3px;
                    margin: 0 2px;
                }}
                QSplitter::handle:vertical {{
                    height: 3px;
                    margin: 2px 0;
                }}
                QSplitter::handle:hover {{
                    background-color: {colors['primary']};
                }}
            """,

            "QScrollBar": f"""
                QScrollBar:vertical {{
                    background-color: {colors['surface_variant']};
                    width: 12px;
                    border-radius: 6px;
                }}
                QScrollBar::handle:vertical {{
                    background-color: {colors['info']};
                    border-radius: 6px;
                    min-height: 20px;
                }}
                QScrollBar::handle:vertical:hover {{
                    background-color: {colors['primary']};
                }}
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                    height: 0px;
                }}
            """,

            "analytics_panel": f"""
                QWidget#analytics_panel {{
                    background-color: {colors['surface']};
                    border: 1px solid {colors['border']};
                    border-radius: 8px;
                }}
                QLabel#analytics_title {{
                    color: {colors['on_surface']};
                    font-size: 16px;
                    font-weight: 600;
                }}
                QGroupBox#analytics_group {{
                    color: {colors['on_surface']};
                    border: 2px solid {colors['border']};
                    border-radius: 6px;
                    margin-top: 12px;
                    padding-top: 8px;
                }}
                QGroupBox#analytics_group::title {{
                    color: {colors['primary']};
                    font-weight: 600;
                    subcontrol-origin: margin;
                    left: 8px;
                    padding: 0 4px 0 4px;
                }}
            """,
        }

        # Generate CSS
        css = css_templates.get(css_class, "")

        # Cache the result
        self._css_class_cache[cache_key] = css

        return css

    def get_weather_colors(self) -> Dict[str, str]:
        """
        🌦️ PROFESSIONAL WEATHER API - Weather-specific colors.
        
        Returns:
            Weather color dictionary with all variants
        """
        if not hasattr(self, 'weather_palette'):
            return {}

        weather_colors = {}
        weather_types = ["temperature", "humidity", "wind", "pressure", "precipitation", "clouds"]

        for weather_type in weather_types:
            weather_key = f"weather_{weather_type}"
            weather_colors[weather_key] = self.weather_palette.get_color(weather_key, "base") or "#6b7280"

            # Add variants
            for variant in ["light", "dark", "hover", "pressed"]:
                variant_key = f"{weather_key}_{variant}"
                weather_colors[variant_key] = self.weather_palette.get_color(weather_key, variant) or "#6b7280"

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
            semantic_colors[semantic_type] = self.color_palette.get_all_variants(semantic_type)

        return semantic_colors

    def toggle_theme(self) -> str:
        """Professional theme toggle with ColorPalette sync."""
        new_theme = "dark" if self.current_theme == "light" else "light"
        self.set_theme(new_theme)
        return new_theme

    def save_preferences(self) -> None:
        """Save professional theme preferences."""
        settings = QSettings("Weather Analytics", "GlobalWeatherAnalyzer")
        settings.setValue("theme/current", self.current_theme)

        # Save ColorPalette configuration
        palette_config = self.color_palette.export_palette()
        settings.setValue("theme/color_palette", palette_config)

        print(f"💾 Professional theme preferences saved: {self.current_theme}")

    def save_theme_preferences(self, settings: QSettings) -> None:
        """
        🔄 BACKWARD COMPATIBILITY - save_theme_preferences alias.
        
        Args:
            settings: QSettings instance
        """
        settings.setValue("theme/current", self.current_theme)

        # Save ColorPalette configuration
        palette_config = self.color_palette.export_palette()
        settings.setValue("theme/color_palette", palette_config)

        print(f"💾 Professional theme preferences saved via compatibility API: {self.current_theme}")

    def load_preferences(self) -> None:
        """Load professional theme preferences."""
        settings = QSettings("Weather Analytics", "GlobalWeatherAnalyzer")
        saved_theme = settings.value("theme/current", "light")

        # Load ColorPalette configuration
        palette_config = settings.value("theme/color_palette", None)
        if palette_config:
            self.color_palette.import_palette(palette_config)

        self.set_theme(saved_theme)
        print(f"📂 Professional theme preferences loaded: {saved_theme}")

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
        colors = self.get_current_colors()

        accessibility_info = {
            "theme": self.current_theme,
            "contrast_ratios": {},
            "wcag_compliance": {},
            "recommendations": []
        }

        # Check contrast ratios
        if hasattr(self.color_palette, 'calculate_contrast_ratio'):
            try:
                primary_surface_contrast = self.color_palette.calculate_contrast_ratio(
                    colors["primary"], colors["surface"]
                )
                text_surface_contrast = self.color_palette.calculate_contrast_ratio(
                    colors["on_surface"], colors["surface"]
                )

                accessibility_info["contrast_ratios"] = {
                    "primary_on_surface": primary_surface_contrast,
                    "text_on_surface": text_surface_contrast
                }

                # WCAG compliance
                accessibility_info["wcag_compliance"] = {
                    "primary_aa": primary_surface_contrast >= 4.5,
                    "primary_aaa": primary_surface_contrast >= 7.0,
                    "text_aa": text_surface_contrast >= 4.5,
                    "text_aaa": text_surface_contrast >= 7.0
                }

                # Recommendations
                if primary_surface_contrast < 4.5:
                    accessibility_info["recommendations"].append(
                        "Primary color contrast below WCAG AA standard"
                    )
                if text_surface_contrast < 4.5:
                    accessibility_info["recommendations"].append(
                        "Text color contrast below WCAG AA standard"
                    )

            except Exception as e:
                accessibility_info["error"] = f"Accessibility check failed: {e}"

        return accessibility_info

    def get_debug_info(self) -> Dict[str, Any]:
        """Professional debug information."""
        debug_info = {
            "current_theme": self.current_theme,
            "qt6_native_available": self._qt6_native_available,
            "professional_themes_available": PROFESSIONAL_THEMES,
            "color_palette_info": self.color_palette.get_debug_info(),
            "css_cache_size": len(self._css_class_cache),
            "app_available": self.app is not None,
            "primary_color": self.color_palette.get_color("primary", "base"),  # 🎨 PIROS DEBUG
        }

        if hasattr(self, 'weather_palette'):
            debug_info["weather_palette_info"] = self.weather_palette.get_debug_info()

        return debug_info


# === PROFESSIONAL SINGLETON ACCESS ===

def get_theme_manager() -> ProfessionalThemeManager:
    """Professional ThemeManager singleton access."""
    return ProfessionalThemeManager()


# === BACKWARD COMPATIBILITY ===

# Legacy class alias
SimplifiedThemeManager = ProfessionalThemeManager
ThemeManager = ProfessionalThemeManager


# === PROFESSIONAL CONVENIENCE API ===

def register_widget_for_theming(widget: QWidget, style_class: str) -> None:
    """
    🎨 PROFESSIONAL WIDGET REGISTRATION - Apply CSS class to widget.
    
    Args:
        widget: Widget to apply styling to
        style_class: CSS class name
    """
    manager = get_theme_manager()
    css = manager.generate_css_for_class(style_class)
    if css:
        widget.setStyleSheet(css)
        print(f"🎨 Professional styling applied to {widget.__class__.__name__}: {style_class}")


def apply_theme_to_app(theme_name: str) -> bool:
    """🎯 PROFESSIONAL THEME API - Apply theme to entire application."""
    return get_theme_manager().set_theme(theme_name)


def get_current_colors() -> Dict[str, str]:
    """🎯 PROFESSIONAL CHART API - Get current color scheme."""
    return get_theme_manager().get_current_colors()


def get_weather_colors() -> Dict[str, str]:
    """🌦️ PROFESSIONAL WEATHER API - Get weather-specific colors."""
    return get_theme_manager().get_weather_colors()


def toggle_app_theme() -> str:
    """🎯 PROFESSIONAL TOGGLE API - Toggle between light and dark theme."""
    return get_theme_manager().toggle_theme()


def initialize_theme_system(default_theme: str = "light",
                          load_saved_preferences: bool = True,
                          create_weather_palette: bool = True) -> None:
    """
    🚀 PROFESSIONAL SETUP - PIROS (#C43939) TÉMA RENDSZER INICIALIZÁLÁSA.
    
    Args:
        default_theme: Default theme if no saved preferences
        load_saved_preferences: Load saved theme preferences
        create_weather_palette: Create weather-specific color palette
    """
    manager = get_theme_manager()

    if create_weather_palette:
        manager.create_weather_specific_palette(base_temperature_color="#C43939")  # 🎨 PIROS BASE

    if load_saved_preferences:
        manager.load_preferences()
    else:
        manager.set_theme(default_theme)

    print(f"🎨 Professional RED (#C43939) theme system initialized: {manager.get_current_theme()}")
    print(f"🌦️ Weather palette: {'enabled' if create_weather_palette else 'disabled'}")


def get_accessibility_info() -> Dict[str, Any]:
    """♿ PROFESSIONAL ACCESSIBILITY API - Get accessibility information."""
    return get_theme_manager().get_accessibility_info()


def get_theme_debug_info() -> Dict[str, Any]:
    """🔧 PROFESSIONAL DEBUG API - Get debug information."""
    return get_theme_manager().get_debug_info()
