#!/usr/bin/env python3
"""Add city_lower/name_lower generated columns and B-tree indexes for autocomplete.

Idempotent — safe to run multiple times. Checks for existing columns before altering.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
CITIES_DB = PROJECT_ROOT / "data" / "cities.db"
HUNGARIAN_DB = PROJECT_ROOT / "data" / "hungarian_settlements.db"


def _column_exists(cursor: sqlite3.Cursor, table: str, column: str) -> bool:
    cursor.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cursor.fetchall())


def _index_exists(cursor: sqlite3.Cursor, index_name: str) -> bool:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name=?", (index_name,))
    return cursor.fetchone() is not None


def migrate_cities_db(db_path: Path) -> None:
    """Add city_lower column and index to cities table."""
    if not db_path.exists():
        print(f"SKIP: {db_path} not found")
        return

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    if _column_exists(cur, "cities", "city_lower"):
        print(f"  {db_path.name}: city_lower column already exists")
    else:
        cur.execute(
            "ALTER TABLE cities ADD COLUMN city_lower TEXT GENERATED ALWAYS AS (LOWER(city)) VIRTUAL"
        )
        print(f"  {db_path.name}: added city_lower generated column")

    if _index_exists(cur, "idx_city_lower"):
        print(f"  {db_path.name}: idx_city_lower already exists")
    else:
        cur.execute("CREATE INDEX idx_city_lower ON cities (city_lower)")
        print(f"  {db_path.name}: created idx_city_lower B-tree index")

    conn.commit()
    conn.close()


def migrate_hungarian_db(db_path: Path) -> None:
    """Add name_lower column and index to hungarian_settlements table."""
    if not db_path.exists():
        print(f"SKIP: {db_path} not found")
        return

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    if _column_exists(cur, "hungarian_settlements", "name_lower"):
        print(f"  {db_path.name}: name_lower column already exists")
    else:
        cur.execute(
            "ALTER TABLE hungarian_settlements ADD COLUMN name_lower TEXT GENERATED ALWAYS AS (LOWER(name)) VIRTUAL"
        )
        print(f"  {db_path.name}: added name_lower generated column")

    if _index_exists(cur, "idx_name_lower"):
        print(f"  {db_path.name}: idx_name_lower already exists")
    else:
        cur.execute("CREATE INDEX idx_name_lower ON hungarian_settlements (name_lower)")
        print(f"  {db_path.name}: created idx_name_lower B-tree index")

    conn.commit()
    conn.close()


def main() -> None:
    """Run the autocomplete index migration on both databases."""
    print("Adding autocomplete indexes...")
    migrate_cities_db(CITIES_DB)
    migrate_hungarian_db(HUNGARIAN_DB)
    print("Done.")


if __name__ == "__main__":
    main()
