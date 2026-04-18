"""Folium-specific visualization methods for weather data."""

from __future__ import annotations

from typing import Any

from src.domain.value_objects.enums import AnalyticsMetric
from src.presentation.gui.weather_data_bridge.constants import (
    METRIC_MAP,
    OVERLAY_CONFIGS,
)
from src.presentation.gui.weather_data_bridge.data import WeatherOverlayData


def _get_gradient_color(normalized: float) -> str:
    if normalized < 0.33:  # noqa: PLR2004
        return "#0000FF"
    if normalized < 0.66:  # noqa: PLR2004
        return "#FFFF00"
    return "#FF0000"


def calculate_marker_size(value: float, metadata: dict[str, Any]) -> int:
    """Calculate marker size based on value position in scale."""
    value_range = metadata["scale_max"] - metadata["scale_min"]
    if value_range == 0:
        return 8
    normalized = (value - metadata["scale_min"]) / value_range
    min_size, max_size = 4, 20
    return int(min_size + normalized * (max_size - min_size))


def calculate_marker_color(value: float, metadata: dict[str, Any]) -> str:
    """Calculate marker color based on overlay type and value."""
    value_range = metadata["scale_max"] - metadata["scale_min"]
    if value_range == 0:
        return "#FF0000"
    normalized = (value - metadata["scale_min"]) / value_range
    overlay_type = metadata["overlay_type"]
    if overlay_type in ["wind_speed", "wind_gusts"]:
        return "#00FF00" if normalized < 0.33 else _get_gradient_color(normalized)  # noqa: PLR2004
    if overlay_type == "precipitation":
        return "#87CEEB" if normalized < 0.5 else "#0000CD"  # noqa: PLR2004
    return _get_gradient_color(normalized)


def get_folium_heatmap_data(overlay_data: WeatherOverlayData) -> list[list[float]]:
    """Convert overlay data to Folium HeatMap format."""
    heatmap_data = []
    for city_data in overlay_data.data.values():
        lat, lon = city_data["coordinates"]
        value = city_data["value"]
        heatmap_data.append([lat, lon, value])
    return heatmap_data


def get_folium_marker_data(overlay_data: WeatherOverlayData) -> list[dict[str, Any]]:
    """Convert overlay data to Folium CircleMarker format."""
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
            "marker_size": calculate_marker_size(city_data["value"], metadata),
            "marker_color": calculate_marker_color(city_data["value"], metadata),
            "rank": city_data.get("rank", 0),
        }

        if overlay_data.overlay_type in ["wind_speed", "wind_gusts"]:
            marker_config["speed"] = city_data.get("speed", city_data["value"])
            marker_config["direction"] = city_data.get("direction", 0)

        marker_data.append(marker_config)

    return marker_data


def debug_metric_mapping() -> dict[str, Any]:
    """Return debug information about metric mapping."""
    return {
        "total_supported_metrics": len(METRIC_MAP),
        "metric_mappings": {str(m): dp for m, dp in METRIC_MAP.items()},
        "overlay_types": list(OVERLAY_CONFIGS.keys()),
        "windspeed_supported": AnalyticsMetric.WINDSPEED_10M_MAX in METRIC_MAP,
        "windspeed_maps_to": METRIC_MAP.get(AnalyticsMetric.WINDSPEED_10M_MAX),
        "bridge_version": "2.0_METRIC_MAP_FIXED",
    }
