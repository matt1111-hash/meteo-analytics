#!/usr/bin/env python3
# mypy: ignore-errors

"""
🗺️ Folium Renderer - Folium térkép generáló thread.

FÁJL: src/presentation/gui/map/folium_renderer.py
"""

import os
import tempfile
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from PySide6.QtCore import QThread, Signal

try:
    import folium

    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False

from .html_generator import (
    create_general_legend,
    create_precipitation_legend,
    create_temperature_legend,
    create_wind_legend,
)
from .layer_builder import LayerBuilder
from .map_state import FoliumMapConfig
from .overlay_manager import OverlayManager

if TYPE_CHECKING:
    import geopandas as gpd


class FoliumMapGenerator(QThread):
    """
    📄 Háttér worker a Folium interaktív térkép generálásához - HTTP SZERVER VERZIÓ.
    """

    progress_updated = Signal(int)
    map_generated = Signal(str)
    error_occurred = Signal(str)
    status_updated = Signal(str)

    def __init__(  # noqa: D107
        self,
        config: FoliumMapConfig,
        counties_gdf: Optional["gpd.GeoDataFrame"] = None,
        weather_data: dict | None = None,
        bridge_id: str | None = None,
        output_path: str | None = None,
    ):
        super().__init__()
        self.config = config
        self.counties_gdf = counties_gdf
        self.weather_data = weather_data
        self.bridge_id = bridge_id or str(uuid.uuid4())

        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.output_path = os.path.join(  # noqa: PTH118
                tempfile.gettempdir(), f"hungarian_folium_map_{timestamp}.html"
            )
        else:
            self.output_path = output_path

    def run(self) -> None:
        """
        🗺️ Folium interaktív térkép generálása.
        """
        try:
            self._generate_map_content()
        except Exception as e:
            import traceback

            error_msg = f"Folium térkép generálási hiba: {e}\n{traceback.format_exc()}"
            self.error_occurred.emit(error_msg)

    def _generate_map_content(self) -> None:
        """Fő lépések szétbontva."""
        if not FOLIUM_AVAILABLE:
            raise ImportError("Folium library not available")

        self.status_updated.emit("🗺️ Folium térkép inicializálása...")
        self.progress_updated.emit(5)

        layer_builder = LayerBuilder(self.config)
        map_obj = layer_builder.create_base_map()
        self.progress_updated.emit(20)

        self._maybe_add_counties(map_obj, layer_builder)
        self.progress_updated.emit(50)

        self._maybe_add_weather_overlay(map_obj)
        self.progress_updated.emit(70)

        self.status_updated.emit("🌉 JavaScript interaktivitás...")
        layer_builder.add_javascript_bridge(map_obj, self.bridge_id)
        self.progress_updated.emit(85)

        layer_builder.add_map_controls(map_obj)
        self.progress_updated.emit(90)

        self._add_weather_legend(map_obj)
        self.progress_updated.emit(95)

        self._save_and_validate_map(map_obj)
        self.progress_updated.emit(100)

        self.status_updated.emit("✅ Folium térkép elkészült!")
        print(
            f"✅ Folium map generated: {self.output_path} ({os.path.getsize(self.output_path):,} bytes)"  # noqa: PTH202
        )
        self.map_generated.emit(self.output_path)

    def _maybe_add_counties(self, map_obj: "folium.Map", layer_builder: LayerBuilder) -> None:
        if self.config.show_counties and self.counties_gdf is not None:
            self.status_updated.emit("🗺️ Megyehatárok hozzáadása...")
            layer_builder.add_counties_layer(map_obj, self.counties_gdf)

    def _maybe_add_weather_overlay(self, map_obj: "folium.Map") -> None:
        if self.config.weather_overlay and self.weather_data:
            self.status_updated.emit("🌤️ Időjárási overlay...")
            overlay_manager = OverlayManager(self.weather_data)
            overlay_manager.add_overlays(map_obj)

    def _add_weather_legend(self, map_obj: "folium.Map") -> None:
        """
        📊 Weather overlay legend hozzáadása.
        """
        try:
            active_parameter = self.config.active_overlay_parameter

            if active_parameter == "temperature":
                legend_html = create_temperature_legend()
            elif active_parameter == "wind_speed":
                legend_html = create_wind_legend()
            elif active_parameter == "precipitation":
                legend_html = create_precipitation_legend()
            else:
                legend_html = create_general_legend()

            map_obj.get_root().html.add_child(folium.Element(legend_html))
            print(f"📊 Weather legend added for parameter: {active_parameter}")

        except Exception as e:
            print(f"⚠️ Weather legend error: {e}")

    def _save_and_validate_map(self, map_obj: "folium.Map") -> None:
        self.status_updated.emit("💾 HTML fájl mentése...")
        map_obj.save(self.output_path)

        if not os.path.exists(self.output_path):  # noqa: PTH110
            raise FileNotFoundError(f"Generated HTML file not found: {self.output_path}")

        file_size = os.path.getsize(self.output_path)  # noqa: PTH202
        if file_size < 1000:  # noqa: PLR2004
            raise ValueError(f"Generated HTML file too small: {file_size} bytes")


# Export
__all__ = [
    "FoliumMapGenerator",
]
