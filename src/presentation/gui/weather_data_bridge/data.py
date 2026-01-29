"""Weather overlay data structures."""
from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class WeatherOverlayData:
    """Weather overlay adat struktúra Folium térképhez"""
    overlay_type: str  # 'temperature', 'precipitation', 'wind_speed', 'wind_gusts'
    data: Dict[str, Dict[str, Any]]  # city_name -> {coordinates, value, additional_info}
    metadata: Dict[str, Any]  # min/max értékek, egységek, színskála info
