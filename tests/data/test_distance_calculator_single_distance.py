"""Tests for DistanceCalculator from distance_calculator.py."""

from __future__ import annotations

from src.data.distance_calculator import DistanceCalculator
from src.data.geo_types import DistanceUnit


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
        distance = calc.haversine_distance(47.4979, 19.0402, 47.5314, 21.6269)
        assert 190 < distance < 200

    def test_budapest_to_london_km(self) -> None:
        """haversine_distance calculates Budapest to London distance correctly."""
        calc = DistanceCalculator()
        distance = calc.haversine_distance(47.4979, 19.0402, 51.5074, -0.1278)
        assert 1400 < distance < 1500

    def test_uses_default_unit(self) -> None:
        """haversine_distance uses default unit when unit is None."""
        distance_km_calc = DistanceCalculator()
        distance_miles_calc = DistanceCalculator(default_unit=DistanceUnit.MILES)

        distance_km = distance_km_calc.haversine_distance(47.5, 19.0, 48.0, 20.0)
        distance_miles = distance_miles_calc.haversine_distance(47.5, 19.0, 48.0, 20.0)

        assert distance_miles < distance_km

    def test_explicit_unit(self) -> None:
        """haversine_distance uses explicit unit."""
        calc = DistanceCalculator()

        distance_miles = calc.haversine_distance(47.5, 19.0, 48.0, 20.0, unit=DistanceUnit.MILES)

        assert distance_miles > 0
        distance_km = calc.haversine_distance(47.5, 19.0, 48.0, 20.0)
        assert 0.6 < distance_miles / distance_km < 0.65

    def test_antipodal_points(self) -> None:
        """haversine_distance handles antipodal points."""
        calc = DistanceCalculator()
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
        distance = calc.haversine_distance(47.5, 19.0, 48.0, 20.0, unit=DistanceUnit.NAUTICAL_MILES)
        assert distance > 0

    def test_meters(self) -> None:
        """haversine_distance returns correct value in meters."""
        calc = DistanceCalculator()
        distance = calc.haversine_distance(47.5, 19.0, 48.0, 20.0, unit=DistanceUnit.METERS)
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
        assert 190 < distance < 200

    def test_compares_with_haversine(self) -> None:
        """vincenty_distance is close to haversine_distance."""
        calc = DistanceCalculator()
        haversine = calc.haversine_distance(47.5, 19.0, 51.5, -0.1)
        vincenty = calc.vincenty_distance(47.5, 19.0, 51.5, -0.1)
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
        distance_miles = calc.vincenty_distance(47.5, 19.0, 48.0, 20.0, unit=DistanceUnit.MILES)
        assert distance_miles > 0

    def test_meters_output(self) -> None:
        """vincenty_distance returns distance in meters when requested."""
        calc = DistanceCalculator()
        distance = calc.vincenty_distance(47.5, 19.0, 48.0, 20.0, unit=DistanceUnit.METERS)
        assert distance > 70000

    def test_increments_calculation_count(self) -> None:
        """vincenty_distance increments calculation_count."""
        calc = DistanceCalculator()
        initial_count = calc.calculation_count
        calc.vincenty_distance(47.5, 19.0, 48.0, 20.0)
        assert calc.calculation_count == initial_count + 1

    def test_long_distance(self) -> None:
        """vincenty_distance handles long distances."""
        calc = DistanceCalculator()
        distance = calc.vincenty_distance(47.5, 19.0, 35.7, 139.7)
        assert 8000 < distance < 10000
