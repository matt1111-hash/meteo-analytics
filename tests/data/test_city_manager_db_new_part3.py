"""Tests split from test_city_manager_db_new.py."""

from __future__ import annotations

from src.data.city_manager_db import CityDatabaseError, CityManagerDB

# ruff: noqa: F403, F405
from tests.data.test_city_manager_db_new_support import *


class TestExecuteQuery:
    """Test _execute_query method."""

    def test_execute_query_on_global_database(
        self, cities_db: Path, hungarian_db: Path
    ) -> None:
        """_execute_query executes query on global database by default."""
        manager = CityManagerDB(db_path=cities_db, hungarian_db_path=hungarian_db)

        results = manager._execute_query(
            "SELECT * FROM cities WHERE city = ?", ("Budapest",)
        )

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
            use_hungarian=True,
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

        manager._execute_query(
            "SELECT * FROM hungarian_settlements", use_hungarian=True
        )

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
            db_path=mock_data_dir / "nonexistent.db", hungarian_db_path=hungarian_db
        )
        manager.connection = None

        with pytest.raises(
            CityDatabaseError, match="Global database connection not available"
        ):
            manager._execute_query("SELECT * FROM cities")

    def test_execute_query_raises_for_hungarian_when_no_connection(
        self, cities_db: Path, mock_data_dir: Path
    ) -> None:
        """_execute_query raises CityDatabaseError when Hungarian connection unavailable."""
        manager = CityManagerDB(
            db_path=cities_db, hungarian_db_path=mock_data_dir / "nonexistent.db"
        )
        manager.hungarian_connection = None

        with pytest.raises(
            CityDatabaseError, match="Hungarian database connection not available"
        ):
            manager._execute_query(
                "SELECT * FROM hungarian_settlements", use_hungarian=True
            )

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
