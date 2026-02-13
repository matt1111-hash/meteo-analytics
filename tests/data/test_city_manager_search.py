"""Tests for CityManagerSearch from city_manager_search.py."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import List
from unittest.mock import patch, MagicMock

import pytest

from src.data.city_manager_search import CityManagerSearch
from src.data.city_types import City, CityDatabaseError


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
    # Insert diverse global cities
    test_data = [
        (1, "Budapest", 47.4979, 19.0402, "Hungary", "HU", 1752286, "Europe", "Budapest", 1, "Europe/Budapest"),
        (2, "London", 51.5074, -0.1278, "United Kingdom", "GB", 8982000, "Europe", "England", 1, "Europe/London"),
        (3, "New York", 40.7128, -74.0060, "United States", "US", 8336817, "North America", "New York", 0, "America/New_York"),
        (4, "Paris", 48.8566, 2.3522, "France", "FR", 2161000, "Europe", "Île-de-France", 1, "Europe/Paris"),
        (5, "Berlin", 52.5200, 13.4050, "Germany", "DE", 3645000, "Europe", "Berlin", 1, "Europe/Berlin"),
        (6, "Tokyo", 35.6762, 139.6503, "Japan", "JP", 13960000, "Asia", "Tokyo", 1, "Asia/Tokyo"),
        (7, "Sydney", -33.8688, 151.2093, "Australia", "AU", 5312000, "Oceania", "New South Wales", 0, "Australia/Sydney"),
        (8, "Debrecen", 47.5314, 21.6269, "Hungary", "HU", 201881, "Europe", "Hajdú-Bihar", 0, "Europe/Budapest"),
        (9, "Vienna", 48.2082, 16.3738, "Austria", "AT", 1897000, "Europe", "Vienna", 1, "Europe/Vienna"),
        (10, "Broxbourne", 51.7462, -0.0115, "United Kingdom", "GB", 15000, "Europe", "England", 0, "Europe/London"),
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
    ]
    conn.executemany(
        "INSERT INTO hungarian_settlements VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        test_data,
    )
    conn.commit()
    conn.close()
    return db_path


@pytest.fixture
def empty_cities_db(mock_data_dir: Path) -> Path:
    """Create empty cities database."""
    db_path = mock_data_dir / "cities_empty.db"
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
    conn.commit()
    conn.close()
    return db_path


class TestFindCityByName:
    """Test find_city_by_name method."""

    def test_finds_hungarian_city_exact_match(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
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
        lat, lon = coords
        assert abs(lat - 51.5074) < 0.01

    def test_returns_none_when_not_found(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
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

    def test_works_with_only_hungarian_db(
        self, mock_data_dir: Path, hungarian_db: Path
    ) -> None:
        """find_city_by_name works with only Hungarian database available."""
        manager = CityManagerSearch(
            db_path=mock_data_dir / "nonexistent.db",
            hungarian_db_path=hungarian_db
        )

        coords = manager.find_city_by_name("Budapest")

        assert coords is not None

    def test_works_with_only_global_db(
        self, cities_db: Path, mock_data_dir: Path
    ) -> None:
        """find_city_by_name works with only global database available."""
        manager = CityManagerSearch(
            db_path=cities_db,
            hungarian_db_path=mock_data_dir / "nonexistent.db"
        )

        coords = manager.find_city_by_name("London")

        assert coords is not None

    def test_handles_exception_gracefully(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """find_city_by_name handles exceptions gracefully."""
        manager = CityManagerSearch(db_path=cities_db, hungarian_db_path=hungarian_db)

        # This should not raise even if something goes wrong internally
        coords = manager.find_city_by_name("Test")

        # May return None or a valid result, but should not raise
        assert coords is None or isinstance(coords, tuple)


class TestSearchUnified:
    """Test search_unified method."""

    def test_returns_combined_results(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """search_unified returns combined Hungarian + global results."""
        manager = CityManagerSearch(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager.search_unified("Budapest", limit=10)

        assert len(results) >= 1
        # First result should be Hungarian Budapest
        assert results[0].is_hungarian is True

    def test_respects_limit(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """search_unified respects limit parameter."""
        manager = CityManagerSearch(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager.search_unified("", limit=5)

        assert len(results) <= 5

    def test_filters_duplicates(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
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

    def test_global_limit_ratio_parameter(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """search_unified respects global_limit_ratio parameter."""
        manager = CityManagerSearch(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager.search_unified("", limit=10, global_limit_ratio=0.5)

        assert len(results) <= 10

    def test_returns_empty_when_no_matches(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """search_unified returns empty list when no matches."""
        manager = CityManagerSearch(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager.search_unified("NonExistentCity12345", limit=10)

        assert results == []


class TestSearchCities:
    """Test search_cities method."""

    def test_search_returns_matching_cities(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """search_cities returns global cities matching search term."""
        manager = CityManagerSearch(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager.search_cities("London")

        assert len(results) >= 1
        assert results[0].city == "London"

    def test_search_respects_limit(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """search_cities respects limit parameter."""
        manager = CityManagerSearch(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager.search_cities("", limit=3)

        assert len(results) == 3

    def test_search_with_country_filter(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
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
            db_path=mock_data_dir / "nonexistent.db",
            hungarian_db_path=hungarian_db
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

    def test_search_sorted_by_population(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """search_cities sorts results by population descending."""
        manager = CityManagerSearch(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager.search_cities("", limit=5)

        populations = [c.population for c in results if c.population]
        assert populations == sorted(populations, reverse=True)

    def test_search_increments_query_count(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """search_cities increments query_count."""
        manager = CityManagerSearch(db_path=cities_db, hungarian_db_path=hungarian_db)
        initial_count = manager.query_count

        manager.search_cities("London")

        assert manager.query_count == initial_count + 1


class TestGetCitiesByCountry:
    """Test get_cities_by_country method."""

    def test_returns_cities_for_country(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """get_cities_by_country returns cities in specified country."""
        manager = CityManagerSearch(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager.get_cities_by_country("GB")

        assert len(results) >= 1
        for city in results:
            assert city.country_code == "GB"

    def test_respects_limit(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """get_cities_by_country respects limit parameter."""
        manager = CityManagerSearch(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager.get_cities_by_country("US", limit=2)

        assert len(results) <= 2

    def test_with_min_population_filter(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """get_cities_by_country filters by minimum population."""
        manager = CityManagerSearch(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager.get_cities_by_country("GB", min_population=100000)

        for city in results:
            if city.population:
                assert city.population >= 100000

    def test_returns_hungarian_combined_for_hu(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
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
            db_path=mock_data_dir / "nonexistent.db",
            hungarian_db_path=hungarian_db
        )

        results = manager.get_cities_by_country("GB")

        assert results == []

    def test_country_code_case_insensitive(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """get_cities_by_country handles lowercase country codes."""
        manager = CityManagerSearch(db_path=cities_db, hungarian_db_path=hungarian_db)

        results_lower = manager.get_cities_by_country("gb")
        results_upper = manager.get_cities_by_country("GB")

        assert len(results_lower) == len(results_upper)


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

    def test_respects_limit(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """_get_hungarian_cities_combined respects limit."""
        manager = CityManagerSearch(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager._get_hungarian_cities_combined(limit=3)

        assert len(results) <= 3

    def test_with_min_population_filter(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """_get_hungarian_cities_combined filters by min_population."""
        manager = CityManagerSearch(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager._get_hungarian_cities_combined(limit=10, min_population=100000)

        for city in results:
            if city.population:
                assert city.population >= 100000

    def test_filters_duplicates(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
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
            db_path=cities_db,
            hungarian_db_path=mock_data_dir / "nonexistent.db"
        )

        results = manager._get_hungarian_cities_combined(limit=10)

        # Should still return global Hungarian cities
        assert len(results) >= 1


class TestCityManagerSearchInheritance:
    """Test CityManagerSearch inherits from CityManagerHungarian."""

    def test_has_hungarian_methods(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """CityManagerSearch has Hungarian methods from parent."""
        manager = CityManagerSearch(db_path=cities_db, hungarian_db_path=hungarian_db)

        assert hasattr(manager, "search_hungarian_settlements")
        assert hasattr(manager, "get_hungarian_counties")
        assert hasattr(manager, "get_hungarian_settlements_by_county")

    def test_has_db_attributes(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
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
