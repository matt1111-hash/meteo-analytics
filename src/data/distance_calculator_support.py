# ruff: noqa: F401,noqa: F401
# mypy: ignore-errors
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global Weather Analyzer - Distance Calculator
🌍 Haversine and Vincenty distance calculations.

Part of the geo_utils refactoring - split into focused modules.
"""

import logging
import math
from typing import Any, Dict, List, Optional, Tuple

from .geo_types import DistanceUnit

logger = logging.getLogger(__name__)


def calculate_cos_2sigma_m(
    cos_sigma: float,
    sin_u1: float,
    sin_u2: float,
    cos2_alpha: float,
) -> float:
    """Calculate cos(2*sigma_m) safely."""
    if cos2_alpha == 0:
        return 0.0
    return cos_sigma - 2 * sin_u1 * sin_u2 / cos2_alpha


def calculate_vincenty_coefficient(flattening: float, cos2_alpha: float) -> float:
    """Calculate Vincenty iteration coefficient."""
    return flattening / 16 * cos2_alpha * (4 + flattening * (4 - 3 * cos2_alpha))


def calculate_vincenty_distance_meters(
    semi_major_axis: float,
    semi_minor_axis: float,
    cos2_alpha: float,
    sin_sigma: float,
    cos_sigma: float,
    cos_2sigma_m: float,
    sigma: float,
) -> float:
    """Calculate final Vincenty distance in meters."""
    u2 = cos2_alpha * (semi_major_axis**2 - semi_minor_axis**2) / (semi_minor_axis**2)
    coefficient_a = 1 + u2 / 16384 * (4096 + u2 * (-768 + u2 * (320 - 175 * u2)))
    coefficient_b = u2 / 1024 * (256 + u2 * (-128 + u2 * (74 - 47 * u2)))
    delta_sigma = (
        coefficient_b
        * sin_sigma
        * (
            cos_2sigma_m
            + coefficient_b
            / 4
            * (
                cos_sigma * (-1 + 2 * cos_2sigma_m**2)
                - coefficient_b
                / 6
                * cos_2sigma_m
                * (-3 + 4 * sin_sigma**2)
                * (-3 + 4 * cos_2sigma_m**2)
            )
        )
    )
    return semi_minor_axis * coefficient_a * (sigma - delta_sigma)


def convert_distance_from_meters(distance_m: float, unit: DistanceUnit) -> float:
    """Convert meters to the requested unit."""
    if unit == DistanceUnit.KILOMETERS:
        return distance_m / 1000
    if unit == DistanceUnit.MILES:
        return distance_m / 1609.344
    if unit == DistanceUnit.NAUTICAL_MILES:
        return distance_m / 1852
    return distance_m
