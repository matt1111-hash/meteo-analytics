"""Tests split from test_city_manager_search.py."""

from __future__ import annotations

# ruff: noqa: F403, F405
from tests.data.test_city_manager_search_support import *


class TestGetHungarianCitiesCombined:
    """Test _get_hungarian_cities_combined method."""

    def test_returns_combined_results(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """_get_hungarian_cities_combined returns Hungarian + global HU cities."""
        manager = CityManagerSearch(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager._get_hungarian_cities_combined(limit=20)

        assert len(results) >= 1
        # Should include at least one Hungarian settlement
        assert any(c.is_hungarian for c in results)

    def test_respects_limit(self, cities_db: Path, hungarian_db: Path) -> None:
        """_get_hungarian_cities_combined respects limit."""
        manager = CityManagerSearch(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager._get_hungarian_cities_combined(limit=3)

        assert len(results) <= 3

    def test_with_min_population_filter(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """_get_hungarian_cities_combined filters by min_population."""
        manager = CityManagerSearch(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager._get_hungarian_cities_combined(
            limit=10, min_population=100000
        )

        for city in results:
            if city.population:
                assert city.population >= 100000

    def test_filters_duplicates(self, cities_db: Path, hungarian_db: Path) -> None:
        """_get_hungarian_cities_combined filters duplicate names."""
        manager = CityManagerSearch(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager._get_hungarian_cities_combined(limit=20)

        # Check that Hungarian Budapest is only included once
        budapest_count = sum(1 for c in results if c.city.lower() == "budapest")
        assert budapest_count <= 1

    def test_works_without_hungarian_db(
        self, cities_db: Path, mock_data_dir: Path
    ) -> None:
        """_get_hungarian_cities_combined works with only global DB."""
        manager = CityManagerSearch(
            db_path=cities_db, hungarian_db_path=mock_data_dir / "nonexistent.db"
        )

        results = manager._get_hungarian_cities_combined(limit=10)

        # Should still return global Hungarian cities
        assert len(results) >= 1


class TestCityManagerSearchInheritance:
    """Test CityManagerSearch inherits from CityManagerHungarian."""

    def test_has_hungarian_methods(self, cities_db: Path, hungarian_db: Path) -> None:
        """CityManagerSearch has Hungarian methods from parent."""
        manager = CityManagerSearch(db_path=cities_db, hungarian_db_path=hungarian_db)

        assert hasattr(manager, "search_hungarian_settlements")
        assert hasattr(manager, "get_hungarian_counties")
        assert hasattr(manager, "get_hungarian_settlements_by_county")

    def test_has_db_attributes(self, cities_db: Path, hungarian_db: Path) -> None:
        """CityManagerSearch has database attributes from ancestors."""
        manager = CityManagerSearch(db_path=cities_db, hungarian_db_path=hungarian_db)

        assert manager.connection is not None
        assert manager.hungarian_connection is not None


class TestCityManagerSearchEdgeCases:
    """Edge case tests for CityManagerSearch."""

    def test_search_unified_with_special_characters(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """search_unified handles special characters."""
        manager = CityManagerSearch(db_path=cities_db, hungarian_db_path=hungarian_db)

        # Search with Hungarian special characters
        results = manager.search_unified("Kiskunhalas", limit=5)

        assert len(results) >= 1
        assert results[0].city == "Kiskunhalas"

    def test_find_city_with_empty_string(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """find_city_by_name handles empty string."""
        manager = CityManagerSearch(db_path=cities_db, hungarian_db_path=hungarian_db)

        coords = manager.find_city_by_name("")

        # Empty string should return some result or None
        assert coords is None or isinstance(coords, tuple)

    def test_search_cities_with_sql_special_chars(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """search_cities handles SQL special characters safely."""
        manager = CityManagerSearch(db_path=cities_db, hungarian_db_path=hungarian_db)

        # These characters should not cause SQL injection
        results = manager.search_cities("'; DROP TABLE cities; --")

        # Should return empty or handle gracefully
        assert isinstance(results, list)

    def test_multiple_queries_increment_counters(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """Multiple queries increment counters correctly."""
        manager = CityManagerSearch(db_path=cities_db, hungarian_db_path=hungarian_db)

        initial_global = manager.query_count
        initial_hungarian = manager.hungarian_query_count

        manager.search_cities("London")
        manager.search_hungarian_settlements("Budapest")
        manager.search_unified("Debrecen")

        assert manager.query_count > initial_global
        assert manager.hungarian_query_count > initial_hungarian

    def test_search_unified_returns_city_objects(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """search_unified returns City objects with proper attributes."""
        manager = CityManagerSearch(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager.search_unified("London", limit=5)

        for city in results:
            assert isinstance(city, City)
            assert city.lat is not None
            assert city.lon is not None
            assert city.country is not None
