#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Quick Overview Tab - Core

Gyors áttekintés tab komponens.

Fájl: src/presentation/gui/results_panel/quick_overview_tab/core.py
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional, TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget

from src.presentation.gui.theme_manager import get_theme_manager, register_widget_for_theming

from .temp_precip_stats import calculate_temperature_stats, calculate_precipitation_stats
from .wind_info_stats import calculate_wind_stats, update_info_labels, clear_stats
from .ui_builder import (
    create_mini_charts_container,
    create_quick_actions,
    create_stats_container,
    create_title_label,
)

if TYPE_CHECKING:
    from src.presentation.gui.results_panel.utils import DataFrameExtractor

logger = logging.getLogger(__name__)


class QuickOverviewTab(QWidget):
    """Gyors Áttekintés TAB - Kompakt statisztikák és mini preview-k."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Inicializálás."""
        super().__init__(parent)

        # Theme manager
        self.theme_manager = get_theme_manager()

        self.current_data: Optional[Dict[str, Any]] = None
        self._stat_labels: Dict[str, QWidget] = {}

        # UI inicializálása
        self._init_ui()
        self._register_widgets_for_theming()

        logger.info("QuickOverviewTab inicializálva")

    def _init_ui(self) -> None:
        """UI inicializálása."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # Cím
        self.title_label = create_title_label()
        layout.addWidget(self.title_label)

        # Statisztikai kártyák
        self._create_stats_section(layout)

        # Mini chartok
        self._create_mini_charts_section(layout)

        # Gyors akciók
        self._create_actions_section(layout)

        layout.addStretch()

    def _create_stats_section(self, layout: QVBoxLayout) -> None:
        """Statisztika szekció létrehozása."""
        def apply_text_styling(label):
            scheme = self.theme_manager.get_color_scheme()
            if not scheme:
                return
            text_color = scheme.get_color("primary", "base") or "#000000"
            label.setStyleSheet(f"QLabel {{ color: {text_color}; font-size: 13px; }}")

        def apply_accent_styling(label, accent_color):
            scheme = self.theme_manager.get_color_scheme()
            if not scheme:
                return
            color_mapping = {
                "#f59e0b": scheme.get_color("warning", "base") or "#f59e0b",
                "#3b82f6": scheme.get_color("primary", "base") or "#3b82f6",
                "#10b981": scheme.get_color("success", "base") or "#10b981",
            }
            theme_color = color_mapping.get(accent_color, scheme.get_color("primary", "base") or "#3b82f6")
            label.setStyleSheet(f"QLabel {{ font-weight: bold; color: {theme_color}; font-size: 14px; }}")

        (
            self.stats_container,
            self.temp_card,
            self.precip_card,
            self.wind_card,
            info_card_tuple,
        ) = create_stats_container(
            self.theme_manager,
            apply_text_styling,
            apply_accent_styling,
            self._stat_labels,
        )
        layout.addWidget(self.stats_container)

        # Info card elements - unpack the tuple
        self.info_card, self.city_info_label, self.date_range_label, self.data_source_label, self.record_count_label = info_card_tuple

    def _create_mini_charts_section(self, layout: QVBoxLayout) -> None:
        """Mini chartok szekció létrehozása."""
        self.mini_charts_container, self.mini_chart_placeholder = create_mini_charts_container()
        layout.addWidget(self.mini_charts_container)

    def _create_actions_section(self, layout: QVBoxLayout) -> None:
        """Gyors akciók szekció létrehozása."""
        container, self.charts_btn, self.table_btn, self.extreme_btn = create_quick_actions()
        layout.addWidget(container)

    def _register_widgets_for_theming(self) -> None:
        """Widget-ek regisztrálása ThemeManager-hez."""
        register_widget_for_theming(self, "container")
        register_widget_for_theming(self.stats_container, "container")
        register_widget_for_theming(self.temp_card, "container")
        register_widget_for_theming(self.precip_card, "container")
        register_widget_for_theming(self.wind_card, "container")
        register_widget_for_theming(self.info_card, "container")
        register_widget_for_theming(self.mini_charts_container, "container")
        register_widget_for_theming(self.title_label, "text")
        register_widget_for_theming(self.city_info_label, "text")
        register_widget_for_theming(self.date_range_label, "text")
        register_widget_for_theming(self.data_source_label, "text")
        register_widget_for_theming(self.record_count_label, "text")
        register_widget_for_theming(self.mini_chart_placeholder, "text")
        register_widget_for_theming(self.charts_btn, "button")
        register_widget_for_theming(self.table_btn, "button")
        register_widget_for_theming(self.extreme_btn, "button")

    def update_data(self, data: Dict[str, Any], city_name: str) -> None:
        """Adatok frissítése."""
        try:
            logger.info(f"QuickOverviewTab.update_data() - City: {city_name}")

            self.current_data = data

            # DataFrame kinyerése
            from ..utils import DataFrameExtractor
            df = DataFrameExtractor.extract_safely(data)

            if df.empty:
                logger.warning("QuickOverviewTab - DataFrame is empty!")
                clear_stats(self)
                return

            logger.info(f"QuickOverviewTab DataFrame shape: {df.shape}")

            # Statisztikák számítása
            calculate_temperature_stats(self, df)
            calculate_precipitation_stats(self, df)
            calculate_wind_stats(self, df)

            # Információk frissítése
            update_info_labels(self, data, city_name, df)

            logger.info("QuickOverviewTab update_data SIKERES!")

        except Exception as e:
            logger.error(f"QuickOverviewTab adatfrissítési hiba: {e}")
            clear_stats(self)
