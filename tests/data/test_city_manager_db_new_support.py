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
    conn.execute(
        "INSERT INTO cities VALUES (1, 'Budapest', 47.5, 19.0, 'Hungary', 'HU', 1750000, 'Europe', 'Budapest', 0, 'Europe/Budapest')"
    )
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
    conn.execute(
        "INSERT INTO hungarian_settlements VALUES (1, 'Budapest', 47.5, 19.0, 'Budapest', 'city', 1750000, 'continental', 1.0)"
    )
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
