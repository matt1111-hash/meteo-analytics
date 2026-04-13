"""Geographic data types tests."""

from __future__ import annotations

import pytest
from src.data.geo_types import BoundingBox, GeoPoint


class TestBoundingBox:
    """Tests for BoundingBox dataclass."""

    def test_create_valid_bounding_box(self) -> None:
        bbox = BoundingBox(
            min_latitude=45.0, max_latitude=50.0, min_longitude=15.0, max_longitude=25.0
        )
        assert bbox.min_latitude == 45.0
        assert bbox.max_latitude == 50.0
        assert bbox.min_longitude == 15.0
        assert bbox.max_longitude == 25.0

    def test_min_latitude_greater_than_max_raises_error(self) -> None:
        with pytest.raises(ValueError, match="min_latitude > max_latitude"):
            BoundingBox(50.0, 45.0, 15.0, 25.0)

    def test_min_longitude_greater_than_max_raises_error(self) -> None:
        with pytest.raises(ValueError, match="min_longitude > max_longitude"):
            BoundingBox(45.0, 50.0, 25.0, 15.0)

    def test_dateline_crossing_allowed(self) -> None:
        bbox = BoundingBox(45.0, 50.0, 170.0, -170.0)
        assert bbox.min_longitude == 170.0
        assert bbox.max_longitude == -170.0

    def test_contains_point_inside(self) -> None:
        bbox = BoundingBox(45.0, 50.0, 15.0, 25.0)
        point = GeoPoint(latitude=47.5, longitude=20.0)
        assert bbox.contains_point(point) is True

    def test_contains_point_outside_latitude(self) -> None:
        bbox = BoundingBox(45.0, 50.0, 15.0, 25.0)
        point = GeoPoint(latitude=55.0, longitude=20.0)
        assert bbox.contains_point(point) is False

    def test_contains_point_outside_longitude(self) -> None:
        bbox = BoundingBox(45.0, 50.0, 15.0, 25.0)
        point = GeoPoint(latitude=47.5, longitude=30.0)
        assert bbox.contains_point(point) is False

    def test_contains_point_on_boundary(self) -> None:
        bbox = BoundingBox(45.0, 50.0, 15.0, 25.0)
        assert bbox.contains_point(GeoPoint(latitude=45.0, longitude=20.0)) is True
        assert bbox.contains_point(GeoPoint(latitude=50.0, longitude=20.0)) is True
        assert bbox.contains_point(GeoPoint(latitude=47.5, longitude=15.0)) is True
        assert bbox.contains_point(GeoPoint(latitude=47.5, longitude=25.0)) is True

    def test_contains_point_dateline_crossing(self) -> None:
        bbox = BoundingBox(45.0, 50.0, 170.0, -170.0)
        assert bbox.contains_point(GeoPoint(latitude=47.5, longitude=175.0)) is True
        assert bbox.contains_point(GeoPoint(latitude=47.5, longitude=-175.0)) is True
        assert bbox.contains_point(GeoPoint(latitude=47.5, longitude=0.0)) is False

    def test_get_center(self) -> None:
        bbox = BoundingBox(45.0, 50.0, 15.0, 25.0)
        center = bbox.get_center()
        assert center.latitude == 47.5
        assert center.longitude == 20.0

    def test_get_center_dateline_crossing(self) -> None:
        bbox = BoundingBox(45.0, 50.0, 170.0, -170.0)
        center = bbox.get_center()
        assert center.latitude == 47.5
        assert center.longitude == pytest.approx(180.0) or center.longitude == pytest.approx(-180.0)

    def test_expand_by_padding(self) -> None:
        bbox = BoundingBox(45.0, 50.0, 15.0, 25.0)
        expanded = bbox.expand_by_padding(5.0)
        assert expanded.min_latitude == 40.0
        assert expanded.max_latitude == 55.0
        assert expanded.min_longitude == 10.0
        assert expanded.max_longitude == 30.0

    def test_expand_by_padding_clamps_at_poles(self) -> None:
        bbox = BoundingBox(85.0, 88.0, 15.0, 25.0)
        expanded = bbox.expand_by_padding(10.0)
        assert expanded.min_latitude == 75.0
        assert expanded.max_latitude == 90.0
        assert expanded.min_longitude == 5.0
        assert expanded.max_longitude == 35.0

        bbox = BoundingBox(-88.0, -85.0, 15.0, 25.0)
        expanded = bbox.expand_by_padding(10.0)
        assert expanded.min_latitude == -90.0
        assert expanded.max_latitude == -75.0

    def test_expand_by_padding_clamps_at_dateline(self) -> None:
        bbox = BoundingBox(45.0, 50.0, 175.0, -175.0)
        expanded = bbox.expand_by_padding(10.0)
        assert expanded.min_latitude == 35.0
        assert expanded.max_latitude == 60.0
        assert expanded.min_longitude == 165.0
        assert expanded.max_longitude == -165.0

        bbox = BoundingBox(45.0, 50.0, 170.0, 175.0)
        expanded = bbox.expand_by_padding(20.0)
        assert expanded.max_longitude == 180.0

        bbox = BoundingBox(45.0, 50.0, -175.0, -170.0)
        expanded = bbox.expand_by_padding(20.0)
        assert expanded.min_longitude == -180.0
        assert expanded.max_longitude == -150.0

    def test_to_dict(self) -> None:
        bbox = BoundingBox(45.0, 50.0, 15.0, 25.0)
        result = bbox.to_dict()
        assert result == {
            "min_latitude": 45.0,
            "max_latitude": 50.0,
            "min_longitude": 15.0,
            "max_longitude": 25.0,
        }
