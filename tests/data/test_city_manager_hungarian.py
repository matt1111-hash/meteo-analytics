"""Tests for CityManagerHungarian from city_manager_hungarian.py."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from unittest.mock import patch

import pytest

from src.data.city_manager_hungarian import CityManagerHungarian
from src.data.city_types import City


@pytest.fixture
def mock_data_dir(tmp_path: Path) -> Path:
    """Create temporary data directory."""
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


@pytest.fixture
def cities_db(mock_data_dir: Path) -> Path:
    """Create minimal cities database."""
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
    conn.execute(
        "INSERT INTO cities VALUES (1, 'Budapest', 47.5, 19.0, 'Hungary', 'HU', 1750000, 'Europe', 'Budapest', 0, 'Europe/Budapest')"
    )
    conn.commit()
    conn.close()
    return db_path


@pytest.fixture
def hungarian_db(mock_data_dir: Path) -> Path:
    """Create Hungarian settlements database with multiple records."""
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
    # Insert diverse test data
    test_data = [
        (1, "Budapest", 47.4979, 19.0402, "Budapest", "főváros", 1752286, "continental", 10.0, None, 52500, 800000),
        (2, "Debrecen", 47.5314, 21.6269, "Hajdú-Bihar", "város", 201881, "continental", 5.0, "Debreceni", 4210, 85000),
        (3, "Szeged", 46.2530, 20.1414, "Csongrád-Csanád", "város", 161837, "continental", 5.0, "Szegedi", 2810, 72000),
        (4, "Miskolc", 48.1035, 20.7784, "Borsod-Abaúj-Zemplén", "város", 157177, "continental", 5.0, "Miskolci", 2360, 70000),
        (5, "Pécs", 46.0727, 18.2323, "Baranya", "város", 145347, "continental", 5.0, "Pécsi", 1630, 65000),
        (6, "Kiskunhalas", 46.4315, 19.4867, "Bács-Kiskun", "város", 18254, "continental", 3.0, "Kiskunhalasi", 350, 8000),
        (7, "Kiskunfélegyháza", 46.7156, 19.9422, "Bács-Kiskun", "város", 28817, "continental", 3.0, "Kiskunfélegyházi", 290, 12000),
        (8, "Kecskemét", 46.8964, 19.6897, "Bács-Kiskun", "város", 110034, "continental", 4.0, "Kecskeméti", 3200, 48000),
        (9, "Kiskőrös", 46.6208, 19.2797, "Bács-Kiskun", "város", 13532, "continental", 2.0, "Kiskőrösi", 150, 6000),
        (10, "Soltvadkert", 46.4769, 19.3833, "Bács-Kiskun", "város", 7270, "continental", 1.0, "Soltvadkerti", 80, 3200),
        (11, "Akasztó", 46.5333, 19.3000, "Bács-Kiskun", "község", 1500, "continental", 1.0, "Kiskőrösi", 35, 650),
        (12, "Harkakötör", 46.4667, 19.4333, "Bács-Kiskun", "község", 800, "continental", 1.0, "Kiskunhalasi", 20, 350),
        (13, "Szeghalom", 47.0333, 21.1667, "Békés", "város", 9200, "continental", 2.0, "Szeghalmi", 95, 4000),
        (14, "Békéscsaba", 46.6756, 21.0875, "Békés", "város", 58024, "continental", 3.0, "Békéscsabai", 610, 26000),
        (15, "Gyula", 46.6500, 21.2667, "Békés", "város", 30000, "continental", 2.0, "Gyulai", 255, 13500),
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


class TestSearchHungarianSettlements:
    """Test search_hungarian_settlements method."""

    def test_search_returns_matching_settlements(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """search_hungarian_settlements returns settlements matching search term."""
        manager = CityManagerHungarian(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager.search_hungarian_settlements("Budapest")

        assert len(results) == 1
        assert results[0].city == "Budapest"
        assert results[0].is_hungarian is True

    def test_search_returns_multiple_matches(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """search_hungarian_settlements returns multiple matching settlements."""
        manager = CityManagerHungarian(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager.search_hungarian_settlements("Kiskun")

        # Kiskunhalas and Kiskunfélegyháza match "Kiskun"
        assert len(results) >= 2
        names = [c.city for c in results]
        assert "Kiskunhalas" in names
        assert "Kiskunfélegyháza" in names

    def test_search_respects_limit(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """search_hungarian_settlements respects limit parameter."""
        manager = CityManagerHungarian(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager.search_hungarian_settlements("Kiskun", limit=2)

        assert len(results) == 2

    def test_search_with_county_filter(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """search_hungarian_settlements filters by county."""
        manager = CityManagerHungarian(db_path=cities_db, hungarian_db_path=hungarian_db)

        # Search for empty string in Bács-Kiskun to get all settlements in county
        results = manager.search_hungarian_settlements(
            "", county_filter="Bács-Kiskun", limit=10
        )

        # Should have multiple settlements in Bács-Kiskun
        assert len(results) >= 5
        for city in results:
            assert city.megye == "Bács-Kiskun"

    def test_search_with_settlement_type_filter(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """search_hungarian_settlements filters by settlement type."""
        manager = CityManagerHungarian(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager.search_hungarian_settlements(
            "", settlement_type_filter="község"
        )

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
            db_path=cities_db,
            hungarian_db_path=mock_data_dir / "nonexistent.db"
        )

        results = manager.search_hungarian_settlements("Budapest")

        assert results == []

    def test_search_uses_like_search(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
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

    def test_returns_list_of_counties(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """get_hungarian_counties returns list of unique counties."""
        manager = CityManagerHungarian(db_path=cities_db, hungarian_db_path=hungarian_db)

        counties = manager.get_hungarian_counties()

        assert isinstance(counties, list)
        assert "Budapest" in counties
        assert "Bács-Kiskun" in counties

    def test_returns_sorted_list(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """get_hungarian_counties returns alphabetically sorted list."""
        manager = CityManagerHungarian(db_path=cities_db, hungarian_db_path=hungarian_db)

        counties = manager.get_hungarian_counties()

        assert counties == sorted(counties)

    def test_uses_cache(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
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
            db_path=cities_db,
            hungarian_db_path=mock_data_dir / "nonexistent.db"
        )

        counties = manager.get_hungarian_counties()

        assert counties == []

    def test_returns_empty_list_for_empty_database(
        self, cities_db: Path, empty_hungarian_db: Path
    ) -> None:
        """get_hungarian_counties returns empty list for empty database."""
        manager = CityManagerHungarian(
            db_path=cities_db, hungarian_db_path=empty_hungarian_db
        )

        counties = manager.get_hungarian_counties()

        assert counties == []


class TestGetHungarianSettlementTypes:
    """Test get_hungarian_settlement_types method."""

    def test_returns_list_of_types(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """get_hungarian_settlement_types returns list of settlement types."""
        manager = CityManagerHungarian(db_path=cities_db, hungarian_db_path=hungarian_db)

        types = manager.get_hungarian_settlement_types()

        assert isinstance(types, list)
        assert "város" in types
        assert "község" in types
        assert "főváros" in types

    def test_returns_sorted_list(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """get_hungarian_settlement_types returns sorted list."""
        manager = CityManagerHungarian(db_path=cities_db, hungarian_db_path=hungarian_db)

        types = manager.get_hungarian_settlement_types()

        assert types == sorted(types)

    def test_returns_empty_list_when_no_connection(
        self, cities_db: Path, mock_data_dir: Path
    ) -> None:
        """get_hungarian_settlement_types returns empty list when DB unavailable."""
        manager = CityManagerHungarian(
            db_path=cities_db,
            hungarian_db_path=mock_data_dir / "nonexistent.db"
        )

        types = manager.get_hungarian_settlement_types()

        assert types == []

    def test_returns_empty_list_for_empty_database(
        self, cities_db: Path, empty_hungarian_db: Path
    ) -> None:
        """get_hungarian_settlement_types returns empty list for empty database."""
        manager = CityManagerHungarian(
            db_path=cities_db, hungarian_db_path=empty_hungarian_db
        )

        types = manager.get_hungarian_settlement_types()

        assert types == []


class TestGetHungarianSettlementsByCounty:
    """Test get_hungarian_settlements_by_county method."""

    def test_returns_settlements_by_county(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """get_hungarian_settlements_by_county returns settlements in county."""
        manager = CityManagerHungarian(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager.get_hungarian_settlements_by_county("Bács-Kiskun")

        assert len(results) >= 3
        for city in results:
            assert city.megye == "Bács-Kiskun"
            assert city.is_hungarian is True

    def test_respects_limit(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """get_hungarian_settlements_by_county respects limit parameter."""
        manager = CityManagerHungarian(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager.get_hungarian_settlements_by_county("Bács-Kiskun", limit=3)

        assert len(results) == 3

    def test_returns_empty_list_when_no_match(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """get_hungarian_settlements_by_county returns empty list for unknown county."""
        manager = CityManagerHungarian(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager.get_hungarian_settlements_by_county("NonExistentCounty")

        assert results == []

    def test_returns_empty_list_when_no_connection(
        self, cities_db: Path, mock_data_dir: Path
    ) -> None:
        """get_hungarian_settlements_by_county returns empty list when DB unavailable."""
        manager = CityManagerHungarian(
            db_path=cities_db,
            hungarian_db_path=mock_data_dir / "nonexistent.db"
        )

        results = manager.get_hungarian_settlements_by_county("Budapest")

        assert results == []

    def test_sorted_by_priority_and_population(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """get_hungarian_settlements_by_county sorts by priority then population."""
        manager = CityManagerHungarian(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager.get_hungarian_settlements_by_county("Bács-Kiskun", limit=10)

        # First result should be Kecskemét (highest priority + population)
        assert results[0].city == "Kecskemét"

    def test_increments_hungarian_query_count(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """get_hungarian_settlements_by_county increments hungarian_query_count."""
        manager = CityManagerHungarian(db_path=cities_db, hungarian_db_path=hungarian_db)
        initial_count = manager.hungarian_query_count

        manager.get_hungarian_settlements_by_county("Bács-Kiskun")

        assert manager.hungarian_query_count == initial_count + 1


class TestCityManagerHungarianInheritance:
    """Test CityManagerHungarian inherits from CityManagerDB."""

    def test_has_connection_attribute(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """CityManagerHungarian has connection attribute from parent."""
        manager = CityManagerHungarian(db_path=cities_db, hungarian_db_path=hungarian_db)

        assert hasattr(manager, "connection")
        assert manager.connection is not None

    def test_has_hungarian_connection_attribute(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """CityManagerHungarian has hungarian_connection attribute from parent."""
        manager = CityManagerHungarian(db_path=cities_db, hungarian_db_path=hungarian_db)

        assert hasattr(manager, "hungarian_connection")
        assert manager.hungarian_connection is not None

    def test_has_query_count_attributes(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """CityManagerHungarian has query count attributes from parent."""
        manager = CityManagerHungarian(db_path=cities_db, hungarian_db_path=hungarian_db)

        assert hasattr(manager, "query_count")
        assert hasattr(manager, "hungarian_query_count")

    def test_has_execute_query_method(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """CityManagerHungarian has _execute_query method from parent."""
        manager = CityManagerHungarian(db_path=cities_db, hungarian_db_path=hungarian_db)

        assert hasattr(manager, "_execute_query")
        assert callable(manager._execute_query)

    def test_has_close_method(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """CityManagerHungarian has close method from parent."""
        manager = CityManagerHungarian(db_path=cities_db, hungarian_db_path=hungarian_db)

        assert hasattr(manager, "close")
        assert callable(manager.close)


class TestCityManagerHungarianEdgeCases:
    """Edge case tests for CityManagerHungarian."""

    def test_search_with_special_characters(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """search_hungarian_settlements handles special Hungarian characters."""
        manager = CityManagerHungarian(db_path=cities_db, hungarian_db_path=hungarian_db)

        # Search with Hungarian special characters (á, é, í, ó, ö, ő, ú, ü, ű)
        results = manager.search_hungarian_settlements("Békéscsaba")

        assert len(results) >= 1
        names = [c.city for c in results]
        assert "Békéscsaba" in names

    def test_search_case_insensitive(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """search_hungarian_settlements is case insensitive."""
        manager = CityManagerHungarian(db_path=cities_db, hungarian_db_path=hungarian_db)

        results_lower = manager.search_hungarian_settlements("budapest")
        results_upper = manager.search_hungarian_settlements("BUDAPEST")

        assert len(results_lower) == len(results_upper) == 1

    def test_search_empty_string(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """search_hungarian_settlements with empty string returns all settlements."""
        manager = CityManagerHungarian(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager.search_hungarian_settlements("", limit=5)

        assert len(results) == 5

    def test_search_combined_filters(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """search_hungarian_settlements works with combined filters."""
        manager = CityManagerHungarian(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager.search_hungarian_settlements(
            "Kiskun",
            county_filter="Bács-Kiskun",
            settlement_type_filter="város",
            limit=5
        )

        assert len(results) >= 1
        for city in results:
            assert "Kiskun" in city.city
            assert city.megye == "Bács-Kiskun"
            assert city.settlement_type == "város"

    def test_get_counties_cache_persists(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """Counties cache persists across multiple calls."""
        manager = CityManagerHungarian(db_path=cities_db, hungarian_db_path=hungarian_db)

        counties1 = manager.get_hungarian_counties()
        # Manually modify cache to test it's being used
        manager._hungarian_counties_cache = ["Modified"]

        counties2 = manager.get_hungarian_counties()

        assert counties2 == ["Modified"]

        # Restore
        manager._hungarian_counties_cache = counties1
