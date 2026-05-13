"""Tests split from test_city_manager_hungarian.py."""

from __future__ import annotations

from src.infrastructure.city_manager.city_manager_hungarian import CityManagerHungarian

# ruff: noqa: F403, F405
from tests.data.test_city_manager_hungarian_support import *


class TestCityManagerHungarianEdgeCases:
    """Edge case tests for CityManagerHungarian."""

    def test_search_with_special_characters(self, cities_db: Path, hungarian_db: Path) -> None:
        """search_hungarian_settlements handles special Hungarian characters."""
        manager = CityManagerHungarian(db_path=cities_db, hungarian_db_path=hungarian_db)

        # Search with Hungarian special characters (á, é, í, ó, ö, ő, ú, ü, ű)
        results = manager.search_hungarian_settlements("Békéscsaba")

        assert len(results) >= 1
        names = [c.city for c in results]
        assert "Békéscsaba" in names

    def test_search_case_insensitive(self, cities_db: Path, hungarian_db: Path) -> None:
        """search_hungarian_settlements is case insensitive."""
        manager = CityManagerHungarian(db_path=cities_db, hungarian_db_path=hungarian_db)

        results_lower = manager.search_hungarian_settlements("budapest")
        results_upper = manager.search_hungarian_settlements("BUDAPEST")

        assert len(results_lower) == len(results_upper) == 1

    def test_search_empty_string(self, cities_db: Path, hungarian_db: Path) -> None:
        """search_hungarian_settlements with empty string returns all settlements."""
        manager = CityManagerHungarian(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager.search_hungarian_settlements("", limit=5)

        assert len(results) == 5

    def test_search_combined_filters(self, cities_db: Path, hungarian_db: Path) -> None:
        """search_hungarian_settlements works with combined filters."""
        manager = CityManagerHungarian(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager.search_hungarian_settlements(
            "Kiskun",
            county_filter="Bács-Kiskun",
            settlement_type_filter="város",
            limit=5,
        )

        assert len(results) >= 1
        for city in results:
            assert "Kiskun" in city.city
            assert city.megye == "Bács-Kiskun"
            assert city.settlement_type == "város"

    def test_get_counties_cache_persists(self, cities_db: Path, hungarian_db: Path) -> None:
        """Counties cache persists across multiple calls."""
        manager = CityManagerHungarian(db_path=cities_db, hungarian_db_path=hungarian_db)

        counties1 = manager.get_hungarian_counties()
        # Manually modify cache to test it's being used
        manager._hungarian_counties_cache = ["Modified"]

        counties2 = manager.get_hungarian_counties()

        assert counties2 == ["Modified"]

        # Restore
        manager._hungarian_counties_cache = counties1
