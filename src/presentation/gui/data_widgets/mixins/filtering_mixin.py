#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Data Widgets - Filtering Mixin
Szűrés, lapozás és keresés kezelése.
"""

import pandas as pd
from PySide6.QtCore import Signal


class FilteringMixin:
    """
    Szűrés, lapozás és keresés kezelése.
    """

    # Signal
    data_filtered = Signal(int)  # szűrt sorok száma

    def _setup_filtering(self) -> None:
        """Lapozási állapot inicializálása."""
        self.current_page = 0
        self.rows_per_page = 1000

    def _apply_filter(self) -> None:
        """Szűrés alkalmazása."""
        if self.current_data is None or self.current_data.empty:
            return

        search_text = self.search_input.text().lower()
        column_filter = self.column_filter.currentText()

        filtered_df = self.current_data.copy()

        if search_text:
            if column_filter == "Összes":
                mask = filtered_df.astype(str).apply(
                    lambda x: x.str.lower().str.contains(search_text, na=False)
                ).any(axis=1)
            elif column_filter == "Dátum":
                mask = filtered_df.iloc[:, 0].astype(str).str.lower().str.contains(search_text, na=False)
            elif column_filter == "Hőmérséklet":
                mask = (filtered_df.iloc[:, 1].astype(str).str.contains(search_text, na=False) |
                       filtered_df.iloc[:, 2].astype(str).str.contains(search_text, na=False) |
                       (len(filtered_df.columns) > 3 and filtered_df.iloc[:, 3].astype(str).str.contains(search_text, na=False)))
            elif column_filter == "Csapadék":
                precip_col = 4 if len(filtered_df.columns) > 4 else 3
                if precip_col < len(filtered_df.columns):
                    mask = filtered_df.iloc[:, precip_col].astype(str).str.contains(search_text, na=False)
                else:
                    mask = pd.Series([False] * len(filtered_df))
            elif column_filter == "Szél":
                if len(filtered_df.columns) > 5:
                    mask = filtered_df.iloc[:, -1].astype(str).str.contains(search_text, na=False)
                else:
                    mask = pd.Series([False] * len(filtered_df))
            else:
                mask = pd.Series([True] * len(filtered_df))

            filtered_df = filtered_df[mask]

        self.filtered_data = filtered_df
        self._update_pagination()
        self._display_current_page()

        self.data_filtered.emit(len(filtered_df))

    def _change_page(self, page: int) -> None:
        """Oldal váltás."""
        self.current_page = page - 1
        self._display_current_page()

    def _change_page_size(self, size_text: str) -> None:
        """Oldalméret váltás."""
        if size_text == "Összes":
            self.rows_per_page = len(self.filtered_data) if self.filtered_data is not None else 1000
        else:
            self.rows_per_page = int(size_text)

        self.current_page = 0
        self.page_spin.setValue(1)
        self._update_pagination()
        self._display_current_page()

        if size_text == "Összes":
            total_rows = len(self.filtered_data) if self.filtered_data is not None else 0
            print(f"✅ Táblázat beállítva: ÖSSZES {total_rows} sor egy oldalon")

    def _update_pagination(self) -> None:
        """Lapozás frissítése."""
        if self.filtered_data is None or self.filtered_data.empty:
            self.page_spin.setMaximum(1)
            return

        total_pages = max(1, (len(self.filtered_data) - 1) // self.rows_per_page + 1)
        self.page_spin.setMaximum(total_pages)

        if self.current_page >= total_pages:
            self.current_page = total_pages - 1
            self.page_spin.setValue(self.current_page + 1)
