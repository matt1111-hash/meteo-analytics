# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Mixin part 1 for DistanceCalculator."""

from __future__ import annotations

from .distance_calculator_support import *


class DistanceCalculatorPart1Mixin:
    def __init__(self, default_unit: DistanceUnit = DistanceUnit.KILOMETERS):
        """Initialize DistanceCalculator."""
        self.default_unit = default_unit
        self.calculation_count = 0
        logger.debug(f"DistanceCalculator initialized ({default_unit.value})")

    def _get_earth_radius(self, unit: DistanceUnit) -> float:
        """Get Earth radius by unit."""
        radius_map = {
            DistanceUnit.KILOMETERS: self.EARTH_RADIUS_KM,
            DistanceUnit.MILES: self.EARTH_RADIUS_MILES,
            DistanceUnit.NAUTICAL_MILES: self.EARTH_RADIUS_NAUTICAL_MILES,
            DistanceUnit.METERS: self.EARTH_RADIUS_KM * 1000,
        }
        return radius_map[unit]

    def haversine_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float,
        unit: Optional[DistanceUnit] = None,
    ) -> float:
        """
        Haversine formula distance calculation.

        Great circle distance between two points on Earth's surface.
        Fast and accurate enough for most applications (< 0.5% error).
        """
        if unit is None:
            unit = self.default_unit

        # Convert to radians
        lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
        lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)

        # Differences
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        # Haversine formula
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        earth_radius = self._get_earth_radius(unit)
        distance = earth_radius * c

        self.calculation_count += 1
        return distance
