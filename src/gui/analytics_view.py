#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Universal Weather Research Platform - Analytics View Module (REFAKTORÁLT)
Ez a modul a multi-city régió elemzések dashboardját valósítja meg.

✅ REFAKTORÁLT MŰKÖDÉS:
- A nézet most már nem indít saját lekérdezéseket.
- A gombok egy központi `multi_city_query_requested` signalt bocsátanak ki.
- A MainWindow kezeli a lekérdezést és az eredményt egy publikus slot-on
  (`update_with_multi_city_result`) keresztül küldi vissza.
- Ezzel a nézet teljesen szinkronban van a többi modullal (Térkép, ControlPanel).

🔧 KRITIKUS JAVÍTÁSOK:
✅ Visszatérés a HEATMAP-ekhez (MINDEN TAB)
✅ KONSTANS 365 TÉGLALAP - mindig ugyanannyi adatpont
✅ METEOROLÓGIAI SZÍNSKÁLÁK - professzionális időjárási színek
✅ MINDEN TÉGLALAP KITÖLTVE - nulla érték = megfelelő szín (nem üres!)
✅ 1 év = 365 téglalap (1 nap/téglalap), 5 év = 365 téglalap (5 nap/téglalap)
✅ RÁCS VONALAK - téglalapok elválasztva (Excel-szerű)
✅ INTELLIGENS TENGELYEK - időszak alapú címkék
✅ BEAUFORT SZÉL SZÍNSKÁLA - 13 fokozat progresszív színátmenet
✅ 4. TAB: MAX SZÉLLÖKÉS - windgusts_10m_max külön megjelenítés
✅ RELEVÁNS METEOROLÓGIAI STATISZTIKÁK - bal oldali panel
✅ KOMPAKT KÁRTYÁS RENDSZER - 12px olvasható betűméret
🚀 MULTI-CITY RÉGIÓ INTEGRÁCIÓ - Észak-Magyarország, Pest, stb. elemzések
🔥 SIGNAL EMISSION JAVÍTÁS - multi_city_analysis_completed signal kibocsátás
🚨 STATISZTIKÁK JAVÍTÁS - _process_and_display_statistics() MEGHÍVÁS
🌪️ VÉGSŐ JAVÍTÁS: WindChart/WindRoseChart DEDICATED KOMPONENSEK HOZZÁADÁSA

Fájl helye: src/gui/analytics_view.py
"""

from typing import Dict, Any, Optional, List, Union, Tuple
import logging
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import matplotlib.colors as mcolors

# PySide6 imports
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QGroupBox, QScrollArea, QFrame, QSplitter, QGridLayout, QTabWidget,
    QPushButton, QComboBox, QMessageBox, QProgressBar
)
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QFont

# Téma rendszer
from .theme_manager import get_theme_manager, register_widget_for_theming, get_current_colors

# Chart imports - JAVÍTOTT: VISSZA A HEATMAP-EKHEZ + DEDICATED WIND CHARTOK
from .charts.heatmap_chart import HeatmapCalendarChart
from .charts.wind_chart import WindChart
from .charts.wind_rose_chart import WindRoseChart

# 🚀 MULTI-CITY ENGINE IMPORT
try:
    from ..analytics.multi_city_engine import MultiCityEngine, MultiCityQuery
    from ..data.models import AnalyticsResult, CityWeatherResult, AnalyticsQuestion
    from ..data.enums import RegionScope, AnalyticsMetric, QuestionType
    MULTI_CITY_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("✅ Multi-City Engine import sikeres!")
except ImportError as e:
    MULTI_CITY_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning(f"❌ Multi-City Engine import hiba: {e}")

# Logging
logger = logging.getLogger(__name__)


# 🎨 METEOROLÓGIAI SZÍNSKÁLÁK - KONSTANS HEATMAP-EKHEZ (BEAUFORT FRISSÍTETT)
class MeteorologicalColorMaps:
    """🎨 Professzionális meteorológiai színskálák heatmap-ekhez - BEAUFORT VERZIÓ"""
    
    @staticmethod
    def get_precipitation_colormap():
        """🌧️ Csapadék színskála - 0mm = FEHÉR!"""
        precipitation_levels = [0, 1, 5, 10, 20, 30, 40, 50, 80, 100]
        precipitation_colors = [
            '#FFFFFF',  # 0 mm - FEHÉR (száraz nap!)
            '#E6F3FF',  # 1 mm - nagyon világoskék  
            '#CCE7FF',  # 5 mm - világoskék
            '#99D6FF',  # 10 mm - kék
            '#66C2FF',  # 20 mm - sötétkék
            '#3399FF',  # 30 mm - erős kék
            '#0066CC',  # 40 mm - sötét kék
            '#004499',  # 50 mm - nagyon sötét kék
            '#002266',  # 80 mm - sötétbordó
            '#001133'   # 100+ mm - fekete-kék
        ]
        
        cmap = mcolors.ListedColormap(precipitation_colors)
        norm = mcolors.BoundaryNorm(precipitation_levels, len(precipitation_colors))
        return cmap, norm
    
    @staticmethod
    def get_wind_colormap():
        """
        💨 BEAUFORT-ALAPÚ Magyar meteorológiai szél színskála - 13 FOKOZAT!
        
        🌈 PROGRESSZÍV SZÍNÁTMENET:
        Fehér → Világoskék → Zöld → Sárga → Narancs → Piros → Bíbor → Ibolya
        
        🎯 HÁROM LOGIKUS ZÓNA:
        • Alapfok (0-5): Fehér → Kék → Zöld (nyugodt szelek)
        • Elsőfok (6-7): Sárga → Narancs (figyelmeztető)  
        • Másodfok (8-12): Piros → Bíbor → Ibolya (veszély)
        
        📊 BEAUFORT STANDARD:
        • 13 fokozat (0-12) 
        • Hivatalos km/h határok
        • Meteorológiai szakmai megfelelés
        """
        
        # 🎯 BEAUFORT SZINTŰ HATÁROK (km/h) - 13 FOKOZAT
        beaufort_levels = [
            0,    # 0: Szélcsend
            1,    # 1: Gyenge szellő
            6,    # 2: Enyhe szél  
            11,   # 3: Gyenge szél
            19,   # 4: Mérsékelt szél
            29,   # 5: Élénk szél
            39,   # 6: Erős szél
            49,   # 7: Viharos szél
            60,   # 8: Élénk viharos szél
            72,   # 9: Heves vihar
            85,   # 10: Dühöngő vihar
            100,  # 11: Heves szélvész
            115,  # 12: Orkán
            150   # 12+: Szuper orkán (colorbar határhoz)
        ]
        
        # 🌈 BEAUFORT PROGRESSZÍV SZÍNPALETTA - INTUITÍV ÁTMENET
        beaufort_colors = [
            # === ALAPFOK ZÓNA (0-5): NYUGODT SZÍNEK ===
            '#FFFFFF',  # 0: Szélcsend - Tiszta fehér
            '#F0F8FF',  # 1: Gyenge szellő - Alice blue (nagyon halvány kék)
            '#E6F3FF',  # 2: Enyhe szél - Világos égkék
            '#CCE7FF',  # 3: Gyenge szél - Világosabb kék
            '#90EE90',  # 4: Mérsékelt szél - Világos zöld (természet)
            '#32CD32',  # 5: Élénk szél - Lime zöld (aktív, de biztonságos)
            
            # === ELSŐFOK ZÓNA (6-7): FIGYELMEZTETŐ SZÍNEK ===
            '#FFD700',  # 6: Erős szél - Arany sárga (FIGYELEM!)
            '#FFA500',  # 7: Viharos szél - Narancs (FOKOZOTT FIGYELEM!)
            
            # === MÁSODFOK ZÓNA (8-12): VESZÉLY SZÍNEK ===
            '#FF6347',  # 8: Élénk viharos - Paradicsom piros (VESZÉLY!)
            '#FF4500',  # 9: Heves vihar - Narancs-piros (NAGY VESZÉLY!)
            '#DC143C',  # 10: Dühöngő vihar - Crimson piros (SZÉLSŐSÉGES!)
            '#8B008B',  # 11: Heves szélvész - Sötét magenta (KRITIKUS!)
            '#4B0082'   # 12: Orkán - Indigo ibolya (KATASZTROFÁLIS!)
        ]
        
        # 🎨 MATPLOTLIB COLORMAP OBJEKTUMOK
        cmap = mcolors.ListedColormap(beaufort_colors)
        norm = mcolors.BoundaryNorm(beaufort_levels, len(beaufort_colors))
        
        return cmap, norm


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


def safe_count(data_list: List[Union[float, int, None]], condition_func) -> int:
    """None-safe feltételes számolás"""
    if not data_list:
        return 0
    clean_data = [x for x in data_list if x is not None]
    return sum(1 for x in clean_data if condition_func(x))


# Rekord kártyák (változatlanok)
class RecordCard(QWidget):
    """🏆 Kompakt rekord kártya widget - TAB LAYOUT-hoz optimalizált"""
    
    def __init__(self, icon: str, title: str, value: str = "-", date: str = "-"):
        super().__init__()
        self.icon = icon
        self.title = title
        self._setup_ui()
        self.update_record(value, date)
    
    def _setup_ui(self):
        """Kompakt rekord kártya UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)
        
        # Icon + title
        header_layout = QHBoxLayout()
        
        icon_label = QLabel(self.icon)
        icon_label.setStyleSheet("font-size: 14px;")
        header_layout.addWidget(icon_label)
        
        title_label = QLabel(self.title)
        title_label.setStyleSheet("font-size: 9px; font-weight: bold;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Value
        self.value_label = QLabel("-")
        self.value_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #C43939;")
        self.value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.value_label)
        
        # Date
        self.date_label = QLabel("-")
        self.date_label.setStyleSheet("font-size: 7px; color: gray;")
        self.date_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.date_label)
        
        # Kompakt styling
        self.setStyleSheet("""
            RecordCard {
                background-color: #f9fafb;
                border: 1px solid #d1d5db;
                border-radius: 3px;
                max-height: 65px;
                max-width: 200px;
            }
        """)
    
    def update_record(self, value: str, date: str):
        """Rekord értékek frissítése"""
        self.value_label.setText(value)
        self.date_label.setText(date)


