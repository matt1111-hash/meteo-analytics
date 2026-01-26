#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🗺️ Magyar Térképes Tab - Weather Data Integration + Analytics → Map Sync TELJES IMPLEMENTÁCIÓ
Magyar Klímaanalitika MVP - Multi-City Engine + Folium Weather Overlay Integráció + Analytics Sync

🔧 KRITIKUS JAVÍTÁS v3.0 - PARAMÉTER MEMÓRIA HOZZÁADÁSA:
✅ current_analytics_parameter memória hozzáadása
✅ set_analytics_parameter() metódus implementálása
✅ set_analytics_result() módosítása paraméter továbbításra
✅ MainWindow koordináció támogatás
✅ Enhanced debug logging minden lépéshez

🚀 KRITIKUS BREAKTHROUGH: ANALYTICS → MAP SYNC 100% BEFEJEZVE
- Analytics View paraméter változások → Automatic Map Tab sync
- 4 Új sync metódus teljes implementációja
- Helper metódusok minden sync típushoz
- Debug logging minden Analytics → Map sync eseményhez
- Error handling és fallback mechanizmusok
- Real-time weather overlay frissítés
- Comprehensive parameter bundle processing

🔧 ÚJ ANALYTICS → MAP SYNC FUNKCIÓK:
✅ update_analysis_parameters() - Analysis típus/régió/megye sync
✅ update_weather_parameters() - Provider/API/timeout sync  
✅ update_date_range() - Dátum tartomány sync
✅ refresh_with_new_parameters() - Komplex bundle sync
✅ 6 helper metódus minden sync típushoz
✅ Enhanced debug logging minden sync lépésnél
✅ Auto-refresh weather overlays parameter change-kor

