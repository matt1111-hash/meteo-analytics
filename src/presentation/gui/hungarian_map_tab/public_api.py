# mypy: ignore-errors
"""
Public API methods for HungarianMapTab.

Ez a modul tartalmazza a publikus API metódusokat.
"""

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


def create_public_api_methods(self) -> None:  # noqa: C901, PLR0915
    """Publikus API metódusok létrehozása."""

    def get_location_selector() -> Optional:
        return self.location_selector

    def get_map_visualizer() -> Optional:
        return self.map_visualizer

    def get_weather_bridge() -> Optional:
        return self.weather_bridge

    def get_multi_city_engine() -> Optional:
        return self.multi_city_engine

    def get_current_analytics_result() -> Optional:
        return self.current_analytics_result

    def get_current_weather_overlay() -> Optional:
        return self.current_weather_overlay

    def get_current_analytics_parameter() -> str | None:
        return self.current_analytics_parameter

    def has_weather_data() -> bool:
        return self.weather_data_available and self.current_weather_overlay is not None

    def get_current_location():
        return self.current_location_data

    def get_counties_geodataframe():
        return self.counties_gdf

    def set_region_and_county(region_key: str, county_name: str) -> bool:
        if not self.location_selector:
            return False
        region_success = self.location_selector.set_region(region_key)
        if not region_success:
            return False
        county_success = self.location_selector.set_county(county_name)
        return county_success

    def focus_on_county(county_name: str) -> bool:
        if self.counties_gdf is None:
            return False
        try:
            county_row = self.counties_gdf[self.counties_gdf["megye"] == county_name]
            if county_row.empty:
                return False
            geometry = county_row.geometry.iloc[0]
            bounds = geometry.bounds
            if self.map_visualizer and self.is_folium_ready:
                self.map_visualizer.update_map_bounds(bounds)
                self.map_visualizer.set_selected_county(county_name)
                return True
        except Exception as e:
            print(f"❌ DEBUG: Focus on county error: {e}")
        return False

    def get_available_counties() -> list[str]:
        if self.location_selector:
            return self.location_selector.get_available_counties()
        return []

    def get_map_status() -> str:
        return self.loading_status.text()

    def is_ready() -> bool:
        return (
            self.is_data_loaded
            and self.location_selector is not None
            and self.map_visualizer is not None
            and self.counties_gdf is not None
            and self.is_folium_ready
            and self.weather_bridge is not None
            and self.multi_city_engine is not None
        )

    def is_folium_ready_status() -> bool:
        return self.is_folium_ready

    def set_theme(theme: str) -> None:
        self.current_theme = theme
        if self.map_visualizer:
            self.map_visualizer.set_map_style(theme)
            print(f"🎨 DEBUG: Folium theme set to: {theme}")

    def set_weather_data(weather_data: dict[str, Any]) -> None:
        if self.map_visualizer:
            self.map_visualizer.set_weather_data(weather_data)
            print("🌤️ DEBUG: Weather data set for Folium overlay (legacy method)")

    def refresh_all_components() -> None:
        print("🔄 DEBUG: Refreshing all HungarianMapTab components")
        if self.location_selector:
            self.location_selector._start_data_loading()
        if self.map_visualizer:
            self.map_visualizer._refresh_map()
        if self.current_analytics_result:
            from .weather_integration import (
                _generate_weather_overlay_from_analytics,
            )

            _generate_weather_overlay_from_analytics(self, self.current_analytics_result)
        self.loading_status.setText("🔄 Folium komponensek frissítve...")

    def clear_selection() -> None:
        print("🧹 DEBUG: Clearing all selections in HungarianMapTab")
        if self.location_selector:
            self.location_selector.reset_selection()
        if self.map_visualizer:
            self.map_visualizer.reset_map_view()
        self.current_analytics_result = None
        self.current_weather_overlay = None
        self.weather_data_available = False
        self.current_analytics_parameter = None
        self.analytics_parameter_label.setText("🧠 Paraméter: Nincs")
        self.analytics_parameter_label.setStyleSheet("color: #95A5A6;")
        self.last_analysis_parameters = None
        self.last_weather_parameters = None
        self.last_date_parameters = None
        self.weather_status_label.setText("🌤️ Weather: Nincs adat")
        self.weather_status_label.setStyleSheet("color: #E74C3C;")
        self.analytics_sync_label.setText("🔄 Analytics Sync: Kész")
        self.analytics_sync_label.setStyleSheet("color: #27AE60;")
        self.current_location_data = None
        self.loading_status.setText("🧹 Kiválasztás törölve")

    def toggle_auto_sync(enabled: bool) -> None:
        self.auto_sync_check.setChecked(enabled)

    def toggle_auto_weather_refresh(enabled: bool) -> None:
        self.auto_weather_refresh_check.setChecked(enabled)

    def get_analytics_sync_status() -> dict[str, Any]:
        return {
            "sync_in_progress": self.sync_in_progress,
            "auto_weather_refresh_enabled": self.auto_weather_refresh_enabled,
            "current_analytics_parameter": self.current_analytics_parameter,
            "last_analysis_parameters": self.last_analysis_parameters,
            "last_weather_parameters": self.last_weather_parameters,
            "last_date_parameters": self.last_date_parameters,
        }

    def get_integration_status() -> dict[str, Any]:
        return {
            "data_loaded": self.is_data_loaded,
            "folium_ready": self.is_folium_ready,
            "auto_sync_enabled": self.auto_sync_enabled,
            "auto_weather_refresh_enabled": self.auto_weather_refresh_enabled,
            "location_selector_available": self.location_selector is not None,
            "map_visualizer_available": self.map_visualizer is not None,
            "folium_available": self.map_visualizer.is_folium_available()
            if self.map_visualizer
            else False,
            "weather_bridge_available": self.weather_bridge is not None,
            "multi_city_engine_available": self.multi_city_engine is not None,
            "weather_data_available": self.weather_data_available,
            "current_location": self.current_location_data,
            "current_analytics_result": self.current_analytics_result is not None,
            "current_analytics_parameter": self.current_analytics_parameter,
            "current_weather_overlay_type": self.current_weather_overlay.overlay_type
            if self.current_weather_overlay
            else None,
            "available_counties_count": len(self.get_available_counties()),
            "current_theme": self.current_theme,
            "map_status": self.get_map_status(),
            "analytics_sync_status": self.get_analytics_sync_status(),
            "sync_in_progress": self.sync_in_progress,
        }

    # Bind methods to self
    self.get_location_selector = get_location_selector
    self.get_map_visualizer = get_map_visualizer
    self.get_weather_bridge = get_weather_bridge
    self.get_multi_city_engine = get_multi_city_engine
    self.get_current_analytics_result = get_current_analytics_result
    self.get_current_weather_overlay = get_current_weather_overlay
    self.get_current_analytics_parameter = get_current_analytics_parameter
    self.has_weather_data = has_weather_data
    self.get_current_location = get_current_location
    self.get_counties_geodataframe = get_counties_geodataframe
    self.set_region_and_county = set_region_and_county
    self.focus_on_county = focus_on_county
    self.get_available_counties = get_available_counties
    self.get_map_status = get_map_status
    self.is_ready = is_ready
    self.is_folium_ready_status = is_folium_ready_status
    self.set_theme = set_theme
    self.set_weather_data = set_weather_data
    self.refresh_all_components = refresh_all_components
    self.clear_selection = clear_selection
    self.toggle_auto_sync = toggle_auto_sync
    self.toggle_auto_weather_refresh = toggle_auto_weather_refresh
    self.get_analytics_sync_status = get_analytics_sync_status
    self.get_integration_status = get_integration_status


__all__ = ["create_public_api_methods"]
