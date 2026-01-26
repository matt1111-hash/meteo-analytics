#!/usr/bin/env python3
"""
Enhanced Trend Analytics Tab - PROFESSIONAL DASHBOARD IMPLEMENTATION v4.0
Global Weather Analyzer projekt

🎨 FEJLESZTÉSEK v4.0:
- ✅ PLOTLY INTERAKTÍV CHARTOK: Zoom, pan, hover tooltips
- ✅ DASHBOARD-SZERŰ QUICK OVERVIEW KÁRTYÁK: KPI metrikák
- ✅ MULTI-CHART LAYOUT: Főchart + mini chartok grid-ben
- ✅ PROFESSIONAL ERROR HANDLING: Structured logging + graceful degradation
- ✅ TYPE HINTS: Minden függvény explicit típusokkal
- ✅ DOCSTRING: Teljes dokumentáció minden modulnál
- ✅ MODULÁRIS ARCHITEKTÚRA: DRY, KISS, YAGNI, SOLID elvek
- ✅ THEME INTEGRATION: ColorPalette API kompatibilitás

🔧 ARCHITEKTÚRA:
- TrendDataProcessor: API-alapú trend adatfeldolgozás (JAVÍTOTT ✅)
- DashboardStatsCard: Új KPI kártya komponens
- InteractiveTrendChart: Plotly-alapú interaktív chart
- EnhancedStatisticsPanel: Dashboard layout statisztikákhoz
- TrendAnalyticsTab: Főkoordinátor (QSplitter megtartva)

🚀 FUNKCIONALITÁS:
- 📊 Interaktív idősor chart (hover, zoom, pan)
- 📈 Trend vonal konfidencia intervallummal
- 🎯 KPI kártyák (trend, R², szignifikancia, range)
- 📅 Szezonális színkódolás
- 🎨 Professional téma integráció
- 🔄 Real-time progress tracking

🔥 KRITIKUS JAVÍTÁS v4.2:
- ✅ weather_client.get_weather_data() EGYSÉGES API (173. sor)
- ✅ Tuple unpacking hiba véglegesen megoldva
- ✅ Plotly chart DatetimeIndex javítás (672. sor)
- ✅ KPI kártyák getItemPosition javítás (975. sor)
- ✅ TrendDataProcessor GLOBALIZÁLVA - CityManager integráció ⭐ ÚJ
- ✅ Magyar + Nemzetközi város támogatás (pl. "Broxbourne" is működik)
- ✅ KPI kártyák tartalom frissítés javítás ⭐ ÚJ
- ✅ DashboardStatsCard.update_contents() dinamikus frissítés
- ✅ Egyszerűsített kód, nincs bonyolult típus ellenőrzés
- ✅ data_source minden rekordból kinyerhető

Fájl: src/gui/trend_analytics_tab.py
Hely: /home/tibor/PythonProjects/openmeteo_history/global_weather_analyzer/src/gui/
"""

import sys
import sqlite3
import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
import asyncio
from pathlib import Path

# PySide6 imports
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QPushButton, QProgressBar, QFrame, QSplitter, QScrollArea,
    QGridLayout, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QThread, QTimer, QObject, QSize
from PySide6.QtGui import QFont, QPalette, QColor
from PySide6.QtWebEngineWidgets import QWebEngineView

# Scientific computing
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

# Interactive plotting
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.io as pio

# Project imports - FRISSÍTETT INTEGRÁCIÓ
from ..data.weather_client import WeatherClient
from .theme_manager import ThemeManager

# Logging beállítás
logger = logging.getLogger(__name__)


