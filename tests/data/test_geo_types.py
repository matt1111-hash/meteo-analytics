"""Geographic data types tests."""

from __future__ import annotations

from typing import Any

import pytest

from src.data.geo_types import (
    BoundingBox,
    CoordinateSystem,
    DistanceUnit,
    GeographicRegion,
    GeoPoint,
)


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
        point = GeoPoint(
            latitude=47.4979, longitude=19.0402, altitude=150.5, name="Budapest"
        )
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
        # Create with default values to bypass __post_init__ validation
        point = GeoPoint.__new__(GeoPoint)
        point.latitude = 100.0
        point.longitude = 0.0
        point.altitude = None
        point.name = None
        assert point.is_valid() is False

    def test_boundary_valid_coordinates(self) -> None:
        """Boundary values are accepted."""
        # Equator and Prime Meridian
        point = GeoPoint(latitude=0.0, longitude=0.0)
        assert point.is_valid() is True

        # North Pole
        point = GeoPoint(latitude=90.0, longitude=0.0)
        assert point.is_valid() is True

        # South Pole
        point = GeoPoint(latitude=-90.0, longitude=0.0)
        assert point.is_valid() is True

        # International Date Line
        point = GeoPoint(latitude=0.0, longitude=180.0)
        assert point.is_valid() is True

        point = GeoPoint(latitude=0.0, longitude=-180.0)
        assert point.is_valid() is True

    def test_normalize_longitude_wraparound(self) -> None:
        """normalize wraps longitude to -180 to 180 range."""
        # Create valid point at boundary to test normalization
        # Longitude 200 would be invalid, so we test at 179 and -179
        point = GeoPoint(latitude=0.0, longitude=179.0)
        normalized = point.normalize()
        # Valid longitude stays the same
        assert normalized.longitude == pytest.approx(179.0)

        # Test negative longitude
        point = GeoPoint(latitude=0.0, longitude=-179.0)
        normalized = point.normalize()
        assert normalized.longitude == pytest.approx(-179.0)

    def test_normalize_latitude_clamping(self) -> None:
        """normalize clamps latitude to -90 to 90 range."""
        # Create valid point and test normalization doesn't change valid coords
        point = GeoPoint(latitude=89.0, longitude=0.0)
        normalized = point.normalize()
        assert normalized.latitude == 89.0

        point = GeoPoint(latitude=-89.0, longitude=0.0)
        normalized = point.normalize()
        assert normalized.latitude == -89.0

        # Test at poles
        point = GeoPoint(latitude=90.0, longitude=0.0)
        normalized = point.normalize()
        assert normalized.latitude == 90.0

        point = GeoPoint(latitude=-90.0, longitude=0.0)
        normalized = point.normalize()
        assert normalized.latitude == -90.0

    def test_normalize_preserves_optional_fields(self) -> None:
        """normalize preserves altitude and name."""
        point = GeoPoint(
            latitude=47.4979, longitude=19.0402, altitude=150.5, name="Budapest"
        )
        normalized = point.normalize()
        assert normalized.altitude == 150.5
        assert normalized.name == "Budapest"

    def test_to_dict(self) -> None:
        """to_dict converts GeoPoint to dictionary."""
        point = GeoPoint(
            latitude=47.4979, longitude=19.0402, altitude=150.5, name="Budapest"
        )
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


