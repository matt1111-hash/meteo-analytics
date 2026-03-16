#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mypy: ignore-errors

"""
Windows Module - Főablak komponensek.

Modul struktúra:
- main_window.py: Fő ablak osztály
- main_window_state.py: Állapotkezelés
- main_window_actions.py: Akciókezelők
- menu_builder.py: Menüsor építő
- toolbar_manager.py: Eszköztár kezelő
- window_layout.py: Layout és nézetek

FÁJL: src/presentation/gui/windows/__init__.py
"""

from .main_window import MainWindow

# Re-export main class
__all__ = ["MainWindow"]
