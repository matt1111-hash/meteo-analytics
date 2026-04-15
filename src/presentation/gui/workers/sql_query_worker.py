#!/usr/bin/env python3
# mypy: ignore-errors

"""
SQL Query Worker - SQLite query worker (read-only, SELECT-only).

Read-only DB connection + strict SELECT-only validation.
"""

import logging
import re
import sqlite3
from pathlib import Path
from typing import Any, Optional

from PySide6.QtCore import QObject, Signal

from .base_worker import BaseWorkerThread

logger = logging.getLogger(__name__)

# Only SELECT statements are allowed — validated via regex before execution.
_SELECT_PATTERN = re.compile(r"^\s*SELECT\s", re.IGNORECASE | re.DOTALL)

# Forbidden patterns that can appear inside a SELECT but change state.
_FORBIDDEN_PATTERNS = re.compile(
    r";\s*(?!$)"  # semicolons followed by more statements
    r"|/\*.*?\*/"  # block comments (obfuscation vector)
    r"|--",  # line comments (obfuscation vector)
    re.IGNORECASE | re.DOTALL,
)


def _is_cancelled(worker: "SQLQueryWorker") -> bool:
    """Return whether the worker has been cancelled."""
    return worker.isInterruptionRequested() or worker.is_cancelled


def _validate_select_only(query: str) -> str | None:
    """Return error message if query is not a safe single SELECT, else None."""
    if not _SELECT_PATTERN.match(query):
        return "Csak SELECT utasítás engedélyezett"
    if _FORBIDDEN_PATTERNS.search(query):
        return "Tiltott karakterlánc az SQL-ben (megjegyzés vagy több utasítás)"
    return None


def _execute_query(query: str, conn: sqlite3.Connection) -> Any:
    """Execute a SELECT query using pandas when available."""
    try:
        import pandas as pd  # noqa: PLC0415

        return pd.read_sql_query(query, conn)
    except ImportError:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        return {"columns": columns, "rows": rows}


def _open_database(worker: "SQLQueryWorker") -> sqlite3.Connection | None:
    """Open the SQLite database in READ-ONLY mode."""
    worker.emit_status("🗄️ Adatbázis kapcsolat (read-only)...")
    worker.progress_updated.emit(20)
    if _is_cancelled(worker):
        return None
    # Open DB in immutable read-only mode via URI
    db_uri = f"file:{worker.db_path}?mode=ro&nolock=1"
    conn = sqlite3.connect(db_uri, uri=True)
    if worker.is_cancelled:
        conn.close()
        return None
    worker.progress_updated.emit(50)
    return conn


def _validate_query_safety(worker: "SQLQueryWorker", conn: sqlite3.Connection) -> bool:
    """Validate SQL is a single SELECT statement."""
    error = _validate_select_only(worker.query)
    if error is None:
        return True
    conn.close()
    worker.emit_error(f"SQL validációs hiba: {error}")
    return False


def _execute_worker_query(worker: "SQLQueryWorker", conn: sqlite3.Connection) -> bool:
    """Execute the worker query unless cancelled."""
    worker.emit_status("📊 SQL lekérdezés végrehajtása...")
    worker.progress_updated.emit(70)
    if _is_cancelled(worker):
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
    SQL query worker thread with read-only SELECT-only enforcement.

    Security:
    - Database opened in read-only mode (immutable URI)
    - Only SELECT statements allowed (regex validated)
    - No comments or multi-statement queries permitted
    """

    query_completed = Signal(object)  # pandas DataFrame vagy list

    def __init__(  # noqa: D107
        self, query: str, db_path: str | Path, parent: Optional["QObject"] = None
    ):
        super().__init__(parent)
        self.query = query.strip()
        self.db_path = Path(db_path)
        self.result: Any | None = None

    def execute(self) -> None:
        """SQL query execution with cancellation support."""
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
