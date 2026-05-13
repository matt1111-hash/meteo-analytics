#!/usr/bin/env python3

"""
City Manager - Database Connection and Initialization
Global Weather Analyzer project

Part of the city_manager refactoring - split into focused modules.
"""

import logging
import sqlite3
import threading
from datetime import datetime
from pathlib import Path

from src.config import DATA_DIR

from .city_types import CityDatabaseError

logger = logging.getLogger(__name__)


class CityManagerDB:
    """
    Database connection and initialization for CityManager.

    Uses thread-local connections for safe concurrent access.
    Dual database setup:
    - Global cities from cities.db (44k cities)
    - Hungarian settlements from hungarian_settlements.db (3200+ settlements)
    """

    def __init__(self, db_path: Path | None = None, hungarian_db_path: Path | None = None):
        """Initialize database paths and thread-local storage."""
        self.db_path = db_path or (DATA_DIR / "cities.db")
        self.hungarian_db_path = hungarian_db_path or (DATA_DIR / "hungarian_settlements.db")

        self._local = threading.local()
        self._closed = False
        self._global_db_valid = True
        self._hungarian_db_valid = True

        self.query_count = 0
        self.hungarian_query_count = 0
        self.last_query_time: datetime | None = None

        logger.info("Dual Database initialization:")
        logger.info(f"   Global cities: {self.db_path}")
        logger.info(f"   Hungarian settlements: {self.hungarian_db_path}")

        self._initialize_databases()

    @property
    def connection(self) -> sqlite3.Connection | None:
        """Thread-local global database connection (lazy per-thread)."""
        conn = getattr(self._local, "connection", None)
        if conn is None and not self._closed and self._global_db_valid and self.db_path.exists():
            try:
                conn = sqlite3.connect(self.db_path)
                conn.row_factory = sqlite3.Row
                self._local.connection = conn
            except sqlite3.Error as e:
                logger.error(f"Thread-local global connection error: {e}")
                return None
        return conn

    @connection.setter
    def connection(self, value: sqlite3.Connection | None) -> None:
        self._local.connection = value

    @property
    def hungarian_connection(self) -> sqlite3.Connection | None:
        """Thread-local Hungarian database connection (lazy per-thread)."""
        conn = getattr(self._local, "hungarian_connection", None)
        if (
            conn is None
            and not self._closed
            and self._hungarian_db_valid
            and self.hungarian_db_path.exists()
        ):
            try:
                conn = sqlite3.connect(self.hungarian_db_path)
                conn.row_factory = sqlite3.Row
                self._local.hungarian_connection = conn
            except sqlite3.Error as e:
                logger.error(f"Thread-local Hungarian connection error: {e}")
                return None
        return conn

    @hungarian_connection.setter
    def hungarian_connection(self, value: sqlite3.Connection | None) -> None:
        self._local.hungarian_connection = value

    def _initialize_databases(self) -> None:
        """Validate dual databases on startup."""
        if not self.db_path.exists():
            self._global_db_valid = False
            logger.warning(f"Global cities.db not found: {self.db_path}")
            logger.warning("   Only Hungarian settlements will be available!")
        else:
            try:
                conn = sqlite3.connect(self.db_path)
                conn.row_factory = sqlite3.Row
                self._validate_database_structure_with(conn)
                total = self._get_count_with(conn, "cities")
                logger.info(f"Global database: {total:,} cities")
                conn.close()
            except sqlite3.Error as e:
                self._global_db_valid = False
                logger.error(f"Global database connection error: {e}")

        if not self.hungarian_db_path.exists():
            self._hungarian_db_valid = False
            logger.warning(f"Hungarian settlements database not found: {self.hungarian_db_path}")
            logger.warning("   Run: python scripts/hungarian_settlements_importer.py")
        else:
            try:
                conn = sqlite3.connect(self.hungarian_db_path)
                conn.row_factory = sqlite3.Row
                self._validate_hungarian_database_structure_with(conn)
                total = self._get_count_with(conn, "hungarian_settlements")
                logger.info(f"Hungarian settlements database: {total:,} settlements")
                conn.close()
            except sqlite3.Error as e:
                self._hungarian_db_valid = False
                logger.error(f"Hungarian database connection error: {e}")

        if self.connection is None and self.hungarian_connection is None:
            raise CityDatabaseError("No database available!")

    def _validate_database_structure(self) -> None:
        """Validate global database table structure (uses thread-local connection)."""
        conn = self.connection
        if not conn:
            return
        self._validate_database_structure_with(conn)

    def _validate_hungarian_database_structure(self) -> None:
        """Validate Hungarian settlements database structure (uses thread-local connection)."""
        conn = self.hungarian_connection
        if not conn:
            return
        self._validate_hungarian_database_structure_with(conn)

    def _validate_database_structure_with(self, conn: sqlite3.Connection) -> None:
        """Validate global database table structure."""
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(cities)")
        columns = [row[1] for row in cursor.fetchall()]

        required_columns = [
            "id",
            "city",
            "lat",
            "lon",
            "country",
            "country_code",
            "population",
            "continent",
            "admin_name",
            "capital",
            "timezone",
        ]

        missing_columns = [col for col in required_columns if col not in columns]
        if missing_columns:
            raise CityDatabaseError(f"Missing columns in cities table: {missing_columns}")

        logger.debug("Global database structure validated")

    def _validate_hungarian_database_structure_with(self, conn: sqlite3.Connection) -> None:
        """Validate Hungarian settlements database structure."""
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(hungarian_settlements)")
        columns = [row[1] for row in cursor.fetchall()]

        required_columns = [
            "id",
            "name",
            "latitude",
            "longitude",
            "megye",
            "settlement_type",
            "population",
            "climate_zone",
            "region_priority",
        ]

        missing_columns = [col for col in required_columns if col not in columns]
        if missing_columns:
            raise CityDatabaseError(
                f"Missing columns in hungarian_settlements table: {missing_columns}"
            )

        logger.debug("Hungarian database structure validated")

    def _get_total_city_count(self) -> int:
        """Get total global city count (thread-local connection)."""
        conn = self.connection
        if not conn:
            return 0
        return self._get_count_with(conn, "cities")

    def _get_total_hungarian_settlements_count(self) -> int:
        """Get total Hungarian settlement count (thread-local connection)."""
        conn = self.hungarian_connection
        if not conn:
            return 0
        return self._get_count_with(conn, "hungarian_settlements")

    _VALID_TABLES = frozenset({"cities", "hungarian_settlements"})

    @staticmethod
    def _get_count_with(conn: sqlite3.Connection, table: str) -> int:
        if table not in CityManagerDB._VALID_TABLES:
            raise ValueError(f"Invalid table name: {table}")
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table}")  # nosec B608
        return cursor.fetchone()[0]

    def _execute_query(
        self, sql: str, params: tuple = (), use_hungarian: bool = False
    ) -> list[sqlite3.Row]:
        """Execute SQL query on appropriate database (thread-local connection)."""
        connection = self.hungarian_connection if use_hungarian else self.connection

        if not connection:
            db_type = "Hungarian" if use_hungarian else "Global"
            raise CityDatabaseError(f"{db_type} database connection not available")

        try:
            cursor = connection.cursor()
            cursor.execute(sql, params)
            results = cursor.fetchall()

            if use_hungarian:
                self.hungarian_query_count += 1
            else:
                self.query_count += 1
            self.last_query_time = datetime.now()

            logger.debug(
                f"SQL query executed ({'Hungarian' if use_hungarian else 'Global'}): {len(results)} results"
            )
            return results

        except sqlite3.Error as e:
            logger.error(f"SQL query error (table query) | Error: {e}")
            raise CityDatabaseError(f"Query execution error: {e}")  # noqa: B904

    def close(self) -> None:
        """Close thread-local database connections and prevent reconnection."""
        self._closed = True

        if hasattr(self._local, "connection") and self._local.connection:
            self._local.connection.close()
            self._local.connection = None

        if hasattr(self._local, "hungarian_connection") and self._local.hungarian_connection:
            self._local.hungarian_connection.close()
            self._local.hungarian_connection = None

        logger.info("Thread-local database connections closed")


__all__ = ["CityManagerDB"]
