# ruff: noqa: F403, F405,noqa: I001
# mypy: ignore-errors
"""Mixin part 2 for DisplayMixin."""

from __future__ import annotations

from .display_mixin_support import *


def _build_headers(column_count: int) -> list[str]:
    """Build table headers for the dataframe."""
    headers = [
        "Dátum",
        "Max hőmérséklet (°C)",
        "Min hőmérséklet (°C)",
        "Napi átlag (°C)",
        "Csapadék (mm)",
    ]
    if column_count > 5:  # noqa: PLR2004
        headers.append("Szélsebesség (km/h)")
    return headers


def _format_numeric_value(column_index: int, numeric_value: float) -> str:  # noqa: ARG001
    """Format numeric table text."""
    return f"{numeric_value:.1f}"


def _create_table_item(value: Any, column_index: int) -> QTableWidgetItem:
    """Create a table item for a cell value."""
    if column_index == 0:
        item = QTableWidgetItem(str(value))
        item.setTextAlignment(Qt.AlignCenter)
        return item
    if pd.isna(value):
        item = NumericTableWidgetItem("N/A", -999999)
        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        return item
    numeric_value = float(value)
    item = NumericTableWidgetItem(_format_numeric_value(column_index, numeric_value), numeric_value)
    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
    return item


def _apply_item_colors(item: QTableWidgetItem, row_index: int, scheme: Any) -> None:
    """Apply themed or fallback colors to a table item."""
    if scheme:
        background_key = ("surface", "base") if row_index % 2 == 0 else ("surface", "light")
        background = scheme.get_color(*background_key) or (
            "#ffffff" if row_index % 2 == 0 else "#f5f5f5"
        )
        foreground = scheme.get_color("primary", "base") or "#1f2937"
        item.setBackground(QColor(background))
        item.setForeground(QColor(foreground))
        return
    item.setBackground(QColor(248, 249, 250) if row_index % 2 == 0 else QColor(255, 255, 255))
    item.setForeground(QColor(31, 41, 55))


class DisplayMixinPart2Mixin:  # noqa: D101
    def _populate_table_with_numeric_items(self, data: pd.DataFrame) -> None:
        """Táblázat feltöltése NumericTableWidgetItem-ekkel."""
        rows, cols = data.shape
        headers = _build_headers(cols)

        self.table.setRowCount(rows)
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)

        scheme = self._theme_manager.get_color_scheme()

        for i in range(rows):
            for j in range(min(cols, len(headers))):
                value = data.iloc[i, j]
                item = _create_table_item(value, j)
                _apply_item_colors(item, i, scheme)
                self.table.setItem(i, j, item)

        self.table.resizeColumnsToContents()

        if self.current_sort_column >= 0:
            self.table.sortItems(self.current_sort_column, self.current_sort_order)

    def _update_info_display(self, total_rows: int, displayed_rows: int) -> None:
        """Információs szöveg frissítése."""
        if total_rows == 0:
            self.rows_info.setText("Nincs megjeleníthető adat")
        else:
            if self.rows_per_page_combo.currentText() == "Összes" or displayed_rows == total_rows:
                info_text = f"Összesen: {total_rows} sor (mind megjelenítve)"
            else:
                current_page = self.current_page + 1
                total_pages = max(1, (total_rows - 1) // self.rows_per_page + 1)
                info_text = f"Összesen: {total_rows} sor | "
                info_text += f"Megjelenítve: {displayed_rows} sor | "
                info_text += f"Oldal: {current_page}/{total_pages}"

            self.rows_info.setText(info_text)

    def apply_theme(self, dark_theme: bool) -> None:
        """Téma alkalmazása."""
        theme_name = "dark" if dark_theme else "light"
        self._theme_manager.set_theme(theme_name)

        scheme = self._theme_manager.get_color_scheme()
        if scheme and hasattr(self, "info_bar"):
            surface_variant = scheme.get_color("surface", "light") or "#f5f5f5"
            border_color = scheme.get_color("info", "light") or "#d1d5db"

            self.info_bar.setStyleSheet(f"""
                QWidget#info_bar {{
                    background-color: {surface_variant};
                    border-top: 1px solid {border_color};
                }}
            """)

            if hasattr(self, "rows_info"):
                text_color = scheme.get_color("info", "base") or "#6b7280"
                self.rows_info.setStyleSheet(f"""
                    QLabel#rows_info {{
                        color: {text_color};
                        font-size: 11px;
                    }}
                """)

        if self.filtered_data is not None and not self.filtered_data.empty:
            self._display_current_page()
