#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Windy Days Tab - Core

Szeles napok analízis tab komponens.

Fájl: src/presentation/gui/results_panel/windy_days_tab/core.py
"""

from __future__ import annotations

import logging
from typing import Dict, Optional, TYPE_CHECKING

import pandas as pd
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QCheckBox, QVBoxLayout, QWidget

from src.analytics.wind_analysis import WINDY_DAY_THRESHOLD_KMH
from src.presentation.gui.charts.windy_days_chart import WindyDaysChart
from src.presentation.gui.theme_manager import ProfessionalThemeManager, register_widget_for_theming

from .data_processor import (
    clear_data,
    get_current_threshold,
    set_threshold,
    update_data,
)
from .handlers import (
    handle_analyze_clicked,
    handle_auto_update_toggled,
    handle_export_clicked,
    handle_threshold_changed,
)
from .ui_builder import (
    create_chart_section,
    create_content_splitter,
    create_controls_section,
    create_footer_section,
    create_header_section,
    create_progress_section,
    create_summary_section,
)

if TYPE_CHECKING:
    from PySide6.QtWidgets import QFrame, QGroupBox, QLabel, QProgressBar, QPushButton, QSpinBox, QSplitter, QTextEdit

logger = logging.getLogger(__name__)


class WindyDaysTab(QWidget):
    """
    Szeles napok analízis tab komponens.

    Megjeleníti a szeles napok havi eloszlását oszlopdiagramon,
    beállítható küszöbértékkel és részletes statisztikákkal.
    """

    # Signals
    analysis_completed = Signal(dict)
    error_occurred = Signal(str)
    export_requested = Signal(str, str)  # file_type, file_path

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Inicializálás."""
        super().__init__(parent)

        # UI components
        self.chart: Optional[WindyDaysChart] = None
        self.summary_text: Optional[QTextEdit] = None
        self.threshold_spinbox: Optional[QSpinBox] = None
        self.progress_bar: Optional[QProgressBar] = None
        self.analyze_button: Optional[QPushButton] = None
        self.export_button: Optional[QPushButton] = None
        self.auto_update_checkbox: Optional[QCheckBox] = None
        self._header_frame: Optional[QFrame] = None
        self._controls_group: Optional[QGroupBox] = None
        self._footer_frame: Optional[QFrame] = None

        # Data
        self.current_weather_data: Optional[pd.DataFrame] = None
        self.current_location: str = "Ismeretlen helyszín"
        self.current_analysis_result: Optional[Dict] = None

        # Theme manager
        self.theme_manager = ProfessionalThemeManager()

        # Initialize
        self._init_ui()
        self._connect_signals()
        self._apply_theme()

        logger.info("WindyDaysTab inicializálva")

    def _init_ui(self) -> None:
        """UI elemek inicializálása."""
        try:
            # Main layout
            main_layout = QVBoxLayout(self)
            main_layout.setSpacing(10)
            main_layout.setContentsMargins(10, 10, 10, 10)

            # Header
            self._header_frame, _, _ = create_header_section()
            main_layout.addWidget(self._header_frame)

            # Controls
            self._controls_group, self.threshold_spinbox, self.analyze_button, self.export_button = create_controls_section(
                WINDY_DAY_THRESHOLD_KMH
            )
            main_layout.addWidget(self._controls_group)

            # Progress bar
            self.progress_bar = create_progress_section()
            main_layout.addWidget(self.progress_bar)

            # Content splitter
            content_splitter = create_content_splitter()

            # Chart és summary
            self.chart = WindyDaysChart()
            chart_frame, _ = create_chart_section(self.chart)
            summary_frame, self.summary_text = create_summary_section()

            content_splitter.addWidget(chart_frame)
            content_splitter.addWidget(summary_frame)

            main_layout.addWidget(content_splitter, 1)

            # Footer
            self._footer_frame, _ = create_footer_section()
            main_layout.addWidget(self._footer_frame)

            # Set initial message
            self._set_initial_summary_message()

            logger.info("WindyDaysTab UI inicializálva")

        except Exception as e:
            logger.error(f"Hiba a UI inicializálásában: {e}")

    def _set_initial_summary_message(self) -> None:
        """Kezdeti üzenet beállítása."""
        try:
            initial_message = """
Szeles Napok Analízis

Még nem futott analízis.

Kattints az "Analízis Futtatása" gombra
az időjárási adatok elemzéséhez.

Beállítható paraméterek:
- Küszöbérték: szélsebesség limit
- Automatikus frissítés: ki/bekapcsolás

A rendszer megszámolja azokat a napokat,
amikor a maximális szélsebesség meghaladja
a beállított küszöbértéket.

MEGBÍZIK A RESULTSPANEL KONVERZIÓJÁBAN!
DUPLA KONVERZIÓ ELTÁVOLÍTVA!
            """.strip()

            if self.summary_text:
                self.summary_text.setPlainText(initial_message)

        except Exception as e:
            logger.error(f"Hiba a kezdeti üzenet beállításában: {e}")

    def _connect_signals(self) -> None:
        """Signal kapcsolatok létrehozása."""
        try:
            if self.analyze_button:
                self.analyze_button.clicked.connect(lambda: handle_analyze_clicked(self))

            if self.export_button:
                self.export_button.clicked.connect(lambda: handle_export_clicked(self))

            if self.threshold_spinbox:
                self.threshold_spinbox.valueChanged.connect(lambda v: handle_threshold_changed(self, v))

            # Auto update checkbox查找
            auto_update = self.findChild(QCheckBox, "auto_update_checkbox")
            if auto_update:
                self.auto_update_checkbox = auto_update
                auto_update.toggled.connect(lambda c: handle_auto_update_toggled(self, c))

            # Theme manager
            self.theme_manager.theme_changed.connect(self._on_theme_changed)

            logger.info("WindyDaysTab signal kapcsolatok létrehozva")

        except Exception as e:
            logger.error(f"Hiba a signal kapcsolatok létrehozásában: {e}")

    def _apply_theme(self) -> None:
        """Theme alkalmazása."""
        try:
            # Theme manager regisztráció
            register_widget_for_theming(self, "container")

            # Chart theme
            if self.chart:
                register_widget_for_theming(self.chart, "chart")

        except Exception as e:
            logger.error(f"Hiba a theme alkalmazásában: {e}")

    def _on_theme_changed(self, theme_name: str) -> None:
        """Theme változás kezelése."""
        try:
            logger.info(f"WindyDaysTab theme változás: {theme_name}")
            self._apply_theme()

        except Exception as e:
            logger.error(f"Hiba a theme változás kezelésében: {e}")

    # Public methods - delegálás a data_processor modulra
    def update_data(self, weather_data: pd.DataFrame, location: str = "Ismeretlen helyszín") -> None:
        """Adatok frissítése."""
        update_data(self, weather_data, location)

    def clear_data(self) -> None:
        """Adatok és UI tartalom törlése."""
        clear_data(self)

    def get_current_threshold(self) -> float:
        """Aktuális küszöbérték lekérdezése."""
        return get_current_threshold(self)

    def set_threshold(self, threshold: float) -> None:
        """Küszöbérték beállítása."""
        set_threshold(self, threshold)
