#!/usr/bin/env python3
# mypy: ignore-errors
# -*- coding: utf-8 -*-

"""
🗺️ Hungarian Location Selector - QueryControlWidget Compatibility
Magyar Klímaanalitika MVP - QueryControlWidget kompatibilitási réteg
"""

import logging
from typing import Any, Dict, Tuple

logger = logging.getLogger(__name__)


def _log_debug_state(widget: Any) -> None:
    """Log the current widget state when debug is enabled."""
    if not widget._debug_enabled:
        return
    logger.info("🔧 get_current_city() hívva - teljes state ellenőrzés:")
    logger.info(f"   current_county: {widget.current_county}")
    logger.info(f"   current_region: {widget.current_region}")
    logger.info(f"   current_location: {widget.current_location}")
    logger.info(f"   county_combo current data: {widget.county_combo.currentData()}")
    logger.info(f"   county_combo current text: {widget.county_combo.currentText()}")


def _log_city_choice(widget: Any, prefix: str, result: str, level: str = "info") -> str:
    """Log and return the selected city result."""
    if widget._debug_enabled:
        getattr(logger, level)(f"{prefix}: {result}")
    return result


def _get_ui_selected_county(widget: Any) -> str | None:
    """Return the county currently visible in the combo box."""
    current_county_data = widget.county_combo.currentData()
    current_county_text = widget.county_combo.currentText()
    if (
        current_county_data
        and current_county_data != "Nincs kiválasztva"
        and not current_county_text.startswith("Válassz")
    ):
        return current_county_data
    return None


def _get_region_admin_center(widget: Any) -> str | None:
    """Return the administrative center from the active region."""
    if widget.current_region and hasattr(
        widget.current_region, "administrative_center"
    ):
        return widget.current_region.administrative_center
    region_data = widget.region_combo.currentData()
    if region_data and region_data in widget.region_data:
        return widget.region_data[region_data].administrative_center
    return None


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
        _log_debug_state(self)
        current_county_data = _get_ui_selected_county(self)
        if current_county_data:
            return _log_city_choice(
                self, "🚨 EMERGENCY get_current_city() UI-ból", current_county_data
            )

        if (
            self.current_county
            and isinstance(self.current_county, dict)
            and "name" in self.current_county
        ):
            return _log_city_choice(
                self,
                "✅ get_current_city() visszaadja county",
                self.current_county["name"],
            )

        if self.current_location and hasattr(self.current_location, "display_name"):
            return _log_city_choice(
                self,
                "✅ get_current_city() visszaadja location",
                self.current_location.display_name,
            )

        admin_center = _get_region_admin_center(self)
        if admin_center:
            return _log_city_choice(
                self, "✅ get_current_city() visszaadja admin center", admin_center
            )

        return _log_city_choice(
            self, "🆘 FINAL get_current_city() fallback", "Budapest", level="warning"
        )

    def get_current_coordinates(self) -> Tuple[float, float]:
        """
        🔧 ÚJ: Jelenlegi koordináták lekérdezése (QueryControlWidget kompatibilitás).

        QueryControlWidget ezt a metódust várja a _build_query_parameters() során.

        Returns:
            Tuple[float, float]: (latitude, longitude) koordináták
        """
        if self.current_county and "centroid" in self.current_county:
            centroid = self.current_county["centroid"]
            return (centroid.y, centroid.x)
        elif self.current_region:
            # Régió adminisztratív központjának közelítő koordinátái
            region_centers = {
                "kozep_magyarorszag": (47.4979, 19.0402),  # Budapest
                "kozep_dunantul": (47.1903, 18.4148),  # Székesfehérvár
                "nyugat_dunantul": (47.6875, 17.6504),  # Győr
                "del_dunantul": (46.0727, 18.2330),  # Pécs
                "eszak_magyarorszag": (48.1034, 20.7784),  # Miskolc
                "eszak_alfold": (47.5316, 21.6273),  # Debrecen
                "del_alfold": (46.2530, 20.1414),  # Szeged
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
                "region": self.current_region.display_name
                if self.current_region
                else None,
                "county": self.current_county["name"] if self.current_county else None,
                "source": "hungarian_location_selector",
            }
        elif self.current_county:
            lat, lon = self.get_current_coordinates()
            return {
                "valid": True,
                "city": self.current_county["name"],
                "latitude": lat,
                "longitude": lon,
                "region": self.current_region.display_name
                if self.current_region
                else None,
                "county": self.current_county["name"],
                "source": "hungarian_location_selector",
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
                "source": "hungarian_location_selector",
            }
        else:
            return {
                "valid": False,
                "city": None,
                "latitude": None,
                "longitude": None,
                "region": None,
                "county": None,
                "source": "hungarian_location_selector",
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
