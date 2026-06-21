"""Tests for SQL LIKE metacharacter escaping (FIX-03).

Verifies that ``%`` and ``_`` in user-supplied search terms are treated as
literals, not wildcards. Without escaping, a search for ``%`` would match every
row and ``_`` would match any single character.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest
from src.infrastructure.city_manager.city_manager_search import CityManagerSearch
from src.infrastructure.db.like_utils import escape_like
from src.infrastructure.repositories.city_repository_queries import (
    CityRepositoryQueries,
)


@pytest.fixture
def like_db(tmp_path: Path) -> Path:
    """cities.db seeded with names containing LIKE metacharacters."""
    db_path = tmp_path / "cities.db"
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
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
            timezone TEXT,
            meteostat_station_id TEXT,
            data_quality_score REAL
        )
        """
    )
    conn.executemany(
        "INSERT INTO cities VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [
            (1, "100%Pure", 1.0, 2.0, "Land", "XX", 100, "X", "R", 0, "t", None, None),
            (2, "A_B", 3.0, 4.0, "Land", "XX", 200, "X", "R", 0, "t", None, None),
            (3, "Plain", 5.0, 6.0, "Land", "XX", 300, "X", "R", 0, "t", None, None),
        ],
    )
    conn.commit()
    conn.close()
    return db_path


@pytest.fixture
def like_hungarian_db(tmp_path: Path) -> Path:
    """hungarian_settlements.db seeded with names containing LIKE metacharacters."""
    db_path = tmp_path / "hungarian_settlements.db"
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
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
        """
    )
    conn.executemany(
        "INSERT INTO hungarian_settlements VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [
            (1, "100%Pure", 1.0, 2.0, "M", "város", 100, "c", 1.0, None, None, None),
            (2, "A_B", 3.0, 4.0, "M", "város", 200, "c", 1.0, None, None, None),
            (3, "Plain", 5.0, 6.0, "M", "város", 300, "c", 1.0, None, None, None),
        ],
    )
    conn.commit()
    conn.close()
    return db_path


class TestEscapeLikeHelper:
    """Unit tests for the escape_like helper itself."""

    def test_escapes_percent(self) -> None:
        assert escape_like("100%") == "100\\%"

    def test_escapes_underscore(self) -> None:
        assert escape_like("a_b") == "a\\_b"

    def test_escapes_backslash_first(self) -> None:
        # Backslash must be escaped first so it cannot neutralize %/_ escaping.
        assert escape_like("a\\%b") == "a\\\\\\%b"

    def test_plain_string_unchanged(self) -> None:
        assert escape_like("Budapest") == "Budapest"


class TestSearchCitiesLikeEscape:
    """search_cities must treat metacharacters as literals."""

    def test_percent_treated_as_literal(self, like_db: Path, like_hungarian_db: Path) -> None:
        manager = CityManagerSearch(db_path=like_db, hungarian_db_path=like_hungarian_db)

        results = manager.search_cities("100%Pure")

        city_names = [c.city for c in results]
        assert "100%Pure" in city_names
        # Without escaping, "%" matches everything → Plain would also appear.
        assert "Plain" not in city_names

    def test_underscore_treated_as_literal(self, like_db: Path, like_hungarian_db: Path) -> None:
        manager = CityManagerSearch(db_path=like_db, hungarian_db_path=like_hungarian_db)

        results = manager.search_cities("A_B")

        city_names = [c.city for c in results]
        assert "A_B" in city_names
        # Without escaping, "_" matches any single char → would over-match.
        assert "Plain" not in city_names


class TestSearchHungarianLikeEscape:
    """search_hungarian_settlements must treat metacharacters as literals."""

    def test_percent_treated_as_literal(self, like_db: Path, like_hungarian_db: Path) -> None:
        manager = CityManagerSearch(db_path=like_db, hungarian_db_path=like_hungarian_db)

        results = manager.search_hungarian_settlements("100%Pure")

        names = [c.city for c in results]
        assert "100%Pure" in names
        assert "Plain" not in names

    def test_underscore_treated_as_literal(self, like_db: Path, like_hungarian_db: Path) -> None:
        manager = CityManagerSearch(db_path=like_db, hungarian_db_path=like_hungarian_db)

        results = manager.search_hungarian_settlements("A_B")

        names = [c.city for c in results]
        assert "A_B" in names
        assert "Plain" not in names


class TestAutocompleteLikeEscape:
    """autocomplete_city_name must treat metacharacters as literals."""

    def test_percent_treated_as_literal(self, like_db: Path, like_hungarian_db: Path) -> None:
        queries = CityRepositoryQueries(db_path=like_db, hungarian_db_path=like_hungarian_db)

        results = queries.autocomplete_city_name("100%P", limit=10)

        city_names = [r["city"] for r in results]
        assert "100%Pure" in city_names
        assert "Plain" not in city_names
