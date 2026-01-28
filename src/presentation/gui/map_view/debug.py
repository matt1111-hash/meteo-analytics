#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Map View - Debug

🐛 Debug információk és monitoring

Képességek:
- Debug információk összegyűjtése
- Integráció státusz lekérdezése
- JavaScript bridge infó
- Folium config infó

Fájl: src/presentation/gui/map_view/debug.py
"""

from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    pass


class MapViewDebugMixin:
    """
    Debug információk kezelése.

    Ez a mixin osztály tartalmazza a debug és monitoring
    metódusokat.
    """

    def get_debug_info(self) -> Dict[str, Any]:
        """
        🐛 Debug információk összegyűjtése.

        Returns:
            Debug információk dictionary
        """
        debug_info = {
            "map_view_initialized": self.map_tab is not None,
            "integration_status": self.get_integration_status(),
            "folium_ready": self.is_folium_ready(),
            "current_location": self.get_current_location(),
            "available_counties": len(self.get_available_counties()),
            "map_status": self.get_map_status()
        }

        # JavaScript Bridge info
        js_bridge = self.get_javascript_bridge()
        if js_bridge:
            debug_info["javascript_bridge_id"] = js_bridge.bridge_id

        # Folium Map Config info
        folium_config = self.get_folium_map_config()
        if folium_config:
            debug_info["folium_config"] = {
                "center_lat": folium_config.center_lat,
                "center_lon": folium_config.center_lon,
                "zoom_start": folium_config.zoom_start,
                "tiles": folium_config.tiles,
                "theme": folium_config.theme,
                "weather_overlay": folium_config.weather_overlay
            }

        return debug_info
