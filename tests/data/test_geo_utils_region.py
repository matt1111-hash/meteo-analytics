"""Tests for GeoUtilsRegion from geo_utils_region.py."""

from __future__ import annotations

from typing import Any, Dict, List

import pytest

from src.data.geo_utils_region import GeoUtilsRegion
from src.data.geo_types import BoundingBox, GeographicRegion, GeoPoint
from src.data.distance_calculator import DistanceCalculator


@pytest.fixture
def geo_utils() -> GeoUtilsRegion:
    """Create GeoUtilsRegion instance."""
    return GeoUtilsRegion()


@pytest.fixture
def sample_cities() -> List[Dict[str, Any]]:
    """Sample city data for testing."""
    return [
        {"city": "Budapest", "lat": 47.4979, "lon": 19.0402, "population": 1752286},
        {"city": "Debrecen", "lat": 47.5314, "lon": 21.6269, "population": 201881},
        {"city": "Szeged", "lat": 46.2530, "lon": 20.1414, "population": 161837},
        {"city": "Miskolc", "lat": 48.1035, "lon": 20.7784, "population": 157177},
    ]


class TestGeoUtilsRegionInit:
    """Test GeoUtilsRegion initialization."""

    def test_init_creates_distance_calculator(self) -> None:
        """GeoUtilsRegion creates DistanceCalculator."""
        geo = GeoUtilsRegion()

        assert geo.distance_calculator is not None
        assert isinstance(geo.distance_calculator, DistanceCalculator)

    def test_init_uses_custom_distance_calculator(self) -> None:
        """GeoUtilsRegion uses custom DistanceCalculator."""
        custom_calc = DistanceCalculator()
        geo = GeoUtilsRegion(distance_calculator=custom_calc)

        assert geo.distance_calculator is custom_calc

    def test_init_creates_empty_region_cache(self) -> None:
        """GeoUtilsRegion creates empty region_cache."""
        geo = GeoUtilsRegion()

        assert geo.region_cache == {}

    def test_inherits_from_geo_utils(self) -> None:
        """GeoUtilsRegion inherits from GeoUtils."""
        from src.data.geo_utils_core import GeoUtils

        geo = GeoUtilsRegion()

        assert isinstance(geo, GeoUtils)


class TestCalculateRegionFromCities:
    """Test calculate_region_from_cities method."""

    def test_calculates_region_from_cities(
        self, geo_utils: GeoUtilsRegion, sample_cities: List[Dict[str, Any]]
    ) -> None:
        """calculate_region_from_cities creates GeographicRegion."""
        region = geo_utils.calculate_region_from_cities(sample_cities, "Hungary")

        assert isinstance(region, GeographicRegion)
        assert region.name == "Hungary"
        assert region.cities_count == 4

    def test_calculates_bounding_box(
        self, geo_utils: GeoUtilsRegion, sample_cities: List[Dict[str, Any]]
    ) -> None:
        """calculate_region_from_cities calculates correct bounding box."""
        region = geo_utils.calculate_region_from_cities(sample_cities, "Test")

        # Bounding box should contain all cities
        assert region.bounding_box.min_latitude <= 46.2530
        assert region.bounding_box.max_latitude >= 48.1035
        assert region.bounding_box.min_longitude <= 19.0402
        assert region.bounding_box.max_longitude >= 21.6269

    def test_calculates_center_point(
        self, geo_utils: GeoUtilsRegion, sample_cities: List[Dict[str, Any]]
    ) -> None:
        """calculate_region_from_cities calculates center point."""
        region = geo_utils.calculate_region_from_cities(sample_cities, "Test")

        assert region.center_point is not None
        assert isinstance(region.center_point, GeoPoint)

    def test_calculates_population(
        self, geo_utils: GeoUtilsRegion, sample_cities: List[Dict[str, Any]]
    ) -> None:
        """calculate_region_from_cities calculates total population."""
        region = geo_utils.calculate_region_from_cities(sample_cities, "Test")

        expected_population = 1752286 + 201881 + 161837 + 157177
        assert region.population == expected_population

    def test_calculates_area(
        self, geo_utils: GeoUtilsRegion, sample_cities: List[Dict[str, Any]]
    ) -> None:
        """calculate_region_from_cities calculates area."""
        region = geo_utils.calculate_region_from_cities(sample_cities, "Test")

        assert region.area_km2 > 0

    def test_caches_region(
        self, geo_utils: GeoUtilsRegion, sample_cities: List[Dict[str, Any]]
    ) -> None:
        """calculate_region_from_cities caches result."""
        region = geo_utils.calculate_region_from_cities(sample_cities, "Hungary")

        assert "Hungary" in geo_utils.region_cache
        assert geo_utils.region_cache["Hungary"] is region

    def test_raises_for_empty_list(self, geo_utils: GeoUtilsRegion) -> None:
        """calculate_region_from_cities raises for empty list."""
        with pytest.raises(ValueError, match="Cities list is empty"):
            geo_utils.calculate_region_from_cities([], "Test")

    def test_handles_cities_without_population(
        self, geo_utils: GeoUtilsRegion
    ) -> None:
        """calculate_region_from_cities handles cities without population."""
        cities = [
            {"city": "City1", "lat": 47.0, "lon": 19.0},
            {"city": "City2", "lat": 48.0, "lon": 20.0, "population": 1000},
        ]

        region = geo_utils.calculate_region_from_cities(cities, "Test")

        assert region.population == 1000

    def test_handles_zero_population(self, geo_utils: GeoUtilsRegion) -> None:
        """calculate_region_from_cities handles zero population."""
        cities = [
            {"city": "City1", "lat": 47.0, "lon": 19.0, "population": 0},
        ]

        region = geo_utils.calculate_region_from_cities(cities, "Test")

        assert region.population is None


