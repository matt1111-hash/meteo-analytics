#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mypy: ignore-errors

"""
Data Widgets - Numeric Table Item
Intelligens QTableWidgetItem numerikus rendezéshez.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidgetItem


class NumericTableWidgetItem(QTableWidgetItem):
    """
    Intelligens QTableWidgetItem, amely lehetővé teszi a numerikus rendezést
    akkor is, ha a megjelenített szöveg mértékegységet tartalmaz.

    Példa: "15.2 °C" szöveg, de 15.2 numerikus érték alapján rendez.
    """

    def __init__(self, display_text: str, numeric_value: float):
        """
        Args:
            display_text: Megjelenítendő szöveg (pl. "15.2 °C")
            numeric_value: Rendezéshez használt numerikus érték (pl. 15.2)
        """
        super().__init__(display_text)
        self.numeric_value = numeric_value

    def __lt__(self, other: "NumericTableWidgetItem") -> bool:
        """
        Összehasonlító metódus felülírása a rendezéshez.
        A tárolt numerikus érték alapján hasonlít össze, nem a szöveg szerint.
        """
        if isinstance(other, NumericTableWidgetItem):
            return self.numeric_value < other.numeric_value
        # Fallback a szöveges összehasonlításra, ha más típusú item
        return super().__lt__(other)

    def data(self, role: int):
        """Qt data role kezelése - numerikus érték visszaadása rendezéshez."""
        if role == Qt.UserRole:
            return self.numeric_value
        return super().data(role)
