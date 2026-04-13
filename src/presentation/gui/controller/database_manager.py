# ruff: noqa: F403,noqa: I001
# mypy: ignore-errors
"""Compatibility wrapper for database_manager.py."""

from __future__ import annotations

from .database_manager_part1 import DatabaseManagerPart1Mixin
from .database_manager_part2 import DatabaseManagerPart2Mixin
from .database_manager_support import *


class DatabaseManager(DatabaseManagerPart1Mixin, DatabaseManagerPart2Mixin):
    """
    Adatbázis műveletek kezelése.

    Felelőségek:
    - Adatbázis kapcsolat inicializálása
    - Séma frissítések (wind_gusts_max, data_provider oszlopok)
    - Város adatok mentése
    - Időjárási adatok mentése
    """
