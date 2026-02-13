#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Universal Location Selector - Core

🇭🇺 ENHANCED Universal Location Selector fő osztály - DUAL DATABASE

Képességek:
- Kombinált keresés (3178 magyar + 44k globális)
- Magyar prioritás működik
- Flag-ek és settlement type-ok
- Signal kibocsátás lokáció változáskor

Fájl: src/presentation/gui/universal_location_selector/core.py
"""

import logging
from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QListWidgetItem,
    QWidget,
)

from src.domain.entities.location_types import LocationType
from src.domain.entities.universal_location import UniversalLocation
from src.domain.ports import CityManagerPort
from src.infrastructure.container import get_city_manager_port

from ..theme_manager import register_widget_for_theming
from .public_api import UniversalLocationSelectorPublicAPI
from .search_handler import SearchHandler
from .ui_builder import create_universal_location_selector_ui

logger = logging.getLogger(__name__)


class UniversalLocationSelector(QWidget, UniversalLocationSelectorPublicAPI):
    """
    🇭🇺 ENHANCED Universal Location Selector - DUAL DATABASE

    KOMBINÁLT KERESÉS:
    - 3178+ magyar település (falvak, községek, városok)
    - 44k+ globális város
    - Magyar prioritás működik
    - Flag-ek és settlement type-ok

    SIGNALOK:
    - search_requested(str): keresés indítva
    - city_selected(str, float, float, dict): lokáció kiválasztva
    - location_changed(UniversalLocation): lokáció változott
    """

    # Signalok
    search_requested = Signal(str)
    city_selected = Signal(str, float, float, dict)
    location_changed = Signal(object)

    def __init__(self, city_manager: Optional[CityManagerPort] = None, parent=None):
        """
        UniversalLocationSelector inicializálása (CA compliant - uses port).

        Args:
            city_manager: CityManagerPort instance
            parent: Szülő widget
        """
        super().__init__(parent)

        self.city_manager: CityManagerPort = city_manager or get_city_manager_port()
        self.current_location: Optional[UniversalLocation] = None

        # UI setup
        self._setup_ui()

        # Search handler
        self._search_handler = SearchHandler(
            self.city_manager,
            self.search_input,
            self.status_label,
            self.results_list,
            self.search_requested.emit,
        )

        self._connect_signals()
        register_widget_for_theming(self, "container")

        logger.info(
            "🇭🇺 Enhanced Universal Location Selector inicializálva (DUAL DATABASE)"
        )

    def _setup_ui(self) -> None:
        """UI elemek létrehozása."""
        ui_elements = create_universal_location_selector_ui(self)

        self.search_input = ui_elements["search_input"]
        self.status_label = ui_elements["status_label"]
        self.results_list = ui_elements["results_list"]
        self.location_card = ui_elements["location_card"]
        self.confirm_button = ui_elements["confirm_button"]

    def _connect_signals(self) -> None:
        """Signal kapcsolatok"""
        self.search_input.textChanged.connect(self._on_search_text_changed)
        self.results_list.itemDoubleClicked.connect(self._on_result_selected)
        self.results_list.itemClicked.connect(self._on_result_clicked)
        self.confirm_button.clicked.connect(self._on_confirm_selection)

    # === SEARCH HANDLERS ===

    def _on_search_text_changed(self, text: str) -> None:
        """Keresés szöveg változáskor"""
        self._search_handler.on_search_text_changed(text)
        self.confirm_button.setEnabled(False)

    # === RESULT HANDLERS ===

    def _on_result_clicked(self, item: QListWidgetItem) -> None:
        """Eredményre kattintás (preview) - MAGYAR TÁMOGATÁSSAL"""
        try:
            result_data = item.data(Qt.UserRole)
            if result_data:
                name = result_data.get("city", "Ismeretlen")
                country = result_data.get("country", "")
                region = result_data.get("admin_name", "")
                lat = float(result_data.get("lat", 0.0))
                lon = float(result_data.get("lon", 0.0))
                is_hungarian = result_data.get("is_hungarian", False)

                # MAGYAR SPECIFIKUS DETAILS
                details_parts = []

                if is_hungarian:
                    # Magyar település részletek
                    settlement_type = result_data.get("settlement_type")
                    if settlement_type:
                        details_parts.append(f"Típus: {settlement_type}")

                    megye = result_data.get("megye")
                    if megye:
                        details_parts.append(f"Megye: {megye}")

                    jaras = result_data.get("jaras")
                    if jaras:
                        details_parts.append(f"Járás: {jaras}")

                    population = result_data.get("population")
                    if population:
                        details_parts.append(f"Lakosság: {population:,}")

                else:
                    # Globális város részletek (eredeti)
                    if region and region != name:
                        details_parts.append(f"Régió: {region}")
                    if country:
                        details_parts.append(f"Ország: {country}")

                details_parts.append(f"Koordináták: [{lat:.4f}, {lon:.4f}]")
                details = "\n".join(details_parts)

                # Card frissítése
                self.location_card.set_location(name, details, is_hungarian)
                self.confirm_button.setEnabled(True)

                logger.info(
                    f"Eredmény preview: {name} ({'magyar' if is_hungarian else 'globális'})"
                )

        except Exception as e:
            logger.error(f"Preview hiba: {e}")

    def _on_result_selected(self, item: QListWidgetItem) -> None:
        """Eredmény dupla kattintás (azonnali kiválasztás)"""
        self._on_result_clicked(item)  # Preview
        self._on_confirm_selection()  # Azonnali megerősítés

    def _on_confirm_selection(self) -> None:
        """Lokáció megerősítése"""
        try:
            current_item = self.results_list.currentItem()
            if not current_item:
                return

            result_data = current_item.data(Qt.UserRole)
            if not result_data:
                return

            name = result_data.get("city", "Ismeretlen")
            lat = float(result_data.get("lat", 0.0))
            lon = float(result_data.get("lon", 0.0))
            is_hungarian = result_data.get("is_hungarian", False)

            # UniversalLocation objektum létrehozása
            location = UniversalLocation(
                type=LocationType.CITY,
                identifier=name,
                display_name=name,
                coordinates=(lat, lon),
            )

            self.current_location = location

            # Signalok küldése
            self.city_selected.emit(name, lat, lon, result_data)
            self.location_changed.emit(location)

            flag = "🇭🇺" if is_hungarian else "🌍"
            logger.info(f"Lokáció megerősítve: {flag} {name} [{lat:.4f}, {lon:.4f}]")

        except Exception as e:
            logger.error(f"Megerősítési hiba: {e}")
