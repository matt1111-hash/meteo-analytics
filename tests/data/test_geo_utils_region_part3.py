"""Tests split from test_geo_utils_region.py."""

from __future__ import annotations

# ruff: noqa: F403, F405
from tests.data.test_geo_utils_region_support import *


class TestGeoUtilsRegionEdgeCases:
    """Edge case tests for GeoUtilsRegion."""

    def test_region_cache_updates(self, geo_utils: GeoUtilsRegion) -> None:
        """Region cache updates on new region calculation."""
        cities1 = [{"city": "A", "lat": 47.0, "lon": 19.0, "population": 1000}]
        cities2 = [{"city": "B", "lat": 48.0, "lon": 20.0, "population": 2000}]

        geo_utils.calculate_region_from_cities(cities1, "Region1")
        geo_utils.calculate_region_from_cities(cities2, "Region2")

        assert len(geo_utils.region_cache) == 2
        assert "Region1" in geo_utils.region_cache
        assert "Region2" in geo_utils.region_cache

    def test_proximity_grouping_with_many_cities(
        self, geo_utils: GeoUtilsRegion
    ) -> None:
        """Proximity grouping handles many cities."""
        # Create a chain of nearby cities
        cities = [
            {"city": f"City{i}", "lat": 47.0 + i * 0.05, "lon": 19.0} for i in range(20)
        ]

        groups = geo_utils.group_cities_by_proximity(cities, max_distance_km=50)

        # Should group all nearby cities together
        total_cities = sum(len(g) for g in groups)
        assert total_cities == 20

    def test_optimal_selection_with_all_same_population(
        self, geo_utils: GeoUtilsRegion
    ) -> None:
        """Optimal selection handles cities with same population."""
        cities = [
            {"city": f"City{i}", "lat": 47.0 + i * 0.1, "lon": 19.0, "population": 1000}
            for i in range(5)
        ]

        result = geo_utils.find_optimal_cities_for_region(cities, target_count=3)

        assert len(result) == 3
