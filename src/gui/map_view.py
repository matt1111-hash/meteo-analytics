#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🗺️ Map View - Teljes Magyar Térképes Nézet - FOLIUM VERZIÓ
Magyar Klímaanalitika MVP - Folium Interaktív Térképes Dashboard

🚀 FRISSÍTVE: Teljes Folium támogatás
- HungarianMapTab: Folium interaktív térképes funkcionalitás
- Signal forwarding: Új Folium signalok támogatása
- JavaScript bridge events: County clicks, coordinates, hover
- Auto-sync: Kétirányú szinkronizáció támogatás
- Weather overlay: Folium heatmap integráció

Fájl helye: src/gui/map_view.py
"""

from typing import Optional, Dict, Any
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

# Saját modulok
from .hungarian_map_tab import HungarianMapTab
from .theme_manager import register_widget_for_theming


class MapView(QWidget):
    """
    🗺️ Map View Widget - Teljes magyar Folium térképes nézet.
    
    Ez a widget a MainWindow térképes nézetét biztosítja, és integrálja
    a HungarianMapTab komponenst Folium támogatással:
    - Hierarchikus magyar lokáció választót (bal oldal)
    - Folium interaktív térképet (jobb oldal)
    - JavaScript bridge támogatást
    - Kétirányú szinkronizációt
    - Weather overlay funkcionalitást
    - Export funkcionalitást
    
    🚀 FOLIUM SIGNALOK (forwarded):
    - location_selected(location_data): Lokáció kiválasztva
    - county_clicked_on_map(county_name): Megye kattintva Folium térképen
    - map_interaction(interaction_type, data): Térkép interakció
    - export_completed(file_path): Export befejezve
    - error_occurred(message): Hiba történt
    - folium_ready(): Folium térkép betöltve
    """
    
    # Forwarded signalok a HungarianMapTab-ból (Folium verzió)
    location_selected = Signal(object)        # Location data
    county_clicked_on_map = Signal(str)       # Folium county click
    map_interaction = Signal(str, object)     # interaction_type, data
    export_completed = Signal(str)           # file_path
    error_occurred = Signal(str)             # error_message
    data_loading_completed = Signal()        # adatok betöltve
    folium_ready = Signal()                  # Folium térkép kész
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Komponens referencia
        self.map_tab: Optional[HungarianMapTab] = None
        
        # UI építés
        self._setup_ui()
        self._setup_theme()
        self._connect_signals()
        
        print("🗺️ DEBUG: MapView initialized with Folium HungarianMapTab integration")
    
    def _setup_ui(self):
        """
        🎨 UI komponensek létrehozása - Folium HungarianMapTab integrációval.
        """
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # Teljes hely a map tab-nak
        layout.setSpacing(0)
        
        # Folium HungarianMapTab létrehozása és hozzáadása
        self.map_tab = HungarianMapTab()
        layout.addWidget(self.map_tab)
        
        print("✅ DEBUG: MapView UI setup complete with Folium HungarianMapTab")
    
    def _setup_theme(self):
        """
        🎨 Téma beállítások alkalmazása.
        """
        register_widget_for_theming(self, "container")
    
    def _connect_signals(self):
        """
        🔗 Signal forwarding beállítása Folium HungarianMapTab-ból.
        """
        if self.map_tab:
            # Signal forwarding - HungarianMapTab signalok → MapView signalok
            self.map_tab.location_selected.connect(self.location_selected.emit)
            self.map_tab.county_clicked_on_map.connect(self.county_clicked_on_map.emit)  # ÚJ!
            self.map_tab.map_interaction.connect(self.map_interaction.emit)
            self.map_tab.export_completed.connect(self.export_completed.emit)
            self.map_tab.error_occurred.connect(self.error_occurred.emit)
            self.map_tab.data_loading_completed.connect(self.data_loading_completed.emit)
            self.map_tab.folium_ready.connect(self.folium_ready.emit)  # ÚJ!
            
            print("✅ DEBUG: MapView Folium signal forwarding setup complete")
        else:
            print("❌ DEBUG: MapTab is None - cannot setup signal forwarding")
    
    # === PUBLIKUS API - FOLIUM HUNGARIANMAPTAB DELEGÁLÁS ===
    
    def get_map_tab(self) -> Optional[HungarianMapTab]:
        """
        🗺️ Folium HungarianMapTab referencia lekérdezése.
        
        Returns:
            HungarianMapTab példány vagy None
        """
        return self.map_tab
    
    def get_location_selector(self):
        """
        📍 Location selector referencia lekérdezése (delegált).
        
        Returns:
            HungarianLocationSelector példány vagy None
        """
        if self.map_tab:
            return self.map_tab.get_location_selector()
        return None
    
    def get_map_visualizer(self):
        """
        🗺️ Folium map visualizer referencia lekérdezése (delegált).
        
        Returns:
            HungarianMapVisualizer példány vagy None
        """
        if self.map_tab:
            return self.map_tab.get_map_visualizer()
        return None
    
    def get_current_location(self):
        """
        📍 Jelenlegi lokáció lekérdezése (delegált).
        
        Returns:
            Location objektum vagy None
        """
        if self.map_tab:
            return self.map_tab.get_current_location()
        return None
    
    def set_region_and_county(self, region_key: str, county_name: str) -> bool:
        """
        📍 Régió és megye beállítása (delegált).
        
        Args:
            region_key: Éghajlati régió kulcs
            county_name: Megye neve
            
        Returns:
            Sikeres volt-e a beállítás
        """
        if self.map_tab:
            return self.map_tab.set_region_and_county(region_key, county_name)
        return False
    
    def focus_on_county(self, county_name: str) -> bool:
        """
        🎯 Folium térkép fókuszálása megyére (delegált).
        
        Args:
            county_name: Megye neve
            
        Returns:
            Sikeres volt-e a fókuszálás
        """
        if self.map_tab:
            return self.map_tab.focus_on_county(county_name)
        return False
    
    def get_available_counties(self) -> list:
        """
        📋 Elérhető megyék listája (delegált).
        
        Returns:
            Megyenevek listája
        """
        if self.map_tab:
            return self.map_tab.get_available_counties()
        return []
    
    def is_ready(self) -> bool:
        """
        ✅ Térképes nézet kész használatra (delegált).
        
        Returns:
            Kész-e a használatra
        """
        if self.map_tab:
            return self.map_tab.is_ready()
        return False
    
    def is_folium_ready(self) -> bool:
        """
        ✅ Folium térkép kész használatra (delegált).
        
        Returns:
            Folium térkép kész-e
        """
        if self.map_tab:
            return self.map_tab.is_folium_ready()
        return False
    
    def get_map_status(self) -> str:
        """
        📊 Térkép státusz lekérdezése (delegált).
        
        Returns:
            Státusz szöveg
        """
        if self.map_tab:
            return self.map_tab.get_map_status()
        return "Folium térkép nem elérhető"
    
    def refresh_all_components(self):
        """
        🔄 Összes komponens frissítése (delegált).
        """
        if self.map_tab:
            self.map_tab.refresh_all_components()
    
    def clear_selection(self):
        """
        🧹 Kiválasztás törlése (delegált).
        """
        if self.map_tab:
            self.map_tab.clear_selection()
    
    def reset_map_view(self):
        """
        🔄 Folium térkép visszaállítása alaphelyzetre (delegált).
        """
        if self.map_tab:
            # Reset gomb kattintás szimulálása
            self.map_tab._reset_map_view()
    
    def export_map(self):
        """
        💾 Folium térkép exportálása (delegált).
        """
        if self.map_tab:
            # Export gomb kattintás szimulálása
            self.map_tab._export_map()
    
    # === ÚJ FOLIUM SPECIFIKUS API ===
    
    def set_theme(self, theme: str):
        """
        🎨 Téma beállítása Folium térképhez (delegált).
        
        Args:
            theme: Téma neve ("light" vagy "dark")
        """
        if self.map_tab:
            self.map_tab.set_theme(theme)
            print(f"🎨 DEBUG: MapView Folium theme set to: {theme}")
    
    def set_weather_data(self, weather_data: Dict[str, Any]):
        """
        🌤️ Időjárási adatok beállítása Folium overlay-hez (delegált).
        
        Args:
            weather_data: Időjárási adatok dictionary
        """
        if self.map_tab:
            self.map_tab.set_weather_data(weather_data)
            print("🌤️ DEBUG: Weather data set for Folium overlay via MapView")
    
    def toggle_auto_sync(self, enabled: bool):
        """
        🔗 Auto-szinkronizáció ki/bekapcsolása (delegált).
        
        Args:
            enabled: Engedélyezett-e az auto-sync
        """
        if self.map_tab:
            self.map_tab.toggle_auto_sync(enabled)
            print(f"🔗 DEBUG: MapView auto-sync {'enabled' if enabled else 'disabled'}")
    
    def get_javascript_bridge(self):
        """
        🌉 JavaScript bridge referencia lekérdezése (delegált).
        
        Returns:
            JavaScriptBridge példány vagy None
        """
        map_visualizer = self.get_map_visualizer()
        if map_visualizer:
            return map_visualizer.get_javascript_bridge()
        return None
    
    def refresh_folium_map(self):
        """
        🗺️ Folium térkép manuális újragenerálása (delegált).
        """
        if self.map_tab:
            self.map_tab._refresh_folium_map()
    
    # === KÜLSŐ INTEGRÁCIÓ TÁMOGATÁS - FOLIUM VERZIÓ ===
    
    def update_from_location_selection(self, location_data: Dict[str, Any]):
        """
        📍 Külső lokáció kiválasztás alapján frissítés.
        
        Args:
            location_data: Lokáció adatok (pl. MainWindow ControlPanel-től)
        """
        # Ha van megye információ, beállítjuk
        county_name = location_data.get('county') or location_data.get('name')
        
        if county_name and self.focus_on_county(county_name):
            print(f"🎯 DEBUG: Folium map focused on county from external selection: {county_name}")
        else:
            print(f"⚠️ DEBUG: Could not focus Folium map on county from external selection: {county_name}")
    
    def handle_external_county_click(self, county_name: str):
        """
        🖱️ Külső megye kattintás kezelése (pl. analytics view-ból).
        
        Args:
            county_name: Kattintott megye neve
        """
        if self.focus_on_county(county_name):
            print(f"🎯 DEBUG: Folium map focused on external county click: {county_name}")
            
            # Location selector szinkronizáció
            location_selector = self.get_location_selector()
            if location_selector:
                location_selector.set_county(county_name)
        else:
            print(f"⚠️ DEBUG: Could not handle external county click: {county_name}")
    
    def get_integration_status(self) -> Dict[str, Any]:
        """
        📊 Folium integráció státusz információk lekérdezése.
        
        Returns:
            Integráció státusz dictionary
        """
        if self.map_tab:
            # Base status from map_tab
            status = self.map_tab.get_integration_status()
            
            # Kiegészítés MapView specifikus infókkal
            status.update({
                "map_view_ready": True,
                "javascript_bridge_available": self.get_javascript_bridge() is not None,
                "folium_map_visualizer_available": self.get_map_visualizer() is not None,
                "external_integration_ready": self.is_folium_ready()
            })
        else:
            status = {
                "map_view_ready": False,
                "map_tab_available": False,
                "error": "HungarianMapTab not initialized"
            }
        
        return status
    
    # === ADVANCED FOLIUM FEATURES ===
    
    def highlight_counties(self, county_names: list):
        """
        ✨ Megyék kiemelése a Folium térképen (delegált).
        
        Args:
            county_names: Kiemelendő megyék nevei
        """
        map_visualizer = self.get_map_visualizer()
        if map_visualizer:
            map_visualizer.highlight_counties(county_names)
            print(f"✨ DEBUG: Highlighted counties on Folium map: {county_names}")
    
    def set_selected_county(self, county_name: str):
        """
        🎯 Kiválasztott megye beállítása Folium térképen (delegált).
        
        Args:
            county_name: Megye neve
        """
        map_visualizer = self.get_map_visualizer()
        if map_visualizer:
            map_visualizer.set_selected_county(county_name)
            print(f"🎯 DEBUG: Selected county set on Folium map: {county_name}")
    
    def toggle_weather_overlay(self, enabled: bool):
        """
        🌤️ Időjárási overlay ki/bekapcsolása (delegált).
        
        Args:
            enabled: Engedélyezett-e az overlay
        """
        map_visualizer = self.get_map_visualizer()
        if map_visualizer:
            map_visualizer.toggle_weather_overlay(enabled)
            print(f"🌤️ DEBUG: Folium weather overlay {'enabled' if enabled else 'disabled'}")
    
    def get_folium_map_config(self):
        """
        📋 Folium térkép konfiguráció lekérdezése (delegált).
        
        Returns:
            FoliumMapConfig objektum vagy None
        """
        map_visualizer = self.get_map_visualizer()
        if map_visualizer:
            return map_visualizer.get_map_config()
        return None
    
    # === TÉMA INTEGRÁCIÓ - FOLIUM VERZIÓ ===
    
    def apply_theme(self, theme_name: str):
        """
        🎨 Téma alkalmazása a teljes Folium térképes komponensre.
        
        Args:
            theme_name: Téma neve ("light" vagy "dark")
        """
        # ThemeManager automatikusan kezeli a regisztrált widget-eket
        
        # Folium map style frissítése téma alapján
        self.set_theme(theme_name)
        
        print(f"🎨 DEBUG: MapView Folium theme applied: {theme_name}")
    
    # === DEBUG ÉS MONITORING ===
    
    def get_debug_info(self) -> Dict[str, Any]:
        """
        🐛 Debug információk összegyűjtése.
        
        Returns:
            Debug információk dictionary
        """
        debug_info = {
            "map_view_initialized": self.map_tab is not None,
            "integration_status": self.get_integration_status(),
            "folium_ready": self.is_folium_ready(),
            "current_location": self.get_current_location(),
            "available_counties": len(self.get_available_counties()),
            "map_status": self.get_map_status()
        }
        
        # JavaScript Bridge info
        js_bridge = self.get_javascript_bridge()
        if js_bridge:
            debug_info["javascript_bridge_id"] = js_bridge.bridge_id
        
        # Folium Map Config info
        folium_config = self.get_folium_map_config()
        if folium_config:
            debug_info["folium_config"] = {
                "center_lat": folium_config.center_lat,
                "center_lon": folium_config.center_lon,
                "zoom_start": folium_config.zoom_start,
                "tiles": folium_config.tiles,
                "theme": folium_config.theme,
                "weather_overlay": folium_config.weather_overlay
            }
        
        return debug_info


# === DEMO FUNKCIONALITÁS - FOLIUM VERZIÓ ===

def demo_map_view_folium():
    """
    🧪 MapView demo alkalmazás - Folium HungarianMapTab integrációval.
    """
    import sys
    from PySide6.QtWidgets import QApplication, QMainWindow
    
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
        print(f"📍 DEMO: Location selected in MapView: {location.display_name if location else 'None'}")
    
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


if __name__ == "__main__":
    demo_map_view_folium()