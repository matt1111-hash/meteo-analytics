"""Tests for DistanceCalculator from distance_calculator.py."""

from __future__ import annotations

import math
from typing import Tuple, Any

import pytest

from src.data.distance_calculator import DistanceCalculator
from src.data.geo_types import DistanceUnit


class TestDistanceCalculatorInit:
    """Test DistanceCalculator initialization."""

    def test_init_default_unit(self) -> None:
        """Initialization with default unit (KILOMETERS)."""
        calc = DistanceCalculator()

        assert calc.default_unit == DistanceUnit.KILOMETERS
        assert calc.calculation_count == 0

    def test_init_custom_unit(self) -> None:
        """Initialization with custom unit."""
        calc = DistanceCalculator(default_unit=DistanceUnit.MILES)

        assert calc.default_unit == DistanceUnit.MILES

    def test_earth_radius_constants(self) -> None:
        """Earth radius constants are defined."""
        calc = DistanceCalculator()

        assert calc.EARTH_RADIUS_KM == 6371.0
        assert calc.EARTH_RADIUS_MILES == 3958.8
        assert calc.EARTH_RADIUS_NAUTICAL_MILES == 3440.1

    def test_wgs84_constants(self) -> None:
        """WGS84 ellipsoid constants are defined."""
        calc = DistanceCalculator()

        assert calc.WGS84_A == 6378137.0
        assert calc.WGS84_B == 6356752.314245
        assert abs(calc.WGS84_F - 1 / 298.257223563) < 1e-15


class TestGetEarthRadius:
    """Test _get_earth_radius method."""

    def test_kilometers(self) -> None:
        """_get_earth_radius returns correct value for KILOMETERS."""
        calc = DistanceCalculator()

        radius = calc._get_earth_radius(DistanceUnit.KILOMETERS)

        assert radius == 6371.0

    def test_miles(self) -> None:
        """_get_earth_radius returns correct value for MILES."""
        calc = DistanceCalculator()

        radius = calc._get_earth_radius(DistanceUnit.MILES)

        assert radius == 3958.8

    def test_nautical_miles(self) -> None:
        """_get_earth_radius returns correct value for NAUTICAL_MILES."""
        calc = DistanceCalculator()

        radius = calc._get_earth_radius(DistanceUnit.NAUTICAL_MILES)

        assert radius == 3440.1

    def test_meters(self) -> None:
        """_get_earth_radius returns correct value for METERS."""
        calc = DistanceCalculator()

        radius = calc._get_earth_radius(DistanceUnit.METERS)

        assert radius == 6371000.0


class TestHaversineDistance:
    """Test haversine_distance method."""

    def test_zero_distance(self) -> None:
        """haversine_distance returns 0 for same point."""
        calc = DistanceCalculator()

        distance = calc.haversine_distance(47.5, 19.0, 47.5, 19.0)

        assert distance == 0.0

    def test_budapest_to_debrecen_km(self) -> None:
        """haversine_distance calculates Budapest to Debrecen distance correctly."""
        calc = DistanceCalculator()

        # Budapest: 47.4979, 19.0402
        # Debrecen: 47.5314, 21.6269
        # Expected distance: ~195 km
        distance = calc.haversine_distance(47.4979, 19.0402, 47.5314, 21.6269)

        assert 190 < distance < 200

    def test_budapest_to_london_km(self) -> None:
        """haversine_distance calculates Budapest to London distance correctly."""
        calc = DistanceCalculator()

        # Budapest: 47.4979, 19.0402
        # London: 51.5074, -0.1278
        # Expected distance: ~1450 km
        distance = calc.haversine_distance(47.4979, 19.0402, 51.5074, -0.1278)

        assert 1400 < distance < 1500

    def test_uses_default_unit(self) -> None:
        """haversine_distance uses default unit when unit is None."""
        calc = DistanceCalculator(default_unit=DistanceUnit.MILES)

        distance_km_calc = DistanceCalculator()
        distance_miles_calc = DistanceCalculator(default_unit=DistanceUnit.MILES)

        distance_km = distance_km_calc.haversine_distance(47.5, 19.0, 48.0, 20.0)
        distance_miles = distance_miles_calc.haversine_distance(47.5, 19.0, 48.0, 20.0)

        # Miles should be less than km
        assert distance_miles < distance_km

    def test_explicit_unit(self) -> None:
        """haversine_distance uses explicit unit."""
        calc = DistanceCalculator()

        distance_miles = calc.haversine_distance(
            47.5, 19.0, 48.0, 20.0, unit=DistanceUnit.MILES
        )

        assert distance_miles > 0
        # Miles should be roughly 0.62 of km
        distance_km = calc.haversine_distance(47.5, 19.0, 48.0, 20.0)
        assert 0.6 < distance_miles / distance_km < 0.65

    def test_antipodal_points(self) -> None:
        """haversine_distance handles antipodal points."""
        calc = DistanceCalculator()

        # Antipodal points (opposite sides of Earth)
        # Should be roughly half the circumference: ~20,000 km
        distance = calc.haversine_distance(0, 0, 0, 180)

        assert 19900 < distance < 20100

    def test_increments_calculation_count(self) -> None:
        """haversine_distance increments calculation_count."""
        calc = DistanceCalculator()
        assert calc.calculation_count == 0

        calc.haversine_distance(47.5, 19.0, 48.0, 20.0)

        assert calc.calculation_count == 1

    def test_nautical_miles(self) -> None:
        """haversine_distance returns correct value in nautical miles."""
        calc = DistanceCalculator()

        distance = calc.haversine_distance(
            47.5, 19.0, 48.0, 20.0, unit=DistanceUnit.NAUTICAL_MILES
        )

        assert distance > 0

    def test_meters(self) -> None:
        """haversine_distance returns correct value in meters."""
        calc = DistanceCalculator()

        distance = calc.haversine_distance(
            47.5, 19.0, 48.0, 20.0, unit=DistanceUnit.METERS
        )

        # Should be roughly 70-100 km in meters
        assert 70000 < distance < 100000


