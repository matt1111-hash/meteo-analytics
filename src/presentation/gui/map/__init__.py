#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
from .map_visualizer import HungarianMapVisualizer
from .map_state import FoliumMapConfig
from .map_interactions import JavaScriptBridge, LocalHttpServerThread
from .folium_renderer import FoliumMapGenerator

# Constants (optional re-export)
from .map_constants import (
    HUNGARY_CENTER,
    COLOR_SCALE_GRADIENTS,
    OVERLAY_COLOR_MAPPING,
    get_beaufort_color,
    get_precipitation_color,
    get_gradient_for_overlay,
)

__all__ = [
    # Main widget
    'HungarianMapVisualizer',
    # Configuration
    'FoliumMapConfig',
    # Interactions
    'JavaScriptBridge',
    'LocalHttpServerThread',
    # Renderer
    'FoliumMapGenerator',
    # Constants
    'HUNGARY_CENTER',
    'COLOR_SCALE_GRADIENTS',
    'OVERLAY_COLOR_MAPPING',
    'get_beaufort_color',
    'get_precipitation_color',
    'get_gradient_for_overlay',
]
