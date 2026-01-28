#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ThemeManager Convenience API - Module-level convenience functions.
"""

from typing import Any, Dict

from PySide6.QtWidgets import QWidget


def get_theme_manager():
    """Get ThemeManager singleton (imported in __init__ to avoid circular import)."""
    from .core import ProfessionalThemeManager
    return ProfessionalThemeManager()


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


def initialize_theme_system(
    default_theme: str = "light",
    load_saved_preferences: bool = True,
    create_weather_palette: bool = True
) -> None:
    """
    🚀 PROFESSIONAL SETUP - PIROS (#C43939) TÉMA RENDSZER INICIALIZÁLÁSA.

    Args:
        default_theme: Default theme if no saved preferences
        load_saved_preferences: Load saved theme preferences
        create_weather_palette: Create weather-specific color palette
    """
    manager = get_theme_manager()

    if create_weather_palette:
        manager.create_weather_specific_palette(base_temperature_color="#C43939")

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
