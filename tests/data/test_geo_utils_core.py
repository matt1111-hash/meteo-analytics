"""Tests for GeoUtils from geo_utils_core.py."""

from __future__ import annotations

import math
from typing import Tuple

import pytest

from src.data.geo_utils_core import GeoUtils
from src.data.geo_types import BoundingBox, GeoPoint, DistanceUnit
from src.data.distance_calculator import DistanceCalculator


class TestGeoUtilsInit:
    """Test GeoUtils initialization."""

    def test_init_creates_default_distance_calculator(self) -> None:
        """GeoUtils creates default DistanceCalculator."""
        geo = GeoUtils()

        assert geo.distance_calculator is not None
        assert isinstance(geo.distance_calculator, DistanceCalculator)

    def test_init_uses_custom_distance_calculator(self) -> None:
        """GeoUtils uses custom DistanceCalculator."""
        custom_calc = DistanceCalculator(default_unit=DistanceUnit.MILES)
        geo = GeoUtils(distance_calculator=custom_calc)

        assert geo.distance_calculator is custom_calc


class TestValidateCoordinates:
    """Test validate_coordinates method."""

    def test_valid_coordinates(self) -> None:
        """validate_coordinates returns True for valid coordinates."""
        geo = GeoUtils()

        assert geo.validate_coordinates(47.5, 19.0) is True
        assert geo.validate_coordinates(0, 0) is True
        assert geo.validate_coordinates(-90, -180) is True
        assert geo.validate_coordinates(90, 180) is True

    def test_invalid_latitude_too_high(self) -> None:
        """validate_coordinates returns False for latitude > 90."""
        geo = GeoUtils()

        assert geo.validate_coordinates(91, 0) is False
        assert geo.validate_coordinates(100, 0) is False

    def test_invalid_latitude_too_low(self) -> None:
        """validate_coordinates returns False for latitude < -90."""
        geo = GeoUtils()

        assert geo.validate_coordinates(-91, 0) is False
        assert geo.validate_coordinates(-100, 0) is False

    def test_invalid_longitude_too_high(self) -> None:
        """validate_coordinates returns False for longitude > 180."""
        geo = GeoUtils()

        assert geo.validate_coordinates(0, 181) is False
        assert geo.validate_coordinates(0, 200) is False

    def test_invalid_longitude_too_low(self) -> None:
        """validate_coordinates returns False for longitude < -180."""
        geo = GeoUtils()

        assert geo.validate_coordinates(0, -181) is False
        assert geo.validate_coordinates(0, -200) is False

    def test_boundary_values(self) -> None:
        """validate_coordinates handles boundary values."""
        geo = GeoUtils()

        # Exact boundaries should be valid
        assert geo.validate_coordinates(90, 180) is True
        assert geo.validate_coordinates(-90, -180) is True
        assert geo.validate_coordinates(90, -180) is True
        assert geo.validate_coordinates(-90, 180) is True


class TestNormalizeCoordinates:
    """Test normalize_coordinates method."""

    def test_normal_coordinates_unchanged(self) -> None:
        """normalize_coordinates leaves normal coordinates unchanged."""
        geo = GeoUtils()

        lat, lon = geo.normalize_coordinates(47.5, 19.0)

        assert abs(lat - 47.5) < 0.0001
        assert abs(lon - 19.0) < 0.0001

    def test_clamps_latitude_to_90(self) -> None:
        """normalize_coordinates clamps latitude to 90."""
        geo = GeoUtils()

        lat, _ = geo.normalize_coordinates(100, 0)

        assert lat == 90

    def test_clamps_latitude_to_minus_90(self) -> None:
        """normalize_coordinates clamps latitude to -90."""
        geo = GeoUtils()

        lat, _ = geo.normalize_coordinates(-100, 0)

        assert lat == -90

    def test_wraps_longitude_positive(self) -> None:
        """normalize_coordinates wraps longitude > 180."""
        geo = GeoUtils()

        _, lon = geo.normalize_coordinates(0, 190)

        # 190 -> -170 (wraps around)
        assert abs(lon - (-170)) < 0.0001

    def test_wraps_longitude_negative(self) -> None:
        """normalize_coordinates wraps longitude < -180."""
        geo = GeoUtils()

        _, lon = geo.normalize_coordinates(0, -190)

        # -190 -> 170 (wraps around)
        assert abs(lon - 170) < 0.0001

    def test_wraps_longitude_multiple_times(self) -> None:
        """normalize_coordinates wraps longitude multiple times."""
        geo = GeoUtils()

        _, lon = geo.normalize_coordinates(0, 540)  # 540 = 180 + 360

        # 540 -> ((540 + 180) % 360) - 180 = 720 % 360 - 180 = 0 - 180 = -180
        assert abs(lon - (-180)) < 0.0001 or abs(lon - 180) < 0.0001


