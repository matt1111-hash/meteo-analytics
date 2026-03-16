#!/usr/bin/env python3
# mypy: ignore-errors
# -*- coding: utf-8 -*-

"""
Data Widgets - Sorting Mixin
Táblázat rendezés kezelése.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QAbstractItemView, QHeaderView


class SortingMixin:
    """
    Táblázat rendezés kezelése.
    """

    # Signal
    sorting_changed = Signal(int, str)  # column, order (asc/desc)

    def _setup_sorting(self) -> None:
        """Rendezési állapot inicializálása."""
        self.current_sort_column = -1
        self.current_sort_order = Qt.AscendingOrder

    def _setup_sortable_table(self) -> None:
        """Táblázat beállítások rendezhető funkcióval."""
        self.table.setSortingEnabled(True)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.sectionClicked.connect(self._on_header_clicked)

    def _on_header_clicked(self, logical_index: int) -> None:
        """Fejléc kattintás kezelése - rendezési állapot követése."""
        if self.current_sort_column == logical_index:
            if self.current_sort_order == Qt.AscendingOrder:
                self.current_sort_order = Qt.DescendingOrder
                order_text = "csökkenő"
            else:
                self.current_sort_order = Qt.AscendingOrder
                order_text = "növekvő"
        else:
            self.current_sort_column = logical_index
            self.current_sort_order = Qt.AscendingOrder
            order_text = "növekvő"

        headers = [
            "Dátum",
            "Max hőmérséklet",
            "Min hőmérséklet",
            "Napi átlag",
            "Csapadék",
            "Szélsebesség",
        ]
        column_name = (
            headers[logical_index]
            if logical_index < len(headers)
            else f"Oszlop {logical_index}"
        )

        self.table.sortItems(logical_index, self.current_sort_order)

        self.sorting_changed.emit(logical_index, order_text)
        print(f"🔢 Táblázat rendezve: {column_name} ({order_text})")

        if hasattr(self, "rows_info"):
            current_text = self.rows_info.text()
            self.rows_info.setText(
                f"{current_text} | Rendezve: {column_name} ({order_text})"
            )

    def get_sorting_info(self) -> tuple:
        """Jelenlegi rendezési állapot lekérdezése."""
        order_text = (
            "növekvő" if self.current_sort_order == Qt.AscendingOrder else "csökkenő"
        )
        return (self.current_sort_column, order_text)
