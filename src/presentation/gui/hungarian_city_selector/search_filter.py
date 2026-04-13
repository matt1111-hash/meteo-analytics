#!/usr/bin/env python3
# mypy: ignore-errors

"""
Hungarian City Selector - Search & Filter Module
Keresés és szűrés logika magyar városokhoz.
"""

import logging

from PySide6.QtCore import QTimer, Signal
from src.presentation.gui.hungarian_city_selector.types import (
    HungarianCity,
    HungarianRegions,
)

logger = logging.getLogger(__name__)


class HungarianCitySearchFilter:
    """
    Keresés és szűrés kezelő osztály.
    """

    def __init__(
        self,
        all_cities: list[HungarianCity],
        search_completed_signal: Signal,
        region_selected_signal: Signal,
        stats_update_callback: callable,
        populate_callback: callable,
    ):
        """
        Inicializálás.

        Args:
            all_cities: Összes betöltött város
            search_completed_signal: Signal keresés befejezésekor
            region_selected_signal: Signal régió választásakor
            stats_update_callback: Statisztika frissítési callback
            populate_callback: Lista feltöltési callback
        """
        self.all_cities = all_cities
        self.search_completed_signal = search_completed_signal
        self.region_selected_signal = region_selected_signal
        self.stats_update_callback = stats_update_callback
        self.populate_callback = populate_callback

        self.current_region = "Összes"
        self.current_search_term = ""
        self.filtered_cities: list[HungarianCity] = []

        # Keresési debounce timer
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self._trigger_search)

    @property
    def search_timer_ref(self) -> QTimer:
        """Timer hivatkozás a szülő számára."""
        return self.search_timer

    def on_search_text_changed(self, text: str) -> None:
        """Keresés szöveg változásának kezelése."""
        self.current_search_term = text.strip()

        if len(self.current_search_term) >= 2:  # noqa: PLR2004
            # Debounce: 300ms késleltetés
            self.search_timer.stop()
            self.search_timer.start(300)
        elif len(self.current_search_term) == 0:
            # Üres keresés esetén összes megjelenítése
            self.clear_search()
        else:
            self.search_timer.stop()

    def _trigger_search(self) -> None:
        """Keresés végrehajtása."""
        if not self.current_search_term:
            self.clear_search()
            return

        logger.debug(f"🔍 Keresés indítása: '{self.current_search_term}'")

        # Keresés a városok között
        search_term_lower = self.current_search_term.lower()
        self.filtered_cities = []

        for city in self.all_cities:
            if search_term_lower in city.city.lower():
                self.filtered_cities.append(city)

        # Régió szűrés alkalmazása a keresési eredményekre
        if self.current_region != "Összes":
            self.filtered_cities = HungarianRegions.get_cities_by_region(
                self.current_region, self.filtered_cities
            )

        # Callback-ek hívása
        self.populate_callback()
        self._update_search_stats()
        self.search_completed_signal.emit(len(self.filtered_cities))

        logger.info(f"✅ Keresés befejezve: {len(self.filtered_cities)} város találva")

    def clear_search(self) -> None:
        """Keresés törlése."""
        self.current_search_term = ""

        # Csak régió szűrés marad aktív
        if self.current_region != "Összes":
            self.filtered_cities = HungarianRegions.get_cities_by_region(
                self.current_region, self.all_cities
            )
        else:
            self.filtered_cities = []

        self.populate_callback()
        logger.debug("🧹 Keresés törölve")

    def on_region_changed(self, region: str) -> None:
        """Régió változás kezelése."""
        self.current_region = region
        logger.debug(f"🗺️ Régió váltás: {self.current_region}")

        # Szűrés alkalmazása
        if self.current_region == "Összes":
            if self.current_search_term:
                # Ha van keresési kifejezés, azt alkalmazzuk
                self._trigger_search()
            else:
                # Különben minden város
                self.filtered_cities = []
                self.populate_callback()
        else:
            # Régió alapú szűrés
            base_cities = self.all_cities

            # Ha van keresési kifejezés, először azt alkalmazzuk
            if self.current_search_term:
                search_term_lower = self.current_search_term.lower()
                base_cities = [
                    city for city in base_cities if search_term_lower in city.city.lower()
                ]

            # Régió szűrés
            self.filtered_cities = HungarianRegions.get_cities_by_region(
                self.current_region, base_cities
            )
            self.populate_callback()
            self._update_region_stats()

        # Signal - régió kiválasztás
        region_cities = self.filtered_cities if self.filtered_cities else self.all_cities
        self.region_selected_signal.emit(self.current_region, [city.city for city in region_cities])

    def get_filtered_cities(self) -> list[HungarianCity]:
        """Szűrt városok lekérdezése."""
        return self.filtered_cities if self.filtered_cities else self.all_cities

    def _update_search_stats(self) -> None:
        """Statisztika frissítése keresés után."""
        found_count = len(self.filtered_cities)
        stats_text = f"🔍 Keresési eredmények: {found_count} város található\nKeresési kifejezés: '{self.current_search_term}'\nRégió szűrés: {self.current_region}"
        self.stats_update_callback(stats_text)

    def _update_region_stats(self) -> None:
        """Statisztika frissítése régió szűrés után."""
        region_display = HungarianRegions.REGION_DISPLAY_NAMES.get(
            self.current_region, self.current_region
        )
        found_count = len(self.filtered_cities)
        stats_text = f"🗺️ Régió szűrés: {region_display}\n{found_count} város a régióban"
        if self.current_search_term:
            stats_text += f"\nKeresési kifejezés: '{self.current_search_term}'"
        self.stats_update_callback(stats_text)
