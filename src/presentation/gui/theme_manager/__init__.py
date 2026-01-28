#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ThemeManager - Professional theme management with PIROS (#C43939) primary color.

This module provides comprehensive theme management for the application,
including dynamic color generation, CSS styling, and accessibility features.

USAGE:
    from src.presentation.gui.theme_manager import get_theme_manager, initialize_theme_system

    # Initialize on startup
    initialize_theme_system(default_theme="light")

    # Get theme manager
    manager = get_theme_manager()

    # Switch themes
    manager.set_theme("dark")

    # Get colors for charts
    colors = manager.get_current_colors()
"""

# Core classes
from .core import ProfessionalThemeManager

# Convenience API
from .convenience_api import (
    get_theme_manager,
    register_widget_for_theming,
    apply_theme_to_app,
    get_current_colors,
    get_weather_colors,
    toggle_app_theme,
    initialize_theme_system,
    get_accessibility_info,
    get_theme_debug_info,
)

# Backward compatibility aliases
ThemeManager = ProfessionalThemeManager
SimplifiedThemeManager = ProfessionalThemeManager

__all__ = [
    # Core
    "ProfessionalThemeManager",
    # Convenience API
    "get_theme_manager",
    "register_widget_for_theming",
    "apply_theme_to_app",
    "get_current_colors",
    "get_weather_colors",
    "toggle_app_theme",
    "initialize_theme_system",
    "get_accessibility_info",
    "get_theme_debug_info",
    # Backward compatibility
    "ThemeManager",
    "SimplifiedThemeManager",
]