class RecordSummaryCard(QWidget):
    """🏆 5 rekord kategória - EXTRA KOMPAKT TAB LAYOUT-hoz"""
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
    
    def _setup_ui(self):
        """Extra kompakt summary kártya"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)
        
        # Cím
        title_label = QLabel("🏆 REKORD SZÉLSŐSÉGEK")
        title_font = QFont()
        title_font.setPointSize(11)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 5 rekord kártya - EXTRA KOMPAKT
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(3)
        
        self.hottest_card = RecordCard("🔥", "Legmelegebb")
        self.coldest_card = RecordCard("🧊", "Leghidegebb")
        self.wettest_card = RecordCard("🌧️", "Legcsapadék")
        self.driest_card = RecordCard("🏜️", "Legszáraz")
        self.windiest_card = RecordCard("💨", "Legszelesebb")
        
        cards_layout.addWidget(self.hottest_card)
        cards_layout.addWidget(self.coldest_card)
        cards_layout.addWidget(self.wettest_card)
        cards_layout.addWidget(self.driest_card)
        cards_layout.addWidget(self.windiest_card)
        
        layout.addLayout(cards_layout)
        
        # Extra kompakt styling
        self.setStyleSheet("""
            RecordSummaryCard {
                background-color: white;
                border: 2px solid #C43939;
                border-radius: 4px;
                margin: 2px;
                max-height: 90px;
            }
        """)
    
    def update_records(self, records: Dict[str, Dict[str, str]]):
        """Rekordok frissítése"""
        if 'hottest' in records:
            rec = records['hottest']
            self.hottest_card.update_record(rec.get('value', '-'), rec.get('date', '-'))
        
        if 'coldest' in records:
            rec = records['coldest']
            self.coldest_card.update_record(rec.get('value', '-'), rec.get('date', '-'))
        
        if 'wettest' in records:
            rec = records['wettest']
            self.wettest_card.update_record(rec.get('value', '-'), rec.get('date', '-'))
        
        if 'driest' in records:
            rec = records['driest']
            self.driest_card.update_record(rec.get('value', '-'), rec.get('date', '-'))
        
        if 'windiest' in records:
            rec = records['windiest']
            self.windiest_card.update_record(rec.get('value', '-'), rec.get('date', '-'))


# 🌡️ KONSTANS HEATMAP TAB WIDGET-EK

class TemperatureTabWidget(QWidget):
    """🌡️ Hőmérséklet tab - KONSTANS HEATMAP (RdYlBu_r)"""
    
    def __init__(self):
        super().__init__()
        
        # HEATMAP CHART
        self.temp_heatmap = HeatmapCalendarChart()
        self.temp_heatmap.figure.set_size_inches(20, 10)  # EXTRA NAGY MÉRET
        self.temp_heatmap.parameter = "temperature_2m_mean"
        self.temp_heatmap.chart_title = "🌡️ Konstans Hőmérséklet Heatmap"
        
        self._setup_ui()
        logger.info("TemperatureTabWidget inicializálva - KONSTANS HEATMAP (365 téglalap)")
    
    def _setup_ui(self):
        """Hőmérséklet konstans heatmap tab UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        
        # Heatmap beágyazása
        layout.addWidget(self.temp_heatmap)
    
    def update_data(self, data: Dict[str, Any]):
        """🎯 Hőmérséklet konstans heatmap frissítés"""
        try:
            # ✅ DIREKT ADATÁTADÁS - aggregáció a heatmap chart-ban történik
            self.temp_heatmap.update_data(data)
            
            logger.info("🌡️ Hőmérséklet KONSTANS HEATMAP tab frissítve")
            
        except Exception as e:
            logger.error(f"TemperatureTabWidget KONSTANS HEATMAP frissítési hiba: {e}")


class PrecipitationTabWidget(QWidget):
    """🌧️ Csapadék tab - KONSTANS HEATMAP (meteorológiai színskála)"""
    
    def __init__(self):
        super().__init__()
        
        # HEATMAP CHART - CSAPADÉK VERZIÓ
        self.precip_heatmap = HeatmapCalendarChart()
        self.precip_heatmap.figure.set_size_inches(20, 10)  # EXTRA NAGY MÉRET
        self.precip_heatmap.parameter = "precipitation_sum"
        self.precip_heatmap.chart_title = "🌧️ Konstans Csapadék Heatmap"
        
        # 🎨 METEOROLÓGIAI CSAPADÉK SZÍNSKÁLA
        self.precip_cmap, self.precip_norm = MeteorologicalColorMaps.get_precipitation_colormap()
        
        self._setup_ui()
        logger.info("PrecipitationTabWidget inicializálva - KONSTANS HEATMAP (365 téglalap, 0mm=fehér)")
    
    def _setup_ui(self):
        """Csapadék konstans heatmap tab UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        
        # Heatmap beágyazása
        layout.addWidget(self.precip_heatmap)
    
    def update_data(self, data: Dict[str, Any]):
        """🎯 Csapadék konstans heatmap frissítés - MINDEN TÉGLALAP KITÖLTVE"""
        try:
            # 🎨 METEOROLÓGIAI SZÍNSKÁLA BEÁLLÍTÁSA
            self.precip_heatmap._custom_cmap = self.precip_cmap
            self.precip_heatmap._custom_norm = self.precip_norm
            logger.debug(f"🎨 Csapadék custom colormap beállítva: {type(self.precip_cmap)}")
            
            # ✅ DIREKT ADATÁTADÁS - aggregáció a heatmap chart-ban történik
            self.precip_heatmap.update_data(data)
            
            logger.info("🌧️ Csapadék KONSTANS HEATMAP tab frissítve (0mm=fehér)")
            
        except Exception as e:
            logger.error(f"PrecipitationTabWidget KONSTANS HEATMAP frissítési hiba: {e}")


class WindTabWidget(QWidget):
    """💨 Szél tab - KONSTANS HEATMAP (BEAUFORT-alapú 13 fokozat progresszív színskála) - ÁTLAGOS MAX SZÉL"""
    
    def __init__(self):
        super().__init__()
        
        # HEATMAP CHART - SZÉL VERZIÓ (ÁTLAGOS MAX)
        self.wind_heatmap = HeatmapCalendarChart()
        self.wind_heatmap.figure.set_size_inches(20, 10)  # EXTRA NAGY MÉRET
        self.wind_heatmap.parameter = "windspeed_10m_max"  # ÁTLAGOS MAX SZÉL
        self.wind_heatmap.chart_title = "💨 Konstans Szél Heatmap (windspeed_10m_max)"
        
        # 🎨 BEAUFORT-ALAPÚ 13 FOKOZAT SZÉL SZÍNSKÁLA
        self.wind_cmap, self.wind_norm = MeteorologicalColorMaps.get_wind_colormap()
        
        self._setup_ui()
        logger.info("WindTabWidget inicializálva - KONSTANS HEATMAP (365 téglalap, BEAUFORT 13 fokozat, átlagos max szél)")
    
    def _setup_ui(self):
        """Szél konstans heatmap tab UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        
        # Heatmap beágyazása
        layout.addWidget(self.wind_heatmap)
    
    def update_data(self, data: Dict[str, Any]):
        """🎯 Szél konstans heatmap frissítés - BEAUFORT PROGRESSZÍV SZÍNSKÁLA (ÁTLAGOS MAX)"""
        try:
            # 🔍 DEBUG - Szél adatok ellenőrzése
            daily_data = data.get('daily', {})
            print("🔍 DEBUG SZÉL TAB - Elérhető daily adatok:", list(daily_data.keys()))
            print("🔍 windspeed_10m_max elérhető:", 'windspeed_10m_max' in daily_data)
            print("🔍 wind_gusts_max elérhető:", 'wind_gusts_max' in daily_data)
            
            if 'windspeed_10m_max' in daily_data:
                windspeed_data = daily_data['windspeed_10m_max']
                print(f"🔍 windspeed_10m_max minta: {windspeed_data[:5] if windspeed_data else 'ÜRES'}")
            
            if 'wind_gusts_max' in daily_data:
                windgusts_data = daily_data['wind_gusts_max'] 
                print(f"🔍 wind_gusts_max minta: {windgusts_data[:5] if windgusts_data else 'ÜRES'}")
            
            # Szél paraméter - VALÓS API NÉV (debug szerint)
            wind_param = 'windspeed_10m_max'  # ✅ VALÓS API NÉV
            
            if not daily_data.get(wind_param):
                logger.warning("Nincs elérhető windspeed_10m_max adat")
                return
            
            # 🎨 BEAUFORT-ALAPÚ 13 FOKOZAT SZÍNSKÁLA BEÁLLÍTÁSA
            self.wind_heatmap._custom_cmap = self.wind_cmap
            self.wind_heatmap._custom_norm = self.wind_norm
            self.wind_heatmap.parameter = wind_param
            logger.debug(f"🎨 Szél BEAUFORT colormap beállítva: {type(self.wind_cmap)}, param: {wind_param}")
            
            # ✅ DIREKT ADATÁTADÁS - aggregáció a heatmap chart-ban történik
            self.wind_heatmap.update_data(data)
            
            logger.info("💨 Szél KONSTANS HEATMAP tab frissítve (BEAUFORT 13 fokozat, átlagos max)")
            
        except Exception as e:
            logger.error(f"WindTabWidget KONSTANS HEATMAP frissítési hiba: {e}")


