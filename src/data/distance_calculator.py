# ruff: noqa: F403,noqa: I001
# mypy: ignore-errors
"""Compatibility wrapper for distance_calculator.py."""

from __future__ import annotations

from .distance_calculator_part1 import DistanceCalculatorPart1Mixin
from .distance_calculator_part2 import DistanceCalculatorPart2Mixin
from .distance_calculator_part3 import DistanceCalculatorPart3Mixin
from .distance_calculator_support import *


class DistanceCalculator(
    DistanceCalculatorPart1Mixin,
    DistanceCalculatorPart2Mixin,
    DistanceCalculatorPart3Mixin,
):
    """
    Haversine and Vincenty distance calculator.

    Great circle distance calculations on Earth's surface:
    - Haversine formula (fast, good accuracy)
    - Vincenty formula (slower, high accuracy)
    - Multiple unit support
    - Batch distance calculations
    """

    # Earth radius constants (meters)
    EARTH_RADIUS_KM = 6371.0
    EARTH_RADIUS_MILES = 3958.8
    EARTH_RADIUS_NAUTICAL_MILES = 3440.1

    # WGS84 ellipsoid constants for Vincenty
    WGS84_A = 6378137.0
    WGS84_B = 6356752.314245
    WGS84_F = 1 / 298.257223563


__all__ = ["DistanceCalculator"]
