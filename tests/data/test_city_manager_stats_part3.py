"""Tests split from test_city_manager_stats.py."""

from __future__ import annotations

from src.infrastructure.city_manager.city_manager_stats import CityManagerStats

# ruff: noqa: F403, F405
from tests.data.test_city_manager_stats_support import *


class TestGetCitiesForHungarianCounty:
    """Test get_cities_for_hungarian_county method."""

    def test_returns_list_of_dicts(self, cities_db: Path, hungarian_db: Path) -> None:
        """get_cities_for_hungarian_county returns list of dicts."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager.get_cities_for_hungarian_county("Bács-Kiskun")

        assert isinstance(results, list)
        assert len(results) >= 1

    def test_dict_has_required_fields(self, cities_db: Path, hungarian_db: Path) -> None:
        """get_cities_for_hungarian_county dicts have required fields."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager.get_cities_for_hungarian_county("Bács-Kiskun")

        for city_dict in results:
            assert "city" in city_dict
            assert "lat" in city_dict
            assert "lon" in city_dict
            assert "is_hungarian" in city_dict

    def test_returns_empty_for_unknown_county(self, cities_db: Path, hungarian_db: Path) -> None:
        """get_cities_for_hungarian_county returns empty for unknown county."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager.get_cities_for_hungarian_county("NonExistentCounty")

        assert results == []


class TestCityManagerStatsInheritance:
    """Test CityManagerStats inherits from CityManagerSearch."""

    def test_has_search_methods(self, cities_db: Path, hungarian_db: Path) -> None:
        """CityManagerStats has search methods from parent."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        assert hasattr(manager, "search_unified")
        assert hasattr(manager, "search_cities")
        assert hasattr(manager, "find_city_by_name")

    def test_has_hungarian_methods(self, cities_db: Path, hungarian_db: Path) -> None:
        """CityManagerStats has Hungarian methods from ancestors."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        assert hasattr(manager, "search_hungarian_settlements")
        assert hasattr(manager, "get_hungarian_counties")


class TestCityManagerStatsEdgeCases:
    """Edge case tests for CityManagerStats."""

    def test_statistics_after_queries(self, cities_db: Path, hungarian_db: Path) -> None:
        """Statistics reflect query counts after queries."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        manager.search_cities("London")
        manager.search_hungarian_settlements("Budapest")

        stats = manager.get_database_statistics()

        assert stats["query_count"] >= 1
        assert stats["hungarian_query_count"] >= 1

    def test_last_query_time_updated(self, cities_db: Path, hungarian_db: Path) -> None:
        """last_query_time is updated after queries."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        assert manager.last_query_time is None

        manager.search_cities("London")

        stats = manager.get_database_statistics()
        assert stats["last_query"] is not None

    def test_empty_hungarian_db_statistics(self, cities_db: Path, empty_hungarian_db: Path) -> None:
        """Statistics work with empty Hungarian database."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=empty_hungarian_db)

        stats = manager.get_database_statistics()

        assert stats["hungarian_settlements"] == 0
        assert stats["hungarian_counties"] == []
        assert stats["settlement_types"] == []

    def test_hungarian_statistics_empty_db(self, cities_db: Path, empty_hungarian_db: Path) -> None:
        """get_hungarian_statistics works with empty database."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=empty_hungarian_db)

        stats = manager.get_hungarian_statistics()

        assert stats["total_settlements"] == 0
