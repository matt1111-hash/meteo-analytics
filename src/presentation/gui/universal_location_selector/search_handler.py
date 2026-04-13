# ruff: noqa: F403,noqa: I001
# mypy: ignore-errors
"""Compatibility wrapper for search_handler.py."""

from __future__ import annotations

from .search_handler_part1 import SearchHandlerPart1Mixin
from .search_handler_part2 import SearchHandlerPart2Mixin
from .search_handler_support import *


class SearchHandler(SearchHandlerPart1Mixin, SearchHandlerPart2Mixin):
    """
    Keresési logika kezelése.

    Felelősség:
    - Keresés indítása és időzítés
    - Eredmények megjelenítése
    - Magyar és globális eredmények formázása
    """
