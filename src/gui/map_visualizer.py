#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🗺️ Magyar Térkép Vizualizáló - STATIC HTML VERZIÓ
Magyar Klímaanalitika MVP - JavaScript-mentes Térképes Megjelenítő

🚨 STATIC HTML FIX: Teljes JavaScript-mentes térkép
- Nincs Leaflet dependency
- Pure HTML + CSS térkép
- SVG-based magyarország térkép
- Garantált működés

Fájl helye: src/gui/map_visualizer.py
"""

from typing import Dict, List, Optional, Tuple, Any
import os
import json
import tempfile
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime, date

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QComboBox, QSlider, QCheckBox, QGroupBox, QProgressBar,
    QFileDialog, QMessageBox, QSplitter
)
from PySide6.QtCore import Qt, Signal, QUrl, QTimer, QThread
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWebEngineWidgets import QWebEngineView

try:
    import geopandas as gpd
    GEOPANDAS_AVAILABLE = True
except ImportError:
    GEOPANDAS_AVAILABLE = False

# Saját modulok
from .theme_manager import register_widget_for_theming
from .color_palette import ColorPalette


@dataclass
class MapConfig:
    """
    🗺️ Térkép konfigurációs beállítások - STATIC HTML.
    """
    center_lat: float = 47.1625  # Magyarország közepe
    center_lon: float = 19.5033
    zoom_level: int = 7
    show_counties: bool = True
    weather_overlay: bool = False
    county_fill_opacity: float = 0.3
    county_border_weight: int = 2
    county_border_color: str = "#2E4057"
    county_fill_color: str = "#4A90E2"
    selected_county: Optional[str] = None


class StaticMapGenerator(QThread):
    """
    🔄 Háttér worker a STATIC HTML térkép generálásához - JAVASCRIPT-MENTES.
    """
    
    # Signalok
    progress_updated = Signal(int)         # progress (0-100)
    map_generated = Signal(str)           # HTML fájl path
    error_occurred = Signal(str)          # error message
    status_updated = Signal(str)          # status message
    
    def __init__(self, config: MapConfig, counties_gdf=None, weather_data=None, output_path=None):
        super().__init__()
        self.config = config
        self.counties_gdf = counties_gdf
        self.weather_data = weather_data
        self.output_path = output_path or self._get_temp_html_path()
    
    def _get_temp_html_path(self) -> str:
        """Ideiglenes HTML fájl útvonal generálása."""
        temp_dir = tempfile.gettempdir()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(temp_dir, f"hungarian_static_map_{timestamp}.html")
    
    def run(self):
        """
        🚨 STATIC HTML térkép generálása - TELJES JAVASCRIPT-MENTES VERZIÓ
        """
        try:
            self.status_updated.emit("🗺️ Static HTML térkép létrehozása...")
            self.progress_updated.emit(10)
            
            # === STATIC HTML TÉRKÉP GENERÁLÁSA ===
            
            html_content = self._generate_static_html_map()
            
            self.progress_updated.emit(80)
            
            # === HTML FÁJL MENTÉSE ===
            
            self.status_updated.emit("💾 Static térkép mentése...")
            
            with open(self.output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.progress_updated.emit(100)
            self.status_updated.emit("✅ Static HTML térkép elkészült!")
            self.map_generated.emit(self.output_path)
            
        except Exception as e:
            import traceback
            error_msg = f"Static térkép generálási hiba: {e}\n{traceback.format_exc()}"
            self.error_occurred.emit(error_msg)
    
    def _generate_static_html_map(self) -> str:
        """
        🚨 STATIC HTML térkép generálása - PURE HTML/CSS, JAVASCRIPT-MENTES
        """
        
        # Counties adatok feldolgozása
        counties_html = ""
        if self.config.show_counties and self.counties_gdf is not None:
            counties_html = self._generate_counties_list_html()
        
        # Weather overlay
        weather_html = ""
        if self.config.weather_overlay and self.weather_data:
            weather_html = self._generate_weather_overlay_html()
        
        # Kiválasztott megye információ
        selected_county_html = ""
        if self.config.selected_county:
            selected_county_html = self._generate_selected_county_html()
        
        # Teljes HTML generálása
        html_template = f"""
