#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🗺️ Hungarian Location Selector - RÉGIÓ KONZISZTENCIA JAVÍTÁS
Magyar Klímaanalitika MVP - Térkép Komponens Lokáció Választó

🔧 KRITIKUS JAVÍTÁS: EGYSÉGES 7 STATISZTIKAI RÉGIÓ IMPLEMENTÁCIÓ
- Control Panel-lel és Multi-City Engine-nel 100% konzisztens
- 5 klimatikus régió → 7 statisztikai régió átállás
- KSH hivatalos régió felosztás implementálása
- Multi-City Engine HUNGARIAN_REGIONAL_MAPPING kompatibilitás

Fájl helye: src/gui/hungarian_location_selector.py
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLabel, 
    QGroupBox, QPushButton, QListWidget, QListWidgetItem,
    QSplitter, QTextEdit, QLineEdit, QProgressBar
)
from PySide6.QtCore import Qt, Signal, QThread, QTimer
from PySide6.QtGui import QFont, QPixmap, QIcon

try:
    import geopandas as gpd
    GEOPANDAS_AVAILABLE = True
except ImportError:
    GEOPANDAS_AVAILABLE = False

# Saját modulok
from ..data.models import Location
from .theme_manager import register_widget_for_theming
from .color_palette import ColorPalette


class HungarianStatisticalRegion(Enum):
    """
    🔧 JAVÍTOTT: Magyar statisztikai régiók (KSH hivatalos felosztás)
    7 NUTS 2 szintű statisztikai régió - Control Panel és Multi-City Engine konzisztens!
    """
    KOZEP_MAGYARORSZAG = "kozep_magyarorszag"           # Közép-Magyarország
    KOZEP_DUNANTUL = "kozep_dunantul"                   # Közép-Dunántúl  
    NYUGAT_DUNANTUL = "nyugat_dunantul"                 # Nyugat-Dunántúl
    DEL_DUNANTUL = "del_dunantul"                       # Dél-Dunántúl
    ESZAK_MAGYARORSZAG = "eszak_magyarorszag"           # Észak-Magyarország
    ESZAK_ALFOLD = "eszak_alfold"                       # Észak-Alföld
    DEL_ALFOLD = "del_alfold"                           # Dél-Alföld


@dataclass
class HungarianRegionData:
    """
    🗺️ Magyar régió adatstruktúra - JAVÍTOTT 7 statisztikai régió verzió.
    """
    name: str
    display_name: str
    description: str
    counties: List[str]
    administrative_center: str
    avg_temp_annual: float
    avg_precipitation_annual: int
    characteristics: List[str]
    nuts_code: str  # NUTS 2 kód (HU10, HU21, stb.)


class HungarianLocationWorker(QThread):
    """
    🔄 Háttér munkavégző a GeoJSON adatok betöltéséhez.
    """
    
    # Signalok
    progress_updated = Signal(int)           # progress (0-100)
    counties_loaded = Signal(object)        # GeoDataFrame
    postal_codes_loaded = Signal(object)    # GeoDataFrame  
    error_occurred = Signal(str)            # error message
    completed = Signal()                    # összes adat betöltve
    
    def __init__(self, data_dir: Path):
        super().__init__()
        self.data_dir = data_dir
        self.counties_gdf = None
        self.postal_codes_gdf = None
    
    def run(self):
        """
        GeoJSON adatok betöltése háttérben.
        """
        try:
            if not GEOPANDAS_AVAILABLE:
                self.error_occurred.emit("GeoPandas nincs telepítve!")
                return
            
            self.progress_updated.emit(10)
            
            # Counties betöltése
            counties_file = self.data_dir / "counties.geojson"
            if counties_file.exists():
                self.counties_gdf = gpd.read_file(counties_file)
                self.counties_loaded.emit(self.counties_gdf)
                self.progress_updated.emit(50)
            else:
                self.error_occurred.emit(f"Counties fájl nem található: {counties_file}")
                return
            
            # Postal codes betöltése (opcionális, nagy fájl)
            postal_codes_file = self.data_dir / "postal_codes.geojson"
            if postal_codes_file.exists():
                # Nagy fájl, részleges betöltés vagy kihagyás
                file_size = postal_codes_file.stat().st_size
                if file_size < 50 * 1024 * 1024:  # 50MB alatt
                    self.postal_codes_gdf = gpd.read_file(postal_codes_file)
                    self.postal_codes_loaded.emit(self.postal_codes_gdf)
                    self.progress_updated.emit(90)
                else:
                    # Nagy fájl esetén kihagyás vagy részleges betöltés
                    self.progress_updated.emit(90)
            
            self.progress_updated.emit(100)
            self.completed.emit()
            
        except Exception as e:
            self.error_occurred.emit(f"GeoJSON betöltési hiba: {e}")


