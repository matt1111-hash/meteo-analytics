#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🗺️ Magyar Folium Térkép Vizualizáló - HELYI HTTP SZERVER VERZIÓ v3.0

FÁJL: src/presentation/gui/map/map_visualizer.py
"""

from typing import Dict, List, Optional, Tuple
import os
import shutil
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QSlider, QCheckBox, QGroupBox, QProgressBar,
    QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QUrl
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebChannel import QWebChannel

try:
    import folium
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False

from ..theme_manager import register_widget_for_theming
from ..color_palette import ColorPalette

from .map_state import FoliumMapConfig
from .map_interactions import LocalHttpServerThread, JavaScriptBridge
from .folium_renderer import FoliumMapGenerator
from .map_debug import (
    generate_demo_weather_data,
    get_http_server_info,
    get_dynamic_gradient_info,
    get_http_debug_info,
)


class HungarianMapVisualizer(QWidget):
    """
    🗺️ Magyar Folium térkép vizualizáló widget - HELYI HTTP SZERVER VERZIÓ v3.0

    SIGNALOK:
    - map_ready(): Térkép betöltve és kész
    - county_clicked(county_name): Megyére kattintás
    - coordinates_clicked(lat, lon): Koordináta kattintás
    - export_completed(file_path): Export befejezve
    - error_occurred(message): Hiba történt
    """

    map_ready = Signal()
    county_clicked = Signal(str)
    coordinates_clicked = Signal(float, float)
    map_moved = Signal(float, float, int)
    county_hovered = Signal(str)
    export_completed = Signal(str)
    error_occurred = Signal(str)
    bounds_changed = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.color_palette = ColorPalette()
        self.map_config = FoliumMapConfig()
        self.counties_gdf = None
        self.current_weather_data = None

        self.local_server = None
        self.http_host = None
        self.http_port = None
        self.current_map_file = None
        self.map_generator = None

        self.js_bridge = JavaScriptBridge()
        self.web_channel = QWebChannel()

        self._setup_ui()
        self._setup_theme()
        self._connect_signals()
        self._start_local_server()

        if not FOLIUM_AVAILABLE:
            self._show_folium_error()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        controls_group = QGroupBox("🌐 HTTP Szerver Folium Térkép v3.0")
        register_widget_for_theming(controls_group, "container")
        controls_layout = QHBoxLayout(controls_group)

        style_label = QLabel("Stílus:")
        register_widget_for_theming(style_label, "text")
        controls_layout.addWidget(style_label)

        self.style_combo = QComboBox()
        self.style_combo.addItems([
            "OpenStreetMap",
            "CartoDB positron",
            "CartoDB dark_matter",
            "Stamen Terrain",
            "Stamen Toner"
        ])
        self.style_combo.setCurrentText(self.map_config.tiles)
        register_widget_for_theming(self.style_combo, "input")
        controls_layout.addWidget(self.style_combo)

        self.counties_check = QCheckBox("Megyehatárok")
        self.counties_check.setChecked(True)
        register_widget_for_theming(self.counties_check, "input")
        controls_layout.addWidget(self.counties_check)

        self.weather_check = QCheckBox("Időjárási overlay")
        self.weather_check.setChecked(False)
        register_widget_for_theming(self.weather_check, "input")
        controls_layout.addWidget(self.weather_check)

        self.overlay_parameter_label = QLabel("🎨 Overlay: Nincs")
        overlay_param_font = self.overlay_parameter_label.font()
        overlay_param_font.setPointSize(9)
        self.overlay_parameter_label.setFont(overlay_param_font)
        self.overlay_parameter_label.setStyleSheet("color: #9B59B6; font-weight: bold;")
        register_widget_for_theming(self.overlay_parameter_label, "text")
        controls_layout.addWidget(self.overlay_parameter_label)

        self.server_status_label = QLabel("🌐 Szerver: Indítás...")
        server_font = self.server_status_label.font()
        server_font.setPointSize(9)
        self.server_status_label.setFont(server_font)
        self.server_status_label.setStyleSheet("color: #3498DB; font-weight: bold;")
        register_widget_for_theming(self.server_status_label, "text")
        controls_layout.addWidget(self.server_status_label)

        zoom_label = QLabel("Zoom:")
        register_widget_for_theming(zoom_label, "text")
        controls_layout.addWidget(zoom_label)

        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setRange(6, 12)
        self.zoom_slider.setValue(7)
        register_widget_for_theming(self.zoom_slider, "input")
        controls_layout.addWidget(self.zoom_slider)

        controls_layout.addStretch()

        self.refresh_btn = QPushButton("🔄 Frissítés")
        register_widget_for_theming(self.refresh_btn, "button")
        controls_layout.addWidget(self.refresh_btn)

        self.export_btn = QPushButton("💾 Export")
        register_widget_for_theming(self.export_btn, "button")
        controls_layout.addWidget(self.export_btn)

        self.reset_btn = QPushButton("🏠 Alaphelyzet")
        register_widget_for_theming(self.reset_btn, "button")
        controls_layout.addWidget(self.reset_btn)

        layout.addWidget(controls_group)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        register_widget_for_theming(self.progress_bar, "input")
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("🌐 HTTP szerver Folium térkép inicializálása...")
        register_widget_for_theming(self.status_label, "text")
        layout.addWidget(self.status_label)

        self.web_view = QWebEngineView()
        register_widget_for_theming(self.web_view, "container")

        try:
            from PySide6.QtWebEngineCore import QWebEngineSettings
            settings = self.web_view.settings()
            settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
            settings.setAttribute(QWebEngineSettings.ErrorPageEnabled, True)
            settings.setAttribute(QWebEngineSettings.WebGLEnabled, True)
            settings.setAttribute(QWebEngineSettings.Accelerated2dCanvasEnabled, True)
            settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
            settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        except ImportError:
            pass

        self.web_channel.registerObject("qtBridge", self.js_bridge)
        self.web_view.page().setWebChannel(self.web_channel)
        layout.addWidget(self.web_view)

        layout.setStretchFactor(controls_group, 0)
        layout.setStretchFactor(self.web_view, 1)

    def _setup_theme(self) -> None:
        register_widget_for_theming(self, "container")

    def _connect_signals(self) -> None:
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

    def _start_local_server(self) -> None:
        if self.local_server and self.local_server.running:
            return

        self.local_server = LocalHttpServerThread(self)
        self.local_server.server_ready.connect(self._on_server_ready)
        self.local_server.server_error.connect(self._on_server_error)
        self.local_server.start()

    def _on_server_ready(self, host: str, port: int) -> None:
        self.http_host = host
        self.http_port = port
        self.server_status_label.setText(f"🌐 Szerver: http://{host}:{port}")
        self.server_status_label.setStyleSheet("color: #27AE60; font-weight: bold;")

        if FOLIUM_AVAILABLE:
            self._generate_default_map()

    def _on_server_error(self, error_message: str) -> None:
        self.server_status_label.setText("🌐 Szerver: HIBA")
        self.server_status_label.setStyleSheet("color: #E74C3C; font-weight: bold;")
        self.error_occurred.emit(f"HTTP szerver hiba: {error_message}")

    def _show_folium_error(self) -> None:
        self.status_label.setText("⚠️ Folium library hiányzik! pip install folium")
        self.progress_bar.setVisible(False)
        self.refresh_btn.setEnabled(False)
        self.export_btn.setEnabled(False)
        self.error_occurred.emit("Folium library not installed. Please run: pip install folium branca")

    def _generate_default_map(self) -> None:
        if not FOLIUM_AVAILABLE or not self.http_host or not self.http_port:
            return
        self._start_map_generation()

    def _start_map_generation(self) -> None:
        if not FOLIUM_AVAILABLE:
            self._show_folium_error()
            return
        if not self.http_host or not self.http_port:
            return
        if self.map_generator and self.map_generator.isRunning():
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("🌐 HTTP szerver Folium térkép generálása...")

        self.map_generator = FoliumMapGenerator(
            config=self.map_config,
            counties_gdf=self.counties_gdf,
            weather_data=self.current_weather_data,
            bridge_id=self.js_bridge.bridge_id
        )
        self.map_generator.progress_updated.connect(self.progress_bar.setValue)
        self.map_generator.status_updated.connect(self.status_label.setText)
        self.map_generator.map_generated.connect(self._on_map_generated)
        self.map_generator.error_occurred.connect(self._on_map_error)
        self.map_generator.start()

    def _on_map_generated(self, file_path: str) -> None:
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
        self.progress_bar.setVisible(False)
        self.status_label.setText("❌ Folium térkép generálási hiba!")
        self.error_occurred.emit(error_message)

    def _on_map_loaded(self, success: bool) -> None:
        if success:
            self.map_ready.emit()
            counties_info = f" ({len(self.counties_gdf)} megye)" if self.counties_gdf is not None else ""
            self.status_label.setText(f"🌐 HTTP szerver interaktív térkép kész!{counties_info}")
        else:
            self.error_occurred.emit("WebEngine HTTP loading failed")
            self.status_label.setText("❌ WebEngine HTTP betöltés sikertelen!")

    def _on_style_changed(self, style: str) -> None:
        self.map_config.tiles = style

    def _on_counties_toggled(self, checked: bool) -> None:
        self.map_config.show_counties = checked

    def _on_weather_toggled(self, checked: bool) -> None:
        self.map_config.weather_overlay = checked

    def _on_zoom_changed(self, zoom: int) -> None:
        self.map_config.zoom_start = zoom

    def _on_js_county_clicked(self, county_name: str) -> None:
        self.map_config.selected_county = county_name
        self.county_clicked.emit(county_name)

    def _on_js_coordinates_clicked(self, lat: float, lon: float) -> None:
        self.coordinates_clicked.emit(lat, lon)

    def _on_js_map_moved(self, lat: float, lon: float, zoom: int) -> None:
        self.map_config.center_lat = lat
        self.map_config.center_lon = lon
        self.map_config.zoom_start = zoom
        self.zoom_slider.setValue(zoom)
        self.map_moved.emit(lat, lon, zoom)

    def _on_js_county_hovered(self, county_name: str) -> None:
        self.county_hovered.emit(county_name)

    def _refresh_map(self) -> None:
        self._start_map_generation()

    def _export_map(self) -> None:
        if not self.current_map_file or not os.path.exists(self.current_map_file):
            QMessageBox.warning(self, "Export", "Nincs Folium térkép az exportáláshoz!")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "HTTP szerver Folium térkép exportálása",
            f"hungarian_folium_map_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
            "HTML fájlok (*.html);;Minden fájl (*)"
        )

        if file_path:
            try:
                shutil.copy2(self.current_map_file, file_path)
                self.export_completed.emit(file_path)
                QMessageBox.information(self, "Export", f"HTTP szerver Folium térkép sikeresen exportálva:\n{file_path}")
            except Exception as e:
                error_msg = f"Export hiba: {e}"
                self.error_occurred.emit(error_msg)
                QMessageBox.critical(self, "Export hiba", error_msg)

    def set_active_overlay_parameter(self, parameter: str) -> None:
        self.map_config.active_overlay_parameter = parameter

        parameter_display_names = {
            "temperature": "🌡️ Hőmérséklet",
            "wind_speed": "💨 Szélsebesség",
            "precipitation": "🌧️ Csapadék",
            "wind_gusts": "🌪️ Széllökések",
            "humidity": "💧 Páratartalom"
        }

        display_name = parameter_display_names.get(parameter, f"🎨 {parameter}")
        self.overlay_parameter_label.setText(f"🎨 Overlay: {display_name}")

    def clear_active_overlay_parameter(self) -> None:
        self.map_config.active_overlay_parameter = None
        self.overlay_parameter_label.setText("🎨 Overlay: Nincs")
        self.overlay_parameter_label.setStyleSheet("color: #95A5A6;")

    def get_active_overlay_parameter(self) -> Optional[str]:
        return self.map_config.active_overlay_parameter

    def set_counties_geodataframe(self, counties_gdf) -> None:
        print(f"🗺️ 🚀 REAKTÍV: Counties GeoDataFrame set: {len(counties_gdf) if counties_gdf is not None else 0} counties")
        self.counties_gdf = counties_gdf

        if counties_gdf is not None and len(counties_gdf) > 0:
            self.map_config.show_counties = True
            self.counties_check.setChecked(True)
            self._start_map_generation()

    def set_weather_data(self, weather_data: Dict) -> None:
        print(f"🌤️ 🚀 REAKTÍV: Real weather data set for HTTP server Folium overlay")
        self.current_weather_data = weather_data

        if weather_data:
            for data_type in weather_data.keys():
                if data_type in ['temperature', 'wind_speed', 'precipitation', 'wind_gusts']:
                    self.set_active_overlay_parameter(data_type)

            self.map_config.weather_overlay = True
            self.weather_check.setChecked(True)
            self._start_map_generation()

    def update_map_bounds(self, bounds: Tuple[float, float, float, float]) -> None:
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

    def get_map_config(self) -> FoliumMapConfig:
        return self.map_config

    def reset_map_view(self) -> None:
        self.map_config.center_lat = 47.1625
        self.map_config.center_lon = 19.5033
        self.map_config.zoom_start = 7
        self.map_config.selected_county = None
        self.map_config.highlighted_counties = []
        self.clear_active_overlay_parameter()
        self.zoom_slider.setValue(7)
        self.style_combo.setCurrentText("OpenStreetMap")
        self._start_map_generation()

    def set_map_style(self, style: str) -> None:
        if style in ["light", "bright"]:
            map_style = "CartoDB positron"
        elif style in ["dark", "night"]:
            map_style = "CartoDB dark_matter"
        else:
            map_style = "OpenStreetMap"

        self.style_combo.setCurrentText(map_style)
        self.map_config.tiles = map_style
        self.map_config.theme = style

    def toggle_counties(self, show: bool) -> None:
        self.counties_check.setChecked(show)

    def toggle_weather_overlay(self, show: bool) -> None:
        self.weather_check.setChecked(show)

    def set_selected_county(self, county_name: str) -> None:
        self.map_config.selected_county = county_name
        self._start_map_generation()

    def highlight_counties(self, county_names: List[str]) -> None:
        self.map_config.highlighted_counties = county_names

    def is_folium_available(self) -> bool:
        return FOLIUM_AVAILABLE

    def get_javascript_bridge(self) -> JavaScriptBridge:
        return self.js_bridge

    def generate_demo_weather_data(self) -> Dict:
        """Demo időjárási adatok generálása teszteléshez."""
        return generate_demo_weather_data()

    def get_http_server_info(self) -> Dict:
        """HTTP szerver információk lekérdezése."""
        return get_http_server_info(self.local_server, self.http_host, self.http_port, self.current_map_file)

    def get_dynamic_gradient_info(self) -> Dict:
        """Dinamikus gradient információk lekérdezése."""
        return get_dynamic_gradient_info(self.get_active_overlay_parameter())

    def get_current_map_file(self) -> Optional[str]:
        return self.current_map_file

    def get_http_debug_info(self) -> Dict:
        """HTTP szerver verzió debug információk."""
        return get_http_debug_info(
            self.local_server,
            self.http_host,
            self.http_port,
            self.current_map_file,
            self.counties_gdf,
            self.current_weather_data
        )

    def cleanup(self) -> None:
        if self.local_server and self.local_server.running:
            print("🛑 Stopping local HTTP server...")
            self.local_server.stop()
            self.local_server.wait()

        if self.current_map_file and os.path.exists(self.current_map_file):
            try:
                os.remove(self.current_map_file)
                print(f"🗑️ Temp map file removed: {self.current_map_file}")
            except Exception as e:
                print(f"⚠️ Failed to remove temp file: {e}")


# Export
__all__ = ['HungarianMapVisualizer']
