#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mypy: ignore-errors

"""
Map View - Demo Functionality

🧪 Demo alkalmazás MapView teszteléséhez

Képességek:
- Demo alkalmazás indítása
- Signal tesztelés
- Debug információk megjelenítése

Fájl: src/presentation/gui/map_view/demo.py
"""

import sys

from PySide6.QtWidgets import QApplication, QMainWindow

from .core import MapView


def demo_map_view_folium() -> None:
    """
    🧪 MapView demo alkalmazás - Folium HungarianMapTab integrációval.
    """
    app = QApplication(sys.argv)

    # Fő ablak
    window = QMainWindow()
    window.setWindowTitle("🗺️ MapView Demo - Folium HungarianMapTab Integráció")
    window.setGeometry(100, 100, 1600, 1000)

    # MapView létrehozása
    map_view = MapView()
    window.setCentralWidget(map_view)

    # Event handlers
    def on_location_selected(location):
        print(
            f"📍 DEMO: Location selected in MapView: {location.display_name if location else 'None'}"
        )

    def on_county_clicked_on_map(county_name):
        print(f"🖱️ DEMO: County clicked on Folium map in MapView: {county_name}")

    def on_map_interaction(interaction_type, data):
        print(f"🗺️ DEMO: Map interaction in MapView: {interaction_type} - {data}")

    def on_export_completed(file_path):
        print(f"💾 DEMO: Export completed in MapView: {file_path}")

    def on_folium_ready():
        print("✅ DEMO: Folium map ready in MapView!")

        # Debug információk kiírása
        debug_info = map_view.get_debug_info()
        print("🐛 DEMO: Debug info:")
        for key, value in debug_info.items():
            print(f"   {key}: {value}")

        # Teszt funkciók
        print("🧪 DEMO: Testing Folium features...")

        # Téma váltás teszt
        map_view.set_theme("dark")

        # Auto-sync teszt
        map_view.toggle_auto_sync(True)

        # County highlight teszt
        map_view.highlight_counties(["Budapest", "Pest"])

    def on_data_loading_completed():
        print("✅ DEMO: MapView data loading completed!")

        # Integráció státusz kiírása
        status = map_view.get_integration_status()
        print("📊 DEMO: Folium integration status:")
        for key, value in status.items():
            print(f"   {key}: {value}")

    # Signalok kapcsolása
    map_view.location_selected.connect(on_location_selected)
    map_view.county_clicked_on_map.connect(on_county_clicked_on_map)
    map_view.map_interaction.connect(on_map_interaction)
    map_view.export_completed.connect(on_export_completed)
    map_view.folium_ready.connect(on_folium_ready)
    map_view.data_loading_completed.connect(on_data_loading_completed)

    window.show()

    print("🗺️ DEMO: MapView elindítva teljes Folium integrációval!")
    print("✅ A MapView most már tartalmazza:")
    print("   📍 HungarianLocationSelector (bal oldal)")
    print("   🗺️ Folium HungarianMapVisualizer (jobb oldal)")
    print("   🖱️ Kattintható megyék Folium térképen")
    print("   👆 Hover tooltipek")
    print("   🔗 Kétirányú auto-szinkronizáció")
    print("   📍 Koordináta kattintás")
    print("   🌉 JavaScript ↔ Python bridge")
    print("   🔗 Signal forwarding MainWindow felé")
    print("   🎯 Teljes API delegálás")
    print("   🎨 Folium theme integráció")
    print("   🌤️ Weather overlay support")
    print("   💾 Folium HTML export")

    sys.exit(app.exec())
