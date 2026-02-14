#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
City Manager - Database Connection and Initialization
Global Weather Analyzer project

Part of the city_manager refactoring - split into focused modules.
"""

import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

from src.config import DATA_DIR

from .city_types import CityDatabaseError

logger = logging.getLogger(__name__)


class CityManagerDB:
    """
    Database connection and initialization for CityManager.

    Handles dual database setup:
    - Global cities from cities.db (44k cities)
    - Hungarian settlements from hungarian_settlements.db (3200+ settlements)
    """

    def __init__(
        self, db_path: Optional[Path] = None, hungarian_db_path: Optional[Path] = None
    ):
        """Initialize database connections."""
        self.db_path = db_path or (DATA_DIR / "cities.db")
        self.hungarian_db_path = hungarian_db_path or (
            DATA_DIR / "hungarian_settlements.db"
        )

        self.connection: Optional[sqlite3.Connection] = None
        self.hungarian_connection: Optional[sqlite3.Connection] = None

        self.query_count = 0
        self.hungarian_query_count = 0
        self.last_query_time: Optional[datetime] = None

        logger.info("Dual Database initialization:")
        logger.info(f"   Global cities: {self.db_path}")
        logger.info(f"   Hungarian settlements: {self.hungarian_db_path}")

        self._initialize_databases()

    def _initialize_databases(self) -> None:
        """Initialize and validate dual databases."""

        if not self.db_path.exists():
            logger.warning(f"Global cities.db not found: {self.db_path}")
            logger.warning("   Only Hungarian settlements will be available!")
        else:
            try:
                self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
                self.connection.row_factory = sqlite3.Row
                self._validate_database_structure()

                total_global = self._get_total_city_count()
                logger.info(f"Global database: {total_global:,} cities")

            except sqlite3.Error as e:
                logger.error(f"Global database connection error: {e}")
                self.connection = None

        if not self.hungarian_db_path.exists():
            logger.warning(
                f"Hungarian settlements database not found: {self.hungarian_db_path}"
            )
            logger.warning("   Run: python scripts/hungarian_settlements_importer.py")
        else:
            try:
                self.hungarian_connection = sqlite3.connect(
                    self.hungarian_db_path, check_same_thread=False
                )
                self.hungarian_connection.row_factory = sqlite3.Row
                self._validate_hungarian_database_structure()

                total_hungarian = self._get_total_hungarian_settlements_count()
                logger.info(
                    f"Hungarian settlements database: {total_hungarian:,} settlements"
                )

            except sqlite3.Error as e:
                logger.error(f"Hungarian database connection error: {e}")
                self.hungarian_connection = None

        if not self.connection and not self.hungarian_connection:
            raise CityDatabaseError("No database available!")

    def _validate_database_structure(self) -> None:
        """Validate global database table structure."""
        if not self.connection:
            return

        cursor = self.connection.cursor()
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
            raise CityDatabaseError(
                f"Missing columns in cities table: {missing_columns}"
            )

        logger.debug("Global database structure validated")

    def _validate_hungarian_database_structure(self) -> None:
        """Validate Hungarian settlements database structure."""
        if not self.hungarian_connection:
            return

        cursor = self.hungarian_connection.cursor()
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
        """Get total global city count."""
        if not self.connection:
            return 0
        cursor = self.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM cities")
        return cursor.fetchone()[0]

    def _get_total_hungarian_settlements_count(self) -> int:
        """Get total Hungarian settlement count."""
        if not self.hungarian_connection:
            return 0
        cursor = self.hungarian_connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM hungarian_settlements")
        return cursor.fetchone()[0]

    def _execute_query(
        self, sql: str, params: Tuple = (), use_hungarian: bool = False
    ) -> List[sqlite3.Row]:
        """Execute SQL query on appropriate database."""
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
            logger.error(f"SQL query error: {sql} | Error: {e}")
            raise CityDatabaseError(f"Query execution error: {e}")

    def close(self) -> None:
        """Close dual database connections."""
        if self.connection:
            self.connection.close()
            self.connection = None

        if self.hungarian_connection:
            self.hungarian_connection.close()
            self.hungarian_connection = None

        logger.info("Dual database connections closed")


__all__ = ["CityManagerDB"]
