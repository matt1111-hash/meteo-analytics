# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Mixin part 2 for WeatherDataBridge."""

from __future__ import annotations

from .core_support import *


def _get_gradient_color(normalized: float) -> str:
    """Return the default cold-to-hot gradient color."""
    if normalized < 0.33:
        return "#0000FF"
    if normalized < 0.66:
        return "#FFFF00"
    return "#FF0000"


def _get_precipitation_color(normalized: float) -> str:
    """Return a precipitation palette color."""
    if normalized < 0.5:
        return "#87CEEB"
    return "#0000CD"


def _resolve_marker_color(overlay_type: str, normalized: float) -> str:
    """Resolve marker color by overlay type."""
    if overlay_type == "precipitation":
        return _get_precipitation_color(normalized)
    if overlay_type in ["temperature", "wind_speed", "wind_gusts"]:
        return _get_gradient_color(normalized)
    return _get_gradient_color(normalized)


class WeatherDataBridgePart2Mixin:
    def get_overlay_legend_data(
        self, overlay_data: WeatherOverlayData
    ) -> Dict[str, Any]:
        """Legend adatok generálása a Folium térképhez"""
        metadata = overlay_data.metadata

        return {
            "title": f"{metadata['icon']} {metadata['name']}",
            "unit": metadata["unit"],
            "min_value": metadata["scale_min"],
            "max_value": metadata["scale_max"],
            "color_scale": metadata["color_scale"],
            "total_cities": metadata["total_cities"],
            "value_range": f"{metadata['value_min']:.1f} - {metadata['value_max']:.1f}",
            "question": metadata["analytics_question"],
            "metric": metadata.get("metric", "unknown"),
        }

    def create_multiple_overlays_from_analytics(
        self, analytics_results: List[AnalyticsResult]
    ) -> Dict[str, WeatherOverlayData]:
        """Több analytics eredményből több overlay létrehozása"""
        overlays = {}

        for result in analytics_results:
            overlay_data = self.convert_analytics_to_weather_overlay(result)
            if overlay_data:
                overlays[overlay_data.overlay_type] = overlay_data

        return overlays

    def get_folium_heatmap_data(
        self, overlay_data: WeatherOverlayData
    ) -> List[List[float]]:
        """Folium HeatMap plugin formátumra konvertálás"""
        heatmap_data = []

        for city_name, city_data in overlay_data.data.items():
            lat, lon = city_data["coordinates"]
            value = city_data["value"]
            heatmap_data.append([lat, lon, value])

        return heatmap_data

    def get_folium_marker_data(
        self, overlay_data: WeatherOverlayData
    ) -> List[Dict[str, Any]]:
        """Folium CircleMarker formátumra konvertálás"""
        marker_data = []
        metadata = overlay_data.metadata

        for city_name, city_data in overlay_data.data.items():
            marker_config = {
                "latitude": city_data["coordinates"][0],
                "longitude": city_data["coordinates"][1],
                "value": city_data["value"],
                "city_name": city_name,
                "country": city_data["country"],
                "popup_text": f"{city_name}, {city_data['country']}<br>{city_data['value']:.1f} {metadata['unit']}",
                "tooltip_text": f"{city_name}: {city_data['value']:.1f} {metadata['unit']}",
                "marker_size": self._calculate_marker_size(
                    city_data["value"], metadata
                ),
                "marker_color": self._calculate_marker_color(
                    city_data["value"], metadata
                ),
                "rank": city_data.get("rank", 0),
            }

            if overlay_data.overlay_type in ["wind_speed", "wind_gusts"]:
                marker_config["speed"] = city_data.get("speed", city_data["value"])
                marker_config["direction"] = city_data.get("direction", 0)

            marker_data.append(marker_config)

        return marker_data

    def _calculate_marker_size(self, value: float, metadata: Dict[str, Any]) -> int:
        """Marker méret számítása érték alapján"""
        value_range = metadata["scale_max"] - metadata["scale_min"]
        if value_range == 0:
            return 8

        normalized = (value - metadata["scale_min"]) / value_range
        min_size, max_size = 4, 20
        return int(min_size + normalized * (max_size - min_size))

    def _calculate_marker_color(self, value: float, metadata: Dict[str, Any]) -> str:
        """Marker szín számítása érték alapján"""
        value_range = metadata["scale_max"] - metadata["scale_min"]
        if value_range == 0:
            return "#FF0000"

        normalized = (value - metadata["scale_min"]) / value_range
        overlay_type = metadata["overlay_type"]
        if overlay_type in ["wind_speed", "wind_gusts"]:
            return "#00FF00" if normalized < 0.33 else _get_gradient_color(normalized)
        return _resolve_marker_color(overlay_type, normalized)

    def debug_metric_mapping(self) -> Dict[str, Any]:
        """DEBUG: Metrika mapping információk"""
        return {
            "total_supported_metrics": len(self.METRIC_MAP),
            "metric_mappings": {str(m): dp for m, dp in self.METRIC_MAP.items()},
            "overlay_types": list(self.OVERLAY_CONFIGS.keys()),
            "windspeed_supported": AnalyticsMetric.WINDSPEED_10M_MAX in self.METRIC_MAP,
            "windspeed_maps_to": self.METRIC_MAP.get(AnalyticsMetric.WINDSPEED_10M_MAX),
            "bridge_version": "2.0_METRIC_MAP_FIXED",
        }
