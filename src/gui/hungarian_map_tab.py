#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🗺️ Magyar Térképes Tab - Teljes Interaktív Térképes Dashboard
Magyar Klímaanalitika MVP - HungarianLocationSelector + HungarianMapVisualizer Integráció

Ez a modul a teljes magyar térképes funkcionalitást biztosítja:
- Bal oldal: HungarianLocationSelector (hierarchikus választás)
- Jobb oldal: HungarianMapVisualizer (interaktív Folium térkép)
- Signal-slot integráció mindkét irányban
- GeoDataFrame megosztás a komponensek között
- ThemeManager integráció

WORKFLOW:
1. User kiválaszt éghajlati régiót → megyék frissülnek
2. User kiválaszt megyét → térkép rázoomol a megyére
3. Interaktív Folium térkép: hover, click, export funkciók
4. Kétirányú integráció: térkép click → location frissítés

Fájl helye: src/gui/hungarian_map_tab.py
"""

from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QLabel,
    QGroupBox, QPushButton, QProgressBar, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont

# Saját modulok
from .hungarian_location_selector import HungarianLocationSelector
from .map_visualizer import HungarianMapVisualizer
from .theme_manager import register_widget_for_theming
from .color_palette import ColorPalette


class HungarianMapTab(QWidget):
    """
    🗺️ Magyar Térképes Tab - Teljes interaktív térképes dashboard.
    
    KOMPONENSEK:
    - HungarianLocationSelector: Hierarchikus lokáció választó (bal oldal, 30%)
    - HungarianMapVisualizer: Interaktív Folium térkép (jobb oldal, 70%)
    - Signal-slot integráció: kétirányú kommunikáció
    - GeoDataFrame sharing: egyszer betöltés, kétszer használat
    
    FUNKCIÓK:
    - Éghajlati régió → megye hierarchikus választás
    - Megye kiválasztás → térkép automatikus központosítás
    - Interaktív térkép: zoom, pan, hover, tooltip
    - Térkép exportálás HTML formátumban
    - Theme-aware design
    
    SIGNALOK:
    - location_selected(location_data): Lokáció kiválasztva
    - map_interaction(interaction_type, data): Térkép interakció
    - export_completed(file_path): Export befejezve
    - error_occurred(message): Hiba történt
    """
    
    # Signalok
    location_selected = Signal(object)        # Location data kiválasztva
    map_interaction = Signal(str, object)     # Térkép interakció (type, data)
    export_completed = Signal(str)           # Export fájl útvonal
    error_occurred = Signal(str)             # Hiba üzenet
    data_loading_started = Signal()          # Adatok betöltése kezdődött
    data_loading_completed = Signal()        # Adatok betöltése befejezve
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Komponens inicializálás
        self.color_palette = ColorPalette()
        
        # Komponens referenciák
        self.location_selector: Optional[HungarianLocationSelector] = None
        self.map_visualizer: Optional[HungarianMapVisualizer] = None
        
        # Adatok
        self.counties_gdf = None
        self.current_location_data = None
        self.is_data_loaded = False
        
        # UI építés
        self._setup_ui()
        self._setup_theme()
        self._connect_signals()
        
        # Kezdeti állapot
        self._initialize_components()
        
        print("🗺️ DEBUG: HungarianMapTab initialized successfully")
    
    def _setup_ui(self):
        """
        🎨 UI komponensek létrehozása - QSplitter layout.
        """
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # === FEJLÉC ===
        
        header_group = QGroupBox("🗺️ Magyar Interaktív Térkép")
        register_widget_for_theming(header_group, "container")
        header_layout = QHBoxLayout(header_group)
        
        # Címsor
        title_label = QLabel("🇭🇺 Magyarország Éghajlati Térképe")
        title_font = title_label.font()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        register_widget_for_theming(title_label, "text")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Gyors akciók
        self.reset_view_btn = QPushButton("🔄 Alaphelyzet")
        self.reset_view_btn.setToolTip("Térkép visszaállítása Magyarország teljes nézetére")
        register_widget_for_theming(self.reset_view_btn, "button")
        header_layout.addWidget(self.reset_view_btn)
        
        self.export_map_btn = QPushButton("💾 Térkép Export")
        self.export_map_btn.setToolTip("Interaktív térkép exportálása HTML fájlba")
        self.export_map_btn.setEnabled(False)  # Kezdetben letiltva
        register_widget_for_theming(self.export_map_btn, "button")
        header_layout.addWidget(self.export_map_btn)
        
        layout.addWidget(header_group)
        
        # === PROGRESS BAR (KEZDETI BETÖLTÉSHEZ) ===
        
        self.loading_progress = QProgressBar()
        self.loading_progress.setRange(0, 100)
        self.loading_progress.setValue(0)
        self.loading_progress.setVisible(False)
        register_widget_for_theming(self.loading_progress, "input")
        layout.addWidget(self.loading_progress)
        
        self.loading_status = QLabel("Térképes komponensek inicializálása...")
        register_widget_for_theming(self.loading_status, "text")
        layout.addWidget(self.loading_status)
        
        # === FŐ SPLITTER LAYOUT ===
        
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.setHandleWidth(12)
        main_splitter.setChildrenCollapsible(False)
        register_widget_for_theming(main_splitter, "splitter")
        
        # === BAL OLDAL: LOCATION SELECTOR (30%) ===
        
        left_panel = QWidget()
        left_panel.setMinimumWidth(350)
        left_panel.setMaximumWidth(500)
        register_widget_for_theming(left_panel, "container")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(5, 5, 5, 5)
        
        # Location selector létrehozása
        self.location_selector = HungarianLocationSelector()
        left_layout.addWidget(self.location_selector)
        
        main_splitter.addWidget(left_panel)
        
        # === JOBB OLDAL: MAP VISUALIZER (70%) ===
        
        right_panel = QWidget()
        right_panel.setMinimumWidth(600)
        register_widget_for_theming(right_panel, "container")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(5, 5, 5, 5)
        
        # Map visualizer létrehozása
        self.map_visualizer = HungarianMapVisualizer()
        right_layout.addWidget(self.map_visualizer)
        
        main_splitter.addWidget(right_panel)
        
        # === SPLITTER KONFIGURÁLÁS ===
        
        # Stretch factors: Location selector fix, Map visualizer expandálható
        main_splitter.setStretchFactor(0, 0)  # Left panel fix
        main_splitter.setStretchFactor(1, 1)  # Right panel expand
        
        # Kezdeti méretek: 380px left, maradék right
        main_splitter.setSizes([380, 820])
        
        layout.addWidget(main_splitter)
        
        # Layout súlyok
        layout.setStretchFactor(header_group, 0)
        layout.setStretchFactor(main_splitter, 1)
        
        print("✅ DEBUG: HungarianMapTab UI setup complete")
    
    def _setup_theme(self):
        """
        🎨 Téma beállítások alkalmazása.
        """
        register_widget_for_theming(self, "container")
    
    def _connect_signals(self):
        """
        🔗 Signal-slot kapcsolatok létrehozása.
        """
        print("🔗 DEBUG: Connecting HungarianMapTab signals...")
        
        # === HEADER GOMBOK ===
        
        self.reset_view_btn.clicked.connect(self._reset_map_view)
        self.export_map_btn.clicked.connect(self._export_map)
        
        # === LOCATION SELECTOR → MAP VISUALIZER ===
        
        if self.location_selector:
            # Megye kiválasztás → térkép frissítés
            self.location_selector.county_selected.connect(self._on_county_selected)
            print("✅ DEBUG: LocationSelector.county_selected → MapTab._on_county_selected CONNECTED")
            
            # Térkép frissítés kérés → térkép bounds frissítés
            self.location_selector.map_update_requested.connect(self._on_map_update_requested)
            print("✅ DEBUG: LocationSelector.map_update_requested → MapTab._on_map_update_requested CONNECTED")
            
            # Lokáció kiválasztás → forward signal
            self.location_selector.location_selected.connect(self._on_location_selected)
            print("✅ DEBUG: LocationSelector.location_selected → MapTab._on_location_selected CONNECTED")
            
            # Általános selection változás
            self.location_selector.selection_changed.connect(self._on_selection_changed)
            print("✅ DEBUG: LocationSelector.selection_changed → MapTab._on_selection_changed CONNECTED")
        
        # === MAP VISUALIZER → LOCATION SELECTOR ===
        
        if self.map_visualizer:
            # Térkép kész → export engedélyezése
            self.map_visualizer.map_ready.connect(self._on_map_ready)
            print("✅ DEBUG: MapVisualizer.map_ready → MapTab._on_map_ready CONNECTED")
            
            # Megye kattintás a térképen → location selector frissítés
            self.map_visualizer.county_clicked.connect(self._on_map_county_clicked)
            print("✅ DEBUG: MapVisualizer.county_clicked → MapTab._on_map_county_clicked CONNECTED")
            
            # Export befejezés → forward signal
            self.map_visualizer.export_completed.connect(self._on_export_completed)
            print("✅ DEBUG: MapVisualizer.export_completed → MapTab._on_export_completed CONNECTED")
            
            # Hiba események → forward signal
            self.map_visualizer.error_occurred.connect(self._on_error_occurred)
            print("✅ DEBUG: MapVisualizer.error_occurred → MapTab._on_error_occurred CONNECTED")
        
        print("✅ DEBUG: All HungarianMapTab signals connected successfully")
    
    def _initialize_components(self):
        """
        🔧 Komponensek inicializálása és adatok betöltése.
        """
        print("🔧 DEBUG: Initializing HungarianMapTab components...")
        
        # Loading indikáció
        self.loading_progress.setVisible(True)
        self.loading_progress.setValue(10)
        self.loading_status.setText("🔄 GeoJSON adatok betöltése...")
        self.data_loading_started.emit()
        
        # Timer a folyamat szimulálásához és lépcsőzetes inicializáláshoz
        QTimer.singleShot(500, self._initialize_step_1)
    
    def _initialize_step_1(self):
        """
        Inicializálás 1. lépés: Location selector adatok.
        """
        print("🔧 DEBUG: Initialization step 1 - Location selector data")
        
        self.loading_progress.setValue(30)
        self.loading_status.setText("📍 Lokáció választó inicializálása...")
        
        # Location selector már automatikusan indítja a GeoJSON betöltést
        # Várunk az adatok betöltésére
        QTimer.singleShot(1000, self._initialize_step_2)
    
    def _initialize_step_2(self):
        """
        Inicializálás 2. lépés: GeoDataFrame megosztás.
        """
        print("🔧 DEBUG: Initialization step 2 - GeoDataFrame sharing")
        
        self.loading_progress.setValue(60)
        self.loading_status.setText("🗺️ Térképes adatok megosztása...")
        
        # GeoDataFrame lekérdezése a location selector-től
        if self.location_selector:
            self.counties_gdf = self.location_selector.get_counties_geodataframe()
            
            if self.counties_gdf is not None:
                print(f"✅ DEBUG: Counties GeoDataFrame received: {len(self.counties_gdf)} counties")
                
                # GeoDataFrame átadása a map visualizer-nek
                if self.map_visualizer:
                    self.map_visualizer.set_counties_geodataframe(self.counties_gdf)
                    print("✅ DEBUG: Counties GeoDataFrame shared with MapVisualizer")
            else:
                print("⚠️ DEBUG: Counties GeoDataFrame not available yet")
        
        QTimer.singleShot(1000, self._initialize_step_3)
    
    def _initialize_step_3(self):
        """
        Inicializálás 3. lépés: Finalizálás.
        """
        print("🔧 DEBUG: Initialization step 3 - Finalization")
        
        self.loading_progress.setValue(90)
        self.loading_status.setText("✅ Térképes dashboard inicializálása...")
        
        # Állapot frissítése
        self.is_data_loaded = True
        
        # Export gomb engedélyezése (ha térkép kész)
        if self.map_visualizer:
            # A map_ready signal automatikusan engedélyezi majd
            pass
        
        QTimer.singleShot(500, self._initialization_complete)
    
    def _initialization_complete(self):
        """
        Inicializálás befejezése.
        """
        print("✅ DEBUG: HungarianMapTab initialization complete")
        
        self.loading_progress.setValue(100)
        self.loading_status.setText("✅ Magyar térképes dashboard kész!")
        
        # Loading indikátorok elrejtése
        QTimer.singleShot(2000, self._hide_loading_indicators)
        
        # Completion signal
        self.data_loading_completed.emit()
    
    def _hide_loading_indicators(self):
        """
        Loading indikátorok elrejtése.
        """
        self.loading_progress.setVisible(False)
        self.loading_status.setText("🗺️ Használd a bal oldali választót a térkép navigálásához")
    
    # === SIGNAL SLOT METÓDUSOK ===
    
    def _on_county_selected(self, county_name: str, geometry):
        """
        🗺️ Megye kiválasztva a location selector-ben → térkép frissítés.
        
        Args:
            county_name: Megye neve
            geometry: Megye geometria (Shapely objektum)
        """
        print(f"🗺️ DEBUG: County selected: {county_name}")
        
        if not self.map_visualizer or not self.is_data_loaded:
            print("⚠️ DEBUG: MapVisualizer not ready for county selection")
            return
        
        try:
            # Geometry bounds lekérdezése
            bounds = geometry.bounds  # (minx, miny, maxx, maxy)
            print(f"🎯 DEBUG: County bounds: {bounds}")
            
            # Térkép bounds frissítése
            self.map_visualizer.update_map_bounds(bounds)
            
            # Status frissítése
            self.loading_status.setText(f"🎯 Térkép központosítva: {county_name}")
            
            # Forward signal
            self.map_interaction.emit("county_focused", {
                'county_name': county_name,
                'bounds': bounds
            })
            
        except Exception as e:
            error_msg = f"Megye térképes megjelenítési hiba: {e}"
            print(f"❌ DEBUG: {error_msg}")
            self._on_error_occurred(error_msg)
    
    def _on_map_update_requested(self, bounds):
        """
        🎯 Térkép frissítés kérés a location selector-től.
        
        Args:
            bounds: Térkép határok (minx, miny, maxx, maxy)
        """
        print(f"🎯 DEBUG: Map update requested with bounds: {bounds}")
        
        if self.map_visualizer and self.is_data_loaded:
            self.map_visualizer.update_map_bounds(bounds)
            self.loading_status.setText("🎯 Térkép frissítve")
        else:
            print("⚠️ DEBUG: MapVisualizer not ready for bounds update")
    
    def _on_location_selected(self, location):
        """
        📍 Lokáció kiválasztva a location selector-ben → forward signal.
        
        Args:
            location: Location objektum
        """
        print(f"📍 DEBUG: Location selected: {location.display_name if location else 'None'}")
        
        self.current_location_data = location
        
        # Forward signal
        self.location_selected.emit(location)
        
        # Status frissítése
        if location:
            self.loading_status.setText(f"📍 Kiválasztva: {location.display_name}")
    
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
    
    def _on_map_ready(self):
        """
        ✅ Térkép kész és betöltve → funkciók engedélyezése.
        """
        print("✅ DEBUG: Map ready - enabling export functionality")
        
        # Export gomb engedélyezése
        self.export_map_btn.setEnabled(True)
        
        # Status frissítése
        self.loading_status.setText("✅ Interaktív térkép kész! Navigálj a bal oldali választóval.")
    
    def _on_map_county_clicked(self, county_name: str):
        """
        🖱️ Megye kattintás a térképen → location selector frissítés.
        
        Args:
            county_name: Kattintott megye neve
        """
        print(f"🖱️ DEBUG: County clicked on map: {county_name}")
        
        # Location selector county beállítása
        if self.location_selector:
            success = self.location_selector.set_county(county_name)
            if success:
                print(f"✅ DEBUG: Location selector updated to county: {county_name}")
            else:
                print(f"⚠️ DEBUG: Failed to set county in location selector: {county_name}")
        
        # Forward signal
        self.map_interaction.emit("county_clicked", {
            'county_name': county_name,
            'source': 'map_click'
        })
    
    def _on_export_completed(self, file_path: str):
        """
        💾 Export befejezve → forward signal és status frissítés.
        
        Args:
            file_path: Exportált fájl útvonala
        """
        print(f"💾 DEBUG: Export completed: {file_path}")
        
        # Status frissítése
        self.loading_status.setText(f"💾 Térkép exportálva: {Path(file_path).name}")
        
        # Forward signal
        self.export_completed.emit(file_path)
    
    def _on_error_occurred(self, error_message: str):
        """
        ❌ Hiba történt → forward signal és status frissítés.
        
        Args:
            error_message: Hiba üzenet
        """
        print(f"❌ DEBUG: Error occurred: {error_message}")
        
        # Status frissítése
        self.loading_status.setText(f"❌ Hiba: {error_message}")
        
        # Forward signal
        self.error_occurred.emit(error_message)
    
    # === AKCIÓ METÓDUSOK ===
    
    def _reset_map_view(self):
        """
        🔄 Térkép nézet visszaállítása Magyarország alapnézetére.
        """
        print("🔄 DEBUG: Resetting map view to default Hungary view")
        
        if self.map_visualizer:
            self.map_visualizer.reset_map_view()
            self.loading_status.setText("🔄 Térkép visszaállítva alaphelyzetre")
        
        # Location selector reset
        if self.location_selector:
            self.location_selector.reset_selection()
        
        # Forward signal
        self.map_interaction.emit("view_reset", {
            'action': 'reset_to_hungary'
        })
    
    def _export_map(self):
        """
        💾 Térkép exportálás kérése.
        """
        print("💾 DEBUG: Map export requested")
        
        if self.map_visualizer:
            # Export delegálása a map visualizer-nek
            self.map_visualizer._export_map()
        else:
            error_msg = "Térkép nem elérhető az exportáláshoz"
            self._on_error_occurred(error_msg)
    
    # === PUBLIKUS API ===
    
    def get_location_selector(self) -> Optional[HungarianLocationSelector]:
        """
        📍 Location selector referencia lekérdezése.
        
        Returns:
            HungarianLocationSelector példány vagy None
        """
        return self.location_selector
    
    def get_map_visualizer(self) -> Optional[HungarianMapVisualizer]:
        """
        🗺️ Map visualizer referencia lekérdezése.
        
        Returns:
            HungarianMapVisualizer példány vagy None
        """
        return self.map_visualizer
    
    def get_current_location(self):
        """
        📍 Jelenlegi kiválasztott lokáció lekérdezése.
        
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
        📍 Régió és megye programmatic beállítása.
        
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
        🎯 Térkép fókuszálása megadott megyére.
        
        Args:
            county_name: Megye neve
            
        Returns:
            Sikeres volt-e a fókuszálás
        """
        if not self.counties_gdf is not None:
            return False
        
        try:
            # Megye geometria keresése
            county_row = self.counties_gdf[self.counties_gdf['megye'] == county_name]
            if county_row.empty:
                return False
            
            geometry = county_row.geometry.iloc[0]
            bounds = geometry.bounds
            
            # Térkép frissítése
            if self.map_visualizer:
                self.map_visualizer.update_map_bounds(bounds)
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
        ✅ Térképes tab kész használatra.
        
        Returns:
            Kész-e a használatra
        """
        return (
            self.is_data_loaded and 
            self.location_selector is not None and 
            self.map_visualizer is not None and
            self.counties_gdf is not None
        )
    
    def refresh_all_components(self):
        """
        🔄 Összes komponens frissítése.
        """
        print("🔄 DEBUG: Refreshing all HungarianMapTab components")
        
        # Location selector frissítése
        if self.location_selector:
            # GeoJSON adatok újratöltése
            self.location_selector._start_data_loading()
        
        # Map visualizer frissítése
        if self.map_visualizer:
            self.map_visualizer._refresh_map()
        
        # Status frissítése
        self.loading_status.setText("🔄 Komponensek frissítése...")
    
    def clear_selection(self):
        """
        🧹 Kiválasztás törlése minden komponensben.
        """
        print("🧹 DEBUG: Clearing all selections in HungarianMapTab")
        
        # Location selector törlése
        if self.location_selector:
            self.location_selector.reset_selection()
        
        # Map reset
        if self.map_visualizer:
            self.map_visualizer.reset_map_view()
        
        # Current data törlése
        self.current_location_data = None
        
        # Status frissítése
        self.loading_status.setText("🧹 Kiválasztás törölve - válassz új régiót és megyét")