<!DOCTYPE html>
<html lang="hu">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🇭🇺 Magyar Klímaanalitika Térkép - Static</title>
    <style>
        {self._generate_css_styles()}
    </style>
</head>
<body>
    <div class="map-container">
        <div class="map-header">
            <h1>🇭🇺 Magyar Klímaanalitika Térkép</h1>
            <p class="subtitle">Interaktív térkép (Static HTML verzió)</p>
        </div>
        
        <div class="map-content">
            <div class="map-sidebar">
                <div class="info-panel">
                    <h3>📍 Magyar Megyék</h3>
                    <p>20 megye adataival</p>
                    {selected_county_html}
                </div>
                
                {counties_html}
                
                {weather_html}
                
                <div class="legend">
                    <h4>Jelmagyarázat</h4>
                    <div class="legend-item">
                        <span class="legend-color alfold"></span>
                        Nagy Alföld (Kontinentális)
                    </div>
                    <div class="legend-item">
                        <span class="legend-color dunantul-west"></span>
                        Nyugat-Dunántúl (Óceáni)
                    </div>
                    <div class="legend-item">
                        <span class="legend-color dunantul-south"></span>
                        Dél-Dunántúl (Mediterrán)
                    </div>
                    <div class="legend-item">
                        <span class="legend-color north-hills"></span>
                        Északi-középhegység
                    </div>
                    <div class="legend-item">
                        <span class="legend-color west-border"></span>
                        Nyugati határvidék
                    </div>
                </div>
            </div>
            
            <div class="map-main">
                <div class="map-display">
                    {self._generate_hungary_svg_map()}
                </div>
                
                <div class="map-controls">
                    <p>🎯 Koordináták: {self.config.center_lat:.4f}°, {self.config.center_lon:.4f}°</p>
                    <p>🔍 Zoom szint: {self.config.zoom_level}</p>
                    <p>📊 Adatok: {len(self.counties_gdf) if self.counties_gdf is not None else 0} megye</p>
                </div>
            </div>
        </div>
        
        <div class="map-footer">
            <p>Generálva: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Magyar Klímaanalitika MVP - Static HTML Térkép</p>
        </div>
    </div>
