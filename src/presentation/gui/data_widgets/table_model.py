#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mypy: ignore-errors

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
                "Dátum",
                "Max hőmérséklet (°C)",
                "Min hőmérséklet (°C)",
                "Napi átlag (°C)",
                "Csapadék (mm)",
                "Szélsebesség (km/h)",
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

    def _get_cell_value(self, row: int, col: int) -> Any:
        """Return raw cell value for a logical column."""
        column_fallbacks = {
            3: None,
            4: 3,
            5: None,
        }
        if col == 0:
            return self._data.iloc[row, 0]
        if col in (1, 2):
            return self._data.iloc[row, col]

        fallback_column = column_fallbacks.get(col)
        if fallback_column is not None and len(self._data.columns) <= col:
            return self._data.iloc[row, fallback_column]
        if len(self._data.columns) <= col:
            return None
        return self._data.iloc[row, col]

    @staticmethod
    def _format_measurement(value: Any, missing: str = "N/A") -> str:
        """Format optional numeric values for display."""
        return f"{value:.1f}" if pd.notna(value) else missing

    def _get_display_value(self, row: int, col: int) -> Any:
        """Return formatted cell value for display role."""
        if col == 0:
            return self._get_cell_value(row, col)

        missing_map = {
            4: "0.0",
        }
        return self._format_measurement(
            self._get_cell_value(row, col),
            missing=missing_map.get(col, "N/A"),
        )

    def _get_background_color(self, row: int) -> QColor:
        """Resolve row background color from theme or fallback palette."""
        scheme = self._theme_manager.get_color_scheme()
        if scheme:
            surface_key = "base" if row % 2 == 0 else "light"
            fallback = "#ffffff" if row % 2 == 0 else "#f5f5f5"
            return QColor(scheme.get_color("surface", surface_key) or fallback)
        return QColor(255, 255, 255) if row % 2 else QColor(248, 249, 250)

    def _get_foreground_color(self) -> QColor:
        """Resolve text color from theme or fallback palette."""
        scheme = self._theme_manager.get_color_scheme()
        if scheme:
            return QColor(scheme.get_color("primary", "base") or "#1f2937")
        return QColor(31, 41, 55)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if not index.isValid() or self._data.empty:
            return None

        row, col = index.row(), index.column()

        if role == Qt.DisplayRole:
            return self._get_display_value(row, col)

        if role == Qt.BackgroundRole:
            return self._get_background_color(row)

        if role == Qt.ForegroundRole:
            return self._get_foreground_color()

        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter if col == 0 else Qt.AlignRight | Qt.AlignVCenter

        return None

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole
    ) -> Any:
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
