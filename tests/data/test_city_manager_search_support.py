"""Tests for CityManagerSearch from city_manager_search.py."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from src.data.city_manager_hungarian import CityManagerHungarian
from src.data.city_manager_search import CityManagerSearch
from src.data.city_types import City


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
        (
            1,
            "Budapest",
            47.4979,
            19.0402,
            "Hungary",
            "HU",
            1752286,
            "Europe",
            "Budapest",
            1,
            "Europe/Budapest",
        ),
        (
            2,
            "London",
            51.5074,
            -0.1278,
            "United Kingdom",
            "GB",
            8982000,
            "Europe",
            "England",
            1,
            "Europe/London",
        ),
        (
            3,
            "New York",
            40.7128,
            -74.0060,
            "United States",
            "US",
            8336817,
            "North America",
            "New York",
            0,
            "America/New_York",
        ),
        (
            4,
            "Paris",
            48.8566,
            2.3522,
            "France",
            "FR",
            2161000,
            "Europe",
            "Île-de-France",
            1,
            "Europe/Paris",
        ),
        (
            5,
            "Berlin",
            52.5200,
            13.4050,
            "Germany",
            "DE",
            3645000,
            "Europe",
            "Berlin",
            1,
            "Europe/Berlin",
        ),
        (
            6,
            "Tokyo",
            35.6762,
            139.6503,
            "Japan",
            "JP",
            13960000,
            "Asia",
            "Tokyo",
            1,
            "Asia/Tokyo",
        ),
        (
            7,
            "Sydney",
            -33.8688,
            151.2093,
            "Australia",
            "AU",
            5312000,
            "Oceania",
            "New South Wales",
            0,
            "Australia/Sydney",
        ),
        (
            8,
            "Debrecen",
            47.5314,
            21.6269,
            "Hungary",
            "HU",
            201881,
            "Europe",
            "Hajdú-Bihar",
            0,
            "Europe/Budapest",
        ),
        (
            9,
            "Vienna",
            48.2082,
            16.3738,
            "Austria",
            "AT",
            1897000,
            "Europe",
            "Vienna",
            1,
            "Europe/Vienna",
        ),
        (
            10,
            "Broxbourne",
            51.7462,
            -0.0115,
            "United Kingdom",
            "GB",
            15000,
            "Europe",
            "England",
            0,
            "Europe/London",
        ),
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
        (
            1,
            "Budapest",
            47.4979,
            19.0402,
            "Budapest",
            "főváros",
            1752286,
            "continental",
            10.0,
            None,
            52500,
            800000,
        ),
        (
            2,
            "Debrecen",
            47.5314,
            21.6269,
            "Hajdú-Bihar",
            "város",
            201881,
            "continental",
            5.0,
            "Debreceni",
            4210,
            85000,
        ),
        (
            3,
            "Szeged",
            46.2530,
            20.1414,
            "Csongrád-Csanád",
            "város",
            161837,
            "continental",
            5.0,
            "Szegedi",
            2810,
            72000,
        ),
        (
            4,
            "Kiskunhalas",
            46.4315,
            19.4867,
            "Bács-Kiskun",
            "város",
            18254,
            "continental",
            3.0,
            "Kiskunhalasi",
            350,
            8000,
        ),
        (
            5,
            "Kecskemét",
            46.8964,
            19.6897,
            "Bács-Kiskun",
            "város",
            110034,
            "continental",
            4.0,
            "Kecskeméti",
            3200,
            48000,
        ),
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
