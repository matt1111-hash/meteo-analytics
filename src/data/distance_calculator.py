# mypy: ignore-errors
"""
Global Weather Analyzer - Distance Calculator.

Haversine and Vincenty distance calculations on Earth's surface:
- Haversine formula (fast, good accuracy)
- Vincenty formula (slower, high accuracy)
- Multiple unit support
- Batch distance calculations
"""

from __future__ import annotations

import logging
import math

from .distance_calculator_batch import DistanceBatchMixin
from .distance_calculator_support import (
    calculate_cos_2sigma_m,
    calculate_vincenty_coefficient,
    calculate_vincenty_distance_meters,
    convert_distance_from_meters,
)
from .geo_types import DistanceUnit

logger = logging.getLogger(__name__)


class DistanceCalculator(DistanceBatchMixin):
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
            DistanceUnit.METERS: self.EARTH_RADIUS_KM * 1000,
        }
        return radius_map[unit]

    def haversine_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float,
        unit: DistanceUnit | None = None,
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

    def _resolve_distance_unit(self, unit: DistanceUnit | None) -> DistanceUnit:
        """Resolve explicit or default distance unit."""
        return self.default_unit if unit is None else unit

    def _to_radians(
        self, lat1: float, lon1: float, lat2: float, lon2: float
    ) -> tuple[float, float, float, float]:
        """Convert coordinates to radians."""
        return (
            math.radians(lat1),
            math.radians(lon1),
            math.radians(lat2),
            math.radians(lon2),
        )

    def _calculate_reduced_latitudes(
        self, lat1_rad: float, lat2_rad: float
    ) -> tuple[float, float, float, float]:
        """Calculate reduced latitude trigonometric values."""
        u1 = math.atan((1 - self.WGS84_F) * math.tan(lat1_rad))
        u2 = math.atan((1 - self.WGS84_F) * math.tan(lat2_rad))
        return math.sin(u1), math.cos(u1), math.sin(u2), math.cos(u2)

    def _iterate_vincenty_lambda(
        self,
        longitude_difference: float,
        sin_u1: float,
        cos_u1: float,
        sin_u2: float,
        cos_u2: float,
    ) -> tuple[int, int, float, float, float, float, float]:
        """Iterate Vincenty lambda until convergence or limit."""
        lambda_val = longitude_difference
        lambda_prev = 0.0
        iteration_limit = 100
        iteration = 0
        cos2_alpha = 0.0
        sin_sigma = 0.0
        cos_sigma = 0.0
        cos_2sigma_m = 0.0
        sigma = 0.0

        while abs(lambda_val - lambda_prev) > 1e-12 and iteration < iteration_limit:  # noqa: PLR2004
            lambda_prev = lambda_val
            (
                lambda_val,
                cos2_alpha,
                sin_sigma,
                cos_sigma,
                cos_2sigma_m,
                sigma,
            ) = self._run_vincenty_iteration(
                lambda_val,
                longitude_difference,
                sin_u1,
                cos_u1,
                sin_u2,
                cos_u2,
            )
            iteration += 1

        return (
            iteration,
            iteration_limit,
            cos2_alpha,
            sin_sigma,
            cos_sigma,
            cos_2sigma_m,
            sigma,
        )

    def _run_vincenty_iteration(
        self,
        lambda_val: float,
        longitude_difference: float,
        sin_u1: float,
        cos_u1: float,
        sin_u2: float,
        cos_u2: float,
    ) -> tuple[float, float, float, float, float, float]:
        """Run one Vincenty iteration step."""
        sin_lambda = math.sin(lambda_val)
        cos_lambda = math.cos(lambda_val)
        sin_sigma = math.sqrt(
            (cos_u2 * sin_lambda) ** 2 + (cos_u1 * sin_u2 - sin_u1 * cos_u2 * cos_lambda) ** 2
        )
        if sin_sigma == 0:
            return lambda_val, 0.0, 0.0, 0.0, 0.0, 0.0

        cos_sigma = sin_u1 * sin_u2 + cos_u1 * cos_u2 * cos_lambda
        sigma = math.atan2(sin_sigma, cos_sigma)
        sin_alpha = cos_u1 * cos_u2 * sin_lambda / sin_sigma
        cos2_alpha = 1 - sin_alpha**2
        cos_2sigma_m = calculate_cos_2sigma_m(cos_sigma, sin_u1, sin_u2, cos2_alpha)
        coefficient = calculate_vincenty_coefficient(self.WGS84_F, cos2_alpha)
        next_lambda = longitude_difference + (1 - coefficient) * self.WGS84_F * sin_alpha * (
            sigma
            + coefficient
            * sin_sigma
            * (cos_2sigma_m + coefficient * cos_sigma * (-1 + 2 * cos_2sigma_m**2))
        )
        return next_lambda, cos2_alpha, sin_sigma, cos_sigma, cos_2sigma_m, sigma

    def vincenty_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float,
        unit: DistanceUnit | None = None,
    ) -> float:
        """
        Vincenty formula distance calculation.

        High accuracy distance calculation using WGS84 ellipsoid.
        Slower than Haversine, but higher accuracy (< 0.01% error).
        """
        unit = self._resolve_distance_unit(unit)
        lat1_rad, lon1_rad, lat2_rad, lon2_rad = self._to_radians(lat1, lon1, lat2, lon2)
        longitude_difference = lon2_rad - lon1_rad
        sin_u1, cos_u1, sin_u2, cos_u2 = self._calculate_reduced_latitudes(lat1_rad, lat2_rad)

        # Check for identical points first
        if longitude_difference == 0 and lat1_rad == lat2_rad:
            return 0.0

        (
            iteration,
            iteration_limit,
            cos2_alpha,
            sin_sigma,
            cos_sigma,
            cos_2sigma_m,
            sigma,
        ) = self._iterate_vincenty_lambda(longitude_difference, sin_u1, cos_u1, sin_u2, cos_u2)

        if sin_sigma == 0:
            return 0.0

        # Handle edge cases where Vincenty fails to converge
        if iteration == 0 or iteration >= iteration_limit:
            logger.warning("Vincenty iteration failed, Haversine fallback")
            return self.haversine_distance(lat1, lon1, lat2, lon2, unit)

        distance_m = calculate_vincenty_distance_meters(
            self.WGS84_A,
            self.WGS84_B,
            cos2_alpha,
            sin_sigma,
            cos_sigma,
            cos_2sigma_m,
            sigma,
        )
        distance = convert_distance_from_meters(distance_m, unit)
        self.calculation_count += 1
        return distance


__all__ = ["DistanceCalculator"]
