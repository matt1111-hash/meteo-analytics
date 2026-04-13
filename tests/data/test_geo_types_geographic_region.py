"""Geographic data types tests."""

from __future__ import annotations

from src.data.geo_types import BoundingBox, GeographicRegion, GeoPoint


class TestGeographicRegion:
    """Tests for GeographicRegion dataclass."""

    def test_create_geographic_region(self) -> None:
        bbox = BoundingBox(45.0, 50.0, 15.0, 25.0)
        center = GeoPoint(latitude=47.5, longitude=20.0)
        region = GeographicRegion(name="Test Region", bounding_box=bbox, center_point=center)
        assert region.name == "Test Region"
        assert region.bounding_box == bbox
        assert region.center_point == center
        assert region.area_km2 is None
        assert region.population is None
        assert region.cities_count is None
        assert region.timezone is None

    def test_create_geographic_region_with_optional_fields(self) -> None:
        bbox = BoundingBox(45.0, 50.0, 15.0, 25.0)
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
        bbox = BoundingBox(45.0, 50.0, 15.0, 25.0)
        center = GeoPoint(latitude=47.5, longitude=20.0)
        region = GeographicRegion(name="Test Region", bounding_box=bbox, center_point=center)
        point = GeoPoint(latitude=47.0, longitude=20.0)
        assert region.is_point_in_region(point) is True

    def test_is_point_in_region_outside(self) -> None:
        bbox = BoundingBox(45.0, 50.0, 15.0, 25.0)
        center = GeoPoint(latitude=47.5, longitude=20.0)
        region = GeographicRegion(name="Test Region", bounding_box=bbox, center_point=center)
        point = GeoPoint(latitude=55.0, longitude=20.0)
        assert region.is_point_in_region(point) is False
