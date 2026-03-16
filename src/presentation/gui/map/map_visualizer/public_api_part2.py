# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Split definitions from public_api.py."""

from __future__ import annotations

from .public_api_support import *


def set_map_style(self, style: str) -> None:
    """
    🎨 Map stílus beállítása.

    Args:
        self: HungarianMapVisualizer instance
        style: Stílus név (light, bright, dark, night)
    """
    if style in ["light", "bright"]:
        map_style = "CartoDB positron"
    elif style in ["dark", "night"]:
        map_style = "CartoDB dark_matter"
    else:
        map_style = "OpenStreetMap"

    self.style_combo.setCurrentText(map_style)
    self.map_config.tiles = map_style
    self.map_config.theme = style


def toggle_counties(self, show: bool) -> None:
    """
    Megyehatárok ki/be kapcsolása.

    Args:
        self: HungarianMapVisualizer instance
        show: True ha látható, False ha nem
    """
    self.counties_check.setChecked(show)


def toggle_weather_overlay(self, show: bool) -> None:
    """
    Időjárás overlay ki/be kapcsolása.

    Args:
        self: HungarianMapVisualizer instance
        show: True ha látható, False ha nem
    """
    self.weather_check.setChecked(show)


def set_selected_county(self, county_name: str) -> None:
    """
    Kiválasztott megye beállítása.

    Args:
        self: HungarianMapVisualizer instance
        county_name: Megye név
    """
    self.map_config.selected_county = county_name
    self._start_map_generation()


def highlight_counties(self, county_names: List[str]) -> None:
    """
    Megyék kiemelése.

    Args:
        self: HungarianMapVisualizer instance
        county_names: Megye nevek listája
    """
    self.map_config.highlighted_counties = county_names


def is_folium_available(self) -> bool:
    """
    Folium elérhetőségének ellenőrzése.

    Args:
        self: HungarianMapVisualizer instance

    Returns:
        bool: True ha folium elérhető
    """
    try:
        import folium  # noqa: F401

        return True
    except ImportError:
        return False


def get_javascript_bridge(self):
    """
    JavaScript bridge lekérdezése.

    Args:
        self: HungarianMapVisualizer instance

    Returns:
        JavaScriptBridge: JS bridge objektum
    """
    return self.js_bridge


def get_current_map_file(self) -> Optional[str]:
    """
    Aktuális map fájl útvonal lekérdezése.

    Args:
        self: HungarianMapVisualizer instance

    Returns:
        Optional[str]: Map fájl útvonal vagy None
    """
    return self.current_map_file
