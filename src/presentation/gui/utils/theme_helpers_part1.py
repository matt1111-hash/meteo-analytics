# ruff: noqa: F403, F405, I001
# mypy: ignore-errors
"""Compatibility wrapper for theme_helpers_part1.py."""

from __future__ import annotations

from .theme_helpers_part1_support import *
from .theme_helpers_part1_part1 import StyleSheetsPart1Mixin
from .theme_helpers_part1_part2 import StyleSheetsPart2Mixin


class StyleSheets(StyleSheetsPart1Mixin, StyleSheetsPart2Mixin):
    """
    PySide6 stíluslapok - THEMEMANAGER INTEGRÁLT VERZIÓ.

    🎨 VÁLTOZÁSOK V2.1:
    ✅ Dinamikus CSS generálás ThemeManager-rel
    ✅ ColorPalette színek használata
    ✅ Legacy CSS-ek fallback-ként megtartva
    ✅ Widget-specifikus styling support
    ✅ Runtime téma váltás támogatás
    ✅ Dual-API source styling
    """

    _LEGACY_LIGHT_THEME = LEGACY_LIGHT_THEME_CSS
    _LEGACY_DARK_THEME = LEGACY_DARK_THEME_CSS