</body>
</html>
        """.strip()
        
        return html_template
    
    def _generate_css_styles(self) -> str:
        """CSS stílusok generálása."""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        
        .map-container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            overflow: hidden;
            min-height: 90vh;
            margin-top: 2vh;
        }
        
        .map-header {
            background: linear-gradient(135deg, #2E4057 0%, #4A90E2 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }
        
        .map-header h1 {
            font-size: 28px;
            margin-bottom: 5px;
        }
        
        .subtitle {
            opacity: 0.9;
            font-size: 14px;
        }
        
        .map-content {
            display: flex;
            min-height: 600px;
        }
        
        .map-sidebar {
            width: 300px;
            background: #f8f9fa;
            padding: 20px;
            border-right: 1px solid #dee2e6;
            overflow-y: auto;
        }
        
        .map-main {
            flex: 1;
            padding: 20px;
            display: flex;
            flex-direction: column;
        }
        
        .info-panel {
            background: white;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .info-panel h3 {
            color: #2E4057;
            margin-bottom: 10px;
        }
        
        .counties-list {
            background: white;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 20px;
            max-height: 200px;
            overflow-y: auto;
        }
        
        .county-item {
            padding: 8px 12px;
            margin: 2px 0;
            border-radius: 4px;
            cursor: pointer;
            transition: background-color 0.2s;
        }
        
        .county-item:hover {
            background-color: #e9ecef;
        }
        
        .county-item.selected {
            background-color: #4A90E2;
            color: white;
        }
        
        .legend {
            background: white;
            border-radius: 8px;
            padding: 15px;
        }
        
        .legend h4 {
            color: #2E4057;
            margin-bottom: 10px;
        }
        
        .legend-item {
            display: flex;
            align-items: center;
            margin-bottom: 8px;
            font-size: 12px;
        }
        
        .legend-color {
            width: 20px;
            height: 15px;
            border-radius: 3px;
            margin-right: 8px;
            border: 1px solid #ccc;
        }
        
        .legend-color.alfold { background: #F4D03F; }
        .legend-color.dunantul-west { background: #58D68D; }
        .legend-color.dunantul-south { background: #F1948A; }
        .legend-color.north-hills { background: #5499C7; }
        .legend-color.west-border { background: #AF7AC5; }
        
        .map-display {
            flex: 1;
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 400px;
        }
        
        .hungary-map {
            max-width: 100%;
            max-height: 100%;
            filter: drop-shadow(0 4px 8px rgba(0,0,0,0.1));
        }
        
        .map-controls {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
            text-align: center;
        }
        
        .map-controls p {
            margin: 5px 0;
            font-size: 14px;
            color: #6c757d;
        }
        
        .map-footer {
            background: #2E4057;
            color: white;
            padding: 15px;
            text-align: center;
            font-size: 12px;
        }
        
        .map-footer p {
            margin: 2px 0;
            opacity: 0.8;
        }
        
        .selected-county {
            background: #e7f3ff;
            border: 2px solid #4A90E2;
            border-radius: 8px;
            padding: 12px;
            margin-top: 10px;
        }
        
        .selected-county h4 {
            color: #2E4057;
            margin-bottom: 8px;
        }
        
        .coord-info {
            font-size: 12px;
            color: #6c757d;
            margin-top: 5px;
        }
        """
    
    def _generate_counties_list_html(self) -> str:
        """Megyék listájának HTML generálása."""
        if not self.counties_gdf is not None:
            return ""
        
        counties_items = []
        for _, county_row in self.counties_gdf.iterrows():
            county_name = county_row.get('megye', 'Ismeretlen')
            is_selected = (county_name == self.config.selected_county)
            css_class = "county-item selected" if is_selected else "county-item"
            
            counties_items.append(f'<div class="{css_class}">{county_name}</div>')
        
        counties_html = f"""
        <div class="counties-list">
            <h4>Magyar Megyék ({len(counties_items)})</h4>
            {''.join(counties_items)}
        </div>
        """
        
        return counties_html
    
    def _generate_selected_county_html(self) -> str:
        """Kiválasztott megye információk HTML-je."""
        if not self.config.selected_county:
            return ""
        
        # Megye adatok keresése
        county_info = "Adatok betöltése..."
        coords = "Koordináták számítása..."
        
        if self.counties_gdf is not None:
            county_row = self.counties_gdf[self.counties_gdf['megye'] == self.config.selected_county]
            if not county_row.empty:
                geometry = county_row.geometry.iloc[0]
                bounds = geometry.bounds
                centroid = geometry.centroid
                
                coords = f"Központ: {centroid.y:.4f}°, {centroid.x:.4f}°"
                area_info = f"Határoló: {bounds[2]-bounds[0]:.3f}° × {bounds[3]-bounds[1]:.3f}°"
                county_info = f"{coords}<br>{area_info}"
        
        selected_html = f"""
        <div class="selected-county">
            <h4>🎯 Kiválasztott megye</h4>
            <p><strong>{self.config.selected_county}</strong></p>
            <div class="coord-info">{county_info}</div>
        </div>
        """
        
        return selected_html
    
    def _generate_weather_overlay_html(self) -> str:
        """Időjárási overlay HTML generálása."""
        if not self.weather_data:
            return ""
        
        weather_html = """
        <div class="weather-overlay">
            <h4>🌤️ Időjárási Adatok</h4>
            <p>Overlay aktív</p>
        </div>
        """
        
        return weather_html
    
    def _generate_hungary_svg_map(self) -> str:
        """Magyarország egyszerű SVG térképe."""
        # Egyszerű Magyarország kontúr SVG
        hungary_svg = """
        <svg class="hungary-map" viewBox="0 0 400 200" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <linearGradient id="hungaryGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#4A90E2;stop-opacity:0.3" />
                    <stop offset="100%" style="stop-color:#2E4057;stop-opacity:0.5" />
                </linearGradient>
            </defs>
            
            <!-- Magyarország egyszerűsített kontúr -->
            <path d="M50 100 L80 80 L120 70 L160 75 L200 70 L240 75 L280 80 L320 85 L350 90 L370 100 L380 120 L370 140 L350 150 L320 155 L280 150 L240 145 L200 150 L160 145 L120 140 L80 130 L50 120 Z" 
                  fill="url(#hungaryGradient)" 
                  stroke="#2E4057" 
                  stroke-width="2"/>
            
            <!-- Megye határok (egyszerűsített) -->
            <line x1="100" y1="70" x2="110" y2="150" stroke="#2E4057" stroke-width="1" opacity="0.5"/>
            <line x1="150" y1="75" x2="160" y2="145" stroke="#2E4057" stroke-width="1" opacity="0.5"/>
            <line x1="200" y1="70" x2="200" y2="150" stroke="#2E4057" stroke-width="1" opacity="0.5"/>
            <line x1="250" y1="75" x2="240" y2="145" stroke="#2E4057" stroke-width="1" opacity="0.5"/>
            <line x1="300" y1="80" x2="280" y2="150" stroke="#2E4057" stroke-width="1" opacity="0.5"/>
            
            <!-- Budapest jelölése -->
            <circle cx="200" cy="110" r="4" fill="#E74C3C" stroke="white" stroke-width="1"/>
            <text x="205" y="115" font-family="Arial" font-size="10" fill="#2E4057">Budapest</text>
            
            <!-- Koordináta rács -->
            <text x="10" y="20" font-family="Arial" font-size="8" fill="#6c757d">49°N</text>
            <text x="10" y="180" font-family="Arial" font-size="8" fill="#6c757d">46°N</text>
            <text x="20" y="195" font-family="Arial" font-size="8" fill="#6c757d">16°E</text>
            <text x="350" y="195" font-family="Arial" font-size="8" fill="#6c757d">22°E</text>
            
            <!-- Címsor -->
            <text x="200" y="40" text-anchor="middle" font-family="Arial" font-size="16" font-weight="bold" fill="#2E4057">
                🇭🇺 MAGYARORSZÁG
            </text>
            <text x="200" y="55" text-anchor="middle" font-family="Arial" font-size="10" fill="#6c757d">
                Static HTML Térkép
            </text>
        </svg>
        """
        
        return hungary_svg


