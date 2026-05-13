#!/usr/bin/env python3

"""Tests for SQLite thread-safety — thread-local connections."""

from __future__ import annotations

import sqlite3
import threading
from pathlib import Path
from typing import Any

import pytest
from src.infrastructure.city_manager.city_manager_db import CityManagerDB


def _create_valid_db(path: Path) -> None:
    conn = sqlite3.connect(path)
    conn.execute("""
        CREATE TABLE cities (
            id INTEGER, city TEXT, lat REAL, lon REAL, country TEXT,
            country_code TEXT, population INTEGER, continent TEXT,
            admin_name TEXT, capital INTEGER, timezone TEXT
        )
    """)
    conn.execute(
        "INSERT INTO cities VALUES (1,'TestCity',47.0,19.0,'HU','HU',1000000,'Europe','Pest',1,'Europe/Budapest')"
    )
    conn.commit()
    conn.close()


def _create_valid_hungarian_db(path: Path) -> None:
    conn = sqlite3.connect(path)
    conn.execute("""
        CREATE TABLE hungarian_settlements (
            id INTEGER, name TEXT, latitude REAL, longitude REAL,
            megye TEXT, settlement_type TEXT, population INTEGER,
            climate_zone TEXT, region_priority REAL
        )
    """)
    conn.execute(
        "INSERT INTO hungarian_settlements VALUES (1,'Budapest',47.5,19.04,'Pest','főváros',1750000,'continental',1.0)"
    )
    conn.commit()
    conn.close()


@pytest.fixture()
def _dbs(tmp_path: Path) -> tuple[Path, Path]:
    cities_db = tmp_path / "cities.db"
    hungarian_db = tmp_path / "hungarian_settlements.db"
    _create_valid_db(cities_db)
    _create_valid_hungarian_db(hungarian_db)
    return cities_db, hungarian_db


class TestThreadLocalConnections:
    """Each thread gets its own SQLite connection."""

    def test_concurrent_queries_use_separate_connections(self, tmp_path: Path) -> None:
        cities_db = tmp_path / "cities.db"
        _create_valid_db(cities_db)
        manager = CityManagerDB(db_path=cities_db)

        conn_ids: dict[str, int] = {}
        errors: list[str] = []

        def query(thread_name: str) -> None:
            try:
                conn = manager.connection
                if conn is None:
                    errors.append(f"{thread_name}: no connection")
                    return
                conn_ids[thread_name] = id(conn)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM cities")
                cursor.fetchone()
            except Exception as e:
                errors.append(f"{thread_name}: {e}")

        threads = [threading.Thread(target=query, args=(f"t{i}",)) for i in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors, f"Errors: {errors}"
        assert len(conn_ids) == 4, "Each thread should have its own connection"
        unique_ids = set(conn_ids.values())
        assert len(unique_ids) == 4, f"Connections must be distinct, got: {conn_ids}"

    def test_concurrent_execute_query_no_errors(self, tmp_path: Path) -> None:
        cities_db = tmp_path / "cities.db"
        _create_valid_db(cities_db)
        manager = CityManagerDB(db_path=cities_db)

        errors: list[str] = []

        def query(thread_name: str) -> None:
            try:
                results = manager._execute_query("SELECT * FROM cities")
                if not results:
                    errors.append(f"{thread_name}: empty results")
            except Exception as e:
                errors.append(f"{thread_name}: {e}")

        threads = [threading.Thread(target=query, args=(f"t{i}",)) for i in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors, f"Errors: {errors}"

    def test_close_prevents_reconnection(self, tmp_path: Path) -> None:
        cities_db = tmp_path / "cities.db"
        _create_valid_db(cities_db)
        manager = CityManagerDB(db_path=cities_db)

        assert manager.connection is not None
        manager.close()
        assert manager.connection is None

    def test_close_flag_affects_all_threads(self, tmp_path: Path) -> None:
        cities_db = tmp_path / "cities.db"
        _create_valid_db(cities_db)
        manager = CityManagerDB(db_path=cities_db)

        manager.close()

        results: dict[str, Any] = {}
        errors: list[str] = []

        def check(thread_name: str) -> None:
            try:
                results[thread_name] = manager.connection is None
            except Exception as e:
                errors.append(f"{thread_name}: {e}")

        threads = [threading.Thread(target=check, args=(f"t{i}",)) for i in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors, f"Errors: {errors}"
        assert all(results.values()), f"All threads should see None: {results}"
