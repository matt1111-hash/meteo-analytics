#!/usr/bin/env python3
# mypy: ignore-errors

"""
Map Visualizer - Debug

🔧 Debug és helper metódusok

Képességek:
- Demo weather data generálás
- HTTP szerver info lekérdezése
- Gradient info lekérdezése
- Debug info lekérdezése

Fájl: src/presentation/gui/map/map_visualizer/debug.py
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


def generate_demo_weather_data(self) -> dict:  # noqa: ARG001
    """
    🧪 Demo időjárási adatok generálása teszteléshez.

    Args:
        self: HungarianMapVisualizer instance

    Returns:
        Dict: Demo weather data
    """
    from .map_debug import generate_demo_weather_data  # noqa: PLC0415

    return generate_demo_weather_data()


def get_http_server_info(self) -> dict:
    """
    🌐 HTTP szerver információk lekérdezése.

    Args:
        self: HungarianMapVisualizer instance

    Returns:
        Dict: HTTP szerver információk
    """
    from .map_debug import get_http_server_info  # noqa: PLC0415

    return get_http_server_info(
        self.local_server, self.http_host, self.http_port, self.current_map_file
    )


def get_dynamic_gradient_info(self) -> dict:
    """
    🎨 Dinamikus gradient információk lekérdezése.

    Args:
        self: HungarianMapVisualizer instance

    Returns:
        Dict: Gradient információk
    """
    from .map_debug import get_dynamic_gradient_info  # noqa: PLC0415

    return get_dynamic_gradient_info(self.get_active_overlay_parameter())


def get_http_debug_info(self) -> dict:
    """
    🔍 HTTP szerver verzió debug információk.

    Args:
        self: HungarianMapVisualizer instance

    Returns:
        Dict: Debug információk
    """
    from .map_debug import get_http_debug_info  # noqa: PLC0415

    return get_http_debug_info(
        self.local_server,
        self.http_host,
        self.http_port,
        self.current_map_file,
        self.counties_gdf,
        self.current_weather_data,
    )


def cleanup(self) -> None:
    """
    🧹 Takarítás when a widget megszűnik.

    Args:
        self: HungarianMapVisualizer instance
    """
    import os  # noqa: PLC0415

    if self.local_server and self.local_server.running:
        print("🛑 Stopping local HTTP server...")
        self.local_server.stop()
        self.local_server.wait()

    if self.current_map_file and os.path.exists(self.current_map_file):  # noqa: PTH110
        try:
            os.remove(self.current_map_file)  # noqa: PTH107
            print(f"🗑️ Temp map file removed: {self.current_map_file}")
        except Exception as e:
            print(f"⚠️ Failed to remove temp file: {e}")
