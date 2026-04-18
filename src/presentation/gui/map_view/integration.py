#!/usr/bin/env python3
# mypy: ignore-errors
# -*- coding: utf-8 -*-

"""
Map View - Integration

🔗 Külső integráció és advanced Folium features

Képességek:
- Külső lokáció kiválasztás kezelése
- Megye kattintás kezelése
- Integráció státusz lekérdezése
- Advanced Folium features

Fájl: src/presentation/gui/map_view/integration.py
"""

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class MapViewIntegrationMixin:
    """
    Külső integráció és advanced features kezelése.

    Ez a mixin osztály tartalmazza a külső integrációs
    és advanced Folium feature metódusokat.
    """

    # These will be set when mixed into MapView
    map_tab: Any

    def get_javascript_bridge(self):
        """
        🌉 JavaScript bridge referencia lekérdezése (delegált).

        Returns:
            JavaScriptBridge példány vagy None
        """
        map_visualizer = self.get_map_visualizer()
        if map_visualizer:
            return map_visualizer.get_javascript_bridge()
        return None

    def refresh_folium_map(self) -> None:
        """
        🗺️ Folium térkép manuális újragenerálása (delegált).
        """
        if self.map_tab:
            self.map_tab._refresh_folium_map()

    # === KÜLSŐ INTEGRÁCIÓ TÁMOGATÁS ===

    def update_from_location_selection(self, location_data: dict[str, Any]) -> None:
        """
        📍 Külső lokáció kiválasztás alapján frissítés.

        Args:
            location_data: Lokáció adatok (pl. MainWindow ControlPanel-től)
        """
        county_name = location_data.get("county") or location_data.get("name")

        if county_name and self.focus_on_county(county_name):
            logger.debug("Folium map focused on county from external selection: %s", county_name)
        else:
            logger.debug(
                "Could not focus Folium map on county from external selection: %s", county_name
            )

    def handle_external_county_click(self, county_name: str) -> None:
        """
        🖱️ Külső megye kattintás kezelése (pl. analytics view-ból).

        Args:
            county_name: Kattintott megye neve
        """
        if self.focus_on_county(county_name):
            logger.debug("Folium map focused on external county click: %s", county_name)

            # Location selector szinkronizáció
            location_selector = self.get_location_selector()
            if location_selector:
                location_selector.set_county(county_name)
        else:
            logger.debug("Could not handle external county click: %s", county_name)

    def get_integration_status(self) -> dict[str, Any]:
        """
        📊 Folium integráció státusz információk lekérdezése.

        Returns:
            Integráció státusz dictionary
        """
        if self.map_tab:
            status = self.map_tab.get_integration_status()

            # Kiegészítés MapView specifikus infókkal
            status.update(
                {
                    "map_view_ready": True,
                    "javascript_bridge_available": self.get_javascript_bridge() is not None,
                    "folium_map_visualizer_available": self.get_map_visualizer() is not None,
                    "external_integration_ready": self.is_folium_ready(),
                }
            )
        else:
            status = {
                "map_view_ready": False,
                "map_tab_available": False,
                "error": "HungarianMapTab not initialized",
            }

        return status

    # === ADVANCED FOLIUM FEATURES ===

    def highlight_counties(self, county_names: list) -> None:
        """
        ✨ Megyék kiemelése a Folium térképen (delegált).

        Args:
            county_names: Kiemelendő megyék nevei
        """
        map_visualizer = self.get_map_visualizer()
        if map_visualizer:
            map_visualizer.highlight_counties(county_names)
            logger.debug("Highlighted counties on Folium map: %s", county_names)

    def set_selected_county(self, county_name: str) -> None:
        """
        🎯 Kiválasztott megye beállítása Folium térképen (delegált).

        Args:
            county_name: Megye neve
        """
        map_visualizer = self.get_map_visualizer()
        if map_visualizer:
            map_visualizer.set_selected_county(county_name)
            logger.debug("Selected county set on Folium map: %s", county_name)

    def toggle_weather_overlay(self, enabled: bool) -> None:
        """
        🌤️ Időjárási overlay ki/bekapcsolása (delegált).

        Args:
            enabled: Engedélyezett-e az overlay
        """
        map_visualizer = self.get_map_visualizer()
        if map_visualizer:
            map_visualizer.toggle_weather_overlay(enabled)
            logger.debug("Folium weather overlay %s", "enabled" if enabled else "disabled")

    def get_folium_map_config(self):
        """
        📋 Folium térkép konfiguráció lekérdezése (delegált).

        Returns:
            FoliumMapConfig objektum vagy None
        """
        map_visualizer = self.get_map_visualizer()
        if map_visualizer:
            return map_visualizer.get_map_config()
        return None

    # === TÉMA INTEGRÁCIÓ ===

    def apply_theme(self, theme_name: str) -> None:
        """
        🎨 Téma alkalmazása a teljes Folium térképes komponensre.

        Args:
            theme_name: Téma neve ("light" vagy "dark")
        """
        # ThemeManager automatikusan kezeli a regisztrált widget-eket
        # Folium map style frissítése téma alapján
        self.set_theme(theme_name)

        logger.debug("MapView Folium theme applied: %s", theme_name)