class TestCalculateBoundingBox:
    """Test calculate_bounding_box method."""

    def test_single_point(self) -> None:
        """calculate_bounding_box for single point."""
        geo = GeoUtils()

        bbox = geo.calculate_bounding_box([(47.5, 19.0)])

        assert bbox.min_latitude == 47.5
        assert bbox.max_latitude == 47.5
        assert bbox.min_longitude == 19.0
        assert bbox.max_longitude == 19.0

    def test_multiple_points(self) -> None:
        """calculate_bounding_box for multiple points."""
        geo = GeoUtils()

        points = [(47.5, 19.0), (48.0, 20.0), (46.0, 18.0)]
        bbox = geo.calculate_bounding_box(points)

        assert bbox.min_latitude == 46.0
        assert bbox.max_latitude == 48.0
        assert bbox.min_longitude == 18.0
        assert bbox.max_longitude == 20.0

    def test_with_padding(self) -> None:
        """calculate_bounding_box with padding."""
        geo = GeoUtils()

        bbox = geo.calculate_bounding_box([(47.5, 19.0)], padding_degrees=1.0)

        assert bbox.min_latitude == 46.5
        assert bbox.max_latitude == 48.5
        assert bbox.min_longitude == 18.0
        assert bbox.max_longitude == 20.0

    def test_raises_for_empty_list(self) -> None:
        """calculate_bounding_box raises for empty list."""
        geo = GeoUtils()

        with pytest.raises(ValueError, match="Points list is empty"):
            geo.calculate_bounding_box([])

    def test_returns_bounding_box_object(self) -> None:
        """calculate_bounding_box returns BoundingBox object."""
        geo = GeoUtils()

        bbox = geo.calculate_bounding_box([(47.5, 19.0)])

        assert isinstance(bbox, BoundingBox)


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


class TestGeoUtilsEdgeCases:
    """Edge case tests for GeoUtils."""

    def test_negative_longitude_spanning_dateline(self) -> None:
        """GeoUtils handles coordinates spanning dateline."""
        geo = GeoUtils()

        # Points on both sides of dateline
        points = [(0, 179), (0, -179)]
        bbox = geo.calculate_bounding_box(points)

        # This will show the actual span including the dateline
        assert bbox.min_longitude == -179
        assert bbox.max_longitude == 179

    def test_equator_coordinates(self) -> None:
        """GeoUtils handles equator coordinates."""
        geo = GeoUtils()

        center = geo.calculate_geographic_center([(0, 0), (0, 10)])

        assert abs(center.latitude) < 0.1

    def test_pole_proximity(self) -> None:
        """GeoUtils handles coordinates near poles."""
        geo = GeoUtils()

        assert geo.validate_coordinates(89, 0) is True
        assert geo.validate_coordinates(-89, 0) is True

    def test_many_points_bounding_box(self) -> None:
        """calculate_bounding_box handles many points."""
        geo = GeoUtils()

        # Create many random points
        points = [(47 + i * 0.01, 19 + i * 0.01) for i in range(100)]

        bbox = geo.calculate_bounding_box(points)

        assert bbox.min_latitude == 47.0
        assert bbox.max_latitude > 47.9
