"""GeoUtilsRegion osztály tesztjei."""

from __future__ import annotations

import pytest

from src.data.geo_types import BoundingBox, GeographicRegion, GeoPoint
from src.data.geo_utils_core import GeoUtils
from src.data.geo_utils_region import GeoUtilsRegion


class TestCalculateRegionFromCities:
    """calculate_region_from_cities metódus tesztjei."""

    def test_empty_cities_raises_error(self) -> None:
        """Üres városlista ValueError-t dob."""
        utils = GeoUtilsRegion()
        with pytest.raises(ValueError, match="Cities list is empty"):
            utils.calculate_region_from_cities([], "Test Region")

    def test_single_city_region(self) -> None:
        """Egyetlen város régiója."""
        utils = GeoUtilsRegion()
        city = {"lat": 47.4979, "lon": 19.0402, "population": 1750000}
        region = utils.calculate_region_from_cities([city], "Budapest")

        assert region.name == "Budapest"
        assert isinstance(region, GeographicRegion)
        assert region.cities_count == 1
        assert region.population == 1750000

    def test_multiple_cities_region(self) -> None:
        """Több város régiója."""
        utils = GeoUtilsRegion()
        cities = [
            {"lat": 47.4979, "lon": 19.0402, "population": 1750000},
            {"lat": 47.5316, "lon": 19.0524, "population": 230000},
            {"lat": 47.4626, "lon": 18.9940, "population": 60000},
        ]
        region = utils.calculate_region_from_cities(cities, "Budapest Area")

        assert region.name == "Budapest Area"
        assert region.cities_count == 3
        assert region.population == 1750000 + 230000 + 60000

    def test_cities_without_population(self) -> None:
        """Városok népesség nélkül."""
        utils = GeoUtilsRegion()
        cities = [
            {"lat": 47.4979, "lon": 19.0402},
            {"lat": 47.5316, "lon": 19.0524},
        ]
        region = utils.calculate_region_from_cities(cities, "Test Region")

        assert region.cities_count == 2
        assert region.population is None

    def test_region_has_bounding_box(self) -> None:
        """A régió rendelkezik bounding boxszal (paddinggel)."""
        utils = GeoUtilsRegion()
        cities = [
            {"lat": 47.0, "lon": 19.0},
            {"lat": 48.0, "lon": 20.0},
        ]
        region = utils.calculate_region_from_cities(cities, "Test Region")

        assert isinstance(region.bounding_box, BoundingBox)
        # A padding_degrees=0.1 kiterjeszti a bounding boxot
        assert region.bounding_box.min_latitude <= 47.0
        assert region.bounding_box.max_latitude >= 48.0
        assert region.bounding_box.min_longitude <= 19.0
        assert region.bounding_box.max_longitude >= 20.0

    def test_region_has_center(self) -> None:
        """A régió rendelkezik középponttal."""
        utils = GeoUtilsRegion()
        cities = [
            {"lat": 47.0, "lon": 19.0},
            {"lat": 48.0, "lon": 20.0},
        ]
        region = utils.calculate_region_from_cities(cities, "Test Region")

        assert isinstance(region.center_point, GeoPoint)
        assert 47.0 < region.center_point.latitude < 48.0
        assert 19.0 < region.center_point.longitude < 20.0

    def test_region_has_area(self) -> None:
        """A régió rendelkezik területtel."""
        utils = GeoUtilsRegion()
        cities = [
            {"lat": 47.0, "lon": 19.0},
            {"lat": 48.0, "lon": 20.0},
        ]
        region = utils.calculate_region_from_cities(cities, "Test Region")

        assert region.area_km2 is not None
        assert region.area_km2 > 0

    def test_region_is_cached(self) -> None:
        """A régió bekerül a cache-be."""
        utils = GeoUtilsRegion()
        cities = [{"lat": 47.0, "lon": 19.0}]
        region1 = utils.calculate_region_from_cities(cities, "Test Region")
        region2 = utils.calculate_region_from_cities(cities, "Test Region")

        # A cache-ben benne van
        assert "Test Region" in utils.region_cache
        # Az értékek megegyeznek (de nem ugyanaz az objektum)
        assert region1.name == region2.name
        assert region1.cities_count == region2.cities_count


class TestEstimateBoundingBoxArea:
    """_estimate_bounding_box_area metódus tesztjei."""

    def test_small_area(self) -> None:
        """Kis terület becslése."""
        utils = GeoUtilsRegion()
        bbox = BoundingBox(
            min_latitude=47.0,
            max_latitude=47.1,
            min_longitude=19.0,
            max_longitude=19.1,
        )
        area = utils._estimate_bounding_box_area(bbox)
        assert area > 0
        assert area < 1000  # kb 100 km²-nél kisebb

    def test_large_area(self) -> None:
        """Nagy terület becslése."""
        utils = GeoUtilsRegion()
        bbox = BoundingBox(
            min_latitude=45.0,
            max_latitude=50.0,
            min_longitude=15.0,
            max_longitude=25.0,
        )
        area = utils._estimate_bounding_box_area(bbox)
        assert area > 10000  # több mint 10000 km²

    def test_equator_area(self) -> None:
        """Terület az egyenlítőn."""
        utils = GeoUtilsRegion()
        bbox = BoundingBox(
            min_latitude=0.0,
            max_latitude=1.0,
            min_longitude=0.0,
            max_longitude=1.0,
        )
        area = utils._estimate_bounding_box_area(bbox)
        # Az egyenlítőn 1 fok ~111 km
        assert area > 10000