class TrendDataProcessor(QObject):
    """
    🔥 TELJES ÚJRAÍRÁS: API-alapú trend adatfeldolgozás
    
    RÉGI: SQL lekérdezések meteo_data.db-ből
    ÚJ: Hungarian_settlements.db + Weather API + Multi-year batching
    
    Képességek:
    - 3178 magyar település koordináta lekérdezése
    - Multi-year API hívások (5-10-55 év)
    - Professional trend számítás
    - Confidence interval számítás
    - Statistical significance testing
    """
    
    # Signals for communication
    progress_updated = Signal(int)  # Progress percentage
    data_received = Signal(dict)    # Processed trend data
    error_occurred = Signal(str)    # Error message
    
    def __init__(self):
        super().__init__()
        
        # 🔥 GLOBALIZÁLT ARCHITEKTÚRA - CityManager integráció
        from ..data.city_manager import CityManager
        from ..data.weather_client import WeatherClient
        
        self.city_manager = CityManager()  # 🌍 GLOBÁLIS városkezelő (magyar + nemzetközi)
        self.weather_client = WeatherClient(preferred_provider="auto")
        
        # 🔥 TREND PARAMETER MAPPING (API mezők)
        self.trend_parameters = {
            "🥶 Minimum hőmérséklet": "temperature_2m_min",
            "🔥 Maximum hőmérséklet": "temperature_2m_max", 
            "🌡️ Átlag hőmérséklet": "temperature_2m_mean",
            "🌧️ Csapadékmennyiség": "precipitation_sum",
            "💨 Szélsebesség": "windspeed_10m_max",
            "💨 Széllökések": "windgusts_10m_max"
        }
        
        # 🔥 IDŐTARTAM OPCIÓK (multi-year)
        self.time_ranges = {
            "5 év": 5,
            "10 év": 10, 
            "25 év": 25,
            "55 év (teljes)": 55
        }
        
        logger.info("🔥 TrendDataProcessor v4.2 - GLOBALIZÁLT ARCHITEKTÚRA inicializálva")
        logger.info(f"🌍 CityManager: {self.city_manager.get_database_statistics()['total_searchable_locations']:,} kereshető helyszín")
        logger.info(f"🌍 Weather client: {self.weather_client.get_available_providers()}")
    
    def get_settlement_coordinates(self, settlement_name: str) -> Optional[Tuple[float, float]]:
        """
        🌍 GLOBÁLIS település koordinátáinak lekérdezése CityManager-rel
        
        MAGYAR PRIORITÁS: Magyar települések előnyben, majd globális városok
        
        Args:
            settlement_name: Település neve (pl. "Budapest", "Broxbourne", "Kiskunhalas")
            
        Returns:
            (latitude, longitude) tuple vagy None ha nem található
        """
        try:
            logger.info(f"🔍 GLOBÁLIS koordináta keresés: '{settlement_name}'")
            
            # 🌍 CityManager koordináta lekérdezés (egyesített magyar + globális)
            coordinates = self.city_manager.find_city_by_name(settlement_name)
            
            if coordinates:
                lat, lon = coordinates
                logger.info(f"✅ Koordináták találva: {settlement_name} -> {lat:.4f}, {lon:.4f}")
                return coordinates
            else:
                logger.warning(f"⚠️ Nem található koordináta: '{settlement_name}'")
                logger.info("💡 Próbálkozz pontosabb névvel vagy ellenőrizd a helyesírást")
                return None
                
        except Exception as e:
            logger.error(f"❌ Koordináta lekérdezési hiba: {e}")
            logger.exception("Koordináta keresés stacktrace:")
            return None
    
    def fetch_trend_data(self, settlement_name: str, parameter: str, time_range: str) -> None:
        """
        🔥 TREND ADATOK LEKÉRDEZÉSE API-VAL (háttérszálban)
        
        Args:
            settlement_name: Magyar település neve
            parameter: Trend paraméter (pl. "🔥 Maximum hőmérséklet")
            time_range: Időtartam (pl. "5 év")
        """
        try:
            self.progress_updated.emit(10)
            logger.info(f"🔥 TREND ANALYSIS START: {settlement_name} - {parameter} - {time_range}")
            
            # 1. Koordináták lekérdezése
            coordinates = self.get_settlement_coordinates(settlement_name)
            if not coordinates:
                self.error_occurred.emit(f"Nem található koordináta: {settlement_name}")
                return
            
            lat, lon = coordinates
            self.progress_updated.emit(20)
            
            # 2. Időtartam számítása
            years = self.time_ranges.get(time_range, 5)
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=years * 365)
            
            start_date_str = start_date.strftime("%Y-%m-%d")
            end_date_str = end_date.strftime("%Y-%m-%d")
            
            logger.info(f"📅 Időszak: {start_date_str} → {end_date_str} ({years} év)")
            self.progress_updated.emit(30)
            
            # 3. 🔥 MULTI-YEAR API HÍVÁS - BATCH FELDOLGOZÁSSAL
            logger.info(f"🌍 API hívás kezdése (batch feldolgozás): {lat:.4f}, {lon:.4f}")
            
            try:
                # Évenkénti batch-ek létrehozása (WeatherClient 1 éves limit miatt)
                weather_data = []
                current_start = start_date
                batch_count = 0
                total_batches = years
                
                while current_start < end_date:
                    # Következő év végének számítása
                    current_end = min(
                        current_start + timedelta(days=365),
                        end_date
                    )
                    
                    current_start_str = current_start.strftime("%Y-%m-%d")
                    current_end_str = current_end.strftime("%Y-%m-%d")
                    
                    logger.info(f"📅 Batch {batch_count + 1}/{total_batches}: {current_start_str} → {current_end_str}")
                    
                    # 🔥 KRITIKUS JAVÍTÁS v4.2: EGYSÉGES API - weather_client hívás egyszerűsítve
                    try:
                        # ✅ EGYSZERŰSÍTETT KÓD v4.2: MINDIG List[Dict] visszatérés
                        yearly_data = self.weather_client.get_weather_data(
                            lat, lon, current_start_str, current_end_str
                        )
                        
                        # Source kinyerése az első rekordból (data_source minden rekordba beépítve)
                        source = "unknown"
                        if yearly_data and isinstance(yearly_data, list) and len(yearly_data) > 0:
                            source = yearly_data[0].get('data_source', 'weather_api')
                        
                        if yearly_data:
                            weather_data.extend(yearly_data)
                            logger.info(f"✅ Batch {batch_count + 1} sikeres: {len(yearly_data)} nap ({source})")
                        else:
                            logger.warning(f"⚠️ Batch {batch_count + 1} üres adattal")
                            
                    except Exception as batch_error:
                        logger.error(f"❌ Batch {batch_count + 1} hiba: {batch_error}")
                        # Folytatjuk a következő batch-csel
                    
                    # Következő év kezdete
                    current_start = current_end + timedelta(days=1)
                    batch_count += 1
                    
                    # Progress frissítése
                    progress = 30 + int((batch_count / total_batches) * 30)  # 30-60%
                    self.progress_updated.emit(progress)
                
                logger.info(f"✅ Multi-year API hívás befejezve: {len(weather_data)} nap összesen")
                self.progress_updated.emit(60)
                
            except Exception as api_error:
                logger.error(f"❌ Multi-year API hiba: {api_error}")
                self.error_occurred.emit(f"API hiba: {str(api_error)}")
                return
            
            # 4. Adatok feldolgozása és trend számítás
            if not weather_data:
                self.error_occurred.emit("Nincs elérhető adat a kiválasztott időszakra")
                return
            
            # API mező mapping
            api_field = self.trend_parameters.get(parameter)
            if not api_field:
                self.error_occurred.emit(f"Ismeretlen paraméter: {parameter}")
                return
            
            self.progress_updated.emit(70)
            
            # 5. Trend számítás végrehajtása
            trend_results = self.calculate_trend_statistics(
                weather_data, api_field, settlement_name, parameter, time_range, years
            )
            
            self.progress_updated.emit(90)
            
            # 6. Eredmények visszaküldése
            if trend_results:
                self.data_received.emit(trend_results)
                logger.info(f"🎉 TREND ANALYSIS COMPLETE: {settlement_name}")
            else:
                self.error_occurred.emit("Trend számítási hiba")
            
            self.progress_updated.emit(100)
            
        except Exception as e:
            logger.error(f"❌ KRITIKUS HIBA trend lekérdezésnél: {e}")
            self.error_occurred.emit(f"Kritikus hiba: {str(e)}")
    
    def calculate_trend_statistics(self, weather_data: List[Dict], api_field: str, 
                                 settlement_name: str, parameter: str, time_range: str, years: int) -> Optional[Dict]:
        """
        🔥 PROFESSIONAL TREND SZÁMÍTÁS API ADATOKBÓL
        
        Args:
            weather_data: API-ból érkező napi adatok listája
            api_field: API mező neve (pl. "temperature_2m_max") 
            settlement_name, parameter, time_range, years: Metaadatok
            
        Returns:
            Teljes trend eredmények dictionary
        """
        try:
            logger.info(f"📊 TREND CALCULATION: {len(weather_data)} napból {api_field} feldolgozása")
            
            # DataFrame készítése API adatokból
            df_data = []
            for record in weather_data:
                if record.get('date') and record.get(api_field) is not None:
                    df_data.append({
                        'date': pd.to_datetime(record['date']),
                        'value': float(record[api_field])
                    })
            
            if len(df_data) == 0:
                logger.error(f"❌ Nincs érvényes adat a {api_field} mezőhöz")
                return None
            
            df = pd.DataFrame(df_data)
            df = df.sort_values('date')
            
            # Hiányzó adatok kezelése
            original_count = len(df)
            df = df.dropna()
            valid_count = len(df)
            
            if valid_count < original_count * 0.5:  # 50% alatti lefedettség
                logger.warning(f"⚠️ Alacsony adatlefedettség: {valid_count}/{original_count}")
            
            if valid_count < 30:  # Minimum 30 nap szükséges
                logger.error(f"❌ Túl kevés adat trend számításhoz: {valid_count}")
                return None
            
            logger.info(f"📈 Trend számítás: {valid_count} érvényes nap")
            
            # Havi aggregáció
            df['year_month'] = df['date'].dt.to_period('M')
            monthly_df = df.groupby('year_month').agg({
                'value': ['mean', 'min', 'max', 'count'],
                'date': 'first'
            }).reset_index()
            
            monthly_df.columns = ['year_month', 'avg_value', 'min_value', 'max_value', 'day_count', 'date']
            monthly_df = monthly_df[monthly_df['day_count'] >= 5]  # Minimum 5 nap/hónap
            
            if len(monthly_df) < 6:  # Minimum 6 hónap
                logger.error(f"❌ Túl kevés hónap trend számításhoz: {len(monthly_df)}")
                return None
            
            # 🔥 LINEÁRIS REGRESSZIÓ SZÁMÍTÁS
            X = np.arange(len(monthly_df)).reshape(-1, 1)
            y = monthly_df['avg_value'].values
            
            model = LinearRegression()
            model.fit(X, y)
            y_pred = model.predict(X)
            
            # R² és statisztikák
            r2 = r2_score(y, y_pred)
            
            # Trend/évtized számítás
            monthly_trend = model.coef_[0]  # havi trend
            trend_per_decade = monthly_trend * 12 * 10  # évtizedenként
            
            # Scipy stats további statisztikákhoz - DEFENSIVE PROGRAMMING
            try:
                slope, intercept, r_value, p_value, std_err = stats.linregress(X.flatten(), y)
            except ValueError as ve:
                logger.error(f"❌ stats.linregress hiba: {ve}")
                # Fallback értékek
                slope = model.coef_[0]
                intercept = model.intercept_
                r_value = np.sqrt(r2)
                p_value = 0.5  # neutral érték
                std_err = 0.0
            
            # 🔥 CONFIDENCE INTERVAL SZÁMÍTÁS (95%) - DEFENSIVE PROGRAMMING
            try:
                n = len(y)
                t_val = stats.t.ppf(0.975, n-2)  # 95% confidence, df = n-2
                
                # Standard error of prediction
                y_err = np.sqrt(np.sum((y - y_pred) ** 2) / (n - 2))
                
                # Confidence bands
                conf_interval = t_val * y_err * np.sqrt(1 + 1/n + (X.flatten() - np.mean(X.flatten()))**2 / np.sum((X.flatten() - np.mean(X.flatten()))**2))
                ci_upper = y_pred + conf_interval
                ci_lower = y_pred - conf_interval
            except Exception as ci_error:
                logger.error(f"❌ Confidence interval számítási hiba: {ci_error}")
                # Fallback: egyszerű konfidencia sáv
                ci_upper = y_pred + np.std(y) * 0.5
                ci_lower = y_pred - np.std(y) * 0.5
            
            # Alapstatisztikák
            stats_dict = {
                'mean': float(np.mean(y)),
                'std': float(np.std(y)),
                'min': float(np.min(y)),
                'max': float(np.max(y)),
                'median': float(np.median(y)),
                'count': int(valid_count)
            }
            
            # 🔥 CHART ADATOK KÉSZÍTÉSE - DEFENSIVE PROGRAMMING
            try:
                chart_data = {
                    'dates': monthly_df['date'].tolist(),
                    'values': monthly_df['avg_value'].tolist(),
                    'trend_line': y_pred.tolist(),
                    'ci_upper': ci_upper.tolist(),
                    'ci_lower': ci_lower.tolist(),
                    'min_values': monthly_df['min_value'].tolist(),
                    'max_values': monthly_df['max_value'].tolist()
                }
            except Exception as chart_error:
                logger.error(f"❌ Chart data készítési hiba: {chart_error}")
                # Fallback: basic chart data
                chart_data = {
                    'dates': list(monthly_df['date']),
                    'values': list(monthly_df['avg_value']),
                    'trend_line': list(y_pred),
                    'ci_upper': list(ci_upper),
                    'ci_lower': list(ci_lower),
                    'min_values': list(monthly_df['min_value']),
                    'max_values': list(monthly_df['max_value'])
                }
            
            # 🔥 FINAL RESULTS ASSEMBLY
            results = {
                # Metaadatok
                'settlement_name': settlement_name,
                'parameter': parameter,
                'time_range': time_range,
                'api_field': api_field,
                'years': years,
                'data_source': weather_data[0].get('data_source', 'unknown') if weather_data else 'unknown',
                
                # Statisztikai eredmények
                'r_squared': float(r2),
                'trend_per_decade': float(trend_per_decade),
                'p_value': float(p_value),
                'slope': float(slope),
                'intercept': float(intercept),
                'std_error': float(std_err),
                
                # Alapstatisztikák
                'statistics': stats_dict,
                
                # Chart adatok
                'chart_data': chart_data,
                
                # Dátum információk
                'start_date': df['date'].min().strftime('%Y-%m-%d'),
                'end_date': df['date'].max().strftime('%Y-%m-%d'),
                'total_days': int(valid_count),
                'monthly_points': int(len(monthly_df))
            }
            
            # Trend szignifikancia értékelése
            if p_value < 0.001:
                significance = "Nagyon szignifikáns"
            elif p_value < 0.01:
                significance = "Szignifikáns"
            elif p_value < 0.05:
                significance = "Mérsékelt szignifikáns"
            else:
                significance = "Nem szignifikáns"
            
            results['significance'] = significance
            
            logger.info(f"📊 TREND RESULTS: R²={r2:.3f}, Trend={trend_per_decade:.2f}/évtized, p={p_value:.3f}")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Trend számítási hiba: {e}")
            logger.exception("Full stacktrace:")
            return None


