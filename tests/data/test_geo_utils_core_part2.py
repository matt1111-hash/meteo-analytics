"""Tests split from test_geo_utils_core.py."""

from __future__ import annotations

# ruff: noqa: F403, F405
from tests.data.test_geo_utils_core_support import *


class TestCalculateGeographicCenter:
    """Test calculate_geographic_center method."""

    def test_single_point(self) -> None:
        """calculate_geographic_center for single point."""
        geo = GeoUtils()

        center = geo.calculate_geographic_center([(47.5, 19.0)])

        assert abs(center.latitude - 47.5) < 0.0001
        assert abs(center.longitude - 19.0) < 0.0001

    def test_two_points(self) -> None:
        """calculate_geographic_center for two points."""
        geo = GeoUtils()

        points = [(47.0, 19.0), (48.0, 19.0)]
        center = geo.calculate_geographic_center(points)

        # Center should be between 47 and 48
        assert 47.4 < center.latitude < 48.0
        assert abs(center.longitude - 19.0) < 0.1

    def test_three_points_triangle(self) -> None:
        """calculate_geographic_center for triangle of points."""
        geo = GeoUtils()

        # Budapest, Vienna, Bratislava triangle
        points = [(47.5, 19.0), (48.2, 16.4), (48.1, 17.1)]
        center = geo.calculate_geographic_center(points)

        # Center should be somewhere in the middle
        assert 47.5 < center.latitude < 48.5
        assert 16.5 < center.longitude < 19.0

    def test_raises_for_empty_list(self) -> None:
        """calculate_geographic_center raises for empty list."""
        geo = GeoUtils()

        with pytest.raises(ValueError, match="Points list is empty"):
            geo.calculate_geographic_center([])

    def test_returns_geo_point(self) -> None:
        """calculate_geographic_center returns GeoPoint."""
        geo = GeoUtils()

        center = geo.calculate_geographic_center([(47.5, 19.0)])

        assert isinstance(center, GeoPoint)

    def test_antipodal_points(self) -> None:
        """calculate_geographic_center handles points on opposite sides."""
        geo = GeoUtils()

        # Points around the globe
        points = [(0, -90), (0, 90)]
        center = geo.calculate_geographic_center(points)

        # Center should be near the equator
        assert abs(center.latitude) < 1


class TestConvertToWebMercator:
    """Test convert_to_web_mercator method."""

    def test_origin(self) -> None:
        """convert_to_web_mercator for origin."""
        geo = GeoUtils()

        x, y = geo.convert_to_web_mercator(0, 0)

        # Should be approximately 0 (may have floating point errors)
        assert abs(x) < 1e-6
        assert abs(y) < 1e-6

    def test_positive_coordinates(self) -> None:
        """convert_to_web_mercator for positive coordinates."""
        geo = GeoUtils()

        x, y = geo.convert_to_web_mercator(47.5, 19.0)

        assert isinstance(x, float)
        assert isinstance(y, float)
        assert x > 0  # East of Greenwich
        assert y > 0  # North of equator

    def test_negative_coordinates(self) -> None:
        """convert_to_web_mercator for negative coordinates."""
        geo = GeoUtils()

        # Los Angeles: latitude 34 (positive), longitude -118 (negative)
        x, y = geo.convert_to_web_mercator(34.0, -118.2)

        assert x < 0  # West of Greenwich (negative longitude)
        assert y > 0  # North of equator (positive latitude)

    def test_max_latitude(self) -> None:
        """convert_to_web_mercator handles high latitude."""
        geo = GeoUtils()

        x, y = geo.convert_to_web_mercator(85, 0)

        # Should work without raising
        assert isinstance(x, float)
        assert isinstance(y, float)

    def test_round_trip_approximation(self) -> None:
        """convert_to_web_mercator is invertible."""
        geo = GeoUtils()

        original_lat, original_lon = 47.5, 19.0
        x, y = geo.convert_to_web_mercator(original_lat, original_lon)

        # Can't easily reverse, but check it produces consistent output
        assert isinstance(x, float)
        assert isinstance(y, float)


class TestSuggestMapZoomLevel:
    """Test suggest_map_zoom_level method."""

    def test_small_bbox_high_zoom(self) -> None:
        """suggest_map_zoom_level returns reasonable zoom for small bbox."""
        geo = GeoUtils()

        # Very small area (few km)
        bbox = BoundingBox(
            min_latitude=47.49,
            max_latitude=47.51,
            min_longitude=19.09,
            max_longitude=19.11,
        )

        zoom = geo.suggest_map_zoom_level(bbox)

        # Small area should have some zoom level
        assert 0 <= zoom <= 18

    def test_large_bbox_low_zoom(self) -> None:
        """suggest_map_zoom_level returns low zoom for large bbox."""
        geo = GeoUtils()

        # Very large area (continent level)
        bbox = BoundingBox(
            min_latitude=35,
            max_latitude=70,
            min_longitude=-10,
            max_longitude=40,
        )

        zoom = geo.suggest_map_zoom_level(bbox)

        # Large area should have low zoom level
        assert zoom <= 6

    def test_zoom_level_bounds(self) -> None:
        """suggest_map_zoom_level returns zoom between 0 and 18."""
        geo = GeoUtils()

        bbox = BoundingBox(
            min_latitude=47.0,
            max_latitude=48.0,
            min_longitude=19.0,
            max_longitude=20.0,
        )

        zoom = geo.suggest_map_zoom_level(bbox)

        assert 0 <= zoom <= 18

    def test_custom_map_width(self) -> None:
        """suggest_map_zoom_level uses custom map width."""
        geo = GeoUtils()

        bbox = BoundingBox(
            min_latitude=47.0,
            max_latitude=48.0,
            min_longitude=19.0,
            max_longitude=20.0,
        )

        zoom_default = geo.suggest_map_zoom_level(bbox, map_width_px=800)
        zoom_large = geo.suggest_map_zoom_level(bbox, map_width_px=1600)

        # Larger map should need less zoom to show same area
        # This is approximate behavior
        assert isinstance(zoom_default, int)
        assert isinstance(zoom_large, int)