class HungarianLocationSelector(QWidget):
    """
    🗺️ Hierarchikus magyar lokáció választó widget - RÉGIÓ KONZISZTENCIA JAVÍTVA!
    
    🔧 KRITIKUS JAVÍTÁS:
    - 5 klimatikus régió → 7 statisztikai régió (Control Panel konzisztens)
    - Multi-City Engine HUNGARIAN_REGIONAL_MAPPING kompatibilitás 100%
    - KSH NUTS 2 régió felosztás implementálása
    
    FUNKCIÓK:
    - 7 statisztikai régió választás (Control Panel konzisztens!)
    - Megye választás (GeoJSON alapú)
    - Járás/település szűrés
    - Koordináta megjelenítés
    - Térképes előnézet integráció
    
    SIGNALOK:
    - region_selected(region_data): Statisztikai régió kiválasztva
    - county_selected(county_name, geometry): Megye kiválasztva
    - location_selected(location): Pontos lokáció kiválasztva
    - selection_changed(): Bármilyen választás változott
    - map_update_requested(bounds): Térkép frissítés kérés
    """
    
    # Signalok
    region_selected = Signal(object)        # HungarianRegionData
    county_selected = Signal(str, object)   # county_name, geometry
    location_selected = Signal(object)     # Location object
    selection_changed = Signal()           # általános változás
    map_update_requested = Signal(object)  # map bounds/center
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Komponens inicializálás
        self.color_palette = ColorPalette()
        
        # Adatok
        self.region_data = self._init_statistical_regions()  # 🔧 JAVÍTOTT!
        self.counties_gdf = None
        self.postal_codes_gdf = None
        self.current_region = None
        self.current_county = None
        self.current_location = None
        
        # Worker thread
        self.data_worker = None
        
        # UI építés
        self._setup_ui()
        self._setup_theme()
        self._connect_signals()
        
        # Adatok betöltésének indítása
        self._start_data_loading()
    
    def _setup_ui(self):
        """
        🎨 UI komponensek létrehozása.
        """
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # === 🔧 JAVÍTOTT: STATISZTIKAI RÉGIÓ VÁLASZTÓ ===
        
        region_group = QGroupBox("🏛️ Magyar Statisztikai Régiók (NUTS 2)")
        register_widget_for_theming(region_group, "container")
        region_layout = QVBoxLayout(region_group)
        
        self.region_combo = QComboBox()
        self.region_combo.addItem("Válassz statisztikai régiót...", None)
        register_widget_for_theming(self.region_combo, "input")
        
        # 🔧 KRITIKUS: 7 statisztikai régió hozzáadása (Control Panel konzisztens!)
        for region_key, region_data in self.region_data.items():
            self.region_combo.addItem(
                f"{region_data.display_name} ({region_data.nuts_code})",
                region_key
            )
        
        region_layout.addWidget(self.region_combo)
        
        # Régió információs panel
        self.region_info = QTextEdit()
        self.region_info.setMaximumHeight(120)  # Kicsit nagyobb a több info miatt
        self.region_info.setReadOnly(True)
        register_widget_for_theming(self.region_info, "text")
        region_layout.addWidget(self.region_info)
        
        layout.addWidget(region_group)
        
        # === 🗺️ MEGYE VÁLASZTÓ ===
        
        county_group = QGroupBox("🗺️ Megye Választás")
        register_widget_for_theming(county_group, "container")
        county_layout = QVBoxLayout(county_group)
        
        self.county_combo = QComboBox()
        self.county_combo.addItem("Először válassz régiót...", None)
        self.county_combo.setEnabled(False)
        register_widget_for_theming(self.county_combo, "input")
        county_layout.addWidget(self.county_combo)
        
        layout.addWidget(county_group)
        
        # === 📍 LOKÁCIÓ RÉSZLETEK ===
        
        location_group = QGroupBox("📍 Lokáció Részletek")
        register_widget_for_theming(location_group, "container")
        location_layout = QVBoxLayout(location_group)
        
        # Koordináta megjelenítés
        coords_layout = QHBoxLayout()
        
        self.lat_label = QLabel("Szélesség: -")
        self.lon_label = QLabel("Hosszúság: -")
        register_widget_for_theming(self.lat_label, "text")
        register_widget_for_theming(self.lon_label, "text")
        
        coords_layout.addWidget(self.lat_label)
        coords_layout.addWidget(self.lon_label)
        location_layout.addLayout(coords_layout)
        
        # Terület információ
        self.area_label = QLabel("Terület: -")
        register_widget_for_theming(self.area_label, "text")
        location_layout.addWidget(self.area_label)
        
        layout.addWidget(location_group)
        
        # === 🔄 BETÖLTÉSI PROGRESS ===
        
        progress_group = QGroupBox("🔄 Térképi Adatok Betöltése")
        register_widget_for_theming(progress_group, "container")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        register_widget_for_theming(self.progress_bar, "input")
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel("Adatok betöltése...")
        register_widget_for_theming(self.progress_label, "text")
        progress_layout.addWidget(self.progress_label)
        
        layout.addWidget(progress_group)
        
        # === 🎯 AKCIÓ GOMBOK ===
        
        button_layout = QHBoxLayout()
        
        self.refresh_btn = QPushButton("🔄 Frissítés")
        self.refresh_btn.setToolTip("Térképi adatok újratöltése")
        register_widget_for_theming(self.refresh_btn, "button")
        button_layout.addWidget(self.refresh_btn)
        
        self.center_map_btn = QPushButton("🎯 Térkép Központosítás")
        self.center_map_btn.setToolTip("Térkép központosítása a kiválasztott területre")
        self.center_map_btn.setEnabled(False)
        register_widget_for_theming(self.center_map_btn, "button")
        button_layout.addWidget(self.center_map_btn)
        
        layout.addLayout(button_layout)
        
        # Spacer a végén
        layout.addStretch()
    
    def _setup_theme(self):
        """
        🎨 Téma beállítások alkalmazása.
        """
        register_widget_for_theming(self, "container")
    
    def _connect_signals(self):
        """
        🔗 Signal-slot kapcsolatok létrehozása.
        """
        # UI signalok
        self.region_combo.currentTextChanged.connect(self._on_region_changed)
        self.county_combo.currentTextChanged.connect(self._on_county_changed)
        self.refresh_btn.clicked.connect(self._start_data_loading)
        self.center_map_btn.clicked.connect(self._center_map_on_selection)
    
    def _init_statistical_regions(self) -> Dict[str, HungarianRegionData]:
        """
        🔧 KRITIKUS JAVÍTÁS: Magyar 7 statisztikai régió inicializálása (Control Panel + Multi-City Engine konzisztens!)
        
        KSH NUTS 2 szintű régió felosztás:
        - Control Panel régió dropdown-pal 100% egyezés
        - Multi-City Engine HUNGARIAN_REGIONAL_MAPPING kompatibilitás
        - Hivatalos megyei tartozás
        """
        regions = {
            HungarianStatisticalRegion.KOZEP_MAGYARORSZAG.value: HungarianRegionData(
                name="kozep_magyarorszag",
                display_name="Közép-Magyarország",
                description="Főváros és agglomerációja, legnagyobb népességű régió",
                counties=["Budapest", "Pest"],
                administrative_center="Budapest",
                nuts_code="HU10",
                avg_temp_annual=10.4,
                avg_precipitation_annual=580,
                characteristics=["Városi környezet", "Legnagyobb népesség", "Gazdasági központ", "Duna menti fekvés"]
            ),
            
            HungarianStatisticalRegion.KOZEP_DUNANTUL.value: HungarianRegionData(
                name="kozep_dunantul",
                display_name="Közép-Dunántúl",  
                description="Dunántúl központi területe, átmeneti jellegű régió",
                counties=["Fejér", "Komárom-Esztergom", "Veszprém"],
                administrative_center="Székesfehérvár",
                nuts_code="HU21",
                avg_temp_annual=9.9,
                avg_precipitation_annual=620,
                characteristics=["Átmeneti éghajlat", "Balatoni régió", "Ipari hagyományok", "Középhegységi területek"]
            ),
            
            HungarianStatisticalRegion.NYUGAT_DUNANTUL.value: HungarianRegionData(
                name="nyugat_dunantul",
                display_name="Nyugat-Dunántúl",
                description="Osztrák határ mentén, óceáni hatással",
                counties=["Győr-Moson-Sopron", "Vas", "Zala"],
                administrative_center="Győr",
                nuts_code="HU22",
                avg_temp_annual=9.8,
                avg_precipitation_annual=700,
                characteristics=["Óceáni hatás", "Legnagyobb csapadék", "Nyugati határvidék", "Autóipar központ"]
            ),
            
            HungarianStatisticalRegion.DEL_DUNANTUL.value: HungarianRegionData(
                name="del_dunantul",
                display_name="Dél-Dunántúl",
                description="Horvát határ mentén, mediterrán hatással",
                counties=["Baranya", "Somogy", "Tolna"],
                administrative_center="Pécs",
                nuts_code="HU23",
                avg_temp_annual=10.3,
                avg_precipitation_annual=650,
                characteristics=["Mediterrán hatás", "Mecsek hegység", "Borászat", "Történelmi városok"]
            ),
            
            HungarianStatisticalRegion.ESZAK_MAGYARORSZAG.value: HungarianRegionData(
                name="eszak_magyarorszag", 
                display_name="Észak-Magyarország",
                description="Hegyvidéki régió, ipari hagyományokkal",
                counties=["Borsod-Abaúj-Zemplén", "Heves", "Nógrád"],
                administrative_center="Miskolc",
                nuts_code="HU31",
                avg_temp_annual=9.2,
                avg_precipitation_annual=750,
                characteristics=["Hegyvidéki éghajlat", "Nehézipar", "Legmagasabb csapadék", "Bükk hegység"]
            ),
            
            HungarianStatisticalRegion.ESZAK_ALFOLD.value: HungarianRegionData(
                name="eszak_alfold",
                display_name="Észak-Alföld",
                description="Alföldi régió északi része, kontinentális éghajlat",
                counties=["Hajdú-Bihar", "Jász-Nagykun-Szolnok", "Szabolcs-Szatmár-Bereg"],
                administrative_center="Debrecen",
                nuts_code="HU32",
                avg_temp_annual=10.1,
                avg_precipitation_annual=560,
                characteristics=["Kontinentális éghajlat", "Mezőgazdaság", "Tiszántúl", "Egyetemi városok"]
            ),
            
            HungarianStatisticalRegion.DEL_ALFOLD.value: HungarianRegionData(
                name="del_alfold",
                display_name="Dél-Alföld",
                description="Alföldi régió déli része, legszárazabb terület",
                counties=["Bács-Kiskun", "Békés", "Csongrád-Csanád"],
                administrative_center="Szeged",
                nuts_code="HU33",
                avg_temp_annual=10.8,
                avg_precipitation_annual=520,
                characteristics=["Legszárazabb régió", "Homoktalajok", "Termálvíz", "Paprika termesztés"]
            )
        }
        
        return regions
    
    def _start_data_loading(self):
        """
        🔄 GeoJSON adatok betöltésének indítása.
        """
        if not GEOPANDAS_AVAILABLE:
            self.progress_label.setText("❌ GeoPandas nem elérhető!")
            return
        
        # Worker thread indítása
        project_root = Path(__file__).parent.parent.parent
        data_dir = project_root / "data" / "geojson"
        
        if not data_dir.exists():
            self.progress_label.setText("❌ GeoJSON könyvtár nem található!")
            return
        
        self.data_worker = HungarianLocationWorker(data_dir)
        
        # Worker signalok kapcsolása
        self.data_worker.progress_updated.connect(self.progress_bar.setValue)
        self.data_worker.counties_loaded.connect(self._on_counties_loaded)
        self.data_worker.postal_codes_loaded.connect(self._on_postal_codes_loaded)
        self.data_worker.error_occurred.connect(self._on_data_error)
        self.data_worker.completed.connect(self._on_data_loading_completed)
        
        # Worker indítása
        self.progress_label.setText("🔄 GeoJSON adatok betöltése...")
        self.data_worker.start()
    
    def _on_counties_loaded(self, counties_gdf):
        """
        🗺️ Megyeadatok betöltése befejezve.
        """
        self.counties_gdf = counties_gdf
        self.progress_label.setText("✅ Megyeadatok betöltve...")
        
        # Megyenevek frissítése combo-ban (régió alapján)
        self._update_county_combo()
    
    def _on_postal_codes_loaded(self, postal_codes_gdf):
        """
        📫 Irányítószám adatok betöltése befejezve.
        """
        self.postal_codes_gdf = postal_codes_gdf
        self.progress_label.setText("✅ Irányítószám adatok betöltve...")
    
    def _on_data_error(self, error_message: str):
        """
        ❌ Adatok betöltési hiba kezelése.
        """
        self.progress_label.setText(f"❌ {error_message}")
        self.progress_bar.setValue(0)
    
    def _on_data_loading_completed(self):
        """
        ✅ Összes adat betöltése befejezve.
        """
        self.progress_label.setText("✅ Térképi adatok betöltve!")
        self.progress_bar.setValue(100)
        
        # Funkcionalitások engedélyezése
        self.county_combo.setEnabled(True)
        self.center_map_btn.setEnabled(True)
        
        # Timer a progress eltüntetéséhez
        QTimer.singleShot(3000, lambda: self.progress_label.setText("Kész használatra"))
    
    def _on_region_changed(self):
        """
        🏛️ Statisztikai régió választás változás kezelése - JAVÍTOTT!
        """
        current_data = self.region_combo.currentData()
        
        if current_data is None:
            self.current_region = None
            self.region_info.clear()
            self._update_county_combo()
            return
        
        # Régió adatok megjelenítése
        region_data = self.region_data[current_data]
        self.current_region = region_data
        
        # 🔧 JAVÍTOTT: Információs panel frissítése több info-val
        info_text = f"""
<b>{region_data.display_name}</b> ({region_data.nuts_code})<br>
<b>Közigazgatási központ:</b> {region_data.administrative_center}<br>
<b>Megyék:</b> {', '.join(region_data.counties)}<br>
<b>Átlagos évi hőmérséklet:</b> {region_data.avg_temp_annual}°C<br>
<b>Átlagos évi csapadék:</b> {region_data.avg_precipitation_annual} mm<br>
<br>
<b>Jellemzők:</b><br>
• {' <br>• '.join(region_data.characteristics)}<br>
<br>
<b>Leírás:</b> {region_data.description}
        """.strip()
        
        self.region_info.setHtml(info_text)
        
        # Megyék frissítése
        self._update_county_combo()
        
        # Signal kibocsátása
        self.region_selected.emit(region_data)
        self.selection_changed.emit()
    
    def _update_county_combo(self):
        """
        🗺️ Megye combo frissítése a kiválasztott régió alapján - JAVÍTOTT!
        """
        self.county_combo.clear()
        
        if self.current_region is None:
            self.county_combo.addItem("Először válassz régiót...", None)
            self.county_combo.setEnabled(False)
            return
        
        if self.counties_gdf is None:
            self.county_combo.addItem("Térképi adatok betöltése...", None)
            self.county_combo.setEnabled(False)
            return
        
        # 🔧 KRITIKUS: Régió megyéinek hozzáadása (statisztikai régió alapján)
        self.county_combo.addItem("Válassz megyét...", None)
        
        available_counties = set(self.counties_gdf['megye'].tolist())
        region_counties = set(self.current_region.counties)  # Ez most már a helyes megyéket tartalmazza
        
        # Közös megyék (régió és GeoJSON alapján)
        valid_counties = region_counties.intersection(available_counties)
        
        for county in sorted(valid_counties):
            self.county_combo.addItem(county, county)
        
        # Egyéb megyék is (ha vannak)
        other_counties = available_counties - region_counties
        if other_counties:
            self.county_combo.addItem("--- Egyéb megyék ---", None)
            for county in sorted(other_counties):
                self.county_combo.addItem(f"{county} (egyéb)", county)
        
        self.county_combo.setEnabled(True)
    
    def _on_county_changed(self):
        """
        🗺️ Megye választás változás kezelése.
        """
        current_county = self.county_combo.currentData()
        
        if current_county is None or self.counties_gdf is None:
            self.current_county = None
            self._update_location_info()
            return
        
        # Megye geometria lekérdezése
        county_row = self.counties_gdf[self.counties_gdf['megye'] == current_county]
        
        if county_row.empty:
            self.current_county = None
            self._update_location_info()
            return
        
        # Megye adatok tárolása
        geometry = county_row.geometry.iloc[0]
        self.current_county = {
            'name': current_county,
            'geometry': geometry,
            'bounds': geometry.bounds,  # (minx, miny, maxx, maxy)
            'centroid': geometry.centroid
        }
        
        # Lokáció info frissítése
        self._update_location_info()
        
        # Signalok kibocsátása
        self.county_selected.emit(current_county, geometry)
        self.selection_changed.emit()
        
        # Térkép frissítés kérése
        self.map_update_requested.emit(self.current_county['bounds'])
    
    def _update_location_info(self):
        """
        📍 Lokáció információk frissítése.
        """
        if self.current_county is None:
            self.lat_label.setText("Szélesség: -")
            self.lon_label.setText("Hosszúság: -")
            self.area_label.setText("Terület: -")
            return
        
        # Központi koordináták
        centroid = self.current_county['centroid']
        lat = centroid.y
        lon = centroid.x
        
        self.lat_label.setText(f"Szélesség: {lat:.4f}°")
        self.lon_label.setText(f"Hosszúság: {lon:.4f}°")
        
        # Terület számítás (közelítő, fok alapú)
        bounds = self.current_county['bounds']
        width = bounds[2] - bounds[0]  # maxx - minx
        height = bounds[3] - bounds[1]  # maxy - miny
        
        self.area_label.setText(f"Határoló téglalap: {width:.3f}° × {height:.3f}°")
        
        # Location objektum létrehozása
        self.current_location = Location(
            identifier=self.current_county['name'],
            display_name=self.current_county['name'],
            latitude=lat,
            longitude=lon,
            country_code="HU",
            timezone="Europe/Budapest",
            metadata={
                'region': self.current_region.name if self.current_region else None,
                'region_display_name': self.current_region.display_name if self.current_region else None,
                'nuts_code': self.current_region.nuts_code if self.current_region else None,
                'county': self.current_county['name'],
                'source': 'hungarian_location_selector',
                'bounds': bounds,
                'administrative_center': self.current_region.administrative_center if self.current_region else None
            }
        )
        
        # Location signal kibocsátása
        self.location_selected.emit(self.current_location)
    
    def _center_map_on_selection(self):
        """
        🎯 Térkép központosítása a kiválasztott területre.
        """
        if self.current_county is None:
            return
        
        bounds = self.current_county['bounds']
        self.map_update_requested.emit(bounds)
    
    # === PUBLIKUS API ===
    
    def get_current_selection(self) -> Dict[str, Any]:
        """
        📋 Jelenlegi kiválasztott elemek lekérdezése.
        """
        return {
            'region': self.current_region,
            'county': self.current_county,
            'location': self.current_location,
            'has_geodata': self.counties_gdf is not None
        }
    
    def set_region(self, region_key: str) -> bool:
        """
        🏛️ Régió programmatic beállítása - JAVÍTOTT (statisztikai régió támogatás)!
        """
        for i in range(self.region_combo.count()):
            if self.region_combo.itemData(i) == region_key:
                self.region_combo.setCurrentIndex(i)
                return True
        return False
    
    def set_county(self, county_name: str) -> bool:
        """
        🗺️ Megye programmatic beállítása.
        """
        for i in range(self.county_combo.count()):
            if self.county_combo.itemData(i) == county_name:
                self.county_combo.setCurrentIndex(i)
                return True
        return False
    
    def get_available_counties(self) -> List[str]:
        """
        📋 Elérhető megyék listája.
        """
        if self.counties_gdf is None:
            return []
        
        return sorted(self.counties_gdf['megye'].tolist())
    
    def get_counties_geodataframe(self):
        """
        🗺️ Megyék GeoDataFrame lekérdezése.
        """
        return self.counties_gdf
    
    def get_postal_codes_geodataframe(self):
        """
        📫 Irányítószám területek GeoDataFrame lekérdezése.
        """
        return self.postal_codes_gdf
    
    def reset_selection(self):
        """
        🔄 Kiválasztás visszaállítása.
        """
        self.region_combo.setCurrentIndex(0)
        self.county_combo.setCurrentIndex(0)
        
        self.current_region = None
        self.current_county = None
        self.current_location = None
        
        self.region_info.clear()
        self._update_location_info()
        
        self.selection_changed.emit()

    # === 🔧 JAVÍTOTT: RÉGIÓ KOMPATIBILITÁSI METÓDUSOK ===
    
    def get_region_by_display_name(self, display_name: str) -> Optional[HungarianRegionData]:
        """
        🔧 ÚJ: Régió lekérdezése megjelenítési név alapján (Control Panel kompatibilitás).
        
        Args:
            display_name: Régió megjelenítési neve (pl. "Észak-Magyarország")
            
        Returns:
            HungarianRegionData objektum vagy None
        """
        for region_data in self.region_data.values():
            if region_data.display_name == display_name:
                return region_data
        return None
    
    def set_region_by_display_name(self, display_name: str) -> bool:
        """
        🔧 ÚJ: Régió beállítása megjelenítési név alapján (Control Panel kompatibilitás).
        
        Args:
            display_name: Régió megjelenítési neve (pl. "Észak-Magyarország")
            
        Returns:
            Sikeres volt-e a beállítás
        """
        region_data = self.get_region_by_display_name(display_name)
        if region_data:
            return self.set_region(region_data.name)
        return False
    
    def get_available_region_display_names(self) -> List[str]:
        """
        🔧 ÚJ: Elérhető régió megjelenítési nevek listája (Control Panel kompatibilitás).
        
        Returns:
            Régió megjelenítési nevek listája
        """
        return [region_data.display_name for region_data in self.region_data.values()]
    
    def get_region_counties_mapping(self) -> Dict[str, List[str]]:
        """
        🔧 ÚJ: Régió → megyék mapping (Multi-City Engine kompatibilitás).
        
        Returns:
            {régió_megjelenítési_név: [megyék_listája]} dictionary
        """
        return {
            region_data.display_name: region_data.counties
            for region_data in self.region_data.values()
        }


