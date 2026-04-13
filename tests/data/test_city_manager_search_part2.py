"""Tests split from test_city_manager_search.py."""

from __future__ import annotations

from src.data.city_manager_search import CityManagerSearch

# ruff: noqa: F403, F405
from tests.data.test_city_manager_search_support import *


class TestSearchCities:
    """Test search_cities method."""

    def test_search_returns_matching_cities(self, cities_db: Path, hungarian_db: Path) -> None:
        """search_cities returns global cities matching search term."""
        manager = CityManagerSearch(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager.search_cities("London")

        assert len(results) >= 1
        assert results[0].city == "London"

    def test_search_respects_limit(self, cities_db: Path, hungarian_db: Path) -> None:
        """search_cities respects limit parameter."""
        manager = CityManagerSearch(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager.search_cities("", limit=3)

        assert len(results) == 3

    def test_search_with_country_filter(self, cities_db: Path, hungarian_db: Path) -> None:
        """search_cities filters by country_code."""
        manager = CityManagerSearch(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager.search_cities("", limit=10, country_filter="GB")

        assert len(results) >= 1
        for city in results:
            assert city.country_code == "GB"

    def test_search_returns_empty_when_no_connection(
        self, mock_data_dir: Path, hungarian_db: Path
    ) -> None:
        """search_cities returns empty list when global DB unavailable."""
        manager = CityManagerSearch(
            db_path=mock_data_dir / "nonexistent.db", hungarian_db_path=hungarian_db
        )

        results = manager.search_cities("London")

        assert results == []

    def test_search_returns_empty_when_no_matches(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """search_cities returns empty list when no matches."""
        manager = CityManagerSearch(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager.search_cities("NonExistentCity12345")

        assert results == []

    def test_search_sorted_by_population(self, cities_db: Path, hungarian_db: Path) -> None:
        """search_cities sorts results by population descending."""
        manager = CityManagerSearch(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager.search_cities("", limit=5)

        populations = [c.population for c in results if c.population]
        assert populations == sorted(populations, reverse=True)

    def test_search_increments_query_count(self, cities_db: Path, hungarian_db: Path) -> None:
        """search_cities increments query_count."""
        manager = CityManagerSearch(db_path=cities_db, hungarian_db_path=hungarian_db)
        initial_count = manager.query_count

        manager.search_cities("London")

        assert manager.query_count == initial_count + 1


class TestGetCitiesByCountry:
    """Test get_cities_by_country method."""

    def test_returns_cities_for_country(self, cities_db: Path, hungarian_db: Path) -> None:
        """get_cities_by_country returns cities in specified country."""
        manager = CityManagerSearch(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager.get_cities_by_country("GB")

        assert len(results) >= 1
        for city in results:
            assert city.country_code == "GB"

    def test_respects_limit(self, cities_db: Path, hungarian_db: Path) -> None:
        """get_cities_by_country respects limit parameter."""
        manager = CityManagerSearch(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager.get_cities_by_country("US", limit=2)

        assert len(results) <= 2

    def test_with_min_population_filter(self, cities_db: Path, hungarian_db: Path) -> None:
        """get_cities_by_country filters by minimum population."""
        manager = CityManagerSearch(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager.get_cities_by_country("GB", min_population=100000)

        for city in results:
            if city.population:
                assert city.population >= 100000

    def test_returns_hungarian_combined_for_hu(self, cities_db: Path, hungarian_db: Path) -> None:
        """get_cities_by_country for HU returns combined Hungarian + global results."""
        manager = CityManagerSearch(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager.get_cities_by_country("HU", limit=20)

        # Should include Hungarian settlements
        hungarian_count = sum(1 for c in results if c.is_hungarian)
        assert hungarian_count >= 1

    def test_returns_empty_when_no_connection(
        self, mock_data_dir: Path, hungarian_db: Path
    ) -> None:
        """get_cities_by_country returns empty list when global DB unavailable."""
        manager = CityManagerSearch(
            db_path=mock_data_dir / "nonexistent.db", hungarian_db_path=hungarian_db
        )

        results = manager.get_cities_by_country("GB")

        assert results == []

    def test_country_code_case_insensitive(self, cities_db: Path, hungarian_db: Path) -> None:
        """get_cities_by_country handles lowercase country codes."""
        manager = CityManagerSearch(db_path=cities_db, hungarian_db_path=hungarian_db)

        results_lower = manager.get_cities_by_country("gb")
        results_upper = manager.get_cities_by_country("GB")

        assert len(results_lower) == len(results_upper)
