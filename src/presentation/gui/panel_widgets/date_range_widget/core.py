#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Date Range Widget - Core

📅 Dátum tartomány választó widget fő osztálya

Képességek:
- Date mode selection (time_range vs manual_dates)
- Multi-year dropdown (1/5/10/25/55 év)
- Manual date pickers + quick buttons
- Signal kibocsátás dátum változáskor

Fájl: src/presentation/gui/panel_widgets/date_range_widget/core.py
"""

from typing import Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QVBoxLayout, QWidget

from ..theme_manager import get_theme_manager
from .date_handlers import DateHandlerMixin
from .public_api import DateRangeWidgetPublicAPI
from .ui_builder import (
    create_manual_dates_group,
    create_time_range_group,
    register_for_theming,
)


class DateRangeWidget(QWidget, DateHandlerMixin, DateRangeWidgetPublicAPI):
    """
    📅 DÁTUM TARTOMÁNY WIDGET - CLEAN ARCHITECTURE

    Felelősség:
    - Date mode selection (time_range vs manual_dates)
    - Multi-year dropdown (1/5/10/25/55 év)
    - Manual date pickers + quick buttons
    - Computed dates calculation
    - Date validation

    Interface:
    - date_range_changed = Signal(str, str) - start_date, end_date
    - date_mode_changed = Signal(str) - "time_range" vagy "manual_dates"
    - get_state() -> dict - aktuális állapot
    - set_state(dict) - állapot beállítása
    - is_valid() -> bool - valid dátum tartomány
    """

    # === KIMENŐ SIGNALOK ===
    date_range_changed = Signal(str, str)  # start_date, end_date (ISO format)
    date_mode_changed = Signal(str)  # "time_range" vagy "manual_dates"

    def __init__(self, parent: Optional[QWidget] = None):
        """
        DateRangeWidget inicializálása.

        Args:
            parent: Szülő widget
        """
        super().__init__(parent)

        # Theme manager
        self.theme_manager = get_theme_manager()

        # State
        self.date_mode = "time_range"  # "time_range" vagy "manual_dates"
        self._updating_state = False

        # UI init
        self._init_ui()
        self._connect_signals()
        self._register_for_theming()

        # Initial computation
        self._update_computed_dates()

        print("📅 DEBUG: DateRangeWidget inicializálva - Multi-Year Batch Support")

    def _init_ui(self) -> None:
        """UI elemek létrehozása."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # Time range group
        time_range_elements = create_time_range_group(self)
        self.time_range_group = time_range_elements["time_range_group"]
        self.time_range_radio = time_range_elements["time_range_radio"]
        self.manual_dates_radio = time_range_elements["manual_dates_radio"]
        self.time_range_combo = time_range_elements["time_range_combo"]
        self.computed_dates_info = time_range_elements["computed_dates_info"]

        # Manual dates group
        manual_dates_elements = create_manual_dates_group(self)
        self.manual_dates_group = manual_dates_elements["manual_dates_group"]
        self.start_date = manual_dates_elements["start_date"]
        self.end_date = manual_dates_elements["end_date"]
        self.last_month_btn = manual_dates_elements["last_month_btn"]
        self.last_year_btn = manual_dates_elements["last_year_btn"]
        self.last_1year_btn = manual_dates_elements["last_1year_btn"]
        self.last_5years_btn = manual_dates_elements["last_5years_btn"]
        self.last_10years_btn = manual_dates_elements["last_10years_btn"]
        self.last_25years_btn = manual_dates_elements["last_25years_btn"]
        self.last_55years_btn = manual_dates_elements["last_55years_btn"]

        # Kezdetben disabled
        self._set_manual_dates_enabled(False)

    def _connect_signals(self) -> None:
        """Signal-slot kapcsolatok."""
        # Mode change
        self.time_range_radio.toggled.connect(self._on_date_mode_changed)
        self.manual_dates_radio.toggled.connect(self._on_date_mode_changed)

        # Time range combo
        self.time_range_combo.currentTextChanged.connect(self._on_time_range_changed)

        # Manual dates
        self.start_date.dateChanged.connect(self._on_manual_date_changed)
        self.end_date.dateChanged.connect(self._on_manual_date_changed)

        # Quick buttons
        self.last_month_btn.clicked.connect(self._set_last_month)
        self.last_year_btn.clicked.connect(self._set_last_year)
        self.last_1year_btn.clicked.connect(lambda: self._set_years_back(1))
        self.last_5years_btn.clicked.connect(lambda: self._set_years_back(5))
        self.last_10years_btn.clicked.connect(lambda: self._set_years_back(10))
        self.last_25years_btn.clicked.connect(lambda: self._set_years_back(25))
        self.last_55years_btn.clicked.connect(lambda: self._set_years_back(55))

    def _register_for_theming(self) -> None:
        """Theme manager regisztráció."""
        buttons = [
            self.last_month_btn, self.last_year_btn, self.last_1year_btn,
            self.last_5years_btn, self.last_10years_btn, self.last_25years_btn,
            self.last_55years_btn
        ]

        register_for_theming(
            self.theme_manager,
            self,
            self.time_range_group,
            self.manual_dates_group,
            self.time_range_radio,
            self.manual_dates_radio,
            self.time_range_combo,
            self.start_date,
            self.end_date,
            buttons,
            self.computed_dates_info
        )

    # === SIGNAL HANDLERS ===

    def _on_date_mode_changed(self) -> None:
        """Date mode változás kezelése."""
        if self._updating_state:
            return

        old_mode = self.date_mode

        if self.time_range_radio.isChecked():
            self.date_mode = "time_range"
            self._set_manual_dates_enabled(False)
            self._update_computed_dates()
        else:
            self.date_mode = "manual_dates"
            self._set_manual_dates_enabled(True)

        print(f"📅 DEBUG: Date mode changed: {old_mode} → {self.date_mode}")

        # Signals
        self.date_mode_changed.emit(self.date_mode)
        start_date, end_date = self._get_effective_date_range()
        self.date_range_changed.emit(start_date, end_date)
