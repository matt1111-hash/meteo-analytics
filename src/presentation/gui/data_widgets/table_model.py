#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Data Widgets - Weather Table Model
Időjárási adatok tábla modellje - ThemeManager kompatibilis.
"""

import logging
from typing import Any, Optional

import pandas as pd
from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtGui import QColor

from ..theme_manager import get_theme_manager

logger = logging.getLogger(__name__)


class WeatherTableModel(QAbstractTableModel):
    """
    Időjárási adatok tábla modellje - THEMEMANAGER KOMPATIBILIS.
    Nagy adathalmazok hatékony kezelésére optimalizálva.
    """

    def __init__(self, data: Optional[pd.DataFrame] = None):
        super().__init__()
        self._data = data if data is not None else pd.DataFrame()
        self._headers = []
        self._theme_manager = get_theme_manager()
        self._update_headers()

    def _update_headers(self) -> None:
        """Oszlop fejlécek frissítése - SZAKMAILAG PONTOS ELNEVEZÉSSEL."""
        if not self._data.empty:
            self._headers = [
                "Dátum", "Max hőmérséklet (°C)", "Min hőmérséklet (°C)",
                "Napi átlag (°C)", "Csapadék (mm)", "Szélsebesség (km/h)"
            ]
        else:
            self._headers = []

    def set_theme(self, dark_theme: bool) -> None:
        """
        Téma beállítása - THEMEMANAGER DELEGÁLÁS.

        Args:
            dark_theme: True, ha sötét téma
        """
        theme_name = "dark" if dark_theme else "light"
        self._theme_manager.set_theme(theme_name)
        self.dataChanged.emit(QModelIndex(), QModelIndex())

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._data)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._headers)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if not index.isValid() or self._data.empty:
            return None

        row, col = index.row(), index.column()

        if role == Qt.DisplayRole:
            if col == 0:  # Dátum
                return self._data.iloc[row, 0]
            elif col == 1:  # Max hőmérséklet
                value = self._data.iloc[row, 1]
                return f"{value:.1f}" if pd.notna(value) else "N/A"
            elif col == 2:  # Min hőmérséklet
                value = self._data.iloc[row, 2]
                return f"{value:.1f}" if pd.notna(value) else "N/A"
            elif col == 3:  # Átlag hőmérséklet
                value = self._data.iloc[row, 3] if len(self._data.columns) > 3 else None
                return f"{value:.1f}" if pd.notna(value) else "N/A"
            elif col == 4:  # Csapadék
                value = self._data.iloc[row, 4] if len(self._data.columns) > 4 else self._data.iloc[row, 3]
                return f"{value:.1f}" if pd.notna(value) else "0.0"
            elif col == 5:  # Szélsebesség
                value = self._data.iloc[row, 5] if len(self._data.columns) > 5 else None
                return f"{value:.1f}" if pd.notna(value) else "N/A"

        elif role == Qt.BackgroundRole:
            scheme = self._theme_manager.get_color_scheme()
            if scheme:
                if row % 2 == 0:
                    return QColor(scheme.get_color("surface", "base") or "#ffffff")
                return QColor(scheme.get_color("surface", "light") or "#f5f5f5")
            return QColor(255, 255, 255) if row % 2 else QColor(248, 249, 250)

        elif role == Qt.ForegroundRole:
            scheme = self._theme_manager.get_color_scheme()
            if scheme:
                return QColor(scheme.get_color("primary", "base") or "#1f2937")
            return QColor(31, 41, 55)

        elif role == Qt.TextAlignmentRole:
            if col == 0:
                return Qt.AlignCenter
            else:
                return Qt.AlignRight | Qt.AlignVCenter

        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> Any:
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            if 0 <= section < len(self._headers):
                return self._headers[section]
        elif role == Qt.ForegroundRole and orientation == Qt.Horizontal:
            scheme = self._theme_manager.get_color_scheme()
            if scheme:
                return QColor(scheme.get_color("primary", "base") or "#374151")
            return QColor(55, 65, 81)
        return None

    def update_data(self, data: pd.DataFrame) -> None:
        """Adatok frissítése."""
        self.beginResetModel()
        self._data = data
        self._update_headers()
        self.endResetModel()