class HungarianMapVisualizer(QWidget):
    """
    🗺️ Magyar térkép vizualizáló widget - STATIC HTML VERZIÓ.
    
    FUNKCIÓK:
    - Static HTML térkép megjelenítés (JavaScript-mentes)
    - Magyar megyék információ megjelenítés
    - Offline működés garantált
    - QWebEngineView kompatibilitás
    
    SIGNALOK:
    - map_ready(): Térkép betöltve és kész
    - county_clicked(county_name): Megyére kattintás (static verzióban nem működik)
    - export_completed(file_path): Export befejezve
    - error_occurred(message): Hiba történt
    """
    
    # Signalok
    map_ready = Signal()                    # térkép kész
    county_clicked = Signal(str)            # megye név (static-ban nem használt)
    coordinates_clicked = Signal(float, float)  # lat, lon (static-ban nem használt)
    export_completed = Signal(str)          # fájl útvonal
    error_occurred = Signal(str)            # hiba üzenet
    bounds_changed = Signal(object)         # térkép határ változás (static-ban nem használt)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Komponens inicializálás
        self.color_palette = ColorPalette()
        
        # Adatok
        self.map_config = MapConfig()
        self.counties_gdf = None
        self.current_weather_data = None
        self.current_html_path = None
        
        # Worker threads
        self.map_generator = None
        
        # UI építés
        self._setup_ui()
        self._setup_theme()
        self._connect_signals()
        
        # Alapértelmezett térkép generálása
        self._generate_default_map()
    
    def _setup_ui(self):
        """
        🎨 UI komponensek létrehozása - STATIC HTML VERZIÓ.
        """
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # === TÉRKÉP VEZÉRLŐK - STATIC VERZIÓ ===
        
        controls_group = QGroupBox("🗺️ Static HTML Térkép Beállítások")
        register_widget_for_theming(controls_group, "container")
        controls_layout = QHBoxLayout(controls_group)
        
        # Megyehatárok checkbox
        self.counties_check = QCheckBox("Megyehatárok")
        self.counties_check.setChecked(True)
        register_widget_for_theming(self.counties_check, "input")
        controls_layout.addWidget(self.counties_check)
        
        # Időjárási overlay checkbox
        self.weather_check = QCheckBox("Időjárási adatok")
        self.weather_check.setChecked(False)
        register_widget_for_theming(self.weather_check, "input")
        controls_layout.addWidget(self.weather_check)
        
        # Frissítés gomb
        self.refresh_btn = QPushButton("🔄 Frissítés")
        self.refresh_btn.setToolTip("Static térkép újragenerálása")
        register_widget_for_theming(self.refresh_btn, "button")
        controls_layout.addWidget(self.refresh_btn)
        
        # Export gomb
        self.export_btn = QPushButton("💾 Export")
        self.export_btn.setToolTip("Static térkép exportálása HTML fájlba")
        register_widget_for_theming(self.export_btn, "button")
        controls_layout.addWidget(self.export_btn)
        
        # Alaphelyzet gomb
        self.reset_btn = QPushButton("🏠 Alaphelyzet")
        self.reset_btn.setToolTip("Térkép visszaállítása alaphelyzetre")
        register_widget_for_theming(self.reset_btn, "button")
        controls_layout.addWidget(self.reset_btn)
        
        controls_layout.addStretch()
        layout.addWidget(controls_group)
        
        # === PROGRESS BAR ===
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        register_widget_for_theming(self.progress_bar, "input")
        layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Static HTML térkép inicializálása...")
        register_widget_for_theming(self.status_label, "text")
        layout.addWidget(self.status_label)
        
        # === WEBENGINE VIEW ===
        
        self.web_view = QWebEngineView()
        register_widget_for_theming(self.web_view, "container")
        layout.addWidget(self.web_view)
        
        # Layout súlyok
        layout.setStretchFactor(controls_group, 0)
        layout.setStretchFactor(self.web_view, 1)
    
    def _setup_theme(self):
        """
        🎨 Téma beállítások alkalmazása.
        """
        register_widget_for_theming(self, "container")
    
    def _connect_signals(self):
        """
        🔗 Signal-slot kapcsolatok létrehozása - STATIC VERZIÓ.
        """
        # UI vezérlők
        self.counties_check.toggled.connect(self._on_counties_toggled)
        self.weather_check.toggled.connect(self._on_weather_toggled)
        self.refresh_btn.clicked.connect(self._refresh_map)
        self.export_btn.clicked.connect(self._export_map)
        self.reset_btn.clicked.connect(self.reset_map_view)
        
        # WebEngine események
        self.web_view.loadFinished.connect(self._on_map_loaded)
    
    def _generate_default_map(self):
        """
        🗺️ Alapértelmezett static térkép generálása.
        """
        self._start_map_generation()
    
    def _start_map_generation(self):
        """
        🔄 Static térkép generálás indítása háttérben.
        """
        if self.map_generator and self.map_generator.isRunning():
            return  # Már fut egy generálás
        
        # Progress bar megjelenítése
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("🔄 Static HTML térkép generálása...")
        
        # Worker létrehozása
        self.map_generator = StaticMapGenerator(
            config=self.map_config,
            counties_gdf=self.counties_gdf,
            weather_data=self.current_weather_data
        )
        
        # Worker signalok
        self.map_generator.progress_updated.connect(self.progress_bar.setValue)
        self.map_generator.status_updated.connect(self.status_label.setText)
        self.map_generator.map_generated.connect(self._on_map_generated)
        self.map_generator.error_occurred.connect(self._on_map_error)
        
        # Worker indítása
        self.map_generator.start()
    
    def _on_map_generated(self, html_path: str):
        """
        ✅ Static térkép generálás befejezve.
        """
        self.current_html_path = html_path
        
        # HTML betöltése WebEngine-be
        file_url = QUrl.fromLocalFile(os.path.abspath(html_path))
        self.web_view.load(file_url)
        
        self.progress_bar.setVisible(False)
        self.status_label.setText("✅ Static HTML térkép betöltve!")
        
        # Timer a status eltüntetéséhez
        QTimer.singleShot(3000, lambda: self.status_label.setText("Static térkép kész használatra ✨"))
    
    def _on_map_error(self, error_message: str):
        """
        ❌ Térkép generálási hiba.
        """
        self.progress_bar.setVisible(False)
        self.status_label.setText("❌ Static térkép generálási hiba!")
        
        print(f"❌ Static map generation error: {error_message}")
        self.error_occurred.emit(error_message)
    
    def _on_map_loaded(self, success: bool):
        """
        🗺️ WebEngine static térkép betöltés befejezve.
        """
        if success:
            self.map_ready.emit()
            print("✅ Static HTML map loaded successfully in WebEngine")
        else:
            self.error_occurred.emit("WebEngine static térkép betöltési hiba!")
    
    def _on_counties_toggled(self, checked: bool):
        """
        🗺️ Megyehatárok megjelenítés kapcsoló.
        """
        self.map_config.show_counties = checked
        print(f"🗺️ Static counties display: {checked}")
    
    def _on_weather_toggled(self, checked: bool):
        """
        🌤️ Időjárási overlay kapcsoló.
        """
        self.map_config.weather_overlay = checked
        print(f"🌤️ Static weather overlay: {checked}")
    
    def _refresh_map(self):
        """
        🔄 Static térkép manuális frissítése.
        """
        print("🔄 Manual static map refresh requested")
        self._start_map_generation()
    
    def _export_map(self):
        """
        💾 Static térkép exportálása.
        """
        if not self.current_html_path:
            QMessageBox.warning(self, "Export", "Nincs static térkép a exportáláshoz!")
            return
        
        # Fájl mentés dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Static térkép exportálása",
            f"hungarian_static_map_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
            "HTML fájlok (*.html);;Minden fájl (*)"
        )
        
        if file_path:
            try:
                # HTML fájl másolása
                import shutil
                shutil.copy2(self.current_html_path, file_path)
                
                self.export_completed.emit(file_path)
                QMessageBox.information(self, "Export", f"Static térkép sikeresen exportálva:\n{file_path}")
                
            except Exception as e:
                error_msg = f"Export hiba: {e}"
                self.error_occurred.emit(error_msg)
                QMessageBox.critical(self, "Export hiba", error_msg)
    
    # === PUBLIKUS API - STATIC VERZIÓ ===
    
    def set_counties_geodataframe(self, counties_gdf):
        """
        🗺️ Megyék GeoDataFrame beállítása.
        """
        self.counties_gdf = counties_gdf
        print(f"🗺️ Static counties GeoDataFrame set: {len(counties_gdf) if counties_gdf is not None else 0} counties")
    
    def set_weather_data(self, weather_data: Dict):
        """
        🌤️ Időjárási adatok beállítása static overlay-hez.
        """
        self.current_weather_data = weather_data
        print(f"🌤️ Weather data set for static overlay")
    
    def update_map_bounds(self, bounds: Tuple[float, float, float, float]):
        """
        🎯 Térkép határok frissítése (minx, miny, maxx, maxy) - STATIC VERZIÓ.
        """
        # Térkép centrum és zoom számítása
        center_lat = (bounds[1] + bounds[3]) / 2
        center_lon = (bounds[0] + bounds[2]) / 2
        
        # Konfiguráció frissítése
        self.map_config.center_lat = center_lat
        self.map_config.center_lon = center_lon
        
        print(f"🎯 Static map bounds updated: center=({center_lat:.4f}, {center_lon:.4f})")
        
        # Static térkép újragenerálása
        self._start_map_generation()
    
    def get_map_config(self) -> MapConfig:
        """
        📋 Jelenlegi térkép konfiguráció lekérdezése.
        """
        return self.map_config
    
    def reset_map_view(self):
        """
        🔄 Térkép nézet visszaállítása Magyarország alapértelmezett nézetére.
        """
        self.map_config.center_lat = 47.1625
        self.map_config.center_lon = 19.5033
        self.map_config.zoom_level = 7
        self.map_config.selected_county = None
        self._start_map_generation()
        print("🏠 Static map reset to default Hungary view")
    
    def set_map_style(self, style: str):
        """
        🎨 Térkép stílus programmatic beállítása - STATIC VERZIÓBAN NEM TÁMOGATOTT.
        """
        print("🎨 Static version: map style change not supported")
    
    def toggle_counties(self, show: bool):
        """
        🗺️ Megyehatárok megjelenítés programmatic kapcsolása.
        """
        self.counties_check.setChecked(show)
    
    def toggle_weather_overlay(self, show: bool):
        """
        🌤️ Időjárási overlay programmatic kapcsolása.
        """
        self.weather_check.setChecked(show)
    
    def set_selected_county(self, county_name: str):
        """
        🎯 Kiválasztott megye beállítása - ÚJ FUNKCIÓ STATIC VERZIÓHOZ.
        """
        self.map_config.selected_county = county_name
        print(f"🎯 Static map selected county: {county_name}")