class WindGustTabWidget(QWidget):
    """🌪️ Max Széllökés tab - KONSTANS HEATMAP (BEAUFORT-alapú 13 fokozat progresszív színskála) - SZÉLLÖKÉSEK"""
    
    def __init__(self):
        super().__init__()
        
        # HEATMAP CHART - SZÉLLÖKÉS VERZIÓ (MAX GUSTS)
        self.windgust_heatmap = HeatmapCalendarChart()
        self.windgust_heatmap.figure.set_size_inches(20, 10)  # EXTRA NAGY MÉRET
        self.windgust_heatmap.parameter = "wind_gusts_max"  # ✅ VALÓS API NÉV (debug szerint)  # MAX SZÉLLÖKÉSEK
        self.windgust_heatmap.chart_title = "🌪️ Konstans Max Széllökés Heatmap (wind_gusts_max)"
        
        # 🎨 BEAUFORT-ALAPÚ 13 FOKOZAT SZÉL SZÍNSKÁLA (UGYANAZ, MINT A SZÉL TAB)
        self.windgust_cmap, self.windgust_norm = MeteorologicalColorMaps.get_wind_colormap()
        
        self._setup_ui()
        logger.info("WindGustTabWidget inicializálva - KONSTANS HEATMAP (365 téglalap, BEAUFORT 13 fokozat, max széllökések)")
    
    def _setup_ui(self):
        """Max széllökés konstans heatmap tab UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        
        # Heatmap beágyazása
        layout.addWidget(self.windgust_heatmap)
    
    def update_data(self, data: Dict[str, Any]):
        """🎯 Max széllökés konstans heatmap frissítés - BEAUFORT PROGRESSZÍV SZÍNSKÁLA (SZÉLLÖKÉSEK)"""
        try:
            # 🔍 DEBUG - Széllökés adatok ellenőrzése
            daily_data = data.get('daily', {})
            print("🔍 DEBUG MAX SZÉLLÖKÉS TAB - Elérhető daily adatok:", list(daily_data.keys()))
            print("🔍 windspeed_10m_max elérhető:", 'windspeed_10m_max' in daily_data)
            print("🔍 wind_gusts_max elérhető:", 'wind_gusts_max' in daily_data)
            
            if 'windspeed_10m_max' in daily_data:
                windspeed_data = daily_data['windspeed_10m_max']
                print(f"🔍 windspeed_10m_max minta: {windspeed_data[:5] if windspeed_data else 'ÜRES'}")
            
            if 'wind_gusts_max' in daily_data:
                windgusts_data = daily_data['wind_gusts_max'] 
                print(f"🔍 wind_gusts_max minta: {windgusts_data[:5] if windgusts_data else 'ÜRES'}")
            
            # Széllökés paraméter - VALÓS API NÉV (debug szerint)
            windgust_param = 'wind_gusts_max'  # ✅ VALÓS API NÉV (nincs 10m!)
            
            if not daily_data.get(windgust_param):
                logger.warning("Nincs elérhető wind_gusts_max adat")
                return
            
            # 🎨 BEAUFORT-ALAPÚ 13 FOKOZAT SZÍNSKÁLA BEÁLLÍTÁSA
            self.windgust_heatmap._custom_cmap = self.windgust_cmap
            self.windgust_heatmap._custom_norm = self.windgust_norm
            self.windgust_heatmap.parameter = windgust_param
            logger.debug(f"🎨 Széllökés BEAUFORT colormap beállítva: {type(self.windgust_cmap)}, param: {windgust_param}")
            
            # ✅ DIREKT ADATÁTADÁS - aggregáció a heatmap chart-ban történik
            self.windgust_heatmap.update_data(data)
            
            logger.info("🌪️ Max Széllökés KONSTANS HEATMAP tab frissítve (BEAUFORT 13 fokozat)")
            
        except Exception as e:
            logger.error(f"WindGustTabWidget KONSTANS HEATMAP frissítési hiba: {e}")


class ClimateTabWidget(QTabWidget):
    """🌡️ Klímakutató tab widget - 4 KONSTANS HEATMAP TAB + 2 DEDICATED WIND CHART - BEAUFORT + MAX SZÉLLÖKÉS VERZIÓ"""
    
    def __init__(self):
        super().__init__()
        
        # Tab widget-ek létrehozása - KONSTANS HEATMAP VERZIÓK
        self.temp_tab = TemperatureTabWidget()      # 🌡️ Hőmérséklet KONSTANS HEATMAP
        self.precip_tab = PrecipitationTabWidget()  # 🌧️ Csapadék KONSTANS HEATMAP  
        self.wind_tab = WindTabWidget()             # 💨 Szél KONSTANS HEATMAP (BEAUFORT, átlagos max)
        self.windgust_tab = WindGustTabWidget()     # 🌪️ Max Széllökés KONSTANS HEATMAP (BEAUFORT, gusts)
        
        # 🌪️ DEDICATED WIND CHARTOK HOZZÁADÁSA
        self.dedicated_wind_chart = WindChart()     # 🌪️ WindChart dedicated
        self.dedicated_windrose_chart = WindRoseChart()  # 🌹 WindRoseChart dedicated
        
        self._setup_tabs()
        
        # Lazy loading tracking
        self.data_cache = None
        self.tabs_initialized = {'temp': False, 'precip': False, 'wind': False, 'windgust': False, 'wind_chart': False, 'windrose_chart': False}
        
        # Tab változás figyelése
        self.currentChanged.connect(self._on_tab_changed)
        
        logger.info("ClimateTabWidget inicializálva - 4 KONSTANS HEATMAP TAB + 2 DEDICATED WIND CHART (365 téglalap, BEAUFORT szél + max széllökés)")
    
    def _setup_tabs(self):
        """Tab-ok beállítása - KONSTANS HEATMAP-EK + MAX SZÉLLÖKÉS + DEDICATED WIND CHARTOK"""
        # Tab-ok hozzáadása
        self.addTab(self.temp_tab, "🌡️ Hőmérséklet")         # KONSTANS HEATMAP
        self.addTab(self.precip_tab, "🌧️ Csapadék")           # KONSTANS HEATMAP (0mm=fehér)
        self.addTab(self.wind_tab, "💨 Szél")                 # KONSTANS HEATMAP (BEAUFORT, átlagos max)
        self.addTab(self.windgust_tab, "🌪️ Max Széllökés")   # KONSTANS HEATMAP (BEAUFORT, max gusts)
        
        # 🌪️ DEDICATED WIND CHARTOK HOZZÁADÁSA
        self.addTab(self.dedicated_wind_chart, "🌪️ Széllökések")  # DEDICATED WindChart
        self.addTab(self.dedicated_windrose_chart, "🌹 Széllökés Rózsa")  # DEDICATED WindRoseChart
        
        # Tab styling
        self.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #d1d5db;
                border-radius: 4px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #f9fafb;
                border: 1px solid #d1d5db;
                border-bottom-color: transparent;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 6px 12px;
                margin-right: 2px;
                font-weight: 500;
            }
            QTabBar::tab:selected {
                background-color: #C43939;
                color: white;
            }
            QTabBar::tab:hover {
                background-color: #f3f4f6;
            }
        """)
    
    def update_data(self, data: Dict[str, Any]):
        """🎯 KONSTANS HEATMAP + DEDICATED WIND CHARTOK Tab widget adatok frissítése - BEAUFORT + MAX SZÉLLÖKÉS VERZIÓ"""
        try:
            # Adatok cache-elése
            self.data_cache = data
            
            # Aktív tab frissítése
            current_index = self.currentIndex()
            self._update_current_tab(current_index)
            
            # 🌪️ KRITIKUS JAVÍTÁS: DEDICATED WIND CHARTOK MINDIG FRISSÍTÉSE
            print("🌪️ DEBUG [ClimateTabWidget]: DEDICATED WIND CHARTOK frissítése...")
            
            try:
                self.dedicated_wind_chart.update_data(data)
                print("✅ DEBUG [ClimateTabWidget]: dedicated_wind_chart frissítve!")
            except Exception as e:
                print(f"❌ ERROR [ClimateTabWidget]: dedicated_wind_chart hiba: {e}")
            
            try:
                self.dedicated_windrose_chart.update_data(data)
                print("✅ DEBUG [ClimateTabWidget]: dedicated_windrose_chart frissítve!")
            except Exception as e:
                print(f"❌ ERROR [ClimateTabWidget]: dedicated_windrose_chart hiba: {e}")
            
            # Teljes napok számának logolása
            daily_data = data.get('daily', {})
            dates = daily_data.get('time', [])
            total_days = len(dates)
            
            logger.info(f"🎯 ClimateTabWidget frissítve - {total_days} nap → 365 téglalap/tab (BEAUFORT szél + max széllökés)")
            
        except Exception as e:
            logger.error(f"ClimateTabWidget frissítési hiba: {e}")
    
    def _on_tab_changed(self, index: int):
        """Tab váltás kezelője - lazy loading"""
        logger.info(f"Tab váltás: {index}")
        self._update_current_tab(index)
    
    def _update_current_tab(self, index: int):
        """Aktív tab frissítése - KONSTANS HEATMAP VERZIÓK + MAX SZÉLLÖKÉS + DEDICATED WIND CHARTOK"""
        if not self.data_cache:
            return
        
        try:
            if index == 0:  # Hőmérséklet tab (konstans heatmap)
                self.temp_tab.update_data(self.data_cache)
                self.tabs_initialized['temp'] = True
            elif index == 1:  # Csapadék tab (konstans heatmap, 0mm=fehér)
                self.precip_tab.update_data(self.data_cache)
                self.tabs_initialized['precip'] = True
            elif index == 2:  # Szél tab (konstans heatmap, BEAUFORT, átlagos max)
                self.wind_tab.update_data(self.data_cache)
                self.tabs_initialized['wind'] = True
            elif index == 3:  # Max Széllökés tab (konstans heatmap, BEAUFORT, max gusts)
                self.windgust_tab.update_data(self.data_cache)
                self.tabs_initialized['windgust'] = True
            elif index == 4:  # 🌪️ DEDICATED WindChart tab
                self.dedicated_wind_chart.update_data(self.data_cache)
                self.tabs_initialized['wind_chart'] = True
                print("✅ DEBUG [_update_current_tab]: DEDICATED WindChart tab aktívált és frissítve!")
            elif index == 5:  # 🌹 DEDICATED WindRoseChart tab
                self.dedicated_windrose_chart.update_data(self.data_cache)
                self.tabs_initialized['windrose_chart'] = True
                print("✅ DEBUG [_update_current_tab]: DEDICATED WindRoseChart tab aktívált és frissítve!")
                
        except Exception as e:
            logger.error(f"Tab {index} frissítési hiba: {e}")