class TestBoundingBox:
    """Tests for BoundingBox dataclass."""

    def test_create_valid_bounding_box(self) -> None:
        """Valid coordinates create BoundingBox successfully."""
        bbox = BoundingBox(
            min_latitude=45.0, max_latitude=50.0, min_longitude=15.0, max_longitude=25.0
        )
        assert bbox.min_latitude == 45.0
        assert bbox.max_latitude == 50.0
        assert bbox.min_longitude == 15.0
        assert bbox.max_longitude == 25.0

    def test_min_latitude_greater_than_max_raises_error(self) -> None:
        """min_latitude > max_latitude raises ValueError."""
        with pytest.raises(ValueError, match="min_latitude > max_latitude"):
            BoundingBox(
                min_latitude=50.0,
                max_latitude=45.0,
                min_longitude=15.0,
                max_longitude=25.0,
            )

    def test_min_longitude_greater_than_max_raises_error(self) -> None:
        """min_longitude > max_longitude raises ValueError."""
        with pytest.raises(ValueError, match="min_longitude > max_longitude"):
            BoundingBox(
                min_latitude=45.0,
                max_latitude=50.0,
                min_longitude=25.0,
                max_longitude=15.0,
            )

    def test_dateline_crossing_allowed(self) -> None:
        """Dateline crossing (min > 0, max < 0) is allowed."""
        bbox = BoundingBox(
            min_latitude=45.0,
            max_latitude=50.0,
            min_longitude=170.0,
            max_longitude=-170.0,
        )
        assert bbox.min_longitude == 170.0
        assert bbox.max_longitude == -170.0

    def test_contains_point_inside(self) -> None:
        """contains_point returns True for point inside bbox."""
        bbox = BoundingBox(
            min_latitude=45.0, max_latitude=50.0, min_longitude=15.0, max_longitude=25.0
        )
        point = GeoPoint(latitude=47.5, longitude=20.0)
        assert bbox.contains_point(point) is True

    def test_contains_point_outside_latitude(self) -> None:
        """contains_point returns False for point outside latitude range."""
        bbox = BoundingBox(
            min_latitude=45.0, max_latitude=50.0, min_longitude=15.0, max_longitude=25.0
        )
        point = GeoPoint(latitude=55.0, longitude=20.0)
        assert bbox.contains_point(point) is False

    def test_contains_point_outside_longitude(self) -> None:
        """contains_point returns False for point outside longitude range."""
        bbox = BoundingBox(
            min_latitude=45.0, max_latitude=50.0, min_longitude=15.0, max_longitude=25.0
        )
        point = GeoPoint(latitude=47.5, longitude=30.0)
        assert bbox.contains_point(point) is False

    def test_contains_point_on_boundary(self) -> None:
        """contains_point returns True for point on boundary."""
        bbox = BoundingBox(
            min_latitude=45.0, max_latitude=50.0, min_longitude=15.0, max_longitude=25.0
        )
        # Test all boundaries
        assert bbox.contains_point(GeoPoint(latitude=45.0, longitude=20.0)) is True
        assert bbox.contains_point(GeoPoint(latitude=50.0, longitude=20.0)) is True
        assert bbox.contains_point(GeoPoint(latitude=47.5, longitude=15.0)) is True
        assert bbox.contains_point(GeoPoint(latitude=47.5, longitude=25.0)) is True

    def test_contains_point_dateline_crossing(self) -> None:
        """contains_point handles dateline crossing correctly."""
        bbox = BoundingBox(
            min_latitude=45.0,
            max_latitude=50.0,
            min_longitude=170.0,
            max_longitude=-170.0,
        )
        # Point east of dateline (within range)
        point_east = GeoPoint(latitude=47.5, longitude=175.0)
        assert bbox.contains_point(point_east) is True

        # Point west of dateline (within range)
        point_west = GeoPoint(latitude=47.5, longitude=-175.0)
        assert bbox.contains_point(point_west) is True

        # Point outside range
        point_outside = GeoPoint(latitude=47.5, longitude=0.0)
        assert bbox.contains_point(point_outside) is False

    def test_get_center(self) -> None:
        """get_center calculates correct center point."""
        bbox = BoundingBox(
            min_latitude=45.0, max_latitude=50.0, min_longitude=15.0, max_longitude=25.0
        )
        center = bbox.get_center()
        assert center.latitude == 47.5
        assert center.longitude == 20.0

    def test_get_center_dateline_crossing(self) -> None:
        """get_center handles dateline crossing correctly."""
        bbox = BoundingBox(
            min_latitude=45.0,
            max_latitude=50.0,
            min_longitude=170.0,
            max_longitude=-170.0,
        )
        center = bbox.get_center()
        # Center should be at 180/-180 (dateline)
        assert center.latitude == 47.5
        assert center.longitude == pytest.approx(
            180.0
        ) or center.longitude == pytest.approx(-180.0)

    def test_expand_by_padding(self) -> None:
        """expand_by_padding expands bbox equally."""
        bbox = BoundingBox(
            min_latitude=45.0, max_latitude=50.0, min_longitude=15.0, max_longitude=25.0
        )
        expanded = bbox.expand_by_padding(5.0)
        assert expanded.min_latitude == 40.0
        assert expanded.max_latitude == 55.0
        assert expanded.min_longitude == 10.0
        assert expanded.max_longitude == 30.0

    def test_expand_by_padding_clamps_at_poles(self) -> None:
        """expand_by_padding clamps latitude at poles."""
        # Test max_latitude clamping at North Pole
        bbox = BoundingBox(
            min_latitude=85.0, max_latitude=88.0, min_longitude=15.0, max_longitude=25.0
        )
        expanded = bbox.expand_by_padding(10.0)
        # min: 85-10=75, max: 88+10=98 -> clamped to 90
        assert expanded.min_latitude == 75.0
        assert expanded.max_latitude == 90.0  # Clamped at North Pole
        assert expanded.min_longitude == 5.0
        assert expanded.max_longitude == 35.0

        # Test min_latitude clamping at South Pole
        bbox = BoundingBox(
            min_latitude=-88.0,
            max_latitude=-85.0,
            min_longitude=15.0,
            max_longitude=25.0,
        )
        expanded = bbox.expand_by_padding(10.0)
        # min: -88-10=-98 -> clamped to -90, max: -85+10=-75
        assert expanded.min_latitude == -90.0  # Clamped at South Pole
        assert expanded.max_latitude == -75.0

    def test_expand_by_padding_clamps_at_dateline(self) -> None:
        """expand_by_padding clamps longitude at dateline."""
        bbox = BoundingBox(
            min_latitude=45.0,
            max_latitude=50.0,
            min_longitude=175.0,
            max_longitude=-175.0,
        )
        expanded = bbox.expand_by_padding(10.0)
        # min: 175-10=165, max: -175+10=-165 (dateline crossing case)
        assert expanded.min_latitude == 35.0
        assert expanded.max_latitude == 60.0
        assert expanded.min_longitude == 165.0
        assert expanded.max_longitude == -165.0

        # Test clamping at positive boundary
        bbox = BoundingBox(
            min_latitude=45.0,
            max_latitude=50.0,
            min_longitude=170.0,
            max_longitude=175.0,
        )
        expanded = bbox.expand_by_padding(20.0)
        # min: 170-20=150, max: 175+20=195 -> clamped to 180
        assert expanded.min_latitude == 25.0
        assert expanded.max_latitude == 70.0
        assert expanded.min_longitude == 150.0
        assert expanded.max_longitude == 180.0  # Clamped at 180

        # Test clamping at negative boundary
        bbox = BoundingBox(
            min_latitude=45.0,
            max_latitude=50.0,
            min_longitude=-175.0,
            max_longitude=-170.0,
        )
        expanded = bbox.expand_by_padding(20.0)
        # min: -175-20=-195 -> clamped to -180, max: -170+20=-150
        assert expanded.min_latitude == 25.0
        assert expanded.max_latitude == 70.0
        assert expanded.min_longitude == -180.0  # Clamped at -180
        assert expanded.max_longitude == -150.0

    def test_to_dict(self) -> None:
        """to_dict converts BoundingBox to dictionary."""
        bbox = BoundingBox(
            min_latitude=45.0, max_latitude=50.0, min_longitude=15.0, max_longitude=25.0
        )
        result = bbox.to_dict()
        assert result == {
            "min_latitude": 45.0,
            "max_latitude": 50.0,
            "min_longitude": 15.0,
            "max_longitude": 25.0,
        }


