"""Tests for CityManagerDB from city_manager_db.py."""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from src.data.city_manager_db import CityManagerDB
from src.data.city_types import CityDatabaseError


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
    conn.execute("INSERT INTO cities VALUES (1, 'Budapest', 47.5, 19.0, 'Hungary', 'HU', 1750000, 'Europe', 'Budapest', 0, 'Europe/Budapest')")
    conn.commit()
    conn.close()
    return db_path


@pytest.fixture
def hungarian_db(mock_data_dir: Path) -> Path:
    """Create minimal Hungarian settlements database."""
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
            region_priority REAL
        )
    """)
    conn.execute("INSERT INTO hungarian_settlements VALUES (1, 'Budapest', 47.5, 19.0, 'Budapest', 'city', 1750000, 'continental', 1.0)")
    conn.commit()
    conn.close()
    return db_path


@pytest.fixture
def incomplete_cities_db(mock_data_dir: Path) -> Path:
    """Create cities database with missing columns."""
    db_path = mock_data_dir / "cities_incomplete.db"
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE cities (
            id INTEGER,
            city TEXT
        )
    """)
    conn.commit()
    conn.close()
    return db_path


@pytest.fixture
def incomplete_hungarian_db(mock_data_dir: Path) -> Path:
    """Create Hungarian database with missing columns."""
    db_path = mock_data_dir / "hungarian_incomplete.db"
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE hungarian_settlements (
            id INTEGER,
            name TEXT
        )
    """)
    conn.commit()
    conn.close()
    return db_path


class TestCityManagerDBInit:
    """Test CityManagerDB initialization."""

    def test_init_sets_default_paths(
        self, mock_data_dir: Path
    ) -> None:
        """Initialization sets default database paths."""
        # Create one database so initialization succeeds
        hungarian_db = mock_data_dir / "hungarian_settlements.db"
        conn = sqlite3.connect(hungarian_db)
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
                region_priority REAL
            )
        """)
        conn.commit()
        conn.close()

        with patch("src.data.city_manager_db.DATA_DIR", mock_data_dir):
            manager = CityManagerDB()

            assert manager.db_path == mock_data_dir / "cities.db"
            assert manager.hungarian_db_path == mock_data_dir / "hungarian_settlements.db"

    def test_init_sets_custom_paths(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """Initialization with custom database paths."""
        manager = CityManagerDB(db_path=cities_db, hungarian_db_path=hungarian_db)

        assert manager.db_path == cities_db
        assert manager.hungarian_db_path == hungarian_db

    def test_init_initializes_query_counters(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """Initialization resets query counters."""
        manager = CityManagerDB(db_path=cities_db, hungarian_db_path=hungarian_db)

        assert manager.query_count == 0
        assert manager.hungarian_query_count == 0
        assert manager.last_query_time is None

    def test_init_raises_when_no_databases_available(
        self, mock_data_dir: Path
    ) -> None:
        """Initialization raises CityDatabaseError when neither database exists."""
        with patch("src.data.city_manager_db.DATA_DIR", mock_data_dir):
            with pytest.raises(CityDatabaseError, match="No database available"):
                CityManagerDB()

    def test_init_connects_to_global_database(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """Initialization connects to global cities database."""
        manager = CityManagerDB(db_path=cities_db, hungarian_db_path=hungarian_db)

        assert manager.connection is not None
        assert isinstance(manager.connection, sqlite3.Connection)

    def test_init_connects_to_hungarian_database(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """Initialization connects to Hungarian settlements database."""
        manager = CityManagerDB(db_path=cities_db, hungarian_db_path=hungarian_db)

        assert manager.hungarian_connection is not None
        assert isinstance(manager.hungarian_connection, sqlite3.Connection)

    def test_init_continues_with_hungarian_when_global_missing(
        self, mock_data_dir: Path, hungarian_db: Path
    ) -> None:
        """Initialization uses Hungarian database when global is missing."""
        manager = CityManagerDB(
            db_path=mock_data_dir / "nonexistent.db",
            hungarian_db_path=hungarian_db
        )

        assert manager.connection is None
        assert manager.hungarian_connection is not None

    def test_init_continues_with_global_when_hungarian_missing(
        self, mock_data_dir: Path, cities_db: Path
    ) -> None:
        """Initialization uses global database when Hungarian is missing."""
        manager = CityManagerDB(
            db_path=cities_db,
            hungarian_db_path=mock_data_dir / "nonexistent.db"
        )

        assert manager.connection is not None
        assert manager.hungarian_connection is None

    def test_init_sets_row_factory(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """Initialization sets row_factory for Row objects."""
        manager = CityManagerDB(db_path=cities_db, hungarian_db_path=hungarian_db)

        assert manager.connection.row_factory == sqlite3.Row
        assert manager.hungarian_connection.row_factory == sqlite3.Row


class TestValidateDatabaseStructure:
    """Test _validate_database_structure method."""

    def test_validate_passes_with_correct_structure(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """_validate_database_structure passes when all required columns exist."""
        manager = CityManagerDB(db_path=cities_db, hungarian_db_path=hungarian_db)

        # Should not raise
        manager._validate_database_structure()

    def test_validate_raises_with_missing_columns(
        self, incomplete_cities_db: Path, hungarian_db: Path
    ) -> None:
        """_validate_database_structure raises when required columns are missing."""
        # The validation happens during __init__, so creating a manager with
        # an incomplete database should raise CityDatabaseError
        with pytest.raises(CityDatabaseError, match="Missing columns"):
            CityManagerDB(db_path=incomplete_cities_db, hungarian_db_path=hungarian_db)

    def test_validate_returns_early_when_no_connection(
        self, mock_data_dir: Path
    ) -> None:
        """_validate_database_structure returns early when connection is None."""
        # Create a minimal DB to allow initialization
        cities_db = mock_data_dir / "cities.db"
        conn = sqlite3.connect(cities_db)
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

        manager = CityManagerDB(db_path=cities_db)
        # Force connection to None (simulating closed connection)
        original_connection = manager.connection
        manager.connection = None

        # Should not raise
        manager._validate_database_structure()

        # Restore for cleanup
        manager.connection = original_connection


class TestValidateHungarianDatabaseStructure:
    """Test _validate_hungarian_database_structure method."""

    def test_validate_hungarian_passes_with_correct_structure(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """_validate_hungarian_database_structure passes when all required columns exist."""
        manager = CityManagerDB(db_path=cities_db, hungarian_db_path=hungarian_db)

        # Should not raise
        manager._validate_hungarian_database_structure()

    def test_validate_hungarian_raises_with_missing_columns(
        self, cities_db: Path, incomplete_hungarian_db: Path
    ) -> None:
        """_validate_hungarian_database_structure raises when required columns are missing."""
        # The validation happens during __init__
        with pytest.raises(CityDatabaseError, match="Missing columns"):
            CityManagerDB(db_path=cities_db, hungarian_db_path=incomplete_hungarian_db)

    def test_validate_hungarian_returns_early_when_no_connection(
        self, cities_db: Path, mock_data_dir: Path
    ) -> None:
        """_validate_hungarian_database_structure returns early when connection is None."""
        # Create a minimal Hungarian DB to allow initialization
        hungarian_db = mock_data_dir / "hungarian_settlements.db"
        conn = sqlite3.connect(hungarian_db)
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
                region_priority REAL
            )
        """)
        conn.commit()
        conn.close()

        manager = CityManagerDB(hungarian_db_path=hungarian_db)
        # Force hungarian_connection to None
        original_conn = manager.hungarian_connection
        manager.hungarian_connection = None

        # Should not raise
        manager._validate_hungarian_database_structure()

        # Restore for cleanup
        manager.hungarian_connection = original_conn


class TestGetTotalCityCount:
    """Test _get_total_city_count method."""

    def test_get_total_city_count_returns_correct_count(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """_get_total_city_count returns actual city count from database."""
        manager = CityManagerDB(db_path=cities_db, hungarian_db_path=hungarian_db)

        count = manager._get_total_city_count()

        assert count == 1  # We inserted 1 city

    def test_get_total_city_count_returns_zero_when_no_connection(
        self, mock_data_dir: Path, hungarian_db: Path
    ) -> None:
        """_get_total_city_count returns 0 when connection is None."""
        manager = CityManagerDB(
            db_path=mock_data_dir / "nonexistent.db",
            hungarian_db_path=hungarian_db
        )
        manager.connection = None

        count = manager._get_total_city_count()

        assert count == 0


class TestGetTotalHungarianSettlementsCount:
    """Test _get_total_hungarian_settlements_count method."""

    def test_get_total_hungarian_count_returns_correct_count(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """_get_total_hungarian_settlements_count returns actual settlement count."""
        manager = CityManagerDB(db_path=cities_db, hungarian_db_path=hungarian_db)

        count = manager._get_total_hungarian_settlements_count()

        assert count == 1  # We inserted 1 settlement

    def test_get_total_hungarian_count_returns_zero_when_no_connection(
        self, cities_db: Path, mock_data_dir: Path
    ) -> None:
        """_get_total_hungarian_settlements_count returns 0 when connection is None."""
        manager = CityManagerDB(
            db_path=cities_db,
            hungarian_db_path=mock_data_dir / "nonexistent.db"
        )
        manager.hungarian_connection = None

        count = manager._get_total_hungarian_settlements_count()

        assert count == 0


class TestExecuteQuery:
    """Test _execute_query method."""

    def test_execute_query_on_global_database(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """_execute_query executes query on global database by default."""
        manager = CityManagerDB(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager._execute_query("SELECT * FROM cities WHERE city = ?", ("Budapest",))

        assert len(results) == 1
        assert results[0]["city"] == "Budapest"

    def test_execute_query_on_hungarian_database(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """_execute_query executes query on Hungarian database when use_hungarian=True."""
        manager = CityManagerDB(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager._execute_query(
            "SELECT * FROM hungarian_settlements WHERE name = ?",
            ("Budapest",),
            use_hungarian=True
        )

        assert len(results) == 1
        assert results[0]["name"] == "Budapest"

    def test_execute_query_increments_global_query_count(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """_execute_query increments global query count."""
        manager = CityManagerDB(db_path=cities_db, hungarian_db_path=hungarian_db)

        manager._execute_query("SELECT * FROM cities")

        assert manager.query_count == 1
        assert manager.hungarian_query_count == 0

    def test_execute_query_increments_hungarian_query_count(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """_execute_query increments Hungarian query count when use_hungarian=True."""
        manager = CityManagerDB(db_path=cities_db, hungarian_db_path=hungarian_db)

        manager._execute_query("SELECT * FROM hungarian_settlements", use_hungarian=True)

        assert manager.query_count == 0
        assert manager.hungarian_query_count == 1

    def test_execute_query_updates_last_query_time(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """_execute_query updates last_query_time."""
        manager = CityManagerDB(db_path=cities_db, hungarian_db_path=hungarian_db)
        assert manager.last_query_time is None

        manager._execute_query("SELECT * FROM cities")

        assert manager.last_query_time is not None
        assert isinstance(manager.last_query_time, datetime)

    def test_execute_query_raises_for_global_when_no_connection(
        self, mock_data_dir: Path, hungarian_db: Path
    ) -> None:
        """_execute_query raises CityDatabaseError when global connection unavailable."""
        manager = CityManagerDB(
            db_path=mock_data_dir / "nonexistent.db",
            hungarian_db_path=hungarian_db
        )
        manager.connection = None

        with pytest.raises(CityDatabaseError, match="Global database connection not available"):
            manager._execute_query("SELECT * FROM cities")

    def test_execute_query_raises_for_hungarian_when_no_connection(
        self, cities_db: Path, mock_data_dir: Path
    ) -> None:
        """_execute_query raises CityDatabaseError when Hungarian connection unavailable."""
        manager = CityManagerDB(
            db_path=cities_db,
            hungarian_db_path=mock_data_dir / "nonexistent.db"
        )
        manager.hungarian_connection = None

        with pytest.raises(CityDatabaseError, match="Hungarian database connection not available"):
            manager._execute_query("SELECT * FROM hungarian_settlements", use_hungarian=True)

    def test_execute_query_raises_on_sql_error(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """_execute_query raises CityDatabaseError on SQL error."""
        manager = CityManagerDB(db_path=cities_db, hungarian_db_path=hungarian_db)

        with pytest.raises(CityDatabaseError, match="Query execution error"):
            manager._execute_query("SELECT * FROM nonexistent_table")


class TestClose:
    """Test close method."""

    def test_close_closes_global_connection(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """close closes global database connection."""
        manager = CityManagerDB(db_path=cities_db, hungarian_db_path=hungarian_db)
        assert manager.connection is not None

        manager.close()

        assert manager.connection is None

    def test_close_closes_hungarian_connection(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """close closes Hungarian database connection."""
        manager = CityManagerDB(db_path=cities_db, hungarian_db_path=hungarian_db)
        assert manager.hungarian_connection is not None

        manager.close()

        assert manager.hungarian_connection is None

    def test_close_closes_both_connections(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """close closes both database connections."""
        manager = CityManagerDB(db_path=cities_db, hungarian_db_path=hungarian_db)
        assert manager.connection is not None
        assert manager.hungarian_connection is not None

        manager.close()

        assert manager.connection is None
        assert manager.hungarian_connection is None

    def test_close_handles_null_connections_gracefully(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """close handles null connections gracefully."""
        manager = CityManagerDB(db_path=cities_db, hungarian_db_path=hungarian_db)
        manager.connection = None
        manager.hungarian_connection = None

        # Should not raise
        manager.close()


class TestErrorHandling:
    """Test error handling scenarios."""

    def test_handles_sqlite_error_on_global_connection(
        self, mock_data_dir: Path, hungarian_db: Path
    ) -> None:
        """Handles SQLite error during global database connection."""
        # Create a file that's not a valid database
        bad_db = mock_data_dir / "bad.db"
        bad_db.write_text("not a database")

        manager = CityManagerDB(db_path=bad_db, hungarian_db_path=hungarian_db)

        assert manager.connection is None
        assert manager.hungarian_connection is not None

    def test_handles_sqlite_error_on_hungarian_connection(
        self, cities_db: Path, mock_data_dir: Path
    ) -> None:
        """Handles SQLite error during Hungarian database connection."""
        # Create a file that's not a valid database
        bad_db = mock_data_dir / "bad_hun.db"
        bad_db.write_text("not a database")

        manager = CityManagerDB(db_path=cities_db, hungarian_db_path=bad_db)

        assert manager.connection is not None
        assert manager.hungarian_connection is None
