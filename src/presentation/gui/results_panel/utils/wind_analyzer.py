# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Compatibility wrapper for wind_analyzer.py."""

from __future__ import annotations

from .wind_analyzer_part1 import WindGustsAnalyzerPart1Mixin
from .wind_analyzer_part2 import WindGustsAnalyzerPart2Mixin
from .wind_analyzer_support import *


class WindGustsAnalyzer(WindGustsAnalyzerPart1Mixin, WindGustsAnalyzerPart2Mixin):
    """
    🌪️ Széllökés elemzéséért felelős utility osztály - Dependency Injection Friendly
    🚀 SOLID: Single Responsibility Principle + Dependency Injection
    🌪️ METEOROLÓGIAI STANDARDOK: Beaufort skála alapú kategorizálás
    """