class TestGroupCitiesByProximity:
    """group_cities_by_proximity metódus tesztjei."""

    def test_empty_list_returns_empty(self) -> None:
        """Üres lista üres listát ad vissza."""
        utils = GeoUtilsRegion()
        result = utils.group_cities_by_proximity([])
        assert result == []

    def test_single_city(self) -> None:
        """Egyetlen város egy csoport."""
        utils = GeoUtilsRegion()
        cities = [{"lat": 47.0, "lon": 19.0}]
        result = utils.group_cities_by_proximity(cities)
        assert len(result) == 1
        assert len(result[0]) == 1

    def test_far_apart_cities(self) -> None:
        """Messzi városok külön csoportok."""
        utils = GeoUtilsRegion()
        cities = [
            {"lat": 47.0, "lon": 19.0},
            {"lat": 50.0, "lon": 30.0},
        ]
        result = utils.group_cities_by_proximity(cities, max_distance_km=100)
        assert len(result) == 2

    def test_close_cities_same_group(self) -> None:
        """Közeli városok ugyanabban a csoportban."""
        utils = GeoUtilsRegion()
        cities = [
            {"lat": 47.4979, "lon": 19.0402},
            {"lat": 47.5316, "lon": 19.0524},
            {"lat": 47.4626, "lon": 18.9940},
        ]
        result = utils.group_cities_by_proximity(cities, max_distance_km=50)
        assert len(result) == 1
        assert len(result[0]) == 3

    def test_groups_sorted_by_size(self) -> None:
        """Csoportok méret szerint csökkenő sorrendben."""
        utils = GeoUtilsRegion()
        cities = [
            {"lat": 47.0, "lon": 19.0},
            {"lat": 47.1, "lon": 19.1},
            {"lat": 50.0, "lon": 30.0},
            {"lat": 47.2, "lon": 19.2},
        ]
        result = utils.group_cities_by_proximity(cities, max_distance_km=100)
        # Az első csoport a legnagyobb
        assert len(result[0]) >= len(result[1])


class TestFindOptimalCitiesForRegion:
    """find_optimal_cities_for_region metódus tesztjei."""

    def test_empty_list(self) -> None:
        """Üres lista üres listát ad vissza."""
        utils = GeoUtilsRegion()
        result = utils.find_optimal_cities_for_region([], 5)
        assert result == []

    def test_target_count_larger_than_list(self) -> None:
        """Ha a target_count nagyobb mint a lista, visszaadja az egészet."""
        utils = GeoUtilsRegion()
        cities = [
            {"lat": 47.0, "lon": 19.0, "population": 100000},
            {"lat": 47.1, "lon": 19.1, "population": 50000},
        ]
        result = utils.find_optimal_cities_for_region(cities, 5)
        assert len(result) == 2

    def test_filters_by_region_bbox(self) -> None:
        """Szűrés régió bounding box alapján."""
        utils = GeoUtilsRegion()
        cities = [
            {"lat": 47.0, "lon": 19.0, "population": 100000},
            {"lat": 50.0, "lon": 30.0, "population": 100000},
        ]
        bbox = BoundingBox(
            min_latitude=46.0,
            max_latitude=48.0,
            min_longitude=18.0,
            max_longitude=20.0,
        )
        result = utils.find_optimal_cities_for_region(cities, 10, region_bbox=bbox)
        assert len(result) == 1
        assert result[0]["lat"] == 47.0

    def test_prioritizes_population(self) -> None:
        """Népesség alapú prioritás."""
        utils = GeoUtilsRegion()
        cities = [
            {"lat": 47.0, "lon": 19.0, "population": 1000000},
            {"lat": 47.1, "lon": 19.1, "population": 50000},
            {"lat": 47.2, "lon": 19.2, "population": 100000},
        ]
        result = utils.find_optimal_cities_for_region(cities, 2)
        # A legnagyobb népességű város az első
        assert result[0]["population"] >= result[1]["population"]

    def test_returns_target_count(self) -> None:
        """Visszaadja a kért számú várost."""
        utils = GeoUtilsRegion()
        cities = [
            {"lat": 47.0 + i * 0.1, "lon": 19.0 + i * 0.1, "population": 100000 + i * 10000}
            for i in range(10)
        ]
        result = utils.find_optimal_cities_for_region(cities, 5)
        assert len(result) == 5


class TestInheritance:
    """Öröklődés tesztek."""

    def test_inherits_from_geoutils(self) -> None:
        """A GeoUtilsRegion a GeoUtils-ból származik."""
        assert issubclass(GeoUtilsRegion, GeoUtils)

    def test_has_core_methods(self) -> None:
        """Rendelkezik az ősi osztály metódusaival."""
        utils = GeoUtilsRegion()
        assert hasattr(utils, 'validate_coordinates')
        assert hasattr(utils, 'normalize_coordinates')
        assert hasattr(utils, 'calculate_bounding_box')
        assert hasattr(utils, 'calculate_geographic_center')

    def test_has_region_cache(self) -> None:
        """Rendelkezik region_cache attribútummal."""
        utils = GeoUtilsRegion()
        assert hasattr(utils, 'region_cache')
        assert isinstance(utils.region_cache, dict)


class TestInitialization:
    """Inicializálási tesztek."""

    def test_default_initialization(self) -> None:
        """Alapértelmezett inicializálás."""
        utils = GeoUtilsRegion()
        assert utils.distance_calculator is not None
        assert utils.region_cache == {}
