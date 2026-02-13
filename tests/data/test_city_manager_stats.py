"""Tests for CityManagerStats from city_manager_stats.py."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Dict
from unittest.mock import patch

import pytest

from src.data.city_manager_stats import CityManagerStats
from src.data.city_types import City


@pytest.fixture
def mock_data_dir(tmp_path: Path) -> Path:
    """Create temporary data directory."""
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


@pytest.fixture
def cities_db(mock_data_dir: Path) -> Path:
    """Create cities database with global cities."""
    db_path = mock_data_dir / "cities.db"
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE cities (
            id INTEGER,
            city TEXT,
            lat REAL,
            lon REAL,
            country TEXT,
            country_code TEXT,
            population INTEGER,
            continent TEXT,
            admin_name TEXT,
            capital INTEGER,
            timezone TEXT
        )
    """)
    test_data = [
        (1, "Budapest", 47.4979, 19.0402, "Hungary", "HU", 1752286, "Europe", "Budapest", 1, "Europe/Budapest"),
        (2, "London", 51.5074, -0.1278, "United Kingdom", "GB", 8982000, "Europe", "England", 1, "Europe/London"),
        (3, "New York", 40.7128, -74.0060, "United States", "US", 8336817, "North America", "New York", 0, "America/New_York"),
        (4, "Paris", 48.8566, 2.3522, "France", "FR", 2161000, "Europe", "Île-de-France", 1, "Europe/Paris"),
        (5, "Berlin", 52.5200, 13.4050, "Germany", "DE", 3645000, "Europe", "Berlin", 1, "Europe/Berlin"),
        (6, "Tokyo", 35.6762, 139.6503, "Japan", "JP", 13960000, "Asia", "Tokyo", 1, "Asia/Tokyo"),
        (7, "Sydney", -33.8688, 151.2093, "Australia", "AU", 5312000, "Oceania", "New South Wales", 0, "Australia/Sydney"),
        (8, "Debrecen", 47.5314, 21.6269, "Hungary", "HU", 201881, "Europe", "Hajdú-Bihar", 0, "Europe/Budapest"),
    ]
    conn.executemany(
        "INSERT INTO cities VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        test_data,
    )
    conn.commit()
    conn.close()
    return db_path


@pytest.fixture
def hungarian_db(mock_data_dir: Path) -> Path:
    """Create Hungarian settlements database."""
    db_path = mock_data_dir / "hungarian_settlements.db"
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE hungarian_settlements (
            id INTEGER,
            name TEXT,
            latitude REAL,
            longitude REAL,
            megye TEXT,
            settlement_type TEXT,
            population INTEGER,
            climate_zone TEXT,
            region_priority REAL,
            jaras TEXT,
            terulet_hektar INTEGER,
            lakasok_szama INTEGER
        )
    """)
    test_data = [
        (1, "Budapest", 47.4979, 19.0402, "Budapest", "főváros", 1752286, "continental", 10.0, None, 52500, 800000),
        (2, "Debrecen", 47.5314, 21.6269, "Hajdú-Bihar", "város", 201881, "continental", 5.0, "Debreceni", 4210, 85000),
        (3, "Szeged", 46.2530, 20.1414, "Csongrád-Csanád", "város", 161837, "continental", 5.0, "Szegedi", 2810, 72000),
        (4, "Kiskunhalas", 46.4315, 19.4867, "Bács-Kiskun", "város", 18254, "continental", 3.0, "Kiskunhalasi", 350, 8000),
        (5, "Kecskemét", 46.8964, 19.6897, "Bács-Kiskun", "város", 110034, "continental", 4.0, "Kecskeméti", 3200, 48000),
        (6, "Soltvadkert", 46.4769, 19.3833, "Bács-Kiskun", "város", 7270, "continental", 1.0, "Soltvadkerti", 80, 3200),
        (7, "Akasztó", 46.5333, 19.3000, "Bács-Kiskun", "község", 1500, "continental", 1.0, "Kiskőrösi", 35, 650),
    ]
    conn.executemany(
        "INSERT INTO hungarian_settlements VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        test_data,
    )
    conn.commit()
    conn.close()
    return db_path


@pytest.fixture
def empty_hungarian_db(mock_data_dir: Path) -> Path:
    """Create empty Hungarian settlements database."""
    db_path = mock_data_dir / "hungarian_empty.db"
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE hungarian_settlements (
            id INTEGER,
            name TEXT,
            latitude REAL,
            longitude REAL,
            megye TEXT,
            settlement_type TEXT,
            population INTEGER,
            climate_zone TEXT,
            region_priority REAL,
            jaras TEXT,
            terulet_hektar INTEGER,
            lakasok_szama INTEGER
        )
    """)
    conn.commit()
    conn.close()
    return db_path


