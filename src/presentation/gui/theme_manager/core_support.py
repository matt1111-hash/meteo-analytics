# ruff: noqa: F401,noqa: F401
# mypy: ignore-errors
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ThemeManager Core - ProfessionalThemeManager main class.
🎨 PIROS (#C43939) PRIMARY TÉMA - Core initialization and theme switching.
"""

from typing import Any, Optional

from PySide6.QtCore import QObject, QSettings, Signal
from PySide6.QtWidgets import QApplication
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

from .accessibility import AccessibilityHelper
from .color_helpers import ColorHelper
from .css_generator import CSSGenerator
from .preferences import PreferencesManager
from .theme_appliers import (
    apply_color_palette_theme,
    apply_qdarktheme_theme,
    apply_qt6_native_theme,
)
