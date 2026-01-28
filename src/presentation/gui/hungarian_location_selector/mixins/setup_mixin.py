#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🗺️ Hungarian Location Selector - Setup Mixin
Magyar Klímaanalitika MVP - UI setup és theme
"""

import logging
from pathlib import Path

from PySide6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from ..worker import HungarianLocationWorker

logger = logging.getLogger(__name__)


class SetupMixin:
    """
    🎨 UI setup és theme mixin a HungarianLocationSelector számára.
    """

    def _setup_ui(self):
        """
        🎨 UI komponensek létrehozása.
        """
        from ...color_palette import ColorPalette
        from ...theme_manager import register_widget_for_theming

        self.color_palette = ColorPalette()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # === 🔧 JAVÍTOTT: STATISZTIKAI RÉGIÓ VÁLASZTÓ ===

        region_group = QGroupBox("🏛️ Magyar Statisztikai Régiók (NUTS 2)")
        register_widget_for_theming(region_group, "container")
        region_layout = QVBoxLayout(region_group)

        self.region_combo = QComboBox()
        self.region_combo.addItem("Válassz statisztikai régiót...", None)
        register_widget_for_theming(self.region_combo, "input")

        # 🔧 KRITIKUS: 7 statisztikai régió hozzáadása (Control Panel konzisztens!)
        for region_key, region_data in self.region_data.items():
            self.region_combo.addItem(
                f"{region_data.display_name} ({region_data.nuts_code})",
                region_key
            )

        region_layout.addWidget(self.region_combo)

        # Régió információs panel
        self.region_info = QTextEdit()
        self.region_info.setMaximumHeight(120)  # Kicsit nagyobb a több info miatt
        self.region_info.setReadOnly(True)
        register_widget_for_theming(self.region_info, "text")
        region_layout.addWidget(self.region_info)

        layout.addWidget(region_group)

        # === 🗺️ MEGYE VÁLASZTÓ ===

        county_group = QGroupBox("🗺️ Megye Választás")
        register_widget_for_theming(county_group, "container")
        county_layout = QVBoxLayout(county_group)

        self.county_combo = QComboBox()
        self.county_combo.addItem("Először válassz régiót...", None)
        self.county_combo.setEnabled(False)
        register_widget_for_theming(self.county_combo, "input")
        county_layout.addWidget(self.county_combo)

        layout.addWidget(county_group)

        # === 📍 LOKÁCIÓ RÉSZLETEK ===

        location_group = QGroupBox("📍 Lokáció Részletek")
        register_widget_for_theming(location_group, "container")
        location_layout = QVBoxLayout(location_group)

        # Koordináta megjelenítés
        coords_layout = QHBoxLayout()

        self.lat_label = QLabel("Szélesség: -")
        self.lon_label = QLabel("Hosszúság: -")
        register_widget_for_theming(self.lat_label, "text")
        register_widget_for_theming(self.lon_label, "text")

        coords_layout.addWidget(self.lat_label)
        coords_layout.addWidget(self.lon_label)
        location_layout.addLayout(coords_layout)

        # Terület információ
        self.area_label = QLabel("Terület: -")
        register_widget_for_theming(self.area_label, "text")
        location_layout.addWidget(self.area_label)

        # 🔧 JAVÍTOTT: Debug információk megjelenítése
        if self._debug_enabled:
            self.debug_label = QLabel("🔧 DEBUG: State = {}")
            self.debug_label.setStyleSheet("color: #E74C3C; font-family: monospace; font-size: 10px;")
            location_layout.addWidget(self.debug_label)

        layout.addWidget(location_group)

        # === 📄 BETÖLTÉSI PROGRESS ===

        progress_group = QGroupBox("📄 Térképi Adatok Betöltése")
        register_widget_for_theming(progress_group, "container")
        progress_layout = QVBoxLayout(progress_group)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        register_widget_for_theming(self.progress_bar, "input")
        progress_layout.addWidget(self.progress_bar)

        self.progress_label = QLabel("Adatok betöltése...")
        register_widget_for_theming(self.progress_label, "text")
        progress_layout.addWidget(self.progress_label)

        layout.addWidget(progress_group)

        # === 🎯 AKCIÓ GOMBOK ===

        button_layout = QHBoxLayout()

        self.refresh_btn = QPushButton("🔄 Frissítés")
        self.refresh_btn.setToolTip("Térképi adatok újratöltése")
        register_widget_for_theming(self.refresh_btn, "button")
        button_layout.addWidget(self.refresh_btn)

        self.center_map_btn = QPushButton("🎯 Térkép Központosítás")
        self.center_map_btn.setToolTip("Térkép központosítása a kiválasztott területre")
        self.center_map_btn.setEnabled(False)
        register_widget_for_theming(self.center_map_btn, "button")
        button_layout.addWidget(self.center_map_btn)

        layout.addLayout(button_layout)

        # Spacer a végén
        layout.addStretch()

    def _setup_theme(self):
        """
        🎨 Téma beállítások alkalmazása.
        """
        from ...theme_manager import register_widget_for_theming
        register_widget_for_theming(self, "container")

    def _connect_signals(self):
        """
        🔗 Signal-slot kapcsolatok létrehozása.
        """
        self.region_combo.currentTextChanged.connect(self._on_region_changed)
        self.county_combo.currentTextChanged.connect(self._on_county_changed)
        self.refresh_btn.clicked.connect(self._start_data_loading)
        self.center_map_btn.clicked.connect(self._center_map_on_selection)

    def _start_data_loading(self):
        """
        📄 GeoJSON adatok betöltésének indítása.
        """
        from ..worker import GEOPANDAS_AVAILABLE

        if not GEOPANDAS_AVAILABLE:
            self.progress_label.setText("❌ GeoPandas nem elérhető!")
            return

        # Worker thread indítása
        project_root = Path(__file__).parent.parent.parent.parent
        data_dir = project_root / "data" / "geojson"

        if not data_dir.exists():
            self.progress_label.setText("❌ GeoJSON könyvtár nem található!")
            return

        self.data_worker = HungarianLocationWorker(data_dir)

        # Worker signalok kapcsolása
        self.data_worker.progress_updated.connect(self.progress_bar.setValue)
        self.data_worker.counties_loaded.connect(self._on_counties_loaded)
        self.data_worker.postal_codes_loaded.connect(self._on_postal_codes_loaded)
        self.data_worker.error_occurred.connect(self._on_data_error)
        self.data_worker.completed.connect(self._on_data_loading_completed)

        # Worker indítása
        self.progress_label.setText("📄 GeoJSON adatok betöltése...")
        self.data_worker.start()