# === DEMO ÉS TESZT FUNKCIÓK ===

def demo_hungarian_map_tab():
    """
    🧪 Hungarian Map Tab demo alkalmazás.
    """
    import sys
    from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
    
    app = QApplication(sys.argv)
    
    # Fő ablak
    window = QMainWindow()
    window.setWindowTitle("🗺️ Hungarian Map Tab Demo - Teljes Interaktív Térkép")
    window.setGeometry(100, 100, 1400, 900)
    
    # Central widget
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    
    layout = QVBoxLayout(central_widget)
    
    # Hungarian Map Tab
    map_tab = HungarianMapTab()
    layout.addWidget(map_tab)
    
    # Event handlers
    def on_location_selected(location):
        print(f"📍 DEMO: Location selected: {location.display_name if location else 'None'}")
    
    def on_map_interaction(interaction_type, data):
        print(f"🗺️ DEMO: Map interaction: {interaction_type} - {data}")
    
    def on_export_completed(file_path):
        print(f"💾 DEMO: Export completed: {file_path}")
    
    def on_error_occurred(message):
        print(f"❌ DEMO: Error occurred: {message}")
    
    def on_data_loading_completed():
        print("✅ DEMO: Data loading completed - ready to use!")
    
    # Signalok kapcsolása
    map_tab.location_selected.connect(on_location_selected)
    map_tab.map_interaction.connect(on_map_interaction)
    map_tab.export_completed.connect(on_export_completed)
    map_tab.error_occurred.connect(on_error_occurred)
    map_tab.data_loading_completed.connect(on_data_loading_completed)
    
    window.show()
    
    print("🗺️ DEMO: Hungarian Map Tab elindítva!")
    print("✅ FUNKCIONALITÁSOK:")
    print("   📍 Bal oldal: Éghajlati régió → Megye választás")
    print("   🗺️ Jobb oldal: Interaktív Folium térkép")
    print("   🔗 Kétirányú integráció: választás ↔ térkép")
    print("   💾 HTML térkép exportálás")
    print("   🎯 Automatikus térkép központosítás")
    print("   🔄 Alaphelyzet visszaállítás")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    demo_hungarian_map_tab()