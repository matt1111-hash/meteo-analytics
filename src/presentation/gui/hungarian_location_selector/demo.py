#!/usr/bin/env python3
# mypy: ignore-errors

"""
🗺️ Hungarian Location Selector - Demo
Magyar Klímaanalitika MVP - Demo és teszt funkciók
"""

import logging
import sys

from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)

logger = logging.getLogger(__name__)


def demo_hungarian_location_selector_with_state_management_fix():  # noqa: PLR0915
    """
    🧪 Hungarian Location Selector demo alkalmazás - GET_CURRENT_CITY() STATE MANAGEMENT FIX!
    """
    app = QApplication(sys.argv)

    # Fő ablak
    window = QMainWindow()
    window.setWindowTitle(
        "🗺️ Hungarian Location Selector Demo - GET_CURRENT_CITY() STATE MANAGEMENT FIX"
    )
    window.setGeometry(100, 100, 1200, 700)

    # Central widget
    central_widget = QWidget()
    window.setCentralWidget(central_widget)

    layout = QVBoxLayout(central_widget)

    # Információs header
    info_label = QLabel(
        "🔧 GET_CURRENT_CITY() STATE MANAGEMENT FIX: Enhanced debug logging + robust state handling!"
    )
    info_label.setStyleSheet(
        "background-color: #27AE60; color: white; padding: 10px; font-weight: bold;"
    )
    layout.addWidget(info_label)

    main_layout = QHBoxLayout()

    # Location selector
    from .core import HungarianLocationSelector

    location_selector = HungarianLocationSelector()
    main_layout.addWidget(location_selector)

    # Debug panel
    debug_panel = QWidget()
    debug_layout = QVBoxLayout(debug_panel)

    debug_label = QLabel("🔧 DEBUG INFORMÁCIÓK + QUERY_CONTROL_WIDGET KOMPATIBILITÁS:")
    debug_label.setStyleSheet("font-weight: bold; color: #E74C3C;")
    debug_layout.addWidget(debug_label)

    region_info_label = QLabel("Régió: -")
    county_info_label = QLabel("Megye: -")
    current_city_label = QLabel("get_current_city(): -")
    coordinates_label = QLabel("get_current_coordinates(): -")
    location_data_label = QLabel("get_selected_location_data(): -")
    is_valid_label = QLabel("is_valid(): -")

    debug_layout.addWidget(region_info_label)
    debug_layout.addWidget(county_info_label)
    debug_layout.addWidget(current_city_label)
    debug_layout.addWidget(coordinates_label)
    debug_layout.addWidget(location_data_label)
    debug_layout.addWidget(is_valid_label)
    debug_layout.addStretch()

    main_layout.addWidget(debug_panel)
    layout.addLayout(main_layout)

    # Event handlers
    def update_debug_info():
        """Debug információk frissítése."""
        # 🔧 JAVÍTOTT: QueryControlWidget kompatibilitási metódusok tesztelése
        current_city = location_selector.get_current_city()
        coordinates = location_selector.get_current_coordinates()
        location_data = location_selector.get_selected_location_data()
        is_valid = location_selector.is_valid()

        current_city_label.setText(f"get_current_city(): {current_city}")
        coordinates_label.setText(
            f"get_current_coordinates(): {coordinates[0]:.4f}, {coordinates[1]:.4f}"
        )
        location_data_label.setText(
            f"get_selected_location_data(): valid={location_data['valid']}, city={location_data['city']}"
        )
        is_valid_label.setText(f"is_valid(): {is_valid}")

    def on_region_selected(region_data):
        print(
            f"🏛️ Statisztikai régió kiválasztva: {region_data.display_name} ({region_data.nuts_code})"
        )
        print(f"   Megyék: {region_data.counties}")
        print(f"   Admin központ: {region_data.administrative_center}")

        region_info_label.setText(f"Régió: {region_data.display_name} ({region_data.nuts_code})")
        update_debug_info()

    def on_county_selected(county_name, geometry):
        print(f"🗺️ Megye kiválasztva: {county_name}")
        print(f"   Határok: {geometry.bounds}")

        county_info_label.setText(f"Megye: {county_name}")
        update_debug_info()

    def on_location_selected(location):
        print(f"📍 Lokáció kiválasztva: {location.display_name}")
        print(f"   Koordináták: {location.latitude:.4f}, {location.longitude:.4f}")
        print(f"   NUTS kód: {location.metadata.get('nuts_code', 'N/A')}")
        print(f"   Admin központ: {location.metadata.get('administrative_center', 'N/A')}")
        update_debug_info()

    def on_selection_changed():
        """Bármilyen változás esetén frissítjük a debug info-t."""
        update_debug_info()
        print(f"🔧 Selection changed - get_current_city(): {location_selector.get_current_city()}")

    def on_map_update_requested(bounds):
        print(f"🎯 Térkép frissítés: {bounds}")

    # Signalok kapcsolása
    location_selector.region_selected.connect(on_region_selected)
    location_selector.county_selected.connect(on_county_selected)
    location_selector.location_selected.connect(on_location_selected)
    location_selector.selection_changed.connect(on_selection_changed)
    location_selector.map_update_requested.connect(on_map_update_requested)

    window.show()

    print(
        "🗺️ Hungarian Location Selector Demo elindítva - GET_CURRENT_CITY() STATE MANAGEMENT JAVÍTVA!"
    )
    print("✅ JAVÍTÁSOK:")
    print("   🔧 _on_county_changed() enhanced debug logging")
    print("   🔧 get_current_city() robust defensive programming")
    print("   🔧 State management hiba kijavítva")
    print("   🔧 QueryControlWidget kompatibilitás 100% működőképes")
    print("   🔧 _update_debug_display() real-time state tracking")
    print()
    print("🧪 TESZT:")
    print("   1. Válassz 'Észak-Magyarország' régiót")
    print("   2. Ellenőrizd: Borsod-Abaúj-Zemplén, Heves, Nógrád megyék jelennek meg")
    print("   3. Válassz egy megyét (pl. 'Borsod-Abaúj-Zemplén')")
    print("   4. Ellenőrizd a debug panel-en: get_current_city() helyes értéket ad vissza!")
    print("   5. Ellenőrizd a konzol logging-ot a state frissítésről")
    print()
    print("🔧 QUERY_CONTROL_WIDGET KOMPATIBILITÁSI METÓDUSOK:")
    print("   • get_current_city() - Enhanced defensive programming")
    print("   • get_current_coordinates() - Robust koordináta visszaadás")
    print("   • get_selected_location_data() - Teljes lokáció adatok")
    print("   • is_valid() - Widget validálása")
    print("   • set_enabled() - Widget engedélyezése/letiltása")
    print()
    print("🚀 EREDMÉNY: QueryControlWidget validation sikeres lesz!")

    sys.exit(app.exec())


if __name__ == "__main__":
    demo_hungarian_location_selector_with_state_management_fix()
