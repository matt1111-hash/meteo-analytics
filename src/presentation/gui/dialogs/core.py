#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Dialogs - Core

🎯 ExtremeWeatherDialog main class

Képességek:
- Main class
- Inicializáció

Fájl: src/presentation/gui/dialogs/core.py
"""

from typing import Any, Dict, Optional

from PySide6.QtWidgets import QDialog, QWidget

from ..theme_manager import get_theme_manager
from .calculation import _calculate_extremes
from .event_handlers import _on_period_type_changed
from .theme_handler import _register_widgets_for_theming
from .ui_builder import (
    _create_close_button,
    _create_extreme_table,
    _create_period_selection_group,
    _init_ui,
    _setup_window,
)


class ExtremeWeatherDialog(QDialog):
    """
    Extrém időjárási események megjelenítésére szolgáló dialógus ablak - THEMEMANAGER INTEGRÁLT.

    🎨 VÁLTOZÁSOK:
    - utils.StyleSheets függőség eltávolítva
    - Widget regisztrációk ThemeManager-ben
    - Automatikus téma kezelés
    - CSS minimalizálás

    🔧 BUGFIX:
    - close_button attribute error javítva
    - Widget referenciák megfelelően elmentve

    🔧 KRITIKUS JAVÍTÁS:
    - Konstruktor típus hiba: QDialog → QWidget (QMainWindow kompatibilitás)

    🔧 IMPORT BUGFIX:
    - QColor import hozzáadva (PySide6.QtGui)

    FUNKCIONALITÁS MEGTARTVA:
    - Napi és havi extrém értékek megjelenítése
    - Interaktív váltás napi/havi nézet között
    - Statisztikai számítások (max/min/átlag/hőingás)
    - Táblázatos megjelenítés
    """

    def __init__(self, parent: Optional[QWidget], data: Dict[str, Any], city_name: str):
        """
        Dialógus inicializálása - THEMEMANAGER VERZIÓ + KONSTRUKTOR JAVÍTÁS.

        Args:
            parent: Szülő widget (QWidget - QMainWindow kompatibilis!)
            data: Open-Meteo API válasz adatok
            city_name: Település neve

        🔧 KRITIKUS JAVÍTÁS: QDialog → QWidget típus a parent paraméterben
        Most már működik QMainWindow szülővel is!
        """
        super().__init__(parent)

        # ThemeManager singleton lekérdezése
        self._theme_manager = get_theme_manager()

        self.data = data
        self.city_name = city_name
        self.period_type = "daily"  # Alapértelmezett: napi adatok

        _setup_window(self)
        _init_ui(self)
        _register_widgets_for_theming(self)
        _calculate_extremes(self)

    # Public API methods
    def apply_theme(self, dark_theme: bool) -> None:
        from .theme_handler import apply_theme

        apply_theme(self, dark_theme)

    # Private methods (imported from modules)
    def _setup_window(self) -> None:
        _setup_window(self)

    def _init_ui(self) -> None:
        _init_ui(self)

    def _create_period_selection_group(self):
        return _create_period_selection_group(self)

    def _create_extreme_table(self):
        return _create_extreme_table(self)

    def _create_close_button(self):
        return _create_close_button(self)

    def _register_widgets_for_theming(self) -> None:
        _register_widgets_for_theming(self)

    def _on_period_type_changed(self) -> None:
        _on_period_type_changed(self)

    def _calculate_extremes(self) -> None:
        _calculate_extremes(self)
