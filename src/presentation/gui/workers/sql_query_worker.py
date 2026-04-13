#!/usr/bin/env python3
# mypy: ignore-errors

"""
SQL Query Worker - SQLite query worker

Adatbázis lekérdezéseket végző worker thread SQL injection
védelemmel és cancellation support-tal.
"""

import sqlite3
from pathlib import Path
from typing import Any, Optional

from PySide6.QtCore import QObject, Signal

from .base_worker import BaseWorkerThread


def _is_cancelled(worker: "SQLQueryWorker") -> bool:
    """Return whether the worker has been cancelled."""
    return worker.isInterruptionRequested() or worker.is_cancelled


def _contains_dangerous_sql(query: str) -> str | None:
    """Return the first dangerous SQL keyword if present."""
    dangerous_keywords = ["DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "CREATE"]
    query_upper = query.upper()
    for keyword in dangerous_keywords:
        if keyword in query_upper:
            return keyword
    return None


def _execute_query(query: str, conn: sqlite3.Connection) -> Any:
    """Execute a SQL query using pandas when available."""
    try:
        import pandas as pd  # noqa: PLC0415

        return pd.read_sql_query(query, conn)
    except ImportError:
        cursor = conn.cursor()
        cursor.execute(query)
        if query.upper().startswith("SELECT"):
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return {"columns": columns, "rows": rows}
        return {"affected_rows": cursor.rowcount}


def _open_database(worker: "SQLQueryWorker") -> sqlite3.Connection | None:
    """Open the SQLite database unless cancellation was requested."""
    worker.emit_status("🗄️ Adatbázis kapcsolat...")
    worker.progress_updated.emit(20)
    if _is_cancelled(worker):
        print("🛑 DEBUG: SQL query cancelled before DB connection")
        return None
    conn = sqlite3.connect(str(worker.db_path))
    if worker.is_cancelled:
        conn.close()
        return None
    worker.progress_updated.emit(50)
    return conn


def _validate_query_safety(worker: "SQLQueryWorker", conn: sqlite3.Connection) -> bool:
    """Validate SQL safety before execution."""
    dangerous_keyword = _contains_dangerous_sql(worker.query)
    if dangerous_keyword is None:
        return True
    conn.close()
    worker.emit_error(f"Tiltott SQL kulcsszó: {dangerous_keyword}")
    return False


def _execute_worker_query(worker: "SQLQueryWorker", conn: sqlite3.Connection) -> bool:
    """Execute the worker query unless cancelled."""
    worker.emit_status("📊 SQL lekérdezés végrehajtása...")
    worker.progress_updated.emit(70)
    if _is_cancelled(worker):
        print("🛑 DEBUG: SQL query cancelled before execution")
        conn.close()
        return False
    worker.result = _execute_query(worker.query, conn)
    conn.close()
    worker.progress_updated.emit(100)
    return True


def _run_sql_query(worker: "SQLQueryWorker") -> None:
    """Run the SQL query workflow."""
    conn = _open_database(worker)
    if conn is None:
        return
    if not _validate_query_safety(worker, conn):
        return
    if not _execute_worker_query(worker, conn):
        return
    if worker.result is not None and not worker.is_cancelled:
        worker.query_completed.emit(worker.result)
        worker.emit_status("✅ SQL lekérdezés befejezve")


class SQLQueryWorker(BaseWorkerThread):
    """
    🔧 FIX: SQL lekérdezéseket végző worker thread cancellation support-tal.

    FUNKCIÓK:
    ✅ SQLite adatbázis safe querying
    ✅ SQL injection védelem
    ✅ Pandas integration
    ✅ Cancellation support
    """

    # Specifikus signalok
    query_completed = Signal(object)  # pandas DataFrame vagy list

    def __init__(  # noqa: D107
        self, query: str, db_path: str | Path, parent: Optional["QObject"] = None
    ):
        super().__init__(parent)
        self.query = query.strip()
        self.db_path = Path(db_path)
        self.result: Any | None = None

    def execute(self) -> None:
        """
        🔧 FIX: SQL lekérdezés végrehajtása cancellation support-tal.
        """
        if not self.query:
            self.emit_error("Üres SQL lekérdezés")
            return

        if not self.db_path.exists():
            self.emit_error(f"Adatbázis fájl nem található: {self.db_path}")
            return

        try:
            _run_sql_query(self)

        except sqlite3.Error as e:
            if not self.is_cancelled:
                self.emit_error(f"SQL hiba: {e!s}")
        except Exception as e:
            if not self.is_cancelled:
                self.emit_error(f"Váratlan hiba az SQL lekérdezés során: {e!s}")
