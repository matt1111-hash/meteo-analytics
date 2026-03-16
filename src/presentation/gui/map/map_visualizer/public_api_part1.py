# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Split definitions from public_api.py."""

from __future__ import annotations

from .public_api_support import *


def set_active_overlay_parameter(self, parameter: str) -> None:
    """
    🎨 Aktív overlay parameter beállítása.

    Args:
        self: HungarianMapVisualizer instance
        parameter: Parameter név (temperature, wind_speed, precipitation, etc.)
    """
    self.map_config.active_overlay_parameter = parameter

    parameter_display_names = {
        "temperature": "🌡️ Hőmérséklet",
        "wind_speed": "💨 Szélsebesség",
        "precipitation": "🌧️ Csapadék",
        "wind_gusts": "🌪️ Széllökések",
        "humidity": "💧 Páratartalom",
    }

    display_name = parameter_display_names.get(parameter, f"🎨 {parameter}")
    self.overlay_parameter_label.setText(f"🎨 Overlay: {display_name}")


def clear_active_overlay_parameter(self) -> None:
    """
    🧹 Aktív overlay parameter törlése.

    Args:
        self: HungarianMapVisualizer instance
    """
    self.map_config.active_overlay_parameter = None
    self.overlay_parameter_label.setText("🎨 Overlay: Nincs")
    self.overlay_parameter_label.setStyleSheet("color: #95A5A6;")


def get_active_overlay_parameter(self) -> Optional[str]:
    """
    Aktív overlay parameter lekérdezése.

    Args:
        self: HungarianMapVisualizer instance

    Returns:
        Optional[str]: Aktív parameter név vagy None
    """
    return self.map_config.active_overlay_parameter


def set_counties_geodataframe(self, counties_gdf) -> None:
    """
    🗺️ Counties GeoDataFrame beállítása.

    Args:
        self: HungarianMapVisualizer instance
        counties_gdf: Counties GeoDataFrame
    """
    print(
        f"🗺️ 🚀 REAKTÍV: Counties GeoDataFrame set: {len(counties_gdf) if counties_gdf is not None else 0} counties"
    )
    self.counties_gdf = counties_gdf

    if counties_gdf is not None and len(counties_gdf) > 0:
        self.map_config.show_counties = True
        self.counties_check.setChecked(True)
        self._start_map_generation()


def set_weather_data(self, weather_data: Dict) -> None:
    """
    🌤️ Weather data beállítása.

    Args:
        self: HungarianMapVisualizer instance
        weather_data: Weather data dictionary
    """
    print("🌤️ 🚀 REAKTÍV: Real weather data set for HTTP server Folium overlay")
    self.current_weather_data = weather_data

    if weather_data:
        for data_type in weather_data.keys():
            if data_type in [
                "temperature",
                "wind_speed",
                "precipitation",
                "wind_gusts",
            ]:
                self.set_active_overlay_parameter(data_type)

        self.map_config.weather_overlay = True
        self.weather_check.setChecked(True)
        self._start_map_generation()


def update_map_bounds(self, bounds: Tuple[float, float, float, float]) -> None:
    """
    🗺️ Map bounds frissítése.

    Args:
        self: HungarianMapVisualizer instance
        bounds: (min_lon, min_lat, max_lon, max_lat)
    """
    center_lat = (bounds[1] + bounds[3]) / 2
    center_lon = (bounds[0] + bounds[2]) / 2
    lat_diff = abs(bounds[3] - bounds[1])
    lon_diff = abs(bounds[2] - bounds[0])

    if lat_diff > 2 or lon_diff > 3:
        zoom = 6
    elif lat_diff > 1 or lon_diff > 1.5:
        zoom = 7
    elif lat_diff > 0.5 or lon_diff > 0.8:
        zoom = 8
    else:
        zoom = 9

    self.map_config.center_lat = center_lat
    self.map_config.center_lon = center_lon
    self.map_config.zoom_start = zoom
    self.zoom_slider.setValue(zoom)
    self._start_map_generation()


def get_map_config(self) -> "FoliumMapConfig":
    """
    Map konfiguráció lekérdezése.

    Args:
        self: HungarianMapVisualizer instance

    Returns:
        FoliumMapConfig: Map konfiguráció
    """
    return self.map_config


def reset_map_view(self) -> None:
    """
    🏠 Map view alaphelyzetbe állítása.

    Args:
        self: HungarianMapVisualizer instance
    """
    self.map_config.center_lat = 47.1625
    self.map_config.center_lon = 19.5033
    self.map_config.zoom_start = 7
    self.map_config.selected_county = None
    self.map_config.highlighted_counties = []
    self.clear_active_overlay_parameter()
    self.zoom_slider.setValue(7)
    self.style_combo.setCurrentText("OpenStreetMap")
    self._start_map_generation()
