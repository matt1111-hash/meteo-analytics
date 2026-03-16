# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Compatibility wrapper for display_mixin.py."""

from __future__ import annotations

from .display_mixin_part1 import DisplayMixinPart1Mixin
from .display_mixin_part2 import DisplayMixinPart2Mixin
from .display_mixin_support import *


class DisplayMixin(DisplayMixinPart1Mixin, DisplayMixinPart2Mixin):
    """
    Táblázat megjelenítés és UI elemek.
    """

    # Signal
    row_selected = Signal(int)  # kiválasztott sor index
