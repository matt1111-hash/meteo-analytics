#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Universal Location Selector - Search Handler

🔍 Keresési logika és eredmények kezelése

Képességek:
- Keresés indítása és időzítés
- Eredmények megjelenítése
- Magyar és globális eredmények formázása

Fájl: src/presentation/gui/universal_location_selector/search_handler.py
"""

import logging
from typing import List

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QLabel, QLineEdit, QListWidget, QListWidgetItem

from typing import Dict, Any

from src.domain.ports import CityManagerPort

logger = logging.getLogger(__name__)


class SearchHandler:
    """
    Keresési logika kezelése.

    Felelősség:
    - Keresés indítása és időzítés
    - Eredmények megjelenítése
    - Magyar és globális eredmények formázása
    """

    def __init__(
        self,
        city_manager: CityManagerPort,
        search_input: QLineEdit,
        status_label: QLabel,
        results_list: QListWidget,
        search_requested_callback
    ):
        """
        SearchHandler inicializálása.

        Args:
            city_manager: CityManager instance
            search_input: Search input widget
            status_label: Status label widget
            results_list: Results list widget
            search_requested_callback: Callback when search is requested
        """
        self.city_manager = city_manager
        self.search_input = search_input
        self.status_label = status_label
        self.results_list = results_list
        self.search_requested_callback = search_requested_callback

        # Search timer
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self._perform_search)

    def on_search_text_changed(self, text: str) -> None:
        """
        Keresés szöveg változáskor.

        Args:
            text: Új kereső szöveg
        """
        if len(text) < 2:
            self.results_list.clear()
            self.status_label.setText("💡 Legalább 2 karakter szükséges...")
            return

        self.search_timer.stop()
        self.search_timer.start(300)  # 300ms késleltetés
        self.status_label.setText("🔍 Keresés...")

    def _perform_search(self) -> None:
        """KOMBINÁLT KERESÉS - Magyar + Globális"""
        query = self.search_input.text().strip()
        if len(query) < 2:
            return

        try:
            self.search_requested_callback(query)

            # KULCS VÁLTOZÁS: search_unified() hívása
            results = self.city_manager.search_unified(query, limit=20, hungarian_priority=True)

            self._display_results(results)

            if not results:
                self.status_label.setText(f"❌ Nincs találat a '{query}' keresésre")
            else:
                # Eredmény típusok számlálása
                hungarian_count = sum(1 for city in results if city.is_hungarian)
                global_count = len(results) - hungarian_count

                if hungarian_count > 0 and global_count > 0:
                    self.status_label.setText(f"✅ {hungarian_count} magyar + {global_count} globális = {len(results)} találat")
                elif hungarian_count > 0:
                    self.status_label.setText(f"✅ {hungarian_count} magyar találat")
                else:
                    self.status_label.setText(f"✅ {global_count} globális találat")

        except Exception as e:
            logger.error(f"Keresési hiba: {e}")
            self.status_label.setText("❌ Keresési hiba történt")

    def _display_results(self, results: List[Dict[str, Any]]) -> None:
        """
        Keresési eredmények megjelenítése MAGYAR PRIORITÁSSAL

        Args:
            results: Talált városok listája
        """
        self.results_list.clear()

        for city in results[:20]:  # Első 20 eredmény
            try:
                # Alap adatok
                name = city.get('city', city.get('name', 'Unknown'))
                lat = city.get('lat', 0.0)
                lon = city.get('lon', 0.0)
                is_hungarian = city.get('is_hungarian', False)

                # MAGYAR SPECIFIKUS FORMATTING
                if is_hungarian:
                    display_text = self._format_hungarian_city(city, name, lat, lon)
                else:
                    # GLOBÁLIS FORMATTING (eredeti)
                    display_text = self._format_global_city(city, name, lat, lon)

                # List item létrehozása
                item = QListWidgetItem(display_text)
                item.setData(Qt.UserRole, city)
                self.results_list.addItem(item)

            except Exception as e:
                logger.warning(f"Eredmény feldolgozási hiba: {e}")

    def _format_hungarian_city(self, city: Dict[str, Any], name: str, lat: float, lon: float) -> str:
        """
        Magyar város formázása.

        Args:
            city: City objektum
            name: Város neve
            lat: Szélesség
            lon: Hosszúság

        Returns:
            Formázott szöveg
        """
        flag = "🇭🇺"

        # Display név: "Kiskunhalas, Bács-Kiskun megye"
        megye = city.get('megye', '')
        if megye:
            display_name = f"{name}, {megye} megye"
        else:
            display_name = name

        # Settlement type info
        settlement_info = ""
        settlement_type = city.get('settlement_type')
        if settlement_type:
            settlement_info = f" ({settlement_type})"

        # Population info
        pop_info = ""
        population = city.get('population')
        if population:
            pop_info = f"\n👥 {population:,} lakos"

        return f"{flag} {display_name}{settlement_info}{pop_info}\n🗺️ [{lat:.3f}, {lon:.3f}]"

    def _format_global_city(self, city: Dict[str, Any], name: str, lat: float, lon: float) -> str:
        """
        Globális város formázása.

        Args:
            city: City objektum
            name: Város neve
            lat: Szélesség
            lon: Hosszúság

        Returns:
            Formázott szöveg
        """
        flag = "🌍"
        country = city.get('country', '') or ''
        region = city.get('admin_name', '') or ''

        display_text = f"{flag} {name}"
        if region and region != name:
            display_text += f"\n📍 {region}"
        if country:
            display_text += f", {country}"
        display_text += f"\n🗺️ [{lat:.3f}, {lon:.3f}]"

        return display_text
