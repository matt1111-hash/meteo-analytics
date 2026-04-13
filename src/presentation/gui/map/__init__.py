#!/usr/bin/env python3
# mypy: ignore-errors

"""
🗺️ Map Visualizer - Folium térkép vizualizáló modul.

Modul struktúra:
- map_constants: Konstansok és színskálák
- map_state: Konfigurációs és állapot osztályok
- html_generator: HTML legend generátorok
- overlay_manager: Időjárási overlay kezelők
- layer_builder: Térkép layer építők
- folium_renderer: Folium térkép generáló
- map_interactions: JavaScript híd és HTTP szerver
- map_visualizer: Fő vizualizáló widget

FÁJL: src/presentation/gui/map/__init__.py
"""

# Re-export public API
from .folium_renderer import FoliumMapGenerator

# Constants (optional re-export)
from .map_constants import (
    COLOR_SCALE_GRADIENTS,
    HUNGARY_CENTER,
    OVERLAY_COLOR_MAPPING,
    get_beaufort_color,
    get_gradient_for_overlay,
    get_precipitation_color,
)
from .map_interactions import JavaScriptBridge, LocalHttpServerThread
from .map_state import FoliumMapConfig
from .map_visualizer import HungarianMapVisualizer

__all__ = [
    "COLOR_SCALE_GRADIENTS",
    # Constants
    "HUNGARY_CENTER",
    "OVERLAY_COLOR_MAPPING",
    # Configuration
    "FoliumMapConfig",
    # Renderer
    "FoliumMapGenerator",
    # Main widget
    "HungarianMapVisualizer",
    # Interactions
    "JavaScriptBridge",
    "LocalHttpServerThread",
    "get_beaufort_color",
    "get_gradient_for_overlay",
    "get_precipitation_color",
]
