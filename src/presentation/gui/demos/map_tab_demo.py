#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Hungarian Map Tab Demo Application.

Demo for testing HungarianMapTab with Analytics Sync and Weather Integration.
Extracted from hungarian_map_tab.py to reduce file size.
"""

import sys
from datetime import datetime, timedelta

from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


def demo_hungarian_map_tab() -> None:
    """Run Hungarian Map Tab demo application."""
    # Import here to avoid circular imports
    from src.presentation.gui.hungarian_map_tab import HungarianMapTab

    app = QApplication(sys.argv)

    window = QMainWindow()
    window.setWindowTitle(
        "Hungarian Map Tab Demo - Analytics Sync + Weather Integration"
    )
    window.setGeometry(100, 100, 1600, 1200)

    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    layout = QVBoxLayout(central_widget)

    # Parameter memory test buttons
    memory_controls = QWidget()
    memory_layout = QHBoxLayout(memory_controls)

    memory_title = QLabel("Parameter Memory Test:")
    memory_title.setStyleSheet("font-weight: bold; color: #8E44AD;")
    memory_layout.addWidget(memory_title)

    set_temp_btn = QPushButton("Temperature")
    set_wind_btn = QPushButton("Wind")
    set_precip_btn = QPushButton("Precipitation")
    clear_param_btn = QPushButton("Clear")

    memory_layout.addWidget(set_temp_btn)
    memory_layout.addWidget(set_wind_btn)
    memory_layout.addWidget(set_precip_btn)
    memory_layout.addWidget(clear_param_btn)
    memory_layout.addStretch()

    layout.addWidget(memory_controls)

    # Analytics Sync test buttons
    sync_controls = QWidget()
    sync_layout = QHBoxLayout(sync_controls)

    sync_title = QLabel("Analytics Sync Test:")
    sync_title.setStyleSheet("font-weight: bold; color: #3498DB;")
    sync_layout.addWidget(sync_title)

    analysis_sync_btn = QPushButton("Analysis Sync")
    weather_sync_btn = QPushButton("Weather Sync")
    date_sync_btn = QPushButton("Date Sync")
    bundle_sync_btn = QPushButton("Bundle Sync")

    sync_layout.addWidget(analysis_sync_btn)
    sync_layout.addWidget(weather_sync_btn)
    sync_layout.addWidget(date_sync_btn)
    sync_layout.addWidget(bundle_sync_btn)
    sync_layout.addStretch()

    layout.addWidget(sync_controls)

    # Weather test buttons
    weather_controls = QWidget()
    weather_layout = QHBoxLayout(weather_controls)

    weather_title = QLabel("Weather Integration Test:")
    weather_title.setStyleSheet("font-weight: bold; color: #27AE60;")
    weather_layout.addWidget(weather_title)

    hottest_btn = QPushButton("Hottest (HU)")
    coldest_btn = QPushButton("Coldest (HU)")
    wettest_btn = QPushButton("Wettest (HU)")
    windiest_btn = QPushButton("Windiest (HU)")

    weather_layout.addWidget(hottest_btn)
    weather_layout.addWidget(coldest_btn)
    weather_layout.addWidget(wettest_btn)
    weather_layout.addWidget(windiest_btn)
    weather_layout.addStretch()

    layout.addWidget(weather_controls)

    # Hungarian Map Tab
    map_tab = HungarianMapTab()
    layout.addWidget(map_tab)

    # Event handlers
    def on_location_selected(location):
        print(f"Location selected: {location.display_name if location else 'None'}")

    def on_county_clicked_on_map(county_name):
        print(f"County clicked on map: {county_name}")

    def on_map_interaction(interaction_type, data):
        print(f"Map interaction: {interaction_type} - {data}")

    def on_export_completed(file_path):
        print(f"Export completed: {file_path}")

    def on_error_occurred(message):
        print(f"Error: {message}")

    def on_folium_ready():
        print("Folium map ready!")
        status = map_tab.get_integration_status()
        print("Integration status:")
        for key, value in status.items():
            print(f"   {key}: {value}")

    def on_weather_data_updated(weather_overlay):
        print(
            f"Weather data updated: {weather_overlay.overlay_type}, {len(weather_overlay.data)} cities"
        )

    def on_analytics_sync_completed(sync_type):
        print(f"Analytics sync completed: {sync_type}")

    def on_data_loading_completed():
        print("Data loading completed!")

    # Parameter memory button handlers
    def test_set_temperature():
        map_tab.set_analytics_parameter("Hőmérséklet")

    def test_set_wind():
        map_tab.set_analytics_parameter("Szél")

    def test_set_precipitation():
        map_tab.set_analytics_parameter("Csapadék")

    def test_clear_parameter():
        map_tab.current_analytics_parameter = None
        map_tab.analytics_parameter_label.setText("Parameter: None")
        map_tab.analytics_parameter_label.setStyleSheet("color: #95A5A6;")

    # Analytics Sync button handlers
    def test_analysis_sync():
        params = {
            "analysis_type": "county",
            "county": "Budapest",
            "region": "central_hungary",
        }
        map_tab.update_analysis_parameters(params)

    def test_weather_sync():
        params = {
            "provider": "open-meteo",
            "timeout": 30,
            "cache": True,
            "timezone": "auto",
        }
        map_tab.update_weather_parameters(params)

    def test_date_sync():
        today = datetime.now()
        week_ago = today - timedelta(days=7)
        map_tab.update_date_range(
            week_ago.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")
        )

    def test_bundle_sync():
        bundle = {
            "analysis": {"analysis_type": "region", "region": "transdanubia"},
            "weather": {"provider": "meteostat", "cache": False},
            "date": {"start_date": "2024-01-01", "end_date": "2024-01-31"},
            "timestamp": datetime.now().isoformat(),
        }
        map_tab.refresh_with_new_parameters(bundle)

    # Weather button handlers
    def load_hottest():
        map_tab.set_analytics_parameter("Hőmérséklet")
        map_tab.load_weather_data_from_analytics("hottest_today", "HU", 20)

    def load_coldest():
        map_tab.set_analytics_parameter("Hőmérséklet")
        map_tab.load_weather_data_from_analytics("coldest_today", "HU", 20)

    def load_wettest():
        map_tab.set_analytics_parameter("Csapadék")
        map_tab.load_weather_data_from_analytics("wettest_today", "HU", 20)

    def load_windiest():
        map_tab.set_analytics_parameter("Szél")
        map_tab.load_weather_data_from_analytics("windiest_today", "HU", 20)

    # Button connections
    set_temp_btn.clicked.connect(test_set_temperature)
    set_wind_btn.clicked.connect(test_set_wind)
    set_precip_btn.clicked.connect(test_set_precipitation)
    clear_param_btn.clicked.connect(test_clear_parameter)

    analysis_sync_btn.clicked.connect(test_analysis_sync)
    weather_sync_btn.clicked.connect(test_weather_sync)
    date_sync_btn.clicked.connect(test_date_sync)
    bundle_sync_btn.clicked.connect(test_bundle_sync)

    hottest_btn.clicked.connect(load_hottest)
    coldest_btn.clicked.connect(load_coldest)
    wettest_btn.clicked.connect(load_wettest)
    windiest_btn.clicked.connect(load_windiest)

    # Signal connections
    map_tab.location_selected.connect(on_location_selected)
    map_tab.county_clicked_on_map.connect(on_county_clicked_on_map)
    map_tab.map_interaction.connect(on_map_interaction)
    map_tab.export_completed.connect(on_export_completed)
    map_tab.error_occurred.connect(on_error_occurred)
    map_tab.folium_ready.connect(on_folium_ready)
    map_tab.weather_data_updated.connect(on_weather_data_updated)
    map_tab.analytics_sync_completed.connect(on_analytics_sync_completed)
    map_tab.data_loading_completed.connect(on_data_loading_completed)

    window.show()
    print("Hungarian Map Tab Demo started!")

    sys.exit(app.exec())


if __name__ == "__main__":
    demo_hungarian_map_tab()
