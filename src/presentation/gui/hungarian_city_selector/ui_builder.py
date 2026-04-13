# ruff: noqa: F403,noqa: I001
# mypy: ignore-errors
"""Compatibility wrapper for ui_builder.py."""

from __future__ import annotations

from .ui_builder_part1 import HungarianCityUIBuilderPart1Mixin
from .ui_builder_part2 import HungarianCityUIBuilderPart2Mixin
from .ui_builder_support import *


class HungarianCityUIBuilder(HungarianCityUIBuilderPart1Mixin, HungarianCityUIBuilderPart2Mixin):
    """
    UI komponens építő osztály.
    """
