#!/usr/bin/env python3
# mypy: ignore-errors

"""
🗺️ Overlay Manager - Weather overlay kezelők.

FÁJL: src/presentation/gui/map/overlay_manager.py
"""

try:
    import folium
    from folium.plugins import HeatMap

    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False

from .map_constants import (
    get_beaufort_color,
    get_gradient_for_overlay,
    get_precipitation_color,
)


class OverlayManager:
    """
    🌤️ Időjárási overlay kezelő.
    """

    def __init__(self, weather_data: dict):
        """
        Args:
            weather_data: Időjárási adatok dictionary
        """
        self.weather_data = weather_data

    def add_overlays(self, map_obj: "folium.Map") -> None:
        """
        🌤️ Összes weather overlay hozzáadása.

        Args:
            map_obj: Folium Map objektum
        """
        if not self.weather_data:
            print("⚠️ No weather data available for overlay")
            return

        print(f"🌤️ Adding weather overlay with {len(self.weather_data)} data types")

        try:
            # Hőmérséklet heatmap
            if "temperature" in self.weather_data:
                self._add_temperature_heatmap(map_obj)

            # Csapadék overlay
            if "precipitation" in self.weather_data:
                self._add_precipitation_overlay(map_obj)

            # Szél sebesség overlay
            if "wind_speed" in self.weather_data:
                self._add_wind_speed_overlay(map_obj)

            print("✅ Weather overlay layers added successfully")

        except Exception as e:
            print(f"⚠️ Weather overlay error: {e}")

    def _add_temperature_heatmap(self, map_obj: "folium.Map") -> None:
        """
        🌡️ Hőmérséklet heatmap hozzáadása.
        """
        try:
            temp_data = self._build_temperature_heatmap_points()
            if not temp_data:
                return

            gradient = get_gradient_for_overlay("temperature")
            heat_map = HeatMap(
                temp_data,
                name="🌡️ Hőmérséklet",
                min_opacity=0.3,
                max_zoom=18,
                radius=25,
                blur=15,
                gradient=gradient,
            )
            heat_map.add_to(map_obj)
            print(f"🌡️ Temperature heatmap added with {len(temp_data)} points")

        except Exception as e:
            print(f"⚠️ Temperature heatmap error: {e}")

    def _build_temperature_heatmap_points(self) -> list[list[float]]:
        """Heatmap pontok összeállítása normalizált intenzitással."""
        temp_data: list[list[float]] = []
        for data in self.weather_data.get("temperature", {}).values():
            if "coordinates" not in data or "value" not in data:
                continue
            lat, lon = data["coordinates"]
            temp = data["value"]
            intensity = max(0.1, min(1.0, (temp + 20) / 60))
            temp_data.append([lat, lon, intensity])
        return temp_data

    def _add_precipitation_overlay(self, map_obj: "folium.Map") -> None:
        """
        🌧️ Csapadék overlay hozzáadása CircleMarker-ekkel.
        """
        try:
            precip_data = self.weather_data.get("precipitation", {})

            for location, data in precip_data.items():
                if "coordinates" in data and "value" in data:
                    lat, lon = data["coordinates"]
                    precip_mm = data["value"]

                    radius = max(3, min(20, precip_mm / 2))
                    color = get_precipitation_color(precip_mm)

                    folium.CircleMarker(
                        location=[lat, lon],
                        radius=radius,
                        popup=f"🌧️ {location}<br>Csapadék: {precip_mm:.1f} mm",
                        color="#FFFFFF",
                        weight=1,
                        fillColor=color,
                        fillOpacity=0.7,
                        tooltip=f"{precip_mm:.1f} mm",
                    ).add_to(map_obj)

            print(f"🌧️ Precipitation overlay added with {len(precip_data)} points")

        except Exception as e:
            print(f"⚠️ Precipitation overlay error: {e}")

    def _add_wind_speed_overlay(self, map_obj: "folium.Map") -> None:
        """
        💨 Szél sebesség overlay hozzáadása nyilakkal.
        """
        try:
            wind_data = self.weather_data.get("wind_speed", {})

            for location, data in wind_data.items():
                if "coordinates" in data and "speed" in data:
                    lat, lon = data["coordinates"]
                    speed_kmh = data["speed"]
                    direction = data.get("direction", 0)

                    max(5, min(15, speed_kmh / 5))
                    color = get_beaufort_color(speed_kmh)

                    wind_icon = f"""
                    <svg width="20" height="20" viewBox="0 0 20 20" style="transform: rotate({direction}deg)">
                        <path d="M10,2 L15,18 L10,15 L5,18 Z" fill="{color}" stroke="#000" stroke-width="1"/>
                    </svg>
                    """

                    wind_marker = folium.Marker(
                        location=[lat, lon],
                        icon=folium.DivIcon(
                            html=wind_icon,
                            class_name="wind-arrow",
                            icon_size=(20, 20),
                            icon_anchor=(10, 10),
                        ),
                        popup=f"💨 {location}<br>Szél: {speed_kmh:.1f} km/h<br>Irány: {direction}°",
                        tooltip=f"{speed_kmh:.1f} km/h",
                    )

                    wind_marker.add_to(map_obj)

            print(f"💨 Wind speed overlay added with {len(wind_data)} points")

        except Exception as e:
            print(f"⚠️ Wind speed overlay error: {e}")


# Export
__all__ = [
    "OverlayManager",
]
