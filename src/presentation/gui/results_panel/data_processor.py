# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Compatibility wrapper for data_processor.py."""

from __future__ import annotations

from .data_processor_part1 import DataProcessorPart1Mixin
from .data_processor_part2 import DataProcessorPart2Mixin
from .data_processor_support import *


class DataProcessor(DataProcessorPart1Mixin, DataProcessorPart2Mixin, QObject):
    """
    Adatfeldolgozás és DataFrame konverzió kezelése.

    Felelőségek:
    - DataFrame konverzió API válaszból
    - Wind speed adatok feldolgozása
    - WindyDaysTab adatok előkészítése
    - Adat validálás
    """
