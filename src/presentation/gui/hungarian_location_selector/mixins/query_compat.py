#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🗺️ Hungarian Location Selector - QueryControlWidget Compatibility
Magyar Klímaanalitika MVP - QueryControlWidget kompatibilitási réteg
"""

import logging
from typing import Any, Dict, Tuple

logger = logging.getLogger(__name__)


class QueryControlWidgetCompatMixin:
    """
    🔧 QueryControlWidget kompatibilitási mixin.
    """

    def get_current_city(self) -> str:
        """
        🔧 KRITIKUS: Jelenlegi város/megye név lekérdezése (QueryControlWidget kompatibilitás).

        A QueryControlWidget ezt a metódust hívja a _build_query_parameters() során.
        Defensive programming: mindig visszaad érvényes város nevet.

        Returns:
            str: Jelenlegi kiválasztott város/megye neve (MINDIG van érték!)
        """
        # 🔧 JAVÍTOTT: Debug logging a teljes state-ről
        if self._debug_enabled:
            logger.info("🔧 get_current_city() hívva - teljes state ellenőrzés:")
            logger.info(f"   current_county: {self.current_county}")
            logger.info(f"   current_region: {self.current_region}")
            logger.info(f"   current_location: {self.current_location}")
            logger.info(f"   county_combo current data: {self.county_combo.currentData()}")
            logger.info(f"   county_combo current text: {self.county_combo.currentText()}")

        # 0. EMERGENCY: UI alapú fallback - ami a combo-ban van kiválasztva
        current_county_data = self.county_combo.currentData()
        current_county_text = self.county_combo.currentText()
        if current_county_data and current_county_data != "Nincs kiválasztva" and not current_county_text.startswith("Válassz"):
            result = current_county_data
            if self._debug_enabled:
                logger.info(f"🚨 EMERGENCY get_current_city() UI-ból: {result}")
            return result

        # 1. Prioritás: Kiválasztott megye
        if self.current_county and isinstance(self.current_county, dict) and 'name' in self.current_county:
            result = self.current_county['name']
            if self._debug_enabled:
                logger.info(f"✅ get_current_city() visszaadja county: {result}")
            return result

        # 2. Fallback: Location objektum
        if self.current_location and hasattr(self.current_location, 'display_name'):
            result = self.current_location.display_name
            if self._debug_enabled:
                logger.info(f"✅ get_current_city() visszaadja location: {result}")
            return result

        # 3. Fallback: Régió adminisztratív központ
        if self.current_region and hasattr(self.current_region, 'administrative_center'):
            result = self.current_region.administrative_center
            if self._debug_enabled:
                logger.info(f"✅ get_current_city() visszaadja admin center: {result}")
            return result

        # 4. DESPERATE Fallback: region combo-ból
        region_data = self.region_combo.currentData()
        if region_data and region_data in self.region_data:
            result = self.region_data[region_data].administrative_center
            if self._debug_enabled:
                logger.info(f"🆘 DESPERATE get_current_city() region-ból: {result}")
            return result

        # 5. FINAL FALLBACK: Budapest mindig működik
        result = "Budapest"
        if self._debug_enabled:
            logger.warning(f"🆘 FINAL get_current_city() fallback: {result}")
        return result

    def get_current_coordinates(self) -> Tuple[float, float]:
        """
        🔧 ÚJ: Jelenlegi koordináták lekérdezése (QueryControlWidget kompatibilitás).

        QueryControlWidget ezt a metódust várja a _build_query_parameters() során.

        Returns:
            Tuple[float, float]: (latitude, longitude) koordináták
        """
        if self.current_county and 'centroid' in self.current_county:
            centroid = self.current_county['centroid']
            return (centroid.y, centroid.x)
        elif self.current_region:
            # Régió adminisztratív központjának közelítő koordinátái
            region_centers = {
                "kozep_magyarorszag": (47.4979, 19.0402),  # Budapest
                "kozep_dunantul": (47.1903, 18.4148),     # Székesfehérvár
                "nyugat_dunantul": (47.6875, 17.6504),    # Győr
                "del_dunantul": (46.0727, 18.2330),       # Pécs
                "eszak_magyarorszag": (48.1034, 20.7784), # Miskolc
                "eszak_alfold": (47.5316, 21.6273),       # Debrecen
                "del_alfold": (46.2530, 20.1414)          # Szeged
            }
            return region_centers.get(self.current_region.name, (47.4979, 19.0402))
        else:
            # Default Budapest koordináták
            return (47.4979, 19.0402)

    def get_selected_location_data(self) -> Dict[str, Any]:
        """
        🔧 ÚJ: Kiválasztott lokáció adatok lekérdezése (QueryControlWidget kompatibilitás).

        QueryControlWidget fallback esetén ezt használja az is_valid() ellenőrzéshez.

        Returns:
            Dict[str, Any]: Lokáció adatok és validálási információk
        """
        if self.current_location:
            return {
                "valid": True,
                "city": self.current_location.display_name,
                "latitude": self.current_location.latitude,
                "longitude": self.current_location.longitude,
                "region": self.current_region.display_name if self.current_region else None,
                "county": self.current_county['name'] if self.current_county else None,
                "source": "hungarian_location_selector"
            }
        elif self.current_county:
            lat, lon = self.get_current_coordinates()
            return {
                "valid": True,
                "city": self.current_county['name'],
                "latitude": lat,
                "longitude": lon,
                "region": self.current_region.display_name if self.current_region else None,
                "county": self.current_county['name'],
                "source": "hungarian_location_selector"
            }
        elif self.current_region:
            lat, lon = self.get_current_coordinates()
            return {
                "valid": True,
                "city": self.current_region.administrative_center,
                "latitude": lat,
                "longitude": lon,
                "region": self.current_region.display_name,
                "county": None,
                "source": "hungarian_location_selector"
            }
        else:
            return {
                "valid": False,
                "city": None,
                "latitude": None,
                "longitude": None,
                "region": None,
                "county": None,
                "source": "hungarian_location_selector"
            }

    def is_valid(self) -> bool:
        """
        🔧 ÚJ: Widget validálása (QueryControlWidget kompatibilitás).

        Returns:
            bool: True ha van kiválasztott régió vagy megye
        """
        return self.current_region is not None

    def set_enabled(self, enabled: bool) -> None:
        """
        🔧 ÚJ: Widget engedélyezése/letiltása (QueryControlWidget kompatibilitás).

        Args:
            enabled: Engedélyezett állapot
        """
        self.region_combo.setEnabled(enabled)
        if self.counties_gdf is not None:
            self.county_combo.setEnabled(enabled and self.current_region is not None)
        self.refresh_btn.setEnabled(enabled)
        if self.current_county is not None:
            self.center_map_btn.setEnabled(enabled)
