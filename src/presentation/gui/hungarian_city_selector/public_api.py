#!/usr/bin/env python3
# mypy: ignore-errors
# -*- coding: utf-8 -*-

"""
Hungarian City Selector - Public API Module
Publikus API metódusok a HungarianCitySelector osztályhoz.
"""

from src.presentation.gui.hungarian_city_selector.types import (
    HungarianCity,
    HungarianRegions,
)


class HungarianCityPublicAPIMixin:
    """Publikus API metódusok a HungarianCitySelector osztályhoz."""

    def get_loaded_cities_count(self) -> int:
        """Betöltött városok számának lekérdezése."""
        return len(self.hungarian_cities)

    def get_filtered_cities_count(self) -> int:
        """Szűrt városok számának lekérdezése."""
        return len(self.search_filter.get_filtered_cities())

    def get_current_region(self) -> str:
        """Jelenlegi régió lekérdezése."""
        return self.search_filter.current_region

    def get_current_search_term(self) -> str:
        """Jelenlegi keresési kifejezés lekérdezése."""
        return self.search_filter.current_search_term

    def set_region(self, region: str) -> None:
        """Régió programozott beállítása."""
        self.ui_builder.set_region(region)

    def set_search_term(self, search_term: str) -> None:
        """Keresési kifejezés programozott beállítása."""
        self.ui_builder.set_search_term(search_term)
        self.search_filter._trigger_search()

    def clear_all_filters(self) -> None:
        """Összes szűrő törlése."""
        self.set_region("Összes")
        self.set_search_term("")

    def get_city_by_name(self, city_name: str) -> HungarianCity | None:
        """
        Város keresése név alapján.

        Args:
            city_name: Város neve

        Returns:
            HungarianCity objektum vagy None
        """
        for city in self.hungarian_cities:
            if city.city.lower() == city_name.lower():
                return city
        return None

    def select_city_by_name(self, city_name: str) -> bool:
        """
        Város kiválasztása név alapján (programozott).

        Args:
            city_name: Város neve

        Returns:
            True, ha sikerült a kiválasztás
        """
        city = self.get_city_by_name(city_name)
        if city:
            self._emit_city_selected(city)
            return True
        return False

    def get_available_regions(self) -> list[str]:
        """Elérhető régiók listájának lekérdezése."""
        return HungarianRegions.get_all_regions()

    def get_cities_by_region_name(self, region: str) -> list[HungarianCity]:
        """
        Városok lekérdezése régió alapján.

        Args:
            region: Régió neve

        Returns:
            HungarianCity objektumok listája
        """
        return HungarianRegions.get_cities_by_region(region, self.hungarian_cities)
