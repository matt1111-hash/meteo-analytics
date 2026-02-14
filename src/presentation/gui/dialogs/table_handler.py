#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Dialogs - Table Handler

📋 Táblázat kezelés

Képességek:
- Táblázat feltöltése
- Üzenetek megjelenítése

Fájl: src/presentation/gui/dialogs/table_handler.py
"""

from typing import TYPE_CHECKING, Dict, List

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QTableWidgetItem

if TYPE_CHECKING:
    pass


def _populate_extreme_table(self, extremes: List[Dict[str, str]]) -> None:
    """
    Extrém értékek táblázatának feltöltése - THEMEMANAGER SZÍNEKKEL.

    Args:
        self: ExtremeWeatherDialog instance
        extremes: Extrém értékek listája
    """
    self.extreme_table.setRowCount(len(extremes))

    # ThemeManager színek lekérdezése
    scheme = self._theme_manager.get_color_scheme()

    for i, extreme in enumerate(extremes):
        # Item-ek létrehozása
        category_item = QTableWidgetItem(extreme["category"])
        value_item = QTableWidgetItem(extreme["value"])
        date_item = QTableWidgetItem(extreme["date"])

        # ThemeManager színek alkalmazása item-ekre
        if scheme:
            # 🔧 KRITIKUS JAVÍTÁS: ColorPalette API helyes használata
            # Alternáló háttérszínek
            if i % 2 == 0:
                bg_color = QColor(scheme.get_color("surface", "base") or "#ffffff")
            else:
                bg_color = QColor(scheme.get_color("surface", "light") or "#f5f5f5")

            # Szövegszín
            text_color = QColor(scheme.get_color("primary", "base") or "#000000")

            for item in [category_item, value_item, date_item]:
                item.setBackground(bg_color)
                item.setForeground(text_color)

        # Táblázat feltöltése
        self.extreme_table.setItem(i, 0, category_item)
        self.extreme_table.setItem(i, 1, value_item)
        self.extreme_table.setItem(i, 2, date_item)

    # Oszlopok szélességének automatikus beállítása
    self.extreme_table.resizeColumnsToContents()


def _show_no_data_message(self) -> None:
    """
    Nincs adat üzenet megjelenítése.

    Args:
        self: ExtremeWeatherDialog instance
    """
    self.extreme_table.setRowCount(1)
    self.extreme_table.setItem(0, 0, QTableWidgetItem("Nincs megjeleníthető adat"))
    self.extreme_table.setItem(0, 1, QTableWidgetItem("-"))
    self.extreme_table.setItem(0, 2, QTableWidgetItem("-"))


def _show_calculation_error(self) -> None:
    """
    Számítási hiba üzenet megjelenítése.

    Args:
        self: ExtremeWeatherDialog instance
    """
    self.extreme_table.setRowCount(1)
    self.extreme_table.setItem(0, 0, QTableWidgetItem("Hiba a számítás során"))
    self.extreme_table.setItem(0, 1, QTableWidgetItem("Ellenőrizze az adatokat"))
    self.extreme_table.setItem(0, 2, QTableWidgetItem("-"))
