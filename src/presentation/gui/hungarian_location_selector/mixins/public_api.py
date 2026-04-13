#!/usr/bin/env python3
# mypy: ignore-errors
# -*- coding: utf-8 -*-

"""
🗺️ Hungarian Location Selector - Public API
Magyar Klímaanalitika MVP - Publikus API metódusok
"""

from typing import Any

from ..models import HungarianRegionData


class PublicApiMixin:
    """
    📋 Publikus API mixin a HungarianLocationSelector számára.
    """

    def get_current_selection(self) -> dict[str, Any]:
        """
        📋 Jelenlegi kiválasztott elemek lekérdezése.
        """
        return {
            "region": self.current_region,
            "county": self.current_county,
            "location": self.current_location,
            "has_geodata": self.counties_gdf is not None,
        }

    def set_region(self, region_key: str) -> bool:
        """
        🏛️ Régió programmatic beállítása - JAVÍTOTT (statisztikai régió támogatás)!
        """
        for i in range(self.region_combo.count()):
            if self.region_combo.itemData(i) == region_key:
                self.region_combo.setCurrentIndex(i)
                return True
        return False

    def set_county(self, county_name: str) -> bool:
        """
        🗺️ Megye programmatic beállítása.
        """
        for i in range(self.county_combo.count()):
            if self.county_combo.itemData(i) == county_name:
                self.county_combo.setCurrentIndex(i)
                return True
        return False

    def get_available_counties(self) -> list[str]:
        """
        📋 Elérhető megyék listája.
        """
        if self.counties_gdf is None:
            return []

        return sorted(self.counties_gdf["megye"].tolist())

    def get_counties_geodataframe(self):
        """
        🗺️ Megyék GeoDataFrame lekérdezése.
        """
        return self.counties_gdf

    def get_postal_codes_geodataframe(self):
        """
        📫 Irányítószám területek GeoDataFrame lekérdezése.
        """
        return self.postal_codes_gdf

    def reset_selection(self):
        """
        🔄 Kiválasztás visszaállítása.
        """
        self.region_combo.setCurrentIndex(0)
        self.county_combo.setCurrentIndex(0)

        self.current_region = None
        self.current_county = None
        self.current_location = None

        self.region_info.clear()
        self._update_location_info()
        self._update_debug_display()

        self.selection_changed.emit()

    # === 🔧 JAVÍTOTT: RÉGIÓ KOMPATIBILITÁSI METÓDUSOK ===

    def get_region_by_display_name(self, display_name: str) -> HungarianRegionData | None:
        """
        🔧 ÚJ: Régió lekérdezése megjelenítési név alapján (Control Panel kompatibilitás).

        Args:
            display_name: Régió megjelenítési neve (pl. "Észak-Magyarország")

        Returns:
            HungarianRegionData objektum vagy None
        """
        for region_data in self.region_data.values():
            if region_data.display_name == display_name:
                return region_data
        return None

    def set_region_by_display_name(self, display_name: str) -> bool:
        """
        🔧 ÚJ: Régió beállítása megjelenítési név alapján (Control Panel kompatibilitás).

        Args:
            display_name: Régió megjelenítési neve (pl. "Észak-Magyarország")

        Returns:
            Sikeres volt-e a beállítás
        """
        region_data = self.get_region_by_display_name(display_name)
        if region_data:
            return self.set_region(region_data.name)
        return False

    def get_available_region_display_names(self) -> list[str]:
        """
        🔧 ÚJ: Elérhető régió megjelenítési nevek listája (Control Panel kompatibilitás).

        Returns:
            Régió megjelenítési nevek listája
        """
        return [region_data.display_name for region_data in self.region_data.values()]

    def get_region_counties_mapping(self) -> dict[str, list[str]]:
        """
        🔧 ÚJ: Régió → megyék mapping (Multi-City Engine kompatibilitás).

        Returns:
            {régió_megjelenítési_név: [megyék_listája]} dictionary
        """
        return {
            region_data.display_name: region_data.counties
            for region_data in self.region_data.values()
        }
