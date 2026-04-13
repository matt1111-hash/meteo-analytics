# ruff: noqa: F403, F405,noqa: I001
# mypy: ignore-errors
"""Mixin part 2 for DistanceCalculator."""

from __future__ import annotations

from .distance_calculator_support import *


class DistanceCalculatorPart2Mixin:  # noqa: D101
    def _resolve_distance_unit(self, unit: Optional[DistanceUnit]) -> DistanceUnit:
        """Resolve explicit or default distance unit."""
        return self.default_unit if unit is None else unit

    def _to_radians(
        self, lat1: float, lon1: float, lat2: float, lon2: float
    ) -> Tuple[float, float, float, float]:
        """Convert coordinates to radians."""
        return (
            math.radians(lat1),
            math.radians(lon1),
            math.radians(lat2),
            math.radians(lon2),
        )

    def _calculate_reduced_latitudes(
        self, lat1_rad: float, lat2_rad: float
    ) -> Tuple[float, float, float, float]:
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
    ) -> Tuple[int, int, float, float, float, float, float]:
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
    ) -> Tuple[float, float, float, float, float, float]:
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
        unit: Optional[DistanceUnit] = None,
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

    def batch_haversine_distances(
        self,
        center_lat: float,
        center_lon: float,
        points: List[Tuple[float, float]],
        unit: Optional[DistanceUnit] = None,
    ) -> List[float]:
        """Batch Haversine distance calculation from center point."""
        if unit is None:
            unit = self.default_unit

        distances = []
        for lat, lon in points:
            distance = self.haversine_distance(center_lat, center_lon, lat, lon, unit)
            distances.append(distance)

        return distances

    def closest_point(
        self,
        reference_lat: float,
        reference_lon: float,
        points: List[Tuple[float, float, Any]],
    ) -> Tuple[float, float, Any, float]:
        """Find closest point."""
        if not points:
            raise ValueError("Points list is empty")

        min_distance = float("inf")
        closest = None

        for lat, lon, data in points:
            distance = self.haversine_distance(reference_lat, reference_lon, lat, lon)
            if distance < min_distance:
                min_distance = distance
                closest = (lat, lon, data, distance)

        return closest
