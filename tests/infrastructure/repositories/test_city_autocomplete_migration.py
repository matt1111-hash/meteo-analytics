"""Regression tests for generated autocomplete columns and repeatable migrations."""

from __future__ import annotations

import sqlite3
from collections.abc import Callable
from pathlib import Path

import pytest
from scripts.add_city_name_index import migrate_cities_db, migrate_hungarian_db
from src.infrastructure.repositories.city_repository_queries import CityRepositoryQueries


@pytest.fixture
def city_databases(tmp_path: Path) -> tuple[Path, Path]:
    """Build both legacy schemas, including prefix, infix and literal wildcard names."""
    cities = tmp_path / "cities.db"
    hungarian = tmp_path / "hungarian.db"
    with sqlite3.connect(cities) as conn:
        conn.executescript(
            "CREATE TABLE cities (city TEXT, country TEXT, country_code TEXT, "
            "lat REAL, lon REAL, population INTEGER, meteostat_station_id TEXT, "
            "data_quality_score REAL);"
        )
        conn.executemany(
            "INSERT INTO cities (city, population) VALUES (?, ?)",
            [("Budapest", 100), ("New Budapest", 90), ("Bu_da", 80), ("Bu%da", 70)],
        )
    with sqlite3.connect(hungarian) as conn:
        conn.executescript(
            "CREATE TABLE hungarian_settlements (name TEXT, latitude REAL, "
            "longitude REAL, population INTEGER);"
        )
        conn.executemany(
            "INSERT INTO hungarian_settlements (name, population) VALUES (?, ?)",
            [("Budakeszi", 60), ("New Budakeszi", 50), ("Bu_dakeszi", 40), ("Bu%dakeszi", 30)],
        )
    return cities, hungarian


@pytest.mark.parametrize(
    ("db_index", "migrate", "table", "column", "index"),
    [
        (0, migrate_cities_db, "cities", "city_lower", "idx_city_lower"),
        (1, migrate_hungarian_db, "hungarian_settlements", "name_lower", "idx_name_lower"),
    ],
)
def test_migration_is_repeatable_and_preserves_rows(
    city_databases: tuple[Path, Path],
    db_index: int,
    migrate: Callable[[Path], None],
    table: str,
    column: str,
    index: str,
) -> None:
    path = city_databases[db_index]
    assert not CityRepositoryQueries._has_column(path, table, column)

    migrate(path)
    with sqlite3.connect(path) as conn:
        first_dump = list(conn.iterdump())
    migrate(path)

    assert CityRepositoryQueries._has_column(path, table, column)
    with sqlite3.connect(path) as conn:
        assert list(conn.iterdump()) == first_dump
        assert conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'index' AND name = ?", (index,)
        ).fetchone() == (1,)
        assert conn.execute(
            "SELECT hidden FROM pragma_table_xinfo(?) WHERE name = ?", (table, column)
        ).fetchone() == (2,)


@pytest.mark.parametrize("migrated", [False, True])
def test_autocomplete_switches_from_legacy_contains_to_generated_prefix(
    city_databases: tuple[Path, Path], migrated: bool
) -> None:
    cities, hungarian = city_databases
    if migrated:
        migrate_cities_db(cities)
        migrate_hungarian_db(hungarian)
    queries = CityRepositoryQueries(cities, hungarian)

    results = queries.autocomplete_city_name("  BUD  ")

    expected = ["Budapest", "Budakeszi"]
    if not migrated:
        expected = ["Budapest", "New Budapest", "Budakeszi", "New Budakeszi"]
    assert [row["city"] for row in results] == expected


@pytest.mark.parametrize(
    ("query", "expected"),
    [("Bu_", ["Bu_da", "Bu_dakeszi"]), ("Bu%", ["Bu%da", "Bu%dakeszi"])],
)
def test_migrated_autocomplete_keeps_wildcards_literal(
    city_databases: tuple[Path, Path], query: str, expected: list[str]
) -> None:
    cities, hungarian = city_databases
    migrate_cities_db(cities)
    migrate_hungarian_db(hungarian)

    results = CityRepositoryQueries(cities, hungarian).autocomplete_city_name(query)

    assert [row["city"] for row in results] == expected


@pytest.mark.parametrize("migrate", [migrate_cities_db, migrate_hungarian_db])
def test_migration_does_not_create_missing_database(
    tmp_path: Path, migrate: Callable[[Path], None]
) -> None:
    path = tmp_path / "missing.db"
    migrate(path)
    assert not path.exists()
