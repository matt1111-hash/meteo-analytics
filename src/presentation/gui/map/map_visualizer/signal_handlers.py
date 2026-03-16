#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mypy: ignore-errors

"""
Map Visualizer - Signal Handlers

🔌 Signal kezelés és event handlers

Képességek:
- Signal connection setup
- UI event handlers
- JavaScript bridge event handlers
- Map event handlers

Fájl: src/presentation/gui/map/map_visualizer/signal_handlers.py
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


def connect_signals(self) -> None:
    """
    🔌 Signal connections beállítása.

    Args:
        self: HungarianMapVisualizer instance
    """
    self.style_combo.currentTextChanged.connect(self._on_style_changed)
    self.counties_check.toggled.connect(self._on_counties_toggled)
    self.weather_check.toggled.connect(self._on_weather_toggled)
    self.zoom_slider.valueChanged.connect(self._on_zoom_changed)
    self.refresh_btn.clicked.connect(self._refresh_map)
    self.export_btn.clicked.connect(self._export_map)
    self.reset_btn.clicked.connect(self.reset_map_view)
    self.web_view.loadFinished.connect(self._on_map_loaded)
    self.js_bridge.county_clicked.connect(self._on_js_county_clicked)
    self.js_bridge.coordinates_clicked.connect(self._on_js_coordinates_clicked)
    self.js_bridge.map_moved.connect(self._on_js_map_moved)
    self.js_bridge.county_hovered.connect(self._on_js_county_hovered)


def _on_style_changed(self, style: str) -> None:
    """Style combo handler."""
    self.map_config.tiles = style


def _on_counties_toggled(self, checked: bool) -> None:
    """Counties checkbox handler."""
    self.map_config.show_counties = checked


def _on_weather_toggled(self, checked: bool) -> None:
    """Weather checkbox handler."""
    self.map_config.weather_overlay = checked


def _on_zoom_changed(self, zoom: int) -> None:
    """Zoom slider handler."""
    self.map_config.zoom_start = zoom


def _on_js_county_clicked(self, county_name: str) -> None:
    """JS county click handler."""
    self.map_config.selected_county = county_name
    self.county_clicked.emit(county_name)


def _on_js_coordinates_clicked(self, lat: float, lon: float) -> None:
    """JS coordinates click handler."""
    self.coordinates_clicked.emit(lat, lon)


def _on_js_map_moved(self, lat: float, lon: float, zoom: int) -> None:
    """JS map moved handler."""
    self.map_config.center_lat = lat
    self.map_config.center_lon = lon
    self.map_config.zoom_start = zoom
    self.zoom_slider.setValue(zoom)
    self.map_moved.emit(lat, lon, zoom)


def _on_js_county_hovered(self, county_name: str) -> None:
    """JS county hover handler."""
    self.county_hovered.emit(county_name)


def _refresh_map(self) -> None:
    """Refresh button handler."""
    self._start_map_generation()


def _export_map(self) -> None:
    """Export button handler."""
    import os
    import shutil
    from datetime import datetime

    from PySide6.QtWidgets import QFileDialog, QMessageBox

    if not self.current_map_file or not os.path.exists(self.current_map_file):
        QMessageBox.warning(self, "Export", "Nincs Folium térkép az exportáláshoz!")
        return

    file_path, _ = QFileDialog.getSaveFileName(
        self,
        "HTTP szerver Folium térkép exportálása",
        f"hungarian_folium_map_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
        "HTML fájlok (*.html);;Minden fájl (*)",
    )

    if file_path:
        try:
            shutil.copy2(self.current_map_file, file_path)
            self.export_completed.emit(file_path)
            QMessageBox.information(
                self,
                "Export",
                f"HTTP szerver Folium térkép sikeresen exportálva:\n{file_path}",
            )
        except Exception as e:
            error_msg = f"Export hiba: {e}"
            self.error_occurred.emit(error_msg)
            QMessageBox.critical(self, "Export hiba", error_msg)


def _on_map_loaded(self, success: bool) -> None:
    """Map loaded handler."""
    if success:
        self.map_ready.emit()
        counties_info = (
            f" ({len(self.counties_gdf)} megye)"
            if self.counties_gdf is not None
            else ""
        )
        self.status_label.setText(
            f"🌐 HTTP szerver interaktív térkép kész!{counties_info}"
        )
    else:
        self.error_occurred.emit("WebEngine HTTP loading failed")
        self.status_label.setText("❌ WebEngine HTTP betöltés sikertelen!")
