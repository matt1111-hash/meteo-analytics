# ruff: noqa: F403, F405,noqa: I001
# mypy: ignore-errors
"""Compatibility wrapper for core.py."""

from __future__ import annotations

from .core_part1 import ProfessionalThemeManagerPart1Mixin
from .core_part2 import ProfessionalThemeManagerPart2Mixin
from .core_support import *


class ProfessionalThemeManager(
    ProfessionalThemeManagerPart1Mixin, ProfessionalThemeManagerPart2Mixin, QObject
):
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

    _instance: Optional[ProfessionalThemeManager] = None
