#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🗺️ Magyar Folium Térkép Vizualizáló - TELJES INTERAKTÍV VERZIÓ
Magyar Klímaanalitika MVP - Folium + Leaflet.js Alapú Térképes Megjelenítő

🚀 FOLIUM INTERAKTÍV TÉRKÉP:
- Teljes Leaflet.js funkcionalitás
- Kattintható magyar megyék
- Weather overlay support
- Hover tooltipek
- Zoom/Pan interakció
- JavaScript ↔ PySide6 bridge
- Téma támogatás (light/dark)

🔧 DINAMIKUS SZÍNSKÁLA JAVÍTÁS v1.1:
✅ COLOR_SCALE_GRADIENTS mapping hozzáadva
✅ _get_dynamic_gradient() metódus implementálva
✅ Hardcoded gradient lecserélve dinamikusra

FÁJL: src/gui/map_visualizer.py
"""

from typing import Dict, List, Optional, Tuple, Any, Union
import os
import json
import tempfile
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime, date
import uuid

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QComboBox, QSlider, QCheckBox, QGroupBox, QProgressBar,
    QFileDialog, QMessageBox, QSplitter, QTextEdit
)
from PySide6.QtCore import Qt, Signal, QUrl, QTimer, QThread
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebChannel import QWebChannel

# Folium import with fallback
try:
    import folium
    from folium import plugins
    import branca.colormap as cm
    FOLIUM_AVAILABLE = True
    print("✅ Folium successfully imported")
except ImportError as e:
    FOLIUM_AVAILABLE = False
    print(f"⚠️ Folium not available: {e}")

# GeoPandas import
try:
    import geopandas as gpd
    import pandas as pd
    GEOPANDAS_AVAILABLE = True
except ImportError:
    GEOPANDAS_AVAILABLE = False

# Saját modulok
from .theme_manager import register_widget_for_theming
from .color_palette import ColorPalette


@dataclass
class FoliumMapConfig:
    """
    🗺️ Folium térkép konfigurációs beállítások.
    """
    # Alap térkép beállítások
    center_lat: float = 47.1625  # Magyarország közepe
    center_lon: float = 19.5033
    zoom_start: int = 7
    min_zoom: int = 6
    max_zoom: int = 12
    
    # Térkép stílus
    tiles: str = "OpenStreetMap"  # "OpenStreetMap", "CartoDB positron", "CartoDB dark_matter"
    attr: str = "Magyar Klímaanalitika"
    
    # County layer beállítások
    show_counties: bool = True
    county_fill_color: str = "#4A90E2"
    county_fill_opacity: float = 0.4
    county_border_color: str = "#2E4057"
    county_border_weight: int = 2
    county_hover_color: str = "#E74C3C"
    
    # Weather overlay
    weather_overlay: bool = False
    weather_opacity: float = 0.6
    
    # Interaktivitás
    disable_scroll_zoom: bool = False
    dragging: bool = True
    touch_zoom: bool = True
    double_click_zoom: bool = True
    
    # Kiválasztott elemek
    selected_county: Optional[str] = None
    highlighted_counties: List[str] = field(default_factory=list)
    
    # Theme
    theme: str = "light"  # "light" vagy "dark"


class JavaScriptBridge(QWidget):
    """
    🌉 JavaScript ↔ PySide6 kommunikációs híd.
    
    Ez az osztály kezeli a Folium térkép JavaScript eseményeit
    és továbbítja őket a Python oldalra.
    """
    
    # Signalok JavaScript eseményekhez
    county_clicked = Signal(str)              # county_name
    coordinates_clicked = Signal(float, float) # lat, lon
    map_moved = Signal(float, float, int)     # lat, lon, zoom
    county_hovered = Signal(str)              # county_name
    county_unhovered = Signal()               # hover vége
    
    def __init__(self):
        super().__init__()
        self.bridge_id = str(uuid.uuid4())
        print(f"🌉 JavaScriptBridge created with ID: {self.bridge_id}")
    
    def handle_county_click(self, county_name: str):
        """Megye kattintás kezelése JavaScript-ből."""
        print(f"🖱️ JS Bridge: County clicked: {county_name}")
        self.county_clicked.emit(county_name)
    
    def handle_coordinates_click(self, lat: float, lon: float):
        """Koordináta kattintás kezelése."""
        print(f"📍 JS Bridge: Coordinates clicked: {lat}, {lon}")
        self.coordinates_clicked.emit(lat, lon)
    
    def handle_map_move(self, lat: float, lon: float, zoom: int):
        """Térkép mozgás kezelése."""
        print(f"🗺️ JS Bridge: Map moved: {lat}, {lon}, zoom={zoom}")
        self.map_moved.emit(lat, lon, zoom)
    
    def handle_county_hover(self, county_name: str):
        """Megye hover kezelése."""
        print(f"👆 JS Bridge: County hovered: {county_name}")
        self.county_hovered.emit(county_name)
    
    def handle_county_unhover(self):
        """Megye hover vége kezelése."""
        self.county_unhovered.emit()


class FoliumMapGenerator(QThread):
    """
    🔄 Háttér worker a Folium interaktív térkép generálásához.
    
    Ez a worker háttérben generálja le a teljes Folium térképet
    minden interaktív funkcióval.
    """
    
    # Signalok
    progress_updated = Signal(int)         # progress (0-100)
    map_generated = Signal(str)           # HTML fájl path
    error_occurred = Signal(str)          # error message
    status_updated = Signal(str)          # status message
    
    def __init__(self, config: FoliumMapConfig, counties_gdf=None, weather_data=None, output_path=None, bridge_id=None):
        super().__init__()
        self.config = config
        self.counties_gdf = counties_gdf
        self.weather_data = weather_data
        self.output_path = output_path or self._get_temp_html_path()
        self.bridge_id = bridge_id or str(uuid.uuid4())
    
    def _get_temp_html_path(self) -> str:
        """Ideiglenes HTML fájl útvonal generálása."""
        temp_dir = tempfile.gettempdir()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(temp_dir, f"hungarian_folium_map_{timestamp}.html")
    
    def run(self):
        """
        🗺️ Folium interaktív térkép generálása.
        """
        try:
            if not FOLIUM_AVAILABLE:
                raise ImportError("Folium library not available")
            
            self.status_updated.emit("🗺️ Folium térkép inicializálása...")
            self.progress_updated.emit(5)
            
            # === ALAP FOLIUM TÉRKÉP ===
            
            map_obj = self._create_base_folium_map()
            self.progress_updated.emit(20)
            
            # === COUNTIES LAYER ===
            
            if self.config.show_counties and self.counties_gdf is not None:
                self.status_updated.emit("🗺️ Megyehatárok hozzáadása...")
                self._add_counties_layer(map_obj)
            self.progress_updated.emit(50)
            
            # === WEATHER OVERLAY ===
            
            if self.config.weather_overlay and self.weather_data:
                self.status_updated.emit("🌤️ Időjárási overlay...")
                self._add_weather_overlay(map_obj)
            self.progress_updated.emit(70)
            
            # === JAVASCRIPT BRIDGE ===
            
            self.status_updated.emit("🌉 JavaScript interaktivitás...")
            self._add_javascript_bridge(map_obj)
            self.progress_updated.emit(85)
            
            # === MAP CONTROLS ===
            
            self._add_map_controls(map_obj)
            self.progress_updated.emit(90)
            
            # === HTML MENTÉS ===
            
            self.status_updated.emit("💾 Folium térkép mentése...")
            map_obj.save(self.output_path)
            
            # === JAVASCRIPT INJECTION ===
            
            self._inject_custom_javascript()
            
            self.progress_updated.emit(100)
            self.status_updated.emit("✅ Folium interaktív térkép elkészült!")
            self.map_generated.emit(self.output_path)
            
        except Exception as e:
            import traceback
            error_msg = f"Folium térkép generálási hiba: {e}\n{traceback.format_exc()}"
            self.error_occurred.emit(error_msg)
    
    def _create_base_folium_map(self) -> folium.Map:
        """
        🗺️ Alap Folium térkép létrehozása.
        """
        # Téma alapján tiles kiválasztása
        if self.config.theme == "dark":
            tiles = "CartoDB dark_matter"
        else:
            tiles = self.config.tiles
        
        # Folium térkép létrehozása
        map_obj = folium.Map(
            location=[self.config.center_lat, self.config.center_lon],
            zoom_start=self.config.zoom_start,
            tiles=tiles,
            attr=self.config.attr,
            min_zoom=self.config.min_zoom,
            max_zoom=self.config.max_zoom,
            control_scale=True,
            prefer_canvas=True
        )
        
        # Térkép opciók
        if self.config.disable_scroll_zoom:
            map_obj.options['scrollWheelZoom'] = False
        
        print(f"✅ Base Folium map created: {tiles}")
        return map_obj
    
    def _add_counties_layer(self, map_obj: folium.Map):
        """
        🗺️ Magyar megyék GeoJSON layer hozzáadása interaktív funkcionalitással.
        """
        if self.counties_gdf is None or len(self.counties_gdf) == 0:
            print("⚠️ No counties GeoDataFrame available")
            return
        
        print(f"📍 Adding {len(self.counties_gdf)} counties to map")
        
        # GeoJSON konvertálás
        counties_geojson = json.loads(self.counties_gdf.to_json())
        
        # Style function
        def style_function(feature):
            county_name = feature['properties'].get('megye', '')
            
            # Kiválasztott megye speciális stílus
            if county_name == self.config.selected_county:
                return {
                    'fillColor': '#E74C3C',
                    'color': '#C0392B',
                    'weight': 3,
                    'fillOpacity': 0.7,
                    'dashArray': '5, 5'
                }
            
            # Highlighted megyék
            if county_name in self.config.highlighted_counties:
                return {
                    'fillColor': '#F39C12',
                    'color': '#E67E22',
                    'weight': 3,
                    'fillOpacity': 0.6
                }
            
            # Normál stílus
            return {
                'fillColor': self.config.county_fill_color,
                'color': self.config.county_border_color,
                'weight': self.config.county_border_weight,
                'fillOpacity': self.config.county_fill_opacity
            }
        
        # Highlight function
        def highlight_function(feature):
            return {
                'fillColor': self.config.county_hover_color,
                'color': '#FFFFFF',
                'weight': 4,
                'fillOpacity': 0.8
            }
        
        # Tooltip function
        def create_tooltip(feature):
            props = feature['properties']
            county_name = props.get('megye', 'Ismeretlen')
            region = props.get('region', 'Ismeretlen régió')
            
            return f"""
            <div style="font-family: Arial; font-size: 12px;">
                <b>🏛️ {county_name}</b><br>
                🌡️ {region}<br>
                🖱️ Kattints a részletekért
            </div>
            """
        
        # GeoJson layer hozzáadása
        counties_layer = folium.GeoJson(
            counties_geojson,
            style_function=style_function,
            highlight_function=highlight_function,
            tooltip=folium.Tooltip(
                folium.Html(
                    '<b>Hover a megyére a részletekért</b>',
                    script=True
                ),
                sticky=True
            ),
            popup=folium.Popup(
                folium.Html(
                    '<b>Kattints a megyére</b>',
                    script=True
                ),
                max_width=200
            )
        )
        
        counties_layer.add_to(map_obj)
        
        print("✅ Counties layer added with interactivity")
    
    def _add_weather_overlay(self, map_obj: folium.Map):
        """
        🌤️ Időjárási adatok overlay hozzáadása HeatMap plugin-nal.
        
        Támogatott overlay típusok:
        - Hőmérséklet heatmap (°C)
        - Csapadék overlay (mm)
        - Szél sebesség (km/h)
        - Relatív páratartalom (%)
        """
        if not self.weather_data:
            print("⚠️ No weather data available for overlay")
            return
        
        print(f"🌤️ Adding weather overlay with {len(self.weather_data)} data points")
        
        try:
            # === HŐMÉRSÉKLET HEATMAP ===
            if 'temperature' in self.weather_data:
                self._add_temperature_heatmap(map_obj)
            
            # === CSAPADÉK OVERLAY ===
            if 'precipitation' in self.weather_data:
                self._add_precipitation_overlay(map_obj)
            
            # === SZÉL SEBESSÉG OVERLAY ===
            if 'wind_speed' in self.weather_data:
                self._add_wind_speed_overlay(map_obj)
            
            # === OVERLAY LEGEND ===
            self._add_weather_legend(map_obj)
            
            print("✅ Weather overlay layers added successfully")
            
        except Exception as e:
            print(f"❌ Weather overlay error: {e}")
    
    def _add_temperature_heatmap(self, map_obj: folium.Map):
        """
        🌡️ Hőmérséklet heatmap hozzáadása DINAMIKUS SZÍNSKÁLÁVAL.
        """
        try:
            from folium.plugins import HeatMap
            
            # Hőmérséklet adatok előkészítése
            temp_data = []
            for location, data in self.weather_data.get('temperature', {}).items():
                if 'coordinates' in data and 'value' in data:
                    lat, lon = data['coordinates']
                    temp = data['value']
                    
                    # Heatmap pont: [lat, lon, intensity]
                    # Intensity normalizálás -20°C - +40°C között
                    intensity = max(0.1, min(1.0, (temp + 20) / 60))
                    temp_data.append([lat, lon, intensity])
            
            if temp_data:
                # 🔧 DINAMIKUS GRADIENT GENERÁLÁS
                gradient = self._get_dynamic_gradient('RdYlBu_r', 'temperature')
                
                # HeatMap layer létrehozása dinamikus gradienttel
                heat_map = HeatMap(
                    temp_data,
                    name="🌡️ Hőmérséklet",
                    min_opacity=0.3,
                    max_zoom=18,
                    radius=25,
                    blur=15,
                    gradient=gradient  # 🔥 DINAMIKUS GRADIENT!
                )
                
                # Hozzáadás a térképhez
                heat_map.add_to(map_obj)
                
                print(f"🌡️ Temperature heatmap added with {len(temp_data)} points (dynamic gradient)")
            
        except ImportError:
            print("⚠️ HeatMap plugin not available")
        except Exception as e:
            print(f"❌ Temperature heatmap error: {e}")
    
    def _get_dynamic_gradient(self, color_scale: str, overlay_type: str) -> Dict[float, str]:
        """
        🔧 KRITIKUS ÚJ METÓDUS: Dinamikus gradient generálás color_scale alapján
        
        Args:
            color_scale: Weather Data Bridge-ből ('RdYlBu_r', 'Blues', 'Greens', 'Oranges')
            overlay_type: Overlay típus ('temperature', 'precipitation', 'wind_speed', 'wind_gusts')
            
        Returns:
            Folium HeatMap gradient dict
        """
        # 🎨 DINAMIKUS SZÍNSKÁLA MAPPING
        COLOR_SCALE_GRADIENTS = {
            'RdYlBu_r': {  # Hőmérséklet - Kék (hideg) → Piros (meleg)
                0.0: '#0000FF',  # Kék
                0.2: '#00BFFF',  # Világoskék  
                0.4: '#87CEEB',  # Égkék
                0.6: '#FFFF00',  # Sárga
                0.8: '#FFA500',  # Narancs
                1.0: '#FF0000'   # Piros
            },
            'Blues': {  # Csapadék - Fehér → Sötétkék
                0.0: '#F0F8FF',  # Alice Blue (szinte fehér)
                0.2: '#E6F3FF',  # Nagyon világoskék
                0.4: '#B3D9FF',  # Világoskék
                0.6: '#4D94FF',  # Közepes kék
                0.8: '#0066CC',  # Sötétkék
                1.0: '#003366'   # Nagyon sötétkék
            },
            'Greens': {  # Szél - Világoszöld → Sötétzöld
                0.0: '#F0FFF0',  # Honeydew (szinte fehér)
                0.2: '#98FB98',  # Pale Green
                0.4: '#90EE90',  # Light Green
                0.6: '#32CD32',  # Lime Green
                0.8: '#228B22',  # Forest Green
                1.0: '#006400'   # Dark Green
            },
            'Oranges': {  # Széllökés - Világos narancs → Sötét narancs/piros
                0.0: '#FFF8DC',  # Cornsilk (krémszín)
                0.2: '#FFEFD5',  # Papaya Whip
                0.4: '#FFE4B5',  # Moccasin  
                0.6: '#FFA500',  # Orange
                0.8: '#FF4500',  # Orange Red
                1.0: '#DC143C'   # Crimson
            }
        }
        
        try:
            # Direkt color_scale mapping
            if color_scale in COLOR_SCALE_GRADIENTS:
                gradient = COLOR_SCALE_GRADIENTS[color_scale]
                print(f"🎨 Dynamic gradient: {color_scale} → {len(gradient)} színfokozat")
                return gradient
            
            # Fallback: overlay_type alapú mapping
            fallback_mapping = {
                'temperature': 'RdYlBu_r',
                'precipitation': 'Blues', 
                'wind_speed': 'Greens',
                'wind_gusts': 'Oranges'
            }
            
            fallback_scale = fallback_mapping.get(overlay_type, 'RdYlBu_r')
            if fallback_scale in COLOR_SCALE_GRADIENTS:
                gradient = COLOR_SCALE_GRADIENTS[fallback_scale]
                print(f"⚠️ Fallback gradient: {color_scale} → {fallback_scale}")
                return gradient
            
            # Ultimate fallback
            print(f"❌ Ismeretlen color_scale és overlay_type: {color_scale}, {overlay_type}")
            return COLOR_SCALE_GRADIENTS['RdYlBu_r']  # Default hőmérséklet
            
        except Exception as e:
            print(f"❌ Gradient generálási hiba: {e}")
            return COLOR_SCALE_GRADIENTS['RdYlBu_r']  # Safe fallback
    
    def _add_precipitation_overlay(self, map_obj: folium.Map):
        """
        🌧️ Csapadék overlay hozzáadása CircleMarker-ekkel.
        """
        try:
            precip_data = self.weather_data.get('precipitation', {})
            
            # Csapadék színskála
            def get_precipitation_color(mm):
                if mm == 0:
                    return '#CCCCCC'  # Szürke - nincs csapadék
                elif mm < 1:
                    return '#E8F4FD'  # Nagyon világos kék
                elif mm < 5:
                    return '#BFE6FF'  # Világos kék
                elif mm < 10:
                    return '#80D0FF'  # Közepes kék
                elif mm < 25:
                    return '#40AAFF'  # Erős kék
                elif mm < 50:
                    return '#0080FF'  # Sötét kék
                else:
                    return '#0040AA'  # Nagyon sötét kék
            
            # CircleMarker-ek hozzáadása
            for location, data in precip_data.items():
                if 'coordinates' in data and 'value' in data:
                    lat, lon = data['coordinates']
                    precip_mm = data['value']
                    
                    # Circle méret csapadék mennyiség alapján
                    radius = max(3, min(20, precip_mm / 2))
                    color = get_precipitation_color(precip_mm)
                    
                    # CircleMarker létrehozása
                    folium.CircleMarker(
                        location=[lat, lon],
                        radius=radius,
                        popup=f"🌧️ {location}<br>Csapadék: {precip_mm:.1f} mm",
                        color='#FFFFFF',
                        weight=1,
                        fillColor=color,
                        fillOpacity=0.7,
                        tooltip=f"{precip_mm:.1f} mm"
                    ).add_to(map_obj)
            
            print(f"🌧️ Precipitation overlay added with {len(precip_data)} points")
            
        except Exception as e:
            print(f"❌ Precipitation overlay error: {e}")
    
    def _add_wind_speed_overlay(self, map_obj: folium.Map):
        """
        💨 Szél sebesség overlay hozzáadása nyilakkal.
        """
        try:
            wind_data = self.weather_data.get('wind_speed', {})
            
            # Szél színskála Beaufort skála alapján
            def get_wind_color(kmh):
                if kmh < 6:      return '#C0C0C0'  # Szélcsend - Szürke
                elif kmh < 12:   return '#00FF00'  # Enyhe szél - Zöld
                elif kmh < 20:   return '#FFFF00'  # Gyenge szél - Sárga  
                elif kmh < 29:   return '#FFA500'  # Mérsékelt szél - Narancs
                elif kmh < 39:   return '#FF8000'  # Élénk szél - Narancssárga
                elif kmh < 50:   return '#FF4000'  # Erős szél - Vörös-narancs
                elif kmh < 62:   return '#FF0000'  # Viharos szél - Piros
                else:            return '#800000'  # Orkán - Sötét piros
            
            # Szél nyilak hozzáadása
            for location, data in wind_data.items():
                if 'coordinates' in data and 'speed' in data:
                    lat, lon = data['coordinates']
                    speed_kmh = data['speed']
                    direction = data.get('direction', 0)  # fok
                    
                    # Nyíl méret sebesség alapján
                    arrow_size = max(5, min(15, speed_kmh / 5))
                    color = get_wind_color(speed_kmh)
                    
                    # Szél irány nyíl SVG icon
                    wind_icon = f"""
                    <svg width="20" height="20" viewBox="0 0 20 20" style="transform: rotate({direction}deg)">
                        <path d="M10,2 L15,18 L10,15 L5,18 Z" fill="{color}" stroke="#000" stroke-width="1"/>
                    </svg>
                    """
                    
                    # DivIcon használata az SVG nyílhoz
                    wind_marker = folium.Marker(
                        location=[lat, lon],
                        icon=folium.DivIcon(
                            html=wind_icon,
                            class_name="wind-arrow",
                            icon_size=(20, 20),
                            icon_anchor=(10, 10)
                        ),
                        popup=f"💨 {location}<br>Szél: {speed_kmh:.1f} km/h<br>Irány: {direction}°",
                        tooltip=f"{speed_kmh:.1f} km/h"
                    )
                    
                    wind_marker.add_to(map_obj)
            
            print(f"💨 Wind speed overlay added with {len(wind_data)} points")
            
        except Exception as e:
            print(f"❌ Wind speed overlay error: {e}")
    
    def _add_weather_legend(self, map_obj: folium.Map):
        """
        📊 Weather overlay legend hozzáadása.
        """
        try:
            # Legend HTML
            legend_html = '''
            <div style="position: fixed; 
                        top: 80px; right: 20px; width: 200px; height: auto; 
                        background-color: rgba(255, 255, 255, 0.9);
                        border: 2px solid grey; z-index:9999; 
                        font-size: 12px; padding: 10px;
                        border-radius: 5px;
                        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                        ">
            <h4 style="margin-top: 0; color: #2E4057;">🌤️ Időjárási Overlay</h4>
            
            <p><b>🌡️ Hőmérséklet:</b></p>
            <div style="background: linear-gradient(to right, #0000FF, #00FFFF, #00FF00, #FFFF00, #FF8000, #FF0000); 
                        height: 15px; margin: 5px 0;"></div>
            <div style="display: flex; justify-content: space-between; font-size: 10px;">
                <span>-20°C</span><span>+40°C</span>
            </div>
            
            <p style="margin-top: 15px;"><b>🌧️ Csapadék:</b></p>
            <div style="display: flex; align-items: center; margin: 5px 0;">
                <div style="width: 10px; height: 10px; background: #E8F4FD; border-radius: 50%; margin-right: 5px;"></div>
                <span style="font-size: 10px;">< 1 mm</span>
            </div>
            <div style="display: flex; align-items: center; margin: 5px 0;">
                <div style="width: 15px; height: 15px; background: #80D0FF; border-radius: 50%; margin-right: 5px;"></div>
                <span style="font-size: 10px;">5-10 mm</span>
            </div>
            <div style="display: flex; align-items: center; margin: 5px 0;">
                <div style="width: 20px; height: 20px; background: #0080FF; border-radius: 50%; margin-right: 5px;"></div>
                <span style="font-size: 10px;">> 25 mm</span>
            </div>
            
            <p style="margin-top: 15px;"><b>💨 Szél:</b></p>
            <div style="font-size: 10px;">
                <div>🟢 < 12 km/h - Enyhe</div>
                <div>🟡 12-20 km/h - Gyenge</div>
                <div>🟠 20-39 km/h - Mérsékelt</div>
                <div>🔴 > 50 km/h - Erős</div>
            </div>
            </div>
            '''
            
            # Legend hozzáadása a térképhez
            map_obj.get_root().html.add_child(folium.Element(legend_html))
            
            print("📊 Weather legend added")
            
        except Exception as e:
            print(f"❌ Weather legend error: {e}")
    
    def _add_javascript_bridge(self, map_obj: folium.Map):
        """
        🌉 JavaScript bridge kód hozzáadása a térképhez.
        """
        # Custom JavaScript kód a bridge kommunikációhoz
        bridge_js = f"""
        <script>
        // Magyar Klímaanalitika - JavaScript Bridge
        console.log('🌉 JavaScript Bridge inicializálása...');
        
        var bridgeId = '{self.bridge_id}';
        
        // QWebChannel initialization
        var channel = null;
        var qtBridge = null;
        
        // Initialize QWebChannel when available
        function initializeQtBridge() {{
            if (typeof qt !== 'undefined' && qt.webChannelTransport) {{
                try {{
                    new QWebChannel(qt.webChannelTransport, function(ch) {{
                        channel = ch;
                        qtBridge = channel.objects.qtBridge;
                        console.log('✅ QWebChannel bridge initialized successfully');
                    }});
                }} catch(e) {{
                    console.log('⚠️ QWebChannel initialization failed:', e);
                }}
            }} else {{
                console.log('⚠️ QWebChannel not available, retrying in 500ms...');
                setTimeout(initializeQtBridge, 500);
            }}
        }}
        
        // County click handler
        function handleCountyClick(countyName) {{
            console.log('🖱️ County clicked:', countyName);
            if (qtBridge && qtBridge.handle_county_click) {{
                qtBridge.handle_county_click(countyName);
            }} else {{
                console.log('⚠️ qtBridge not available for county click');
            }}
        }}
        
        // Coordinates click handler
        function handleCoordinatesClick(lat, lon) {{
            console.log('📍 Coordinates clicked:', lat, lon);
            if (qtBridge && qtBridge.handle_coordinates_click) {{
                qtBridge.handle_coordinates_click(lat, lon);
            }} else {{
                console.log('⚠️ qtBridge not available for coordinates click');
            }}
        }}
        
        // Map move handler with null check
        function handleMapMove(lat, lon, zoom) {{
            console.log('🗺️ Map moved:', lat, lon, 'zoom:', zoom);
            if (qtBridge && typeof qtBridge.handle_map_move === 'function') {{
                qtBridge.handle_map_move(lat, lon, zoom);
            }} else {{
                console.log('⚠️ qtBridge.handle_map_move not available');
            }}
        }}
        
        // Document ready
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('📄 DOM ready, initializing bridge...');
            
            // Initialize QWebChannel
            initializeQtBridge();
            
            // Map click események figyelése
            setTimeout(function() {{
                if (typeof window.map_{map_obj._id} !== 'undefined') {{
                    var map = window.map_{map_obj._id};
                    
                    // Map click event
                    map.on('click', function(e) {{
                        handleCoordinatesClick(e.latlng.lat, e.latlng.lng);
                    }});
                    
                    // Map move event with protection
                    map.on('moveend', function(e) {{
                        try {{
                            var center = map.getCenter();
                            var zoom = map.getZoom();
                            handleMapMove(center.lat, center.lng, zoom);
                        }} catch(err) {{
                            console.log('⚠️ Map move event error:', err);
                        }}
                    }});
                    
                    console.log('🗺️ Map event listeners attached');
                }} else {{
                    console.log('⚠️ Map object not found, retrying...');
                    setTimeout(arguments.callee, 1000);
                }}
            }}, 1000);
        }});
        
        // QWebChannel script loading
        if (typeof QWebChannel === 'undefined') {{
            console.log('📥 Loading QWebChannel script...');
            var script = document.createElement('script');
            script.src = 'qrc:///qtwebchannel/qwebchannel.js';
            script.onload = function() {{
                console.log('✅ QWebChannel script loaded');
                initializeQtBridge();
            }};
            script.onerror = function() {{
                console.log('❌ Failed to load QWebChannel script');
            }};
            document.head.appendChild(script);
        }} else {{
            initializeQtBridge();
        }}
        </script>
        """
        
        # JavaScript kód hozzáadása a térképhez
        map_obj.get_root().html.add_child(folium.Element(bridge_js))
        
        print("✅ JavaScript bridge added to map")
    
    def _add_map_controls(self, map_obj: folium.Map):
        """
        🎮 További térkép vezérlők hozzáadása.
        """
        # Fullscreen control
        plugins.Fullscreen().add_to(map_obj)
        
        # Measure control
        plugins.MeasureControl().add_to(map_obj)
        
        # Mouse position
        plugins.MousePosition(
            position='bottomright',
            separator=' | ',
            empty_string='Koordináták...',
            lng_first=False,
            num_digits=20,
            prefix='Pos: ',
            lat_formatter="function(num) {return L.Util.formatNum(num, 4) + '°';}",
            lng_formatter="function(num) {return L.Util.formatNum(num, 4) + '°';}"
        ).add_to(map_obj)
        
        # MiniMap
        minimap = plugins.MiniMap(
            tile_layer="OpenStreetMap",
            position='bottomleft',
            width=150,
            height=150,
            collapsed_width=25,
            collapsed_height=25,
            zoom_level_offset=-5,
            zoom_animation=True
        )
        minimap.add_to(map_obj)
        
        print("✅ Map controls added")
    
    def _inject_custom_javascript(self):
        """
        💉 Custom JavaScript kód injektálása a generált HTML-be.
        """
        try:
            # HTML fájl beolvasása
            with open(self.output_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Custom CSS és JavaScript hozzáadása
            custom_head = """
            <style>
            /* Magyar Klímaanalitika Custom Styles */
            .folium-map {
                border-radius: 8px !important;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1) !important;
            }
            
            .leaflet-popup-content {
                font-family: 'Segoe UI', Arial, sans-serif !important;
                color: #2E4057 !important;
            }
            
            .leaflet-tooltip {
                background: rgba(46, 64, 87, 0.9) !important;
                color: white !important;
                border: none !important;
                border-radius: 4px !important;
                font-size: 12px !important;
            }
            </style>
            """
            
            # HTML módosítása
            html_content = html_content.replace('</head>', custom_head + '</head>')
            
            # Módosított HTML mentése
            with open(self.output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print("✅ Custom JavaScript injected")
            
        except Exception as e:
            print(f"⚠️ Failed to inject custom JavaScript: {e}")


class HungarianMapVisualizer(QWidget):
    """
    🗺️ Magyar Folium térkép vizualizáló widget - TELJES INTERAKTÍV VERZIÓ.
    
    FUNKCIÓK:
    - Folium + Leaflet.js alapú interaktív térkép
    - Kattintható magyar megyék
    - Hover tooltipek és popupok
    - Weather overlay support
    - JavaScript ↔ PySide6 bridge
    - Téma támogatás
    - Export funkciók
    
    SIGNALOK:
    - map_ready(): Térkép betöltve és kész
    - county_clicked(county_name): Megyére kattintás
    - coordinates_clicked(lat, lon): Koordináta kattintás
    - export_completed(file_path): Export befejezve
    - error_occurred(message): Hiba történt
    """
    
    # Signalok
    map_ready = Signal()                           # térkép kész
    county_clicked = Signal(str)                   # megye név
    coordinates_clicked = Signal(float, float)     # lat, lon
    map_moved = Signal(float, float, int)          # lat, lon, zoom
    county_hovered = Signal(str)                   # megye hover
    export_completed = Signal(str)                 # fájl útvonal
    error_occurred = Signal(str)                   # hiba üzenet
    bounds_changed = Signal(object)                # térkép határ változás
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Komponens inicializálás
        self.color_palette = ColorPalette()
        
        # Folium konfiguráció
        self.map_config = FoliumMapConfig()
        
        # Adatok
        self.counties_gdf = None
        self.current_weather_data = None
        self.current_html_path = None
        
        # Worker threads
        self.map_generator = None
        
        # JavaScript Bridge
        self.js_bridge = JavaScriptBridge()
        self.web_channel = QWebChannel()
        
        # UI építés
        self._setup_ui()
        self._setup_theme()
        self._connect_signals()
        
        # Folium elérhetőség ellenőrzése
        if FOLIUM_AVAILABLE:
            self._generate_default_map()
        else:
            self._show_folium_error()
    
    def _setup_ui(self):
        """
        🎨 UI komponensek létrehozása - FOLIUM VERZIÓ.
        """
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # === FOLIUM TÉRKÉP VEZÉRLŐK ===
        
        controls_group = QGroupBox("🗺️ Folium Interaktív Térkép")
        register_widget_for_theming(controls_group, "container")
        controls_layout = QHBoxLayout(controls_group)
        
        # Térkép stílus választó
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
        
        # Megyehatárok checkbox
        self.counties_check = QCheckBox("Megyehatárok")
        self.counties_check.setChecked(True)
        register_widget_for_theming(self.counties_check, "input")
        controls_layout.addWidget(self.counties_check)
        
        # Időjárási overlay checkbox
        self.weather_check = QCheckBox("Időjárási overlay")
        self.weather_check.setChecked(False)
        register_widget_for_theming(self.weather_check, "input")
        controls_layout.addWidget(self.weather_check)
        
        # Zoom kontroll
        zoom_label = QLabel("Zoom:")
        register_widget_for_theming(zoom_label, "text")
        controls_layout.addWidget(zoom_label)
        
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setRange(6, 12)
        self.zoom_slider.setValue(7)
        self.zoom_slider.setToolTip("Térkép nagyítás szintje")
        register_widget_for_theming(self.zoom_slider, "input")
        controls_layout.addWidget(self.zoom_slider)
        
        controls_layout.addStretch()
        
        # Akció gombok
        self.refresh_btn = QPushButton("🔄 Frissítés")
        self.refresh_btn.setToolTip("Folium térkép újragenerálása")
        register_widget_for_theming(self.refresh_btn, "button")
        controls_layout.addWidget(self.refresh_btn)
        
        self.export_btn = QPushButton("💾 Export")
        self.export_btn.setToolTip("Folium térkép exportálása")
        register_widget_for_theming(self.export_btn, "button")
        controls_layout.addWidget(self.export_btn)
        
        self.reset_btn = QPushButton("🏠 Alaphelyzet")
        self.reset_btn.setToolTip("Térkép visszaállítása")
        register_widget_for_theming(self.reset_btn, "button")
        controls_layout.addWidget(self.reset_btn)
        
        layout.addWidget(controls_group)
        
        # === PROGRESS BAR ===
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        register_widget_for_theming(self.progress_bar, "input")
        layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Folium interaktív térkép inicializálása...")
        register_widget_for_theming(self.status_label, "text")
        layout.addWidget(self.status_label)
        
        # === WEBENGINE VIEW + JAVASCRIPT BRIDGE ===
        
        self.web_view = QWebEngineView()
        register_widget_for_theming(self.web_view, "container")
        
        # 🔧 WEBENGINE SETTINGS FIX - Same-Origin Policy engedélyezés
        try:
            from PySide6.QtWebEngineCore import QWebEngineSettings
            
            settings = self.web_view.settings()
            # Helyi fájlok elérés engedélyezése
            settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
            settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True) 
            settings.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
            settings.setAttribute(QWebEngineSettings.AllowRunningInsecureContent, True)
            # JavaScript debugging
            settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
            settings.setAttribute(QWebEngineSettings.ErrorPageEnabled, True)
            # WebGL és Canvas engedélyezés
            settings.setAttribute(QWebEngineSettings.WebGLEnabled, True)
            settings.setAttribute(QWebEngineSettings.Accelerated2dCanvasEnabled, True)
            
            print("✅ WebEngine settings configured for local content access")
            
        except ImportError as e:
            print(f"⚠️ WebEngineSettings not available: {e}")
        
        # WebChannel setup JavaScript bridge-hez
        self.web_channel.registerObject("qtBridge", self.js_bridge)
        self.web_view.page().setWebChannel(self.web_channel)
        
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
        🔗 Signal-slot kapcsolatok létrehozása - FOLIUM VERZIÓ.
        """
        # UI vezérlők
        self.style_combo.currentTextChanged.connect(self._on_style_changed)
        self.counties_check.toggled.connect(self._on_counties_toggled)
        self.weather_check.toggled.connect(self._on_weather_toggled)
        self.zoom_slider.valueChanged.connect(self._on_zoom_changed)
        
        self.refresh_btn.clicked.connect(self._refresh_map)
        self.export_btn.clicked.connect(self._export_map)
        self.reset_btn.clicked.connect(self.reset_map_view)
        
        # WebEngine események
        self.web_view.loadFinished.connect(self._on_map_loaded)
        
        # JavaScript Bridge signalok
        self.js_bridge.county_clicked.connect(self._on_js_county_clicked)
        self.js_bridge.coordinates_clicked.connect(self._on_js_coordinates_clicked)
        self.js_bridge.map_moved.connect(self._on_js_map_moved)
        self.js_bridge.county_hovered.connect(self._on_js_county_hovered)
        
        print("✅ Folium MapVisualizer signals connected")
    
    def _show_folium_error(self):
        """
        ❌ Folium hiány esetén hibaüzenet megjelenítése.
        """
        self.status_label.setText("❌ Folium library hiányzik! pip install folium")
        self.progress_bar.setVisible(False)
        
        # Vezérlők letiltása
        self.refresh_btn.setEnabled(False)
        self.export_btn.setEnabled(False)
        
        error_msg = "Folium library not installed. Please run: pip install folium branca"
        self.error_occurred.emit(error_msg)
    
    def _generate_default_map(self):
        """
        🗺️ Alapértelmezett Folium térkép generálása.
        """
        if not FOLIUM_AVAILABLE:
            return
        
        self._start_map_generation()
    
    def _start_map_generation(self):
        """
        🔄 Folium térkép generálás indítása háttérben.
        """
        if not FOLIUM_AVAILABLE:
            self._show_folium_error()
            return
        
        if self.map_generator and self.map_generator.isRunning():
            return  # Már fut egy generálás
        
        # Progress bar megjelenítése
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("🔄 Folium interaktív térkép generálása...")
        
        # Worker létrehozása
        self.map_generator = FoliumMapGenerator(
            config=self.map_config,
            counties_gdf=self.counties_gdf,
            weather_data=self.current_weather_data,
            bridge_id=self.js_bridge.bridge_id
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
        ✅ Folium térkép generálás befejezve.
        """
        self.current_html_path = html_path
        
        # 🔧 WEBENGINE FIX: Proper file URL handling
        file_url = QUrl.fromLocalFile(os.path.abspath(html_path))
        
        print(f"🔧 DEBUG: Loading Folium HTML: {file_url.toString()}")
        
        # 🚀 DELAYED LOADING FIX: WebEngine késleltetett betöltés
        QTimer.singleShot(500, lambda: self._load_folium_html_delayed(file_url))
        
        self.progress_bar.setVisible(False)
        self.status_label.setText("🔄 Folium térkép WebEngine betöltése...")
        
        print(f"✅ Folium map generated: {html_path}")
    
    def _load_folium_html_delayed(self, file_url: QUrl):
        """
        🚀 FIXED: HTML Content Injection - Same-Origin Policy megkerülés.
        
        A file:// protokoll korlátozások helyett a HTML tartalmát 
        közvetlenül injektáljuk a WebEngine-be.
        """
        try:
            # WebEngine reset before loading
            self.web_view.stop()
            
            # 🔧 HTML CONTENT INJECTION FIX
            html_path = file_url.toLocalFile()
            
            # HTML tartalom beolvasása
            with open(html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Base URL meghatározása a relatív hivatkozásokhoz
            base_url = QUrl.fromLocalFile(os.path.dirname(html_path))
            
            # HTML tartalom közvetlen betöltése Same-Origin Policy megkerüléssel
            self.web_view.setHtml(html_content, base_url)
            
            print(f"✅ HTML Content Injection: {html_path}")
            print(f"📁 Base URL for relative paths: {base_url.toString()}")
            
            # Status update
            self.status_label.setText("🔧 HTML Content Injection - Same-Origin Policy megkerülése...")
            
        except Exception as e:
            error_msg = f"HTML Content Injection hiba: {e}"
            print(f"❌ HTML Injection Error: {error_msg}")
            self.error_occurred.emit(error_msg)
    
    def _on_map_error(self, error_message: str):
        """
        ❌ Térkép generálási hiba.
        """
        self.progress_bar.setVisible(False)
        self.status_label.setText("❌ Folium térkép generálási hiba!")
        
        print(f"❌ Folium map generation error: {error_message}")
        self.error_occurred.emit(error_message)
    
    def _on_map_loaded(self, success: bool):
        """
        🗺️ WebEngine Folium térkép betöltés befejezve.
        """
        if success:
            self.map_ready.emit()
            self.status_label.setText("🗺️ Interaktív térkép kész! Kattints a megyékre!")
            print("✅ Folium map loaded successfully in WebEngine")
        else:
            # 🔧 DETAILED ERROR DIAGNOSIS
            page = self.web_view.page()
            
            print("❌ WebEngine load failed - diagnosing...")
            print(f"🔧 DEBUG: Page URL: {page.url().toString()}")
            print(f"🔧 DEBUG: Page title: {page.title()}")
            
            # Próbáljuk meg újra betölteni 2 másodperc múlva
            self.status_label.setText("⚠️ WebEngine újrapróbálkozás 2 másodpercben...")
            QTimer.singleShot(2000, self._retry_map_loading)
            
            print("🔄 Scheduling retry in 2 seconds...")
    
    def _retry_map_loading(self):
        """
        🔄 Térkép betöltés újrapróbálása alternatív módszerrel.
        """
        if not self.current_html_path:
            self.error_occurred.emit("No HTML path available for retry")
            return
        
        print("🔄 Retrying map loading with alternative method...")
        
        try:
            # 🔧 ALTERNATÍV MÓDSZER: Egyszerű file:// URL betöltés
            file_url = QUrl.fromLocalFile(os.path.abspath(self.current_html_path))
            
            # WebEngine teljes reset
            self.web_view.stop()
            self.web_view.reload()
            
            # Egyszerű betöltés
            self.web_view.load(file_url)
            
            self.status_label.setText("🔄 Alternatív betöltési módszer...")
            print(f"🔄 Alternative loading method: {file_url.toString()}")
            
        except Exception as e:
            error_msg = f"Retry loading failed: {e}"
            print(f"❌ Retry failed: {error_msg}")
            self.error_occurred.emit(error_msg)
    
    # === UI EVENT HANDLERS ===
    
    def _on_style_changed(self, style: str):
        """
        🎨 Térkép stílus változtatása.
        """
        self.map_config.tiles = style
        print(f"🎨 Map style changed to: {style}")
    
    def _on_counties_toggled(self, checked: bool):
        """
        🗺️ Megyehatárok megjelenítés kapcsoló.
        """
        self.map_config.show_counties = checked
        print(f"🗺️ Counties display: {checked}")
    
    def _on_weather_toggled(self, checked: bool):
        """
        🌤️ Időjárási overlay kapcsoló.
        """
        self.map_config.weather_overlay = checked
        print(f"🌤️ Weather overlay: {checked}")
    
    def _on_zoom_changed(self, zoom: int):
        """
        🔍 Zoom szint változtatása.
        """
        self.map_config.zoom_start = zoom
        print(f"🔍 Zoom level: {zoom}")
    
    # === JAVASCRIPT BRIDGE HANDLERS ===
    
    def _on_js_county_clicked(self, county_name: str):
        """
        🖱️ Megye kattintás JavaScript bridge-ből.
        """
        print(f"🖱️ County clicked from JS: {county_name}")
        self.map_config.selected_county = county_name
        self.county_clicked.emit(county_name)
    
    def _on_js_coordinates_clicked(self, lat: float, lon: float):
        """
        📍 Koordináta kattintás JavaScript bridge-ből.
        """
        print(f"📍 Coordinates clicked from JS: {lat}, {lon}")
        self.coordinates_clicked.emit(lat, lon)
    
    def _on_js_map_moved(self, lat: float, lon: float, zoom: int):
        """
        🗺️ Térkép mozgás JavaScript bridge-ből.
        """
        self.map_config.center_lat = lat
        self.map_config.center_lon = lon
        self.map_config.zoom_start = zoom
        
        # UI frissítése
        self.zoom_slider.setValue(zoom)
        
        self.map_moved.emit(lat, lon, zoom)
    
    def _on_js_county_hovered(self, county_name: str):
        """
        👆 Megye hover JavaScript bridge-ből.
        """
        self.county_hovered.emit(county_name)
    
    # === AKCIÓ METÓDUSOK ===
    
    def _refresh_map(self):
        """
        🔄 Folium térkép manuális frissítése.
        """
        print("🔄 Manual Folium map refresh requested")
        self._start_map_generation()
    
    def _generate_demo_weather(self):
        """
        🧪 Demo időjárási adatok generálása és betöltése.
        """
        try:
            # Demo adatok generálása
            demo_data = self.generate_demo_weather_data()
            
            # Adatok beállítása
            self.set_weather_data(demo_data)
            
            # Weather overlay bekapcsolása
            self.weather_check.setChecked(True)
            self.map_config.weather_overlay = True
            
            # Térkép frissítése az új adatokkal
            self._start_map_generation()
            
            self.status_label.setText("🧪 Demo időjárási adatok betöltve! Weather overlay bekapcsolva.")
            
        except Exception as e:
            error_msg = f"Demo weather data generation failed: {e}"
            print(f"❌ {error_msg}")
            self.error_occurred.emit(error_msg)
    
    def _export_map(self):
        """
        💾 Folium térkép exportálása.
        """
        if not self.current_html_path:
            QMessageBox.warning(self, "Export", "Nincs Folium térkép az exportáláshoz!")
            return
        
        # Fájl mentés dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Folium térkép exportálása",
            f"hungarian_folium_map_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
            "HTML fájlok (*.html);;Minden fájl (*)"
        )
        
        if file_path:
            try:
                # HTML fájl másolása
                import shutil
                shutil.copy2(self.current_html_path, file_path)
                
                self.export_completed.emit(file_path)
                QMessageBox.information(self, "Export", f"Folium térkép sikeresen exportálva:\n{file_path}")
                
            except Exception as e:
                error_msg = f"Export hiba: {e}"
                self.error_occurred.emit(error_msg)
                QMessageBox.critical(self, "Export hiba", error_msg)
    
    # === PUBLIKUS API - FOLIUM VERZIÓ ===
    
    def set_counties_geodataframe(self, counties_gdf):
        """
        🗺️ Megyék GeoDataFrame beállítása.
        """
        self.counties_gdf = counties_gdf
        print(f"🗺️ Folium counties GeoDataFrame set: {len(counties_gdf) if counties_gdf is not None else 0} counties")
    
    def set_weather_data(self, weather_data: Dict):
        """
        🌤️ Időjárási adatok beállítása Folium overlay-hez.
        
        Expected weather_data format:
        {
            'temperature': {
                'Budapest': {
                    'coordinates': [47.4979, 19.0402],
                    'value': 22.5  # °C
                },
                ...
            },
            'precipitation': {
                'Budapest': {
                    'coordinates': [47.4979, 19.0402], 
                    'value': 15.3  # mm
                },
                ...
            },
            'wind_speed': {
                'Budapest': {
                    'coordinates': [47.4979, 19.0402],
                    'speed': 18.2,    # km/h
                    'direction': 225  # degrees
                },
                ...
            }
        }
        
        Ez a metódus VALÓS ADATOKAT fogad a weather_client.py-ból
        és az analytics engine-ből.
        """
        self.current_weather_data = weather_data
        print(f"🌤️ Real weather data set for Folium overlay:")
        
        if weather_data:
            for data_type, locations in weather_data.items():
                print(f"  📊 {data_type}: {len(locations)} locations")
        
        # Ha a weather overlay be van kapcsolva, frissítjük a térképet
        if self.map_config.weather_overlay:
            self._start_map_generation()
    
    def update_map_bounds(self, bounds: Tuple[float, float, float, float]):
        """
        🎯 Térkép határok frissítése (minx, miny, maxx, maxy).
        """
        # Térkép centrum számítása
        center_lat = (bounds[1] + bounds[3]) / 2
        center_lon = (bounds[0] + bounds[2]) / 2
        
        # Zoom szint számítása bounds alapján
        lat_diff = abs(bounds[3] - bounds[1])
        lon_diff = abs(bounds[2] - bounds[0])
        
        # Zoom szint heurisztika
        if lat_diff > 2 or lon_diff > 3:
            zoom = 6
        elif lat_diff > 1 or lon_diff > 1.5:
            zoom = 7
        elif lat_diff > 0.5 or lon_diff > 0.8:
            zoom = 8
        else:
            zoom = 9
        
        # Konfiguráció frissítése
        self.map_config.center_lat = center_lat
        self.map_config.center_lon = center_lon
        self.map_config.zoom_start = zoom
        
        # UI frissítése
        self.zoom_slider.setValue(zoom)
        
        print(f"🎯 Folium map bounds updated: center=({center_lat:.4f}, {center_lon:.4f}), zoom={zoom}")
        
        # Folium térkép újragenerálása
        self._start_map_generation()
    
    def get_map_config(self) -> FoliumMapConfig:
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
        self.map_config.zoom_start = 7
        self.map_config.selected_county = None
        self.map_config.highlighted_counties = []
        
        # UI reset
        self.zoom_slider.setValue(7)
        self.style_combo.setCurrentText("OpenStreetMap")
        
        self._start_map_generation()
        print("🏠 Folium map reset to default Hungary view")
    
    def set_map_style(self, style: str):
        """
        🎨 Térkép stílus programmatic beállítása.
        """
        if style in ["light", "bright"]:
            map_style = "CartoDB positron"
        elif style in ["dark", "night"]:
            map_style = "CartoDB dark_matter"
        else:
            map_style = "OpenStreetMap"
        
        self.style_combo.setCurrentText(map_style)
        self.map_config.tiles = map_style
        self.map_config.theme = style
        
        print(f"🎨 Folium map style set to: {map_style} (theme: {style})")
    
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
        🎯 Kiválasztott megye beállítása és térkép frissítése.
        """
        self.map_config.selected_county = county_name
        print(f"🎯 Folium map selected county: {county_name}")
        
        # Térkép frissítése a kiválasztott megyével
        self._start_map_generation()
    
    def highlight_counties(self, county_names: List[str]):
        """
        ✨ Megyék kiemelése a térképen.
        """
        self.map_config.highlighted_counties = county_names
        print(f"✨ Highlighted counties: {county_names}")
    
    def is_folium_available(self) -> bool:
        """
        ✅ Folium elérhetőség ellenőrzése.
        """
        return FOLIUM_AVAILABLE
    
    def get_javascript_bridge(self) -> JavaScriptBridge:
        """
        🌉 JavaScript bridge referencia lekérdezése.
        """
        return self.js_bridge


# === DEMO ÉS TESZT FUNKCIÓK ===

def demo_folium_map_visualizer():
    """
    🧪 Folium Map Visualizer demo alkalmazás.
    """
    import sys
    from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
    
    app = QApplication(sys.argv)
    
    # Fő ablak
    window = QMainWindow()
    window.setWindowTitle("🗺️ Folium Map Visualizer Demo - Teljes Interaktív")
    window.setGeometry(100, 100, 1400, 900)
    
    # Central widget
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    
    layout = QVBoxLayout(central_widget)
    
    # Folium map visualizer
    map_visualizer = HungarianMapVisualizer()
    layout.addWidget(map_visualizer)
    
    # Event handlers
    def on_map_ready():
        print("🗺️ Folium térkép betöltve és kész!")
    
    def on_county_clicked(county_name):
        print(f"🖱️ Megye kattintva: {county_name}")
    
    def on_coordinates_clicked(lat, lon):
        print(f"📍 Koordináta kattintva: {lat}, {lon}")
    
    def on_map_moved(lat, lon, zoom):
        print(f"🗺️ Térkép mozgott: {lat}, {lon}, zoom={zoom}")
    
    def on_export_completed(file_path):
        print(f"💾 Export befejezve: {file_path}")
    
    def on_error_occurred(message):
        print(f"❌ Hiba: {message}")
    
    # Signalok kapcsolása
    map_visualizer.map_ready.connect(on_map_ready)
    map_visualizer.county_clicked.connect(on_county_clicked)
    map_visualizer.coordinates_clicked.connect(on_coordinates_clicked)
    map_visualizer.map_moved.connect(on_map_moved)
    map_visualizer.export_completed.connect(on_export_completed)
    map_visualizer.error_occurred.connect(on_error_occurred)
    
    window.show()
    
    print("🗺️ Folium Map Visualizer Demo elindítva!")
    print("✅ TELJES INTERAKTÍV FOLIUM TÉRKÉP!")
    print("🎮 Elérhető funkciók:")
    print("   🖱️ Kattintható megyék")
    print("   📍 Koordináta kattintás")
    print("   🔍 Zoom/Pan interakció")
    print("   👆 Hover tooltipek")
    print("   🌤️ Weather overlay")
    print("   🎨 Téma támogatás")
    print("   💾 HTML export")
    print("   🌉 JavaScript ↔ Python bridge")
    
    if FOLIUM_AVAILABLE:
        print("✅ Folium library elérhető!")
    else:
        print("❌ Folium library hiányzik - telepítsd: pip install folium branca")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    demo_folium_map_visualizer()