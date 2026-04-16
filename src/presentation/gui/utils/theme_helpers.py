# ruff: noqa: F403,noqa: I001
# mypy: ignore-errors
"""Merged theme_helpers.py."""

from __future__ import annotations

from .theme_helpers_part1 import StyleSheetsPart1Mixin, StyleSheetsPart2Mixin
from .theme_helpers_part1_support import LEGACY_DARK_THEME_CSS, LEGACY_LIGHT_THEME_CSS
from .theme_helpers_part2 import log_theme_change, log_wind_gusts_event
from .theme_helpers_support import *


class StyleSheets(StyleSheetsPart1Mixin, StyleSheetsPart2Mixin):
    """
    PySide6 stylesheets - ThemeManager integrated version.

    Features:
    - Dynamic CSS generation via ThemeManager
    - ColorPalette support
    - Legacy CSS fallback
    - Widget-specific styling support
    - Runtime theme switching
    - Dual-API source styling
    """

    _LEGACY_LIGHT_THEME = LEGACY_LIGHT_THEME_CSS
    _LEGACY_DARK_THEME = LEGACY_DARK_THEME_CSS


__all__ = [
    "StyleSheets",
    "log_theme_change",
    "log_wind_gusts_event",
]