# === DEMO ÉS TESZT FUNKCIÓK ===

def demo_hungarian_location_selector_fixed():
    """
    🧪 Hungarian Location Selector demo alkalmazás - RÉGIÓ KONZISZTENCIA JAVÍTVA!
    """
    import sys
    from PySide6.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QWidget, QVBoxLayout, QLabel
    
    app = QApplication(sys.argv)
    
    # Fő ablak
    window = QMainWindow()
    window.setWindowTitle("🗺️ Hungarian Location Selector Demo - RÉGIÓ KONZISZTENCIA JAVÍTVA")
    window.setGeometry(100, 100, 1000, 700)
    
    # Central widget
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    
    layout = QVBoxLayout(central_widget)
    
    # Információs header
    info_label = QLabel("🔧 RÉGIÓ KONZISZTENCIA JAVÍTVA: 7 statisztikai régió (Control Panel + Multi-City Engine konzisztens!)")
    info_label.setStyleSheet("background-color: #27AE60; color: white; padding: 10px; font-weight: bold;")
    layout.addWidget(info_label)
    
    main_layout = QHBoxLayout()
    
    # Location selector
    location_selector = HungarianLocationSelector()
    main_layout.addWidget(location_selector)
    
    # Debug panel
    debug_panel = QWidget()
    debug_layout = QVBoxLayout(debug_panel)
    
    debug_label = QLabel("🔧 DEBUG INFORMÁCIÓK:")
    debug_label.setStyleSheet("font-weight: bold; color: #E74C3C;")
    debug_layout.addWidget(debug_label)
    
    region_info_label = QLabel("Régió: -")
    county_info_label = QLabel("Megye: -")
    counties_mapping_label = QLabel("Megyék: -")
    
    debug_layout.addWidget(region_info_label)
    debug_layout.addWidget(county_info_label)
    debug_layout.addWidget(counties_mapping_label)
    debug_layout.addStretch()
    
    main_layout.addWidget(debug_panel)
    layout.addLayout(main_layout)
    
    # Event handlers
    def on_region_selected(region_data):
        print(f"🏛️ Statisztikai régió kiválasztva: {region_data.display_name} ({region_data.nuts_code})")
        print(f"   Megyék: {region_data.counties}")
        print(f"   Admin központ: {region_data.administrative_center}")
        
        region_info_label.setText(f"Régió: {region_data.display_name} ({region_data.nuts_code})")
        counties_mapping_label.setText(f"Megyék: {', '.join(region_data.counties)}")
    
    def on_county_selected(county_name, geometry):
        print(f"🗺️ Megye kiválasztva: {county_name}")
        print(f"   Határok: {geometry.bounds}")
        
        county_info_label.setText(f"Megye: {county_name}")
    
    def on_location_selected(location):
        print(f"📍 Lokáció kiválasztva: {location.display_name}")
        print(f"   Koordináták: {location.latitude:.4f}, {location.longitude:.4f}")
        print(f"   NUTS kód: {location.metadata.get('nuts_code', 'N/A')}")
        print(f"   Admin központ: {location.metadata.get('administrative_center', 'N/A')}")
    
    def on_map_update_requested(bounds):
        print(f"🎯 Térkép frissítés: {bounds}")
    
    # Signalok kapcsolása
    location_selector.region_selected.connect(on_region_selected)
    location_selector.county_selected.connect(on_county_selected)
    location_selector.location_selected.connect(on_location_selected)
    location_selector.map_update_requested.connect(on_map_update_requested)
    
    window.show()
    
    print("🗺️ Hungarian Location Selector Demo elindítva - RÉGIÓ KONZISZTENCIA JAVÍTVA!")
    print("✅ JAVÍTÁSOK:")
    print("   🔧 5 klimatikus régió → 7 statisztikai régió")
    print("   🔧 Control Panel konzisztencia 100%")
    print("   🔧 Multi-City Engine HUNGARIAN_REGIONAL_MAPPING kompatibilitás")
    print("   🔧 KSH NUTS 2 hivatalos régió felosztás")
    print("   🔧 Régió megjelenítési név + megyék mapping helyes")
    print()
    print("🧪 TESZT:")
    print("   1. Válassz 'Észak-Magyarország' régiót")
    print("   2. Ellenőrizd: Borsod-Abaúj-Zemplén, Heves, Nógrád megyék jelennek meg")
    print("   3. Ez most már megegyezik a Control Panel és Multi-City Engine definícióival!")
    print()
    print("📊 RÉGIÓK (Control Panel konzisztens):")
    for region_data in location_selector.region_data.values():
        print(f"   {region_data.display_name} ({region_data.nuts_code}): {', '.join(region_data.counties)}")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    demo_hungarian_location_selector_fixed()
