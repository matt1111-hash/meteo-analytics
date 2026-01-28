#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Hungarian City Selector - Event Handlers Module
Event handler metódusok a HungarianCitySelector osztályhoz.
"""

import logging

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QListWidgetItem

from src.presentation.gui.hungarian_city_selector.database_loader import (
    HungarianCityDatabaseLoader,
)
from src.presentation.gui.hungarian_city_selector.types import HungarianCity

logger = logging.getLogger(__name__)


class HungarianCityEventHandlersMixin:
    """Event handler metódusok a HungarianCitySelector osztályhoz."""

    def _on_search_text_changed(self, text: str) -> None:
        """Keresés szöveg változásának kezelése."""
        self.search_filter.on_search_text_changed(text)

    def _on_region_changed(self) -> None:
        """Régió változás kezelése."""
        region = self.ui_builder.get_current_region()
        self.search_filter.on_region_changed(region)

    def _on_city_selected(self, item: QListWidgetItem) -> None:
        """Város kiválasztás kezelése (dupla kattintás)."""
        city = item.data(Qt.UserRole)
        if isinstance(city, HungarianCity):
            self._emit_city_selected(city)

    def _select_current_city(self) -> None:
        """Jelenlegi kiválasztott város elfogadása."""
        if not self.ui_builder.city_list:
            return

        current_item = self.ui_builder.city_list.currentItem()
        if current_item:
            self._on_city_selected(current_item)
        else:
            logger.warning("⚠️ Nincs kiválasztott város")

    def _select_quick_city(self, city_name: str) -> None:
        """Gyors hozzáférésű város kiválasztása."""
        # Város keresése a betöltött adatok között
        for city in self.hungarian_cities:
            if city.city == city_name:
                self._emit_city_selected(city)
                return

        logger.warning(f"⚠️ Gyors hozzáférésű város nem található: {city_name}")

    def _emit_city_selected(self, city: HungarianCity) -> None:
        """
        City selected signal kibocsátása.

        Args:
            city: Kiválasztott HungarianCity objektum
        """
        # Metadata összeállítása
        metadata = {
            'name': city.city,
            'latitude': city.lat,
            'longitude': city.lon,
            'country': city.country,
            'country_code': city.country_code,
            'population': city.population,
            'admin_name': city.admin_name,
            'region': city.region,
            'meteostat_station_id': city.meteostat_station_id,
            'data_quality_score': city.data_quality_score,
            'source': 'hungarian_city_selector',
            'display_name': f"{city.city}, Magyarország",
            'preferred_source': 'open-meteo'  # Magyar városokhoz Open-Meteo optimális
        }

        # Signal kibocsátása
        self.city_selected.emit(city.city, city.lat, city.lon, metadata)

        logger.info(f"✅ Város kiválasztva: {city.city} ({city.lat:.4f}, {city.lon:.4f})")

    def _reload_cities(self) -> None:
        """Városok listájának újratöltése."""
        logger.info("🔄 Magyar városok újratöltése...")
        self.hungarian_cities.clear()
        if self.ui_builder.city_list:
            self.ui_builder.city_list.clear()
        self.ui_builder.update_stats("🔄 Újratöltés...")
        self._load_hungarian_cities()

    def _clear_search(self) -> None:
        """Keresés törlése."""
        self.search_filter.clear_search()
        self.ui_builder.clear_search_box()
        stats_text = HungarianCityDatabaseLoader.calculate_city_stats(self.hungarian_cities)
        self.ui_builder.update_stats(stats_text)

    def _on_theme_changed(self, theme_name: str) -> None:
        """Téma változás kezelése."""
        self.theme_handler._apply_current_theme()
        logger.debug(f"🎨 HungarianCitySelector téma frissítve: {theme_name}")
