# mypy: ignore-errors
"""Batch and utility methods for DistanceCalculator."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from src.data.geo_types import DistanceUnit

if TYPE_CHECKING:
    from src.data.distance_calculator import DistanceCalculator


class DistanceBatchMixin:
    """Batch calculation mixin for DistanceCalculator."""

    def batch_haversine_distances(
        self: DistanceCalculator,
        center_lat: float,
        center_lon: float,
        points: list[tuple[float, float]],
        unit: DistanceUnit | None = None,
    ) -> list[float]:
        """Batch Haversine distance calculation from center point."""
        if unit is None:
            unit = self.default_unit
        return [
            self.haversine_distance(center_lat, center_lon, lat, lon, unit) for lat, lon in points
        ]

    def closest_point(
        self: DistanceCalculator,
        reference_lat: float,
        reference_lon: float,
        points: list[tuple[float, float, Any]],
    ) -> tuple[float, float, Any, float]:
        """Find closest point from a list."""
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

    def get_calculation_statistics(self: DistanceCalculator) -> dict[str, Any]:
        """Get calculation statistics."""
        return {
            "total_calculations": self.calculation_count,
            "default_unit": self.default_unit.value,
        }
