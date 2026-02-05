"""GeoUtilsAnalytics osztály tesztjei."""

from __future__ import annotations

from src.data.geo_utils_analytics import GeoUtilsAnalytics
from src.data.geo_utils_core import GeoUtils
from src.data.geo_utils_region import GeoUtilsRegion


class TestOptimizeCitiesForWeatherAnalytics:
    """optimize_cities_for_weather_analytics metódus tesztjei."""

    def test_empty_list(self) -> None:
        """Üres lista üres listát ad vissza."""
        utils = GeoUtilsAnalytics()
        result = utils.optimize_cities_for_weather_analytics([], "temperature")
        assert result == []

    def test_temperature_filter(self) -> None:
        """Hőmérséklet analitikához szűrés."""
        utils = GeoUtilsAnalytics()
        cities = [
            {"lat": 47.0, "lon": 19.0, "population": 200000},
            {"lat": 47.1, "lon": 19.1, "population": 50000},
            {"lat": 47.2, "lon": 19.2, "population": 150000},
        ]
        result = utils.optimize_cities_for_weather_analytics(cities, "temperature", max_cities=10)
        # 100000+ lakos: 2 város, de 2 < 5, így fallback 50000+ -> 3 város
        assert len(result) == 3
        assert all(c["population"] >= 50000 for c in result)

    def test_precipitation_filter(self) -> None:
        """Csapadék analitikához szűrés."""
        utils = GeoUtilsAnalytics()
        cities = [
            {"lat": 47.0, "lon": 19.0, "population": 60000},
            {"lat": 47.1, "lon": 19.1, "population": 30000},
            {"lat": 47.2, "lon": 19.2, "population": 100000},
        ]
        result = utils.optimize_cities_for_weather_analytics(cities, "precipitation", max_cities=10)
        # 50000+ lakos: 2 város, de 2 < 5, így fallback 25000+ -> 3 város
        assert len(result) == 3
        assert all(c["population"] >= 25000 for c in result)

    def test_wind_filter(self) -> None:
        """Szél analitikához szűrés."""
        utils = GeoUtilsAnalytics()
        cities = [
            {"lat": 47.0, "lon": 19.0, "population": 250000},
            {"lat": 47.1, "lon": 19.1, "population": 150000},
        ]
        result = utils.optimize_cities_for_weather_analytics(cities, "wind", max_cities=10)
        # 200000+ lakos: 1 város, de 1 < 5, így fallback 100000+ -> 2 város
        assert len(result) == 2
        assert all(c["population"] >= 100000 for c in result)

    def test_global_filter(self) -> None:
        """Globális analitikához szűrés."""
        utils = GeoUtilsAnalytics()
        cities = [
            {"lat": 47.0, "lon": 19.0, "population": 600000},
            {"lat": 47.1, "lon": 19.1, "population": 400000},
        ]
        result = utils.optimize_cities_for_weather_analytics(cities, "global", max_cities=10)
        # Min 500000 lakos kell, de 400000 >= 250000 (fallback)
        # Mindkét város át kell hogy menjen a fallback miatt
        assert len(result) == 2

    def test_unknown_analytics_type_uses_global(self) -> None:
        """Ismeretlen analitikai típusnál globális szűrés."""
        utils = GeoUtilsAnalytics()
        cities = [
            {"lat": 47.0, "lon": 19.0, "population": 600000},
            {"lat": 47.1, "lon": 19.1, "population": 400000},
        ]
        result = utils.optimize_cities_for_weather_analytics(cities, "unknown", max_cities=10)
        # Ismeretlen típus -> global, de fallback miatt 2 város
        assert len(result) == 2

    def test_fallback_to_lower_threshold(self) -> None:
        """Ha kevés a város, alacsonyabb küszöb."""
        utils = GeoUtilsAnalytics()
        cities = [
            {"lat": 47.0, "lon": 19.0, "population": 60000},
            {"lat": 47.1, "lon": 19.1, "population": 55000},
        ]
        result = utils.optimize_cities_for_weather_analytics(cities, "temperature", max_cities=10)
        # Csak 2 város van < 100000, de >= 50000
        assert len(result) == 2

    def test_respects_max_cities(self) -> None:
        """Respektálja a max_cities limitet."""
        utils = GeoUtilsAnalytics()
        cities = [
            {"lat": 47.0 + i * 0.1, "lon": 19.0 + i * 0.1, "population": 200000 + i * 10000}
            for i in range(20)
        ]
        result = utils.optimize_cities_for_weather_analytics(cities, "temperature", max_cities=5)
        assert len(result) <= 5


