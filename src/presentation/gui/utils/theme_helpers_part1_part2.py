# ruff: noqa: F401,F403,F405,I001
# mypy: ignore-errors
"""Mixin part 2 for StyleSheets."""

from __future__ import annotations

from .theme_helpers_part1_support import *


class StyleSheetsPart2Mixin:
    @property
    def DARK_THEME(self) -> str:
        """🔄 Backward compatibility - dinamikus dark theme."""
        return self.get_theme_stylesheet(ThemeType.DARK)
