#!/usr/bin/env python3

"""SA-1 migration tool: orphan `weather_data` rows referencing deleted `cities` ids.

Background (repair plan 20260910T092914Z, RT-2 / L-01 + SA-1):
the GUI used `INSERT OR REPLACE INTO cities`, so every re-save of an existing
name deleted the old row and inserted a new one with a **new id**. Weather rows
written earlier kept pointing at the deleted id, because `PRAGMA foreign_keys`
is off. RT-2 stopped new orphans; this tool only deals with the existing ones.

Measured on the production copy (2026-09-10): 62 957 of 79 824 rows (78.9 %)
across 118 distinct orphan city ids; 4 271 of them carry dates that no living
city has. The schema stores no former-id/alias mapping, so relinking by name is
**not** recoverable from the database alone.

Safety:
  * default mode is a read-only dry run — nothing is written;
  * `--apply` refuses to run without an existing `--backup` file (make a copy of
    the database yourself first: `cp data/meteo_data.db /path/to/backup.db`);
  * deletions happen in a single transaction.

Usage:
    python scripts/sa1_orphan_weather_migration.py --db data/meteo_data.db
    python scripts/sa1_orphan_weather_migration.py --db data/meteo_data.db \
        --export /tmp/orphans.csv
    python scripts/sa1_orphan_weather_migration.py --db data/meteo_data.db \
        --apply --backup /tmp/meteo_data.db.bak
"""

from __future__ import annotations

import argparse
import csv
import sqlite3
import sys
from pathlib import Path
from typing import Any

ORPHAN_PREDICATE = "city_id NOT IN (SELECT id FROM cities)"
EXPORT_COLUMNS = (
    "id",
    "city_id",
    "date",
    "temp_max",
    "temp_min",
    "precipitation",
    "windspeed_max",
    "humidity",
    "pressure",
    "created_at",
    "wind_gusts_max",
    "data_provider",
)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--db", required=True, type=Path, help="SQLite database file")
    parser.add_argument("--export", type=Path, help="write orphan rows to this CSV file")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="delete the orphan rows (requires --backup)",
    )
    parser.add_argument(
        "--backup",
        type=Path,
        help="existing file copy of the database (mandatory with --apply)",
    )
    parser.add_argument(
        "--vacuum",
        action="store_true",
        help="run VACUUM after a successful delete",
    )
    return parser.parse_args(argv)


def _connect(path: Path) -> Any:
    """Open the database read-only."""
    return sqlite3.connect(f"file:{path}?mode=ro", uri=True)


def _summary(con: Any) -> dict[str, Any]:
    """Collect orphan statistics without modifying anything."""
    cur = con.cursor()
    total = cur.execute("SELECT COUNT(*) FROM weather_data").fetchone()[0]
    orphan_rows = cur.execute(
        f"SELECT COUNT(*) FROM weather_data WHERE {ORPHAN_PREDICATE}"
    ).fetchone()[0]
    orphan_ids = cur.execute(
        f"SELECT COUNT(DISTINCT city_id) FROM weather_data WHERE {ORPHAN_PREDICATE}"
    ).fetchone()[0]
    unique_dates = cur.execute(
        "SELECT COUNT(*) FROM weather_data w WHERE w.city_id NOT IN (SELECT id FROM cities) "
        "AND NOT EXISTS (SELECT 1 FROM weather_data x WHERE x.city_id IN (SELECT id FROM cities) "
        "AND x.date = w.date)"
    ).fetchone()[0]
    return {
        "weather_data": total,
        "orphan_rows": orphan_rows,
        "orphan_city_ids": orphan_ids,
        "orphan_unique_dates": unique_dates,
    }


def _export(con: Any, target: Path) -> int:
    """Write the orphan rows to CSV and return the row count."""
    cur = con.cursor()
    rows = cur.execute(
        f"SELECT {', '.join(EXPORT_COLUMNS)} FROM weather_data WHERE {ORPHAN_PREDICATE}"
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(EXPORT_COLUMNS)
        count = 0
        for row in rows:
            writer.writerow(row)
            count += 1
    return count


def _apply(db_path: Path, backup: Path | None, vacuum: bool) -> int:
    """Delete the orphan rows in one transaction; returns the deleted row count."""
    if backup is None or not backup.is_file():
        raise SystemExit("--apply requires an existing --backup file copy of the database")
    if backup.resolve() == db_path.resolve():
        raise SystemExit("--backup must be a different file than --db")

    con = sqlite3.connect(str(db_path))
    try:
        with con:
            cur = con.execute(f"DELETE FROM weather_data WHERE {ORPHAN_PREDICATE}")
            deleted = cur.rowcount
        if vacuum:
            con.execute("VACUUM")
    finally:
        con.close()
    return deleted


def main(argv: list[str] | None = None) -> int:
    """Run the dry run, the optional export and the optional delete."""
    args = _parse_args(argv)
    if not args.db.is_file():
        raise SystemExit(f"database not found: {args.db}")

    con = _connect(args.db)
    try:
        stats = _summary(con)
        for key, value in stats.items():
            print(f"{key}: {value}")
        if args.export:
            print(f"exported_rows: {_export(con, args.export)} -> {args.export}")
    finally:
        con.close()

    if not args.apply:
        print("dry run only — pass --apply --backup <file> to delete the orphan rows")
        return 0

    deleted = _apply(args.db, args.backup, args.vacuum)
    print(f"deleted_rows: {deleted}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