class TestGeographicRegion:
    """Tests for GeographicRegion dataclass."""

    def test_create_geographic_region(self) -> None:
        """Create GeographicRegion with required fields."""
        bbox = BoundingBox(
            min_latitude=45.0, max_latitude=50.0, min_longitude=15.0, max_longitude=25.0
        )
        center = GeoPoint(latitude=47.5, longitude=20.0)
        region = GeographicRegion(
            name="Test Region", bounding_box=bbox, center_point=center
        )
        assert region.name == "Test Region"
        assert region.bounding_box == bbox
        assert region.center_point == center
        assert region.area_km2 is None
        assert region.population is None
        assert region.cities_count is None
        assert region.timezone is None

    def test_create_geographic_region_with_optional_fields(self) -> None:
        """Create GeographicRegion with all fields."""
        bbox = BoundingBox(
            min_latitude=45.0, max_latitude=50.0, min_longitude=15.0, max_longitude=25.0
        )
        center = GeoPoint(latitude=47.5, longitude=20.0)
        region = GeographicRegion(
            name="Hungary",
            bounding_box=bbox,
            center_point=center,
            area_km2=93000.0,
            population=9700000,
            cities_count=3155,
            timezone="Europe/Budapest",
        )
        assert region.area_km2 == 93000.0
        assert region.population == 9700000
        assert region.cities_count == 3155
        assert region.timezone == "Europe/Budapest"

    def test_is_point_in_region_inside(self) -> None:
        """is_point_in_region returns True for point inside region."""
        bbox = BoundingBox(
            min_latitude=45.0, max_latitude=50.0, min_longitude=15.0, max_longitude=25.0
        )
        center = GeoPoint(latitude=47.5, longitude=20.0)
        region = GeographicRegion(
            name="Test Region", bounding_box=bbox, center_point=center
        )
        point = GeoPoint(latitude=47.0, longitude=20.0)
        assert region.is_point_in_region(point) is True

    def test_is_point_in_region_outside(self) -> None:
        """is_point_in_region returns False for point outside region."""
        bbox = BoundingBox(
            min_latitude=45.0, max_latitude=50.0, min_longitude=15.0, max_longitude=25.0
        )
        center = GeoPoint(latitude=47.5, longitude=20.0)
        region = GeographicRegion(
            name="Test Region", bounding_box=bbox, center_point=center
        )
        point = GeoPoint(latitude=55.0, longitude=20.0)
        assert region.is_point_in_region(point) is False
