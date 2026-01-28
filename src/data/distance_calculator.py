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


class DistanceCalculator:
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
            DistanceUnit.METERS: self.EARTH_RADIUS_KM * 1000
        }
        return radius_map[unit]

    def haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float,
                          unit: Optional[DistanceUnit] = None) -> float:
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
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        earth_radius = self._get_earth_radius(unit)
        distance = earth_radius * c

        self.calculation_count += 1
        return distance

    def vincenty_distance(self, lat1: float, lon1: float, lat2: float, lon2: float,
                         unit: Optional[DistanceUnit] = None) -> float:
        """
        Vincenty formula distance calculation.

        High accuracy distance calculation using WGS84 ellipsoid.
        Slower than Haversine, but higher accuracy (< 0.01% error).
        """
        if unit is None:
            unit = self.default_unit

        # Convert to radians
        lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
        lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)

        # Longitude difference
        L = lon2_rad - lon1_rad

        # Auxiliary values
        U1 = math.atan((1 - self.WGS84_F) * math.tan(lat1_rad))
        U2 = math.atan((1 - self.WGS84_F) * math.tan(lat2_rad))

        sin_U1, cos_U1 = math.sin(U1), math.cos(U1)
        sin_U2, cos_U2 = math.sin(U2), math.cos(U2)

        # Iterative calculation
        lambda_val = L
        lambda_prev = 0
        iteration_limit = 100
        iteration = 0

        while abs(lambda_val - lambda_prev) > 1e-12 and iteration < iteration_limit:
            sin_lambda = math.sin(lambda_val)
            cos_lambda = math.cos(lambda_val)

            sin_sigma = math.sqrt((cos_U2 * sin_lambda) ** 2 +
                           (cos_U1 * sin_U2 - sin_U1 * cos_U2 * cos_lambda) ** 2)

            if sin_sigma == 0:
                return 0

            cos_sigma = sin_U1 * sin_U2 + cos_U1 * cos_U2 * cos_lambda
            sigma = math.atan2(sin_sigma, cos_sigma)

            sin_alpha = cos_U1 * cos_U2 * sin_lambda / sin_sigma
            cos2_alpha = 1 - sin_alpha ** 2

            if cos2_alpha == 0:
                cos_2sigma_m = 0
            else:
                cos_2sigma_m = cos_sigma - 2 * sin_U1 * sin_U2 / cos2_alpha

            C = self.WGS84_F / 16 * cos2_alpha * (4 + self.WGS84_F * (4 - 3 * cos2_alpha))

            lambda_prev = lambda_val
            lambda_val = L + (1 - C) * self.WGS84_F * sin_alpha * \
                        (sigma + C * sin_sigma * (cos_2sigma_m + C * cos_sigma *
                        (-1 + 2 * cos_2sigma_m ** 2)))

            iteration += 1

        if iteration >= iteration_limit:
            logger.warning("Vincenty iteration failed, Haversine fallback")
            return self.haversine_distance(lat1, lon1, lat2, lon2, unit)

        # Calculate distance
        u2 = cos2_alpha * (self.WGS84_A ** 2 - self.WGS84_B ** 2) / (self.WGS84_B ** 2)
        A = 1 + u2 / 16384 * (4096 + u2 * (-768 + u2 * (320 - 175 * u2)))
        B = u2 / 1024 * (256 + u2 * (-128 + u2 * (74 - 47 * u2)))

        delta_sigma = B * sin_sigma * (cos_2sigma_m + B / 4 *
                     (cos_sigma * (-1 + 2 * cos_2sigma_m ** 2) -
                     B / 6 * cos_2sigma_m * (-3 + 4 * sin_sigma ** 2) *
                     (-3 + 4 * cos_2sigma_m ** 2)))

        distance_m = self.WGS84_B * A * (sigma - delta_sigma)

        # Convert to requested unit
        if unit == DistanceUnit.KILOMETERS:
            distance = distance_m / 1000
        elif unit == DistanceUnit.MILES:
            distance = distance_m / 1609.344
        elif unit == DistanceUnit.NAUTICAL_MILES:
            distance = distance_m / 1852
        else:  # METERS
            distance = distance_m

        self.calculation_count += 1
        return distance

    def batch_haversine_distances(self, center_lat: float, center_lon: float,
                                 points: List[Tuple[float, float]],
                                 unit: Optional[DistanceUnit] = None) -> List[float]:
        """Batch Haversine distance calculation from center point."""
        if unit is None:
            unit = self.default_unit

        distances = []
        for lat, lon in points:
            distance = self.haversine_distance(center_lat, center_lon, lat, lon, unit)
            distances.append(distance)

        return distances

    def closest_point(self, reference_lat: float, reference_lon: float,
                     points: List[Tuple[float, float, Any]]) -> Tuple[float, float, Any, float]:
        """Find closest point."""
        if not points:
            raise ValueError("Points list is empty")

        min_distance = float('inf')
        closest = None

        for lat, lon, data in points:
            distance = self.haversine_distance(reference_lat, reference_lon, lat, lon)
            if distance < min_distance:
                min_distance = distance
                closest = (lat, lon, data, distance)

        return closest

    def get_calculation_statistics(self) -> Dict[str, Any]:
        """Get calculation statistics."""
        return {
            "total_calculations": self.calculation_count,
            "default_unit": self.default_unit.value
        }


__all__ = ['DistanceCalculator']
