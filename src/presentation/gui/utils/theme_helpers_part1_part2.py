# ruff: noqa: F403, F405
# mypy: ignore-errors
"""Mixin part 2 for StyleSheets."""

from __future__ import annotations

from .theme_helpers_part1_support import *


class StyleSheetsPart2Mixin:  # noqa: D101
    @property
    def DARK_THEME(self) -> str:
        """🔄 Backward compatibility - dinamikus dark theme."""
        return self.get_theme_stylesheet(ThemeType.DARK)
