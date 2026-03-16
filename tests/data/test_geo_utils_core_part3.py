"""Tests split from test_geo_utils_core.py."""

from __future__ import annotations

# ruff: noqa: F403, F405
from tests.data.test_geo_utils_core_support import *


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