class TestGetDatabaseStatistics:
    """Test get_database_statistics method."""

    def test_returns_dict_with_query_counts(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """get_database_statistics returns dict with query counts."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        stats = manager.get_database_statistics()

        assert isinstance(stats, dict)
        assert "query_count" in stats
        assert "hungarian_query_count" in stats

    def test_returns_global_cities_count(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """get_database_statistics returns global_cities count."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        stats = manager.get_database_statistics()

        assert "global_cities" in stats
        assert stats["global_cities"] >= 1

    def test_returns_hungarian_settlements_count(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """get_database_statistics returns hungarian_settlements count."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        stats = manager.get_database_statistics()

        assert "hungarian_settlements" in stats
        assert stats["hungarian_settlements"] >= 1

    def test_returns_continents_list(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """get_database_statistics returns continents list."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        stats = manager.get_database_statistics()

        assert "continents" in stats
        assert isinstance(stats["continents"], list)

    def test_returns_countries_list(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """get_database_statistics returns countries list."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        stats = manager.get_database_statistics()

        assert "countries" in stats
        assert isinstance(stats["countries"], list)

    def test_returns_hungarian_counties(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """get_database_statistics returns hungarian_counties."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        stats = manager.get_database_statistics()

        assert "hungarian_counties" in stats
        assert isinstance(stats["hungarian_counties"], list)

    def test_returns_settlement_types(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """get_database_statistics returns settlement_types."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        stats = manager.get_database_statistics()

        assert "settlement_types" in stats
        assert isinstance(stats["settlement_types"], list)

    def test_returns_total_searchable_locations(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """get_database_statistics returns total_searchable_locations."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        stats = manager.get_database_statistics()

        assert "total_searchable_locations" in stats
        assert stats["total_searchable_locations"] == (
            stats["global_cities"] + stats["hungarian_settlements"]
        )

    def test_handles_missing_global_db(
        self, mock_data_dir: Path, hungarian_db: Path
    ) -> None:
        """get_database_statistics handles missing global DB."""
        manager = CityManagerStats(
            db_path=mock_data_dir / "nonexistent.db",
            hungarian_db_path=hungarian_db
        )

        stats = manager.get_database_statistics()

        assert stats["global_cities"] == 0
        assert stats["continents"] == []
        assert stats["countries"] == []

    def test_handles_missing_hungarian_db(
        self, cities_db: Path, mock_data_dir: Path
    ) -> None:
        """get_database_statistics handles missing Hungarian DB."""
        manager = CityManagerStats(
            db_path=cities_db,
            hungarian_db_path=mock_data_dir / "nonexistent.db"
        )

        stats = manager.get_database_statistics()

        assert stats["hungarian_settlements"] == 0
        assert stats["hungarian_counties"] == []
        assert stats["settlement_types"] == []


class TestGetHungarianStatistics:
    """Test get_hungarian_statistics method."""

    def test_returns_dict_with_settlements(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """get_hungarian_statistics returns dict with settlement data."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        stats = manager.get_hungarian_statistics()

        assert isinstance(stats, dict)
        assert "total_settlements" in stats

    def test_returns_by_settlement_type(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """get_hungarian_statistics returns by_settlement_type."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        stats = manager.get_hungarian_statistics()

        assert "by_settlement_type" in stats
        assert isinstance(stats["by_settlement_type"], dict)

    def test_returns_top_counties(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """get_hungarian_statistics returns top_counties."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        stats = manager.get_hungarian_statistics()

        assert "top_counties" in stats
        assert isinstance(stats["top_counties"], dict)

    def test_returns_population_stats(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """get_hungarian_statistics returns population_stats."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        stats = manager.get_hungarian_statistics()

        assert "population_stats" in stats
        pop_stats = stats["population_stats"]
        assert "large_cities_100k_plus" in pop_stats
        assert "medium_towns_10k_plus" in pop_stats
        assert "small_towns_under_10k" in pop_stats

    def test_returns_error_when_no_hungarian_db(
        self, cities_db: Path, mock_data_dir: Path
    ) -> None:
        """get_hungarian_statistics returns error when Hungarian DB unavailable."""
        manager = CityManagerStats(
            db_path=cities_db,
            hungarian_db_path=mock_data_dir / "nonexistent.db"
        )

        stats = manager.get_hungarian_statistics()

        assert "error" in stats
        assert stats["error"] == "Hungarian database not available"

    def test_calculates_average_population(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """get_hungarian_statistics calculates average population."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        stats = manager.get_hungarian_statistics()

        assert stats["population_stats"]["average_population"] > 0


class TestGetCitiesByContinent:
    """Test get_cities_by_continent method."""

    def test_returns_cities_for_europe(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """get_cities_by_continent returns European cities."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager.get_cities_by_continent("Europe")

        assert len(results) >= 1
        for city in results:
            assert city.continent == "Europe"

    def test_respects_limit(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """get_cities_by_continent respects limit."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager.get_cities_by_continent("Europe", limit=2)

        assert len(results) <= 2

    def test_with_min_population_filter(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """get_cities_by_continent filters by min_population."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager.get_cities_by_continent("Europe", min_population=1000000)

        for city in results:
            if city.population:
                assert city.population >= 1000000

    def test_returns_empty_for_unknown_continent(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """get_cities_by_continent returns empty for unknown continent."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager.get_cities_by_continent("NonExistentContinent")

        assert results == []

    def test_returns_empty_when_no_connection(
        self, mock_data_dir: Path, hungarian_db: Path
    ) -> None:
        """get_cities_by_continent returns empty when global DB unavailable."""
        manager = CityManagerStats(
            db_path=mock_data_dir / "nonexistent.db",
            hungarian_db_path=hungarian_db
        )

        results = manager.get_cities_by_continent("Europe")

        assert results == []


class TestGetAvailableContinents:
    """Test _get_available_continents method."""

    def test_returns_list_of_continents(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """_get_available_continents returns list of continents."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        continents = manager._get_available_continents()

        assert isinstance(continents, list)
        assert "Europe" in continents
        assert "Asia" in continents

    def test_returns_sorted_list(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """_get_available_continents returns sorted list."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        continents = manager._get_available_continents()

        assert continents == sorted(continents)

    def test_returns_empty_when_no_connection(
        self, mock_data_dir: Path, hungarian_db: Path
    ) -> None:
        """_get_available_continents returns empty when no connection."""
        manager = CityManagerStats(
            db_path=mock_data_dir / "nonexistent.db",
            hungarian_db_path=hungarian_db
        )

        continents = manager._get_available_continents()

        assert continents == []


class TestGetAvailableCountries:
    """Test _get_available_countries method."""

    def test_returns_list_of_countries(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """_get_available_countries returns list of country dicts."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        countries = manager._get_available_countries()

        assert isinstance(countries, list)
        assert len(countries) >= 1

    def test_country_dicts_have_required_fields(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """_get_available_countries returns dicts with required fields."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        countries = manager._get_available_countries()

        for country in countries:
            assert "country_code" in country
            assert "country_name" in country
            assert "city_count" in country

    def test_sorted_by_city_count(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """_get_available_countries sorts by city count descending."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        countries = manager._get_available_countries()

        city_counts = [c["city_count"] for c in countries]
        assert city_counts == sorted(city_counts, reverse=True)

    def test_returns_empty_when_no_connection(
        self, mock_data_dir: Path, hungarian_db: Path
    ) -> None:
        """_get_available_countries returns empty when no connection."""
        manager = CityManagerStats(
            db_path=mock_data_dir / "nonexistent.db",
            hungarian_db_path=hungarian_db
        )

        countries = manager._get_available_countries()

        assert countries == []


class TestContextManager:
    """Test context manager functionality."""

    def test_enter_returns_self(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """__enter__ returns self."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        with manager as ctx_manager:
            assert ctx_manager is manager

    def test_exit_closes_connections(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """__exit__ closes database connections."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        assert manager.connection is not None
        assert manager.hungarian_connection is not None

        with manager:
            pass

        assert manager.connection is None
        assert manager.hungarian_connection is None

    def test_context_manager_with_exception(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """Context manager closes connections even with exception."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        try:
            with manager:
                raise ValueError("Test exception")
        except ValueError:
            pass

        assert manager.connection is None


class TestGetCitiesForHungarianCounty:
    """Test get_cities_for_hungarian_county method."""

    def test_returns_list_of_dicts(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """get_cities_for_hungarian_county returns list of dicts."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager.get_cities_for_hungarian_county("Bács-Kiskun")

        assert isinstance(results, list)
        assert len(results) >= 1

    def test_dict_has_required_fields(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """get_cities_for_hungarian_county dicts have required fields."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager.get_cities_for_hungarian_county("Bács-Kiskun")

        for city_dict in results:
            assert "city" in city_dict
            assert "lat" in city_dict
            assert "lon" in city_dict
            assert "is_hungarian" in city_dict

    def test_returns_empty_for_unknown_county(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """get_cities_for_hungarian_county returns empty for unknown county."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager.get_cities_for_hungarian_county("NonExistentCounty")

        assert results == []


class TestCityManagerStatsInheritance:
    """Test CityManagerStats inherits from CityManagerSearch."""

    def test_has_search_methods(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """CityManagerStats has search methods from parent."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        assert hasattr(manager, "search_unified")
        assert hasattr(manager, "search_cities")
        assert hasattr(manager, "find_city_by_name")

    def test_has_hungarian_methods(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """CityManagerStats has Hungarian methods from ancestors."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        assert hasattr(manager, "search_hungarian_settlements")
        assert hasattr(manager, "get_hungarian_counties")


class TestCityManagerStatsEdgeCases:
    """Edge case tests for CityManagerStats."""

    def test_statistics_after_queries(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """Statistics reflect query counts after queries."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        manager.search_cities("London")
        manager.search_hungarian_settlements("Budapest")

        stats = manager.get_database_statistics()

        assert stats["query_count"] >= 1
        assert stats["hungarian_query_count"] >= 1

    def test_last_query_time_updated(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """last_query_time is updated after queries."""
        manager = CityManagerStats(db_path=cities_db, hungarian_db_path=hungarian_db)

        assert manager.last_query_time is None

        manager.search_cities("London")

        stats = manager.get_database_statistics()
        assert stats["last_query"] is not None

    def test_empty_hungarian_db_statistics(
        self, cities_db: Path, empty_hungarian_db: Path
    ) -> None:
        """Statistics work with empty Hungarian database."""
        manager = CityManagerStats(
            db_path=cities_db, hungarian_db_path=empty_hungarian_db
        )

        stats = manager.get_database_statistics()

        assert stats["hungarian_settlements"] == 0
        assert stats["hungarian_counties"] == []
        assert stats["settlement_types"] == []

    def test_hungarian_statistics_empty_db(
        self, cities_db: Path, empty_hungarian_db: Path
    ) -> None:
        """get_hungarian_statistics works with empty database."""
        manager = CityManagerStats(
            db_path=cities_db, hungarian_db_path=empty_hungarian_db
        )

        stats = manager.get_hungarian_statistics()

        assert stats["total_settlements"] == 0
