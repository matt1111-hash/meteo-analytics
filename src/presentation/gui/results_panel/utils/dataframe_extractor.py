# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Compatibility wrapper for dataframe_extractor.py."""

from __future__ import annotations

from .dataframe_extractor_part1 import DataFrameExtractorPart1Mixin
from .dataframe_extractor_part2 import DataFrameExtractorPart2Mixin
from .dataframe_extractor_support import *


class DataFrameExtractor(DataFrameExtractorPart1Mixin, DataFrameExtractorPart2Mixin):
    """
    🔥 JAVÍTOTT: Adatok DataFrame-be konvertálásáért felelős utility osztály.
    🎯 API KONZISZTENCIA: Helyes mezőnevek használata
    🌪️ WIND GUSTS TÁMOGATÁS: wind_gusts_10m_max prioritással, windspeed_10m_max fallback-kel
    """
