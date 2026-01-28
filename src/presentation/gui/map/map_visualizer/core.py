#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Map Visualizer - Core

🗺️ HungarianMapVisualizer main class

Képességek:
- Main HungarianMapVisualizer class
- Signal definíciók
- Inicializáció
- Mixin metódusok összekötése

Fájl: src/presentation/gui/map/map_visualizer/core.py
"""


from PySide6.QtCore import Signal
from PySide6.QtWebChannel import QWebChannel

from ..color_palette import ColorPalette
from ..theme_manager import register_widget_for_theming
from .map_interactions import JavaScriptBridge
from .map_state import FoliumMapConfig
from .server_handler import _show_folium_error, start_local_server
from .signal_handlers import connect_signals

# Mixin imports
from .ui_builder import setup_map_visualizer_ui, setup_web_view

try:
    import folium  # noqa: F401
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False


class HungarianMapVisualizer(
    # Mixin classes
    object
):
    """
    🗺️ Magyar Folium térkép vizualizáló widget - HELYI HTTP SZERVER VERZIÓ v3.0

    SIGNALOK:
    - map_ready(): Térkép betöltve és kész
    - county_clicked(county_name): Megyére kattintás
    - coordinates_clicked(lat, lon): Koordináta kattintás
    - export_completed(file_path): Export befejezve
    - error_occurred(message): Hiba történt
    """

    map_ready = Signal()
    county_clicked = Signal(str)
    coordinates_clicked = Signal(float, float)
    map_moved = Signal(float, float, int)
    county_hovered = Signal(str)
    export_completed = Signal(str)
    error_occurred = Signal(str)
    bounds_changed = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.color_palette = ColorPalette()
        self.map_config = FoliumMapConfig()
        self.counties_gdf = None
        self.current_weather_data = None

        self.local_server = None
        self.http_host = None
        self.http_port = None
        self.current_map_file = None
        self.map_generator = None

        self.js_bridge = JavaScriptBridge()
        self.web_channel = QWebChannel()

        setup_map_visualizer_ui(self)
        setup_web_view(self)
        register_widget_for_theming(self, "container")
        connect_signals(self)
        start_local_server(self)

        if not FOLIUM_AVAILABLE:
            _show_folium_error(self)
