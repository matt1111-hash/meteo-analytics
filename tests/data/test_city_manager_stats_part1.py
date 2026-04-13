"""Tests split from test_city_manager_stats.py."""

from __future__ import annotations

from src.data.city_manager_stats import CityManagerStats

# ruff: noqa: F403, F405
from tests.data.test_city_manager_stats_support import *


class TestGetDatabaseStatistics:
    """Test get_database_statistics method."""

    def test_returns_dict_with_query_counts(self, cities_db: Path, hungarian_db: Path) -> None:
        """get_database_statistics returns dict with query counts."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        stats = manager.get_database_statistics()

        assert isinstance(stats, dict)
        assert "query_count" in stats
        assert "hungarian_query_count" in stats

    def test_returns_global_cities_count(self, cities_db: Path, hungarian_db: Path) -> None:
        """get_database_statistics returns global_cities count."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        stats = manager.get_database_statistics()

        assert "global_cities" in stats
        assert stats["global_cities"] >= 1

    def test_returns_hungarian_settlements_count(self, cities_db: Path, hungarian_db: Path) -> None:
        """get_database_statistics returns hungarian_settlements count."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        stats = manager.get_database_statistics()

        assert "hungarian_settlements" in stats
        assert stats["hungarian_settlements"] >= 1

    def test_returns_continents_list(self, cities_db: Path, hungarian_db: Path) -> None:
        """get_database_statistics returns continents list."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        stats = manager.get_database_statistics()

        assert "continents" in stats
        assert isinstance(stats["continents"], list)

    def test_returns_countries_list(self, cities_db: Path, hungarian_db: Path) -> None:
        """get_database_statistics returns countries list."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        stats = manager.get_database_statistics()

        assert "countries" in stats
        assert isinstance(stats["countries"], list)

    def test_returns_hungarian_counties(self, cities_db: Path, hungarian_db: Path) -> None:
        """get_database_statistics returns hungarian_counties."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        stats = manager.get_database_statistics()

        assert "hungarian_counties" in stats
        assert isinstance(stats["hungarian_counties"], list)

    def test_returns_settlement_types(self, cities_db: Path, hungarian_db: Path) -> None:
        """get_database_statistics returns settlement_types."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        stats = manager.get_database_statistics()

        assert "settlement_types" in stats
        assert isinstance(stats["settlement_types"], list)

    def test_returns_total_searchable_locations(self, cities_db: Path, hungarian_db: Path) -> None:
        """get_database_statistics returns total_searchable_locations."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        stats = manager.get_database_statistics()

        assert "total_searchable_locations" in stats
        assert stats["total_searchable_locations"] == (
            stats["global_cities"] + stats["hungarian_settlements"]
        )

    def test_handles_missing_global_db(self, mock_data_dir: Path, hungarian_db: Path) -> None:
        """get_database_statistics handles missing global DB."""
        manager = CityManagerStats(
            db_path=mock_data_dir / "nonexistent.db", hungarian_db_path=hungarian_db
        )

        stats = manager.get_database_statistics()

        assert stats["global_cities"] == 0
        assert stats["continents"] == []
        assert stats["countries"] == []

    def test_handles_missing_hungarian_db(self, cities_db: Path, mock_data_dir: Path) -> None:
        """get_database_statistics handles missing Hungarian DB."""
        manager = CityManagerStats(
            db_path=cities_db, hungarian_db_path=mock_data_dir / "nonexistent.db"
        )

        stats = manager.get_database_statistics()

        assert stats["hungarian_settlements"] == 0
        assert stats["hungarian_counties"] == []
        assert stats["settlement_types"] == []


class TestGetHungarianStatistics:
    """Test get_hungarian_statistics method."""

    def test_returns_dict_with_settlements(self, cities_db: Path, hungarian_db: Path) -> None:
        """get_hungarian_statistics returns dict with settlement data."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        stats = manager.get_hungarian_statistics()

        assert isinstance(stats, dict)
        assert "total_settlements" in stats

    def test_returns_by_settlement_type(self, cities_db: Path, hungarian_db: Path) -> None:
        """get_hungarian_statistics returns by_settlement_type."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        stats = manager.get_hungarian_statistics()

        assert "by_settlement_type" in stats
        assert isinstance(stats["by_settlement_type"], dict)

    def test_returns_top_counties(self, cities_db: Path, hungarian_db: Path) -> None:
        """get_hungarian_statistics returns top_counties."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        stats = manager.get_hungarian_statistics()

        assert "top_counties" in stats
        assert isinstance(stats["top_counties"], dict)

    def test_returns_population_stats(self, cities_db: Path, hungarian_db: Path) -> None:
        """get_hungarian_statistics returns population_stats."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        stats = manager.get_hungarian_statistics()

        assert "population_stats" in stats
        pop_stats = stats["population_stats"]
        assert "large_cities_100k_plus" in pop_stats
        assert "medium_towns_10k_plus" in pop_stats
        assert "small_towns_under_10k" in pop_stats

    def test_returns_error_when_no_hungarian_db(self, cities_db: Path, mock_data_dir: Path) -> None:
        """get_hungarian_statistics returns error when Hungarian DB unavailable."""
        manager = CityManagerStats(
            db_path=cities_db, hungarian_db_path=mock_data_dir / "nonexistent.db"
        )

        stats = manager.get_hungarian_statistics()

        assert "error" in stats
        assert stats["error"] == "Hungarian database not available"

    def test_calculates_average_population(self, cities_db: Path, hungarian_db: Path) -> None:
        """get_hungarian_statistics calculates average population."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        stats = manager.get_hungarian_statistics()

        assert stats["population_stats"]["average_population"] > 0
