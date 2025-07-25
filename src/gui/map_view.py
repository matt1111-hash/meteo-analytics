#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🗺️ Map View - Teljes Magyar Térképes Nézet 
Magyar Klímaanalitika MVP - Interaktív Térképes Dashboard

Ez a modul a főablak térképes nézetét biztosítja, amely integrálja:
- HungarianMapTab: Teljes térképes funkcionalitás
- HungarianLocationSelector: Hierarchikus lokáció választó
- HungarianMapVisualizer: Folium interaktív térkép
- Signal forwarding: MainWindow integráció

FRISSÍTVE: Placeholder → HungarianMapTab valódi integráció

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
    🗺️ Map View Widget - Teljes magyar térképes nézet.
    
    Ez a widget a MainWindow térképes nézetét biztosítja, és integrálja
    a HungarianMapTab komponenst, ami tartalmazza:
    - Hierarchikus magyar lokáció választót (bal oldal)
    - Interaktív Folium térképet (jobb oldal)
    - Signal-slot integrációt
    - Export funkcionalitást
    
    SIGNALOK (forwarded):
    - location_selected(location_data): Lokáció kiválasztva
    - map_interaction(interaction_type, data): Térkép interakció
    - export_completed(file_path): Export befejezve
    - error_occurred(message): Hiba történt
    """
    
    # Forwarded signalok a HungarianMapTab-ból
    location_selected = Signal(object)        # Location data
    map_interaction = Signal(str, object)     # interaction_type, data
    export_completed = Signal(str)           # file_path
    error_occurred = Signal(str)             # error_message
    data_loading_completed = Signal()        # adatok betöltve
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Komponens referencia
        self.map_tab: Optional[HungarianMapTab] = None
        
        # UI építés
        self._setup_ui()
        self._setup_theme()
        self._connect_signals()
        
        print("🗺️ DEBUG: MapView initialized with HungarianMapTab integration")
    
    def _setup_ui(self):
        """
        🎨 UI komponensek létrehozása - HungarianMapTab integrációval.
        """
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # Teljes hely a map tab-nak
        layout.setSpacing(0)
        
        # HungarianMapTab létrehozása és hozzáadása
        self.map_tab = HungarianMapTab()
        layout.addWidget(self.map_tab)
        
        print("✅ DEBUG: MapView UI setup complete with HungarianMapTab")
    
    def _setup_theme(self):
        """
        🎨 Téma beállítások alkalmazása.
        """
        register_widget_for_theming(self, "container")
    
    def _connect_signals(self):
        """
        🔗 Signal forwarding beállítása HungarianMapTab-ból.
        """
        if self.map_tab:
            # Signal forwarding - HungarianMapTab signalok → MapView signalok
            self.map_tab.location_selected.connect(self.location_selected.emit)
            self.map_tab.map_interaction.connect(self.map_interaction.emit)
            self.map_tab.export_completed.connect(self.export_completed.emit)
            self.map_tab.error_occurred.connect(self.error_occurred.emit)
            self.map_tab.data_loading_completed.connect(self.data_loading_completed.emit)
            
            print("✅ DEBUG: MapView signal forwarding setup complete")
        else:
            print("❌ DEBUG: MapTab is None - cannot setup signal forwarding")
    
    # === PUBLIKUS API - HungarianMapTab DELEGÁLÁS ===
    
    def get_map_tab(self) -> Optional[HungarianMapTab]:
        """
        🗺️ HungarianMapTab referencia lekérdezése.
        
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
        🗺️ Map visualizer referencia lekérdezése (delegált).
        
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
        🎯 Térkép fókuszálása megyére (delegált).
        
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
    
    def get_map_status(self) -> str:
        """
        📊 Térkép státusz lekérdezése (delegált).
        
        Returns:
            Státusz szöveg
        """
        if self.map_tab:
            return self.map_tab.get_map_status()
        return "Térkép nem elérhető"
    
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
        🔄 Térkép visszaállítása alaphelyzetre (delegált).
        """
        if self.map_tab:
            # Reset gomb kattintás szimulálása
            self.map_tab._reset_map_view()
    
    def export_map(self):
        """
        💾 Térkép exportálása (delegált).
        """
        if self.map_tab:
            # Export gomb kattintás szimulálása
            self.map_tab._export_map()
    
    # === KÜLSŐ INTEGRÁCIÓ TÁMOGATÁS ===
    
    def set_weather_data(self, weather_data: Dict[str, Any]):
        """
        🌤️ Időjárási adatok beállítása térképes overlay-hez.
        
        Args:
            weather_data: Időjárási adatok dictionary
        """
        map_visualizer = self.get_map_visualizer()
        if map_visualizer:
            map_visualizer.set_weather_data(weather_data)
            print("🌤️ DEBUG: Weather data set for map overlay")
        else:
            print("⚠️ DEBUG: MapVisualizer not available for weather data")
    
    def update_from_location_selection(self, location_data: Dict[str, Any]):
        """
        📍 Külső lokáció kiválasztás alapján frissítés.
        
        Args:
            location_data: Lokáció adatok (pl. MainWindow ControlPanel-től)
        """
        # Ha van megye információ, beállítjuk
        county_name = location_data.get('county') or location_data.get('name')
        
        if county_name and self.focus_on_county(county_name):
            print(f"🎯 DEBUG: Map focused on county from external selection: {county_name}")
        else:
            print(f"⚠️ DEBUG: Could not focus on county from external selection: {county_name}")
    
    def get_integration_status(self) -> Dict[str, Any]:
        """
        📊 Integráció státusz információk lekérdezése.
        
        Returns:
            Integráció státusz dictionary
        """
        status = {
            "map_view_ready": self.map_tab is not None,
            "map_tab_ready": self.is_ready(),
            "location_selector_available": self.get_location_selector() is not None,
            "map_visualizer_available": self.get_map_visualizer() is not None,
            "current_location": self.get_current_location(),
            "available_counties_count": len(self.get_available_counties()),
            "map_status": self.get_map_status()
        }
        
        return status
    
    # === TÉMA INTEGRÁCIÓ ===
    
    def apply_theme(self, theme_name: str):
        """
        🎨 Téma alkalmazása a teljes térképes komponensre.
        
        Args:
            theme_name: Téma neve ("light" vagy "dark")
        """
        # A ThemeManager automatikusan kezeli a regisztrált widget-eket
        # De ha szükséges, itt lehet specifikus térképes téma logika
        
        # Map style frissítése téma alapján
        map_visualizer = self.get_map_visualizer()
        if map_visualizer:
            if theme_name == "dark":
                map_visualizer.set_map_style("CartoDB dark_matter")
            else:
                map_visualizer.set_map_style("OpenStreetMap")
        
        print(f"🎨 DEBUG: MapView theme applied: {theme_name}")


# === DEMO FUNKCIONALITÁS ===

def demo_map_view():
    """
    🧪 MapView demo alkalmazás (HungarianMapTab integrációval).
    """
    import sys
    from PySide6.QtWidgets import QApplication, QMainWindow
    
    app = QApplication(sys.argv)
    
    # Fő ablak
    window = QMainWindow()
    window.setWindowTitle("🗺️ MapView Demo - HungarianMapTab Integráció")
    window.setGeometry(100, 100, 1400, 900)
    
    # MapView létrehozása
    map_view = MapView()
    window.setCentralWidget(map_view)
    
    # Event handlers
    def on_location_selected(location):
        print(f"📍 DEMO: Location selected in MapView: {location.display_name if location else 'None'}")
    
    def on_map_interaction(interaction_type, data):
        print(f"🗺️ DEMO: Map interaction in MapView: {interaction_type} - {data}")
    
    def on_export_completed(file_path):
        print(f"💾 DEMO: Export completed in MapView: {file_path}")
    
    def on_data_loading_completed():
        print("✅ DEMO: MapView data loading completed!")
        
        # Integráció státusz kiírása
        status = map_view.get_integration_status()
        print("📊 DEMO: Integration status:")
        for key, value in status.items():
            print(f"   {key}: {value}")
    
    # Signalok kapcsolása
    map_view.location_selected.connect(on_location_selected)
    map_view.map_interaction.connect(on_map_interaction)
    map_view.export_completed.connect(on_export_completed)
    map_view.data_loading_completed.connect(on_data_loading_completed)
    
    window.show()
    
    print("🗺️ DEMO: MapView elindítva HungarianMapTab integrációval!")
    print("✅ A MapView most már tartalmazza:")
    print("   📍 HungarianLocationSelector (bal oldal)")
    print("   🗺️ HungarianMapVisualizer (jobb oldal)")
    print("   🔗 Signal forwarding MainWindow felé")
    print("   🎯 Teljes API delegálás")
    print("   🎨 Theme integráció")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    demo_map_view()