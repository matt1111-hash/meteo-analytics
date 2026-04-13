"""Tests split from test_city_manager_db_new.py."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from unittest.mock import patch

import pytest
from src.data.city_manager_db import CityDatabaseError, CityManagerDB

# ruff: noqa: F403
from tests.data.test_city_manager_db_new_support import *


class TestCityManagerDBInit:
    """Test CityManagerDB initialization."""

    def test_init_sets_default_paths(self, mock_data_dir: Path) -> None:
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

    def test_init_sets_custom_paths(self, cities_db: Path, hungarian_db: Path) -> None:
        """Initialization with custom database paths."""
        manager = CityManagerDB(db_path=cities_db, hungarian_db_path=hungarian_db)

        assert manager.db_path == cities_db
        assert manager.hungarian_db_path == hungarian_db

    def test_init_initializes_query_counters(self, cities_db: Path, hungarian_db: Path) -> None:
        """Initialization resets query counters."""
        manager = CityManagerDB(db_path=cities_db, hungarian_db_path=hungarian_db)

        assert manager.query_count == 0
        assert manager.hungarian_query_count == 0
        assert manager.last_query_time is None

    def test_init_raises_when_no_databases_available(self, mock_data_dir: Path) -> None:
        """Initialization raises CityDatabaseError when neither database exists."""
        with (
            patch("src.data.city_manager_db.DATA_DIR", mock_data_dir),
            pytest.raises(CityDatabaseError, match="No database available"),
        ):
            CityManagerDB()

    def test_init_connects_to_global_database(self, cities_db: Path, hungarian_db: Path) -> None:
        """Initialization connects to global cities database."""
        manager = CityManagerDB(db_path=cities_db, hungarian_db_path=hungarian_db)

        assert manager.connection is not None
        assert isinstance(manager.connection, sqlite3.Connection)

    def test_init_connects_to_hungarian_database(self, cities_db: Path, hungarian_db: Path) -> None:
        """Initialization connects to Hungarian settlements database."""
        manager = CityManagerDB(db_path=cities_db, hungarian_db_path=hungarian_db)

        assert manager.hungarian_connection is not None
        assert isinstance(manager.hungarian_connection, sqlite3.Connection)

    def test_init_continues_with_hungarian_when_global_missing(
        self, mock_data_dir: Path, hungarian_db: Path
    ) -> None:
        """Initialization uses Hungarian database when global is missing."""
        manager = CityManagerDB(
            db_path=mock_data_dir / "nonexistent.db", hungarian_db_path=hungarian_db
        )

        assert manager.connection is None
        assert manager.hungarian_connection is not None

    def test_init_continues_with_global_when_hungarian_missing(
        self, mock_data_dir: Path, cities_db: Path
    ) -> None:
        """Initialization uses global database when Hungarian is missing."""
        manager = CityManagerDB(
            db_path=cities_db, hungarian_db_path=mock_data_dir / "nonexistent.db"
        )

        assert manager.connection is not None
        assert manager.hungarian_connection is None

    def test_init_sets_row_factory(self, cities_db: Path, hungarian_db: Path) -> None:
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

    def test_validate_returns_early_when_no_connection(self, mock_data_dir: Path) -> None:
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