class TestCalculateMultiCityCoverageArea:
    """calculate_multi_city_coverage_area metódus tesztjei."""

    def test_empty_list_returns_empty_dict(self) -> None:
        """Üres lista üres dict-et ad vissza."""
        utils = GeoUtilsAnalytics()
        result = utils.calculate_multi_city_coverage_area([])
        assert result == {}

    def test_single_city(self) -> None:
        """Egyetlen város coverage-e."""
        utils = GeoUtilsAnalytics()
        cities = [{"lat": 47.0, "lon": 19.0}]
        result = utils.calculate_multi_city_coverage_area(cities)

        assert "bounding_box" in result
        assert "geographic_center" in result
        assert "area_km2" in result
        assert "cities_count" in result
        assert "distances" in result

    def test_multiple_cities(self) -> None:
        """Több város coverage-e."""
        utils = GeoUtilsAnalytics()
        cities = [
            {"lat": 47.0, "lon": 19.0},
            {"lat": 48.0, "lon": 20.0},
            {"lat": 46.0, "lon": 18.0},
        ]
        result = utils.calculate_multi_city_coverage_area(cities)

        assert result["cities_count"] == 3
        assert result["area_km2"] > 0
        assert result["distances"]["max_distance_from_center"] > 0

    def test_bounding_box_structure(self) -> None:
        """Bounding box struktúrája."""
        utils = GeoUtilsAnalytics()
        cities = [
            {"lat": 47.0, "lon": 19.0},
            {"lat": 48.0, "lon": 20.0},
        ]
        result = utils.calculate_multi_city_coverage_area(cities)

        bbox = result["bounding_box"]
        assert "min_latitude" in bbox
        assert "max_latitude" in bbox
        assert "min_longitude" in bbox
        assert "max_longitude" in bbox

    def test_geographic_center_structure(self) -> None:
        """Geographic center struktúrája."""
        utils = GeoUtilsAnalytics()
        cities = [{"lat": 47.0, "lon": 19.0}]
        result = utils.calculate_multi_city_coverage_area(cities)

        center = result["geographic_center"]
        assert "latitude" in center
        assert "longitude" in center

    def test_distances_calculations(self) -> None:
        """Távolság számítások."""
        utils = GeoUtilsAnalytics()
        cities = [
            {"lat": 47.0, "lon": 19.0},
            {"lat": 48.0, "lon": 20.0},
        ]
        result = utils.calculate_multi_city_coverage_area(cities)

        distances = result["distances"]
        assert "max_distance_from_center" in distances
        assert "avg_distance_from_center" in distances
        assert "coverage_radius_km" in distances

        assert distances["max_distance_from_center"] > 0
        assert distances["avg_distance_from_center"] > 0
        assert distances["coverage_radius_km"] == distances["max_distance_from_center"]


class TestInheritance:
    """Öröklődés tesztek."""

    def test_inherits_from_geoutilsregion(self) -> None:
        """A GeoUtilsAnalytics a GeoUtilsRegion-ból származik."""
        assert issubclass(GeoUtilsAnalytics, GeoUtilsRegion)

    def test_inherits_from_geoutils(self) -> None:
        """A GeoUtilsAnalytics közvetve a GeoUtils-ból is származik."""
        assert issubclass(GeoUtilsAnalytics, GeoUtils)

    def test_has_core_methods(self) -> None:
        """Rendelkezik az ősi osztály metódusaival."""
        utils = GeoUtilsAnalytics()
        assert hasattr(utils, 'validate_coordinates')
        assert hasattr(utils, 'calculate_bounding_box')
        assert hasattr(utils, 'calculate_geographic_center')
        assert hasattr(utils, 'calculate_region_from_cities')
        assert hasattr(utils, 'group_cities_by_proximity')

    def test_has_region_cache(self) -> None:
        """Rendelkezik region_cache attribútummal."""
        utils = GeoUtilsAnalytics()
        assert hasattr(utils, 'region_cache')
        assert isinstance(utils.region_cache, dict)


class TestIntegration:
    """Integrációs tesztek."""

    def test_optimize_and_coverage_combined(self) -> None:
        """Optimalizálás és coverage számítás kombinációja."""
        utils = GeoUtilsAnalytics()
        cities = [
            {"lat": 47.0 + i * 0.5, "lon": 19.0 + i * 0.5, "population": 100000 + i * 50000}
            for i in range(10)
        ]

        optimized = utils.optimize_cities_for_weather_analytics(cities, "global", max_cities=5)
        coverage = utils.calculate_multi_city_coverage_area(optimized)

        assert len(optimized) <= 5
        assert coverage["cities_count"] == len(optimized)
        assert coverage["area_km2"] > 0

    def test_find_optimal_cities_for_region(self) -> None:
        """find_optimal_cities_for_region metódus elérhető."""
        utils = GeoUtilsAnalytics()
        cities = [
            {"lat": 47.0, "lon": 19.0, "population": 100000},
            {"lat": 47.1, "lon": 19.1, "population": 50000},
            {"lat": 47.2, "lon": 19.2, "population": 200000},
        ]
        result = utils.find_optimal_cities_for_region(cities, 2)
        assert len(result) == 2


class TestInitialization:
    """Inicializálási tesztek."""

    def test_default_initialization(self) -> None:
        """Alapértelmezett inicializálás."""
        utils = GeoUtilsAnalytics()
        assert utils.distance_calculator is not None
        assert utils.region_cache == {}
