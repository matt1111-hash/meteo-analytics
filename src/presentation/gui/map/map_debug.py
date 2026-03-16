#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mypy: ignore-errors

"""
🗺️ Map Debug - Demo adat generálás és debug információk.

FÁJL: src/presentation/gui/map/map_debug.py
"""

import os
from typing import Any, Dict, Optional


def generate_demo_weather_data() -> Dict[str, Any]:
    """
    🧪 Demo időjárási adatok generálása teszteléshez.

    Returns:
        Demo időjárási adatok dictionary
    """
    import random

    cities = [
        {"name": "Budapest", "coordinates": [47.4979, 19.0402]},
        {"name": "Debrecen", "coordinates": [47.5316, 21.6273]},
        {"name": "Szeged", "coordinates": [46.2530, 20.1414]},
        {"name": "Miskolc", "coordinates": [48.1034, 20.7784]},
        {"name": "Pécs", "coordinates": [46.0727, 18.2329]},
        {"name": "Győr", "coordinates": [47.6874, 17.6504]},
        {"name": "Nyíregyháza", "coordinates": [47.9562, 21.7201]},
        {"name": "Kecskemét", "coordinates": [46.9061, 19.6938]},
        {"name": "Székesfehérvár", "coordinates": [47.1884, 18.4241]},
        {"name": "Szombathely", "coordinates": [47.2309, 16.6218]},
    ]

    demo_data = {"temperature": {}, "precipitation": {}, "wind_speed": {}}

    for city in cities:
        demo_data["temperature"][city["name"]] = {
            "coordinates": city["coordinates"],
            "value": random.uniform(-5, 35),
        }
        demo_data["precipitation"][city["name"]] = {
            "coordinates": city["coordinates"],
            "value": random.uniform(0, 25),
        }
        demo_data["wind_speed"][city["name"]] = {
            "coordinates": city["coordinates"],
            "speed": random.uniform(5, 45),
            "direction": random.randint(0, 360),
        }

    print(f"🧪 Demo weather data generated: {len(cities)} cities")
    return demo_data


def get_http_server_info(
    local_server,
    http_host: Optional[str],
    http_port: Optional[int],
    current_map_file: Optional[str],
) -> Dict[str, Any]:
    """
    🌐 HTTP szerver információk lekérdezése.

    Args:
        local_server: LocalHttpServerThread objektum
        http_host: HTTP szerver host
        http_port: HTTP szerver port
        current_map_file: Jelenlegi térkép fájl

    Returns:
        HTTP szerver információk dictionary
    """
    return {
        "server_running": local_server is not None and local_server.running,
        "http_host": http_host,
        "http_port": http_port,
        "server_url": f"http://{http_host}:{http_port}"
        if http_host and http_port
        else None,
        "current_map_file": current_map_file,
        "current_map_size": os.path.getsize(current_map_file)
        if current_map_file and os.path.exists(current_map_file)
        else 0,
        "version": "v3.0",
    }


def get_dynamic_gradient_info(
    active_overlay_parameter: Optional[str],
) -> Dict[str, Any]:
    """
    🔧 Dinamikus gradient információk lekérdezése.

    Args:
        active_overlay_parameter: Aktív overlay parameter

    Returns:
        Gradient információk dictionary
    """
    from .map_constants import OVERLAY_COLOR_MAPPING

    return {
        "active_overlay_parameter": active_overlay_parameter,
        "available_gradients": ["RdYlBu_r", "Blues", "Greens", "Oranges"],
        "gradient_mapping": OVERLAY_COLOR_MAPPING,
        "dynamic_gradient_support": True,
        "http_server_version": True,
        "same_origin_policy_fixed": True,
        "reactive_counties": True,
        "reactive_weather": True,
        "large_html_support": True,
        "version": "v3.0",
    }


def get_http_debug_info(
    local_server,
    http_host: Optional[str],
    http_port: Optional[int],
    current_map_file: Optional[str],
    counties_gdf,
    current_weather_data,
) -> Dict[str, Any]:
    """
    🌐 HTTP szerver verzió debug információk.

    Args:
        local_server: LocalHttpServerThread objektum
        http_host: HTTP szerver host
        http_port: HTTP szerver port
        current_map_file: Jelenlegi térkép fájl
        counties_gdf: Megyék GeoDataFrame
        current_weather_data: Jelenlegi időjárási adatok

    Returns:
        HTTP szerver debug információk
    """
    server_info = get_http_server_info(
        local_server, http_host, http_port, current_map_file
    )

    return {
        "http_server_running": server_info["server_running"],
        "server_url": server_info["server_url"],
        "map_file_available": server_info["current_map_file"] is not None,
        "map_file_size": server_info["current_map_size"],
        "large_html_support": True,
        "same_origin_policy_fix": True,
        "webengine_http_loading": True,
        "no_temp_files_conflict": True,
        "reactive_counties": True,
        "reactive_weather": True,
        "counties_loaded": counties_gdf is not None,
        "counties_count": len(counties_gdf) if counties_gdf is not None else 0,
        "weather_data_loaded": current_weather_data is not None,
        "version": "v3.0",
    }


# Export
__all__ = [
    "generate_demo_weather_data",
    "get_http_server_info",
    "get_dynamic_gradient_info",
    "get_http_debug_info",
]
