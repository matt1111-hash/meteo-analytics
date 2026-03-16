"""Tests for DistanceCalculator from distance_calculator.py."""

from __future__ import annotations

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