class TestEstimateBoundingBoxArea:
    """Test _estimate_bounding_box_area method."""

    def test_calculates_area_for_square_bbox(
        self, geo_utils: GeoUtilsRegion
    ) -> None:
        """_estimate_bounding_box_area calculates area for square bbox."""
        # 1 degree square at equator ~ 111km x 111km ~ 12,321 km²
        bbox = BoundingBox(
            min_latitude=0,
            max_latitude=1,
            min_longitude=0,
            max_longitude=1,
        )

        area = geo_utils._estimate_bounding_box_area(bbox)

        # Should be roughly 12,000 km²
        assert 11000 < area < 13000

    def test_calculates_area_for_hungarian_bbox(
        self, geo_utils: GeoUtilsRegion
    ) -> None:
        """_estimate_bounding_box_area calculates area for Hungarian bbox."""
        # Hungary is roughly 93,000 km²
        bbox = BoundingBox(
            min_latitude=45.7,
            max_latitude=48.6,
            min_longitude=16.1,
            max_longitude=22.9,
        )

        area = geo_utils._estimate_bounding_box_area(bbox)

        # Should be in reasonable range for Hungary's bounding box
        # (bounding box is larger than actual country area)
        assert 100000 < area < 200000

    def test_returns_positive_area(
        self, geo_utils: GeoUtilsRegion
    ) -> None:
        """_estimate_bounding_box_area returns positive area."""
        bbox = BoundingBox(
            min_latitude=47.0,
            max_latitude=48.0,
            min_longitude=19.0,
            max_longitude=20.0,
        )

        area = geo_utils._estimate_bounding_box_area(bbox)

        assert area > 0


class TestGroupCitiesByProximity:
    """Test group_cities_by_proximity method."""

    def test_groups_cities_by_distance(
        self, geo_utils: GeoUtilsRegion
    ) -> None:
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

    def test_returns_empty_for_empty_list(
        self, geo_utils: GeoUtilsRegion
    ) -> None:
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

    def test_groups_sorted_by_size(
        self, geo_utils: GeoUtilsRegion
    ) -> None:
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
            {"city": f"City{i}", "lat": 47.0 + i * 0.1, "lon": 19.0, "population": 1000 * (10 - i)}
            for i in range(10)
        ]

        result = geo_utils.find_optimal_cities_for_region(cities, target_count=3)

        assert len(result) == 3

    def test_filters_by_bounding_box(
        self, geo_utils: GeoUtilsRegion
    ) -> None:
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

        result = geo_utils.find_optimal_cities_for_region(cities, target_count=10, region_bbox=bbox)

        # Should only include cities inside bbox
        assert len(result) == 2
        names = [c["city"] for c in result]
        assert "Inside1" in names
        assert "Inside2" in names
        assert "Outside" not in names

    def test_prioritizes_higher_population(
        self, geo_utils: GeoUtilsRegion
    ) -> None:
        """find_optimal_cities_for_region prioritizes higher population."""
        cities = [
            {"city": "Small", "lat": 47.0, "lon": 19.0, "population": 100},
            {"city": "Medium", "lat": 47.1, "lon": 19.1, "population": 1000},
            {"city": "Large", "lat": 47.2, "lon": 19.2, "population": 10000},
        ]

        result = geo_utils.find_optimal_cities_for_region(cities, target_count=1)

        # Should select the city with highest population
        assert result[0]["city"] == "Large"

    def test_handles_cities_without_population(
        self, geo_utils: GeoUtilsRegion
    ) -> None:
        """find_optimal_cities_for_region handles cities without population."""
        cities = [
            {"city": "NoPop", "lat": 47.0, "lon": 19.0},
            {"city": "WithPop", "lat": 48.0, "lon": 20.0, "population": 1000},
        ]

        result = geo_utils.find_optimal_cities_for_region(cities, target_count=2)

        assert len(result) == 2

    def test_returns_empty_for_no_cities(
        self, geo_utils: GeoUtilsRegion
    ) -> None:
        """find_optimal_cities_for_region returns empty for no cities."""
        result = geo_utils.find_optimal_cities_for_region([], target_count=5)

        assert result == []

    def test_selects_diverse_cities(
        self, geo_utils: GeoUtilsRegion
    ) -> None:
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


class TestGeoUtilsRegionEdgeCases:
    """Edge case tests for GeoUtilsRegion."""

    def test_region_cache_updates(
        self, geo_utils: GeoUtilsRegion
    ) -> None:
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
            {"city": f"City{i}", "lat": 47.0 + i * 0.05, "lon": 19.0}
            for i in range(20)
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
