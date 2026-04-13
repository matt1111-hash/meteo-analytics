"""Geographic data types tests."""

from __future__ import annotations

from typing import Any

import pytest
from src.data.geo_types import CoordinateSystem, DistanceUnit, GeoPoint


class TestDistanceUnit:
    """Tests for DistanceUnit enum."""

    def test_kilometers_value(self) -> None:
        """KILOMETERS enum has correct string value."""
        assert DistanceUnit.KILOMETERS.value == "km"

    def test_miles_value(self) -> None:
        """MILES enum has correct string value."""
        assert DistanceUnit.MILES.value == "miles"

    def test_nautical_miles_value(self) -> None:
        """NAUTICAL_MILES enum has correct string value."""
        assert DistanceUnit.NAUTICAL_MILES.value == "nm"

    def test_meters_value(self) -> None:
        """METERS enum has correct string value."""
        assert DistanceUnit.METERS.value == "m"


class TestCoordinateSystem:
    """Tests for CoordinateSystem enum."""

    def test_wgs84_value(self) -> None:
        """WGS84 enum has correct string value."""
        assert CoordinateSystem.WGS84.value == "WGS84"

    def test_wgs72_value(self) -> None:
        """WGS72 enum has correct string value."""
        assert CoordinateSystem.WGS72.value == "WGS72"

    def test_nad83_value(self) -> None:
        """NAD83 enum has correct string value."""
        assert CoordinateSystem.NAD83.value == "NAD83"

    def test_etrs89_value(self) -> None:
        """ETRS89 enum has correct string value."""
        assert CoordinateSystem.ETRS89.value == "ETRS89"


class TestGeoPoint:
    """Tests for GeoPoint dataclass."""

    def test_create_valid_geopoint(self) -> None:
        """Valid coordinates create GeoPoint successfully."""
        point = GeoPoint(latitude=47.4979, longitude=19.0402)
        assert point.latitude == 47.4979
        assert point.longitude == 19.0402
        assert point.altitude is None
        assert point.name is None

    def test_create_geopoint_with_optional_fields(self) -> None:
        """GeoPoint with altitude and name."""
        point = GeoPoint(latitude=47.4979, longitude=19.0402, altitude=150.5, name="Budapest")
        assert point.altitude == 150.5
        assert point.name == "Budapest"

    def test_invalid_latitude_raises_error(self) -> None:
        """Latitude outside valid range raises ValueError."""
        with pytest.raises(ValueError, match="Invalid coordinates"):
            GeoPoint(latitude=91.0, longitude=0.0)

        with pytest.raises(ValueError, match="Invalid coordinates"):
            GeoPoint(latitude=-91.0, longitude=0.0)

    def test_invalid_longitude_raises_error(self) -> None:
        """Longitude outside valid range raises ValueError."""
        with pytest.raises(ValueError, match="Invalid coordinates"):
            GeoPoint(latitude=0.0, longitude=181.0)

        with pytest.raises(ValueError, match="Invalid coordinates"):
            GeoPoint(latitude=0.0, longitude=-181.0)

    def test_is_valid_returns_true_for_valid_coords(self) -> None:
        """is_valid returns True for valid coordinates."""
        point = GeoPoint(latitude=47.4979, longitude=19.0402)
        assert point.is_valid() is True

    def test_is_valid_returns_false_for_invalid_coords(self) -> None:
        """is_valid returns False for invalid coordinates (created manually)."""
        point = GeoPoint.__new__(GeoPoint)
        point.latitude = 100.0
        point.longitude = 0.0
        point.altitude = None
        point.name = None
        assert point.is_valid() is False

    def test_boundary_valid_coordinates(self) -> None:
        """Boundary values are accepted."""
        point = GeoPoint(latitude=0.0, longitude=0.0)
        assert point.is_valid() is True

        point = GeoPoint(latitude=90.0, longitude=0.0)
        assert point.is_valid() is True

        point = GeoPoint(latitude=-90.0, longitude=0.0)
        assert point.is_valid() is True

        point = GeoPoint(latitude=0.0, longitude=180.0)
        assert point.is_valid() is True

        point = GeoPoint(latitude=0.0, longitude=-180.0)
        assert point.is_valid() is True

    def test_normalize_longitude_wraparound(self) -> None:
        """normalize wraps longitude to -180 to 180 range."""
        point = GeoPoint(latitude=0.0, longitude=179.0)
        normalized = point.normalize()
        assert normalized.longitude == pytest.approx(179.0)

        point = GeoPoint(latitude=0.0, longitude=-179.0)
        normalized = point.normalize()
        assert normalized.longitude == pytest.approx(-179.0)

    def test_normalize_latitude_clamping(self) -> None:
        """normalize clamps latitude to -90 to 90 range."""
        point = GeoPoint(latitude=89.0, longitude=0.0)
        normalized = point.normalize()
        assert normalized.latitude == 89.0

        point = GeoPoint(latitude=-89.0, longitude=0.0)
        normalized = point.normalize()
        assert normalized.latitude == -89.0

        point = GeoPoint(latitude=90.0, longitude=0.0)
        normalized = point.normalize()
        assert normalized.latitude == 90.0

        point = GeoPoint(latitude=-90.0, longitude=0.0)
        normalized = point.normalize()
        assert normalized.latitude == -90.0

    def test_normalize_preserves_optional_fields(self) -> None:
        """normalize preserves altitude and name."""
        point = GeoPoint(latitude=47.4979, longitude=19.0402, altitude=150.5, name="Budapest")
        normalized = point.normalize()
        assert normalized.altitude == 150.5
        assert normalized.name == "Budapest"

    def test_to_dict(self) -> None:
        """to_dict converts GeoPoint to dictionary."""
        point = GeoPoint(latitude=47.4979, longitude=19.0402, altitude=150.5, name="Budapest")
        result = point.to_dict()
        assert result == {
            "latitude": 47.4979,
            "longitude": 19.0402,
            "altitude": 150.5,
            "name": "Budapest",
        }

    def test_to_dict_with_none_optional_fields(self) -> None:
        """to_dict includes None for optional fields."""
        point = GeoPoint(latitude=47.4979, longitude=19.0402)
        result = point.to_dict()
        assert result == {
            "latitude": 47.4979,
            "longitude": 19.0402,
            "altitude": None,
            "name": None,
        }

    def test_from_dict(self) -> None:
        """from_dict creates GeoPoint from dictionary."""
        data: dict[str, Any] = {
            "latitude": 47.4979,
            "longitude": 19.0402,
            "altitude": 150.5,
            "name": "Budapest",
        }
        point = GeoPoint.from_dict(data)
        assert point.latitude == 47.4979
        assert point.longitude == 19.0402
        assert point.altitude == 150.5
        assert point.name == "Budapest"

    def test_from_dict_with_missing_optional_fields(self) -> None:
        """from_dict handles missing optional fields."""
        data = {"latitude": 47.4979, "longitude": 19.0402}
        point = GeoPoint.from_dict(data)
        assert point.latitude == 47.4979
        assert point.longitude == 19.0402
        assert point.altitude is None
        assert point.name is None
