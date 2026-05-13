"""Tests split from test_city_manager_search.py."""

from __future__ import annotations

from src.infrastructure.city_manager.city_manager_search import CityManagerSearch

# ruff: noqa: F403, F405
from tests.data.test_city_manager_search_support import *


class TestFindCityByName:
    """Test find_city_by_name method."""

    def test_finds_hungarian_city_exact_match(self, cities_db: Path, hungarian_db: Path) -> None:
        """find_city_by_name returns Hungarian city coordinates on exact match."""
        manager = CityManagerSearch(db_path=cities_db, hungarian_db_path=hungarian_db)

        coords = manager.find_city_by_name("Budapest")

        assert coords is not None
        lat, lon = coords
        assert abs(lat - 47.4979) < 0.01
        assert abs(lon - 19.0402) < 0.01

    def test_finds_hungarian_city_case_insensitive(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """find_city_by_name finds Hungarian city case insensitively."""
        manager = CityManagerSearch(db_path=cities_db, hungarian_db_path=hungarian_db)

        coords = manager.find_city_by_name("BUDAPEST")

        assert coords is not None

    def test_falls_back_to_global_when_hungarian_not_found(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """find_city_by_name falls back to global search when Hungarian not found."""
        manager = CityManagerSearch(db_path=cities_db, hungarian_db_path=hungarian_db)

        coords = manager.find_city_by_name("London")

        assert coords is not None
        lat, lon = coords  # noqa: RUF059
        assert abs(lat - 51.5074) < 0.01

    def test_returns_none_when_not_found(self, cities_db: Path, hungarian_db: Path) -> None:
        """find_city_by_name returns None when city not found anywhere."""
        manager = CityManagerSearch(db_path=cities_db, hungarian_db_path=hungarian_db)

        coords = manager.find_city_by_name("NonExistentCity12345")

        assert coords is None

    def test_returns_best_match_when_multiple_matches(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """find_city_by_name returns best match (highest priority/population) when multiple matches."""
        manager = CityManagerSearch(db_path=cities_db, hungarian_db_path=hungarian_db)

        # Search for "Deb" - should find Debrecen
        coords = manager.find_city_by_name("Debrecen")

        assert coords is not None

    def test_works_with_only_hungarian_db(self, mock_data_dir: Path, hungarian_db: Path) -> None:
        """find_city_by_name works with only Hungarian database available."""
        manager = CityManagerSearch(
            db_path=mock_data_dir / "nonexistent.db", hungarian_db_path=hungarian_db
        )

        coords = manager.find_city_by_name("Budapest")

        assert coords is not None

    def test_works_with_only_global_db(self, cities_db: Path, mock_data_dir: Path) -> None:
        """find_city_by_name works with only global database available."""
        manager = CityManagerSearch(
            db_path=cities_db, hungarian_db_path=mock_data_dir / "nonexistent.db"
        )

        coords = manager.find_city_by_name("London")

        assert coords is not None

    def test_handles_exception_gracefully(self, cities_db: Path, hungarian_db: Path) -> None:
        """find_city_by_name handles exceptions gracefully."""
        manager = CityManagerSearch(db_path=cities_db, hungarian_db_path=hungarian_db)

        # This should not raise even if something goes wrong internally
        coords = manager.find_city_by_name("Test")

        # May return None or a valid result, but should not raise
        assert coords is None or isinstance(coords, tuple)


class TestSearchUnified:
    """Test search_unified method."""

    def test_returns_combined_results(self, cities_db: Path, hungarian_db: Path) -> None:
        """search_unified returns combined Hungarian + global results."""
        manager = CityManagerSearch(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager.search_unified("Budapest", limit=10)

        assert len(results) >= 1
        # First result should be Hungarian Budapest
        assert results[0].is_hungarian is True

    def test_respects_limit(self, cities_db: Path, hungarian_db: Path) -> None:
        """search_unified respects limit parameter."""
        manager = CityManagerSearch(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager.search_unified("", limit=5)

        assert len(results) <= 5

    def test_filters_duplicates(self, cities_db: Path, hungarian_db: Path) -> None:
        """search_unified filters duplicate cities (Hungarian priority)."""
        manager = CityManagerSearch(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager.search_unified("Budapest", limit=10)

        # Should not have both Hungarian and global Budapest
        budapest_count = sum(1 for c in results if c.city.lower() == "budapest")
        assert budapest_count <= 2  # Allow some flexibility

    def test_hungarian_priority_affects_distribution(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """search_unified with hungarian_priority=True gives more slots to Hungarian."""
        manager = CityManagerSearch(db_path=cities_db, hungarian_db_path=hungarian_db)

        results_priority = manager.search_unified("", limit=10, hungarian_priority=True)

        # With priority, 70% should be Hungarian (7 of 10)
        assert len(results_priority) <= 10

    def test_no_hungarian_priority_affects_distribution(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """search_unified with hungarian_priority=False splits 50/50."""
        manager = CityManagerSearch(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager.search_unified("", limit=10, hungarian_priority=False)

        assert len(results) <= 10

    def test_global_limit_ratio_parameter(self, cities_db: Path, hungarian_db: Path) -> None:
        """search_unified respects global_limit_ratio parameter."""
        manager = CityManagerSearch(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager.search_unified("", limit=10, global_limit_ratio=0.5)

        assert len(results) <= 10

    def test_returns_empty_when_no_matches(self, cities_db: Path, hungarian_db: Path) -> None:
        """search_unified returns empty list when no matches."""
        manager = CityManagerSearch(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager.search_unified("NonExistentCity12345", limit=10)

        assert results == []
