#!/usr/bin/env python3
# mypy: ignore-errors

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
from PySide6.QtWidgets import QWidget

from src.presentation.gui.color_palette import ColorPalette
from src.presentation.gui.runtime_environment import is_headless_qt_platform
from src.presentation.gui.theme_manager import register_widget_for_theming

from ..map_interactions import JavaScriptBridge
from ..map_state import FoliumMapConfig
from .server_handler import _show_folium_error, start_local_server
from .signal_handlers import connect_signals

# Mixin imports
from .ui_builder import setup_map_visualizer_ui, setup_web_view

try:
    import folium  # noqa: F401

    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False


# Import signal handler methods and attach to class
# Import map generation methods
from .map_generation import (
    _generate_default_map,
    _load_map_from_http_url,
    _on_map_error,
    _on_map_generated,
    _start_map_generation,
)

# Import public API methods
from .public_api import (
    clear_active_overlay_parameter,
    get_active_overlay_parameter,
    get_current_map_file,
    get_javascript_bridge,
    get_map_config,
    highlight_counties,
    is_folium_available,
    reset_map_view,
    set_active_overlay_parameter,
    set_counties_geodataframe,
    set_map_style,
    set_selected_county,
    set_weather_data,
    toggle_counties,
    toggle_weather_overlay,
    update_map_bounds,
)

# Import server handler methods
from .server_handler import (
    _on_server_error,
    _on_server_ready,
)
from .signal_handlers import (
    _export_map,
    _on_counties_toggled,
    _on_js_coordinates_clicked,
    _on_js_county_clicked,
    _on_js_county_hovered,
    _on_js_map_moved,
    _on_map_loaded,
    _on_style_changed,
    _on_weather_toggled,
    _on_zoom_changed,
    _refresh_map,
)


class HungarianMapVisualizer(QWidget):
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

    def __init__(self, parent=None):  # noqa: D107
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
        if not is_headless_qt_platform():
            start_local_server(self)

        if not FOLIUM_AVAILABLE:
            _show_folium_error(self)

    def cleanup(self) -> None:
        """Leállítja a térképhez tartozó háttérszálakat."""
        if self.map_generator and self.map_generator.isRunning():
            self.map_generator.quit()
            if not self.map_generator.wait(3000):
                self.map_generator.terminate()
                self.map_generator.wait(1000)

        if self.local_server:
            if self.local_server.running:
                self.local_server.stop()
            if self.local_server.isRunning():
                self.local_server.quit()
                if not self.local_server.wait(3000):
                    self.local_server.terminate()
                    self.local_server.wait(1000)

    def closeEvent(self, event) -> None:
        """Widget bezárása előtt felszabadítja a háttér erőforrásokat."""
        self.cleanup()
        super().closeEvent(event)


# Attach imported methods as class methods
HungarianMapVisualizer._on_style_changed = _on_style_changed
HungarianMapVisualizer._on_counties_toggled = _on_counties_toggled
HungarianMapVisualizer._on_weather_toggled = _on_weather_toggled
HungarianMapVisualizer._on_zoom_changed = _on_zoom_changed
HungarianMapVisualizer._on_js_county_clicked = _on_js_county_clicked
HungarianMapVisualizer._on_js_coordinates_clicked = _on_js_coordinates_clicked
HungarianMapVisualizer._on_js_map_moved = _on_js_map_moved
HungarianMapVisualizer._on_js_county_hovered = _on_js_county_hovered
HungarianMapVisualizer._refresh_map = _refresh_map
HungarianMapVisualizer._export_map = _export_map
HungarianMapVisualizer._on_map_loaded = _on_map_loaded

HungarianMapVisualizer.set_active_overlay_parameter = set_active_overlay_parameter
HungarianMapVisualizer.clear_active_overlay_parameter = clear_active_overlay_parameter
HungarianMapVisualizer.get_active_overlay_parameter = get_active_overlay_parameter
HungarianMapVisualizer.set_counties_geodataframe = set_counties_geodataframe
HungarianMapVisualizer.set_weather_data = set_weather_data
HungarianMapVisualizer.update_map_bounds = update_map_bounds
HungarianMapVisualizer.get_map_config = get_map_config
HungarianMapVisualizer.reset_map_view = reset_map_view
HungarianMapVisualizer.set_map_style = set_map_style
HungarianMapVisualizer.toggle_counties = toggle_counties
HungarianMapVisualizer.toggle_weather_overlay = toggle_weather_overlay
HungarianMapVisualizer.set_selected_county = set_selected_county
HungarianMapVisualizer.highlight_counties = highlight_counties
HungarianMapVisualizer.is_folium_available = is_folium_available
HungarianMapVisualizer.get_javascript_bridge = get_javascript_bridge
HungarianMapVisualizer.get_current_map_file = get_current_map_file

HungarianMapVisualizer._generate_default_map = _generate_default_map
HungarianMapVisualizer._start_map_generation = _start_map_generation
HungarianMapVisualizer._on_map_generated = _on_map_generated
HungarianMapVisualizer._load_map_from_http_url = _load_map_from_http_url
HungarianMapVisualizer._on_map_error = _on_map_error

HungarianMapVisualizer.start_local_server = start_local_server
HungarianMapVisualizer._on_server_ready = _on_server_ready
HungarianMapVisualizer._on_server_error = _on_server_error
HungarianMapVisualizer._show_folium_error = _show_folium_error