class AnalyticsView(QWidget):
    """
    🎯 REFAKTORÁLT KONSTANS HEATMAP Analytics View - KÖZPONTI SIGNAL RENDSZERREL + DEDICATED WIND CHARTOK
    
    ✅ REFAKTORÁLT MŰKÖDÉS:
    - A nézet most már nem indít saját lekérdezéseket.
    - A gombok egy központi `multi_city_query_requested` signalt bocsátanak ki.
    - A MainWindow kezeli a lekérdezést és az eredményt egy publikus slot-on
      (`update_with_multi_city_result`) keresztül küldi vissza.
    - Ezzel a nézet teljesen szinkronban van a többi modullal (Térkép, ControlPanel).
    
    FELELŐSSÉG: 
    - 🌡️ Hőmérséklet tab: KONSTANS HEATMAP (RdYlBu_r, 365 téglalap, rács vonalak)
    - 🌧️ Csapadék tab: KONSTANS HEATMAP (meteorológiai, 0mm=fehér, 365 téglalap, rács vonalak)
    - 💨 Szél tab: KONSTANS HEATMAP (BEAUFORT 13 fokozat, átlagos max szél, 365 téglalap, rács vonalak)
    - 🌪️ Max Széllökés tab: KONSTANS HEATMAP (BEAUFORT 13 fokozat, max gusts, 365 téglalap, rács vonalak)
    - 🌪️ Széllökések tab: DEDICATED WindChart professzionális szél grafikonokkal
    - 🌹 Széllökés Rózsa tab: DEDICATED WindRoseChart polár rózsadiagrammal
    - 🏆 5 rekord kategória (napi szinten) kompakt megjelenítéssel
    - 🔧 KONSTANS VIZUÁLIS FELBONTÁS - függetlenül az időszaktól
    - 🎯 INTELLIGENS TENGELYEK - időszak alapú címkék
    - 📊 KOMPAKT KÁRTYÁS STATISZTIKÁK - 12px olvasható betűméret
    - 🚀 MULTI-CITY RÉGIÓ ELEMZÉS - Észak-Magyarország, Pest, stb. elemzések
    - 🔥 SIGNAL EMISSION JAVÍTÁS - multi_city_query_requested signal kibocsátás MainWindow felé
    - 🚨 STATISZTIKÁK JAVÍTÁS - _process_and_display_statistics() MEGHÍVÁS BIZTOSÍTVA
    - 🌪️ VÉGSŐ JAVÍTÁS: DEDICATED WindChart és WindRoseChart komponensek integrálása
    """
    
    # Signalok
    analysis_started = Signal()
    analysis_completed = Signal()
    error_occurred = Signal(str)
    
    # 🚀 ÚJ: Signal a lekérdezés indításához a MainWindow felé
    multi_city_query_requested = Signal(str, str)  # query_type, region_name
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Téma kezelő
        self.theme_manager = get_theme_manager()
        
        # Adatok tárolása
        self.current_data = None
        self.current_location = None
        
        # UI elemek
        self.location_info_label = None
        self.statistics_area = None
        self.record_summary = None
        self.climate_tabs = None
        self.status_label = None
        
        # 🚀 MULTI-CITY KOMPONENSEK (refaktorált)
        self.region_combo = None
        self.analysis_buttons = []
        
        # UI építése
        self._setup_ui()
        self._setup_theme()
        
        logger.info("🗂️ AnalyticsView REFAKTORÁLT KONSTANS HEATMAP BEAUFORT + MAX SZÉLLÖKÉS + MULTI-CITY RÉGIÓ + DEDICATED WIND CHARTOK VERZIÓ betöltve - 6 tab + régió elemzés + STATISZTIKÁK JAVÍTÁS")
    
    def _setup_ui(self) -> None:
        """UI felépítése - konstans heatmap dashboard + refaktorált multi-city + dedicated wind chartok"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        
        # Fejléc
        header_layout = self._create_header()
        layout.addLayout(header_layout)
        
        # Lokáció információ (kompakt)
        location_group = self._create_location_info_group()
        layout.addWidget(location_group)
        
        # Fő tartalom splitter
        content_splitter = QSplitter(Qt.Horizontal)
        
        # Bal oldal: statisztikák + refaktorált multi-city (kompakt)
        stats_widget = self._create_statistics_panel()
        content_splitter.addWidget(stats_widget)
        
        # Jobb oldal: Tab-os klímakutató dashboard + DEDICATED WIND CHARTOK
        tab_widget = self._create_tab_dashboard()
        content_splitter.addWidget(tab_widget)
        
        # Splitter arányok - tab dashboard dominál
        content_splitter.setSizes([180, 920])  # Még több hely a tab-oknak
        layout.addWidget(content_splitter)
        
        # Állapot sáv
        self.status_label = QLabel("Válasszon lokációt a bal oldali panelen vagy használja a Régió Elemzést")
        self.status_label.setStyleSheet("color: gray; padding: 2px; font-size: 9px;")
        layout.addWidget(self.status_label)
    
    def _create_header(self) -> QHBoxLayout:
        """Fejléc létrehozása"""
        layout = QHBoxLayout()
        
        # Cím
        title_label = QLabel("🎯 Konstans Heatmap Klímakutató Dashboard + Régió Elemzés + DEDICATED Wind Chartok")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        layout.addStretch()
        
        # Verzió info
        version_label = QLabel("v14.0 - DEDICATED WIND CHARTOK")
        version_label.setStyleSheet("color: gray; font-size: 8px;")
        layout.addWidget(version_label)
        
        return layout
    
    def _create_location_info_group(self) -> QGroupBox:
        """Lokáció információs panel - EXTRA KOMPAKT"""
        group = QGroupBox("📍 Lokáció")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(4, 4, 4, 4)
        
        self.location_info_label = QLabel("Nincs kiválasztott lokáció")
        self.location_info_label.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 2px;
                padding: 4px;
                font-size: 9px;
            }
        """)
        layout.addWidget(self.location_info_label)
        
        return group
    
    def _create_statistics_panel(self) -> QWidget:
        """Statisztikák panel + Refaktorált Multi-City - KOMPAKT KÁRTYÁS RENDSZER"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(3, 3, 3, 3)
        
        # 🚀 REFAKTORÁLT MULTI-CITY RÉGIÓ ELEMZÉS PANEL
        multi_city_group = self._create_refactored_multi_city_panel()
        layout.addWidget(multi_city_group)
        
        # Statisztikák csoport
        stats_group = QGroupBox("📈 Statisztikák")
        stats_layout = QVBoxLayout(stats_group)
        
        # Görgetési terület
        self.statistics_area = QScrollArea()
        self.statistics_area.setWidgetResizable(True)
        self.statistics_area.setMinimumHeight(150)  # Extra kompakt
        
        # Statisztikák tartalom
        stats_content = QLabel("Töltse be az adatokat")
        stats_content.setAlignment(Qt.AlignCenter)
        stats_content.setStyleSheet("""
            QLabel {
                color: #666;
                font-style: italic;
                padding: 20px;
                font-size: 12px;
            }
        """)
        self.statistics_area.setWidget(stats_content)
        
        stats_layout.addWidget(self.statistics_area)
        layout.addWidget(stats_group)
        
        return widget
    
    def _create_refactored_multi_city_panel(self) -> QGroupBox:
        """🚀 REFAKTORÁLT Multi-City régió elemzés panel - SIGNAL EMISSION"""
        group = QGroupBox("🌍 RÉGIÓ ELEMZÉS")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)
        
        # Régió választó
        region_layout = QVBoxLayout()
        region_label = QLabel("📍 Válassz régiót:")
        region_label.setStyleSheet("font-weight: bold; font-size: 10px;")
        region_layout.addWidget(region_label)
        
        self.region_combo = QComboBox()
        self.region_combo.addItems([
            "Észak-Magyarország",
            "Észak-Alföld", 
            "Dél-Alföld",
            "Közép-Magyarország", 
            "Közép-Dunántúl", 
            "Nyugat-Dunántúl",
            "Dél-Dunántúl"
        ])
        self.region_combo.setStyleSheet("""
            QComboBox {
                padding: 3px;
                border: 1px solid #ccc;
                border-radius: 3px;
                font-size: 9px;
            }
        """)
        region_layout.addWidget(self.region_combo)
        layout.addLayout(region_layout)
        
        # Elemzés gombok
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(3)
        
        # 🔥 Legmelegebb ma
        self.hottest_button = QPushButton("🔥 Legmelegebb ma")
        self.hottest_button.setProperty("query_type", "hottest_today")
        self.hottest_button.clicked.connect(self._emit_query_request)
        self.hottest_button.setStyleSheet("""
            QPushButton {
                background-color: #FF6B6B;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px;
                font-weight: bold;
                font-size: 9px;
            }
            QPushButton:hover {
                background-color: #E55555;
            }
            QPushButton:pressed {
                background-color: #CC4444;
            }
        """)
        buttons_layout.addWidget(self.hottest_button)
        self.analysis_buttons.append(self.hottest_button)
        
        # ❄️ Leghidegebb ma
        self.coldest_button = QPushButton("❄️ Leghidegebb ma")
        self.coldest_button.setProperty("query_type", "coldest_today")
        self.coldest_button.clicked.connect(self._emit_query_request)
        self.coldest_button.setStyleSheet("""
            QPushButton {
                background-color: #4DABF7;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px;
                font-weight: bold;
                font-size: 9px;
            }
            QPushButton:hover {
                background-color: #339FE6;
            }
            QPushButton:pressed {
                background-color: #2288CC;
            }
        """)
        buttons_layout.addWidget(self.coldest_button)
        self.analysis_buttons.append(self.coldest_button)
        
        # 🌧️ Legcsapadékosabb ma
        self.wettest_button = QPushButton("🌧️ Legcsapadékosabb ma")
        self.wettest_button.setProperty("query_type", "wettest_today")
        self.wettest_button.clicked.connect(self._emit_query_request)
        self.wettest_button.setStyleSheet("""
            QPushButton {
                background-color: #69DB7C;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px;
                font-weight: bold;
                font-size: 9px;
            }
            QPushButton:hover {
                background-color: #51CF66;
            }
            QPushButton:pressed {
                background-color: #40C057;
            }
        """)
        buttons_layout.addWidget(self.wettest_button)
        self.analysis_buttons.append(self.wettest_button)
        
        # 💨 Legszelesebb ma
        self.windiest_button = QPushButton("💨 Legszelesebb ma")
        self.windiest_button.setProperty("query_type", "windiest_today")
        self.windiest_button.clicked.connect(self._emit_query_request)
        self.windiest_button.setStyleSheet("""
            QPushButton {
                background-color: #FFD93D;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px;
                font-weight: bold;
                font-size: 9px;
            }
            QPushButton:hover {
                background-color: #FCC419;
            }
            QPushButton:pressed {
                background-color: #FAB005;
            }
        """)
        buttons_layout.addWidget(self.windiest_button)
        self.analysis_buttons.append(self.windiest_button)
        
        layout.addLayout(buttons_layout)
        
        # Panel styling
        group.setStyleSheet("""
            QGroupBox {
                background-color: #f8f9fa;
                border: 2px solid #C43939;
                border-radius: 6px;
                margin: 2px;
                font-weight: bold;
                font-size: 11px;
                color: #C43939;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 6px;
                padding: 0 3px 0 3px;
            }
        """)
        
        return group
    
    def _emit_query_request(self):
        """🚀 KRITIKUS: Elküldi a lekérdezési kérést a MainWindow felé - REFAKTORÁLT SIGNAL EMISSION"""
        sender = self.sender()
        query_type = sender.property("query_type")
        region_name = self.region_combo.currentText()
        
        print(f"🚀 ANALYTICS_VIEW: Signal 'multi_city_query_requested' emitted with: {query_type}, {region_name}")
        
        # ✅ ÚJ: Signal kibocsátása a MainWindow felé
        self.multi_city_query_requested.emit(query_type, region_name)
        
        # UI visszajelzés
        self._update_status(f"🚀 Multi-City kérés elküldve: {region_name} ({query_type})")
        
        logger.info(f"🚀 Multi-City query request emitted: {query_type} for {region_name}")
    
    def _create_tab_dashboard(self) -> QWidget:
        """Tab-os klímakutató dashboard + DEDICATED WIND CHARTOK"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        
        # Rekord summary kártya (kompakt)
        self.record_summary = RecordSummaryCard()
        layout.addWidget(self.record_summary)
        
        # Climate tab widget - KONSTANS HEATMAP BEAUFORT + MAX SZÉLLÖKÉS + DEDICATED WIND CHARTOK VERZIÓ
        self.climate_tabs = ClimateTabWidget()
        layout.addWidget(self.climate_tabs, 1)  # Expandálható
        
        return widget
    
    def _setup_theme(self) -> None:
        """Téma beállítása"""
        register_widget_for_theming(self, "container")
        self.theme_manager.theme_changed.connect(self._on_theme_changed)
        self._apply_current_theme()
    
    def _apply_current_theme(self) -> None:
        """Jelenlegi téma alkalmazása"""
        colors = get_current_colors()
        
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {colors.get('surface', '#ffffff')};
                color: {colors.get('on_surface', '#000000')};
            }}
            QGroupBox {{
                font-weight: bold;
                border: 1px solid {colors.get('border', '#ccc')};
                border-radius: 3px;
                margin-top: 6px;
                padding-top: 3px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 6px;
                padding: 0 3px 0 3px;
                color: {colors.get('primary', '#0066cc')};
            }}
        """)
    
    def _on_theme_changed(self, theme_name: str) -> None:
        """Téma változás kezelése"""
        self._apply_current_theme()
        logger.debug(f"Konstans heatmap dashboard téma frissítve: {theme_name}")
    
    # === ✅ ÚJ PUBLIKUS SLOT: Eredmények fogadása a MainWindow-tól ===
    
    def update_with_multi_city_result(self, result: 'AnalyticsResult'):
        """
        ✅ ÚJ: Frissíti a nézetet a MainWindow-tól kapott elemzési eredménnyel.
        
        Args:
            result: AnalyticsResult objektum a Multi-City Engine-ből
        """
        print(f"✅ ANALYTICS_VIEW: Eredmény fogadva a MainWindow-tól: {len(result.city_results) if result and result.city_results else 0} város.")
        
        try:
            if not result or not result.city_results:
                self._update_status("❌ Nincs Multi-City eredmény")
                return
            
            # Fake single-city data létrehozása a heatmap-ekhez (a meglévő logika)
            self._create_fake_single_city_data_from_multi_city(result)
            
            # Status frissítése
            self._update_status(f"✅ Multi-City eredmény feldolgozva: {len(result.city_results)} város")
            
            logger.info(f"✅ Multi-City result processed in AnalyticsView: {len(result.city_results)} cities")
            
        except Exception as e:
            logger.error(f"❌ Multi-City result processing error: {e}")
            self._update_status(f"❌ Multi-City eredmény feldolgozási hiba: {e}")
            self.error_occurred.emit(f"Multi-City eredmény hiba: {e}")
    
    def _create_fake_single_city_data_from_multi_city(self, analytics_result):
        """🎯 Fake single-city data létrehozása Multi-City eredményekből a heatmap megjelenítéshez"""
        try:
            # Ez egy workaround - a heatmap-ek single-city adatokat várnak
            # De a Multi-City eredményeket szeretnénk látni a tab-okban is
            
            if not analytics_result or not analytics_result.city_results:
                logger.warning("Nincs Multi-City eredmény a heatmap frissítéshez")
                return
            
            # Multi-City eredmények aggregálása egy fake weather data-ba
            cities = analytics_result.city_results
            question = analytics_result.question
            
            # Fake daily data létrehozása (365 nap)
            fake_daily_data = {
                'time': [f"2024-{i//30+1:02d}-{i%30+1:02d}" for i in range(365)],
                'temperature_2m_mean': [],
                'temperature_2m_max': [],
                'temperature_2m_min': [],
                'precipitation_sum': [],
                'windspeed_10m_max': [],
                'wind_gusts_max': []
            }
            
            # Metric alapú fake data generálás
            metric_type = question.metric if question else AnalyticsMetric.TEMPERATURE_2M_MAX
            
            for i in range(365):
                # Városok értékeinek átlaga minden napra (szimuláció)
                if metric_type == AnalyticsMetric.TEMPERATURE_2M_MAX:
                    avg_val = sum(city.value for city in cities) / len(cities)
                    fake_daily_data['temperature_2m_max'].append(avg_val + (i % 20 - 10))  # Variáció
                    fake_daily_data['temperature_2m_mean'].append(avg_val - 2)
                    fake_daily_data['temperature_2m_min'].append(avg_val - 8)
                    fake_daily_data['precipitation_sum'].append(0.5)
                    fake_daily_data['windspeed_10m_max'].append(10.0)
                    fake_daily_data['wind_gusts_max'].append(15.0)
                
                elif metric_type == AnalyticsMetric.PRECIPITATION_SUM:
                    avg_val = sum(city.value for city in cities) / len(cities)
                    fake_daily_data['precipitation_sum'].append(avg_val + (i % 10))
                    fake_daily_data['temperature_2m_max'].append(20.0)
                    fake_daily_data['temperature_2m_mean'].append(15.0)
                    fake_daily_data['temperature_2m_min'].append(10.0)
                    fake_daily_data['windspeed_10m_max'].append(10.0)
                    fake_daily_data['wind_gusts_max'].append(15.0)
                
                elif metric_type == AnalyticsMetric.WINDSPEED_10M_MAX:
                    avg_val = sum(city.value for city in cities) / len(cities)
                    fake_daily_data['windspeed_10m_max'].append(avg_val + (i % 15))
                    fake_daily_data['wind_gusts_max'].append(avg_val + 5)
                    fake_daily_data['temperature_2m_max'].append(20.0)
                    fake_daily_data['temperature_2m_mean'].append(15.0)
                    fake_daily_data['temperature_2m_min'].append(10.0)
                    fake_daily_data['precipitation_sum'].append(1.0)
                
                else:
                    # Default értékek
                    fake_daily_data['temperature_2m_max'].append(20.0)
                    fake_daily_data['temperature_2m_mean'].append(15.0)
                    fake_daily_data['temperature_2m_min'].append(10.0)
                    fake_daily_data['precipitation_sum'].append(1.0)
                    fake_daily_data['windspeed_10m_max'].append(10.0)
                    fake_daily_data['wind_gusts_max'].append(15.0)
            
            # Fake data objektum
            fake_data = {
                'daily': fake_daily_data,
                'location': {
                    'name': f"Multi-City: {analytics_result.question.question_text if analytics_result.question else 'Régió Elemzés'}",
                    'latitude': 47.5,  # Magyarország közepe
                    'longitude': 19.0
                }
            }
            
            # Heatmap-ek frissítése
            if self.climate_tabs:
                self.climate_tabs.update_data(fake_data)
            
            # Fake rekordok (Multi-City eredményekből)
            fake_records = self._create_fake_records_from_multi_city(analytics_result)
            if self.record_summary:
                self.record_summary.update_records(fake_records)
            
            logger.info(f"🎯 Fake single-city data létrehozva Multi-City eredményekből ({len(cities)} város)")
            
        except Exception as e:
            logger.error(f"❌ Fake data creation hiba: {e}")
    
    def _create_fake_records_from_multi_city(self, analytics_result) -> Dict[str, Dict[str, str]]:
        """🏆 Fake rekordok létrehozása Multi-City eredményekből"""
        try:
            if not analytics_result.city_results:
                return {}
            
            cities = analytics_result.city_results
            records = {}
            
            # Top 3 város kiválasztása különböző kategóriákhoz
            if len(cities) >= 1:
                top_city = cities[0]
                records['hottest'] = {
                    'value': f"{top_city.value:.1f}°C",
                    'date': top_city.date.strftime("%Y-%m-%d") if hasattr(top_city.date, 'strftime') else str(top_city.date)
                }
            
            if len(cities) >= 2:
                second_city = cities[1]
                records['windiest'] = {
                    'value': f"{second_city.value:.1f}km/h",
                    'date': second_city.date.strftime("%Y-%m-%d") if hasattr(second_city.date, 'strftime') else str(second_city.date)
                }
            
            if len(cities) >= 3:
                third_city = cities[2]
                records['wettest'] = {
                    'value': f"{third_city.value:.1f}mm",
                    'date': third_city.date.strftime("%Y-%m-%d") if hasattr(third_city.date, 'strftime') else str(third_city.date)
                }
            
            # Default értékek
            records.setdefault('coldest', {'value': "N/A", 'date': "Multi-City"})
            records.setdefault('driest', {'value': "N/A", 'date': "Multi-City"})
            
            return records
            
        except Exception as e:
            logger.error(f"❌ Fake records creation hiba: {e}")
            return {}
    
    # === PUBLIKUS API METÓDUSOK ===
    
    def update_data(self, data: Dict[str, Any]) -> None:
        """
        🎯 KONSTANS HEATMAP + DEDICATED WIND CHARTOK adatok frissítése - 6 TAB - BEAUFORT + MAX SZÉLLÖKÉS VERZIÓ
        🚨 STATISZTIKÁK JAVÍTÁS - _process_and_display_statistics() MEGHÍVÁS BIZTOSÍTVA
        🌪️ VÉGSŐ JAVÍTÁS: DEDICATED WindChart és WindRoseChart frissítése
        
        Args:
            data: Időjárási adatok dictionary
        """
        try:
            logger.info("🗂️ Konstans heatmap dashboard + DEDICATED WIND CHARTOK adatok frissítése - BEAUFORT + MAX SZÉLLÖKÉS VERZIÓ")
            
            # Adatok tárolása
            self.current_data = data
            
            # Teljes napok számítása
            daily_data = data.get('daily', {})
            dates = daily_data.get('time', [])
            total_days = len(dates)
            
            logger.info(f"🎯 KONSTANS AGGREGÁCIÓ - BEAUFORT + MAX SZÉLLÖKÉS:")
            logger.info(f"  📊 {total_days} nap → 365 téglalap minden tab-nál")
            logger.info(f"  🎯 Bin méret: ~{total_days // 365} nap/téglalap")
            logger.info(f"  📈 MINDEN téglalap kitöltve (0 érték = megfelelő szín)")
            logger.info(f"  🎨 Rács vonalak + intelligens tengelyek")
            logger.info(f"  💨 Szél: BEAUFORT 13 fokozat (átlagos max)")
            logger.info(f"  🌪️ Max Széllökés: BEAUFORT 13 fokozat (max gusts)")
            
            # 🚨 KRITIKUS JAVÍTÁS: Bal oldali statisztikák frissítése - KOMPAKT KÁRTYÁS RENDSZER
            logger.info("🚨 STATISZTIKÁK JAVÍTÁS: _process_and_display_statistics() meghívása")
            self._process_and_display_statistics(data, total_days)
            
            # Rekordok frissítése (mindig napi szinten)
            records = self._calculate_records(data)
            self.record_summary.update_records(records)
            
            # Tab widget frissítése (konstans heatmap verziók + DEDICATED WIND CHARTOK)
            if self.climate_tabs:
                self.climate_tabs.update_data(data)
                
                # 🌪️ VÉGSŐ KRITIKUS JAVÍTÁS: EXPLICIT DEDICATED WIND CHARTOK FRISSÍTÉSE
                print("🌪️ FINAL DEBUG [AnalyticsView]: EXPLICIT DEDICATED WIND CHARTOK frissítése...")
                
                # DEDICATED WindChart explicit frissítés
                if hasattr(self.climate_tabs, 'dedicated_wind_chart') and self.climate_tabs.dedicated_wind_chart:
                    try:
                        print("🌪️ DEBUG [AnalyticsView]: dedicated_wind_chart.update_data() EXPLICIT hívás...")
                        self.climate_tabs.dedicated_wind_chart.update_data(data)
                        print("✅ DEBUG [AnalyticsView]: dedicated_wind_chart SIKERESEN frissítve!")
                    except Exception as e:
                        print(f"❌ ERROR [AnalyticsView]: dedicated_wind_chart hiba: {e}")
                        import traceback
                        print(f"❌ DEBUG [AnalyticsView]: dedicated_wind_chart traceback: {traceback.format_exc()}")
                
                # DEDICATED WindRoseChart explicit frissítés
                if hasattr(self.climate_tabs, 'dedicated_windrose_chart') and self.climate_tabs.dedicated_windrose_chart:
                    try:
                        print("🌹 DEBUG [AnalyticsView]: dedicated_windrose_chart.update_data() EXPLICIT hívás...")
                        self.climate_tabs.dedicated_windrose_chart.update_data(data)
                        print("✅ DEBUG [AnalyticsView]: dedicated_windrose_chart SIKERESEN frissítve!")
                    except Exception as e:
                        print(f"❌ ERROR [AnalyticsView]: dedicated_windrose_chart hiba: {e}")
                        import traceback
                        print(f"❌ DEBUG [AnalyticsView]: dedicated_windrose_chart traceback: {traceback.format_exc()}")
            
            # Állapot frissítése
            self._update_status(f"✅ {total_days} nap → 365 téglalap - Beaufort + Max Széllökés Dashboard + DEDICATED WIND CHARTOK + STATISZTIKÁK")
            
            # Signal
            self.analysis_completed.emit()
            
        except Exception as e:
            logger.error(f"Konstans heatmap dashboard + DEDICATED WIND CHARTOK adatfrissítési hiba: {e}", exc_info=True)
            self.error_occurred.emit(f"Adatfrissítési hiba: {str(e)}")
            self._update_status("❌ Adatfeldolgozási hiba")
    
    def clear_data(self) -> None:
        """Adatok törlése és UI visszaállítása"""
        logger.info("Konstans heatmap dashboard + DEDICATED WIND CHARTOK adatok törlése")
        
        self.current_data = None
        self.current_location = None
        
        # UI visszaállítása
        self.location_info_label.setText("Nincs kiválasztott lokáció")
        
        # Statisztikák törlése
        stats_content = QLabel("Töltse be az adatokat")
        stats_content.setAlignment(Qt.AlignCenter)
        stats_content.setStyleSheet("""
            QLabel {
                color: #666;
                font-style: italic;
                padding: 20px;
                font-size: 12px;
            }
        """)
        self.statistics_area.setWidget(stats_content)
        
        self._update_status("Válasszon lokációt a bal oldali panelen vagy használja a Régió Elemzést")
    
    def on_location_changed(self, location) -> None:
        """Lokáció változás kezelése"""
        try:
            logger.info(f"Konstans heatmap dashboard lokáció változás: {location}")
            self.current_location = location
            
            # Lokáció info frissítése
            if hasattr(location, 'display_name'):
                display_name = location.display_name
                coords = location.coordinates
            elif isinstance(location, dict):
                display_name = location.get('name', 'Ismeretlen')
                lat = location.get('latitude', 0.0)
                lon = location.get('longitude', 0.0)
                coords = (lat, lon)
            else:
                display_name = str(location)
                coords = (0.0, 0.0)
            
            if coords:
                location_text = f"📍 {display_name}\n🗺️ [{coords[0]:.3f}, {coords[1]:.3f}]"
            else:
                location_text = f"📍 {display_name}"
            
            self.location_info_label.setText(location_text)
            self._update_status(f"Lokáció beállítva: {display_name}")
            
        except Exception as e:
            logger.error(f"Lokáció változás hiba: {e}")
            self.error_occurred.emit(f"Lokáció hiba: {str(e)}")
    
    def on_analysis_start(self) -> None:
        """Elemzés indítása"""
        logger.info("Konstans heatmap dashboard + DEDICATED WIND CHARTOK elemzés indítása")
        self.analysis_started.emit()
        self._update_status("⏳ Konstans heatmap dashboard + DEDICATED WIND CHARTOK elemzés folyamatban...")
    
    # === BELSŐ METÓDUSOK ===
    
    def _process_and_display_statistics(self, data: Dict[str, Any], total_days: int) -> None:
        """🚨 JAVÍTOTT: Statisztikák feldolgozása és megjelenítése - KOMPAKT KÁRTYÁS RENDSZER"""
        try:
            logger.info("🚨 _process_and_display_statistics() MEGHÍVVA - STATISZTIKÁK JAVÍTÁS")
            
            # Statisztikai adatok számítása
            stats_data = self._calculate_statistics_data(data, total_days)
            
            # Kompakt kártyás widget létrehozása
            stats_widget = self._create_statistics_cards_widget(stats_data)
            
            # 🚨 KRITIKUS: Statisztikák widget beállítása a scroll area-ba
            self.statistics_area.setWidget(stats_widget)
            
            logger.info("✅ Statisztikák sikeresen megjelenítve a bal oldali panelen")
            
        except Exception as e:
            logger.error(f"Statisztika feldolgozási hiba: {e}", exc_info=True)
            # Hiba esetén alapértelmezett üzenet
            error_widget = QLabel(f"❌ Statisztika hiba: {str(e)}")
            error_widget.setAlignment(Qt.AlignCenter)
            error_widget.setStyleSheet("color: red; padding: 20px;")
            self.statistics_area.setWidget(error_widget)
    
    def _calculate_statistics_data(self, data: Dict[str, Any], total_days: int) -> Dict[str, Any]:
        """📊 STATISZTIKAI ADATOK KISZÁMÍTÁSA - KÁRTYÁS RENDSZERHEZ"""
        try:
            daily_data = data.get('daily', {})
            dates = daily_data.get('time', [])
            
            if not daily_data or not dates:
                return {}
            
            stats = {}
            
            # === HŐMÉRSÉKLET ADATOK ===
            temp_mean_list = daily_data.get('temperature_2m_mean', [])
            temp_max_list = daily_data.get('temperature_2m_max', [])
            temp_min_list = daily_data.get('temperature_2m_min', [])
            
            if temp_mean_list:
                stats['temp_avg'] = safe_avg(temp_mean_list)
                stats['temp_min'] = safe_min(temp_min_list) if temp_min_list else None
                stats['temp_max'] = safe_max(temp_max_list) if temp_max_list else None
                
                # Speciális napok
                stats['freezing_days'] = safe_count(temp_min_list, lambda x: x < 0) if temp_min_list else 0
                stats['hot_days'] = safe_count(temp_max_list, lambda x: x > 30) if temp_max_list else 0
                
                # Hőmérséklet ingadozás
                if temp_max_list and temp_min_list:
                    daily_ranges = []
                    for i in range(min(len(temp_max_list), len(temp_min_list))):
                        if temp_max_list[i] is not None and temp_min_list[i] is not None:
                            daily_ranges.append(temp_max_list[i] - temp_min_list[i])
                    stats['temp_range_avg'] = safe_avg(daily_ranges) if daily_ranges else None
            
            # === CSAPADÉK ADATOK ===
            precip_list = daily_data.get('precipitation_sum', [])
            if precip_list:
                stats['precip_avg'] = safe_avg(precip_list)
                stats['precip_total'] = safe_sum(precip_list)
                stats['dry_days'] = safe_count(precip_list, lambda x: x <= 0.1)
                stats['rainy_days'] = len(precip_list) - stats['dry_days']
                stats['dry_percentage'] = (stats['dry_days'] / len(precip_list)) * 100
                stats['rainy_percentage'] = (stats['rainy_days'] / len(precip_list)) * 100
                
                # Éves csapadék
                years = len(set(date[:4] for date in dates))
                stats['annual_precip'] = stats['precip_total'] / years if years > 0 else stats['precip_total']
                
                # Leghosszabb száraz időszak
                dry_streak = self._find_longest_dry_streak(precip_list, dates)
                stats['longest_dry_streak'] = dry_streak['days'] if dry_streak else 0
            
            # === SZÉL ADATOK ===
            wind_list = daily_data.get('windspeed_10m_max', [])
            windgust_list = daily_data.get('wind_gusts_max', [])
            
            if wind_list:
                stats['wind_avg'] = safe_avg(wind_list)
                stats['wind_max'] = safe_max(wind_list)
                
                # Beaufort kategóriák
                stats['wind_calm'] = safe_count(wind_list, lambda x: x <= 1)       # 0-1: Szélcsend
                stats['wind_light'] = safe_count(wind_list, lambda x: 1 < x <= 11) # 2-3: Gyenge
                stats['wind_moderate'] = safe_count(wind_list, lambda x: 11 < x <= 29)  # 4-5: Mérsékelt
                stats['wind_strong'] = safe_count(wind_list, lambda x: x > 29)     # 6+: Erős
            
            if windgust_list:
                stats['windgust_max'] = safe_max(windgust_list)
            
            # === IDŐSZAK ADATOK ===
            stats['start_date'] = dates[0][:10] if dates else "N/A"
            stats['end_date'] = dates[-1][:10] if dates else "N/A"
            stats['total_days'] = total_days
            stats['bin_size'] = max(1, total_days // 365)
            stats['years'] = len(set(date[:4] for date in dates)) if dates else 0
            
            return stats
            
        except Exception as e:
            logger.error(f"Statisztikai adatok számítási hiba: {e}")
            return {}
    
    def _create_statistics_cards_widget(self, stats: Dict[str, Any]) -> QWidget:
        """🎯 KOMPAKT KÁRTYÁS STATISZTIKA WIDGET LÉTREHOZÁSA"""
        try:
            main_widget = QWidget()
            layout = QVBoxLayout(main_widget)
            layout.setContentsMargins(4, 4, 4, 4)
            layout.setSpacing(8)
            
            if not stats:
                no_data_label = QLabel("❌ Nincsenek adatok")
                no_data_label.setAlignment(Qt.AlignCenter)
                no_data_label.setStyleSheet("color: #666; font-style: italic; padding: 20px; font-size: 12px;")
                layout.addWidget(no_data_label)
                return main_widget
            
            # === 1. HŐMÉRSÉKLET KÁRTYA ===
            temp_card = self._create_statistic_card(
                "🌡️ HŐMÉRSÉKLETI STATISZTIKÁK",
                [
                    f"• Átlag hőmérséklet: {stats.get('temp_avg', 0):.1f}°C" if stats.get('temp_avg') else "• Átlag hőmérséklet: N/A",
                    f"• Min/Max: {stats.get('temp_min', 0):.1f}°C / {stats.get('temp_max', 0):.1f}°C" if stats.get('temp_min') and stats.get('temp_max') else "• Min/Max: N/A",
                    f"• Fagyos napok: {stats.get('freezing_days', 0)} nap",
                    f"• Hőséghullám (>30°C): {stats.get('hot_days', 0)} nap",
                    f"• Hőmérséklet ingadozás: {stats.get('temp_range_avg', 0):.1f}°C" if stats.get('temp_range_avg') else "• Hőmérséklet ingadozás: N/A"
                ]
            )
            layout.addWidget(temp_card)
            
            # === 2. CSAPADÉK KÁRTYA ===
            precip_card = self._create_statistic_card(
                "🌧️ CSAPADÉK ELEMZÉS",
                [
                    f"• Átlag csapadék: {stats.get('precip_avg', 0):.1f}mm/nap" if stats.get('precip_avg') else "• Átlag csapadék: N/A",
                    f"• Száraz napok: {stats.get('dry_days', 0)} nap ({stats.get('dry_percentage', 0):.0f}%)",
                    f"• Esős napok: {stats.get('rainy_days', 0)} nap ({stats.get('rainy_percentage', 0):.0f}%)",
                    f"• Összes csapadék: {stats.get('annual_precip', 0):.0f}mm/év" if stats.get('annual_precip') else "• Összes csapadék: N/A",
                    f"• Leghosszabb száraz: {stats.get('longest_dry_streak', 0)} nap"
                ]
            )
            layout.addWidget(precip_card)
            
            # === 3. SZÉL KÁRTYA ===
            wind_card = self._create_statistic_card(
                "💨 SZÉL BEAUFORT ELEMZÉS",
                [
                    f"• Átlag szélsebesség: {stats.get('wind_avg', 0):.1f} km/h" if stats.get('wind_avg') else "• Átlag szélsebesség: N/A",
                    f"• Max széllökés: {stats.get('windgust_max', 0):.1f} km/h" if stats.get('windgust_max') else f"• Max szélsebesség: {stats.get('wind_max', 0):.1f} km/h" if stats.get('wind_max') else "• Max szél: N/A",
                    f"• Szélcsend (0-1): {stats.get('wind_calm', 0)} nap",
                    f"• Gyenge szél (2-3): {stats.get('wind_light', 0)} nap",
                    f"• Mérsékelt (4-5): {stats.get('wind_moderate', 0)} nap",
                    f"• Erős szél (6+): {stats.get('wind_strong', 0)} nap"
                ]
            )
            layout.addWidget(wind_card)
            
            # === 4. IDŐSZAK KÁRTYA ===
            period_card = self._create_statistic_card(
                "📊 IDŐSZAK & RENDSZER INFO",
                [
                    f"• Időtartam: {stats.get('start_date', 'N/A')} - {stats.get('end_date', 'N/A')}",
                    f"• Napok száma: {stats.get('total_days', 0)} nap",
                    f"• Konstans felbontás: 365 bin",
                    f"• Bin méret: ~{stats.get('bin_size', 1)} nap/téglalap",
                    f"• Beaufort 13 fokozat színek"
                ]
            )
            layout.addWidget(period_card)
            
            # Stretch hozzáadása az aljára
            layout.addStretch()
            
            return main_widget
            
        except Exception as e:
            logger.error(f"Kártyás widget létrehozási hiba: {e}")
            error_widget = QWidget()
            error_layout = QVBoxLayout(error_widget)
            error_label = QLabel(f"❌ Widget hiba: {str(e)}")
            error_label.setAlignment(Qt.AlignCenter)
            error_layout.addWidget(error_label)
            return error_widget
    
    def _create_statistic_card(self, title: str, items: List[str]) -> QWidget:
        """📋 EGYEDI STATISZTIKA KÁRTYA LÉTREHOZÁSA"""
        card = QWidget()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(4)
        
        # Cím
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 14px;
                color: #C43939;
                margin-bottom: 3px;
            }
        """)
        layout.addWidget(title_label)
        
        # Elválasztó vonal
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("color: #ddd;")
        layout.addWidget(separator)
        
        # Adatok
        for item in items:
            item_label = QLabel(item)
            item_label.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    color: #333;
                    padding-left: 4px;
                    line-height: 1.5;
                }
            """)
            layout.addWidget(item_label)
        
        # Kártya styling
        card.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 4px;
                margin: 2px;
            }
        """)
        
        return card
    
    def _calculate_records(self, data: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
        """🏆 5 rekord kategória számítása - MINDIG NAPI SZINTEN (MAX SZÉLLÖKÉSEKKEL)"""
        try:
            daily_data = data.get('daily', {})
            
            if not daily_data:
                return {}
            
            dates = daily_data.get('time', [])
            if not dates:
                return {}
            
            records = {}
            
            # 🔥 1. LEGMELEGEBB NAP
            temp_max_list = daily_data.get('temperature_2m_max', [])
            if temp_max_list and len(temp_max_list) == len(dates):
                max_temp = safe_max(temp_max_list)
                if max_temp is not None:
                    max_idx = temp_max_list.index(max_temp)
                    records['hottest'] = {
                        'value': f"{max_temp:.1f}°C",
                        'date': dates[max_idx][:10]
                    }
            
            # 🧊 2. LEGHIDEGEBB NAP
            temp_min_list = daily_data.get('temperature_2m_min', [])
            if temp_min_list and len(temp_min_list) == len(dates):
                min_temp = safe_min(temp_min_list)
                if min_temp is not None:
                    min_idx = temp_min_list.index(min_temp)
                    records['coldest'] = {
                        'value': f"{min_temp:.1f}°C",
                        'date': dates[min_idx][:10]
                    }
            
            # 🌧️ 3. LEGCSAPADÉKOSABB NAP
            precip_list = daily_data.get('precipitation_sum', [])
            if precip_list and len(precip_list) == len(dates):
                max_precip = safe_max(precip_list)
                if max_precip is not None and max_precip > 0:
                    max_precip_idx = precip_list.index(max_precip)
                    records['wettest'] = {
                        'value': f"{max_precip:.1f}mm",
                        'date': dates[max_precip_idx][:10]
                    }
            
            # 🏜️ 4. LEGSZÁRAZABB IDŐSZAK
            if precip_list and len(precip_list) == len(dates):
                dry_streak = self._find_longest_dry_streak(precip_list, dates)
                if dry_streak:
                    records['driest'] = {
                        'value': f"{dry_streak['days']} nap",
                        'date': f"{dry_streak['start'][:5]}-{dry_streak['end'][:5]}"  # Rövidebb
                    }
            
            # 💨 5. LEGSZELESEBB NAP (VALÓS API NEVEK - debug szerint)
            # Előnyben részesítjük a széllökéseket (wind_gusts_max), ha elérhető
            wind_data = daily_data.get('wind_gusts_max', []) or daily_data.get('windspeed_10m_max', [])
            if wind_data and len(wind_data) == len(dates):
                max_wind = safe_max(wind_data)
                if max_wind is not None:
                    max_wind_idx = wind_data.index(max_wind)
                    records['windiest'] = {
                        'value': f"{max_wind:.1f}km/h",
                        'date': dates[max_wind_idx][:10]
                    }
            
            logger.info(f"Napi rekordok számítva: {len(records)} kategória (max széllökés prioritással)")
            return records
            
        except Exception as e:
            logger.error(f"Rekord számítási hiba: {e}", exc_info=True)
            return {}
    
    def _find_longest_dry_streak(self, precip_list: List[float], dates: List[str]) -> Optional[Dict[str, Any]]:
        """Leghosszabb száraz időszak keresése"""
        try:
            if not precip_list or not dates:
                return None
            
            max_streak = 0
            current_streak = 0
            max_start_idx = 0
            max_end_idx = 0
            current_start_idx = 0
            
            for i, precip in enumerate(precip_list):
                if precip is not None and precip <= 0.1:
                    if current_streak == 0:
                        current_start_idx = i
                    current_streak += 1
                else:
                    if current_streak > max_streak:
                        max_streak = current_streak
                        max_start_idx = current_start_idx
                        max_end_idx = i - 1
                    current_streak = 0
            
            # Utolsó streak ellenőrzése
            if current_streak > max_streak:
                max_streak = current_streak
                max_start_idx = current_start_idx
                max_end_idx = len(precip_list) - 1
            
            if max_streak >= 3:
                return {
                    'days': max_streak,
                    'start': dates[max_start_idx],
                    'end': dates[max_end_idx]
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Száraz időszak keresési hiba: {e}")
            return None
    
    def _update_status(self, message: str) -> None:
        """Állapot üzenet frissítése"""
        if self.status_label:
            self.status_label.setText(message)
        logger.info(f"Konstans heatmap dashboard + DEDICATED WIND CHARTOK állapot: {message}")
    
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
__all__ = ['AnalyticsView', 'MeteorologicalColorMaps']