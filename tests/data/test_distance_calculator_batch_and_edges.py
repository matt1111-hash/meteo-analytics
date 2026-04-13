"""Tests for DistanceCalculator from distance_calculator.py."""

from __future__ import annotations

import pytest
from src.data.distance_calculator import DistanceCalculator
from src.data.geo_types import DistanceUnit


class TestBatchHaversineDistances:
    """Test batch_haversine_distances method."""

    def test_empty_points_list(self) -> None:
        """batch_haversine_distances returns empty list for empty input."""
        calc = DistanceCalculator()
        distances = calc.batch_haversine_distances(47.5, 19.0, [])
        assert distances == []

    def test_single_point(self) -> None:
        """batch_haversine_distances handles single point."""
        calc = DistanceCalculator()
        distances = calc.batch_haversine_distances(47.5, 19.0, [(48.0, 20.0)])
        assert len(distances) == 1
        assert distances[0] > 0

    def test_multiple_points(self) -> None:
        """batch_haversine_distances handles multiple points."""
        calc = DistanceCalculator()
        points = [(48.0, 20.0), (46.0, 18.0), (50.0, 14.0)]
        distances = calc.batch_haversine_distances(47.5, 19.0, points)
        assert len(distances) == 3
        assert all(d > 0 for d in distances)

    def test_uses_default_unit(self) -> None:
        """batch_haversine_distances uses default unit."""
        calc = DistanceCalculator(default_unit=DistanceUnit.MILES)
        distances = calc.batch_haversine_distances(47.5, 19.0, [(48.0, 20.0)])
        assert len(distances) == 1

    def test_explicit_unit(self) -> None:
        """batch_haversine_distances uses explicit unit."""
        calc = DistanceCalculator()
        distances = calc.batch_haversine_distances(
            47.5, 19.0, [(48.0, 20.0)], unit=DistanceUnit.MILES
        )
        assert len(distances) == 1

    def test_increments_calculation_count(self) -> None:
        """batch_haversine_distances increments count per point."""
        calc = DistanceCalculator()
        initial_count = calc.calculation_count
        calc.batch_haversine_distances(47.5, 19.0, [(48.0, 20.0), (46.0, 18.0)])
        assert calc.calculation_count == initial_count + 2


class TestClosestPoint:
    """Test closest_point method."""

    def test_raises_for_empty_list(self) -> None:
        """closest_point raises ValueError for empty list."""
        calc = DistanceCalculator()
        with pytest.raises(ValueError, match="Points list is empty"):
            calc.closest_point(47.5, 19.0, [])

    def test_returns_closest_single_point(self) -> None:
        """closest_point returns the only point when single."""
        calc = DistanceCalculator()
        points = [(48.0, 20.0, "data1")]
        result = calc.closest_point(47.5, 19.0, points)
        lat, lon, data, distance = result
        assert lat == 48.0
        assert lon == 20.0
        assert data == "data1"
        assert distance > 0

    def test_returns_closest_of_multiple(self) -> None:
        """closest_point returns the closest of multiple points."""
        calc = DistanceCalculator()
        points = [
            (47.6, 19.1, "Close"),
            (48.0, 20.0, "Medium"),
            (50.0, 25.0, "Far"),
        ]
        result = calc.closest_point(47.5, 19.0, points)
        lat, lon, data, distance = result  # noqa: RUF059
        assert data == "Close"
        assert distance < 20

    def test_returns_tuple_with_distance(self) -> None:
        """closest_point returns tuple with (lat, lon, data, distance)."""
        calc = DistanceCalculator()
        points = [(48.0, 20.0, {"name": "TestCity"})]
        result = calc.closest_point(47.5, 19.0, points)
        assert isinstance(result, tuple)
        assert len(result) == 4
        lat, lon, data, distance = result
        assert isinstance(lat, float)
        assert isinstance(lon, float)
        assert isinstance(data, dict)
        assert isinstance(distance, float)

    def test_increments_calculation_count(self) -> None:
        """closest_point increments calculation_count per point."""
        calc = DistanceCalculator()
        initial_count = calc.calculation_count
        points = [(48.0, 20.0, "a"), (46.0, 18.0, "b")]
        calc.closest_point(47.5, 19.0, points)
        assert calc.calculation_count == initial_count + 2


class TestGetCalculationStatistics:
    """Test get_calculation_statistics method."""

    def test_returns_dict_with_required_fields(self) -> None:
        """get_calculation_statistics returns dict with required fields."""
        calc = DistanceCalculator()
        stats = calc.get_calculation_statistics()
        assert isinstance(stats, dict)
        assert "total_calculations" in stats
        assert "default_unit" in stats

    def test_total_calculations_initial_zero(self) -> None:
        """get_calculation_statistics shows 0 calculations initially."""
        calc = DistanceCalculator()
        stats = calc.get_calculation_statistics()
        assert stats["total_calculations"] == 0

    def test_total_calculations_after_operations(self) -> None:
        """get_calculation_statistics shows correct count after operations."""
        calc = DistanceCalculator()
        calc.haversine_distance(47.5, 19.0, 48.0, 20.0)
        calc.haversine_distance(47.5, 19.0, 46.0, 18.0)
        stats = calc.get_calculation_statistics()
        assert stats["total_calculations"] == 2

    def test_default_unit_in_stats(self) -> None:
        """get_calculation_statistics shows default unit."""
        calc = DistanceCalculator(default_unit=DistanceUnit.MILES)
        stats = calc.get_calculation_statistics()
        assert stats["default_unit"] == "miles"


class TestDistanceCalculatorEdgeCases:
    """Edge case tests for DistanceCalculator."""

    def test_negative_coordinates(self) -> None:
        """DistanceCalculator handles negative coordinates."""
        calc = DistanceCalculator()
        distance = calc.haversine_distance(0, 0, -33.8688, 151.2093)
        assert distance > 0

    def test_crossing_dateline(self) -> None:
        """DistanceCalculator handles crossing the dateline."""
        calc = DistanceCalculator()
        distance = calc.haversine_distance(35.7, 139.7, 34.0, -118.2)
        assert 8500 < distance < 9500

    def test_pole_to_pole(self) -> None:
        """DistanceCalculator handles pole to pole distance."""
        calc = DistanceCalculator()
        distance = calc.haversine_distance(90, 0, -90, 0)
        assert 19900 < distance < 20100

    def test_equator_distance(self) -> None:
        """DistanceCalculator calculates equator distance correctly."""
        calc = DistanceCalculator()
        distance = calc.haversine_distance(0, 0, 0, 90)
        assert 9900 < distance < 10100

    def test_very_small_distance(self) -> None:
        """DistanceCalculator handles very small distances."""
        calc = DistanceCalculator()
        distance = calc.haversine_distance(47.5, 19.0, 47.501, 19.0)
        assert 0.05 < distance < 0.2

    def test_vincenty_identical_points(self) -> None:
        """vincenty_distance returns 0 for identical points."""
        calc = DistanceCalculator()
        distance = calc.vincenty_distance(47.5, 19.0, 47.5, 19.0)
        assert distance == 0.0

    def test_mixed_unit_calculations(self) -> None:
        """DistanceCalculator handles mixed unit calculations."""
        calc = DistanceCalculator(default_unit=DistanceUnit.KILOMETERS)
        distance_km = calc.haversine_distance(47.5, 19.0, 48.0, 20.0, unit=DistanceUnit.KILOMETERS)
        distance_miles = calc.haversine_distance(47.5, 19.0, 48.0, 20.0, unit=DistanceUnit.MILES)
        ratio = distance_miles / distance_km
        assert 0.60 < ratio < 0.65