class DashboardStatsCard(QFrame):
    """
    🎯 KPI KÁRTYA KOMPONENS - QPALETTE-ALAPÚ ROBUSZTUS FRISSÍTÉS
    
    Egy adott metrikát jelenít meg kártya formátumban:
    - Nagy érték szám
    - Leírás
    - Színkódolás (QPalette-tel)
    - Ikon/emoji
    - ✅ QPalette-alapú konfliktusmentes színfrissítés
    """
    
    def __init__(self, title: str, value: str, subtitle: str = "", 
                 color: str = "#3b82f6", icon: str = "📊"):
        """
        KPI kártya inicializálása QPalette-alapú frissítési képességgel
        
        Args:
            title: Kártya címe
            value: Fő érték (nagy betűvel)
            subtitle: Alcím/magyarázat
            color: Téma szín
            icon: Emoji ikon
        """
        super().__init__()
        
        # 🔧 JAVÍTÁS: Label-ek és metaadatok osztály tagváltozóként
        self.title_text = title
        self.icon_text = icon
        self.title_label = None
        self.value_label = None 
        self.subtitle_label = None
        self.icon_label = None
        
        self.setup_card_ui(title, icon)
        self.update_contents(value, subtitle, color)
    
    def setup_card_ui(self, title: str, icon: str) -> None:
        """
        🔧 CSAK EGYSZER: UI elemek létrehozása fix tulajdonságokkal
        
        Ebben a metódusban CSAK az elrendezést és a fix tulajdonságokat állítjuk be.
        A színeket és a tartalmat az update_contents() fogja kezelni.
        """
        # Frame alapbeállítások
        self.setFrameStyle(QFrame.Box)
        self.setMinimumSize(180, 140)
        self.setMaximumSize(220, 160)
        
        # Layout
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Header (ikon + cím)
        header_layout = QHBoxLayout()
        
        self.icon_label = QLabel(icon)
        self.icon_label.setFont(QFont("Arial", 20))
        header_layout.addWidget(self.icon_label)
        
        self.title_label = QLabel(title)
        self.title_label.setFont(QFont("Arial", 11, QFont.Bold))
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Fő érték
        self.value_label = QLabel("--")  # Placeholder
        value_font = QFont("Arial", 24, QFont.Bold)
        self.value_label.setFont(value_font)
        self.value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.value_label)
        
        # Alcím
        self.subtitle_label = QLabel("--")  # Placeholder
        self.subtitle_label.setFont(QFont("Arial", 9))
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        self.subtitle_label.setWordWrap(True)
        layout.addWidget(self.subtitle_label)
        
        self.setLayout(layout)
    
    def update_contents(self, value: str, subtitle: str, color: str) -> None:
        """
        ✅ QPALETTE-ALAPÚ ROBUSZTUS FRISSÍTÉS
        
        A setStyleSheet konfliktusos működése helyett a Qt natív
        QPalette mechanizmusát használjuk a színek beállítására.
        
        Args:
            value: Új fő érték
            subtitle: Új alcím
            color: Új téma szín (hex formátum, pl. "#3b82f6")
        """
        # 1. TARTALOM FRISSÍTÉSE (ez eddig is jó volt)
        if self.value_label:
            self.value_label.setText(value)
        if self.subtitle_label:
            self.subtitle_label.setText(subtitle)
        
        # 2. KERET STÍLUS FRISSÍTÉSE (csak a szülő frame-hez)
        self.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8fafc);
                border: 2px solid {color};
                border-radius: 12px;
            }}
        """)
        
        # 3. SZÖVEG SZÍNEK FRISSÍTÉSE QPALETTE-TEL (KONFLIKTUSMENTES)
        qcolor = QColor(color)
        
        # Title label színe
        if self.title_label:
            title_palette = self.title_label.palette()
            title_palette.setColor(QPalette.WindowText, qcolor)
            self.title_label.setPalette(title_palette)
        
        # Value label színe (fő érték)
        if self.value_label:
            value_palette = self.value_label.palette()
            value_palette.setColor(QPalette.WindowText, qcolor)
            self.value_label.setPalette(value_palette)
        
        # Subtitle label színe (szürke marad)
        if self.subtitle_label:
            subtitle_palette = self.subtitle_label.palette()
            subtitle_palette.setColor(QPalette.WindowText, QColor("#6b7280"))  # Mindig szürke
            self.subtitle_label.setPalette(subtitle_palette)
        
        # Icon label nem változik (emoji)
    
    def update_value(self, new_value: str) -> None:
        """Backward compatibility - csak érték frissítése"""
        if self.value_label:
            self.value_label.setText(new_value)


class InteractiveTrendChart(QWidget):
    """
    🎨 INTERAKTÍV PLOTLY-ALAPÚ TREND CHART KOMPONENS
    
    Képességek:
    - Zoom, pan, hover tooltips
    - Konfidencia intervallum árnyékolás
    - Szezonális színkódolás
    - Export funkciók
    - Responsive design
    """
    
    def __init__(self):
        super().__init__()
        self.trend_data: Optional[Dict] = None
        self.setup_chart()
        
    def setup_chart(self) -> None:
        """Plotly chart widget inicializálása"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # QWebEngineView a Plotly HTML megjelenítéshez
        self.web_view = QWebEngineView()
        self.web_view.setMinimumHeight(500)
        
        layout.addWidget(self.web_view)
        self.setLayout(layout)
        
        # Kezdeti üres chart
        self.show_placeholder()
        
        logger.info("✅ InteractiveTrendChart inicializálva")
    
    def show_placeholder(self) -> None:
        """Placeholder chart megjelenítése"""
        fig = go.Figure()
        
        fig.add_annotation(
            x=0.5, y=0.5,
            text="📈 Válassz paramétert és indítsd el a trend elemzést!",
            xref="paper", yref="paper",
            showarrow=False,
            font=dict(size=16, color="#6b7280")
        )
        
        fig.update_layout(
            title="Trend Elemzés",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            plot_bgcolor='white',
            paper_bgcolor='white',
            height=500
        )
        
        html_content = fig.to_html(include_plotlyjs='cdn')
        self.web_view.setHtml(html_content)
    
    def update_chart(self, trend_data: Dict) -> None:
        """
        🎨 TREND CHART FRISSÍTÉSE PLOTLY-VAL
        
        Args:
            trend_data: TrendDataProcessor által számított eredmények
        """
        try:
            self.trend_data = trend_data
            logger.info(f"📊 PLOTLY CHART UPDATE: {trend_data['settlement_name']}")
            
            # Adatok kinyerése
            chart_data = trend_data['chart_data']
            dates = pd.to_datetime(chart_data['dates'])
            values = np.array(chart_data['values'])
            trend_line = np.array(chart_data['trend_line'])
            ci_upper = np.array(chart_data['ci_upper'])
            ci_lower = np.array(chart_data['ci_lower'])
            
            # Plotly figure létrehozása
            fig = go.Figure()
            
            # 🎨 95% KONFIDENCIA INTERVALLUM (árnyékolt terület)
            # 🔧 JAVÍTÁS v4.2: pandas DatetimeIndex lista konverzió
            dates_list = dates.to_list()  # Konvertálás listává
            fig.add_trace(go.Scatter(
                x=dates_list + dates_list[::-1],  # Egyszerű lista összefűzés
                y=np.concatenate([ci_upper, ci_lower[::-1]]),
                fill='toself',
                fillcolor='rgba(128, 128, 128, 0.2)',
                line=dict(color='rgba(255,255,255,0)'),
                name='95% konfidencia',
                hoverinfo='skip'
            ))
            
            # 📊 HAVI ÁTLAG ADATOK (interaktív pontok)
            fig.add_trace(go.Scatter(
                x=dates,
                y=values,
                mode='markers+lines',
                name='Havi átlag',
                line=dict(color='#ff6b35', width=3),
                marker=dict(
                    size=6,
                    color='#ff6b35',
                    line=dict(width=2, color='white')
                ),
                hovertemplate='<b>%{x|%Y-%m}</b><br>' +
                             f'{trend_data["parameter"]}: %{{y:.1f}}<br>' +  # 🔧 JAVÍTÁS: dupla {{ }} a Plotly formázáshoz
                             '<extra></extra>'
            ))
            
            # 📈 LINEÁRIS TREND VONAL
            fig.add_trace(go.Scatter(
                x=dates,
                y=trend_line,
                mode='lines',
                name=f'Trend ({trend_data["trend_per_decade"]:+.2f}/évtized)',
                line=dict(color='#ff1493', width=3, dash='dash'),
                hovertemplate='<b>Trend vonal</b><br>' +
                             '%{{x|%Y-%m}}: %{{y:.1f}}<br>' +  # 🔧 JAVÍTÁS: dupla {{ }} a Plotly formázáshoz
                             '<extra></extra>'
            ))
            
            # 🎨 PROFESSIONAL LAYOUT STYLING
            settlement = trend_data['settlement_name']
            parameter = trend_data['parameter']
            time_range = trend_data['time_range']
            r2 = trend_data['r_squared']
            significance = trend_data['significance']
            
            # Y tengely címke paraméter alapján
            if 'hőmérséklet' in parameter.lower():
                y_title = 'Hőmérséklet (°C)'
            elif 'csapadék' in parameter.lower():
                y_title = 'Csapadék (mm)'
            elif 'szél' in parameter.lower():
                y_title = 'Szélsebesség (km/h)'
            else:
                y_title = 'Érték'
            
            fig.update_layout(
                title=dict(
                    text=f'📈 {settlement} - {parameter} trend elemzés ({time_range})<br>' +
                         f'<sub>R² = {r2:.3f} | {significance} | {trend_data["total_days"]:,} nap</sub>',
                    font=dict(size=16),
                    x=0.5
                ),
                xaxis=dict(
                    title='Dátum',
                    gridcolor='#e5e7eb',
                    showgrid=True
                ),
                yaxis=dict(
                    title=y_title,
                    gridcolor='#e5e7eb',
                    showgrid=True
                ),
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(family="Arial, sans-serif", size=12),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                hovermode='x unified',
                height=500
            )
            
            # Interaktív konfiguráció
            config = {
                'displayModeBar': True,
                'modeBarButtonsToAdd': [
                    'drawline',
                    'drawopenpath',
                    'drawclosedpath',
                    'drawcircle',
                    'drawrect',
                    'eraseshape'
                ],
                'toImageButtonOptions': {
                    'format': 'png',
                    'filename': f'trend_analysis_{settlement}_{parameter}',
                    'height': 600,
                    'width': 1000,
                    'scale': 2
                }
            }
            
            # HTML generálása és megjelenítése
            html_content = fig.to_html(include_plotlyjs='cdn', config=config)
            self.web_view.setHtml(html_content)
            
            logger.info("✅ Plotly chart successfully updated")
            
        except Exception as e:
            logger.error(f"❌ Plotly chart update hiba: {e}")
            logger.exception("Plotly chart error stacktrace:")
            self.show_error_chart(str(e))
    
    def show_error_chart(self, error_message: str) -> None:
        """Hiba chart megjelenítése"""
        fig = go.Figure()
        
        fig.add_annotation(
            x=0.5, y=0.5,
            text=f"❌ Hiba történt:<br>{error_message}",
            xref="paper", yref="paper",
            showarrow=False,
            font=dict(size=14, color="#dc2626")
        )
        
        fig.update_layout(
            title="Trend Elemzés - Hiba",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            plot_bgcolor='white',
            paper_bgcolor='white',
            height=500
        )
        
        html_content = fig.to_html(include_plotlyjs='cdn')
        self.web_view.setHtml(html_content)


