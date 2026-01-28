#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Hungarian City Selector - Core Module
Fő HungarianCitySelector widget osztály.
"""

import logging
from pathlib import Path
from typing import List

from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Signal

from src.presentation.gui.hungarian_city_selector.types import HungarianCity
from src.presentation.gui.hungarian_city_selector.database_loader import HungarianCityDatabaseLoader
from src.presentation.gui.hungarian_city_selector.search_filter import HungarianCitySearchFilter
from src.presentation.gui.hungarian_city_selector.ui_builder import HungarianCityUIBuilder
from src.presentation.gui.hungarian_city_selector.theme_handler import HungarianCityThemeHandler
from src.presentation.gui.hungarian_city_selector.event_handlers import HungarianCityEventHandlersMixin
from src.presentation.gui.hungarian_city_selector.public_api import HungarianCityPublicAPIMixin


logger = logging.getLogger(__name__)


class HungarianCitySelector(
    HungarianCityEventHandlersMixin,
    HungarianCityPublicAPIMixin
):
    """
    🇭🇺 Hungarian City Selector Widget - Magyar Klímaanalitika MVP

    165 magyar város dinamikus választó widget teljes funkcionalitással:
    - Adatbázis integráció (cities.db)
    - Régió alapú szűrés
    - Keresési funkció
    - ThemeManager integráció
    - Signal-based kommunikáció
    """

    # Signalok
    city_selected = Signal(str, float, float, dict)      # name, lat, lon, metadata
    region_selected = Signal(str, list)                  # region_name, cities
    search_completed = Signal(int)                       # results_count
    data_loaded = Signal(int)                           # cities_count
    error_occurred = Signal(str)                        # error_message

    def __init__(self, db_path: str = "src/data/cities.db", parent=None):
        super().__init__(parent)

        # Konfiguráció
        self.db_path = Path(db_path)

        # Adatok
        self.hungarian_cities: List[HungarianCity] = []

        # UI builder
        self.ui_builder = HungarianCityUIBuilder(self)

        # Theme handler
        self.theme_handler = HungarianCityThemeHandler(self, self._on_theme_changed)

        # Search filter (később inicializálva, a városok betöltése után)
        self.search_filter: HungarianCitySearchFilter = None  # type: ignore

        # UI építése
        self._setup_ui()

        # Adatok betöltése
        self._load_hungarian_cities()

        logger.info("🇭🇺 HungarianCitySelector widget inicializálva")

    def _setup_ui(self) -> None:
        """UI komponensek felépítése."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)

        # === FEJLÉC ===
        header_layout = self.ui_builder.create_header()
        main_layout.addLayout(header_layout)

        # === KERESÉSI SZAKASZ ===
        search_group = self.ui_builder.create_search_section(
            self._on_search_text_changed,
            self._clear_search
        )
        main_layout.addWidget(search_group)

        # === SZŰRÉSI SZAKASZ ===
        filter_group = self.ui_builder.create_filter_section(self._on_region_changed)
        main_layout.addWidget(filter_group)

        # === VÁROSOK LISTÁJA ===
        cities_group = self.ui_builder.create_cities_list_section(
            self._select_current_city,
            self._reload_cities
        )
        main_layout.addWidget(cities_group)

        # === GYORS HOZZÁFÉRÉS ===
        quick_group = self.ui_builder.create_quick_access_section(self._select_quick_city)
        main_layout.addWidget(quick_group)

        # === STATISZTIKÁK ===
        stats_group = self.ui_builder.create_statistics_section()
        main_layout.addWidget(stats_group)

        # Rugalmas tér
        main_layout.addStretch()

        # Theme regisztráció (a UI elemek létrehozása után)
        self.theme_handler.register_widgets(
            self.ui_builder.search_box,
            self.ui_builder.region_combo,
            self.ui_builder.city_list,
            self.ui_builder.quick_access_buttons
        )

        # Kezdeti téma alkalmazása
        self.theme_handler.apply_initial_theme()

    def _load_hungarian_cities(self) -> None:
        """Magyar városok betöltése a cities.db adatbázisból."""
        db_loader = HungarianCityDatabaseLoader(self.db_path)
        self.hungarian_cities = db_loader.load_cities(
            self.error_occurred,
            self.ui_builder.update_stats
        )

        # Search filter létrehozása a városok betöltése után
        self.search_filter = HungarianCitySearchFilter(
            self.hungarian_cities,
            self.search_completed,
            self.region_selected,
            self.ui_builder.update_stats,
            lambda: self.ui_builder.populate_city_list(self.search_filter.get_filtered_cities())
        )

        # Lista feltöltése
        self.ui_builder.populate_city_list(self.hungarian_cities)

        # Statisztikák frissítése
        stats_text = HungarianCityDatabaseLoader.calculate_city_stats(self.hungarian_cities)
        self.ui_builder.update_stats(stats_text)

        # Signal
        self.data_loaded.emit(len(self.hungarian_cities))
