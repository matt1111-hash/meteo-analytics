#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Results Panel Components - Clean Architecture Refactor

Ez a modul tartalmazza a ResultsPanel komponenseit,
szétbontva funkcionális területek szerint.

Modul struktúra:
- results_panel: Fő panel osztály
- progress_manager: Progress tracking és loading indicator
- tab_manager: Tab management és frissítés
- data_processor: DataFrame konverzió és adatfeldolgozás
"""

from .results_panel import ResultsPanel
from .progress_manager import ProgressManager
from .tab_manager import TabManager
from .data_processor import DataProcessor

__all__ = [
    "ResultsPanel",
    "ProgressManager",
    "TabManager",
    "DataProcessor",
]
