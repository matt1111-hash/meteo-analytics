"""Tests for CityManagerHungarian from city_manager_hungarian.py."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from src.data.city_manager_db import CityManagerDB
from src.data.city_manager_hungarian import CityManagerHungarian


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
            "Miskolc",
            48.1035,
            20.7784,
            "Borsod-Abaúj-Zemplén",
            "város",
            157177,
            "continental",
            5.0,
            "Miskolci",
            2360,
            70000,
        ),
        (
            5,
            "Pécs",
            46.0727,
            18.2323,
            "Baranya",
            "város",
            145347,
            "continental",
            5.0,
            "Pécsi",
            1630,
            65000,
        ),
        (
            6,
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
            7,
            "Kiskunfélegyháza",
            46.7156,
            19.9422,
            "Bács-Kiskun",
            "város",
            28817,
            "continental",
            3.0,
            "Kiskunfélegyházi",
            290,
            12000,
        ),
        (
            8,
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
        (
            9,
            "Kiskőrös",
            46.6208,
            19.2797,
            "Bács-Kiskun",
            "város",
            13532,
            "continental",
            2.0,
            "Kiskőrösi",
            150,
            6000,
        ),
        (
            10,
            "Soltvadkert",
            46.4769,
            19.3833,
            "Bács-Kiskun",
            "város",
            7270,
            "continental",
            1.0,
            "Soltvadkerti",
            80,
            3200,
        ),
        (
            11,
            "Akasztó",
            46.5333,
            19.3000,
            "Bács-Kiskun",
            "község",
            1500,
            "continental",
            1.0,
            "Kiskőrösi",
            35,
            650,
        ),
        (
            12,
            "Harkakötör",
            46.4667,
            19.4333,
            "Bács-Kiskun",
            "község",
            800,
            "continental",
            1.0,
            "Kiskunhalasi",
            20,
            350,
        ),
        (
            13,
            "Szeghalom",
            47.0333,
            21.1667,
            "Békés",
            "város",
            9200,
            "continental",
            2.0,
            "Szeghalmi",
            95,
            4000,
        ),
        (
            14,
            "Békéscsaba",
            46.6756,
            21.0875,
            "Békés",
            "város",
            58024,
            "continental",
            3.0,
            "Békéscsabai",
            610,
            26000,
        ),
        (
            15,
            "Gyula",
            46.6500,
            21.2667,
            "Békés",
            "város",
            30000,
            "continental",
            2.0,
            "Gyulai",
            255,
            13500,
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
