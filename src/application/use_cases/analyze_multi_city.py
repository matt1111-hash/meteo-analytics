# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Compatibility wrapper for analyze_multi_city.py."""

from __future__ import annotations

from .analyze_multi_city_part1 import AnalyzeMultiCityUseCasePart1Mixin
from .analyze_multi_city_part2 import AnalyzeMultiCityUseCasePart2Mixin
from .analyze_multi_city_support import *


class AnalyzeMultiCityUseCase(
    AnalyzeMultiCityUseCasePart1Mixin, AnalyzeMultiCityUseCasePart2Mixin
):
    """Run multi-city analytics by coordinating domain services."""
