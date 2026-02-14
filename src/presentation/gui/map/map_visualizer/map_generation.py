#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Map Visualizer - Map Generation

🗺️ Map generálás és betöltés

Képességek:
- Map generálás indítása
- Map generálás callback
- Map betöltés HTTP URL-ről
- Map hiba kezelés

Fájl: src/presentation/gui/map/map_visualizer/map_generation.py
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


def _generate_default_map(self) -> None:
    """
    🗺️ Alapértelmezett map generálása.

    Args:
        self: HungarianMapVisualizer instance
    """
    try:
        import folium  # noqa: F401
    except ImportError:
        return

    if not self.http_host or not self.http_port:
        return
    self._start_map_generation()


def _start_map_generation(self) -> None:
    """
    🚀 Map generálás indítása.

    Args:
        self: HungarianMapVisualizer instance
    """
    try:
        import folium  # noqa: F401
    except ImportError:
        self._show_folium_error()
        return

    if not self.http_host or not self.http_port:
        return
    if self.map_generator and self.map_generator.isRunning():
        return

    self.progress_bar.setVisible(True)
    self.progress_bar.setValue(0)
    self.status_label.setText("🌐 HTTP szerver Folium térkép generálása...")

    from .folium_renderer import FoliumMapGenerator

    self.map_generator = FoliumMapGenerator(
        config=self.map_config,
        counties_gdf=self.counties_gdf,
        weather_data=self.current_weather_data,
        bridge_id=self.js_bridge.bridge_id,
    )
    self.map_generator.progress_updated.connect(self.progress_bar.setValue)
    self.map_generator.status_updated.connect(self.status_label.setText)
    self.map_generator.map_generated.connect(self._on_map_generated)
    self.map_generator.error_occurred.connect(self._on_map_error)
    self.map_generator.start()


def _on_map_generated(self, file_path: str) -> None:
    """
    Map generálás callback.

    Args:
        self: HungarianMapVisualizer instance
        file_path: Generált HTML fájl útvonal
    """
    import os

    if not os.path.exists(file_path):
        self.error_occurred.emit(f"Generated HTML file not found: {file_path}")
        return

    file_size = os.path.getsize(file_path)
    if file_size < 1000:
        self.error_occurred.emit(f"Generated HTML file too small: {file_size} bytes")
        return

    self.current_map_file = file_path
    self._load_map_from_http_url(file_path)
    self.progress_bar.setVisible(False)
    self.status_label.setText("🌐 HTTP szerver térkép betöltése...")


def _load_map_from_http_url(self, file_path: str) -> None:
    """
    🌐 Map betöltése HTTP URL-ről.

    Args:
        self: HungarianMapVisualizer instance
        file_path: Map HTML fájl útvonal
    """
    import os

    from PySide6.QtCore import QUrl

    try:
        filename = os.path.basename(file_path)
        http_url = f"http://{self.http_host}:{self.http_port}/{filename}"
        self.web_view.stop()
        self.web_view.load(QUrl(http_url))
        self.status_label.setText(f"🌐 HTTP térkép betöltve: {filename}")
    except Exception as e:
        error_msg = f"HTTP URL betöltési hiba: {e}"
        self.error_occurred.emit(error_msg)


def _on_map_error(self, error_message: str) -> None:
    """
    Map generálás error handler.

    Args:
        self: HungarianMapVisualizer instance
        error_message: Error message
    """
    self.progress_bar.setVisible(False)
    self.status_label.setText("❌ Folium térkép generálási hiba!")
    self.error_occurred.emit(error_message)
