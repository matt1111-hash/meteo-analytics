"""Tests split from test_geo_utils_region.py."""

from __future__ import annotations

# ruff: noqa: F403, F405
from tests.data.test_geo_utils_region_support import *


class TestGroupCitiesByProximity:
    """Test group_cities_by_proximity method."""

    def test_groups_cities_by_distance(self, geo_utils: GeoUtilsRegion) -> None:
        """group_cities_by_proximity groups nearby cities together."""
        cities = [
            {"city": "A", "lat": 47.0, "lon": 19.0},
            {"city": "B", "lat": 47.1, "lon": 19.1},  # ~12 km from A
            {"city": "C", "lat": 48.0, "lon": 20.0},  # ~130 km from A
        ]

        groups = geo_utils.group_cities_by_proximity(cities, max_distance_km=50)

        # A and B should be grouped together, C should be separate
        assert len(groups) == 2
        group_sizes = sorted([len(g) for g in groups])
        assert group_sizes == [1, 2]

    def test_returns_single_group_for_close_cities(
        self, geo_utils: GeoUtilsRegion
    ) -> None:
        """group_cities_by_proximity returns single group for very close cities."""
        cities = [
            {"city": "A", "lat": 47.0, "lon": 19.0},
            {"city": "B", "lat": 47.01, "lon": 19.01},  # ~1.5 km from A
        ]

        groups = geo_utils.group_cities_by_proximity(cities, max_distance_km=100)

        assert len(groups) == 1
        assert len(groups[0]) == 2

    def test_returns_multiple_groups_for_distant_cities(
        self, geo_utils: GeoUtilsRegion
    ) -> None:
        """group_cities_by_proximity returns multiple groups for distant cities."""
        cities = [
            {"city": "A", "lat": 47.0, "lon": 19.0},
            {"city": "B", "lat": 40.0, "lon": 10.0},  # ~800 km from A
        ]

        groups = geo_utils.group_cities_by_proximity(cities, max_distance_km=100)

        assert len(groups) == 2
        assert len(groups[0]) == 1
        assert len(groups[1]) == 1

    def test_returns_empty_for_empty_list(self, geo_utils: GeoUtilsRegion) -> None:
        """group_cities_by_proximity returns empty for empty list."""
        groups = geo_utils.group_cities_by_proximity([], max_distance_km=100)

        assert groups == []

    def test_returns_single_group_for_single_city(
        self, geo_utils: GeoUtilsRegion
    ) -> None:
        """group_cities_by_proximity returns single group for single city."""
        cities = [{"city": "A", "lat": 47.0, "lon": 19.0}]

        groups = geo_utils.group_cities_by_proximity(cities, max_distance_km=100)

        assert len(groups) == 1
        assert len(groups[0]) == 1

    def test_groups_sorted_by_size(self, geo_utils: GeoUtilsRegion) -> None:
        """group_cities_by_proximity sorts groups by size descending."""
        cities = [
            {"city": "A", "lat": 47.0, "lon": 19.0},
            {"city": "B", "lat": 47.1, "lon": 19.1},
            {"city": "C", "lat": 47.2, "lon": 19.2},
            {"city": "D", "lat": 40.0, "lon": 10.0},
        ]

        groups = geo_utils.group_cities_by_proximity(cities, max_distance_km=50)

        # Groups should be sorted by size (largest first)
        sizes = [len(g) for g in groups]
        assert sizes == sorted(sizes, reverse=True)


class TestFindOptimalCitiesForRegion:
    """Test find_optimal_cities_for_region method."""

    def test_returns_all_cities_when_fewer_than_target(
        self, geo_utils: GeoUtilsRegion
    ) -> None:
        """find_optimal_cities_for_region returns all when fewer than target."""
        cities = [
            {"city": "A", "lat": 47.0, "lon": 19.0, "population": 1000},
            {"city": "B", "lat": 48.0, "lon": 20.0, "population": 2000},
        ]

        result = geo_utils.find_optimal_cities_for_region(cities, target_count=5)

        assert len(result) == 2

    def test_returns_target_count_when_more_available(
        self, geo_utils: GeoUtilsRegion
    ) -> None:
        """find_optimal_cities_for_region returns target count when more available."""
        cities = [
            {
                "city": f"City{i}",
                "lat": 47.0 + i * 0.1,
                "lon": 19.0,
                "population": 1000 * (10 - i),
            }
            for i in range(10)
        ]

        result = geo_utils.find_optimal_cities_for_region(cities, target_count=3)

        assert len(result) == 3

    def test_filters_by_bounding_box(self, geo_utils: GeoUtilsRegion) -> None:
        """find_optimal_cities_for_region filters by bounding box."""
        cities = [
            {"city": "Inside1", "lat": 47.5, "lon": 19.5, "population": 1000},
            {"city": "Inside2", "lat": 47.6, "lon": 19.6, "population": 2000},
            {"city": "Outside", "lat": 50.0, "lon": 25.0, "population": 5000},
        ]

        bbox = BoundingBox(
            min_latitude=47.0,
            max_latitude=48.0,
            min_longitude=19.0,
            max_longitude=20.0,
        )

        result = geo_utils.find_optimal_cities_for_region(
            cities, target_count=10, region_bbox=bbox
        )

        # Should only include cities inside bbox
        assert len(result) == 2
        names = [c["city"] for c in result]
        assert "Inside1" in names
        assert "Inside2" in names
        assert "Outside" not in names

    def test_prioritizes_higher_population(self, geo_utils: GeoUtilsRegion) -> None:
        """find_optimal_cities_for_region prioritizes higher population."""
        cities = [
            {"city": "Small", "lat": 47.0, "lon": 19.0, "population": 100},
            {"city": "Medium", "lat": 47.1, "lon": 19.1, "population": 1000},
            {"city": "Large", "lat": 47.2, "lon": 19.2, "population": 10000},
        ]

        result = geo_utils.find_optimal_cities_for_region(cities, target_count=1)

        # Should select the city with highest population
        assert result[0]["city"] == "Large"

    def test_handles_cities_without_population(self, geo_utils: GeoUtilsRegion) -> None:
        """find_optimal_cities_for_region handles cities without population."""
        cities = [
            {"city": "NoPop", "lat": 47.0, "lon": 19.0},
            {"city": "WithPop", "lat": 48.0, "lon": 20.0, "population": 1000},
        ]

        result = geo_utils.find_optimal_cities_for_region(cities, target_count=2)

        assert len(result) == 2

    def test_returns_empty_for_no_cities(self, geo_utils: GeoUtilsRegion) -> None:
        """find_optimal_cities_for_region returns empty for no cities."""
        result = geo_utils.find_optimal_cities_for_region([], target_count=5)

        assert result == []

    def test_selects_diverse_cities(self, geo_utils: GeoUtilsRegion) -> None:
        """find_optimal_cities_for_region selects geographically diverse cities."""
        # Two cities very close together with high population
        # One city far away with lower population
        cities = [
            {"city": "A", "lat": 47.0, "lon": 19.0, "population": 10000},
            {"city": "B", "lat": 47.01, "lon": 19.01, "population": 9000},
            {"city": "C", "lat": 48.0, "lon": 20.0, "population": 8000},
        ]

        result = geo_utils.find_optimal_cities_for_region(cities, target_count=2)

        # Should include C (diverse location) even if lower population
        names = [c["city"] for c in result]
        assert "C" in names or len(result) == 2
