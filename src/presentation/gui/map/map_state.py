#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🗺️ Map State - Folium térkép konfiguráció és állapotkezelés.

FÁJL: src/presentation/gui/map/map_state.py
"""

from dataclasses import dataclass, field
from typing import Optional, List

from .map_constants import COUNTY_STYLE_DEFAULT


@dataclass
class FoliumMapConfig:
    """
    🗺️ Folium térkép konfigurációs beállítások.
    """
    # Alap térkép beállítások
    center_lat: float = 47.1625  # Magyarország közepe
    center_lon: float = 19.5033
    zoom_start: int = 7
    min_zoom: int = 6
    max_zoom: int = 12

    # Térkép stílus
    tiles: str = "OpenStreetMap"  # "OpenStreetMap", "CartoDB positron", "CartoDB dark_matter"
    attr: str = "Magyar Klímaanalitika"

    # County layer beállítások
    show_counties: bool = True
    county_fill_color: str = COUNTY_STYLE_DEFAULT['fillColor']
    county_fill_opacity: float = COUNTY_STYLE_DEFAULT['fillOpacity']
    county_border_color: str = COUNTY_STYLE_DEFAULT['color']
    county_border_weight: int = COUNTY_STYLE_DEFAULT['weight']
    county_hover_color: str = "#E74C3C"

    # Weather overlay
    weather_overlay: bool = False
    weather_opacity: float = 0.6

    # Active overlay parameter
    active_overlay_parameter: Optional[str] = None  # "temperature", "wind_speed", "precipitation"

    # Interaktivitás
    disable_scroll_zoom: bool = False
    dragging: bool = True
    touch_zoom: bool = True
    double_click_zoom: bool = True

    # Kiválasztott elemek
    selected_county: Optional[str] = None
    highlighted_counties: List[str] = field(default_factory=list)

    # Theme
    theme: str = "light"  # "light" vagy "dark"


@dataclass
class MapViewState:
    """
    🗺️ Térkép nézet állapota.
    """
    server_running: bool = False
    http_host: Optional[str] = None
    http_port: Optional[int] = None
    current_map_file: Optional[str] = None
    counties_loaded: bool = False
    weather_loaded: bool = False


@dataclass
class MapGenerationState:
    """
    🗺️ Térkép generálási állapota.
    """
    is_generating: bool = False
    progress: int = 0
    status_message: str = ""
    last_error: Optional[str] = None


# Export
__all__ = [
    'FoliumMapConfig',
    'MapViewState',
    'MapGenerationState',
]
