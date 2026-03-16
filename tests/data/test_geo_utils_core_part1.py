"""Tests split from test_geo_utils_core.py."""

from __future__ import annotations

# ruff: noqa: F403, F405
from tests.data.test_geo_utils_core_support import *


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
