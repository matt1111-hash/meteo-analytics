# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Mixin part 1 for DisplayMixin."""

from __future__ import annotations

from .display_mixin_support import *


class DisplayMixinPart1Mixin:
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
