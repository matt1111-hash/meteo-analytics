"""Tests for the SQLite-backed CityRepository."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest
from src.infrastructure.repositories.city_repository import CityRepository

__all__ = [
    "CityRepository",
    "build_repository",
    "create_cities_db",
    "create_hungarian_settlements_db",
    "pytest",
]


def create_cities_db(path: Path, rows: list[dict[str, object]]) -> None:
    """Create a minimal cities database with the required schema."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE cities (
                city TEXT,
                country TEXT,
                country_code TEXT,
                lat REAL,
                lon REAL,
                population INTEGER,
                meteostat_station_id TEXT,
                data_quality_score REAL,
                city_lower TEXT GENERATED ALWAYS AS (LOWER(city)) VIRTUAL
            )
            """
        )
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_city_lower ON cities (city_lower)")
        for row in rows:
            cursor.execute(
                """
                INSERT INTO cities (
                    city, country, country_code, lat, lon, population,
                    meteostat_station_id, data_quality_score
                ) VALUES (
                    :city, :country, :country_code, :lat, :lon, :population,
                    :meteostat_station_id, :data_quality_score
                )
                """,
                {
                    "city": row["city"],
                    "country": row["country"],
                    "country_code": row["country_code"],
                    "lat": row["lat"],
                    "lon": row["lon"],
                    "population": row.get("population"),
                    "meteostat_station_id": row.get("meteostat_station_id"),
                    "data_quality_score": row.get("data_quality_score"),
                },
            )
        conn.commit()


def create_hungarian_settlements_db(path: Path, rows: list[dict[str, object]]) -> None:
    """Create a minimal hungarian_settlements database with the required schema."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE hungarian_settlements (
                name TEXT,
                megye TEXT,
                latitude REAL,
                longitude REAL,
                population INTEGER,
                region_priority REAL,
                name_lower TEXT GENERATED ALWAYS AS (LOWER(name)) VIRTUAL
            )
            """
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_name_lower ON hungarian_settlements (name_lower)"
        )
        for row in rows:
            cursor.execute(
                """
                INSERT INTO hungarian_settlements (
                    name, megye, latitude, longitude, population, region_priority
                ) VALUES (
                    :name, :megye, :latitude, :longitude, :population, :region_priority
                )
                """,
                {
                    "name": row["name"],
                    "megye": row["megye"],
                    "latitude": row["latitude"],
                    "longitude": row["longitude"],
                    "population": row.get("population"),
                    "region_priority": row.get("region_priority"),
                },
            )
        conn.commit()


def build_repository(db_path: Path, hungarian_db_path: Path) -> CityRepository:
    """Instantiate repository with explicit database paths."""
    repository = CityRepository(db_path=db_path, hungarian_db_path=hungarian_db_path)
    repository.db_path = db_path
    repository.hungarian_db_path = hungarian_db_path
    return repository
