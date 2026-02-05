#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tests for src.data.city_manager_db.CityManagerDB
"""

import sqlite3
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.data.city_manager_db import CityManagerDB
from src.data.city_types import CityDatabaseError


# Helper function for valid PRAGMA table_info results
def pragma_cities_columns():
    """Return valid PRAGMA table_info result for cities table."""
    return [
        (0, "id", "INTEGER", 0, None, 0),
        (1, "city", "TEXT", 0, None, 0),
        (2, "lat", "REAL", 0, None, 0),
        (3, "lon", "REAL", 0, None, 0),
        (4, "country", "TEXT", 0, None, 0),
        (5, "country_code", "TEXT", 0, None, 0),
        (6, "population", "INTEGER", 0, None, 0),
        (7, "continent", "TEXT", 0, None, 0),
        (8, "admin_name", "TEXT", 0, None, 0),
        (9, "capital", "TEXT", 0, None, 0),
        (10, "timezone", "TEXT", 0, None, 0),
    ]


def pragma_hungarian_columns():
    """Return valid PRAGMA table_info result for hungarian_settlements table."""
    return [
        (0, "id", "INTEGER", 0, None, 1),
        (1, "name", "TEXT", 0, None, 0),
        (2, "latitude", "REAL", 0, None, 0),
        (3, "longitude", "REAL", 0, None, 0),
        (4, "megye", "TEXT", 0, None, 0),
        (5, "settlement_type", "TEXT", 0, None, 0),
        (6, "population", "INTEGER", 0, None, 0),
        (7, "climate_zone", "TEXT", 0, None, 0),
        (8, "region_priority", "INTEGER", 0, None, 0),
    ]


def setup_mock_connection(mock_cursor, has_global=True, has_hungarian=False):
    """Setup mock connection with database responses."""
    results = []
    if has_global:
        results.extend([
            pragma_cities_columns(),  # PRAGMA for global
        ])
    if has_hungarian:
        results.extend([
            pragma_hungarian_columns(),  # PRAGMA for Hungarian
        ])

    # Setup fetchall for PRAGMA queries
    mock_cursor.fetchall.side_effect = results

    # Setup fetchone for COUNT queries
    fetchone_values = []
    if has_global:
        fetchone_values.append([50000])  # COUNT(*) from cities
    if has_hungarian:
        fetchone_values.append([3200])  # COUNT(*) from hungarian_settlements

    if fetchone_values:
        mock_cursor.fetchone.side_effect = fetchone_values
    else:
        mock_cursor.fetchone.return_value = [0]


class TestCityManagerDBInit:
    """Test CityManagerDB initialization."""

    def test_init_with_default_paths(self, tmp_path):
        """Test initialization with default database paths."""
        with patch('src.data.city_manager_db.DATA_DIR', tmp_path):
            global_db = tmp_path / "cities.db"
            global_db.touch()

            with patch('sqlite3.connect') as mock_connect:
                mock_conn = MagicMock()
                mock_connect.return_value = mock_conn
                mock_cursor = MagicMock()
                mock_conn.cursor.return_value = mock_cursor
                setup_mock_connection(mock_cursor, has_global=True)

                manager = CityManagerDB()

                assert manager.db_path == global_db

    def test_init_with_custom_paths(self, tmp_path):
        """Test initialization with custom database paths."""
        global_db = tmp_path / "custom_cities.db"
        global_db.touch()

        with patch('sqlite3.connect') as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            setup_mock_connection(mock_cursor, has_global=True)

            manager = CityManagerDB(db_path=global_db, hun_db=tmp_path / "hun.db")

            assert manager.db_path == global_db

    def test_init_no_database_raises_error(self, tmp_path):
        """Test initialization raises error when no database available."""
        with patch('src.data.city_manager_db.DATA_DIR', tmp_path):
            with pytest.raises(CityDatabaseError, match="No database available"):
                CityManagerDB()

    def test_init_initializes_stats(self, tmp_path):
        """Test initialization sets statistics to zero."""
        with patch('src.data.city_manager_db.DATA_DIR', tmp_path):
            global_db = tmp_path / "cities.db"
            global_db.touch()

            with patch('sqlite3.connect') as mock_connect:
                mock_conn = MagicMock()
                mock_connect.return_value = mock_conn
                mock_cursor = MagicMock()
                mock_conn.cursor.return_value = mock_cursor
                setup_mock_connection(mock_cursor, has_global=True)

                manager = CityManagerDB()

                assert manager.query_count == 0
                assert manager.hungarian_query_count == 0
                assert manager.last_query_time is None


class TestDatabaseValidation:
    """Test database structure validation."""

    def test_validate_global_db_structure_valid(self, tmp_path):
        """Test validation passes for correct global database structure."""
        with patch('src.data.city_manager_db.DATA_DIR', tmp_path):
            global_db = tmp_path / "cities.db"
            global_db.touch()

            with patch('sqlite3.connect') as mock_connect:
                mock_conn = MagicMock()
                mock_connect.return_value = mock_conn
                mock_cursor = MagicMock()
                mock_conn.cursor.return_value = mock_cursor
                setup_mock_connection(mock_cursor, has_global=True)

                CityManagerDB()  # Should not raise

    def test_validate_global_db_missing_columns_raises(self, tmp_path):
        """Test validation raises error for missing columns."""
        with patch('src.data.city_manager_db.DATA_DIR', tmp_path):
            global_db = tmp_path / "cities.db"
            global_db.touch()

            with patch('sqlite3.connect') as mock_connect:
                mock_conn = MagicMock()
                mock_connect.return_value = mock_conn
                mock_cursor = MagicMock()
                mock_conn.cursor.return_value = mock_cursor
                # Return incomplete column list
                mock_cursor.fetchall.side_effect = [
                    [(0, "id", "INTEGER", 0, None, 0), (1, "city", "TEXT", 0, None, 0)]
                ]
                # fetchone should not be called since validation fails

                with pytest.raises(CityDatabaseError, match="Missing columns"):
                    CityManagerDB()

    def test_validate_hungarian_db_structure_valid(self, tmp_path):
        """Test validation passes for correct Hungarian database structure."""
        with patch('src.data.city_manager_db.DATA_DIR', tmp_path):
            global_db = tmp_path / "cities.db"
            hun_db = tmp_path / "hungarian_settlements.db"
            global_db.touch()
            hun_db.touch()

            with patch('sqlite3.connect') as mock_connect:
                mock_conn = MagicMock()
                mock_connect.return_value = mock_conn
                mock_cursor = MagicMock()
                mock_conn.cursor.return_value = mock_cursor
                setup_mock_connection(mock_cursor, has_global=True, has_hungarian=True)

                CityManagerDB()  # Should not raise

    def test_validate_hungarian_db_missing_columns_raises(self, tmp_path):
        """Test validation raises error for missing Hungarian columns."""
        with patch('src.data.city_manager_db.DATA_DIR', tmp_path):
            global_db = tmp_path / "cities.db"
            hun_db = tmp_path / "hungarian_settlements.db"
            global_db.touch()
            hun_db.touch()

            with patch('sqlite3.connect') as mock_connect:
                mock_conn = MagicMock()
                mock_connect.return_value = mock_conn
                mock_cursor = MagicMock()
                mock_conn.cursor.return_value = mock_cursor
                mock_cursor.fetchall.side_effect = [
                    pragma_cities_columns(),  # Global OK
                    [(0, "id", "INTEGER", 0, None, 0), (1, "name", "TEXT", 0, None, 0)]  # Hungarian incomplete
                ]
                # Global DB succeeds, needs count
                mock_cursor.fetchone.return_value = [1000]

                with pytest.raises(CityDatabaseError, match="Missing columns"):
                    CityManagerDB()


class TestDatabaseErrors:
    """Test database connection error handling."""

    def test_global_db_connection_error_logs_warning(self, tmp_path):
        """Test connection error to global DB logs warning."""
        with patch('src.data.city_manager_db.DATA_DIR', tmp_path):
            global_db = tmp_path / "cities.db"
            hun_db = tmp_path / "hungarian_settlements.db"
            global_db.touch()
            hun_db.touch()

            with patch('sqlite3.connect') as mock_connect:
                mock_hun_conn = MagicMock()
                mock_cursor = MagicMock()
                # Global fails, Hungarian succeeds
                mock_connect.side_effect = [
                    sqlite3.Error("Connection failed"),
                    mock_hun_conn
                ]
                mock_hun_conn.cursor.return_value = mock_cursor
                mock_cursor.fetchall.side_effect = [
                    pragma_hungarian_columns(),
                ]
                mock_cursor.fetchone.return_value = [3200]

                # Should not raise - falls back to Hungarian
                CityManagerDB()

    def test_hungarian_db_connection_error_logs_warning(self, tmp_path):
        """Test connection error to Hungarian DB logs warning."""
        with patch('src.data.city_manager_db.DATA_DIR', tmp_path):
            global_db = tmp_path / "cities.db"
            hun_db = tmp_path / "hungarian_settlements.db"
            global_db.touch()
            hun_db.touch()

            with patch('sqlite3.connect') as mock_connect:
                mock_global_conn = MagicMock()
                mock_cursor = MagicMock()
                # Global succeeds, Hungarian fails
                mock_connect.side_effect = [
                    mock_global_conn,
                    sqlite3.Error("Connection failed")
                ]
                mock_global_conn.cursor.return_value = mock_cursor
                mock_cursor.fetchall.side_effect = [
                    pragma_cities_columns(),
                ]
                mock_cursor.fetchone.return_value = [1000]

                # Should not raise - has global database
                CityManagerDB()


class TestExecuteQuery:
    """Test _execute_query method."""

    def test_execute_query_on_global_db(self, tmp_path):
        """Test executing query on global database."""
        with patch('src.data.city_manager_db.DATA_DIR', tmp_path):
            global_db = tmp_path / "cities.db"
            global_db.touch()

            with patch('sqlite3.connect') as mock_connect:
                mock_conn = MagicMock()
                mock_connect.return_value = mock_conn
                mock_cursor = MagicMock()
                mock_conn.cursor.return_value = mock_cursor
                mock_cursor.fetchall.side_effect = [
                    pragma_cities_columns(),
                    [("Budapest", "HU", 47.4979, 19.0402)]
                ]
                mock_cursor.fetchone.return_value = [1000]

                manager = CityManagerDB()
                results = manager._execute_query("SELECT * FROM cities")

                assert len(results) == 1
                assert results[0][0] == "Budapest"
                assert manager.query_count == 1

    def test_execute_query_on_hungarian_db(self, tmp_path):
        """Test executing query on Hungarian database."""
        with patch('src.data.city_manager_db.DATA_DIR', tmp_path):
            global_db = tmp_path / "cities.db"
            hun_db = tmp_path / "hungarian_settlements.db"
            global_db.touch()
            hun_db.touch()

            with patch('sqlite3.connect') as mock_connect:
                mock_conn = MagicMock()
                mock_connect.return_value = mock_conn
                mock_cursor = MagicMock()
                mock_conn.cursor.return_value = mock_cursor
                mock_cursor.fetchall.side_effect = [
                    pragma_cities_columns(),
                    pragma_hungarian_columns(),
                    [("Pécs", "Baranya", 45.0, 18.0)]
                ]
                mock_cursor.fetchone.side_effect = [[1000], [3200]]

                manager = CityManagerDB()
                results = manager._execute_query("SELECT * FROM hungarian_settlements", use_hungarian=True)

                assert len(results) == 1
                assert results[0][0] == "Pécs"
                assert manager.hungarian_query_count == 1

    def test_execute_query_no_connection_raises(self, tmp_path):
        """Test query raises error when database not available."""
        with patch('src.data.city_manager_db.DATA_DIR', tmp_path):
            global_db = tmp_path / "cities.db"
            global_db.touch()

            with patch('sqlite3.connect') as mock_connect:
                mock_conn = MagicMock()
                mock_connect.return_value = mock_conn
                mock_cursor = MagicMock()
                mock_conn.cursor.return_value = mock_cursor
                setup_mock_connection(mock_cursor, has_global=True)

                manager = CityManagerDB()
                manager.connection = None  # Simulate no connection

                with pytest.raises(CityDatabaseError, match="database connection not available"):
                    manager._execute_query("SELECT * FROM cities")

    def test_execute_query_sql_error_raises(self, tmp_path):
        """Test query raises error on SQL error."""
        with patch('src.data.city_manager_db.DATA_DIR', tmp_path):
            global_db = tmp_path / "cities.db"
            global_db.touch()

            with patch('sqlite3.connect') as mock_connect:
                mock_conn = MagicMock()
                mock_connect.return_value = mock_conn
                mock_cursor = MagicMock()
                mock_conn.cursor.return_value = mock_cursor
                mock_cursor.fetchall.side_effect = [
                    pragma_cities_columns(),
                ]
                mock_cursor.fetchone.return_value = [1000]

                manager = CityManagerDB()
                # Set error AFTER initialization
                mock_cursor.execute.side_effect = sqlite3.Error("SQL syntax error")

                with pytest.raises(CityDatabaseError, match="Query execution error"):
                    manager._execute_query("INVALID SQL")

    def test_execute_query_updates_last_query_time(self, tmp_path):
        """Test query updates last_query_time."""
        with patch('src.data.city_manager_db.DATA_DIR', tmp_path):
            global_db = tmp_path / "cities.db"
            global_db.touch()

            with patch('sqlite3.connect') as mock_connect:
                mock_conn = MagicMock()
                mock_connect.return_value = mock_conn
                mock_cursor = MagicMock()
                mock_conn.cursor.return_value = mock_cursor
                mock_cursor.fetchall.side_effect = [
                    pragma_cities_columns(),
                    [("Budapest",)]
                ]
                mock_cursor.fetchone.return_value = [1000]

                manager = CityManagerDB()
                assert manager.last_query_time is None

                manager._execute_query("SELECT * FROM cities")

                assert manager.last_query_time is not None


class TestClose:
    """Test database connection closing."""

    def test_close_closes_global_connection(self, tmp_path):
        """Test close() closes global database connection."""
        with patch('src.data.city_manager_db.DATA_DIR', tmp_path):
            global_db = tmp_path / "cities.db"
            global_db.touch()

            with patch('sqlite3.connect') as mock_connect:
                mock_conn = MagicMock()
                mock_connect.return_value = mock_conn
                mock_cursor = MagicMock()
                mock_conn.cursor.return_value = mock_cursor
                setup_mock_connection(mock_cursor, has_global=True)

                manager = CityManagerDB()
                assert manager.connection is not None

                manager.close()

                assert manager.connection is None
                mock_conn.close.assert_called_once()

    def test_close_closes_hungarian_connection(self, tmp_path):
        """Test close() closes Hungarian database connection."""
        with patch('src.data.city_manager_db.DATA_DIR', tmp_path):
            global_db = tmp_path / "cities.db"
            hun_db = tmp_path / "hungarian_settlements.db"
            global_db.touch()
            hun_db.touch()

            with patch('sqlite3.connect') as mock_connect:
                mock_conn = MagicMock()
                mock_hun_conn = MagicMock()
                mock_connect.side_effect = [mock_conn, mock_hun_conn]
                mock_cursor = MagicMock()
                mock_conn.cursor.return_value = mock_cursor
                mock_hun_conn.cursor.return_value = mock_cursor
                setup_mock_connection(mock_cursor, has_global=True, has_hungarian=True)

                manager = CityManagerDB()
                assert manager.hungarian_connection is not None

                manager.close()

                assert manager.hungarian_connection is None
                mock_hun_conn.close.assert_called_once()

    def test_close_with_no_connections(self, tmp_path):
        """Test close() handles no connections gracefully."""
        with patch('src.data.city_manager_db.DATA_DIR', tmp_path):
            global_db = tmp_path / "cities.db"
            global_db.touch()

            with patch('sqlite3.connect') as mock_connect:
                mock_conn = MagicMock()
                mock_connect.return_value = mock_conn
                mock_cursor = MagicMock()
                mock_conn.cursor.return_value = mock_cursor
                setup_mock_connection(mock_cursor, has_global=True)

                manager = CityManagerDB()
                manager.close()
                # Close again - should not raise
                manager.close()


class TestGetCityCount:
    """Test city count retrieval methods."""

    def test_get_total_city_count(self, tmp_path):
        """Test _get_total_city_count returns correct count."""
        with patch('src.data.city_manager_db.DATA_DIR', tmp_path):
            global_db = tmp_path / "cities.db"
            global_db.touch()

            with patch('sqlite3.connect') as mock_connect:
                mock_conn = MagicMock()
                mock_connect.return_value = mock_conn
                mock_cursor = MagicMock()
                mock_conn.cursor.return_value = mock_cursor
                mock_cursor.fetchall.side_effect = [
                    pragma_cities_columns(),
                ]
                mock_cursor.fetchone.return_value = [50000]

                manager = CityManagerDB()
                count = manager._get_total_city_count()

                assert count == 50000

    def test_get_total_city_count_no_connection_returns_zero(self, tmp_path):
        """Test _get_total_city_count returns 0 when no connection."""
        with patch('src.data.city_manager_db.DATA_DIR', tmp_path):
            global_db = tmp_path / "cities.db"
            global_db.touch()

            with patch('sqlite3.connect') as mock_connect:
                mock_conn = MagicMock()
                mock_connect.return_value = mock_conn
                mock_cursor = MagicMock()
                mock_conn.cursor.return_value = mock_cursor
                setup_mock_connection(mock_cursor, has_global=True)

                manager = CityManagerDB()
                manager.connection = None

                count = manager._get_total_city_count()

                assert count == 0

    def test_get_total_hungarian_settlements_count(self, tmp_path):
        """Test _get_total_hungarian_settlements_count returns correct count."""
        with patch('src.data.city_manager_db.DATA_DIR', tmp_path):
            global_db = tmp_path / "cities.db"
            hun_db = tmp_path / "hungarian_settlements.db"
            global_db.touch()
            hun_db.touch()

            with patch('sqlite3.connect') as mock_connect:
                mock_conn = MagicMock()
                mock_connect.return_value = mock_conn
                mock_cursor = MagicMock()
                mock_conn.cursor.return_value = mock_cursor
                mock_cursor.fetchall.side_effect = [
                    pragma_cities_columns(),
                    pragma_hungarian_columns(),
                ]
                # Direct assignment for initialization (global count)
                mock_cursor.fetchone.return_value = [1000]

                manager = CityManagerDB()

                # After init, change fetchone to return Hungarian count
                mock_cursor.fetchone.return_value = [3155]
                count = manager._get_total_hungarian_settlements_count()

                assert count == 3155