class TestVincentyDistance:
    """Test vincenty_distance method."""

    def test_zero_distance_same_point(self) -> None:
        """vincenty_distance returns 0 for same point."""
        calc = DistanceCalculator()

        distance = calc.vincenty_distance(47.5, 19.0, 47.5, 19.0)

        assert distance == 0.0

    def test_budapest_to_debrecen(self) -> None:
        """vincenty_distance calculates Budapest to Debrecen distance."""
        calc = DistanceCalculator()

        distance = calc.vincenty_distance(47.4979, 19.0402, 47.5314, 21.6269)

        # Should be similar to Haversine (~195 km)
        assert 190 < distance < 200

    def test_compares_with_haversine(self) -> None:
        """vincenty_distance is close to haversine_distance."""
        calc = DistanceCalculator()

        haversine = calc.haversine_distance(47.5, 19.0, 51.5, -0.1)
        vincenty = calc.vincenty_distance(47.5, 19.0, 51.5, -0.1)

        # Vincenty should be within 0.5% of Haversine
        diff_percent = abs(vincenty - haversine) / haversine * 100
        assert diff_percent < 0.5

    def test_uses_default_unit(self) -> None:
        """vincenty_distance uses default unit."""
        calc = DistanceCalculator(default_unit=DistanceUnit.MILES)

        distance = calc.vincenty_distance(47.5, 19.0, 48.0, 20.0)

        assert distance > 0

    def test_explicit_unit(self) -> None:
        """vincenty_distance uses explicit unit."""
        calc = DistanceCalculator()

        distance_miles = calc.vincenty_distance(
            47.5, 19.0, 48.0, 20.0, unit=DistanceUnit.MILES
        )

        assert distance_miles > 0

    def test_meters_output(self) -> None:
        """vincenty_distance returns distance in meters when requested."""
        calc = DistanceCalculator()

        distance = calc.vincenty_distance(
            47.5, 19.0, 48.0, 20.0, unit=DistanceUnit.METERS
        )

        assert distance > 70000  # Should be ~70-100 km in meters

    def test_increments_calculation_count(self) -> None:
        """vincenty_distance increments calculation_count."""
        calc = DistanceCalculator()
        initial_count = calc.calculation_count

        calc.vincenty_distance(47.5, 19.0, 48.0, 20.0)

        assert calc.calculation_count == initial_count + 1

    def test_long_distance(self) -> None:
        """vincenty_distance handles long distances."""
        calc = DistanceCalculator()

        # Budapest to Tokyo
        distance = calc.vincenty_distance(47.5, 19.0, 35.7, 139.7)

        assert 8000 < distance < 10000  # ~9000 km


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
        # Reference point: Budapest (47.5, 19.0)

        # Points at known distances from Budapest
        points = [
            (47.6, 19.1, "Close"),      # Very close (~12 km north)
            (48.0, 20.0, "Medium"),     # Medium distance (~70 km)
            (50.0, 25.0, "Far"),        # Far away
        ]

        result = calc.closest_point(47.5, 19.0, points)

        lat, lon, data, distance = result
        assert data == "Close"
        assert distance < 20  # Should be less than 20 km

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

        # Sydney: -33.8688, 151.2093
        distance = calc.haversine_distance(0, 0, -33.8688, 151.2093)

        assert distance > 0

    def test_crossing_dateline(self) -> None:
        """DistanceCalculator handles crossing the dateline."""
        calc = DistanceCalculator()

        # Tokyo (139.7) to Los Angeles (-118.2)
        distance = calc.haversine_distance(35.7, 139.7, 34.0, -118.2)

        # Should be roughly 8800-9000 km
        assert 8500 < distance < 9500

    def test_pole_to_pole(self) -> None:
        """DistanceCalculator handles pole to pole distance."""
        calc = DistanceCalculator()

        distance = calc.haversine_distance(90, 0, -90, 0)

        # Should be roughly half the circumference: ~20,000 km
        assert 19900 < distance < 20100

    def test_equator_distance(self) -> None:
        """DistanceCalculator calculates equator distance correctly."""
        calc = DistanceCalculator()

        # Quarter way around equator
        distance = calc.haversine_distance(0, 0, 0, 90)

        # Should be roughly 10,000 km
        assert 9900 < distance < 10100

    def test_very_small_distance(self) -> None:
        """DistanceCalculator handles very small distances."""
        calc = DistanceCalculator()

        # 0.001 degree difference ~ 100m at Budapest latitude
        distance = calc.haversine_distance(47.5, 19.0, 47.501, 19.0)

        # Should be ~0.11 km (111 meters)
        assert 0.05 < distance < 0.2

    def test_vincenty_identical_points(self) -> None:
        """vincenty_distance returns 0 for identical points."""
        calc = DistanceCalculator()

        distance = calc.vincenty_distance(47.5, 19.0, 47.5, 19.0)

        assert distance == 0.0

    def test_mixed_unit_calculations(self) -> None:
        """DistanceCalculator handles mixed unit calculations."""
        calc = DistanceCalculator(default_unit=DistanceUnit.KILOMETERS)

        # Calculate in different units
        distance_km = calc.haversine_distance(47.5, 19.0, 48.0, 20.0, unit=DistanceUnit.KILOMETERS)
        distance_miles = calc.haversine_distance(47.5, 19.0, 48.0, 20.0, unit=DistanceUnit.MILES)

        # Miles should be roughly 0.62 * km
        ratio = distance_miles / distance_km
        assert 0.60 < ratio < 0.65
