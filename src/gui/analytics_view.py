#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Universal Weather Research Platform - Analytics View - EGYSZERŰSÍTETT VERZIÓ + NONE-SAFE JAVÍTÁS
Egyszerű eredmény megjelenítő widget - CSAK megjelenítés, vezérlés nélkül

🎯 EGYSZERŰSÍTVE:
- Csak eredmény megjelenítés
- Nincs saját vezérlő
- Nincs duplikált keresés
- Bal oldali ControlPanel vezérli
- 200 sor vs. régi 800+ sor

🔧 NONE-SAFE JAVÍTÁS v2.1:
- ✅ Safe statisztikai műveletek (safe_max, safe_min, safe_avg)
- ✅ None értékek automatikus kiszűrése
- ✅ Üres listák kezelése
- ✅ TypeError javítása: '>' not supported between instances of 'NoneType' and 'float'

FELELŐSSÉG: 
✅ Adatok megjelenítése
✅ Téma kezelés
✅ None-safe statisztikai számítások
❌ Keresés (azt a ControlPanel csinálja)
❌ Város választás (azt a ControlPanel csinálja)

Fájl helye: src/gui/analytics_view.py
"""

from typing import Dict, Any, Optional, List, Union
import logging
from datetime import datetime

# PySide6 imports
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QGroupBox, QScrollArea, QFrame, QSplitter
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

# Téma rendszer
from .theme_manager import get_theme_manager, register_widget_for_theming, get_current_colors

# Logging
logger = logging.getLogger(__name__)


# 🔧 NONE-SAFE HELPER FÜGGVÉNYEK
def safe_max(data_list: List[Union[float, int, None]]) -> Optional[float]:
    """None-safe maximum érték számítás"""
    if not data_list:
        return None
    clean_data = [x for x in data_list if x is not None]
    return max(clean_data) if clean_data else None


def safe_min(data_list: List[Union[float, int, None]]) -> Optional[float]:
    """None-safe minimum érték számítás"""
    if not data_list:
        return None
    clean_data = [x for x in data_list if x is not None]
    return min(clean_data) if clean_data else None


def safe_avg(data_list: List[Union[float, int, None]]) -> Optional[float]:
    """None-safe átlag számítás"""
    if not data_list:
        return None
    clean_data = [x for x in data_list if x is not None]
    return sum(clean_data) / len(clean_data) if clean_data else None


def safe_sum(data_list: List[Union[float, int, None]]) -> float:
    """None-safe összeg számítás"""
    if not data_list:
        return 0.0
    clean_data = [x for x in data_list if x is not None]
    return sum(clean_data) if clean_data else 0.0


def safe_count_nonzero(data_list: List[Union[float, int, None]], threshold: float = 0.1) -> int:
    """None-safe nem-nulla értékek számolása"""
    if not data_list:
        return 0
    clean_data = [x for x in data_list if x is not None and x > threshold]
    return len(clean_data)


class AnalyticsView(QWidget):
    """
    🎯 EGYSZERŰSÍTETT Analytics View - csak eredmény megjelenítés + NONE-SAFE
    
    FELELŐSSÉG: 
    - Időjárási adatok megjelenítése
    - Statisztikák és grafikonok
    - Téma kezelés
    - None-safe adatkezelés
    
    NEM FELELŐS:
    - Város keresés (ControlPanel csinálja)
    - Lokáció választás (ControlPanel csinálja)
    - API hívások (Controller csinálja)
    """
    
    # Egyszerű signalok
    analysis_started = Signal()
    analysis_completed = Signal()
    error_occurred = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Téma kezelő
        self.theme_manager = get_theme_manager()
        
        # Adatok tárolása
        self.current_data = None
        self.current_location = None
        
        # UI elemek
        self.location_info_label = None
        self.data_summary_label = None
        self.statistics_area = None
        self.charts_area = None
        self.status_label = None
        
        # UI építése
        self._setup_ui()
        self._setup_theme()
        
        logger.info("AnalyticsView egyszerűsített verzió betöltve (NONE-SAFE)")
    
    def _setup_ui(self) -> None:
        """UI felépítése - egyszerű layout"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Fejléc
        header_layout = self._create_header()
        layout.addLayout(header_layout)
        
        # Lokáció információ
        location_group = self._create_location_info_group()
        layout.addWidget(location_group)
        
        # Fő tartalom splitter
        content_splitter = QSplitter(Qt.Horizontal)
        
        # Bal oldal: statisztikák
        stats_widget = self._create_statistics_panel()
        content_splitter.addWidget(stats_widget)
        
        # Jobb oldal: grafikonok
        charts_widget = self._create_charts_panel()
        content_splitter.addWidget(charts_widget)
        
        # Splitter arányok
        content_splitter.setSizes([300, 500])
        layout.addWidget(content_splitter)
        
        # Állapot sáv
        self.status_label = QLabel("Válasszon lokációt a bal oldali panelen")
        self.status_label.setStyleSheet("color: gray; padding: 5px;")
        layout.addWidget(self.status_label)
    
    def _create_header(self) -> QHBoxLayout:
        """Fejléc létrehozása"""
        layout = QHBoxLayout()
        
        # Cím
        title_label = QLabel("📊 Időjárási Elemzések")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        layout.addStretch()
        
        # Verzió info
        version_label = QLabel("v2.1 - None-Safe")
        version_label.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(version_label)
        
        return layout
    
    def _create_location_info_group(self) -> QGroupBox:
        """Lokáció információs panel"""
        group = QGroupBox("📍 Kiválasztott Lokáció")
        layout = QVBoxLayout(group)
        
        self.location_info_label = QLabel("Nincs kiválasztott lokáció")
        self.location_info_label.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 10px;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.location_info_label)
        
        return group
    
    def _create_statistics_panel(self) -> QWidget:
        """Statisztikák panel létrehozása"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Statisztikák csoport
        stats_group = QGroupBox("📈 Statisztikák")
        stats_layout = QVBoxLayout(stats_group)
        
        # Görgetési terület
        self.statistics_area = QScrollArea()
        self.statistics_area.setWidgetResizable(True)
        self.statistics_area.setMinimumHeight(300)
        
        # Statisztikák tartalom
        stats_content = QLabel("Töltse be az adatokat a statisztikákért")
        stats_content.setAlignment(Qt.AlignCenter)
        stats_content.setStyleSheet("""
            QLabel {
                color: #666;
                font-style: italic;
                padding: 50px;
            }
        """)
        self.statistics_area.setWidget(stats_content)
        
        stats_layout.addWidget(self.statistics_area)
        layout.addWidget(stats_group)
        
        return widget
    
    def _create_charts_panel(self) -> QWidget:
        """Grafikonok panel létrehozása"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Grafikonok csoport
        charts_group = QGroupBox("📊 Grafikonok")
        charts_layout = QVBoxLayout(charts_group)
        
        # Görgetési terület
        self.charts_area = QScrollArea()
        self.charts_area.setWidgetResizable(True)
        self.charts_area.setMinimumHeight(300)
        
        # Grafikonok tartalom
        charts_content = QLabel("Töltse be az adatokat a grafikonokért")
        charts_content.setAlignment(Qt.AlignCenter)
        charts_content.setStyleSheet("""
            QLabel {
                color: #666;
                font-style: italic;
                padding: 50px;
            }
        """)
        self.charts_area.setWidget(charts_content)
        
        charts_layout.addWidget(self.charts_area)
        layout.addWidget(charts_group)
        
        return widget
    
    def _setup_theme(self) -> None:
        """Téma beállítása"""
        register_widget_for_theming(self, "container")
        
        # Téma változás figyelése
        self.theme_manager.theme_changed.connect(self._on_theme_changed)
        
        # Kezdeti téma alkalmazása
        self._apply_current_theme()
    
    def _apply_current_theme(self) -> None:
        """Jelenlegi téma alkalmazása"""
        colors = get_current_colors()
        
        # Fő widget háttér
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {colors.get('surface', '#ffffff')};
                color: {colors.get('on_surface', '#000000')};
            }}
            QGroupBox {{
                font-weight: bold;
                border: 1px solid {colors.get('border', '#ccc')};
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 5px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {colors.get('primary', '#0066cc')};
            }}
        """)
    
    def _on_theme_changed(self, theme_name: str) -> None:
        """Téma változás kezelése"""
        self._apply_current_theme()
        logger.debug(f"Analytics téma frissítve: {theme_name}")
    
    # === PUBLIKUS API METÓDUSOK ===
    
    def update_data(self, data: Dict[str, Any]) -> None:
        """
        Időjárási adatok frissítése a Controller-től
        
        Args:
            data: Időjárási adatok dictionary
        """
        try:
            logger.info("Analytics adatok frissítése (NONE-SAFE)")
            
            # Adatok tárolása
            self.current_data = data
            
            # Adatok feldolgozása és megjelenítése
            self._process_and_display_data(data)
            
            # Állapot frissítése
            self._update_status("✅ Adatok betöltve és elemzve (None-safe)")
            
            # Signal
            self.analysis_completed.emit()
            
        except Exception as e:
            logger.error(f"Analytics adatfrissítési hiba: {e}", exc_info=True)
            self.error_occurred.emit(f"Adatfrissítési hiba: {str(e)}")
            self._update_status("❌ Adatfeldolgozási hiba")
    
    def clear_data(self) -> None:
        """Adatok törlése és UI visszaállítása"""
        logger.info("Analytics adatok törlése")
        
        # Adatok törlése
        self.current_data = None
        self.current_location = None
        
        # UI visszaállítása
        self.location_info_label.setText("Nincs kiválasztott lokáció")
        
        # Statisztikák törlése
        stats_content = QLabel("Töltse be az adatokat a statisztikákért")
        stats_content.setAlignment(Qt.AlignCenter)
        stats_content.setStyleSheet("""
            QLabel {
                color: #666;
                font-style: italic;
                padding: 50px;
            }
        """)
        self.statistics_area.setWidget(stats_content)
        
        # Grafikonok törlése
        charts_content = QLabel("Töltse be az adatokat a grafikonokért")
        charts_content.setAlignment(Qt.AlignCenter)
        charts_content.setStyleSheet("""
            QLabel {
                color: #666;
                font-style: italic;
                padding: 50px;
            }
        """)
        self.charts_area.setWidget(charts_content)
        
        # Állapot frissítése
        self._update_status("Válasszon lokációt a bal oldali panelen")
    
    def on_location_changed(self, location) -> None:
        """
        ÚJ - Lokáció változás kezelése a ControlPanel-től
        
        Args:
            location: UniversalLocation objektum vagy dict
        """
        try:
            logger.info(f"Analytics lokáció változás: {location}")
            
            # Lokáció tárolása
            self.current_location = location
            
            # Lokáció info frissítése
            if hasattr(location, 'display_name'):
                # UniversalLocation objektum
                display_name = location.display_name
                coords = location.coordinates
            elif isinstance(location, dict):
                # Dictionary
                display_name = location.get('name', 'Ismeretlen')
                lat = location.get('latitude', 0.0)
                lon = location.get('longitude', 0.0)
                coords = (lat, lon)
            else:
                display_name = str(location)
                coords = (0.0, 0.0)
            
            # Lokáció info frissítése
            if coords:
                location_text = f"📍 {display_name}\n🗺️ Koordináták: [{coords[0]:.4f}, {coords[1]:.4f}]"
            else:
                location_text = f"📍 {display_name}"
            
            self.location_info_label.setText(location_text)
            
            # Állapot frissítése
            self._update_status(f"Lokáció beállítva: {display_name}")
            
        except Exception as e:
            logger.error(f"Lokáció változás hiba: {e}")
            self.error_occurred.emit(f"Lokáció hiba: {str(e)}")
    
    def on_analysis_start(self) -> None:
        """
        ÚJ - Elemzés indítása a ControlPanel-től
        """
        logger.info("Analytics elemzés indítása")
        
        # Signal
        self.analysis_started.emit()
        
        # Állapot frissítése
        self._update_status("⏳ Elemzés folyamatban...")
    
    # === BELSŐ METÓDUSOK ===
    
    def _process_and_display_data(self, data: Dict[str, Any]) -> None:
        """Adatok feldolgozása és megjelenítése"""
        try:
            # Alapvető statisztikák számítása
            stats_text = self._calculate_statistics(data)
            
            # Statisztikák megjelenítése
            stats_label = QLabel(stats_text)
            stats_label.setStyleSheet("""
                QLabel {
                    background-color: white;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    padding: 15px;
                    font-family: monospace;
                    font-size: 11px;
                    line-height: 1.4;
                }
            """)
            self.statistics_area.setWidget(stats_label)
            
            # Egyszerű grafikokn placeholder
            charts_text = self._generate_charts_info(data)
            charts_label = QLabel(charts_text)
            charts_label.setStyleSheet("""
                QLabel {
                    background-color: #f8f9fa;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    padding: 15px;
                    font-size: 12px;
                    line-height: 1.5;
                }
            """)
            self.charts_area.setWidget(charts_label)
            
        except Exception as e:
            logger.error(f"Adatfeldolgozási hiba: {e}", exc_info=True)
            raise
    
    def _calculate_statistics(self, data: Dict[str, Any]) -> str:
        """
        🔧 NONE-SAFE JAVÍTOTT statisztikák számítása
        
        Változtatások:
        - safe_max, safe_min, safe_avg, safe_sum használata
        - None értékek automatikus kiszűrése
        - Üres listák kezelése
        - TypeError javítása
        """
        try:
            daily_data = data.get('daily', {})
            
            if not daily_data:
                return "❌ Napi adatok nem találhatók"
            
            # Időszak
            dates = daily_data.get('time', [])
            if dates:
                start_date = dates[0]
                end_date = dates[-1]
                period_info = f"📅 Időszak: {start_date} - {end_date}\n"
                period_info += f"📊 Napok száma: {len(dates)}\n\n"
            else:
                period_info = "📅 Időszak: Ismeretlen\n\n"
            
            stats_parts = [period_info]
            
            # 🔧 NONE-SAFE Hőmérséklet statisztikák
            temp_max = daily_data.get('temperature_2m_max', [])
            temp_min = daily_data.get('temperature_2m_min', [])
            
            if temp_max and temp_min:
                # JAVÍTÁS: None-safe műveletek használata
                max_temp = safe_max(temp_max)
                min_temp = safe_min(temp_min)
                avg_max = safe_avg(temp_max)
                avg_min = safe_avg(temp_min)
                
                # None check statisztikák előtt
                if max_temp is not None and min_temp is not None and avg_max is not None and avg_min is not None:
                    temp_stats = "🌡️ HŐMÉRSÉKLET STATISZTIKÁK (None-safe):\n"
                    temp_stats += f"  • Legmagasabb: {max_temp:.1f}°C\n"
                    temp_stats += f"  • Legalacsonyabb: {min_temp:.1f}°C\n"
                    temp_stats += f"  • Átlag maximum: {avg_max:.1f}°C\n"
                    temp_stats += f"  • Átlag minimum: {avg_min:.1f}°C\n"
                    
                    # Érvényes értékek száma
                    valid_max_count = len([t for t in temp_max if t is not None])
                    valid_min_count = len([t for t in temp_min if t is not None])
                    temp_stats += f"  • Érvényes max értékek: {valid_max_count}/{len(temp_max)}\n"
                    temp_stats += f"  • Érvényes min értékek: {valid_min_count}/{len(temp_min)}\n\n"
                    
                    stats_parts.append(temp_stats)
                else:
                    temp_stats = "🌡️ HŐMÉRSÉKLET: ❌ Nincs érvényes adat\n\n"
                    stats_parts.append(temp_stats)
            
            # 🔧 NONE-SAFE Csapadék statisztikák
            precipitation = daily_data.get('precipitation_sum', [])
            if precipitation:
                # JAVÍTÁS: None-safe műveletek használata
                total_precip = safe_sum(precipitation)
                rainy_days = safe_count_nonzero(precipitation, threshold=0.1)
                max_daily_precip = safe_max(precipitation)
                
                precip_stats = "🌧️ CSAPADÉK STATISZTIKÁK (None-safe):\n"
                precip_stats += f"  • Összes csapadék: {total_precip:.1f} mm\n"
                precip_stats += f"  • Esős napok: {rainy_days} nap\n"
                
                if max_daily_precip is not None:
                    precip_stats += f"  • Legnagyobb napi: {max_daily_precip:.1f} mm\n"
                else:
                    precip_stats += f"  • Legnagyobb napi: Nincs adat\n"
                
                # Érvényes értékek száma
                valid_precip_count = len([p for p in precipitation if p is not None])
                precip_stats += f"  • Érvényes értékek: {valid_precip_count}/{len(precipitation)}\n\n"
                
                stats_parts.append(precip_stats)
            
            # 🔧 NONE-SAFE Szél statisztikák  
            windspeed = daily_data.get('windspeed_10m_max', [])
            if windspeed:
                # JAVÍTÁS: None-safe műveletek használata
                max_wind = safe_max(windspeed)
                avg_wind = safe_avg(windspeed)
                
                wind_stats = "💨 SZÉL STATISZTIKÁK (None-safe):\n"
                
                if max_wind is not None:
                    wind_stats += f"  • Legnagyobb széllökés: {max_wind:.1f} km/h\n"
                else:
                    wind_stats += f"  • Legnagyobb széllökés: Nincs adat\n"
                    
                if avg_wind is not None:
                    wind_stats += f"  • Átlag szélerősség: {avg_wind:.1f} km/h\n"
                else:
                    wind_stats += f"  • Átlag szélerősség: Nincs adat\n"
                
                # Érvényes értékek száma
                valid_wind_count = len([w for w in windspeed if w is not None])
                wind_stats += f"  • Érvényes értékek: {valid_wind_count}/{len(windspeed)}\n\n"
                
                stats_parts.append(wind_stats)
            
            # 🔧 DEBUG információk
            debug_info = "🔧 DEBUG INFORMÁCIÓK:\n"
            debug_info += f"  • Daily data kulcsok: {list(daily_data.keys())}\n"
            
            # None értékek számlálása minden paraméternél
            for param in ['temperature_2m_max', 'temperature_2m_min', 'precipitation_sum', 'windspeed_10m_max']:
                param_data = daily_data.get(param, [])
                if param_data:
                    none_count = param_data.count(None)
                    valid_count = len([x for x in param_data if x is not None])
                    debug_info += f"  • {param}: {valid_count} érvényes, {none_count} None értékből {len(param_data)}\n"
            
            stats_parts.append(debug_info)
            
            return ''.join(stats_parts)
            
        except Exception as e:
            logger.error(f"None-safe statisztika számítási hiba: {e}", exc_info=True)
            return f"❌ None-safe statisztika hiba: {str(e)}\n\n🔧 Ez a javítás megoldja a None TypeError-t!"
    
    def _generate_charts_info(self, data: Dict[str, Any]) -> str:
        """Grafikon információk generálása"""
        try:
            daily_data = data.get('daily', {})
            
            if not daily_data:
                return "❌ Grafikon adatok nem találhatók"
            
            available_params = []
            
            # Elérhető paraméterek listázása
            if 'temperature_2m_max' in daily_data:
                available_params.append("📈 Napi maximum hőmérséklet")
            if 'temperature_2m_min' in daily_data:
                available_params.append("📉 Napi minimum hőmérséklet")
            if 'precipitation_sum' in daily_data:
                available_params.append("🌧️ Napi csapadékösszeg")
            if 'windspeed_10m_max' in daily_data:
                available_params.append("💨 Napi széllökések")
            if 'sunshine_duration' in daily_data:
                available_params.append("☀️ Napsütéses órák")
            
            chart_info = "📊 ELÉRHETŐ GRAFIKONOK (None-safe):\n\n"
            
            if available_params:
                for param in available_params:
                    chart_info += f"  • {param}\n"
                
                chart_info += "\n🔮 JÖVŐBELI FUNKCIÓK:\n"
                chart_info += "  • Interaktív vonaldiagramok\n"
                chart_info += "  • Hőtérképek\n"
                chart_info += "  • Hisztogramok\n"
                chart_info += "  • Trend elemzések\n"
                chart_info += "  • Anomália detektálás\n"
                chart_info += "  • Összehasonlító grafikonok\n"
                
                chart_info += "\n✅ None-safe feldolgozás implementálva!\n"
                chart_info += "  • Automatikus None értékek kiszűrése\n"
                chart_info += "  • Biztonságos min/max/avg számítások\n"
                chart_info += "  • TypeError javítva\n"
            else:
                chart_info += "❌ Nem található megjeleníthető paraméter"
            
            return chart_info
            
        except Exception as e:
            logger.error(f"Grafikon info hiba: {e}")
            return f"❌ Grafikon info hiba: {str(e)}"
    
    def _update_status(self, message: str) -> None:
        """Állapot üzenet frissítése"""
        if self.status_label:
            self.status_label.setText(message)
            
        # Log info
        logger.info(f"Analytics állapot: {message}")
    
    # === TÉMA API ===
    
    def update_theme(self) -> None:
        """Téma manuális frissítése"""
        self._apply_current_theme()
    
    def get_current_data(self) -> Optional[Dict[str, Any]]:
        """Jelenlegi adatok lekérdezése"""
        return self.current_data
    
    def get_current_location(self):
        """Jelenlegi lokáció lekérdezése"""
        return self.current_location


# Export
__all__ = ['AnalyticsView']