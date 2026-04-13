"""Tests split from test_city_manager_hungarian.py."""

from __future__ import annotations

from src.data.city_manager_hungarian import CityManagerHungarian

# ruff: noqa: F403, F405
from tests.data.test_city_manager_hungarian_support import *


class TestSearchHungarianSettlements:
    """Test search_hungarian_settlements method."""

    def test_search_returns_matching_settlements(self, cities_db: Path, hungarian_db: Path) -> None:
        """search_hungarian_settlements returns settlements matching search term."""
        manager = CityManagerHungarian(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager.search_hungarian_settlements("Budapest")

        assert len(results) == 1
        assert results[0].city == "Budapest"
        assert results[0].is_hungarian is True

    def test_search_returns_multiple_matches(self, cities_db: Path, hungarian_db: Path) -> None:
        """search_hungarian_settlements returns multiple matching settlements."""
        manager = CityManagerHungarian(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager.search_hungarian_settlements("Kiskun")

        # Kiskunhalas and Kiskunfélegyháza match "Kiskun"
        assert len(results) >= 2
        names = [c.city for c in results]
        assert "Kiskunhalas" in names
        assert "Kiskunfélegyháza" in names

    def test_search_respects_limit(self, cities_db: Path, hungarian_db: Path) -> None:
        """search_hungarian_settlements respects limit parameter."""
        manager = CityManagerHungarian(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager.search_hungarian_settlements("Kiskun", limit=2)

        assert len(results) == 2

    def test_search_with_county_filter(self, cities_db: Path, hungarian_db: Path) -> None:
        """search_hungarian_settlements filters by county."""
        manager = CityManagerHungarian(db_path=cities_db, hungarian_db_path=hungarian_db)

        # Search for empty string in Bács-Kiskun to get all settlements in county
        results = manager.search_hungarian_settlements("", county_filter="Bács-Kiskun", limit=10)

        # Should have multiple settlements in Bács-Kiskun
        assert len(results) >= 5
        for city in results:
            assert city.megye == "Bács-Kiskun"

    def test_search_with_settlement_type_filter(self, cities_db: Path, hungarian_db: Path) -> None:
        """search_hungarian_settlements filters by settlement type."""
        manager = CityManagerHungarian(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager.search_hungarian_settlements("", settlement_type_filter="község")

        assert len(results) >= 1
        for city in results:
            assert city.settlement_type == "község"

    def test_search_returns_empty_list_when_no_match(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """search_hungarian_settlements returns empty list when no match."""
        manager = CityManagerHungarian(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager.search_hungarian_settlements("NonExistentCity12345")

        assert results == []

    def test_search_returns_empty_list_when_no_connection(
        self, cities_db: Path, mock_data_dir: Path
    ) -> None:
        """search_hungarian_settlements returns empty list when Hungarian DB unavailable."""
        manager = CityManagerHungarian(
            db_path=cities_db, hungarian_db_path=mock_data_dir / "nonexistent.db"
        )

        results = manager.search_hungarian_settlements("Budapest")

        assert results == []

    def test_search_uses_like_search(self, cities_db: Path, hungarian_db: Path) -> None:
        """search_hungarian_settlements uses LIKE for partial matching."""
        manager = CityManagerHungarian(db_path=cities_db, hungarian_db_path=hungarian_db)

        # Search for partial name
        results = manager.search_hungarian_settlements("Debr")

        assert len(results) == 1
        assert results[0].city == "Debrecen"

    def test_search_results_sorted_by_priority_and_population(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """search_hungarian_settlements sorts results by priority then population."""
        manager = CityManagerHungarian(db_path=cities_db, hungarian_db_path=hungarian_db)

        # Search for all Bács-Kiskun settlements
        results = manager.search_hungarian_settlements("", county_filter="Bács-Kiskun", limit=10)

        # Should be sorted by region_priority DESC, then population DESC
        assert len(results) >= 3
        # Kecskemét has highest priority (4.0) among non-capital cities
        assert results[0].city == "Kecskemét"

    def test_search_increments_hungarian_query_count(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """search_hungarian_settlements increments hungarian_query_count."""
        manager = CityManagerHungarian(db_path=cities_db, hungarian_db_path=hungarian_db)
        initial_count = manager.hungarian_query_count

        manager.search_hungarian_settlements("Budapest")

        assert manager.hungarian_query_count == initial_count + 1


class TestGetHungarianCounties:
    """Test get_hungarian_counties method."""

    def test_returns_list_of_counties(self, cities_db: Path, hungarian_db: Path) -> None:
        """get_hungarian_counties returns list of unique counties."""
        manager = CityManagerHungarian(db_path=cities_db, hungarian_db_path=hungarian_db)

        counties = manager.get_hungarian_counties()

        assert isinstance(counties, list)
        assert "Budapest" in counties
        assert "Bács-Kiskun" in counties

    def test_returns_sorted_list(self, cities_db: Path, hungarian_db: Path) -> None:
        """get_hungarian_counties returns alphabetically sorted list."""
        manager = CityManagerHungarian(db_path=cities_db, hungarian_db_path=hungarian_db)

        counties = manager.get_hungarian_counties()

        assert counties == sorted(counties)

    def test_uses_cache(self, cities_db: Path, hungarian_db: Path) -> None:
        """get_hungarian_counties caches results."""
        manager = CityManagerHungarian(db_path=cities_db, hungarian_db_path=hungarian_db)

        # First call
        counties1 = manager.get_hungarian_counties()
        query_count1 = manager.hungarian_query_count

        # Second call
        counties2 = manager.get_hungarian_counties()
        query_count2 = manager.hungarian_query_count

        assert counties1 == counties2
        # Query count should only increment once (cache used on second call)
        assert query_count2 == query_count1

    def test_returns_empty_list_when_no_connection(
        self, cities_db: Path, mock_data_dir: Path
    ) -> None:
        """get_hungarian_counties returns empty list when DB unavailable."""
        manager = CityManagerHungarian(
            db_path=cities_db, hungarian_db_path=mock_data_dir / "nonexistent.db"
        )

        counties = manager.get_hungarian_counties()

        assert counties == []

    def test_returns_empty_list_for_empty_database(
        self, cities_db: Path, empty_hungarian_db: Path
    ) -> None:
        """get_hungarian_counties returns empty list for empty database."""
        manager = CityManagerHungarian(db_path=cities_db, hungarian_db_path=empty_hungarian_db)

        counties = manager.get_hungarian_counties()

        assert counties == []
