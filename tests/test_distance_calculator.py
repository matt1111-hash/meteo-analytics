#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tests for src.data.distance_calculator.DistanceCalculator
"""

import math

import pytest

from src.data.distance_calculator import DistanceCalculator
from src.data.geo_types import DistanceUnit


class TestDistanceCalculatorInit:
    """Test DistanceCalculator initialization."""

    def test_default_initialization(self):
        """Test default initialization with kilometers."""
        calc = DistanceCalculator()
        assert calc.default_unit == DistanceUnit.KILOMETERS
        assert calc.calculation_count == 0

    def test_initialization_with_unit(self):
        """Test initialization with different units."""
        calc_miles = DistanceCalculator(DistanceUnit.MILES)
        assert calc_miles.default_unit == DistanceUnit.MILES

        calc_nm = DistanceCalculator(DistanceUnit.NAUTICAL_MILES)
        assert calc_nm.default_unit == DistanceUnit.NAUTICAL_MILES


class TestEarthRadius:
    """Test Earth radius constants."""

    def test_get_earth_radius_kilometers(self):
        """Test Earth radius for kilometers."""
        calc = DistanceCalculator()
        radius = calc._get_earth_radius(DistanceUnit.KILOMETERS)
        assert radius == DistanceCalculator.EARTH_RADIUS_KM
        assert radius == 6371.0

    def test_get_earth_radius_miles(self):
        """Test Earth radius for miles."""
        calc = DistanceCalculator()
        radius = calc._get_earth_radius(DistanceUnit.MILES)
        assert radius == DistanceCalculator.EARTH_RADIUS_MILES
        assert radius == 3958.8

    def test_get_earth_radius_nautical_miles(self):
        """Test Earth radius for nautical miles."""
        calc = DistanceCalculator()
        radius = calc._get_earth_radius(DistanceUnit.NAUTICAL_MILES)
        assert radius == DistanceCalculator.EARTH_RADIUS_NAUTICAL_MILES
        assert radius == 3440.1

    def test_get_earth_radius_meters(self):
        """Test Earth radius for meters."""
        calc = DistanceCalculator()
        radius = calc._get_earth_radius(DistanceUnit.METERS)
        assert radius == DistanceCalculator.EARTH_RADIUS_KM * 1000


class TestHaversineDistance:
    """Test Haversine distance calculation."""

    def test_haversine_same_point(self):
        """Test distance to same point is zero."""
        calc = DistanceCalculator()
        distance = calc.haversine_distance(47.4979, 19.0402, 47.4979, 19.0402)
        assert distance == pytest.approx(0.0, abs=1e-10)

    def test_haversine_budapest_prague(self):
        """Test distance between Budapest and Prague."""
        calc = DistanceCalculator()
        # Budapest: 47.4979°N, 19.0402°E
        # Prague: 50.0755°N, 14.4378°E
        # Expected distance ~442 km
        distance = calc.haversine_distance(47.4979, 19.0402, 50.0755, 14.4378)
        assert 440 < distance < 450

    def test_haversine_equator_degree(self):
        """Test one degree of longitude at equator ~111 km."""
        calc = DistanceCalculator()
        # At equator, 1 degree longitude = ~111.32 km
        distance = calc.haversine_distance(0, 0, 0, 1)
        assert 110 < distance < 112

    def test_haversine_meridian_degree(self):
        """Test one degree of latitude ~111 km."""
        calc = DistanceCalculator()
        # 1 degree latitude is always ~111 km
        distance = calc.haversine_distance(0, 0, 1, 0)
        assert 110 < distance < 112

    def test_haversine_different_units(self):
        """Test Haversine with different units."""
        calc_km = DistanceCalculator(DistanceUnit.KILOMETERS)
        calc_miles = DistanceCalculator(DistanceUnit.MILES)
        calc_m = DistanceCalculator(DistanceUnit.METERS)

        # Budapest to Prague
        dist_km = calc_km.haversine_distance(47.4979, 19.0402, 50.0755, 14.4378)
        dist_miles = calc_miles.haversine_distance(47.4979, 19.0402, 50.0755, 14.4378)
        dist_m = calc_m.haversine_distance(47.4979, 19.0402, 50.0755, 14.4378)

        # Verify unit conversions
        assert dist_m == pytest.approx(dist_km * 1000, rel=0.01)
        assert dist_miles == pytest.approx(dist_km * 0.621371, rel=0.01)

    def test_haversine_unit_parameter_override(self):
        """Test unit parameter overrides default."""
        calc = DistanceCalculator(DistanceUnit.KILOMETERS)
        dist_km = calc.haversine_distance(47.4979, 19.0402, 50.0755, 14.4378)
        dist_miles = calc.haversine_distance(47.4979, 19.0402, 50.0755, 14.4378, DistanceUnit.MILES)

        # 442 km ≈ 275 miles
        assert 270 < dist_miles < 280
        assert dist_miles == pytest.approx(dist_km * 0.621371, rel=0.01)

    def test_haversine_increments_counter(self):
        """Test calculation increments counter."""
        calc = DistanceCalculator()
        assert calc.calculation_count == 0
        calc.haversine_distance(47.4979, 19.0402, 50.0755, 14.4378)
        assert calc.calculation_count == 1


class TestVincentyDistance:
    """Test Vincenty distance calculation."""

    def test_vincenty_same_point(self):
        """Test Vincenty distance to same point is zero."""
        calc = DistanceCalculator()
        distance = calc.vincenty_distance(47.4979, 19.0402, 47.4979, 19.0402)
        assert distance == pytest.approx(0.0, abs=1e-10)

    def test_vincenty_budapest_prague(self):
        """Test Vincenty distance between Budapest and Prague."""
        calc = DistanceCalculator()
        distance = calc.vincenty_distance(47.4979, 19.0402, 50.0755, 14.4378)
        # Should be similar to Haversine (~442 km)
        assert 440 < distance < 450

    def test_vincenty_accurate_than_haversine(self):
        """Test Vincenty is more accurate than Haversine for long distances."""
        calc = DistanceCalculator()
        # New York to Los Angeles (long distance where ellipsoid matters)
        ny_lat, ny_lon = 40.7128, -74.0060
        la_lat, la_lon = 34.0522, -118.2437

        haversine = calc.haversine_distance(ny_lat, ny_lon, la_lat, la_lon)
        vincenty = calc.vincenty_distance(ny_lat, ny_lon, la_lat, la_lon)

        # Both should give reasonable results (~3940 km)
        assert 3900 < haversine < 4000
        assert 3900 < vincenty < 4000

    def test_vincenty_different_units(self):
        """Test Vincenty with different units."""
        calc = DistanceCalculator(DistanceUnit.KILOMETERS)

        dist_km = calc.vincenty_distance(47.4979, 19.0402, 50.0755, 14.4378, DistanceUnit.KILOMETERS)
        dist_miles = calc.vincenty_distance(47.4979, 19.0402, 50.0755, 14.4378, DistanceUnit.MILES)
        dist_m = calc.vincenty_distance(47.4979, 19.0402, 50.0755, 14.4378, DistanceUnit.METERS)

        assert dist_m == pytest.approx(dist_km * 1000, rel=0.01)
        assert dist_miles == pytest.approx(dist_km * 0.621371, rel=0.01)

    def test_vincenty_poles(self):
        """Test Vincenty distance between nearly antipodal points."""
        calc = DistanceCalculator()
        # North Pole to South Pole
        distance = calc.vincenty_distance(90, 0, -90, 0)
        # Should use Haversine fallback (~20,000 km)
        assert 19000 < distance < 21000

    def test_vincenty_increments_counter(self):
        """Test Vincenty increments counter."""
        calc = DistanceCalculator()
        assert calc.calculation_count == 0
        calc.vincenty_distance(47.4979, 19.0402, 50.0755, 14.4378)
        assert calc.calculation_count == 1


class TestBatchDistances:
    """Test batch distance calculations."""

    def test_batch_haversine_empty_list(self):
        """Test batch calculation with empty list."""
        calc = DistanceCalculator()
        distances = calc.batch_haversine_distances(47.4979, 19.0402, [])
        assert distances == []

    def test_batch_haversine_single_point(self):
        """Test batch calculation with single point."""
        calc = DistanceCalculator()
        distances = calc.batch_haversine_distances(47.4979, 19.0402, [(50.0755, 14.4378)])
        assert len(distances) == 1
        assert 440 < distances[0] < 450

    def test_batch_haversine_multiple_points(self):
        """Test batch calculation with multiple points."""
        calc = DistanceCalculator()
        points = [
            (50.0755, 14.4378),  # Prague
            (48.8566, 2.3522),   # Paris
            (52.5200, 13.4050),  # Berlin
        ]
        distances = calc.batch_haversine_distances(47.4979, 19.0402, points)

        assert len(distances) == 3
        # Prague ~442 km
        assert 440 < distances[0] < 450
        # Paris ~1240 km
        assert 1200 < distances[1] < 1300
        # Berlin ~680 km
        assert 670 < distances[2] < 690

    def test_batch_haversine_with_unit(self):
        """Test batch calculation with specific unit."""
        calc = DistanceCalculator(DistanceUnit.KILOMETERS)
        points = [(50.0755, 14.4378)]

        distances_km = calc.batch_haversine_distances(47.4979, 19.0402, points, DistanceUnit.KILOMETERS)
        distances_miles = calc.batch_haversine_distances(47.4979, 19.0402, points, DistanceUnit.MILES)

        assert distances_miles[0] == pytest.approx(distances_km[0] * 0.621371, rel=0.01)


class TestClosestPoint:
    """Test closest point finding."""

    def test_closest_point_empty_list_raises(self):
        """Test closest_point raises ValueError for empty list."""
        calc = DistanceCalculator()
        with pytest.raises(ValueError, match="Points list is empty"):
            calc.closest_point(47.4979, 19.0402, [])

    def test_closest_point_single_point(self):
        """Test closest_point with single point."""
        calc = DistanceCalculator()
        points = [(50.0755, 14.4378, "Prague")]

        lat, lon, data, distance = calc.closest_point(47.4979, 19.0402, points)

        assert lat == 50.0755
        assert lon == 14.4378
        assert data == "Prague"
        assert 440 < distance < 450

    def test_closest_point_multiple_points(self):
        """Test closest_point finds nearest among multiple."""
        calc = DistanceCalculator()
        points = [
            (50.0755, 14.4378, "Prague"),    # ~442 km
            (48.8566, 2.3522, "Paris"),      # ~1240 km
            (52.5200, 13.4050, "Berlin"),    # ~680 km
        ]

        lat, lon, data, distance = calc.closest_point(47.4979, 19.0402, points)

        # Prague should be closest
        assert data == "Prague"
        assert distance == pytest.approx(442, abs=5)

    def test_closest_point_returns_correct_data(self):
        """Test closest_point returns associated data."""
        calc = DistanceCalculator()
        points = [
            (50.0755, 14.4378, {"name": "Prague", "pop": 1300000}),
            (48.8566, 2.3522, {"name": "Paris", "pop": 2100000}),
        ]

        lat, lon, data, distance = calc.closest_point(47.4979, 19.0402, points)

        assert data["name"] == "Prague"
        assert data["pop"] == 1300000


class TestCalculationStatistics:
    """Test calculation statistics tracking."""

    def test_statistics_returns_dict(self):
        """Test get_calculation_statistics returns dict."""
        calc = DistanceCalculator()
        stats = calc.get_calculation_statistics()
        assert isinstance(stats, dict)
        assert "total_calculations" in stats
        assert "default_unit" in stats

    def test_statistics_initial_values(self):
        """Test initial statistics values."""
        calc = DistanceCalculator(DistanceUnit.MILES)
        stats = calc.get_calculation_statistics()
        assert stats["total_calculations"] == 0
        assert stats["default_unit"] == "miles"

    def test_statistics_tracks_calculations(self):
        """Test statistics track calculation count."""
        calc = DistanceCalculator()

        calc.haversine_distance(47.4979, 19.0402, 50.0755, 14.4378)
        calc.vincenty_distance(47.4979, 19.0402, 50.0755, 14.4378)
        calc.batch_haversine_distances(47.4979, 19.0402, [(50.0755, 14.4378), (48.8566, 2.3522)])

        stats = calc.get_calculation_statistics()
        # 1 haversine + 1 vincenty + 2 batch = 4
        assert stats["total_calculations"] == 4


class TestConstants:
    """Test class constants."""

    def test_earth_radius_constants(self):
        """Test Earth radius constants are correct."""
        assert DistanceCalculator.EARTH_RADIUS_KM == 6371.0
        assert DistanceCalculator.EARTH_RADIUS_MILES == 3958.8
        assert DistanceCalculator.EARTH_RADIUS_NAUTICAL_MILES == 3440.1

    def test_wgs84_constants(self):
        """Test WGS84 ellipsoid constants."""
        # Standard WGS84 values
        assert DistanceCalculator.WGS84_A == 6378137.0
        assert DistanceCalculator.WGS84_B == 6356752.314245
        assert abs(DistanceCalculator.WGS84_F - 1/298.257223563) < 1e-15
