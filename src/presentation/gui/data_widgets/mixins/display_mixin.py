#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Data Widgets - Display Mixin
Táblázat megjelenítés és UI elemek.
"""

import pandas as pd
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ...theme_manager import register_widget_for_theming
from ..items import NumericTableWidgetItem


class DisplayMixin:
    """
    Táblázat megjelenítés és UI elemek.
    """

    # Signal
    row_selected = Signal(int)  # kiválasztott sor index

    def _init_ui(self) -> None:
        """UI elemek inicializálása."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        self.controls = self._create_controls()
        layout.addWidget(self.controls)

        self.table = QTableWidget()
        self._setup_sortable_table()
        layout.addWidget(self.table)

        self.info_bar = self._create_info_bar()
        layout.addWidget(self.info_bar)

    def _create_controls(self) -> QWidget:
        """Vezérlő panel létrehozása."""
        controls = QGroupBox("🔍 Táblázat vezérlők")
        layout = QHBoxLayout(controls)

        # Keresés
        search_layout = QHBoxLayout()
        search_label = QLabel("Keresés:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Írjon be keresési kifejezést...")
        self.search_input.textChanged.connect(self._apply_filter)

        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        # Oszlop szűrő
        filter_layout = QHBoxLayout()
        filter_label = QLabel("Oszlop:")
        self.column_filter = QComboBox()
        self.column_filter.addItems(
            ["Összes", "Dátum", "Hőmérséklet", "Csapadék", "Szél"]
        )
        self.column_filter.currentTextChanged.connect(self._apply_filter)

        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.column_filter)
        layout.addLayout(filter_layout)

        # Lapozás
        pagination_layout = QHBoxLayout()
        self.page_label = QLabel("Oldal:")
        self.page_spin = QSpinBox()
        self.page_spin.setMinimum(1)
        self.page_spin.setValue(1)
        self.page_spin.valueChanged.connect(self._change_page)

        self.rows_per_page_combo = QComboBox()
        self.rows_per_page_combo.addItems(["50", "100", "200", "Összes"])
        self.rows_per_page_combo.setCurrentText("Összes")
        self.rows_per_page_combo.currentTextChanged.connect(self._change_page_size)

        pagination_layout.addWidget(self.page_label)
        pagination_layout.addWidget(self.page_spin)
        pagination_layout.addWidget(QLabel("/ oldal"))
        pagination_layout.addWidget(self.rows_per_page_combo)
        layout.addLayout(pagination_layout)

        # Export gombok
        export_layout = QHBoxLayout()
        self.csv_btn = QPushButton("📄 CSV")
        self.csv_btn.clicked.connect(lambda: self._export_data("csv"))
        self.csv_btn.setEnabled(False)

        self.excel_btn = QPushButton("📊 Excel")
        self.excel_btn.clicked.connect(lambda: self._export_data("excel"))
        self.excel_btn.setEnabled(False)

        export_layout.addWidget(self.csv_btn)
        export_layout.addWidget(self.excel_btn)
        layout.addLayout(export_layout)

        return controls

    def _create_info_bar(self) -> QWidget:
        """Információs sáv létrehozása."""
        info_bar = QWidget()
        info_bar.setMaximumHeight(30)
        info_bar.setObjectName("info_bar")

        layout = QHBoxLayout(info_bar)
        layout.setContentsMargins(10, 5, 10, 5)

        self.rows_info = QLabel("Nincs adat")
        self.rows_info.setObjectName("rows_info")
        layout.addWidget(self.rows_info)

        layout.addStretch()

        return info_bar

    def _register_widgets_for_theming(self) -> None:
        """Widget-ek regisztrálása ThemeManager-ben."""
        register_widget_for_theming(self.search_input, "input")
        register_widget_for_theming(self.column_filter, "input")
        register_widget_for_theming(self.page_spin, "input")
        register_widget_for_theming(self.rows_per_page_combo, "input")
        register_widget_for_theming(self.csv_btn, "button")
        register_widget_for_theming(self.excel_btn, "button")
        register_widget_for_theming(self.table, "table")
        register_widget_for_theming(self.controls, "container")
        register_widget_for_theming(self, "container")

    def _connect_signals(self) -> None:
        """Signal-slot kapcsolatok."""
        self.table.itemSelectionChanged.connect(self._on_selection_changed)

    def _on_selection_changed(self) -> None:
        """Kiválasztás változás kezelése."""
        current_row = self.table.currentRow()
        if current_row >= 0:
            global_row = self.current_page * self.rows_per_page + current_row
            self.row_selected.emit(global_row)

    def _display_current_page(self) -> None:
        """Aktuális oldal megjelenítése."""
        if self.filtered_data is None or self.filtered_data.empty:
            self.table.setRowCount(0)
            self.table.setColumnCount(0)
            self._update_info_display(0, 0)
            return

        start_idx = self.current_page * self.rows_per_page
        end_idx = start_idx + self.rows_per_page
        page_data = self.filtered_data.iloc[start_idx:end_idx]

        self._populate_table_with_numeric_items(page_data)
        self._update_info_display(len(self.filtered_data), len(page_data))

    def _populate_table_with_numeric_items(self, data: pd.DataFrame) -> None:
        """Táblázat feltöltése NumericTableWidgetItem-ekkel."""
        rows, cols = data.shape

        headers = [
            "Dátum",
            "Max hőmérséklet (°C)",
            "Min hőmérséklet (°C)",
            "Napi átlag (°C)",
            "Csapadék (mm)",
        ]
        if cols > 5:
            headers.append("Szélsebesség (km/h)")

        self.table.setRowCount(rows)
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)

        scheme = self._theme_manager.get_color_scheme()

        for i in range(rows):
            for j in range(min(cols, len(headers))):
                value = data.iloc[i, j]

                if j == 0:
                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(Qt.AlignCenter)
                elif pd.isna(value):
                    item = NumericTableWidgetItem("N/A", -999999)
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                else:
                    numeric_value = float(value)

                    if j in [1, 2, 3]:
                        display_text = f"{numeric_value:.1f}"
                    elif j == 4:
                        display_text = f"{numeric_value:.1f}"
                    elif j == 5:
                        display_text = f"{numeric_value:.1f}"
                    else:
                        display_text = f"{numeric_value:.1f}"

                    item = NumericTableWidgetItem(display_text, numeric_value)
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

                if scheme:
                    if i % 2 == 0:
                        item.setBackground(
                            QColor(scheme.get_color("surface", "base") or "#ffffff")
                        )
                    else:
                        item.setBackground(
                            QColor(scheme.get_color("surface", "light") or "#f5f5f5")
                        )
                    item.setForeground(
                        QColor(scheme.get_color("primary", "base") or "#1f2937")
                    )
                else:
                    if i % 2 == 0:
                        item.setBackground(QColor(248, 249, 250))
                    else:
                        item.setBackground(QColor(255, 255, 255))
                    item.setForeground(QColor(31, 41, 55))

                self.table.setItem(i, j, item)

        self.table.resizeColumnsToContents()

        if self.current_sort_column >= 0:
            self.table.sortItems(self.current_sort_column, self.current_sort_order)

    def _update_info_display(self, total_rows: int, displayed_rows: int) -> None:
        """Információs szöveg frissítése."""
        if total_rows == 0:
            self.rows_info.setText("Nincs megjeleníthető adat")
        else:
            if (
                self.rows_per_page_combo.currentText() == "Összes"
                or displayed_rows == total_rows
            ):
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
