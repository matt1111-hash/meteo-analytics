# mypy: ignore-errors
"""Hungarian City Selector - UI Builder Module."""

from __future__ import annotations

import logging
from collections.abc import Callable

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QComboBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.presentation.gui.hungarian_city_selector.types import (
    HungarianCity,
    HungarianRegions,
)

logger = logging.getLogger(__name__)


class HungarianCityUIBuilder:
    """UI komponens epito osztaly."""

    def __init__(self, parent: QWidget):
        """
        Inicializalas.

        Args:
            parent: Szulo widget
        """
        self.parent = parent
        self.search_box: QLineEdit | None = None
        self.region_combo: QComboBox | None = None
        self.city_list: QListWidget | None = None
        self.stats_label: QLabel | None = None
        self.quick_access_buttons: list[QPushButton] = []

    def create_header(self) -> QHBoxLayout:
        """Fejlec letrehozasa."""
        layout = QHBoxLayout()
        layout.setSpacing(8)

        # Magyar zaszlo es cim
        flag_label = QLabel("HU")
        flag_label.setStyleSheet("font-size: 24px; border: none; background: transparent;")
        layout.addWidget(flag_label)

        title_label = QLabel("Magyar Varosok")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        layout.addStretch()

        # Verzio info
        version_label = QLabel("MVP v1.0")
        version_label.setStyleSheet(
            "color: gray; font-size: 10px; border: none; background: transparent;"
        )
        layout.addWidget(version_label)

        return layout

    def create_search_section(
        self, search_callback: Callable, clear_callback: Callable
    ) -> QGroupBox:
        """Keresesi szakasz letrehozasa."""
        group = QGroupBox("Kereses")
        layout = QVBoxLayout(group)
        layout.setSpacing(8)

        # Kerezomezo
        search_container = QHBoxLayout()

        search_icon = QLabel("S")
        search_icon.setStyleSheet("font-size: 16px; border: none; background: transparent;")
        search_container.addWidget(search_icon)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText(
            "Kereses magyar varosokban... (pl. Budapest, Szeged, Debrecen)"
        )
        self.search_box.textChanged.connect(search_callback)
        self.search_box.returnPressed.connect(search_callback)
        search_container.addWidget(self.search_box)

        clear_btn = QPushButton("X")
        clear_btn.setMaximumWidth(30)
        clear_btn.setToolTip("Kereses torlese")
        clear_btn.clicked.connect(clear_callback)
        search_container.addWidget(clear_btn)

        layout.addLayout(search_container)

        return group

    def create_filter_section(self, region_callback: Callable) -> QGroupBox:
        """Szuresi szakasz letrehozasa."""
        group = QGroupBox("Regio szures")
        layout = QVBoxLayout(group)
        layout.setSpacing(8)

        # Regio valaszto
        region_layout = QHBoxLayout()

        region_label = QLabel("Regio:")
        region_layout.addWidget(region_label)

        self.region_combo = QComboBox()
        self.region_combo.addItem("Osszes magyar varos", "Osszes")

        # Regiok hozzaadasa
        for region in HungarianRegions.get_all_regions():
            display_name = HungarianRegions.REGION_DISPLAY_NAMES[region]
            description = HungarianRegions.REGION_DESCRIPTIONS[region]
            self.region_combo.addItem(f"{display_name}", region)

            # Tooltip beallitasa
            index = self.region_combo.count() - 1
            self.region_combo.setItemData(index, description, Qt.ToolTipRole)

        self.region_combo.currentTextChanged.connect(region_callback)
        region_layout.addWidget(self.region_combo)

        region_layout.addStretch()

        layout.addLayout(region_layout)

        return group

    def create_cities_list_section(
        self, select_callback: Callable, reload_callback: Callable
    ) -> QGroupBox:
        """Varosok listaja szakasz letrehozasa."""
        group = QGroupBox("Magyar varosok listaja")
        layout = QVBoxLayout(group)
        layout.setSpacing(8)

        # Varosok lista
        self.city_list = QListWidget()
        self.city_list.setMinimumHeight(300)
        self.city_list.setMaximumHeight(400)
        layout.addWidget(self.city_list)

        # Lista alatti muveletek
        actions_layout = QHBoxLayout()

        select_btn = QPushButton("Kivalasztas")
        select_btn.clicked.connect(select_callback)
        actions_layout.addWidget(select_btn)

        actions_layout.addStretch()

        refresh_btn = QPushButton("Frissites")
        refresh_btn.setToolTip("Varosok listajanak ujratoltese")
        refresh_btn.clicked.connect(reload_callback)
        actions_layout.addWidget(refresh_btn)

        layout.addLayout(actions_layout)

        return group

    def create_quick_access_section(self, city_callback: Callable) -> QGroupBox:
        """Gyors hozzaferes szakasz letrehozasa."""
        group = QGroupBox("Gyors hozzaferes - Nagy magyar varosok")
        layout = QGridLayout(group)
        layout.setSpacing(6)

        # Nepeszeru magyar varosok
        quick_cities = [
            ("Budapest", "Budapest", "Fovaros - 1.7M lakos"),
            ("Debrecen", "Debrecen", "Civisvaros - 201k lakos"),
            ("Miskolc", "Miskolc", "Eszak-Magyarorszag - 161k lakos"),
            ("Szeged", "Szeged", "Tisza-parti egyetemvaros - 161k lakos"),
            ("Pecs", "Pecs", "Dunantuli kulturális kozpont - 143k lakos"),
            ("Gyor", "Gyor", "Kisalfold kozpontja - 129k lakos"),
            ("Szekesfehervar", "Szekesfehervar", "Fejer megye szekhelye - 95k lakos"),
            ("Nyiregyhaza", "Nyiregyhaza", "Szabolcs-Szatmar-Bereg - 118k lakos"),
            ("Kecskemet", "Kecskemet", "Bacs-Kiskun megye - 109k lakos"),
            ("Szombathely", "Szombathely", "Vas megye szekhelye - 76k lakos"),
            ("Veszprem", "Veszprem", "Balaton-felvidek - 57k lakos"),
            ("Kaposvar", "Kaposvar", "Somogy megye szekhelye - 63k lakos"),
        ]

        self.quick_access_buttons = []

        for i, (display, city, tooltip) in enumerate(quick_cities):
            btn = QPushButton(display)
            btn.setToolTip(tooltip)
            btn.setMinimumHeight(35)
            btn.clicked.connect(lambda checked, c=city: city_callback(c))  # noqa: ARG005

            # Racsc elrendezes: 3 varos per sor
            row = i // 3
            col = i % 3
            layout.addWidget(btn, row, col)

            self.quick_access_buttons.append(btn)

        return group

    def create_statistics_section(self) -> QGroupBox:
        """Statisztikak szakasz letrehozasa."""
        group = QGroupBox("Statisztikak")
        layout = QVBoxLayout(group)
        layout.setSpacing(4)

        self.stats_label = QLabel("Varosok betoltese...")
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

    def populate_city_list(self, cities: list[HungarianCity]) -> None:
        """Varosok lista feltoltese."""
        if not self.city_list:
            return

        self.city_list.clear()

        for city in cities:
            # Lista elem szoveg
            population_text = f"{city.population:,}" if city.population else "n/a"
            region_text = city.region or "Egyeb"

            item_text = f"{city.city} ({population_text} fo) - {region_text}"

            # Lista elem letrehozasa
            item = QListWidgetItem(item_text)

            # Tooltip reszletes informaciokkal
            tooltip = f"""
            Varos: {city.city}
            Regio: {region_text}
            Nepesseg: {population_text} fo
            Koordinatak: {city.lat:.4f}, {city.lon:.4f}
            Megye: {city.admin_name or "n/a"}
            Adatminoseg: {city.data_quality_score or "n/a"}
            """
            item.setToolTip(tooltip.strip())

            # City objektum tarolasa
            item.setData(Qt.UserRole, city)

            self.city_list.addItem(item)

        logger.debug(f"{len(cities)} varos megjelenitve a listaban")

    def update_stats(self, stats_text: str) -> None:
        """Statisztikak szoveg frissitese."""
        if self.stats_label:
            self.stats_label.setText(stats_text)

    def get_current_region(self) -> str:
        """Jelenlegi regio lekerdezese."""
        if not self.region_combo:
            return "Osszes"
        current_data = self.region_combo.currentData()
        return current_data if current_data else "Osszes"

    def set_region(self, region: str) -> None:
        """Regio programozott beallitasa."""
        if self.region_combo:
            for i in range(self.region_combo.count()):
                if self.region_combo.itemData(i) == region:
                    self.region_combo.setCurrentIndex(i)
                    break

    def set_search_term(self, search_term: str) -> None:
        """Keresesi kifejezes programozott beallitasa."""
        if self.search_box:
            self.search_box.setText(search_term)

    def clear_search_box(self) -> None:
        """Kerezomezo torlese."""
        if self.search_box:
            self.search_box.clear()