Fájl helye: src/gui/hungarian_map_tab.py (ANALYTICS SYNC 100% KÉSZ + PARAMÉTER MEMÓRIA)
"""

from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QLabel,
    QGroupBox, QPushButton, QProgressBar, QMessageBox, QCheckBox
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont

# GUI modules (absolute imports for package compatibility)
from src.presentation.gui.hungarian_location_selector import HungarianLocationSelector
from src.presentation.gui.map import HungarianMapVisualizer
from src.presentation.gui.theme_manager import register_widget_for_theming
from src.presentation.gui.color_palette import ColorPalette
from src.presentation.gui.weather_data_bridge import WeatherDataBridge, WeatherOverlayData

# Analytics and data modules
from src.analytics.multi_city_engine import MultiCityEngine
from src.data.models import AnalyticsResult, AnalyticsQuestion
from src.data.enums import RegionScope, AnalyticsMetric, QuestionType

# Mixins for modular functionality
from .map_analytics_sync import MapAnalyticsSyncMixin
from .map_tab_ui import MapTabUIMixin


class HungarianMapTab(MapTabUIMixin, MapAnalyticsSyncMixin, QWidget):
    """
    🗺️ Magyar Térképes Tab - Weather Data Integration + Analytics → Map Sync TELJES IMPLEMENTÁCIÓ + PARAMÉTER MEMÓRIA.
    
    🔧 KRITIKUS JAVÍTÁS v3.0:
    - current_analytics_parameter memória hozzáadása
    - MainWindow koordináció javítása
    - Paraméter továbbítás WeatherDataBridge-nek
    - Enhanced debug logging minden analytics sync lépésnél
    
    KOMPONENSEK:
    - HungarianLocationSelector: Hierarchikus lokáció választó (bal oldal, 30%)
    - Folium HungarianMapVisualizer: Teljes interaktív térkép (jobb oldal, 70%)
    - WeatherDataBridge: Analytics → Folium konverzió (100% JAVÍTVA)
    - MultiCityEngine: Valós időjárási adatok lekérdezése
    
    🌤️ WEATHER FUNKCIÓK - 100% MŰKÖDŐKÉPES:
    - Analytics eredmények fogadása és térképes megjelenítése
    - Weather overlay automatikus generálás
    - Multi-City Engine integráció valós adatokkal
    - 4 weather típus támogatás (hőmérséklet, csapadék, szél, széllökés)
    - Valós idejű weather data frissítés
    - Format kompatibilitás HungarianMapVisualizer-rel
    
    🚀 ÚJ: ANALYTICS → MAP SYNC FUNKCIÓK - 100% IMPLEMENTÁLVA:
    - Analytics paraméter változások automatic sync
    - Weather provider változások sync
    - Dátum tartomány változások sync
    - Komplex parameter bundle processing
    - Real-time weather overlay refresh
    - Enhanced debug logging minden sync eseményhez
    
    SIGNALOK:
    - location_selected(location_data): Lokáció kiválasztva
    - county_clicked_on_map(county_name): Megye kattintva térképen
    - map_interaction(interaction_type, data): Térkép interakció
    - export_completed(file_path): Export befejezve
    - error_occurred(message): Hiba történt
    - folium_ready(): Folium térkép betöltve
    - weather_data_updated(overlay_data): Weather overlay frissítve
    - analytics_sync_completed(sync_type): Analytics sync befejezve
    """
    
    # Signalok
    location_selected = Signal(object)        # Location data kiválasztva
    county_clicked_on_map = Signal(str)       # Megye kattintva Folium térképen
    map_interaction = Signal(str, object)     # Térkép interakció (type, data)
    export_completed = Signal(str)           # Export fájl útvonal
    error_occurred = Signal(str)             # Hiba üzenet
    data_loading_started = Signal()          # Adatok betöltése kezdődött
    data_loading_completed = Signal()        # Adatok betöltése befejezve
    folium_ready = Signal()                  # Folium térkép betöltve
    weather_data_updated = Signal(object)    # 🌤️ Weather overlay frissítve
    analytics_sync_completed = Signal(str)   # 🚀 ÚJ: Analytics sync befejezve
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Komponens inicializálás
        self.color_palette = ColorPalette()
        
        # Komponens referenciák
        self.location_selector: Optional[HungarianLocationSelector] = None
        self.map_visualizer: Optional[HungarianMapVisualizer] = None
        
        # 🚀 Weather integráció komponensek
        self.weather_bridge: Optional[WeatherDataBridge] = None
        self.multi_city_engine: Optional[MultiCityEngine] = None
        
        # Adatok
        self.counties_gdf = None
        self.current_location_data = None
        self.is_data_loaded = False
        self.is_folium_ready = False
        
        # 🌤️ Weather data állapot
        self.current_analytics_result: Optional[AnalyticsResult] = None
        self.current_weather_overlay: Optional[WeatherOverlayData] = None
        self.weather_data_available = False
        
        # 🔧 KRITIKUS ÚJ: Analytics paraméter memória
        self.current_analytics_parameter: Optional[str] = None  # "Hőmérséklet", "Szél", "Csapadék"
        
        # 🚀 ÚJ: Analytics → Map Sync állapot
        self.last_analysis_parameters: Optional[Dict[str, Any]] = None
        self.last_weather_parameters: Optional[Dict[str, Any]] = None
        self.last_date_parameters: Optional[Dict[str, Any]] = None
        self.sync_in_progress = False
        self.auto_weather_refresh_enabled = True
        
        # Folium specifikus állapot
        self.current_theme = "light"
        self.auto_sync_enabled = True
        
        # UI építés
        self._setup_ui()
        self._setup_theme()
        self._connect_signals()
        
        # 🚀 Weather komponensek inicializálása
        self._initialize_weather_components()
        
        # Kezdeti állapot
        self._initialize_components()
        
        print("🗺️ DEBUG: HungarianMapTab initialized with Analytics → Map Sync TELJES IMPLEMENTÁCIÓ + PARAMÉTER MEMÓRIA v3.0")
    
    def _initialize_weather_components(self):
        """
        🌤️ Weather integráció komponensek inicializálása.
        """
        try:
            # Weather Data Bridge létrehozása
            self.weather_bridge = WeatherDataBridge()
            print("✅ DEBUG: WeatherDataBridge initialized")
            
            # Multi-City Engine létrehozása
            self.multi_city_engine = MultiCityEngine()
            print("✅ DEBUG: MultiCityEngine initialized")
            
        except Exception as e:
            print(f"❌ DEBUG: Weather components initialization error: {e}")
            self.weather_bridge = None
            self.multi_city_engine = None
    
    def _initialize_components(self):
        """
        🔧 Komponensek inicializálása és adatok betöltése - ANALYTICS SYNC VERZIÓ.
        """
        print("🔧 DEBUG: Initializing HungarianMapTab components with Analytics → Map Sync + Paraméter Memória...")
        
        # Loading indikáció
        self.loading_progress.setVisible(True)
        self.loading_progress.setValue(10)
        self.loading_status.setText("🔄 GeoJSON adatok + Weather komponensek + Analytics Sync + Paraméter Memória betöltése...")
        self.data_loading_started.emit()
        
        # Weather komponensek státusz frissítése
        if self.weather_bridge and self.multi_city_engine:
            self.weather_status_label.setText("🌤️ Weather: Kész")
            self.weather_status_label.setStyleSheet("color: #27AE60;")
        else:
            self.weather_status_label.setText("🌤️ Weather: Hiba")
            self.weather_status_label.setStyleSheet("color: #E74C3C;")
        
        # Analytics Sync komponensek státusz frissítése
        self.analytics_sync_label.setText("🔄 Analytics Sync: Kész")
        self.analytics_sync_label.setStyleSheet("color: #27AE60;")
        
        # Folium elérhetőség ellenőrzése
        if self.map_visualizer and not self.map_visualizer.is_folium_available():
            self.folium_status_label.setText("❌ Folium hiányzik")
            self.folium_status_label.setStyleSheet("color: #E74C3C;")
            self._show_folium_installation_message()
        else:
            self.folium_status_label.setText("✅ Folium elérhető")
            self.folium_status_label.setStyleSheet("color: #27AE60;")
        
        # Timer a folyamat szimulálásához és lépcsőzetes inicializáláshoz
        QTimer.singleShot(500, self._initialize_step_1)
    
    def _show_folium_installation_message(self):
        """
        ⚠️ Folium hiány esetén telepítési útmutató.
        """
        QMessageBox.information(
            self,
            "Folium Library Hiányzik",
            "A teljes interaktív térkép + weather overlay + analytics sync működéséhez szükséges a Folium library.\n\n"
            "Telepítés:\n"
            "pip install folium branca geopandas\n\n"
            "A térkép static módban fog működni Folium nélkül."
        )
    
    def _initialize_step_1(self):
        """
        Inicializálás 1. lépés: Location selector adatok.
        """
        print("🔧 DEBUG: Initialization step 1 - Location selector data")
        
        self.loading_progress.setValue(30)
        self.loading_status.setText("🔍 Lokáció választó inicializálása...")
        
        # Location selector már automatikusan indítja a GeoJSON betöltést
        # Várunk az adatok betöltésére
        QTimer.singleShot(1000, self._initialize_step_2)
    
    def _initialize_step_2(self):
        """
        Inicializálás 2. lépés: GeoDataFrame megosztás Folium-mal.
        """
        print("🔧 DEBUG: Initialization step 2 - GeoDataFrame sharing with Folium")
        
        self.loading_progress.setValue(60)
        self.loading_status.setText("🗺️ Folium térképes adatok megosztása...")
        
        # GeoDataFrame lekérdezése a location selector-től
        if self.location_selector:
            self.counties_gdf = self.location_selector.get_counties_geodataframe()
            
            if self.counties_gdf is not None:
                print(f"✅ DEBUG: Counties GeoDataFrame received: {len(self.counties_gdf)} counties")
                
                # GeoDataFrame átadása a Folium map visualizer-nek
                if self.map_visualizer:
                    self.map_visualizer.set_counties_geodataframe(self.counties_gdf)
                    print("✅ DEBUG: Counties GeoDataFrame shared with Folium MapVisualizer")
            else:
                print("⚠️ DEBUG: Counties GeoDataFrame not available yet")
        
        QTimer.singleShot(1000, self._initialize_step_3)
    
    def _initialize_step_3(self):
        """
        Inicializálás 3. lépés: Folium térkép generálás indítása.
        """
        print("🔧 DEBUG: Initialization step 3 - Folium map generation")
        
        self.loading_progress.setValue(80)
        self.loading_status.setText("🗺️ Folium interaktív térkép generálása...")
        
        # Folium térkép generálás indítása (ha elérhető)
        if self.map_visualizer and self.map_visualizer.is_folium_available():
            # A map_visualizer automatikusan indítja a Folium generálást
            pass
        
        QTimer.singleShot(1500, self._initialize_step_4)
    
    def _initialize_step_4(self):
        """
        Inicializálás 4. lépés: Finalizálás.
        """
        print("🔧 DEBUG: Initialization step 4 - Finalization")
        
        self.loading_progress.setValue(95)
        self.loading_status.setText("✅ Folium térképes dashboard + Weather integráció + Analytics Sync + Paraméter Memória finalizálása...")
        
        # Állapot frissítése
        self.is_data_loaded = True
        
        # Folium gombok engedélyezése (map_ready signal-ban később)
        
        QTimer.singleShot(500, self._initialization_complete)
    
    def _initialization_complete(self):
        """
        Inicializálás befejezése.
        """
        print("✅ DEBUG: HungarianMapTab initialization complete with Analytics → Map Sync + Paraméter Memória")
        
        self.loading_progress.setValue(100)
        self.loading_status.setText("✅ Magyar Folium térképes dashboard + Weather overlay + Analytics Sync + Paraméter Memória kész!")
        
        # Loading indikátorok elrejtése
        QTimer.singleShot(2000, self._hide_loading_indicators)
        
        # Completion signal
        self.data_loading_completed.emit()
    
    def _hide_loading_indicators(self):
        """
        Loading indikátorok elrejtése.
        """
        self.loading_progress.setVisible(False)
        self.loading_status.setText("🗺️ Kattints a megyékre a Folium térképen vagy használd a bal oldali választót + 🌤️ Töltsd be weather adatokat az Analytics-ból! 🔄 Analytics Sync + 🧠 Paraméter Memória aktív!")
    
    # === 🔧 KRITIKUS ÚJ METÓDUSOK - PARAMÉTER MEMÓRIA ===
    
    def set_analytics_parameter(self, parameter_name: str):
        """
        🧠 KRITIKUS ÚJ METÓDUS: Analytics paraméter beállítása - MainWindow koordinációhoz
        
        Ez a metódus a MainWindow-ból hívódik meg, hogy jelezze,
        milyen típusú paraméter várható (pl. 'Hőmérséklet', 'Szél', 'Csapadék').
        
        Args:
            parameter_name: Paraméter neve ('Hőmérséklet', 'Szél', 'Csapadék', stb.)
        """
        print(f"🧠 DEBUG: Analytics paraméter beállítva: {parameter_name}")
        
        # Paraméter mentése
        self.current_analytics_parameter = parameter_name
        
        # UI frissítése
        self.analytics_parameter_label.setText(f"🧠 Paraméter: {parameter_name}")
        self.analytics_parameter_label.setStyleSheet("color: #8E44AD; font-weight: bold;")
        
        # Status frissítése
        self.loading_status.setText(f"🧠 Analytics paraméter beállítva: {parameter_name} - várakozás eredményekre...")
        
        print(f"✅ DEBUG: Current analytics parameter stored: {self.current_analytics_parameter}")
    
    def set_analytics_result(self, analytics_result: AnalyticsResult):
        """
        🌤️ KRITIKUS MÓDOSÍTOTT METÓDUS: Analytics eredmény fogadása paraméter továbbításával
        
        Ez a metódus az Analytics View-től fogadja az eredményeket
        és automatikusan létrehozza a Folium weather overlay-t a tárolt paraméter alapján.
        
        Args:
            analytics_result: Multi-City Engine eredménye
        """
        print(f"🌤️ DEBUG: Analytics result received: {len(analytics_result.city_results) if analytics_result.city_results else 0} cities")
        print(f"🧠 DEBUG: Current stored parameter: {self.current_analytics_parameter}")
        
        self.current_analytics_result = analytics_result
        
        # 🔧 KRITIKUS: Weather overlay generálása paraméter továbbításával
        self._generate_weather_overlay_from_analytics(analytics_result)
    
    # === SIGNAL SLOT METÓDUSOK - LOCATION SELECTOR → FOLIUM ===
    
    def _on_county_selected(self, county_name: str, geometry):
        """
        🗺️ Megye kiválasztva a location selector-ben → Folium térkép frissítés.
        
        Args:
            county_name: Megye neve
            geometry: Megye geometria (Shapely objektum)
        """
        print(f"🗺️ DEBUG: County selected in LocationSelector: {county_name}")
        
        if not self.auto_sync_enabled:
            print("🔗 DEBUG: Auto-sync disabled, skipping Folium update")
            return
        
        if not self.map_visualizer or not self.is_folium_ready:
            print("⚠️ DEBUG: Folium MapVisualizer not ready for county selection")
            return
        
        try:
            # Geometry bounds lekérdezése
            bounds = geometry.bounds  # (minx, miny, maxx, maxy)
            print(f"🎯 DEBUG: County bounds: {bounds}")
            
            # Folium térkép bounds frissítése
            self.map_visualizer.update_map_bounds(bounds)
            
            # Kiválasztott megye beállítása Folium-ban
            self.map_visualizer.set_selected_county(county_name)
            
            # Status frissítése
            self.loading_status.setText(f"🎯 Folium térkép központosítva: {county_name}")
            
            # Forward signal
            self.map_interaction.emit("county_focused", {
                'county_name': county_name,
                'bounds': bounds,
                'source': 'location_selector'
            })
            
        except Exception as e:
            error_msg = f"Megye Folium térképes megjelenítési hiba: {e}"
            print(f"❌ DEBUG: {error_msg}")
            self._on_error_occurred(error_msg)
    
    def _on_map_update_requested(self, bounds):
        """
        🎯 Térkép frissítés kérés a location selector-től → Folium frissítés.
        
        Args:
            bounds: Térkép határok (minx, miny, maxx, maxy)
        """
        print(f"🎯 DEBUG: Map update requested with bounds: {bounds}")
        
        if self.map_visualizer and self.is_folium_ready and self.auto_sync_enabled:
            self.map_visualizer.update_map_bounds(bounds)
            self.loading_status.setText("🎯 Folium térkép frissítve")
        else:
            print("⚠️ DEBUG: Folium MapVisualizer not ready for bounds update")
    
    def _on_location_selected(self, location):
        """
        🔍 Lokáció kiválasztva a location selector-ben → forward signal.
        
        Args:
            location: Location objektum
        """
        print(f"🔍 DEBUG: Location selected: {location.display_name if location else 'None'}")
        
        self.current_location_data = location
        
        # Forward signal
        self.location_selected.emit(location)
        
        # Status frissítése
        if location:
            self.loading_status.setText(f"🔍 Kiválasztva: {location.display_name}")
    
    def _on_selection_changed(self):
        """
        🔄 Selection változás a location selector-ben.
        """
        print("🔄 DEBUG: Location selector selection changed")
        
        # Selection info lekérdezése
        if self.location_selector:
            selection_info = self.location_selector.get_current_selection()
            
            # Status frissítése
            region = selection_info.get('region')
            county = selection_info.get('county')
            
            if county:
                status = f"🗺️ {region.display_name if region else 'Régió'} → {county['name']}"
            elif region:
                status = f"🌡️ {region.display_name}"
            else:
                status = "🗺️ Válassz éghajlati régiót és megyét"
            
            self.loading_status.setText(status)
    
    # === SIGNAL SLOT METÓDUSOK - FOLIUM → LOCATION SELECTOR ===
    
    def _on_folium_map_ready(self):
        """
        ✅ Folium térkép kész és betöltve → funkciók engedélyezése.
        """
        print("✅ DEBUG: Folium map ready - enabling functionality")
        
        self.is_folium_ready = True
        
        # Export és refresh gombok engedélyezése
        self.export_map_btn.setEnabled(True)
        self.refresh_folium_btn.setEnabled(True)
        
        # 🌤️ Weather frissítés gomb engedélyezése
        if self.weather_bridge and self.multi_city_engine:
            self.refresh_weather_btn.setEnabled(True)
        
        # Folium status frissítése
        self.folium_status_label.setText("✅ Folium kész")
        self.folium_status_label.setStyleSheet("color: #27AE60;")
        
        # Status frissítése
        self.loading_status.setText("✅ Folium interaktív térkép kész! Kattints a megyékre vagy töltsd be weather adatokat! 🔄 Analytics Sync + 🧠 Paraméter Memória aktív!")
        
        # Forward signal
        self.folium_ready.emit()
    
    def _on_folium_county_clicked(self, county_name: str):
        """
        🖱️ Megye kattintás a Folium térképen → location selector frissítés.
        
        Args:
            county_name: Kattintott megye neve
        """
        print(f"🖱️ DEBUG: County clicked on Folium map: {county_name}")
        
        # Location selector county beállítása (ha auto-sync engedélyezve)
        if self.location_selector and self.auto_sync_enabled:
            success = self.location_selector.set_county(county_name)
            if success:
                print(f"✅ DEBUG: Location selector synced to county: {county_name}")
            else:
                print(f"⚠️ DEBUG: Failed to sync location selector to county: {county_name}")
        
        # Forward signal
        self.county_clicked_on_map.emit(county_name)
        self.map_interaction.emit("county_clicked", {
            'county_name': county_name,
            'source': 'folium_map'
        })
        
        # Status frissítése
        self.loading_status.setText(f"🖱️ Megye kattintva Folium térképen: {county_name}")
    
    def _on_folium_coordinates_clicked(self, lat: float, lon: float):
        """
        🔍 Koordináta kattintás a Folium térképen.
        
        Args:
            lat: Szélesség
            lon: Hosszúság
        """
        print(f"🔍 DEBUG: Coordinates clicked on Folium map: {lat:.4f}, {lon:.4f}")
        
        # Forward signal
        self.map_interaction.emit("coordinates_clicked", {
            'lat': lat,
            'lon': lon,
            'source': 'folium_map'
        })
        
        # Status frissítése
        self.loading_status.setText(f"🔍 Koordináta: {lat:.4f}°, {lon:.4f}°")
    
    def _on_folium_map_moved(self, lat: float, lon: float, zoom: int):
        """
        🗺️ Folium térkép mozgott (zoom/pan).
        
        Args:
            lat: Új központ szélesség
            lon: Új központ hosszúság  
            zoom: Új zoom szint
        """
        print(f"🗺️ DEBUG: Folium map moved: center=({lat:.4f}, {lon:.4f}), zoom={zoom}")
        
        # Forward signal
        self.map_interaction.emit("map_moved", {
            'lat': lat,
            'lon': lon,
            'zoom': zoom,
            'source': 'folium_map'
        })
    
    def _on_folium_county_hovered(self, county_name: str):
        """
        👆 Megye hover a Folium térképen.
        
        Args:
            county_name: Hover-elt megye neve
        """
        print(f"👆 DEBUG: County hovered on Folium map: {county_name}")
        
        # Status frissítése hover-rel
        self.loading_status.setText(f"👆 Hover: {county_name}")
        
        # Forward signal
        self.map_interaction.emit("county_hovered", {
            'county_name': county_name,
            'source': 'folium_map'
        })
    
    def _on_export_completed(self, file_path: str):
        """
        💾 Export befejezve → forward signal és status frissítés.
        
        Args:
            file_path: Exportált fájl útvonala
        """
        print(f"💾 DEBUG: Folium export completed: {file_path}")
        
        # Status frissítése
        self.loading_status.setText(f"💾 Folium térkép exportálva: {Path(file_path).name}")
        
        # Forward signal
        self.export_completed.emit(file_path)
    
    def _on_error_occurred(self, error_message: str):
        """
        ❌ Hiba történt → forward signal és status frissítés.
        
        Args:
            error_message: Hiba üzenet
        """
        print(f"❌ DEBUG: Folium error occurred: {error_message}")
        
        # Status frissítése
        self.loading_status.setText(f"❌ Folium hiba: {error_message}")
        
        # Forward signal
        self.error_occurred.emit(error_message)
    
    # === AKCIÓ METÓDUSOK - FOLIUM + ANALYTICS SYNC VERZIÓ ===
    
    def _on_auto_sync_toggled(self, enabled: bool):
        """
        🔗 Auto-szinkronizáció ki/bekapcsolása.
        
        Args:
            enabled: Engedélyezett-e az auto-sync
        """
        self.auto_sync_enabled = enabled
        print(f"🔗 DEBUG: Auto-sync {'enabled' if enabled else 'disabled'}")
        
        if enabled:
            self.loading_status.setText("🔗 Auto-szinkronizáció engedélyezve")
        else:
            self.loading_status.setText("🔗 Auto-szinkronizáció letiltva")
    
    def _on_auto_weather_refresh_toggled(self, enabled: bool):
        """
        🌤️ Auto weather refresh ki/bekapcsolása.
        
        Args:
            enabled: Engedélyezett-e az auto weather refresh
        """
        self.auto_weather_refresh_enabled = enabled
        print(f"🌤️ DEBUG: Auto weather refresh {'enabled' if enabled else 'disabled'}")
        
        if enabled:
            self.loading_status.setText("🌤️ Auto weather refresh engedélyezve")
        else:
            self.loading_status.setText("🌤️ Auto weather refresh letiltva")
    
    def _reset_map_view(self):
        """
        🔄 Folium térkép nézet visszaállítása Magyarország alapnézetére.
        """
        print("🔄 DEBUG: Resetting Folium map view to default Hungary view")
        
        if self.map_visualizer:
            self.map_visualizer.reset_map_view()
            self.loading_status.setText("🔄 Folium térkép visszaállítva alaphelyzetre")
        
        # Location selector reset
        if self.location_selector:
            self.location_selector.reset_selection()
        
        # Forward signal
        self.map_interaction.emit("view_reset", {
            'action': 'reset_to_hungary',
            'source': 'manual_reset'
        })
    
    def _export_map(self):
        """
        💾 Folium térkép exportálás kérése.
        """
        print("💾 DEBUG: Folium map export requested")
        
        if self.map_visualizer:
            # Export delegálása a Folium map visualizer-nek
            self.map_visualizer._export_map()
        else:
            error_msg = "Folium térkép nem elérhető az exportáláshoz"
            self._on_error_occurred(error_msg)
    
    def _refresh_folium_map(self):
        """
        🗺️ Folium térkép manuális újragenerálása.
        """
        print("🗺️ DEBUG: Manual Folium map refresh requested")
        
        if self.map_visualizer:
            self.map_visualizer._refresh_map()
            self.loading_status.setText("🔄 Folium térkép újragenerálása...")
        else:
            print("⚠️ DEBUG: Folium MapVisualizer not available for refresh")
    
    # === 🌤️ WEATHER INTEGRATION METÓDUSOK - 100% JAVÍTVA + PARAMÉTER TOVÁBBÍTÁS ===
    
    def _refresh_weather_overlay(self):
        """
        🌤️ Weather overlay manuális frissítése a jelenlegi analytics eredményekkel.
        """
        print("🌤️ DEBUG: Manual weather overlay refresh requested")
        
        if not self.current_analytics_result:
            self.loading_status.setText("⚠️ Nincs analytics eredmény a weather overlay frissítéséhez")
            return
        
        # Weather overlay újragenerálása
        self._generate_weather_overlay_from_analytics(self.current_analytics_result)
    
    def _generate_weather_overlay_from_analytics(self, analytics_result: AnalyticsResult):
        """
        🌤️ JAVÍTOTT + PARAMÉTER TOVÁBBÍTÁS: Weather overlay generálása Analytics eredményből + ENHANCED DEBUG.
        
        Args:
            analytics_result: Multi-City Engine eredménye
        """
        try:
            if not self.weather_bridge:
                error_msg = "WeatherDataBridge nem elérhető"
                print(f"❌ DEBUG: {error_msg}")
                self._on_error_occurred(error_msg)
                return
            
            print(f"🔄 DEBUG: Generating weather overlay from analytics result...")
            print(f"🔄 DEBUG: Analytics result - Cities: {len(analytics_result.city_results)}, Metric: {analytics_result.question.metric}")
            print(f"🧠 DEBUG: Stored parameter: {self.current_analytics_parameter}")
            
            # 🔧 KRITIKUS DEBUG: Analytics city results részletek
            print("🔄 DEBUG: City results details:")
            for i, city in enumerate(analytics_result.city_results[:5]):  # Első 5 város
                print(f"   City {i+1}: {city.city_name} - lat: {city.latitude}, lon: {city.longitude}, value: {city.value}")
            
            self.loading_status.setText("🌤️ Weather overlay generálása...")
            
            # 🔧 KRITIKUS JAVÍTÁS: Analytics eredmény → Weather overlay konverzió PARAMÉTER TOVÁBBÍTÁSÁVAL
            if self.current_analytics_parameter:
                # Explicit paraméter használata
                folium_format = self.weather_bridge.convert_analytics_result(analytics_result, self.current_analytics_parameter)
                print(f"🧠 DEBUG: Explicit parameter conversion: {self.current_analytics_parameter}")
            else:
                # Auto-detect fallback
                folium_format = self.weather_bridge.convert_analytics_result(analytics_result)
                print("🔄 DEBUG: Auto-detect parameter conversion")
            
            # Weather overlay generálás is
            weather_overlay = self.weather_bridge.convert_analytics_to_weather_overlay(analytics_result)
            
            if not weather_overlay or not folium_format:
                error_msg = "Weather overlay konverzió sikertelen"
                print(f"❌ DEBUG: {error_msg}")
                self._on_error_occurred(error_msg)
                return
            
            # Weather overlay mentése
            self.current_weather_overlay = weather_overlay
            self.weather_data_available = True
            
            print(f"✅ DEBUG: Weather overlay generated: {weather_overlay.overlay_type}, {len(weather_overlay.data)} cities")
            print(f"✅ DEBUG: Folium format generated: {list(folium_format.keys())}")
            
            # 🔧 KRITIKUS JAVÍTÁS: HungarianMapVisualizer kompatibilis formátum használata
            if self.map_visualizer and self.is_folium_ready:
                # 🚀 JAVÍTOTT: Direkt folium_format használata convert_overlay_to_folium_format helyett
                if folium_format:
                    self.map_visualizer.set_weather_data(folium_format)
                    print("✅ DEBUG: Weather data passed to Folium map visualizer (direct format)")
                    
                    # Status frissítés
                    self.weather_status_label.setText(f"🌤️ {weather_overlay.metadata['name']}: {weather_overlay.metadata['total_cities']} város")
                    self.weather_status_label.setStyleSheet("color: #27AE60;")
                    
                    self.loading_status.setText(f"🌤️ Weather overlay aktív: {weather_overlay.metadata['name']} ({weather_overlay.metadata['total_cities']} város)")
                    
                    # Signal kiküldése
                    self.weather_data_updated.emit(weather_overlay)
                else:
                    print("❌ DEBUG: Weather data format conversion failed")
                    self.loading_status.setText("❌ Weather overlay formátum konverzió sikertelen")
            else:
                print("⚠️ DEBUG: Folium map not ready for weather data")
                self.loading_status.setText("⚠️ Folium térkép nem kész a weather overlay-hez")
            
        except Exception as e:
            error_msg = f"Weather overlay generálási hiba: {e}"
            print(f"❌ DEBUG: {error_msg}")
            import traceback
            traceback.print_exc()
            self._on_error_occurred(error_msg)
    
    def load_weather_data_from_analytics(self, question_type: str, region: str = "HU", limit: int = 50):
        """
        🌤️ Weather adatok betöltése Multi-City Engine-ből és térkép frissítése.
        
        Ez a metódus közvetlenül a Multi-City Engine-t használja
        valós időjárási adatok lekérdezéséhez és térképes megjelenítéséhez.
        
        Args:
            question_type: Lekérdezés típusa (pl. "hottest_today")
            region: Régió (pl. "HU", "EU", "GLOBAL")
            limit: Eredmények száma
        """
        try:
            if not self.multi_city_engine:
                error_msg = "MultiCityEngine nem elérhető"
                print(f"❌ DEBUG: {error_msg}")
                self._on_error_occurred(error_msg)
                return
            
            print(f"🌤️ DEBUG: Loading weather data: {question_type}, {region}, limit={limit}")
            self.loading_status.setText(f"🌤️ Weather adatok betöltése: {question_type}...")
            
            # Paraméter beállítás question_type alapján
            QUERY_TYPE_TO_PARAMETER = {
                "hottest_today": "Hőmérséklet",
                "coldest_today": "Hőmérséklet", 
                "windiest_today": "Szél",        # ← EZ A KRITIKUS
                "wettest_today": "Csapadék",
                "temperature_range": "Hőmérséklet"
            }
            
            parameter = QUERY_TYPE_TO_PARAMETER.get(question_type, "Hőmérséklet")
            self.set_analytics_parameter(parameter)
            
            # Aktuális dátum
            from datetime import datetime
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Multi-City Engine lekérdezés
            analytics_result = self.multi_city_engine.analyze_multi_city(
                query_type=question_type,
                region=region,
                date=today,
                limit=limit
            )
            
            if analytics_result and analytics_result.city_results:
                print(f"✅ DEBUG: Weather data loaded: {len(analytics_result.city_results)} cities")
                
                # Analytics eredmény feldolgozása (automatikusan weather overlay-t generál)
                self.set_analytics_result(analytics_result)
                
            else:
                error_msg = f"Nincs weather adat: {question_type}"
                print(f"⚠️ DEBUG: {error_msg}")
                self.loading_status.setText(f"⚠️ {error_msg}")
            
        except Exception as e:
            error_msg = f"Weather adatok betöltési hiba: {e}"
            print(f"❌ DEBUG: {error_msg}")
            self._on_error_occurred(error_msg)
    
    # === PUBLIKUS API - ANALYTICS SYNC + WEATHER INTEGRATION 100% VERZIÓ + PARAMÉTER MEMÓRIA ===
    
    def get_location_selector(self) -> Optional[HungarianLocationSelector]:
        """
        🔍 Location selector referencia lekérdezése.
        
        Returns:
            HungarianLocationSelector példány vagy None
        """
        return self.location_selector
    
    def get_map_visualizer(self) -> Optional[HungarianMapVisualizer]:
        """
        🗺️ Folium map visualizer referencia lekérdezése.
        
        Returns:
            HungarianMapVisualizer példány vagy None
        """
        return self.map_visualizer
    
    def get_weather_bridge(self) -> Optional[WeatherDataBridge]:
        """
        🌤️ Weather data bridge referencia lekérdezése.
        
        Returns:
            WeatherDataBridge példány vagy None
        """
        return self.weather_bridge
    
    def get_multi_city_engine(self) -> Optional[MultiCityEngine]:
        """
        🌤️ Multi-city engine referencia lekérdezése.
        
        Returns:
            MultiCityEngine példány vagy None
        """
        return self.multi_city_engine
    
    def get_current_analytics_result(self) -> Optional[AnalyticsResult]:
        """
        🌤️ Jelenlegi analytics eredmény lekérdezése.
        
        Returns:
            AnalyticsResult objektum vagy None
        """
        return self.current_analytics_result
    
    def get_current_weather_overlay(self) -> Optional[WeatherOverlayData]:
        """
        🌤️ Jelenlegi weather overlay lekérdezése.
        
        Returns:
            WeatherOverlayData objektum vagy None
        """
        return self.current_weather_overlay
    
    def get_current_analytics_parameter(self) -> Optional[str]:
        """
        🧠 KRITIKUS ÚJ: Jelenlegi analytics paraméter lekérdezése.
        
        Returns:
            Analytics paraméter string vagy None
        """
        return self.current_analytics_parameter
    
    def has_weather_data(self) -> bool:
        """
        🌤️ Van-e betöltve weather adat.
        
        Returns:
            Van-e weather overlay adat
        """
        return self.weather_data_available and self.current_weather_overlay is not None
    
    def get_current_location(self):
        """
        🔍 Jelenlegi kiválasztott lokáció lekérdezése.
        
        Returns:
            Location objektum vagy None
        """
        return self.current_location_data
    
    def get_counties_geodataframe(self):
        """
        🗺️ Megyék GeoDataFrame lekérdezése.
        
        Returns:
            GeoPandas GeoDataFrame vagy None
        """
        return self.counties_gdf
    
    def set_region_and_county(self, region_key: str, county_name: str) -> bool:
        """
        🔍 Régió és megye programmatic beállítása.
        
        Args:
            region_key: Éghajlati régió kulcs
            county_name: Megye neve
            
        Returns:
            Sikeres volt-e a beállítás
        """
        if not self.location_selector:
            return False
        
        # Régió beállítása
        region_success = self.location_selector.set_region(region_key)
        if not region_success:
            return False
        
        # Megye beállítása
        county_success = self.location_selector.set_county(county_name)
        return county_success
    
    def focus_on_county(self, county_name: str) -> bool:
        """
        🎯 Folium térkép fókuszálása megadott megyére.
        
        Args:
            county_name: Megye neve
            
        Returns:
            Sikeres volt-e a fókuszálás
        """
        if self.counties_gdf is None:
            return False
        
        try:
            # Megye geometria keresése
            county_row = self.counties_gdf[self.counties_gdf['megye'] == county_name]
            if county_row.empty:
                return False
            
            geometry = county_row.geometry.iloc[0]
            bounds = geometry.bounds
            
            # Folium térkép frissítése
            if self.map_visualizer and self.is_folium_ready:
                self.map_visualizer.update_map_bounds(bounds)
                self.map_visualizer.set_selected_county(county_name)
                return True
            
        except Exception as e:
            print(f"❌ DEBUG: Focus on county error: {e}")
        
        return False
    
    def get_available_counties(self) -> List[str]:
        """
        📋 Elérhető megyék listája.
        
        Returns:
            Megyenevek listája
        """
        if self.location_selector:
            return self.location_selector.get_available_counties()
        return []
    
    def get_map_status(self) -> str:
        """
        📊 Térkép komponens státuszának lekérdezése.
        
        Returns:
            Státusz szöveg
        """
        return self.loading_status.text()
    
    def is_ready(self) -> bool:
        """
        ✅ Térképes tab kész használatra (Analytics Sync + Weather Integration 100% verzió + Paraméter Memória).
        
        Returns:
            Kész-e a használatra
        """
        return (
            self.is_data_loaded and 
            self.location_selector is not None and 
            self.map_visualizer is not None and
            self.counties_gdf is not None and
            self.is_folium_ready and
            self.weather_bridge is not None and
            self.multi_city_engine is not None
        )
    
    def is_folium_ready_status(self) -> bool:
        """
        ✅ Folium térkép kész használatra.
        
        Returns:
            Folium térkép kész-e
        """
        return self.is_folium_ready
    
    def set_theme(self, theme: str):
        """
        🎨 Téma beállítása Folium térképhez.
        
        Args:
            theme: Téma neve ("light" vagy "dark")
        """
        self.current_theme = theme
        
        if self.map_visualizer:
            self.map_visualizer.set_map_style(theme)
            print(f"🎨 DEBUG: Folium theme set to: {theme}")
    
    def set_weather_data(self, weather_data: Dict[str, Any]):
        """
        🌤️ DEPRECATED: Időjárási adatok beállítása Folium overlay-hez (legacy kompatibilitás).
        
        ÚJ: Használd a set_analytics_result() metódust WeatherDataBridge automatikus konverzióval!
        
        Args:
            weather_data: Időjárási adatok dictionary
        """
        if self.map_visualizer:
            self.map_visualizer.set_weather_data(weather_data)
            print("🌤️ DEBUG: Weather data set for Folium overlay (legacy method)")
    
    def refresh_all_components(self):
        """
        🔄 Összes komponens frissítése (Analytics Sync + Weather Integration 100% verzió + Paraméter Memória).
        """
        print("🔄 DEBUG: Refreshing all HungarianMapTab components with Analytics Sync + Weather Integration 100% + Paraméter Memória")
        
        # Location selector frissítése
        if self.location_selector:
            # GeoJSON adatok újratöltése
            self.location_selector._start_data_loading()
        
        # Folium map visualizer frissítése
        if self.map_visualizer:
            self.map_visualizer._refresh_map()
        
        # Weather overlay frissítése (ha van adat)
        if self.current_analytics_result:
            self._generate_weather_overlay_from_analytics(self.current_analytics_result)
        
        # Status frissítése
        self.loading_status.setText("🔄 Folium komponensek + Weather integráció + Analytics Sync 100% + Paraméter Memória frissítése...")
    
    def clear_selection(self):
        """
        🧹 Kiválasztás törlése minden komponensben (Analytics Sync + Weather Integration 100% verzió + Paraméter Memória).
        """
        print("🧹 DEBUG: Clearing all selections in HungarianMapTab with Analytics Sync + Weather Integration 100% + Paraméter Memória")
        
        # Location selector törlése
        if self.location_selector:
            self.location_selector.reset_selection()
        
        # Folium map reset
        if self.map_visualizer:
            self.map_visualizer.reset_map_view()
        
        # Weather data törlése
        self.current_analytics_result = None
        self.current_weather_overlay = None
        self.weather_data_available = False
        
        # 🧠 KRITIKUS ÚJ: Analytics paraméter törlése
        self.current_analytics_parameter = None
        self.analytics_parameter_label.setText("🧠 Paraméter: Nincs")
        self.analytics_parameter_label.setStyleSheet("color: #95A5A6;")
        
        # Analytics sync paraméterek törlése
        self.last_analysis_parameters = None
        self.last_weather_parameters = None
        self.last_date_parameters = None
        
        # Weather status frissítése
        self.weather_status_label.setText("🌤️ Weather: Nincs adat")
        self.weather_status_label.setStyleSheet("color: #E74C3C;")
        
        # Analytics sync status frissítése
        self.analytics_sync_label.setText("🔄 Analytics Sync: Kész")
        self.analytics_sync_label.setStyleSheet("color: #27AE60;")
        
        # Current data törlése
        self.current_location_data = None
        
        # Status frissítése
        self.loading_status.setText("🧹 Kiválasztás törölve - kattints a Folium térképre vagy töltsd be weather adatokat - Analytics Sync + Paraméter Memória aktív!")
    
    def toggle_auto_sync(self, enabled: bool):
        """
        🔗 Auto-szinkronizáció programmatic kapcsolása.
        
        Args:
            enabled: Engedélyezett-e az auto-sync
        """
        self.auto_sync_check.setChecked(enabled)
    
    def toggle_auto_weather_refresh(self, enabled: bool):
        """
        🌤️ Auto weather refresh programmatic kapcsolása.
        
        Args:
            enabled: Engedélyezett-e az auto weather refresh
        """
        self.auto_weather_refresh_check.setChecked(enabled)
    
    def get_analytics_sync_status(self) -> Dict[str, Any]:
        """
        🚀 Analytics → Map Sync státusz információk lekérdezése.
        
        Returns:
            Analytics sync státusz dictionary
        """
        return {
            "sync_in_progress": self.sync_in_progress,
            "auto_weather_refresh_enabled": self.auto_weather_refresh_enabled,
            "current_analytics_parameter": self.current_analytics_parameter,  # 🧠 ÚJ
            "last_analysis_parameters": self.last_analysis_parameters,
            "last_weather_parameters": self.last_weather_parameters,
            "last_date_parameters": self.last_date_parameters,
            "sync_methods_available": [
                "update_analysis_parameters",
                "update_weather_parameters", 
                "update_date_range",
                "refresh_with_new_parameters"
            ]
        }
    
    def get_integration_status(self) -> Dict[str, Any]:
        """
        📊 Analytics Sync + Weather Integration 100% + Paraméter Memória státusz információk lekérdezése.
        
        Returns:
            Teljes integráció státusz dictionary
        """
        status = {
            "data_loaded": self.is_data_loaded,
            "folium_ready": self.is_folium_ready,
            "auto_sync_enabled": self.auto_sync_enabled,
            "auto_weather_refresh_enabled": self.auto_weather_refresh_enabled,
            "location_selector_available": self.location_selector is not None,
            "map_visualizer_available": self.map_visualizer is not None,
            "folium_available": self.map_visualizer.is_folium_available() if self.map_visualizer else False,
            "weather_bridge_available": self.weather_bridge is not None,
            "multi_city_engine_available": self.multi_city_engine is not None,
            "weather_data_available": self.weather_data_available,
            "current_location": self.current_location_data,
            "current_analytics_result": self.current_analytics_result is not None,
            "current_analytics_parameter": self.current_analytics_parameter,  # 🧠 ÚJ
            "current_weather_overlay_type": self.current_weather_overlay.overlay_type if self.current_weather_overlay else None,
            "available_counties_count": len(self.get_available_counties()),
            "current_theme": self.current_theme,
            "map_status": self.get_map_status(),
            "analytics_sync_status": self.get_analytics_sync_status(),
            "sync_in_progress": self.sync_in_progress,
            "weather_integration_version": "100% BEFEJEZVE",
            "analytics_sync_version": "100% IMPLEMENTÁLVA",
            "parameter_memory_version": "v3.0 HOZZÁADVA"  # 🧠 ÚJ
        }
        
        return status


# Demo moved to src/gui/demos/map_tab_demo.py
# To run demo: python -m src.gui.demos.map_tab_demo


__all__ = ["HungarianMapTab"]