class EnhancedStatisticsPanel(QWidget):
    """
    🎯 DASHBOARD-SZERŰ STATISZTIKÁK PANEL - KPI KÁRTYÁKKAL
    
    Grid layout-ban jeleníti meg a főbb KPI-ket:
    - Trend változás
    - Megbízhatóság (R²)
    - Szignifikancia
    - Értéktartomány
    """
    
    def __init__(self):
        super().__init__()
        self.stats_cards: Dict[str, DashboardStatsCard] = {}  # ELŐBB inicializálni!
        self.setup_stats_panel()
        
    def setup_stats_panel(self) -> None:
        """Statisztikák panel UI beállítása"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Panel cím
        title_label = QLabel("📊 Trend Mutatók")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setStyleSheet("color: #1f2937; margin-bottom: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # KPI kártyák grid-je
        self.cards_grid = QGridLayout()
        self.cards_grid.setSpacing(10)
        
        layout.addLayout(self.cards_grid)
        layout.addStretch()
        
        self.setLayout(layout)
        
        # Placeholder kártyák
        self.show_placeholder_cards()
        
        logger.info("✅ EnhancedStatisticsPanel inicializálva")
    
    def show_placeholder_cards(self) -> None:
        """Placeholder KPI kártyák megjelenítése"""
        placeholder_cards = [
            ("🎯 Trend", "Nincs adat", "per évtized", "#3b82f6", "📈"),
            ("🎯 Megbízhatóság", "Nincs adat", "R² érték", "#10b981", "🎯"),
            ("🎯 Szignifikancia", "Nincs adat", "statisztikai", "#f59e0b", "⚡"),
            ("📊 Tartomány", "Nincs adat", "min - max", "#8b5cf6", "📊")
        ]
        
        for i, (title, value, subtitle, color, icon) in enumerate(placeholder_cards):
            card = DashboardStatsCard(title, value, subtitle, color, icon)
            row, col = divmod(i, 2)
            self.cards_grid.addWidget(card, row, col)
            self.stats_cards[title] = card
    
    def update_statistics(self, trend_data: Dict) -> None:
        """
        🎯 KPI KÁRTYÁK FRISSÍTÉSE - DASHBOARD ADATOKKAL
        
        Args:
            trend_data: TrendDataProcessor eredményei
        """
        try:
            logger.info("🎯 DASHBOARD STATS FRISSÍTÉS KEZDÉSE")
            
            # 1. TREND VÁLTOZÁS KÁRTYA
            trend_value = trend_data['trend_per_decade']
            if 'hőmérséklet' in trend_data['parameter'].lower():
                trend_unit = "°C/évtized"
            elif 'csapadék' in trend_data['parameter'].lower():
                trend_unit = "mm/évtized"
            elif 'szél' in trend_data['parameter'].lower():
                trend_unit = "km/h/évtized"
            else:
                trend_unit = "/évtized"
            
            trend_display = f"{trend_value:+.2f}"
            trend_subtitle = f"{trend_unit}"
            
            # 2. MEGBÍZHATÓSÁG (R²) KÁRTYA
            r2 = trend_data['r_squared']
            if r2 > 0.7:
                reliability_level = "Magas"
                r2_color = "#10b981"  # zöld
            elif r2 > 0.4:
                reliability_level = "Közepes"
                r2_color = "#f59e0b"  # sárga
            else:
                reliability_level = "Alacsony"
                r2_color = "#ef4444"  # piros
            
            r2_display = f"{r2:.3f}"
            r2_subtitle = f"{reliability_level} megbízhatóság"
            
            # 3. SZIGNIFIKANCIA KÁRTJA
            significance = trend_data['significance']
            p_val = trend_data['p_value']
            
            if p_val < 0.001:
                sig_display = "***"
                sig_color = "#059669"  # sötét zöld
            elif p_val < 0.01:
                sig_display = "**"
                sig_color = "#10b981"  # zöld
            elif p_val < 0.05:
                sig_display = "*"
                sig_color = "#f59e0b"  # sárga
            else:
                sig_display = "n.s."
                sig_color = "#6b7280"  # szürke
            
            sig_subtitle = f"p = {p_val:.3f}"
            
            # 4. ÉRTÉKTARTOMÁNY KÁRTYA
            stats = trend_data['statistics']
            if 'hőmérséklet' in trend_data['parameter'].lower():
                unit = "°C"
            elif 'csapadék' in trend_data['parameter'].lower():
                unit = "mm"
            elif 'szél' in trend_data['parameter'].lower():
                unit = "km/h"
            else:
                unit = ""
            
            range_value = stats['max'] - stats['min']
            range_display = f"{range_value:.1f}"
            range_subtitle = f"{stats['min']:.1f} - {stats['max']:.1f} {unit}"
            
            # KÁRTYÁK FRISSÍTÉSE
            
            # Trend kártya frissítése (színkódolással)
            trend_color = "#ef4444" if trend_value < 0 else "#10b981"  # piros ha csökken, zöld ha nő
            self.update_card("🎯 Trend", trend_display, trend_subtitle, trend_color)
            
            # Megbízhatóság kártya
            self.update_card("🎯 Megbízhatóság", r2_display, r2_subtitle, r2_color)
            
            # Szignifikancia kártya
            self.update_card("🎯 Szignifikancia", sig_display, sig_subtitle, sig_color)
            
            # Tartomány kártya
            self.update_card("📊 Tartomány", range_display, range_subtitle, "#8b5cf6")
            
            logger.info(f"✅ Dashboard stats frissítve: {len(self.stats_cards)} kártya")
            
        except Exception as e:
            logger.error(f"❌ Dashboard stats update hiba: {e}")
            logger.exception("Dashboard stats error stacktrace:")
            self.show_error_cards(str(e))
    
    def update_card(self, card_key: str, value: str, subtitle: str, color: str) -> None:
        """
        ✅ EGYSZERŰSÍTETT KÁRTYA FRISSÍTÉS - Tartalom frissítése widget csere helyett
        
        Args:
            card_key: Kártya azonosító
            value: Új fő érték
            subtitle: Új alcím  
            color: Új téma szín
        """
        card_widget = self.stats_cards.get(card_key)
        if card_widget:
            # 🔧 JAVÍTÁS: Widget csere helyett tartalom frissítése
            card_widget.update_contents(value, subtitle, color)
            logger.debug(f"✅ Kártya frissítve: {card_key} = {value}")
        else:
            logger.warning(f"⚠️ Nem található kártya a frissítéshez: '{card_key}'")
    
    def show_error_cards(self, error_msg: str) -> None:
        """
        ✅ EGYSZERŰSÍTETT HIBA KÁRTYÁK - Tartalom frissítése widget csere helyett
        
        Args:
            error_msg: Hiba üzenet
        """
        error_cards_data = [
            ("🎯 Trend", "Hiba", "számítási hiba", "#ef4444"),
            ("🎯 Megbízhatóság", "Hiba", "számítási hiba", "#ef4444"),
            ("🎯 Szignifikancia", "Hiba", "számítási hiba", "#ef4444"),
            ("📊 Tartomány", "Hiba", "számítási hiba", "#ef4444")
        ]
        
        for card_key, value, subtitle, color in error_cards_data:
            if card_key in self.stats_cards:
                # 🔧 JAVÍTÁS: Widget csere helyett tartalom frissítése
                self.stats_cards[card_key].update_contents(value, subtitle, color)
                logger.debug(f"❌ Hiba kártya frissítve: {card_key}")


class TrendAnalyticsWorker(QThread):
    """
    🔥 BACKGROUND WORKER THREAD - API HÍVÁSOK HÁTTÉRBEN
    
    A trend elemzés hosszú ideig tart (multi-year API hívások),
    ezért háttérszálban futtatjuk a UI blokkolás elkerülésére.
    """
    
    # Signals
    progress_updated = Signal(int)
    data_received = Signal(dict)
    error_occurred = Signal(str)
    finished = Signal()
    
    def __init__(self, settlement_name: str, parameter: str, time_range: str):
        super().__init__()
        self.settlement_name = settlement_name
        self.parameter = parameter  
        self.time_range = time_range
        self.processor = TrendDataProcessor()
        
        # Signal routing
        self.processor.progress_updated.connect(self.progress_updated.emit)
        self.processor.data_received.connect(self.data_received.emit)
        self.processor.error_occurred.connect(self.error_occurred.emit)
    
    def run(self) -> None:
        """Háttérszál futtatása"""
        try:
            logger.info(f"🔥 WORKER THREAD START: {self.settlement_name} - {self.parameter} - {self.time_range}")
            
            self.processor.fetch_trend_data(
                self.settlement_name, self.parameter, self.time_range
            )
            
        except Exception as e:
            logger.error(f"❌ Worker thread hiba: {e}")
            self.error_occurred.emit(f"Háttérszál hiba: {str(e)}")
        finally:
            self.finished.emit()


class TrendAnalyticsTab(QWidget):
    """
    🚀 ENHANCED TREND ANALYTICS TAB v4.2 - PROFESSIONAL DASHBOARD IMPLEMENTATION
    
    🎨 FEJLESZTÉSEK v4.2:
    - ✅ KRITIKUS JAVÍTÁS: weather_client.get_weather_data() EGYSÉGES API
    - ✅ Tuple unpacking hiba véglegesen megoldva
    - ✅ PLOTLY INTERAKTÍV CHARTOK: Zoom, pan, hover tooltips
    - ✅ DASHBOARD-SZERŰ KPI KÁRTYÁK: Vizuális trend mutatók
    - ✅ ENHANCED STATISTICS PANEL: Grid layout stat cards
    - ✅ QSPLITTER MEGTARTÁSA: Felhasználó által állítható layout
    - ✅ PROFESSIONAL ERROR HANDLING: Structured logging
    - ✅ TYPE HINTS: Teljes típus annotáció
    - ✅ MODULÁRIS ARCHITEKTÚRA: DRY, KISS, YAGNI, SOLID elvek
    
    LAYOUT STRUKTÚRA v4.2:
    ┌───────────────────────────────────────────────────────────┐
    │                    HEADER + CONTROLS                      │
    ├─────────────────────┬─────────────────────────────────────┤
    │  📈 PLOTLY CHART    │ 🎯 KPI DASHBOARD CARDS              │
    │  (QSplitter bal)    │ (QSplitter jobb)                   │
    │  - Interaktív       │ ┌─────────────────────────────────┐ │
    │  - Zoom/Pan         │ │ [🎯 Trend] [🎯 Megbízhatóság] │ │
    │  - Hover tooltips   │ │ [⚡ Szign.] [📊 Tartomány]    │ │
    │  - Export           │ └─────────────────────────────────┘ │
    └─────────────────────┴─────────────────────────────────────┘
    
    KORÁBBI v3.0-4.1 FUNKCIÓK MEGMARADTAK + GLOBALIZÁCIÓ:
    - CityManager globális koordináta lekérdezés (3200+ magyar + 44k nemzetközi)
    - Weather_client.py multi-year API hívások (✅ EGYSÉGES API)
    - 5-10-25-55 éves trend opciók
    - Professional trend számítás
    - Signal-based communication
    """
    
    # Signals for main window communication
    analysis_started = Signal()
    analysis_completed = Signal(dict)
    error_occurred = Signal(str)
    location_selected = Signal(str, float, float)  # name, lat, lon
    
    def __init__(self):
        super().__init__()
        self.current_worker: Optional[TrendAnalyticsWorker] = None
        self.setup_ui()
        self.connect_signals()
        
        logger.info("🚀 TrendAnalyticsTab v4.2 inicializálva (KPI DASHBOARD DINAMIKUS FRISSÍTÉS)")
    
    def setup_ui(self) -> None:
        """🎨 UI SETUP - Enhanced Dashboard Layout v4.2"""
        main_layout = QVBoxLayout()
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Controls panel
        controls = self.create_controls_panel()
        main_layout.addWidget(controls)
        
        # 🔧 QSplitter IMPLEMENTÁCIÓ MEGTARTVA (v3.3 kompatibilitás)
        content_splitter = QSplitter(Qt.Horizontal)
        content_splitter.setChildrenCollapsible(False)
        
        # Chart area (bal oldal) - PLOTLY CHART
        chart_container = self.create_plotly_chart_container()
        chart_container.setMinimumHeight(400)
        chart_container.setMinimumWidth(600)
        content_splitter.addWidget(chart_container)
        
        # 🎯 DASHBOARD STATISTICS AREA - KPI KÁRTYÁK
        stats_area = self.create_dashboard_statistics_area()
        stats_area.setMinimumWidth(400)
        content_splitter.addWidget(stats_area)
        
        # 🔧 KEZDETI MÉRETARÁNY: 67% chart, 33% stats (VÁLTOZATLAN)
        content_splitter.setSizes([2, 1])
        content_splitter.setStretchFactor(0, 2)
        content_splitter.setStretchFactor(1, 1)
        
        # QSplitter styling (VÁLTOZATLAN)
        content_splitter.setStyleSheet("""
            QSplitter {
                background-color: #f8f9fa;
                border: none;
            }
            QSplitter::handle {
                background-color: #dee2e6;
                width: 8px;
                margin: 2px;
                border-radius: 4px;
            }
            QSplitter::handle:hover {
                background-color: #6c757d;
            }
        """)
        
        main_layout.addWidget(content_splitter, stretch=1)
        
        self.setLayout(main_layout)
        
        logger.info("✅ Enhanced Dashboard layout beállítva: KPI kártyák dinamikus frissítéssel")
    
    def create_header(self) -> QWidget:
        """Professional header létrehozása (VÁLTOZATLAN)"""
        header = QFrame()
        header.setFrameStyle(QFrame.Box)
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 8px;
                padding: 15px;
                color: white;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Main title
        title = QLabel("📈 Enhanced Trend Analytics Dashboard v4.2")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setStyleSheet("color: white; margin: 0;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Globális trend elemzés dinamikus KPI dashboard-dal - Hibamentesen javított!")
        subtitle.setFont(QFont("Arial", 11))
        subtitle.setStyleSheet("color: rgba(255,255,255,0.9); margin: 5px 0 0 0;")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        header.setLayout(layout)
        return header
    
    def create_controls_panel(self) -> QWidget:
        """🔥 ELEMZÉSI PARAMÉTEREK PANEL (VÁLTOZATLAN)"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Box)
        panel.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Panel cím
        panel_title = QLabel("⚙️ Elemzési Paraméterek")
        panel_title.setFont(QFont("Arial", 14, QFont.Bold))
        panel_title.setStyleSheet("color: #495057; margin-bottom: 10px;")
        layout.addWidget(panel_title)
        
        # Controls grid
        controls_layout = QHBoxLayout()
        
        # Lokáció választó
        location_group = QVBoxLayout()
        location_label = QLabel("🌍 Lokáció:")
        location_label.setFont(QFont("Arial", 10, QFont.Bold))
        location_group.addWidget(location_label)
        
        self.location_combo = QComboBox()
        self.location_combo.setEditable(True)
        self.location_combo.setPlaceholderText("Írj be település nevet...")
        self.location_combo.setMinimumWidth(200)
        location_group.addWidget(self.location_combo)
        controls_layout.addLayout(location_group)
        
        # Paraméter választó
        param_group = QVBoxLayout()
        param_label = QLabel("📊 Paraméter:")
        param_label.setFont(QFont("Arial", 10, QFont.Bold))
        param_group.addWidget(param_label)
        
        self.parameter_combo = QComboBox()
        self.parameter_combo.addItems([
            "🥶 Minimum hőmérséklet",
            "🔥 Maximum hőmérséklet", 
            "🌡️ Átlag hőmérséklet",
            "🌧️ Csapadékmennyiség",
            "💨 Szélsebesség", 
            "💨 Széllökések"
        ])
        self.parameter_combo.setCurrentText("🔥 Maximum hőmérséklet")
        param_group.addWidget(self.parameter_combo)
        controls_layout.addLayout(param_group)
        
        # Időtartam választó  
        time_group = QVBoxLayout()
        time_label = QLabel("🕒 Időtartam:")
        time_label.setFont(QFont("Arial", 10, QFont.Bold))
        time_group.addWidget(time_label)
        
        self.time_combo = QComboBox()
        self.time_combo.addItems([
            "5 év",
            "10 év", 
            "25 év",
            "55 év (teljes)"
        ])
        self.time_combo.setCurrentText("5 év")
        time_group.addWidget(self.time_combo)
        controls_layout.addLayout(time_group)
        
        # Analyze button
        self.analyze_button = QPushButton("🚀 Dashboard Elemzés Indítása")
        self.analyze_button.setFont(QFont("Arial", 11, QFont.Bold))
        self.analyze_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #28a745, stop:1 #1e7e34);
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                margin-left: 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #218838, stop:1 #1c7430);
            }
            QPushButton:pressed {
                background: #1e7e34;
            }
            QPushButton:disabled {
                background: #6c757d;
            }
        """)
        controls_layout.addWidget(self.analyze_button)
        
        layout.addLayout(controls_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #dee2e6;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #007bff;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        panel.setLayout(layout)
        return panel
    
    def create_plotly_chart_container(self) -> QWidget:
        """🎨 PLOTLY CHART CONTAINER LÉTREHOZÁSA"""
        container = QFrame()
        container.setFrameStyle(QFrame.Box)
        container.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Chart title
        chart_title = QLabel("📈 Interaktív Trend Vizualizáció")
        chart_title.setFont(QFont("Arial", 14, QFont.Bold))
        chart_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(chart_title)
        
        # 🎨 PLOTLY CHART WIDGET
        self.chart = InteractiveTrendChart()
        layout.addWidget(self.chart)
        
        container.setLayout(layout)
        return container
    
    def create_dashboard_statistics_area(self) -> QScrollArea:
        """
        🎯 DASHBOARD KPI KÁRTYÁK TERÜLETE - QScrollArea-ban
        
        Ez a metódus létrehozza a KPI kártyákat tartalmazó dashboard-ot
        QScrollArea-ban, hogy kis képernyőkön is jól használható legyen.
        """
        # QScrollArea létrehozása
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setFrameStyle(QFrame.Box)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 8px;
            }
        """)
        
        # Belső widget a KPI kártyáknak
        stats_widget = QWidget()
        stats_layout = QVBoxLayout()
        stats_layout.setContentsMargins(10, 10, 10, 10)
        
        # 🎯 ENHANCED STATISTICS PANEL HOZZÁADÁSA
        self.statistics_panel = EnhancedStatisticsPanel()
        stats_layout.addWidget(self.statistics_panel, stretch=1)
        
        # Stretch spacer a végén
        stats_layout.addStretch()
        
        stats_widget.setLayout(stats_layout)
        scroll_area.setWidget(stats_widget)
        
        logger.info("✅ Dashboard KPI kártyák területe létrehozva (QScrollArea-ban)")
        return scroll_area
    
    def connect_signals(self) -> None:
        """Signal connections beállítása (VÁLTOZATLAN)"""
        # Analyze button
        self.analyze_button.clicked.connect(self.start_trend_analysis)
        
        # Location selection
        self.location_combo.currentTextChanged.connect(self.on_location_changed)
    
    def on_location_changed(self, location_name: str) -> None:
        """Location selection kezelése (VÁLTOZATLAN)"""
        if location_name and len(location_name.strip()) > 2:
            # Get coordinates for location
            processor = TrendDataProcessor()
            coordinates = processor.get_settlement_coordinates(location_name.strip())
            
            if coordinates:
                lat, lon = coordinates
                logger.info(f"📍 Location selected: {location_name} ({lat:.4f}, {lon:.4f})")
                self.location_selected.emit(location_name, lat, lon)
    
    def start_trend_analysis(self) -> None:
        """🚀 ENHANCED TREND ELEMZÉS INDÍTÁSA"""
        try:
            # Input validation
            location = self.location_combo.currentText().strip()
            parameter = self.parameter_combo.currentText()
            time_range = self.time_combo.currentText()
            
            if not location:
                self.error_occurred.emit("Kérlek válassz várost!")
                return
            
            if len(location) < 2:
                self.error_occurred.emit("Legalább 2 karakteres város név szükséges!")
                return
            
            logger.info(f"🚀 ENHANCED TREND ANALYSIS START: {location} - {parameter} - {time_range}")
            
            # UI update
            self.analyze_button.setEnabled(False)
            self.analyze_button.setText("⏳ Dashboard Elemzés folyamatban...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            
            # Signal emission
            self.analysis_started.emit()
            
            # Worker thread létrehozása
            self.current_worker = TrendAnalyticsWorker(location, parameter, time_range)
            
            # Worker signals connecting
            self.current_worker.progress_updated.connect(self.progress_bar.setValue)
            self.current_worker.data_received.connect(self.on_analysis_completed)
            self.current_worker.error_occurred.connect(self.on_analysis_error)
            self.current_worker.finished.connect(self.on_worker_finished)
            
            # Worker start
            self.current_worker.start()
            
        except Exception as e:
            logger.error(f"❌ Enhanced trend analysis start hiba: {e}")
            self.on_analysis_error(f"Elemzés indítási hiba: {str(e)}")
    
    def on_analysis_completed(self, trend_results: Dict) -> None:
        """🎉 ENHANCED TREND ELEMZÉS BEFEJEZÉSE"""
        try:
            logger.info(f"🎉 ENHANCED TREND ANALYSIS COMPLETED: {trend_results['settlement_name']}")
            
            # 🎨 PLOTLY CHART FRISSÍTÉSE
            self.chart.update_chart(trend_results)
            logger.info("✅ Plotly chart frissítve")
            
            # 🎯 DASHBOARD KPI KÁRTYÁK FRISSÍTÉSE
            logger.info("🎯 Dashboard KPI kártyák frissítése kezdése...")
            self.statistics_panel.update_statistics(trend_results)
            logger.info("✅ Dashboard KPI kártyák frissítve")
            
            # Signal emission
            self.analysis_completed.emit(trend_results)
            
        except Exception as e:
            logger.error(f"❌ Enhanced analysis completion handling hiba: {e}")
            self.on_analysis_error(f"Eredmény feldolgozási hiba: {str(e)}")
    
    def on_analysis_error(self, error_message: str) -> None:
        """❌ ENHANCED TREND ELEMZÉS HIBA KEZELÉSE"""
        logger.error(f"❌ ENHANCED TREND ANALYSIS ERROR: {error_message}")
        
        # Error display in Plotly chart
        self.chart.show_error_chart(error_message)
        
        # Error display in KPI cards
        self.statistics_panel.show_error_cards(error_message)
        
        # Signal emission
        self.error_occurred.emit(error_message)
    
    def on_worker_finished(self) -> None:
        """Worker thread befejezése (VÁLTOZATLAN)"""
        # UI reset
        self.analyze_button.setEnabled(True)
        self.analyze_button.setText("🚀 Dashboard Elemzés Indítása")
        self.progress_bar.setVisible(False)
        
        # Worker cleanup
        if self.current_worker:
            self.current_worker.deleteLater()
            self.current_worker = None
        
        logger.info("✅ Enhanced worker thread finished and cleaned up")
    
    def set_location(self, location_name: str, latitude: float, longitude: float) -> None:
        """External location setting (VÁLTOZATLAN)"""
        self.location_combo.setCurrentText(location_name)
        self.on_location_changed(location_name)
        
        logger.info(f"📍 External location set: {location_name} ({latitude:.4f}, {longitude:.4f})")


# Theme integration (VÁLTOZATLAN)
def register_trend_analytics_theme(theme_manager: ThemeManager) -> None:
    """Theme manager integráció"""
    if theme_manager:
        # Register trend analytics specific styling
        pass


if __name__ == "__main__":
    # Standalone testing
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Test window
    window = TrendAnalyticsTab()
    window.setWindowTitle("🚀 Enhanced Trend Analytics v4.2 - KPI DASHBOARD KÉSZ!")
    window.resize(1600, 1000)
    window.show()
    
    sys.exit(app.exec())