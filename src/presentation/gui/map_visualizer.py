#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🗺️ Magyar Folium Térkép Vizualizáló - HELYI HTTP SZERVER VERZIÒ v3.0
Magyar Klímaanalitika MVP - Folium + Leaflet.js Alapú Térképes Megjelenítő

🚀 HELYI HTTP SZERVER MEGOLDÁS v3.0:
- Beágyazott HTTP szerver QThread-ben
- WebEngine http://127.0.0.1:PORT/map.html betöltés
- Same-Origin Policy problémák végleg megoldva
- Nagy HTML fájlok (1.5MB+) támogatása
- Folium teljes funkcionalitás
- Stabil és megbízható működés

🔧 KRITIKUS JAVÍTÁS:
- setHtml() méretkorlát megoldva
- file:// protokoll problémák megszűntek
- JavaScript és CSS teljes támogatás
- Nincs WebEngine cache konfliktus

FÁJL: src/gui/map_visualizer.py
"""

from typing import Dict, List, Optional, Tuple, Any
import os
import json
import tempfile
import socketserver
import http.server
from dataclasses import dataclass, field
from datetime import datetime
import uuid

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QComboBox, QSlider, QCheckBox, QGroupBox, QProgressBar,
    QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QUrl, QThread
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebChannel import QWebChannel

# Folium import with fallback
try:
    import folium
    from folium import plugins
    FOLIUM_AVAILABLE = True
    print("✅ Folium successfully imported")
except ImportError as e:
    FOLIUM_AVAILABLE = False
    print(f"⚠️ Folium not available: {e}")

# GeoPandas import
try:
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
    
    # 🔧 Active overlay parameter
    active_overlay_parameter: Optional[str] = None  # "temperature", "wind_speed", "precipitation"
    
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


class LocalHttpServerThread(QThread):
    """
    🌐 Helyi HTTP szerver QThread-ben a Folium térképek kiszolgálásához.
    
    Ez a szerver megoldja a WebEngine Same-Origin Policy problémáit
    és támogatja a nagy HTML fájlokat (1.5MB+).
    """
    
    # Signalok
    server_ready = Signal(str, int)  # host, port
    server_error = Signal(str)       # error message
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.server = None
        self.httpd = None
        self.temp_dir = tempfile.gettempdir()
        self.host = "127.0.0.1"
        self.port = 0  # 0 = automatikus szabad port keresés
        self.running = False
        
    def run(self):
        """
        🚀 HTTP szerver indítása háttérben.
        """
        try:
            # Munkamappa beállítása
            os.chdir(self.temp_dir)
            
            # HTTP kérés handler
            class QuietHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
                def log_message(self, format, *args):
                    # Csendes mód - nincs console spam
                    pass
            
            # HTTP szerver létrehozása
            with socketserver.TCPServer((self.host, self.port), QuietHTTPRequestHandler) as httpd:
                self.httpd = httpd
                self.port = httpd.server_address[1]  # Valós port megszerzése
                self.running = True
                
                print(f"🌐 Local HTTP Server started: http://{self.host}:{self.port}")
                
                # Szerver kész jelzés
                self.server_ready.emit(self.host, self.port)
                
                # Szerver futtatása
                httpd.serve_forever()
                
        except Exception as e:
            error_msg = f"HTTP Server error: {e}"
            print(f"❌ {error_msg}")
            self.server_error.emit(error_msg)
    
    def stop(self):
        """
        🛑 HTTP szerver leállítása.
        """
        if self.httpd:
            self.httpd.shutdown()
            self.running = False
            print("🛑 Local HTTP Server stopped")


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
    📄 Háttér worker a Folium interaktív térkép generálásához - HTTP SZERVER VERZIÓ.
    
    🔧 KRITIKUS VÁLTOZÁS v3.0:
    - Visszatér a fájlmentéshez
    - HTTP szerver kiszolgálja a fájlokat
    - Nagy HTML fájlok (1.5MB+) támogatása
    - Same-Origin Policy problémák végleg megoldva
    """
    
    # Signalok
    progress_updated = Signal(int)         # progress (0-100)
    map_generated = Signal(str)           # HTML FILE PATH (nem content!)
    error_occurred = Signal(str)          # error message
    status_updated = Signal(str)          # status message
    
    def __init__(self, config: FoliumMapConfig, counties_gdf=None, weather_data=None, bridge_id=None, output_path=None):
        super().__init__()
        self.config = config
        self.counties_gdf = counties_gdf
        self.weather_data = weather_data
        self.bridge_id = bridge_id or str(uuid.uuid4())
        
        # Output path generálás
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            self.output_path = os.path.join(tempfile.gettempdir(), f"hungarian_folium_map_{timestamp}.html")
        else:
            self.output_path = output_path
    
    def run(self):
        """
        🗺️ Folium interaktív térkép generálása - HTTP SZERVER VERZIÓ.
        """
        try:
            self._generate_map_content()
        except Exception as e:
            import traceback
            error_msg = f"Folium térkép generálási hiba: {e}\n{traceback.format_exc()}"
            self.error_occurred.emit(error_msg)

    def _generate_map_content(self) -> None:
        """Fő lépések szétbontva az átláthatóságért."""
        if not FOLIUM_AVAILABLE:
            raise ImportError("Folium library not available")
        
        self.status_updated.emit("🗺️ Folium térkép inicializálása...")
        self.progress_updated.emit(5)
        
        map_obj = self._create_base_folium_map()
        self.progress_updated.emit(20)
        
        self._maybe_add_counties(map_obj)
        self.progress_updated.emit(50)
        
        self._maybe_add_weather_overlay(map_obj)
        self.progress_updated.emit(70)
        
        self.status_updated.emit("🌉 JavaScript interaktivitás...")
        self._add_javascript_bridge(map_obj)
        self.progress_updated.emit(85)
        
        self._add_map_controls(map_obj)
        self.progress_updated.emit(90)
        
        self._save_and_validate_map(map_obj)
        self.progress_updated.emit(100)
        self.status_updated.emit("✅ Folium térkép HTTP szerver verzió elkészült!")
        
        print(f"✅ HTTP Server Folium map generated: {self.output_path} ({os.path.getsize(self.output_path):,} bytes)")
        self.map_generated.emit(self.output_path)

    def _maybe_add_counties(self, map_obj: folium.Map) -> None:
        if self.config.show_counties and self.counties_gdf is not None:
            self.status_updated.emit("🗺️ Megyehatárok hozzáadása...")
            self._add_counties_layer(map_obj)

    def _maybe_add_weather_overlay(self, map_obj: folium.Map) -> None:
        if self.config.weather_overlay and self.weather_data:
            self.status_updated.emit("🌤️ Időjárási overlay...")
            self._add_weather_overlay(map_obj)

    def _save_and_validate_map(self, map_obj: folium.Map) -> None:
        self.status_updated.emit("💾 HTML fájl mentése...")
        map_obj.save(self.output_path)
        if not os.path.exists(self.output_path):
            raise FileNotFoundError(f"Generated HTML file not found: {self.output_path}")
        file_size = os.path.getsize(self.output_path)
        if file_size < 1000:
            raise ValueError(f"Generated HTML file too small: {file_size} bytes")

        try:
            host_msg = f"http://{self.config.center_lat}:{self.config.center_lon}"
            _ = host_msg  # placeholder to keep previous side-effects minimal
        except Exception:
            # No previous behavior depended on this; keep silent
            pass

    
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
            print(f"⚠️ Weather overlay error: {e}")
    
    def _add_temperature_heatmap(self, map_obj: folium.Map):
        """
        🌡️ Hőmérséklet heatmap hozzáadása DINAMIKUS SZÍNSKÁLÁVAL.
        """
        try:
            from folium.plugins import HeatMap
            temp_data = self._build_temperature_heatmap_points()
            if not temp_data:
                return

            gradient = self._get_dynamic_gradient('RdYlBu_r', 'temperature')
            heat_map = HeatMap(
                temp_data,
                name="🌡️ Hőmérséklet",
                min_opacity=0.3,
                max_zoom=18,
                radius=25,
                blur=15,
                gradient=gradient
            )
            heat_map.add_to(map_obj)
            print(f"🌡️ Temperature heatmap added with {len(temp_data)} points (dynamic gradient)")
            
        except ImportError:
            print("⚠️ HeatMap plugin not available")
        except Exception as e:
            print(f"⚠️ Temperature heatmap error: {e}")

    def _build_temperature_heatmap_points(self) -> List[List[float]]:
        """Heatmap pontok összeállítása normalizált intenzitással."""
        temp_data: List[List[float]] = []
        for _, data in self.weather_data.get('temperature', {}).items():
            if 'coordinates' not in data or 'value' not in data:
                continue
            lat, lon = data['coordinates']
            temp = data['value']
            intensity = max(0.1, min(1.0, (temp + 20) / 60))
            temp_data.append([lat, lon, intensity])
        return temp_data
    
    def _get_dynamic_gradient(self, color_scale: str, overlay_type: str) -> Dict[float, str]:
        """
        🔧 KRITIKUS ÚJ METÓDUS: Dinamikus gradient generálás color_scale alapján
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
            'Oranges': {  # Széllökések - Világos narancs → Sötét narancs/piros
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
            print(f"⚠️ Ismeretlen color_scale és overlay_type: {color_scale}, {overlay_type}")
            return COLOR_SCALE_GRADIENTS['RdYlBu_r']  # Default hőmérséklet
            
        except Exception as e:
            print(f"⚠️ Gradient generálási hiba: {e}")
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
            print(f"⚠️ Precipitation overlay error: {e}")
    
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
            print(f"⚠️ Wind speed overlay error: {e}")
    
    def _add_weather_legend(self, map_obj: folium.Map):
        """
        📊 Weather overlay legend hozzáadása DINAMIKUS OVERLAY PARAMETER alapján.
        """
        try:
            # 🔧 JAVÍTOTT: Active overlay parameter alapú legend
            active_parameter = self.config.active_overlay_parameter
            
            if active_parameter == 'temperature':
                legend_html = self._create_temperature_legend()
            elif active_parameter == 'wind_speed':
                legend_html = self._create_wind_legend()
            elif active_parameter == 'precipitation':
                legend_html = self._create_precipitation_legend()
            else:
                # Fallback: általános legend
                legend_html = self._create_general_legend()
            
            # Legend hozzáadása a térképhez
            map_obj.get_root().html.add_child(folium.Element(legend_html))
            
            print(f"📊 Weather legend added for parameter: {active_parameter}")
            
        except Exception as e:
            print(f"⚠️ Weather legend error: {e}")
    
    def _create_temperature_legend(self) -> str:
        """🌡️ Hőmérséklet specifikus legend HTML."""
        return '''
        <div style="position: fixed; 
                    top: 80px; right: 20px; width: 200px; height: auto; 
                    background-color: rgba(255, 255, 255, 0.9);
                    border: 2px solid grey; z-index:9999; 
                    font-size: 12px; padding: 10px;
                    border-radius: 5px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                    ">
        <h4 style="margin-top: 0; color: #2E4057;">🌡️ Hőmérséklet</h4>
        
        <div style="background: linear-gradient(to right, #0000FF, #00FFFF, #00FF00, #FFFF00, #FF8000, #FF0000); 
                    height: 15px; margin: 5px 0;"></div>
        <div style="display: flex; justify-content: space-between; font-size: 10px;">
            <span>-20°C</span><span>+40°C</span>
        </div>
        
        <p style="margin-top: 10px; font-size: 10px;">
            <b>Színskála:</b> Kék (hideg) → Piros (meleg)<br>
            <b>Adatok:</b> Napi maximum hőmérséklet
        </p>
        </div>
        '''
    
    def _create_wind_legend(self) -> str:
        """💨 Szél specifikus legend HTML."""
        return '''
        <div style="position: fixed; 
                    top: 80px; right: 20px; width: 200px; height: auto; 
                    background-color: rgba(255, 255, 255, 0.9);
                    border: 2px solid grey; z-index:9999; 
                    font-size: 12px; padding: 10px;
                    border-radius: 5px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                    ">
        <h4 style="margin-top: 0; color: #2E4057;">💨 Szélsebesség</h4>
        
        <div style="background: linear-gradient(to right, #F0FFF0, #90EE90, #32CD32, #228B22, #006400); 
                    height: 15px; margin: 5px 0;"></div>
        <div style="display: flex; justify-content: space-between; font-size: 10px;">
            <span>0 km/h</span><span>60+ km/h</span>
        </div>
        
        <p style="margin-top: 10px; font-size: 10px;">
            <div>🟢 < 12 km/h - Enyhe szél</div>
            <div>🟡 12-20 km/h - Gyenge szél</div>
            <div>🟠 20-39 km/h - Mérsékelt szél</div>
            <div>🔴 > 50 km/h - Erős szél</div>
        </p>
        </div>
        '''
    
    def _create_precipitation_legend(self) -> str:
        """🌧️ Csapadék specifikus legend HTML."""
        return '''
        <div style="position: fixed; 
                    top: 80px; right: 20px; width: 200px; height: auto; 
                    background-color: rgba(255, 255, 255, 0.9);
                    border: 2px solid grey; z-index:9999; 
                    font-size: 12px; padding: 10px;
                    border-radius: 5px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                    ">
        <h4 style="margin-top: 0; color: #2E4057;">🌧️ Csapadék</h4>
        
        <div style="background: linear-gradient(to right, #F0F8FF, #B3D9FF, #4D94FF, #0066CC, #003366); 
                    height: 15px; margin: 5px 0;"></div>
        <div style="display: flex; justify-content: space-between; font-size: 10px;">
            <span>0 mm</span><span>50+ mm</span>
        </div>
        
        <p style="margin-top: 10px; font-size: 10px;">
            <div style="display: flex; align-items: center; margin: 5px 0;">
                <div style="width: 10px; height: 10px; background: #E8F4FD; border-radius: 50%; margin-right: 5px;"></div>
                <span>< 1 mm</span>
            </div>
            <div style="display: flex; align-items: center; margin: 5px 0;">
                <div style="width: 15px; height: 15px; background: #80D0FF; border-radius: 50%; margin-right: 5px;"></div>
                <span>5-10 mm</span>
            </div>
            <div style="display: flex; align-items: center; margin: 5px 0;">
                <div style="width: 20px; height: 20px; background: #0080FF; border-radius: 50%; margin-right: 5px;"></div>
                <span>> 25 mm</span>
            </div>
        </p>
        </div>
        '''
    
    def _create_general_legend(self) -> str:
        """🌤️ Általános weather legend HTML."""
        return '''
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
            
            // Map click esemény figyelése
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
            console.log('🔥 Loading QWebChannel script...');
            var script = document.createElement('script');
            script.src = 'qrc:///qtwebchannel/qwebchannel.js';
            script.onload = function() {{
                console.log('✅ QWebChannel script loaded');
                initializeQtBridge();
            }};
            script.onerror = function() {{
                console.log('⚠️ Failed to load QWebChannel script');
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


class HungarianMapVisualizer(QWidget):
    """
    🗺️ Magyar Folium térkép vizualizáló widget - HELYI HTTP SZERVER VERZIÓ v3.0
    
    🔧 HELYI HTTP SZERVER MEGOLDÁS v3.0:
    - Beágyazott HTTP szerver QThread-ben
    - WebEngine http://127.0.0.1:PORT/map.html betöltés
    - Same-Origin Policy problémák végleg megoldva
    - Nagy HTML fájlok (1.5MB+) támogatása
    - Folium teljes funkcionalitás
    - Stabil és megbízható működés
    
    🚀 REAKTÍV MEGYEHATÁROK v3.0:
    - set_counties_geodataframe() AZONNALI térképfrissítést indít
    - set_weather_data() AZONNALI térképfrissítést indít  
    - A "futár és festő" probléma megoldva
    - Magyar megyék automatikusan megjelennek betöltés után
    - Nincs manuális frissítés szükséges
    
    🔧 DINAMIKUS SZÍNSKÁLA v1.2:
    - COLOR_SCALE_GRADIENTS mapping minden overlay típushoz
    - set_active_overlay_parameter() metódus
    - Overlay-specifikus jelmagyarázat generálás
    
    FUNKCIÓK:
    - Folium + Leaflet.js alapú interaktív térkép
    - Kattintható magyar megyék
    - Hover tooltipek és popupok
    - Weather overlay support (DINAMIKUS SZÍNSKÁLÁVAL)
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
        
        # 🔧 HTTP SZERVER VERZIÓ: Szerver objektumok
        self.local_server = None
        self.http_host = None
        self.http_port = None
        self.current_map_file = None
        
        # Worker threads
        self.map_generator = None
        
        # JavaScript Bridge
        self.js_bridge = JavaScriptBridge()
        self.web_channel = QWebChannel()
        
        # UI építés
        self._setup_ui()
        self._setup_theme()
        self._connect_signals()
        
        # HTTP szerver indítása
        self._start_local_server()
        
        # Folium elérhető ellenőrzése
        if FOLIUM_AVAILABLE:
            # Várunk a szervertől majd generálunk alapértelmezett térképet
            pass
        else:
            self._show_folium_error()
    
    def _setup_ui(self):
        """
        🎨 UI komponensek létrehozása - HTTP SZERVER VERZIÓ.
        """
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # === FOLIUM TÉRKÉP VEZÉRLŐK ===
        
        controls_group = QGroupBox("🌐 HTTP Szerver Folium Térkép v3.0 + 🔧 Same-Origin Policy Fix + Reaktív Megyehatárok + Dinamikus Színskála")
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
        
        # 🔧 ÚJ: Active overlay parameter kijelző
        self.overlay_parameter_label = QLabel("🎨 Overlay: Nincs")
        overlay_param_font = self.overlay_parameter_label.font()
        overlay_param_font.setPointSize(9)
        self.overlay_parameter_label.setFont(overlay_param_font)
        self.overlay_parameter_label.setStyleSheet("color: #9B59B6; font-weight: bold;")
        register_widget_for_theming(self.overlay_parameter_label, "text")
        controls_layout.addWidget(self.overlay_parameter_label)
        
        # HTTP szerver status
        self.server_status_label = QLabel("🌐 Szerver: Indítás...")
        server_font = self.server_status_label.font()
        server_font.setPointSize(9)
        self.server_status_label.setFont(server_font)
        self.server_status_label.setStyleSheet("color: #3498DB; font-weight: bold;")
        register_widget_for_theming(self.server_status_label, "text")
        controls_layout.addWidget(self.server_status_label)
        
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
        
        self.status_label = QLabel("🌐 HTTP szerver Folium térkép + Same-Origin Policy fix + Reaktív megyehatárok inicializálása...")
        register_widget_for_theming(self.status_label, "text")
        layout.addWidget(self.status_label)
        
        # === WEBENGINE VIEW + JAVASCRIPT BRIDGE ===
        
        self.web_view = QWebEngineView()
        register_widget_for_theming(self.web_view, "container")
        
        # 🔧 WEBENGINE SETTINGS - HTTP szerver optimalizált beállítások
        try:
            from PySide6.QtWebEngineCore import QWebEngineSettings
            
            settings = self.web_view.settings()
            # JavaScript engedélyezés
            settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
            settings.setAttribute(QWebEngineSettings.ErrorPageEnabled, True)
            # WebGL és Canvas engedélyezés
            settings.setAttribute(QWebEngineSettings.WebGLEnabled, True)
            settings.setAttribute(QWebEngineSettings.Accelerated2dCanvasEnabled, True)
            # Local content optimalizáció
            settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
            # HTTP cache
            settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
            
            print("✅ WebEngine settings configured for HTTP server content")
            
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
        🔗 Signal-slot kapcsolatok létrehozása - HTTP SZERVER VERZIÓ.
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
        
        print("✅ HTTP Server MapVisualizer signals connected")
    
    def _start_local_server(self):
        """
        🌐 Helyi HTTP szerver indítása.
        """
        if self.local_server and self.local_server.running:
            print("⚠️ Local server already running")
            return
        
        print("🌐 Starting local HTTP server...")
        
        # LocalHttpServerThread létrehozása
        self.local_server = LocalHttpServerThread(self)
        
        # Szerver signalok bekötése
        self.local_server.server_ready.connect(self._on_server_ready)
        self.local_server.server_error.connect(self._on_server_error)
        
        # Szerver indítása
        self.local_server.start()
    
    def _on_server_ready(self, host: str, port: int):
        """
        ✅ HTTP szerver kész és elérhető.
        """
        self.http_host = host
        self.http_port = port
        
        print(f"✅ Local HTTP server ready: http://{host}:{port}")
        
        # UI frissítése
        self.server_status_label.setText(f"🌐 Szerver: http://{host}:{port}")
        self.server_status_label.setStyleSheet("color: #27AE60; font-weight: bold;")
        
        # Alapértelmezett térkép generálása a szerver elindulása után
        if FOLIUM_AVAILABLE:
            self._generate_default_map()
    
    def _on_server_error(self, error_message: str):
        """
        ❌ HTTP szerver hiba.
        """
        print(f"❌ Local HTTP server error: {error_message}")
        
        # UI frissítése
        self.server_status_label.setText("🌐 Szerver: HIBA")
        self.server_status_label.setStyleSheet("color: #E74C3C; font-weight: bold;")
        
        # Hiba jelzés
        self.error_occurred.emit(f"HTTP szerver hiba: {error_message}")
    
    def _show_folium_error(self):
        """
        ⚠️ Folium hiány esetén hibaüzenet megjelenítése.
        """
        self.status_label.setText("⚠️ Folium library hiányzik! pip install folium")
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
        
        if not self.http_host or not self.http_port:
            print("⚠️ HTTP server not ready for map generation")
            return
        
        self._start_map_generation()
    
    def _start_map_generation(self):
        """
        🔄 Folium térkép generálás indítása háttérben - HTTP SZERVER VERZIÓ.
        """
        if not self._can_generate_map():
            return
        if self.map_generator and self.map_generator.isRunning():
            return  # Már fut egy generálás
        
        self._prepare_progress_bar()
        self._create_and_start_map_generator()

    def _can_generate_map(self) -> bool:
        if not FOLIUM_AVAILABLE:
            self._show_folium_error()
            return False
        if not self.http_host or not self.http_port:
            print("⚠️ HTTP server not ready for map generation")
            return False
        return True

    def _prepare_progress_bar(self) -> None:
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("🌐 HTTP szerver Folium térkép + Same-Origin Policy fix + Reaktív megyehatárok generálása...")

    def _create_and_start_map_generator(self) -> None:
        self.map_generator = FoliumMapGenerator(
            config=self.map_config,
            counties_gdf=self.counties_gdf,
            weather_data=self.current_weather_data,
            bridge_id=self.js_bridge.bridge_id
        )
        self.map_generator.progress_updated.connect(self.progress_bar.setValue)
        self.map_generator.status_updated.connect(self.status_label.setText)
        self.map_generator.map_generated.connect(self._on_map_generated)
        self.map_generator.error_occurred.connect(self._on_map_error)
        self.map_generator.start()
    
    def _on_map_generated(self, file_path: str):
        """
        ✅ Folium térkép generálás befejezve - HTTP SZERVER VERZIÓ.
        
        Args:
            file_path: Generált HTML fájl teljes elérési útja
        """
        print(f"🌐 DEBUG: HTTP Server map generated - {file_path}")
        
        # Fájl elérési út tárolása
        self.current_map_file = file_path
        
        # Fájl létezés ellenőrzése
        if not os.path.exists(file_path):
            error_msg = f"Generated HTML file not found: {file_path}"
            self.error_occurred.emit(error_msg)
            return
        
        # Fájl méret ellenőrzése
        file_size = os.path.getsize(file_path)
        if file_size < 1000:
            error_msg = f"Generated HTML file too small: {file_size} bytes"
            self.error_occurred.emit(error_msg)
            return
        
        print(f"✅ Valid HTML file generated - Size: {file_size:,} bytes")
        
        # 🌐 HTTP URL GENERÁLÁS ÉS BETÖLTÉS
        self._load_map_from_http_url(file_path)
        
        self.progress_bar.setVisible(False)
        self.status_label.setText("🌐 HTTP szerver térkép betöltése...")
        
        print(f"✅ HTTP Server Folium map loading initiated")
    
    def _load_map_from_http_url(self, file_path: str):
        """
        🌐 KRITIKUS ÚJ METÓDUS: Térkép betöltése HTTP URL-ről.
        
        Ez a metódus generálja a http://127.0.0.1:PORT/filename.html URL-t
        és betölti a WebEngine-be.
        
        Args:
            file_path: Generált HTML fájl teljes elérési útja
        """
        try:
            print("🌐 DEBUG: Starting HTTP URL loading...")
            
            # Fájlnév kinyerése az elérési útból
            filename = os.path.basename(file_path)
            
            # HTTP URL összeállítása
            http_url = f"http://{self.http_host}:{self.http_port}/{filename}"
            
            print(f"🌐 DEBUG: Loading map from HTTP URL: {http_url}")
            
            # WebEngine reset és cache clear
            self.web_view.stop()
            
            # HTTP URL betöltése WebEngine-be
            self.web_view.load(QUrl(http_url))
            
            print(f"✅ HTTP URL loading initiated: {http_url}")
            
            # Status update
            self.status_label.setText(f"🌐 HTTP térkép betöltve: {filename}")
            
        except Exception as e:
            error_msg = f"HTTP URL betöltési hiba: {e}"
            print(f"❌ HTTP URL Loading Error: {error_msg}")
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
        🗺️ WebEngine Folium térkép betöltés befejezve - HTTP SZERVER VERZIÓ + REAKTÍV MEGYEHATÁROK.
        """
        if success:
            self.map_ready.emit()
            counties_info = f" ({len(self.counties_gdf)} megye)" if self.counties_gdf is not None else ""
            self.status_label.setText(f"🌐 HTTP szerver interaktív térkép kész!{counties_info} Kattints a megyékre!")
            print("✅ HTTP Server Folium map with reactive counties loaded successfully in WebEngine")
        else:
            error_msg = "WebEngine HTTP loading failed"
            self.error_occurred.emit(error_msg)
            self.status_label.setText("❌ WebEngine HTTP betöltés sikertelen!")
            print(f"❌ WebEngine HTTP loading failed")
    
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
    
    def _export_map(self):
        """
        💾 Folium térkép exportálása - HTTP SZERVER VERZIÓ.
        """
        if not self.current_map_file or not os.path.exists(self.current_map_file):
            QMessageBox.warning(self, "Export", "Nincs Folium térkép az exportáláshoz!")
            return
        
        # Fájl mentés dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "HTTP szerver Folium térkép exportálása",
            f"hungarian_folium_map_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
            "HTML fájlok (*.html);;Minden fájl (*)"
        )
        
        if file_path:
            try:
                # HTML fájl másolása
                import shutil
                shutil.copy2(self.current_map_file, file_path)
                
                self.export_completed.emit(file_path)
                QMessageBox.information(self, "Export", f"HTTP szerver Folium térkép sikeresen exportálva:\n{file_path}")
                
                print(f"✅ HTTP server map exported: {file_path}")
                
            except Exception as e:
                error_msg = f"Export hiba: {e}"
                self.error_occurred.emit(error_msg)
                QMessageBox.critical(self, "Export hiba", error_msg)
    
    # === 🔧 ÚJ METÓDUSOK - DINAMIKUS SZÍNSKÁLA TÁMOGATÁS ===
    
    def set_active_overlay_parameter(self, parameter: str):
        """
        🔧 KRITIKUS ÚJ METÓDUS: Active overlay parameter beállítása
        
        Args:
            parameter: Overlay parameter ("temperature", "wind_speed", "precipitation", stb.)
        """
        print(f"🎨 DEBUG: Setting active overlay parameter: {parameter}")
        
        # Config frissítése
        self.map_config.active_overlay_parameter = parameter
        
        # UI frissítése
        parameter_display_names = {
            "temperature": "🌡️ Hőmérséklet",
            "wind_speed": "💨 Szélsebesség",
            "precipitation": "🌧️ Csapadék",
            "wind_gusts": "🌪️ Széllökések",
            "humidity": "💧 Páratartalom"
        }
        
        display_name = parameter_display_names.get(parameter, f"🎨 {parameter}")
        self.overlay_parameter_label.setText(f"🎨 Overlay: {display_name}")
        
        print(f"✅ DEBUG: Active overlay parameter set: {parameter} → {display_name}")
    
    def clear_active_overlay_parameter(self):
        """
        🧹 Active overlay parameter törlése.
        """
        print("🧹 DEBUG: Clearing active overlay parameter")
        
        self.map_config.active_overlay_parameter = None
        self.overlay_parameter_label.setText("🎨 Overlay: Nincs")
        self.overlay_parameter_label.setStyleSheet("color: #95A5A6;")
    
    def get_active_overlay_parameter(self) -> Optional[str]:
        """
        📍 Jelenlegi active overlay parameter lekérdezése.
        
        Returns:
            Active overlay parameter vagy None
        """
        return self.map_config.active_overlay_parameter
    
    # === 🚀 REAKTÍV PUBLIKUS API - HTTP SZERVER VERZIÓ + DINAMIKUS SZÍNSKÁLA ===
    
    def set_counties_geodataframe(self, counties_gdf):
        """
        🗺️ 🚀 REAKTÍV JAVÍTÁS: Megyék GeoDataFrame beállítása és a térkép AZONNALI frissítése.
        
        🔧 KRITIKUS VÁLTOZÁS v3.0:
        Ez a metódus most REAKTÍV! Amint megkapja az új megyeadatokat,
        azonnal elindít egy új térképgenerálási folyamatot.
        
        Megoldja a "futár és festő" problémát:
        - A "futár" (MainWindow) átadja az adatokat
        - A "festő" (HungarianMapVisualizer) AZONNAL újrafesti a térképet
        
        Args:
            counties_gdf: Magyar megyék GeoDataFrame
        """
        print(f"🗺️ 🚀 REAKTÍV: Counties GeoDataFrame set: {len(counties_gdf) if counties_gdf is not None else 0} counties")
        
        # Adatok tárolása
        self.counties_gdf = counties_gdf
        
        # 🚀 KRITIKUS JAVÍTÁS: AZONNALI TÉRKÉPFRISSÍTÉS!
        # A "futár és festő" probléma megoldása
        if counties_gdf is not None and len(counties_gdf) > 0:
            print("🔄 🚀 REAKTÍV: County data received, triggering IMMEDIATE map refresh...")
            print(f"📍 Counties columns: {list(counties_gdf.columns) if hasattr(counties_gdf, 'columns') else 'No columns'}")
            
            # Térképkonfiguráció automatikus beállítása
            self.map_config.show_counties = True
            self.counties_check.setChecked(True)
            
            # AZONNALI térképgenerálás indítása az új adatokkal
            self._start_map_generation()
            
            print("✅ 🚀 REAKTÍV: Map refresh triggered automatically after county data received")
        else:
            print("⚠️ Empty or None counties data received - no map refresh triggered")
    
    def set_weather_data(self, weather_data: Dict):
        """
        🌤️ 🚀 REAKTÍV JAVÍTÁS: Időjárási adatok beállítása Folium overlay-hez DINAMIKUS SZÍNSKÁLÁVAL + AZONNALI FRISSÍTÉS - HTTP SZERVER VERZIÓ.
        
        🔧 KRITIKUS VÁLTOZÁS v3.0:
        Ez a metódus most REAKTÍV! Amint megkapja az új időjárási adatokat,
        azonnal elindít egy új térképgenerálási folyamatot.
        
        Ez a metódus VALÓS ADATOKAT fogad a weather_client.py-ból
        és az analytics engine-ből.
        
        Args:
            weather_data: Időjárási adatok dictionary
        """
        print(f"🌤️ 🚀 REAKTÍV: Real weather data set for HTTP server Folium overlay with dynamic gradients:")
        
        # Adatok tárolása
        self.current_weather_data = weather_data
        
        if weather_data:
            for data_type, locations in weather_data.items():
                print(f"  📊 {data_type}: {len(locations)} locations")
                
                # 🔧 AUTOMATIKUS OVERLAY PARAMETER BEÁLLÍTÁS
                if data_type in ['temperature', 'wind_speed', 'precipitation', 'wind_gusts']:
                    self.set_active_overlay_parameter(data_type)
                    print(f"  🎨 Auto-set active overlay parameter: {data_type}")
            
            # 🚀 KRITIKUS JAVÍTÁS: AZONNALI TÉRKÉPFRISSÍTÉS!
            # Weather overlay automatikus bekapcsolása
            self.map_config.weather_overlay = True
            self.weather_check.setChecked(True)
            
            print("🔄 🚀 REAKTÍV: Weather data received, triggering IMMEDIATE map refresh...")
            
            # AZONNALI térképgenerálás indítása az új időjárási adatokkal
            self._start_map_generation()
            
            print("✅ 🚀 REAKTÍV: Map refresh triggered automatically after weather data received")
        else:
            print("⚠️ Empty weather data received - no map refresh triggered")
    
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
        
        print(f"🎯 HTTP server map bounds updated: center=({center_lat:.4f}, {center_lon:.4f}), zoom={zoom}")
        
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
        
        # 🔧 Active overlay parameter reset
        self.clear_active_overlay_parameter()
        
        # UI reset
        self.zoom_slider.setValue(7)
        self.style_combo.setCurrentText("OpenStreetMap")
        
        self._start_map_generation()
        print("🏠 HTTP server map reset to default Hungary view")
    
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
        
        print(f"🎨 HTTP server map style set to: {map_style} (theme: {style})")
    
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
        print(f"🎯 HTTP server map selected county: {county_name}")
        
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
    
    def get_http_server_info(self) -> Dict[str, Any]:
        """
        🌐 HTTP szerver információk lekérdezése.
        
        Returns:
            HTTP szerver információk dictionary
        """
        return {
            "server_running": self.local_server is not None and self.local_server.running,
            "http_host": self.http_host,
            "http_port": self.http_port,
            "server_url": f"http://{self.http_host}:{self.http_port}" if self.http_host and self.http_port else None,
            "current_map_file": self.current_map_file,
            "current_map_size": os.path.getsize(self.current_map_file) if self.current_map_file and os.path.exists(self.current_map_file) else 0,
            "version": "v3.0"
        }
    
    def generate_demo_weather_data(self) -> Dict[str, Any]:
        """
        🧪 Demo időjárási adatok generálása teszteléshez.
        """
        import random
        
        # Magyar városok demo adatok
        cities = [
            {"name": "Budapest", "coordinates": [47.4979, 19.0402]},
            {"name": "Debrecen", "coordinates": [47.5316, 21.6273]},
            {"name": "Szeged", "coordinates": [46.2530, 20.1414]},
            {"name": "Miskolc", "coordinates": [48.1034, 20.7784]},
            {"name": "Pécs", "coordinates": [46.0727, 18.2329]},
            {"name": "Győr", "coordinates": [47.6874, 17.6504]},
            {"name": "Nyíregyháza", "coordinates": [47.9562, 21.7201]},
            {"name": "Kecskemét", "coordinates": [46.9061, 19.6938]},
            {"name": "Székesfehérvár", "coordinates": [47.1884, 18.4241]},
            {"name": "Szombathely", "coordinates": [47.2309, 16.6218]}
        ]
        
        demo_data = {
            'temperature': {},
            'precipitation': {},
            'wind_speed': {}
        }
        
        for city in cities:
            # Hőmérséklet
            demo_data['temperature'][city['name']] = {
                'coordinates': city['coordinates'],
                'value': random.uniform(-5, 35)  # nosec B311 - demo/preview adat
            }
            
            # Csapadék
            demo_data['precipitation'][city['name']] = {
                'coordinates': city['coordinates'],
                'value': random.uniform(0, 25)  # nosec B311 - demo/preview adat
            }
            
            # Szélsebesség
            demo_data['wind_speed'][city['name']] = {
                'coordinates': city['coordinates'],
                'speed': random.uniform(5, 45),  # nosec B311 - demo/preview adat
                'direction': random.randint(0, 360)  # nosec B311 - demo/preview adat
            }
        
        print(f"🧪 Demo weather data generated: {len(cities)} cities")
        return demo_data
    
    def get_dynamic_gradient_info(self) -> Dict[str, Any]:
        """
        🔧 Dinamikus gradient információk lekérdezése debugging célokra.
        
        Returns:
            Gradient információk dictionary
        """
        return {
            "active_overlay_parameter": self.get_active_overlay_parameter(),
            "available_gradients": ["RdYlBu_r", "Blues", "Greens", "Oranges"],
            "gradient_mapping": {
                "temperature": "RdYlBu_r",
                "precipitation": "Blues",
                "wind_speed": "Greens", 
                "wind_gusts": "Oranges"
            },
            "dynamic_gradient_support": True,
            "http_server_version": True,
            "same_origin_policy_fixed": True,
            "reactive_counties": True,
            "reactive_weather": True,
            "large_html_support": True,
            "version": "v3.0"
        }
    
    def get_current_map_file(self) -> Optional[str]:
        """
        📄 Jelenlegi térkép fájl elérési útja - HTTP SZERVER VERZIÓ.
        
        Returns:
            Jelenleg betöltött térkép fájl elérési útja vagy None
        """
        return self.current_map_file
    
    def get_http_debug_info(self) -> Dict[str, Any]:
        """
        🌐 HTTP szerver verzió debug információk.
        
        Returns:
            HTTP szerver debug információk
        """
        server_info = self.get_http_server_info()
        
        return {
            "http_server_running": server_info["server_running"],
            "server_url": server_info["server_url"],
            "map_file_available": server_info["current_map_file"] is not None,
            "map_file_size": server_info["current_map_size"],
            "large_html_support": True,
            "same_origin_policy_fix": True,
            "webengine_http_loading": True,
            "no_temp_files_conflict": True,
            "reactive_counties": True,
            "reactive_weather": True,
            "counties_loaded": self.counties_gdf is not None,
            "counties_count": len(self.counties_gdf) if self.counties_gdf is not None else 0,
            "weather_data_loaded": self.current_weather_data is not None,
            "version": "v3.0"
        }
    
    def cleanup(self):
        """
        🧹 Cleanup metódus az objektum megszüntetésekor.
        """
        # HTTP szerver leállítása
        if self.local_server and self.local_server.running:
            print("🛑 Stopping local HTTP server...")
            self.local_server.stop()
            self.local_server.wait()
        
        # Temp fájlok törlése
        if self.current_map_file and os.path.exists(self.current_map_file):
            try:
                os.remove(self.current_map_file)
                print(f"🗑️ Temp map file removed: {self.current_map_file}")
            except Exception as e:
                print(f"⚠️ Failed to remove temp file: {e}")
        
        print("🧹 HungarianMapVisualizer cleanup completed")


# === DEMO ÉS TESZT FUNKCIÓK ===

def demo_http_server_folium_map_visualizer():
    """
    🧪 🌐 HTTP SZERVER Folium Map Visualizer demo alkalmazás - Same-Origin Policy Fix + Reaktív Megyehatárok verziója.
    """
    import sys
    from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QLabel
    
    app = QApplication(sys.argv)
    
    # Fő ablak
    window = QMainWindow()
    window.setWindowTitle("🌐 HTTP SZERVER Folium Map Visualizer Demo - Same-Origin Policy Fix v3.0 + Reaktív Megyehatárok + Dinamikus Színskála")
    window.setGeometry(100, 100, 1400, 900)
    
    # Central widget
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    
    layout = QVBoxLayout(central_widget)
    
    # 🌐 HTTP szerver verzió info
    server_info = QWidget()
    server_layout = QHBoxLayout(server_info)
    
    server_title = QLabel("🌐 HTTP SZERVER VERZIÓ TESZT:")
    server_title.setStyleSheet("font-weight: bold; color: #3498DB;")
    server_layout.addWidget(server_title)
    
    debug_info_btn = QPushButton("🔍 Debug Info")
    counties_test_btn = QPushButton("🗺️ Megyék Teszt")
    weather_test_btn = QPushButton("🌤️ Weather Teszt")
    server_info_btn = QPushButton("🌐 Szerver Info")
    
    server_layout.addWidget(debug_info_btn)
    server_layout.addWidget(counties_test_btn)
    server_layout.addWidget(weather_test_btn)
    server_layout.addWidget(server_info_btn)
    server_layout.addStretch()
    
    layout.addWidget(server_info)
    
    # 🔧 Dinamikus színskála teszt gombok
    gradient_controls = QWidget()
    gradient_layout = QHBoxLayout(gradient_controls)
    
    gradient_title = QLabel("🎨 DINAMIKUS SZÍNSKÁLA TESZT:")
    gradient_title.setStyleSheet("font-weight: bold; color: #9B59B6;")
    gradient_layout.addWidget(gradient_title)
    
    temp_overlay_btn = QPushButton("🌡️ Hőmérséklet Overlay")
    wind_overlay_btn = QPushButton("💨 Szél Overlay")
    precip_overlay_btn = QPushButton("🌧️ Csapadék Overlay")
    clear_overlay_btn = QPushButton("🧹 Clear Overlay")
    
    gradient_layout.addWidget(temp_overlay_btn)
    gradient_layout.addWidget(wind_overlay_btn)
    gradient_layout.addWidget(precip_overlay_btn)
    gradient_layout.addWidget(clear_overlay_btn)
    gradient_layout.addStretch()
    
    layout.addWidget(gradient_controls)
    
    # Folium map visualizer
    map_visualizer = HungarianMapVisualizer()
    layout.addWidget(map_visualizer)
    
    # Event handlers
    def on_map_ready():
        print("🌐 HTTP SZERVER Folium térkép betöltve és kész - Same-Origin Policy fix + Reaktív megyehatárok sikeres!")
        
        # Server info
        server_info = map_visualizer.get_http_server_info()
        print("🌐 HTTP szerver információk:")
        for key, value in server_info.items():
            print(f"   {key}: {value}")
        
        # Gradient info
        gradient_info = map_visualizer.get_dynamic_gradient_info()
        print("🎨 Dinamikus gradient információk:")
        for key, value in gradient_info.items():
            print(f"   {key}: {value}")
        
        # HTTP debug info
        http_info = map_visualizer.get_http_debug_info()
        print("🌐 HTTP szerver verzió információk:")
        for key, value in http_info.items():
            print(f"   {key}: {value}")
    
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
    
    # HTTP szerver button handlers
    def show_debug_info():
        print("🔍 HTTP szerver debug info megjelenítése...")
        http_info = map_visualizer.get_http_debug_info()
        gradient_info = map_visualizer.get_dynamic_gradient_info()
        
        debug_text = "🌐 HTTP SZERVER DEBUG INFO:\n"
        for key, value in http_info.items():
            debug_text += f"  {key}: {value}\n"
        
        debug_text += "\n🎨 GRADIENT DEBUG INFO:\n"
        for key, value in gradient_info.items():
            debug_text += f"  {key}: {value}\n"
        
        QMessageBox.information(window, "HTTP Szerver Debug Info", debug_text)
    
    def test_counties_reactive():
        print("🗺️ 🚀 HTTP SZERVER Megyék teszt...")
        print("🧪 Generálok demo megyeadatokat és tesztelem a reaktív frissítést...")
        
        # Demo megyék generálása (egyszerű téglalap geometriákkal)
        import geopandas as gpd
        from shapely.geometry import Polygon
        
        demo_counties = []
        county_names = ["Budapest", "Pest", "Fejér", "Komárom-Esztergom", "Veszprém"]
        
        for i, name in enumerate(county_names):
            # Egyszerű téglalap minden megyének
            bounds = [
                18.5 + i * 0.5,     # min_x
                47.0 + i * 0.3,     # min_y  
                19.0 + i * 0.5,     # max_x
                47.5 + i * 0.3      # max_y
            ]
            
            polygon = Polygon([
                (bounds[0], bounds[1]),  # SW
                (bounds[2], bounds[1]),  # SE
                (bounds[2], bounds[3]),  # NE
                (bounds[0], bounds[3]),  # NW
                (bounds[0], bounds[1])   # SW (close)
            ])
            
            demo_counties.append({
                'megye': name,
                'geometry': polygon
            })
        
        demo_gdf = gpd.GeoDataFrame(demo_counties)
        
        print(f"🧪 Demo counties GeoDataFrame created: {len(demo_gdf)} counties")
        print("🚀 Testing HTTP SERVER REACTIVE set_counties_geodataframe...")
        
        # REAKTÍV teszt - a térkép automatikusan frissül!
        map_visualizer.set_counties_geodataframe(demo_gdf)
        
        print("✅ 🚀 HTTP SZERVER REAKTÍV teszt befejezve - a térkép automatikusan frissült!")
    
    def test_weather_reactive():
        print("🌤️ 🚀 HTTP SZERVER Weather teszt...")
        demo_data = map_visualizer.generate_demo_weather_data()
        
        print("🚀 Testing HTTP SERVER REACTIVE set_weather_data...")
        
        # REAKTÍV teszt - a térkép automatikusan frissül!
        map_visualizer.set_weather_data(demo_data)
        
        print("✅ 🚀 HTTP SZERVER weather teszt befejezve - a térkép automatikusan frissült!")
    
    def show_server_info():
        print("🌐 HTTP szerver információk megjelenítése...")
        server_info = map_visualizer.get_http_server_info()
        
        if server_info["server_running"]:
            info_text = f"🌐 HTTP SZERVER AKTÍV:\n\n"
            info_text += f"URL: {server_info['server_url']}\n"
            info_text += f"Host: {server_info['http_host']}\n"
            info_text += f"Port: {server_info['http_port']}\n"
            info_text += f"Térkép fájl: {server_info['current_map_file']}\n"
            info_text += f"Fájl méret: {server_info['current_map_size']:,} bytes\n"
            info_text += f"Verzió: {server_info['version']}"
        else:
            info_text = "❌ HTTP szerver nem fut!"
        
        QMessageBox.information(window, "HTTP Szerver Info", info_text)
    
    # Gradient teszt button handlers
    def test_temperature_overlay():
        print("🌡️ Hőmérséklet overlay teszt...")
        demo_data = map_visualizer.generate_demo_weather_data()
        temp_data = {'temperature': demo_data['temperature']}
        map_visualizer.set_weather_data(temp_data)  # REAKTÍV!
    
    def test_wind_overlay():
        print("💨 Szél overlay teszt...")
        demo_data = map_visualizer.generate_demo_weather_data()
        wind_data = {'wind_speed': demo_data['wind_speed']}
        map_visualizer.set_weather_data(wind_data)  # REAKTÍV!
    
    def test_precipitation_overlay():
        print("🌧️ Csapadék overlay teszt...")
        demo_data = map_visualizer.generate_demo_weather_data()
        precip_data = {'precipitation': demo_data['precipitation']}
        map_visualizer.set_weather_data(precip_data)  # REAKTÍV!
    
    def test_clear_overlay():
        print("🧹 Overlay törlése...")
        map_visualizer.clear_active_overlay_parameter()
        map_visualizer.toggle_weather_overlay(False)
    
    # HTTP szerver button connections
    debug_info_btn.clicked.connect(show_debug_info)
    counties_test_btn.clicked.connect(test_counties_reactive)
    weather_test_btn.clicked.connect(test_weather_reactive)
    server_info_btn.clicked.connect(show_server_info)
    
    # Gradient button connections
    temp_overlay_btn.clicked.connect(test_temperature_overlay)
    wind_overlay_btn.clicked.connect(test_wind_overlay)
    precip_overlay_btn.clicked.connect(test_precipitation_overlay)
    clear_overlay_btn.clicked.connect(test_clear_overlay)
    
    # Signalok kapcsolása
    map_visualizer.map_ready.connect(on_map_ready)
    map_visualizer.county_clicked.connect(on_county_clicked)
    map_visualizer.coordinates_clicked.connect(on_coordinates_clicked)
    map_visualizer.map_moved.connect(on_map_moved)
    map_visualizer.export_completed.connect(on_export_completed)
    map_visualizer.error_occurred.connect(on_error_occurred)
    
    # Cleanup
    def cleanup_on_close():
        print("🧹 Application closing - cleaning up...")
        map_visualizer.cleanup()
    
    app.aboutToQuit.connect(cleanup_on_close)
    
    window.show()
    
    print("🌐 HTTP SZERVER Folium Map Visualizer Demo elindítva - Same-Origin Policy Fix v3.0 + Reaktív Megyehatárok!")
    print("🔧 HTTP SZERVER MEGOLDÁS ELŐNYEI v3.0:")
    print("   ✅ Beágyazott HTTP szerver QThread-ben")
    print("   ✅ WebEngine http://127.0.0.1:PORT/map.html betöltés")
    print("   ✅ Same-Origin Policy problémák végleg megoldva")
    print("   ✅ Nagy HTML fájlok (1.5MB+) teljes támogatása")
    print("   ✅ setHtml() méretkorlát megoldva")
    print("   ✅ file:// protokoll problémák megszűntek")
    print("   ✅ JavaScript és CSS teljes támogatás")
    print("   ✅ Nincs WebEngine cache konfliktus")
    print("   ✅ Stabil és megbízható működés")
    print("   🚀 REAKTÍV MEGYEHATÁROK - A 'futár és festő' probléma megoldva!")
    print("   🚀 REAKTÍV IDŐJÁRÁSI OVERLAY - Automatikus frissítés")
    print("   🚀 set_counties_geodataframe() → AZONNALI térképfrissítés")
    print("   🚀 set_weather_data() → AZONNALI térképfrissítés")
    print("🔧 DINAMIKUS SZÍNSKÁLA JAVÍTÁSOK v1.2:")
    print("   ✅ COLOR_SCALE_GRADIENTS mapping minden overlay típushoz")
    print("   ✅ set_active_overlay_parameter() metódus")
    print("   ✅ Overlay-specifikus jelmagyarázat generálás")
    print("   ✅ Automatikus overlay parameter beállítás")
    print("   ✅ UI kijelző az aktív overlay parameter-hez")
    print("✅ TELJES HTTP SZERVER INTERAKTÍV FOLIUM TÉRKÉP!")
    print("🎮 Elérhető funkciók:")
    print("   🖱️ Kattintható megyék")
    print("   📍 Koordináta kattintás")
    print("   🔍 Zoom/Pan interakció")
    print("   👆 Hover tooltipek")
    print("   🌤️ Weather overlay dinamikus színskálával")
    print("   🎨 Téma támogatás")
    print("   💾 HTML export")
    print("   🌉 JavaScript ↔ Python bridge")
    print("   🧪 HTTP SZERVER TESZT GOMBOK:")
    print("      🚀 Kattints a reaktív gombokra a működés teszteléséhez!")
    print("      🗺️ 'Megyék Teszt' - Demo megyék betöltése és AZONNALI térképfrissítés")
    print("      🌤️ 'Weather Teszt' - Demo időjárási adatok és AZONNALI térképfrissítés") 
    print("      🌐 'Szerver Info' - HTTP szerver részletes információk")
    print("      🎨 Kattints a színskála gombokra a különböző overlay típusok teszteléséhez!")
    print("🎯 HTTP SZERVER MŰKÖDÉS:")
    print("   🌐 Automatikus helyi HTTP szerver indítás")
    print("   🌐 Folium térkép fájlba mentés")
    print("   🌐 WebEngine http://127.0.0.1:PORT/map.html betöltés")
    print("   🚀 Amikor az alkalmazás betölti a magyar megyéket → AUTOMATIKUS térképfrissítés")
    print("   🚀 Amikor időjárási adatok érkeznek → AUTOMATIKUS térképfrissítés")
    print("   🚀 Nincs manuális frissítés szükséges!")
    print("   🚀 A 'futár és festő' probléma végleg megoldva!")
    
    if FOLIUM_AVAILABLE:
        print("✅ Folium library elérhető!")
    else:
        print("❌ Folium library hiányzik - telepítsd: pip install folium branca")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    demo_http_server_folium_map_visualizer()


# Export
__all__ = ['HungarianMapVisualizer', 'FoliumMapConfig', 'JavaScriptBridge', 'FoliumMapGenerator', 'LocalHttpServerThread']
        