# === DEMO ÉS TESZT FUNKCIÓK ===

def demo_hungarian_map_visualizer():
    """
    🧪 Hungarian Map Visualizer demo alkalmazás - STATIC HTML VERZIÓ.
    """
    import sys
    from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
    
    app = QApplication(sys.argv)
    
    # Fő ablak
    window = QMainWindow()
    window.setWindowTitle("🗺️ Hungarian Map Visualizer Demo - Static HTML")
    window.setGeometry(100, 100, 1200, 800)
    
    # Central widget
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    
    layout = QVBoxLayout(central_widget)
    
    # Map visualizer
    map_visualizer = HungarianMapVisualizer()
    layout.addWidget(map_visualizer)
    
    # Event handlers
    def on_map_ready():
        print("🗺️ Static HTML térkép betöltve és kész!")
    
    def on_export_completed(file_path):
        print(f"💾 Export befejezve: {file_path}")
    
    def on_error_occurred(message):
        print(f"❌ Hiba: {message}")
    
    # Signalok kapcsolása
    map_visualizer.map_ready.connect(on_map_ready)
    map_visualizer.export_completed.connect(on_export_completed)
    map_visualizer.error_occurred.connect(on_error_occurred)
    
    window.show()
    
    print("🗺️ Hungarian Map Visualizer Demo elindítva - STATIC HTML!")
    print("✅ JavaScript-mentes HTML térkép!")
    print("🎮 Elérhető funkciók:")
    print("   - Megyehatárok ki/be")
    print("   - Static térkép frissítés")  
    print("   - HTML export")
    print("   - Alaphelyzet visszaállítás")
    print("   - 100% offline működés")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    demo_hungarian_map_visualizer()