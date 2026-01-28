#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SQL Query Worker - SQLite query worker

Adatbázis lekérdezéseket végző worker thread SQL injection
védelemmel és cancellation support-tal.
"""

import sqlite3
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

from PySide6.QtCore import Signal
from .base_worker import BaseWorkerThread


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

    def __init__(self, query: str, db_path: Union[str, Path],
                 parent: Optional['QObject'] = None):
        super().__init__(parent)
        self.query = query.strip()
        self.db_path = Path(db_path)
        self.result: Optional[Any] = None

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
            self.emit_status("🗄️ Adatbázis kapcsolat...")
            self.progress_updated.emit(20)

            # 🚨 FIX: Cancellation check
            if self.isInterruptionRequested() or self.is_cancelled:
                print("🛑 DEBUG: SQL query cancelled before DB connection")
                return

            # Adatbázis kapcsolat
            conn = sqlite3.connect(str(self.db_path))

            if self.is_cancelled:
                conn.close()
                return

            self.progress_updated.emit(50)

            # Biztonsági ellenőrzés (SQL injection védelem)
            dangerous_keywords = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'CREATE']
            query_upper = self.query.upper()

            for keyword in dangerous_keywords:
                if keyword in query_upper:
                    conn.close()
                    self.emit_error(f"Tiltott SQL kulcsszó: {keyword}")
                    return

            self.emit_status("📊 SQL lekérdezés végrehajtása...")
            self.progress_updated.emit(70)

            # 🚨 FIX: Cancellation check before query execution
            if self.isInterruptionRequested() or self.is_cancelled:
                print("🛑 DEBUG: SQL query cancelled before execution")
                conn.close()
                return

            # Pandas használata a jobb adatkezeléshez
            try:
                import pandas as pd
                result = pd.read_sql_query(self.query, conn)
                self.result = result
            except ImportError:
                # Fallback pandas nélkül
                cursor = conn.cursor()
                cursor.execute(self.query)

                if self.query.upper().startswith('SELECT'):
                    rows = cursor.fetchall()
                    columns = [description[0] for description in cursor.description]
                    self.result = {"columns": columns, "rows": rows}
                else:
                    self.result = {"affected_rows": cursor.rowcount}

            conn.close()

            self.progress_updated.emit(100)

            # Eredmény kibocsátása (ha nem cancelled)
            if self.result is not None and not self.is_cancelled:
                self.query_completed.emit(self.result)
                self.emit_status("✅ SQL lekérdezés befejezve")

        except sqlite3.Error as e:
            if not self.is_cancelled:
                self.emit_error(f"SQL hiba: {str(e)}")
        except Exception as e:
            if not self.is_cancelled:
                self.emit_error(f"Váratlan hiba az SQL lekérdezés során: {str(e)}")
