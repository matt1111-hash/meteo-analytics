# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Compatibility wrapper for category_calculators.py."""

from __future__ import annotations

from .category_calculators_part1 import CategoryCalculatorsPart1Mixin
from .category_calculators_part2 import CategoryCalculatorsPart2Mixin
from .category_calculators_part3 import CategoryCalculatorsPart3Mixin
from .category_calculators_support import *


class CategoryCalculators(
    CategoryCalculatorsPart1Mixin,
    CategoryCalculatorsPart2Mixin,
    CategoryCalculatorsPart3Mixin,
):
    """
    🌡️ Kategória alapú rekord számítások

    Felelős:
    - Hőmérséklet rekordok számítása
    - Csapadék rekordok számítása
    - Szél rekordok számítása
    """
