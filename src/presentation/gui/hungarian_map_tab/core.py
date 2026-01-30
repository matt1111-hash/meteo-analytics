"""
HungarianMapTab - Core implementation.

Ez a modul tartalmazza a HungarianMapTab fő osztályát és a signalokat.
"""

import logging
from typing import Any, Dict, Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget

logger = logging.getLogger(__name__)

# Mixins
# Analytics and data modules
from src.analytics.ports import get_multi_city_engine_port
from src.domain.entities.analytics_models import AnalyticsResult
from src.presentation.gui.color_palette import ColorPalette

# GUI modules
from src.presentation.gui.hungarian_location_selector import HungarianLocationSelector
from src.presentation.gui.map import HungarianMapVisualizer
from src.presentation.gui.weather_data_bridge import (
    WeatherDataBridge,
    WeatherOverlayData,
)

from .mixins import MapAnalyticsSyncMixin, MapTabUIMixin


class HungarianMapTab(MapTabUIMixin, MapAnalyticsSyncMixin, QWidget):
    """
    🗺️ Magyar Térképes Tab - Fő osztály.

    KOMPONENSEK:
    - HungarianLocationSelector: Hierarchikus lokáció választó
    - HungarianMapVisualizer: Folium interaktív térkép
    - WeatherDataBridge: Analytics → Folium konverzió
    - MultiCityEngine: Valós időjárási adatok

    SIGNALOK:
    - location_selected(location_data): Lokáció kiválasztva
    - county_clicked_on_map(county_name): Megye kattintva térképen
    - map_interaction(interaction_type, data): Térkép interakció
    - export_completed(file_path): Export befejezve
    - error_occurred(message): Hiba történt
    - folium_ready(): Folium térkép betöltve
    - weather_data_updated(overlay_data): Weather overlay frissítve
    - analytics_sync_completed(sync_type): Analytics sync befejezve
    """

    # Signalok
    location_selected = Signal(object)
    county_clicked_on_map = Signal(str)
    map_interaction = Signal(str, object)
    export_completed = Signal(str)
    error_occurred = Signal(str)
    data_loading_started = Signal()
    data_loading_completed = Signal()
    folium_ready = Signal()
    weather_data_updated = Signal(object)
    analytics_sync_completed = Signal(str)

    def __init__(self, parent=None):
        """HungarianMapTab inicializálása."""
        super().__init__(parent)

        # Komponens inicializálás
        self.color_palette = ColorPalette()

        # Komponens referenciák
        self.location_selector: Optional[HungarianLocationSelector] = None
        self.map_visualizer: Optional[HungarianMapVisualizer] = None

        # Weather integráció komponensek
        self.weather_bridge: Optional[WeatherDataBridge] = None
        self.multi_city_engine: Optional[MultiCityEngine] = None

        # Adatok
        self.counties_gdf = None
        self.current_location_data = None
        self.is_data_loaded = False
        self.is_folium_ready = False

        # Weather data állapot
        self.current_analytics_result: Optional[AnalyticsResult] = None
        self.current_weather_overlay: Optional[WeatherOverlayData] = None
        self.weather_data_available = False

        # Analytics paraméter memória
        self.current_analytics_parameter: Optional[str] = None

        # Analytics → Map Sync állapot
        self.last_analysis_parameters: Optional[Dict[str, Any]] = None
        self.last_weather_parameters: Optional[Dict[str, Any]] = None
        self.last_date_parameters: Optional[Dict[str, Any]] = None
        self.sync_in_progress = False
        self.auto_weather_refresh_enabled = True

        # Folium specifikus állapot
        self.current_theme = "light"
        self.auto_sync_enabled = True

        # Import the other modules
        from .actions import (
            _export_map,
            _on_auto_sync_toggled,
            _on_auto_weather_refresh_toggled,
            _refresh_folium_map,
            _reset_map_view,
        )
        from .folium_handlers import (
            on_county_selected,
            on_error_occurred,
            on_export_completed,
            on_folium_coordinates_clicked,
            on_folium_county_clicked,
            on_folium_county_hovered,
            on_folium_map_moved,
            on_folium_map_ready,
            on_location_selected,
            on_map_update_requested,
            on_selection_changed,
        )
        from .initialization import (
            initialize_components_steps,
            initialize_weather_components,
        )
        from .public_api import create_public_api_methods
        from .weather_integration import (
            _generate_weather_overlay_from_analytics,
            _refresh_weather_overlay,
            load_weather_data_from_analytics,
            set_analytics_parameter,
            set_analytics_result,
        )

        # UI építés
        self._setup_ui()
        self._setup_theme()
        self._connect_signals()

        # Weather komponensek inicializálása
        initialize_weather_components(self)

        # Kezdeti állapot
        initialize_components_steps(self)

        # Bind methods
        self.set_analytics_parameter = lambda param: set_analytics_parameter(self, param)
        self.set_analytics_result = lambda result: set_analytics_result(self, result)
        self._refresh_weather_overlay = lambda: _refresh_weather_overlay(self)
        self._generate_weather_overlay_from_analytics = lambda result: _generate_weather_overlay_from_analytics(self, result)
        self.load_weather_data_from_analytics = lambda *args, **kwargs: load_weather_data_from_analytics(self, *args, **kwargs)

        # Folium handlers
        self._on_county_selected = lambda *args: on_county_selected(self, *args)
        self._on_map_update_requested = lambda bounds: on_map_update_requested(self, bounds)
        self._on_location_selected = lambda location: on_location_selected(self, location)
        self._on_selection_changed = lambda: on_selection_changed(self)
        self._on_folium_map_ready = lambda: on_folium_map_ready(self)
        self._on_folium_county_clicked = lambda name: on_folium_county_clicked(self, name)
        self._on_folium_coordinates_clicked = lambda lat, lon: on_folium_coordinates_clicked(self, lat, lon)
        self._on_folium_map_moved = lambda lat, lon, zoom: on_folium_map_moved(self, lat, lon, zoom)
        self._on_folium_county_hovered = lambda name: on_folium_county_hovered(self, name)
        self._on_export_completed = lambda path: on_export_completed(self, path)
        self._on_error_occurred = lambda msg: on_error_occurred(self, msg)

        # Actions
        self._on_auto_sync_toggled = lambda enabled: _on_auto_sync_toggled(self, enabled)
        self._on_auto_weather_refresh_toggled = lambda enabled: _on_auto_weather_refresh_toggled(self, enabled)
        self._reset_map_view = lambda: _reset_map_view(self)
        self._export_map = lambda: _export_map(self)
        self._refresh_folium_map = lambda: _refresh_folium_map(self)

        # Public API methods
        create_public_api_methods(self)

        logger.info("🗺️ HungarianMapTab initialized")


# Export
__all__ = ["HungarianMapTab"]
