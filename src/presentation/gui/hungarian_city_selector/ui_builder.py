#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Hungarian City Selector - UI Builder Module
UI komponensek létrehozása a HungarianCitySelector widgethez.
"""

import logging
from typing import List, Optional, Callable

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QGroupBox, QLabel, QLineEdit, QComboBox, QListWidget,
    QListWidgetItem, QPushButton
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from src.presentation.gui.hungarian_city_selector.types import HungarianCity, HungarianRegions


logger = logging.getLogger(__name__)


class HungarianCityUIBuilder:
    """
    UI komponens építő osztály.
    """

    def __init__(self, parent: QWidget):
        """
        Inicializálás.

        Args:
            parent: Szülő widget
        """
        self.parent = parent
        self.search_box: Optional[QLineEdit] = None
        self.region_combo: Optional[QComboBox] = None
        self.city_list: Optional[QListWidget] = None
        self.stats_label: Optional[QLabel] = None
        self.quick_access_buttons: List[QPushButton] = []

    def create_header(self) -> QHBoxLayout:
        """Fejléc létrehozása."""
        layout = QHBoxLayout()
        layout.setSpacing(8)

        # Magyar zászló és cím
        flag_label = QLabel("🇭🇺")
        flag_label.setStyleSheet("font-size: 24px; border: none; background: transparent;")
        layout.addWidget(flag_label)

        title_label = QLabel("Magyar Városok")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        layout.addStretch()

        # Verzió info
        version_label = QLabel("MVP v1.0")
        version_label.setStyleSheet("color: gray; font-size: 10px; border: none; background: transparent;")
        layout.addWidget(version_label)

        return layout

    def create_search_section(self, search_callback: Callable, clear_callback: Callable) -> QGroupBox:
        """Keresési szakasz létrehozása."""
        group = QGroupBox("🔍 Keresés")
        layout = QVBoxLayout(group)
        layout.setSpacing(8)

        # Keresőmező
        search_container = QHBoxLayout()

        search_icon = QLabel("🔍")
        search_icon.setStyleSheet("font-size: 16px; border: none; background: transparent;")
        search_container.addWidget(search_icon)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Keresés magyar városokban... (pl. Budapest, Szeged, Debrecen)")
        self.search_box.textChanged.connect(search_callback)
        self.search_box.returnPressed.connect(search_callback)
        search_container.addWidget(self.search_box)

        clear_btn = QPushButton("✖")
        clear_btn.setMaximumWidth(30)
        clear_btn.setToolTip("Keresés törlése")
        clear_btn.clicked.connect(clear_callback)
        search_container.addWidget(clear_btn)

        layout.addLayout(search_container)

        return group

    def create_filter_section(self, region_callback: Callable) -> QGroupBox:
        """Szűrési szakasz létrehozása."""
        group = QGroupBox("🗺️ Régió szűrés")
        layout = QVBoxLayout(group)
        layout.setSpacing(8)

        # Régió választó
        region_layout = QHBoxLayout()

        region_label = QLabel("Régió:")
        region_layout.addWidget(region_label)

        self.region_combo = QComboBox()
        self.region_combo.addItem("🇭🇺 Összes magyar város", "Összes")

        # Régiók hozzáadása
        for region in HungarianRegions.get_all_regions():
            display_name = HungarianRegions.REGION_DISPLAY_NAMES[region]
            description = HungarianRegions.REGION_DESCRIPTIONS[region]
            self.region_combo.addItem(f"{display_name}", region)

            # Tooltip beállítása
            index = self.region_combo.count() - 1
            self.region_combo.setItemData(index, description, Qt.ToolTipRole)

        self.region_combo.currentTextChanged.connect(region_callback)
        region_layout.addWidget(self.region_combo)

        region_layout.addStretch()

        layout.addLayout(region_layout)

        return group

    def create_cities_list_section(self, select_callback: Callable, reload_callback: Callable) -> QGroupBox:
        """Városok listája szakasz létrehozása."""
        group = QGroupBox("🏙️ Magyar városok listája")
        layout = QVBoxLayout(group)
        layout.setSpacing(8)

        # Városok lista
        self.city_list = QListWidget()
        self.city_list.setMinimumHeight(300)
        self.city_list.setMaximumHeight(400)
        layout.addWidget(self.city_list)

        # Lista alatti műveletek
        actions_layout = QHBoxLayout()

        select_btn = QPushButton("✅ Kiválasztás")
        select_btn.clicked.connect(select_callback)
        actions_layout.addWidget(select_btn)

        actions_layout.addStretch()

        refresh_btn = QPushButton("🔄 Frissítés")
        refresh_btn.setToolTip("Városok listájának újratöltése")
        refresh_btn.clicked.connect(reload_callback)
        actions_layout.addWidget(refresh_btn)

        layout.addLayout(actions_layout)

        return group

    def create_quick_access_section(self, city_callback: Callable) -> QGroupBox:
        """Gyors hozzáférés szakasz létrehozása."""
        group = QGroupBox("⚡ Gyors hozzáférés - Nagy magyar városok")
        layout = QGridLayout(group)
        layout.setSpacing(6)

        # Népszerű magyar városok
        quick_cities = [
            ("🏛️ Budapest", "Budapest", "Főváros - 1.7M lakos"),
            ("🌾 Debrecen", "Debrecen", "Cívisváros - 201k lakos"),
            ("🏭 Miskolc", "Miskolc", "Észak-Magyarország - 161k lakos"),
            ("🌊 Szeged", "Szeged", "Tisza-parti egyetemváros - 161k lakos"),
            ("⚙️ Pécs", "Pécs", "Dunántúli kulturális központ - 143k lakos"),
            ("🌍 Győr", "Győr", "Kisalföld központja - 129k lakos"),
            ("🏔️ Székesfehérvár", "Székesfehérvár", "Fejér megye székhelye - 95k lakos"),
            ("⛰️ Nyíregyháza", "Nyíregyháza", "Szabolcs-Szatmár-Bereg - 118k lakos"),
            ("🍇 Kecskemét", "Kecskemét", "Bács-Kiskun megye - 109k lakos"),
            ("🌲 Szombathely", "Szombathely", "Vas megye székhelye - 76k lakos"),
            ("💎 Veszprém", "Veszprém", "Balaton-felvidék - 57k lakos"),
            ("🍷 Kaposvár", "Kaposvár", "Somogy megye székhelye - 63k lakos")
        ]

        self.quick_access_buttons = []

        for i, (display, city, tooltip) in enumerate(quick_cities):
            btn = QPushButton(display)
            btn.setToolTip(tooltip)
            btn.setMinimumHeight(35)
            btn.clicked.connect(lambda checked, c=city: city_callback(c))

            # Rács elrendezés: 3 város per sor
            row = i // 3
            col = i % 3
            layout.addWidget(btn, row, col)

            self.quick_access_buttons.append(btn)

        return group

    def create_statistics_section(self) -> QGroupBox:
        """Statisztikák szakasz létrehozása."""
        group = QGroupBox("📊 Statisztikák")
        layout = QVBoxLayout(group)
        layout.setSpacing(4)

        self.stats_label = QLabel("Városok betöltése...")
        self.stats_label.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 8px;
                font-family: monospace;
                font-size: 11px;
            }
        """)
        layout.addWidget(self.stats_label)

        return group

    def populate_city_list(self, cities: List[HungarianCity]) -> None:
        """Városok lista feltöltése."""
        if not self.city_list:
            return

        self.city_list.clear()

        for city in cities:
            # Lista elem szöveg
            population_text = f"{city.population:,}" if city.population else "n/a"
            region_text = city.region or "Egyéb"

            item_text = f"🏙️ {city.city} ({population_text} fő) - {region_text}"

            # Lista elem létrehozása
            item = QListWidgetItem(item_text)

            # Tooltip részletes információkkal
            tooltip = f"""
            Város: {city.city}
            Régió: {region_text}
            Népesség: {population_text} fő
            Koordináták: {city.lat:.4f}, {city.lon:.4f}
            Megye: {city.admin_name or 'n/a'}
            Adatminőség: {city.data_quality_score or 'n/a'}
            """
            item.setToolTip(tooltip.strip())

            # City objektum tárolása
            item.setData(Qt.UserRole, city)

            self.city_list.addItem(item)

        logger.debug(f"🏙️ {len(cities)} város megjelenítve a listában")

    def update_stats(self, stats_text: str) -> None:
        """Statisztikák szöveg frissítése."""
        if self.stats_label:
            self.stats_label.setText(stats_text)

    def get_current_region(self) -> str:
        """Jelenlegi régió lekérdezése."""
        if not self.region_combo:
            return 'Összes'
        current_data = self.region_combo.currentData()
        return current_data if current_data else 'Összes'

    def set_region(self, region: str) -> None:
        """Régió programozott beállítása."""
        if self.region_combo:
            for i in range(self.region_combo.count()):
                if self.region_combo.itemData(i) == region:
                    self.region_combo.setCurrentIndex(i)
                    break

    def set_search_term(self, search_term: str) -> None:
        """Keresési kifejezés programozott beállítása."""
        if self.search_box:
            self.search_box.setText(search_term)

    def clear_search_box(self) -> None:
        """Keresőmező törlése."""
        if self.search_box:
            self.search_box.clear()
