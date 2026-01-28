#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Map Visualizer - UI Builder

🎨 UI elemek létrehozása a map visualizerhoz

Képességek:
- Controls panel létrehozása
- Web view setup
- Progress és status label setup

Fájl: src/presentation/gui/map/map_visualizer/ui_builder.py
"""

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGroupBox,
    QLabel,
    QProgressBar,
    QPushButton,
    QSlider,
)

from ...theme_manager import register_widget_for_theming

if TYPE_CHECKING:
    pass


def setup_map_visualizer_ui(self) -> None:
    """
    🗺️ Map Visualizer UI setup.

    Args:
        self: HungarianMapVisualizer instance
    """
    layout = layout = self.layout() if self.layout() else __import__('PySide6.QtWidgets').QtWidgets.QVBoxLayout(self)
    layout.setContentsMargins(5, 5, 5, 5)
    layout.setSpacing(5)

    controls_group = QGroupBox("🌐 HTTP Szerver Folium Térkép v3.0")
    register_widget_for_theming(controls_group, "container")
    controls_layout = __import__('PySide6.QtWidgets').QtWidgets.QHBoxLayout(controls_group)

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


def setup_web_view(self) -> None:
    """
    🌐 WebEngineView setup.

    Args:
        self: HungarianMapVisualizer instance
    """
    from PySide6.QtWebEngineWidgets import QWebEngineView

    layout = self.layout()

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

    layout.setStretchFactor(layout.itemAt(0).widget(), 0)
    layout.setStretchFactor(self.web_view, 1)
