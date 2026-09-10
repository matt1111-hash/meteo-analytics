"""SA-1 C: FOREIGN KEY enforcement a DatabaseManager kapcsolatain.

A séma deklarálja a `weather_data.city_id -> cities.id` FK-t, de a
`PRAGMA foreign_keys` kapcsolatonként alapból KI van kapcsolva — eddig ez
tette lehetővé az árva sorok csendes keletkezését (L-01 / SA-1). Ezek a
tesztek rögzítik, hogy minden DatabaseManager-kapcsolat enforcementtel nyílik,
az árva beszúrás DB-szinten blokkolva van, és a normál mentési út (upsert +
INSERT OR REPLACE) az enforcement mellett is működik.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest
from src.presentation.gui.controller.database_manager import DatabaseManager

SCHEMA_SQL = """
CREATE TABLE cities (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE,
    latitude REAL,
    longitude REAL,
    country TEXT,
    region TEXT,
    created_at TEXT
);
CREATE TABLE weather_data (
    id INTEGER PRIMARY KEY,
    city_id INTEGER REFERENCES cities (id),
    date TEXT,
    temp_max REAL,
    temp_min REAL,
    precipitation REAL,
    windspeed_max REAL,
    UNIQUE (city_id, date)
);
"""


@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    """Üres, valódi FK-t deklaráló sémájú SQLite fájl."""
    path = tmp_path / "meteo_test.db"
    con = sqlite3.connect(path)
    con.executescript(SCHEMA_SQL)
    con.commit()
    con.close()
    return path


@pytest.fixture
def manager(db_path: Path) -> DatabaseManager:
    return DatabaseManager(db_path)


def _city_data(latitude: float = 47.4978, longitude: float = 19.0402) -> dict[str, object]:
    return {
        "name": "Budapest",
        "latitude": latitude,
        "longitude": longitude,
        "metadata": {"country": "Hungary", "admin1": "Budapest"},
    }


def _weather_payload() -> dict[str, object]:
    return {
        "daily": {
            "time": ["2026-09-09", "2026-09-10"],
            "temperature_2m_max": [21.5, 23.0],
            "temperature_2m_min": [12.0, 13.5],
            "precipitation_sum": [0.0, 1.2],
        },
        "provider": "open-meteo",
    }


def test_every_connection_enforces_foreign_keys(manager: DatabaseManager) -> None:
    conn = manager.get_connection()
    try:
        assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    finally:
        conn.close()


def test_orphan_weather_insert_is_rejected_by_the_database(
    manager: DatabaseManager,
) -> None:
    conn = manager.get_connection()
    try:
        with pytest.raises(sqlite3.IntegrityError, match="FOREIGN KEY constraint failed"):
            conn.execute("INSERT INTO weather_data (city_id, date) VALUES (999, '2026-01-01')")
    finally:
        conn.close()


def test_save_city_then_weather_happy_path_under_fk(manager: DatabaseManager) -> None:
    manager.save_city_to_database(_city_data())  # type: ignore[arg-type]

    city = _city_data()
    result = manager.save_weather_to_database(
        _weather_payload(),  # type: ignore[arg-type]
        {"name": city["name"], "latitude": city["latitude"], "longitude": city["longitude"]},
    )

    assert result is True
    conn = manager.get_connection()
    try:
        rows = conn.execute(
            "SELECT w.city_id, c.name FROM weather_data w JOIN cities c ON c.id = w.city_id"
        ).fetchall()
        assert len(rows) == 2
        assert all(name == "Budapest" for _, name in rows)
    finally:
        conn.close()


def test_city_resave_keeps_id_and_history_linked_under_fk(
    manager: DatabaseManager,
) -> None:
    manager.save_city_to_database(_city_data())  # type: ignore[arg-type]
    city = _city_data()
    weather = _weather_payload()

    first = manager.save_weather_to_database(
        weather,  # type: ignore[arg-type]
        {"name": city["name"], "latitude": city["latitude"], "longitude": city["longitude"]},
    )
    # Ujramentes mas koordinataval: az id nem valtozhat (RT-2), az elozmeny
    # marad csatolva — most mar FK-enforcement mellett is.
    manager.save_city_to_database(_city_data(latitude=47.5, longitude=19.05))  # type: ignore[arg-type]
    second = manager.save_weather_to_database(
        weather,  # type: ignore[arg-type]
        {"name": "Budapest", "latitude": 47.5, "longitude": 19.05},
    )

    assert first is True
    assert second is True
    conn = manager.get_connection()
    try:
        (city_id,) = conn.execute("SELECT id FROM cities WHERE name = 'Budapest'").fetchone()
        orphans = conn.execute(
            "SELECT COUNT(*) FROM weather_data WHERE city_id NOT IN (SELECT id FROM cities)"
        ).fetchone()[0]
        assert orphans == 0
        assert (
            conn.execute(
                "SELECT COUNT(*) FROM weather_data WHERE city_id = ?", (city_id,)
            ).fetchone()[0]
            == 2
        )
    finally:
        conn.close()
