"""Tests split from test_geo_utils_region.py."""

from __future__ import annotations

# ruff: noqa: F403, F405
from tests.data.test_geo_utils_region_support import *


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

    def test_handles_cities_without_population(self, geo_utils: GeoUtilsRegion) -> None:
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

    def test_calculates_area_for_square_bbox(self, geo_utils: GeoUtilsRegion) -> None:
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

    def test_returns_positive_area(self, geo_utils: GeoUtilsRegion) -> None:
        """_estimate_bounding_box_area returns positive area."""
        bbox = BoundingBox(
            min_latitude=47.0,
            max_latitude=48.0,
            min_longitude=19.0,
            max_longitude=20.0,
        )

        area = geo_utils._estimate_bounding_box_area(bbox)

        assert area > 0
