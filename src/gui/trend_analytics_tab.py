#!/usr/bin/env python3
"""
Trend Analytics Tab - TELJES INTEGRÁCIÓ HUNGARIAN_SETTLEMENTS.DB + METEOSTAT API
Global Weather Analyzer projekt

🔥 KRITIKUS JAVÍTÁS v3.0:
- Hungarian_settlements.db integráció (3178 település + javított koordináták)
- Weather_client.py multi-year API hívások
- Meteostat API 55+ éves történelmi adatok
- Professional trend számítás API adatokból
- 5/10/55 éves trend opciók

🎯 v3.1 UI/UX JAVÍTÁSOK:
- Statistics panel átrendezés (nem takarja el a chartot)
- Egyszerű táblázat formátum (könnyen érthető)
- Kompakt layout (nincs scroll hell)
- Magyar nyelvű magyarázatok

🔧 v3.3 SPLITTER REFAKTOR:
- QSplitter(Qt.Horizontal) implementáció
- Állítható méretarány a felhasználó számára
- QScrollArea a statisztikai táblázathoz
- Kezdeti arány: grafikon 67%, statisztika 33%

Fájl: src/gui/trend_analytics_tab.py
Hely: /home/tibor/PythonProjects/openmeteo_history/global_weather_analyzer/src/gui/
"""

import sys
import sqlite3
import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import asyncio
from pathlib import Path

# PySide6 imports
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QPushButton, QProgressBar, QFrame, QSplitter, QScrollArea,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt, Signal, QThread, QTimer, QObject, QSize
from PySide6.QtGui import QFont, QPalette, QColor

# Matplotlib imports
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from matplotlib.patches import Polygon
import seaborn as sns

# Scientific computing
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

# Project imports - FRISSÍTETT INTEGRÁCIÓ
from ..data.weather_client import WeatherClient  # 🔥 MULTI-YEAR TÁMOGATÁS
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
        
        # 🔥 ÚJ ARCHITEKTÚRA KOMPONENSEK
        self.weather_client = WeatherClient(preferred_provider="auto")
        self.db_path = Path(__file__).parent.parent.parent / "data" / "hungarian_settlements.db"
        
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
        
        logger.info("🔥 TrendDataProcessor v3.0 - API-BASED inicializálva")
        logger.info(f"📁 Hungarian settlements DB: {self.db_path}")
        logger.info(f"🌍 Weather client: {self.weather_client.get_available_providers()}")
    
    def get_settlement_coordinates(self, settlement_name: str) -> Optional[Tuple[float, float]]:
        """
        Magyar település koordinátáinak lekérdezése javított adatbázisból
        
        Args:
            settlement_name: Település neve
            
        Returns:
            (latitude, longitude) tuple vagy None ha nem található
        """
        try:
            if not self.db_path.exists():
                logger.error(f"❌ Hungarian settlements DB nem található: {self.db_path}")
                return None
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Fuzzy search support
                cursor.execute('''
                    SELECT latitude, longitude, name
                    FROM hungarian_settlements 
                    WHERE name LIKE ? OR name = ?
                    ORDER BY 
                        CASE 
                            WHEN name = ? THEN 1
                            WHEN name LIKE ? THEN 2
                            ELSE 3
                        END
                    LIMIT 1
                ''', (f"{settlement_name}%", settlement_name, settlement_name, f"%{settlement_name}%"))
                
                result = cursor.fetchone()
                
                if result:
                    lat, lon, found_name = result
                    logger.info(f"📍 Település koordináták: {found_name} -> {lat:.4f}, {lon:.4f}")
                    
                    # Koordináta validálás (nem Budapest default)
                    if lat == 47.4979 and lon == 19.0402:
                        logger.warning(f"⚠️ FIGYELEM: {found_name} még Budapest koordinátákon van!")
                        return None
                    
                    return (lat, lon)
                else:
                    logger.warning(f"⚠️ Település nem található: {settlement_name}")
                    return None
                    
        except sqlite3.Error as e:
            logger.error(f"❌ Adatbázis hiba: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Váratlan hiba koordináta lekérdezésnél: {e}")
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
            
            # 3. 🔥 MULTI-YEAR API HÍVÁS
            logger.info(f"🌍 API hívás kezdése: {lat:.4f}, {lon:.4f}")
            
            try:
                weather_data, source = self.weather_client.get_weather_data(
                    lat, lon, start_date_str, end_date_str
                )
                
                logger.info(f"✅ API válasz: {len(weather_data)} nap ({source})")
                self.progress_updated.emit(60)
                
            except Exception as api_error:
                logger.error(f"❌ API hiba: {api_error}")
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
            
            # Scipy stats további statisztikákhoz
            slope, intercept, r_value, p_value, std_err = stats.linregress(X.flatten(), y)
            
            # 🔥 CONFIDENCE INTERVAL SZÁMÍTÁS (95%)
            n = len(y)
            t_val = stats.t.ppf(0.975, n-2)  # 95% confidence, df = n-2
            
            # Standard error of prediction
            y_err = np.sqrt(np.sum((y - y_pred) ** 2) / (n - 2))
            
            # Confidence bands
            conf_interval = t_val * y_err * np.sqrt(1 + 1/n + (X.flatten() - np.mean(X.flatten()))**2 / np.sum((X.flatten() - np.mean(X.flatten()))**2))
            ci_upper = y_pred + conf_interval
            ci_lower = y_pred - conf_interval
            
            # Alapstatisztikák
            stats_dict = {
                'mean': float(np.mean(y)),
                'std': float(np.std(y)),
                'min': float(np.min(y)),
                'max': float(np.max(y)),
                'median': float(np.median(y)),
                'count': int(valid_count)
            }
            
            # 🔥 CHART ADATOK KÉSZÍTÉSE
            chart_data = {
                'dates': monthly_df['date'].tolist(),
                'values': monthly_df['avg_value'].tolist(),
                'trend_line': y_pred.tolist(),
                'ci_upper': ci_upper.tolist(),
                'ci_lower': ci_lower.tolist(),
                'min_values': monthly_df['min_value'].tolist(),
                'max_values': monthly_df['max_value'].tolist()
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


class ProfessionalTrendChart(QWidget):
    """
    🔥 PROFESSIONAL TREND VISUALIZATION - FRISSÍTETT API ADATOKKAL
    
    Képességek:
    - Hőtérkép style háttér évszakok szerint
    - Gradient effect vonalak (4 rétegű alpha)
    - Lineáris regresszió trendvonal + konfidencia
    - Modern glassmorphism UI design
    - Professional annotation és legend
    """
    
    def __init__(self):
        super().__init__()
        self.setup_chart()
        self.trend_data = None
        
    def setup_chart(self):
        """Professional matplotlib chart inicializálás"""
        self.figure = Figure(figsize=(12, 8), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        
        # Modern styling
        self.figure.patch.set_facecolor('#f8f9fa')
        
    def update_chart(self, trend_data: Dict):
        """
        🔥 CHART FRISSÍTÉS API TREND ADATOKKAL
        
        Args:
            trend_data: TrendDataProcessor által számított eredmények
        """
        try:
            self.trend_data = trend_data
            self.figure.clear()
            
            # Chart setup
            ax = self.figure.add_subplot(111)
            
            # Chart adatok kinyerése
            chart_data = trend_data['chart_data']
            dates = pd.to_datetime(chart_data['dates'])
            values = np.array(chart_data['values'])
            trend_line = np.array(chart_data['trend_line'])
            ci_upper = np.array(chart_data['ci_upper'])
            ci_lower = np.array(chart_data['ci_lower'])
            
            logger.info(f"📊 CHART UPDATE: {len(dates)} havi pont, {trend_data['total_days']} napi adat")
            
            # 🎨 HŐTÉRKÉP HÁTTÉR (évszakok szerint)
            self.create_seasonal_background(ax, dates)
            
            # 🔥 95% KONFIDENCIA INTERVALLUM (árnyékolt terület)
            ax.fill_between(dates, ci_lower, ci_upper, 
                          alpha=0.2, color='gray', label='95% konfidencia')
            
            # 📈 GRADIENT VONALAK (4 rétegű alpha átmenet)
            self.plot_gradient_lines(ax, dates, values)
            
            # 📊 LINEÁRIS REGRESSZIÓ TRENDVONAL
            ax.plot(dates, trend_line, '--', color='#ff1493', linewidth=3, 
                   label=f'Trend ({trend_data["trend_per_decade"]:+.2f}/évtized)', alpha=0.8)
            
            # 🎨 PROFESSIONAL STYLING
            self.apply_professional_styling(ax, trend_data)
            
            # Legend és grid - JAVÍTÁS: Legend kívülre helyezés
            ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1), borderaxespad=0, framealpha=0.9)
            ax.grid(True, alpha=0.3)
            
            # Layout és refresh - JAVÍTÁS: Hely a legend számára
            self.figure.tight_layout(rect=[0, 0, 0.85, 1])  # 85% width, helyot hagy a legend-nek
            self.canvas.draw()
            
            logger.info("✅ Chart successfully updated")
            
        except Exception as e:
            logger.error(f"❌ Chart update hiba: {e}")
            logger.exception("Chart error stacktrace:")
    
    def create_seasonal_background(self, ax, dates):
        """Évszakos hőtérkép háttér létrehozása"""
        try:
            # Évszak színek
            season_colors = {
                'tavasz': '#90EE90',  # világos zöld
                'nyár': '#FFD700',    # arany
                'ősz': '#FF8C00',     # narancs  
                'tél': '#87CEEB'      # világos kék
            }
            
            # Évszak meghatározás hónapok szerint
            def get_season(month):
                if month in [3, 4, 5]:
                    return 'tavasz'
                elif month in [6, 7, 8]:
                    return 'nyár'
                elif month in [9, 10, 11]:
                    return 'ősz'
                else:
                    return 'tél'
            
            # Hátér színezés hónapok szerint
            for i, date in enumerate(dates):
                if i < len(dates) - 1:
                    season = get_season(date.month)
                    color = season_colors[season]
                    
                    ax.axvspan(date, dates[i+1], alpha=0.1, color=color)
                    
        except Exception as e:
            logger.warning(f"⚠️ Seasonal background hiba: {e}")
    
    def plot_gradient_lines(self, ax, dates, values):
        """4 rétegű gradient effect vonalak"""
        try:
            # Gradient rétegek (csökkenő vastagság és alpha)
            line_configs = [
                {'linewidth': 4, 'alpha': 0.3, 'color': '#ff6b35'},
                {'linewidth': 3, 'alpha': 0.5, 'color': '#ff8c42'}, 
                {'linewidth': 2, 'alpha': 0.7, 'color': '#ffa726'},
                {'linewidth': 1.5, 'alpha': 0.9, 'color': '#ffb74d'}
            ]
            
            for i, config in enumerate(line_configs):
                ax.plot(dates, values, **config, 
                       label='Havi átlag' if i == 0 else "")
                       
        except Exception as e:
            logger.warning(f"⚠️ Gradient lines hiba: {e}")
            # Fallback: egyszerű vonal
            ax.plot(dates, values, color='#ff6b35', linewidth=2, label='Havi átlag')
    
    def apply_professional_styling(self, ax, trend_data):
        """Professional chart styling alkalmazása"""
        try:
            # Címek és címkék
            settlement = trend_data['settlement_name']
            parameter = trend_data['parameter']
            time_range = trend_data['time_range']
            
            ax.set_title(f'📈 {settlement} - {parameter} trend elemzés ({time_range})',
                        fontsize=16, fontweight='bold', pad=20)
            
            # Y tengely címke paraméter alapján
            if 'hőmérséklet' in parameter.lower():
                ax.set_ylabel('Hőmérséklet (°C)', fontsize=12)
            elif 'csapadék' in parameter.lower():
                ax.set_ylabel('Csapadék (mm)', fontsize=12)
            elif 'szél' in parameter.lower():
                ax.set_ylabel('Szélsebesség (km/h)', fontsize=12)
            else:
                ax.set_ylabel('Érték', fontsize=12)
            
            ax.set_xlabel('Dátum', fontsize=12)
            
            # X tengely dátum formázás
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            ax.xaxis.set_major_locator(mdates.YearLocator())
            ax.xaxis.set_minor_locator(mdates.MonthLocator((1, 7)))
            
            # Dátum címkék forgatása
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
            
            # Modern színséma
            ax.set_facecolor('#fdfdfd')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('#cccccc')
            ax.spines['bottom'].set_color('#cccccc')
            
        except Exception as e:
            logger.warning(f"⚠️ Professional styling hiba: {e}")


class CompactSideStatisticsTable(QWidget):
    """
    🎯 SIDE PANEL STATISTICS - FINAL OPTIMALIZÁLT MÉRETEZÉS!
    
    🔥 FINAL MÉRETEZÉSI OPTIMALIZÁCIÓK:
    - Teljes container kihasználás (nincs fix width constraint)
    - NAGY betűméret (16px) és padding (20px)
    - NAGY sorok (45px magasság)
    - Dinamikus oszlop stretch (mind a 4 oszlop)
    - Optimalizált container layout (minimal margins)
    - Post-update sizing optimization
    
    EREDMÉNY:
    - Mind a 12 statisztikai adat NAGY, olvasható formában
    - 2 oszlopos layout kitölti a rendelkezésre álló helyet  
    - 6 sor magasság, NAGY cellák (45px magasság)
    - Nincs vízszintes scroll
    - Professional, tágas megjelenés
    """
    
    def __init__(self):
        super().__init__()
        self.setup_table()
        
    def setup_table(self):
        """DINAMIKUS 2 oszlopos side panel táblázat beállítása - FINAL MÉRETEZÉS"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # NINCS MARGIN -> több hely
        
        # Táblázat létrehozása - 4 OSZLOP (Mutató1, Érték1, Mutató2, Érték2)
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setRowCount(6)  # Fix 6 sor
        self.table.setHorizontalHeaderLabels(["Mutató", "Érték", "Mutató", "Érték"])
        
        # 🔥 KRITIKUS MÉRETEZÉSI JAVÍTÁSOK
        self.apply_dynamic_sizing()
        self.apply_statistics_table_style()
        
        # DINAMIKUS LAYOUT - kitölti a rendelkezésre álló helyet
        layout.addWidget(self.table, stretch=1)  # Stretch=1 -> kitölti a helyet
        self.setLayout(layout)
        
        # Placeholder megjelenítése
        self.show_placeholder()
    
    def apply_dynamic_sizing(self):
        """🔥 DINAMIKUS MÉRETEZÉS ALKALMAZÁSA - FIX MINDEN SIZING PROBLÉMA"""
        from PySide6.QtWidgets import QSizePolicy, QHeaderView
        
        # 1. TELJES SZÉLESSÉGI STRETCH - MINDEN OSZLOP
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)  # MINDEN OSZLOP STRETCH
        header.setStretchLastSection(True)
        header.setDefaultSectionSize(100)  # Default szélesség növelése
        
        # 2. SIZEPOLICY EXPLICIT BEÁLLÍTÁS  
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # 3. MINIMÁLIS MÉRETEK NÖVELÉSE
        self.table.setMinimumHeight(300)  # NAGYOBB MIN MAGASSÁG: 250 → 300px
        self.table.setMinimumWidth(450)   # Nagyobb minimum szélesség
        
        # 4. TÁBLÁZAT VISELKEDÉS OPTIMALIZÁLÁS
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # NINCS H-SCROLL!
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        
        # 5. ROW HEIGHT NÖVELÉS - NAGYOBB SOROK!
        self.table.verticalHeader().setDefaultSectionSize(45)  # NAGY SOROK: 35 → 45px
        
    def apply_statistics_table_style(self):
        """🔥 NAGYOBB, OLVASHATÓ STYLING ALKALMAZÁSA - FINAL VERSION"""
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                gridline-color: #dee2e6;
                font-size: 16px;  /* NAGY BETŰMÉRET: 14 → 16px! */
                font-weight: 500;
                selection-background-color: #e3f2fd;
            }
            QTableWidget::item {
                padding: 20px 12px;  /* NAGY PADDING: 15 → 20px! */
                border-bottom: 1px solid #e9ecef;
                border-right: 1px solid #e9ecef;
                text-align: center;
            }
            QHeaderView::section {
                background-color: #e9ecef;
                border: 1px solid #dee2e6;
                padding: 15px 12px;  /* NAGY HEADER PADDING: 12 → 15px */
                font-weight: bold;
                font-size: 14px;  /* NAGYOBB HEADER BETŰ: 13 → 14px */
                text-align: center;
            }
            QTableWidget::item:selected {
                background-color: #cce5ff;
                color: #000;
            }
        """)
    
    def show_placeholder(self):
        """Placeholder megjelenítése adatok hiányában"""
        placeholders = [
            ("🎯 Trend", "Nincs adat", "📅 Időszak", "Nincs adat"),
            ("🎯 Megbízhatóság", "Nincs adat", "📅 Évek száma", "Nincs adat"),
            ("🎯 Szignifikancia", "Nincs adat", "📊 Elemzett napok", "Nincs adat"),
            ("📊 Átlagérték", "Nincs adat", "📊 Legkisebb érték", "Nincs adat"),
            ("📊 Legnagyobb érték", "Nincs adat", "📊 Szórás", "Nincs adat"),
            ("🌍 Adatforrás", "Nincs adat", "📊 P-érték", "Nincs adat")
        ]
        
        for i, (mutato1, ertek1, mutato2, ertek2) in enumerate(placeholders):
            self.table.setItem(i, 0, QTableWidgetItem(mutato1))
            self.table.setItem(i, 1, QTableWidgetItem(ertek1))
            self.table.setItem(i, 2, QTableWidgetItem(mutato2))
            self.table.setItem(i, 3, QTableWidgetItem(ertek2))
        
        # Sor magasság optimalizálása
        self.table.resizeRowsToContents()
    
    def optimize_table_sizing(self):
        """🔥 TÁBLÁZAT MÉRETEZÉS OPTIMALIZÁLÁS FRISSÍTÉS UTÁN"""
        from PySide6.QtWidgets import QHeaderView
        
        # 1. OSZLOPOK EGYENLETES ELOSZTÁSA
        self.table.resizeColumnsToContents()
        
        # 2. HEADER STRETCH MODE ÚJRA ALKALMAZÁSA
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        
        # 3. MINIMUM OSZLOP SZÉLESSÉGEK BEÁLLÍTÁSA
        total_width = self.table.width()
        min_col_width = max(80, total_width // 4)  # Minimum 80px vagy 1/4 szélesség
        
        for col in range(4):
            header.setMinimumSectionSize(min_col_width)
        
        # 4. ROW HEIGHT OPTIMALIZÁLÁS
        self.table.resizeRowsToContents()
        
        # 5. VIEWPORT UPDATE
        self.table.viewport().update()
    
    def update_statistics(self, trend_data: Dict):
        """
        🎯 2 OSZLOPOS STATISTICS FRISSÍTÉSE - MIND A 12 ADAT!
        
        Args:
            trend_data: TrendDataProcessor eredményei
        """
        try:
            logger.info("🎯 TELJES DINAMIKUS STATISTICS FRISSÍTÉS KEZDÉSE")
            
            # ADATOK ELŐKÉSZÍTÉSE
            
            # 1. TREND VÁLTOZÁS
            trend_value = trend_data['trend_per_decade']
            if 'hőmérséklet' in trend_data['parameter'].lower():
                trend_unit = "°C/évtized"
            elif 'csapadék' in trend_data['parameter'].lower():
                trend_unit = "mm/évtized"
            elif 'szél' in trend_data['parameter'].lower():
                trend_unit = "km/h/évtized"
            else:
                trend_unit = "/évtized"
            trend_display = f"{trend_value:+.2f} {trend_unit}"
            
            # 2. MEGBÍZHATÓSÁG (R²)
            r2 = trend_data['r_squared']
            if r2 > 0.7:
                reliability_level = "Magas"
            elif r2 > 0.4:
                reliability_level = "Közepes"
            else:
                reliability_level = "Alacsony"
            reliability_display = f"{r2:.3f} ({reliability_level})"
            
            # 3. SZIGNIFIKANCIA
            significance_display = trend_data['significance']
            
            # 4. ALAPSTATISZTIKÁK
            stats = trend_data['statistics']
            if 'hőmérséklet' in trend_data['parameter'].lower():
                unit = "°C"
            elif 'csapadék' in trend_data['parameter'].lower():
                unit = "mm"
            elif 'szél' in trend_data['parameter'].lower():
                unit = "km/h"
            else:
                unit = ""
            
            avg_display = f"{stats['mean']:.1f} {unit}"
            min_display = f"{stats['min']:.1f} {unit}"
            max_display = f"{stats['max']:.1f} {unit}"
            std_display = f"{stats['std']:.1f} {unit}"
            
            # 5. IDŐSZAK ÉS ADATFORRÁS
            period_display = f"{trend_data['start_date']} → {trend_data['end_date']}"
            years_display = f"{trend_data['years']} év"
            days_display = f"{trend_data['total_days']:,} nap"
            provider_display = "🌍 Open-Meteo" if trend_data['data_source'] == 'open-meteo' else "💎 Meteostat"
            
            # 6. P-ÉRTÉK
            p_val = trend_data['p_value']
            if p_val < 0.001:
                p_display = "< 0.001"
            else:
                p_display = f"{p_val:.3f}"
            
            # 🎯 2 OSZLOPOS ADATOK ÖSSZEÁLLÍTÁSA (6 sor)
            statistics_data = [
                # Sor 1: Trend vs Időszak
                ("🎯 Trend", trend_display, "📅 Időszak", period_display),
                # Sor 2: Megbízhatóság vs Évek
                ("🎯 Megbízhatóság", reliability_display, "📅 Évek száma", years_display),
                # Sor 3: Szignifikancia vs Napok
                ("🎯 Szignifikancia", significance_display, "📊 Elemzett napok", days_display),
                # Sor 4: Átlag vs Minimum
                ("📊 Átlagérték", avg_display, "📊 Legkisebb érték", min_display),
                # Sor 5: Maximum vs Szórás
                ("📊 Legnagyobb érték", max_display, "📊 Szórás", std_display),
                # Sor 6: Adatforrás vs P-érték
                ("🌍 Adatforrás", provider_display, "📊 P-érték", p_display)
            ]
            
            # TÁBLÁZAT FELTÖLTÉSE
            for i, (mutato1, ertek1, mutato2, ertek2) in enumerate(statistics_data):
                
                # BAL OSZLOP (fontosabb adatok)
                mutato1_item = QTableWidgetItem(mutato1)
                ertek1_item = QTableWidgetItem(ertek1)
                
                # JOBB OSZLOP (kiegészítő adatok)
                mutato2_item = QTableWidgetItem(mutato2)
                ertek2_item = QTableWidgetItem(ertek2)
                
                # STYLING - Trend adatok kiemelése
                if "🎯" in mutato1:
                    font = mutato1_item.font()
                    font.setBold(True)
                    mutato1_item.setFont(font)
                    ertek1_item.setFont(font)
                    mutato1_item.setBackground(QColor("#fff3cd"))  # Sárga kiemelés
                    ertek1_item.setBackground(QColor("#fff3cd"))
                
                # STYLING - Időszak/évek kiemelése
                if "📅" in mutato2:
                    font = mutato2_item.font()
                    font.setBold(True)
                    mutato2_item.setFont(font)
                    ertek2_item.setFont(font)
                    mutato2_item.setBackground(QColor("#d4edda"))  # Zöld kiemelés
                    ertek2_item.setBackground(QColor("#d4edda"))
                
                # Táblázat feltöltése
                self.table.setItem(i, 0, mutato1_item)
                self.table.setItem(i, 1, ertek1_item)
                self.table.setItem(i, 2, mutato2_item)
                self.table.setItem(i, 3, ertek2_item)
            
            # Sor magasság optimalizálása
            self.table.resizeRowsToContents()
            
            # 🔥 DINAMIKUS MÉRETEZÉS ALKALMAZÁSA FRISSÍTÉS UTÁN
            self.optimize_table_sizing()
            
            logger.info(f"✅ Teljes dinamikus statistics frissítve: 12 mutató, teljes méretezés")
            
        except Exception as e:
            logger.error(f"❌ Teljes dinamikus statistics update hiba: {e}")
            logger.exception("Teljes dinamikus statistics error stacktrace:")
            self.show_error_message(f"Hiba: {str(e)}")
    
    def show_error_message(self, error_msg: str):
        """Hibaüzenet megjelenítése a teljes dinamikus táblázatban"""
        error_data = [
            ("❌ Hiba", "Számítási hiba", "❌ Hiba", "Számítási hiba"),
            ("Részletek", error_msg[:15] + "...", "Állapot", "Sikertelen"),
            ("", "", "", ""),
            ("", "", "", ""),
            ("", "", "", ""),
            ("", "", "", "")
        ]
        
        for i, (mutato1, ertek1, mutato2, ertek2) in enumerate(error_data):
            self.table.setItem(i, 0, QTableWidgetItem(mutato1))
            self.table.setItem(i, 1, QTableWidgetItem(ertek1))
            self.table.setItem(i, 2, QTableWidgetItem(mutato2))
            self.table.setItem(i, 3, QTableWidgetItem(ertek2))
        
        self.table.resizeRowsToContents()



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
    
    def run(self):
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
    🔥 MAIN TREND ANALYTICS TAB - TELJES INTEGRÁCIÓ v3.3 (QSplitter)
    
    KRITIKUS JAVÍTÁSOK v3.3:
    - 🔧 QSplitter(Qt.Horizontal) implementáció grafikon és statisztikák között
    - 🔧 Felhasználó által állítható méretarány (kezdeti: 67% grafikon, 33% statisztika)
    - 🔧 QScrollArea a statisztikai táblázat számára (jobb olvashatóság kis képernyőn)
    - 🔧 Meglévő funkciók és UI-elemek változatlanul megmaradtak
    
    LAYOUT STRUKTÚRA v3.3:
    ┌───────────────────────────────────────────────────────────┐
    │                    HEADER + CONTROLS                      │
    ├─────────────────────┬─────────────────────────────────────┤
    │  📈 TREND CHART     │ 📊 STATISTICS (QScrollArea-ban)     │
    │  (QSplitter bal)    │ (QSplitter jobb)                    │
    │  Stretch: 2 (67%)   │ Stretch: 1 (33%)                   │
    │                     │ ┌─────────────────────────────────┐ │
    │  Professional       │ │ NAGY BETŰMÉRET + TÁGAS CELLÁK  │ │
    │  Chart + Legend     │ │ 4 OSZLOP STRETCH               │ │
    │  + Confidence       │ │ TELJES DINAMIKUS MÉRETEZÉS     │ │
    │  + Seasonal BG      │ └─────────────────────────────────┘ │
    └─────────────────────┴─────────────────────────────────────┘
    
    KORÁBBI v3.0-3.2 FUNKCIÓK:
    - Hungarian_settlements.db koordináta lekérdezés
    - Weather_client.py multi-year API hívások  
    - 5-10-25-55 éves trend opciók
    - Professional trend számítás és vizualizáció
    - Signal-based communication
    
    Támogatott paraméterek:
    - 🥶 Minimum hőmérséklet (temperature_2m_min)
    - 🔥 Maximum hőmérséklet (temperature_2m_max)
    - 🌡️ Átlag hőmérséklet (temperature_2m_mean)
    - 🌧️ Csapadékmennyiség (precipitation_sum)
    - 💨 Szélsebesség (windspeed_10m_max)
    - 💨 Széllökések (windgusts_10m_max)
    """
    
    # Signals for main window communication
    analysis_started = Signal()
    analysis_completed = Signal(dict)
    error_occurred = Signal(str)
    location_selected = Signal(str, float, float)  # name, lat, lon
    
    def __init__(self):
        super().__init__()
        self.current_worker = None
        self.setup_ui()
        self.connect_signals()
        
        logger.info("🔥 TrendAnalyticsTab v3.3 inicializálva (QSplitter implementáció)")
    
    def setup_ui(self):
        """🔧 UI SETUP - QSplitter implementáció v3.3"""
        main_layout = QVBoxLayout()
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Controls panel
        controls = self.create_controls_panel()
        main_layout.addWidget(controls)
        
        # 🔧 QSplitter IMPLEMENTÁCIÓ (v3.3 REFAKTOR)
        content_splitter = QSplitter(Qt.Horizontal)
        content_splitter.setChildrenCollapsible(False)  # Nem engedünk teljes összecsukást
        
        # Chart area (bal oldal) - változatlan funkciók
        chart_container = self.create_chart_container()
        chart_container.setMinimumHeight(400)
        chart_container.setMinimumWidth(600)  # Minimum szélesség a chartnak
        content_splitter.addWidget(chart_container)
        
        # 🔧 STATISTICS AREA - QScrollArea becsomagolással
        stats_scroll_area = self.create_scrollable_statistics_area()
        stats_scroll_area.setMinimumWidth(400)  # Minimum szélesség a statisztikáknak
        content_splitter.addWidget(stats_scroll_area)
        
        # 🔧 KEZDETI MÉRETARÁNY BEÁLLÍTÁSA: 67% chart, 33% stats
        content_splitter.setSizes([2, 1])  # 2:1 arány
        content_splitter.setStretchFactor(0, 2)  # Chart stretch: 2
        content_splitter.setStretchFactor(1, 1)  # Stats stretch: 1
        
        # QSplitter styling
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
        
        logger.info("✅ QSplitter layout beállítva: grafikon bal (67%), statisztika jobb (33%)")
    
    def create_header(self) -> QWidget:
        """Professional header létrehozása"""
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
        title = QLabel("📈 Trend Elemzések")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setStyleSheet("color: white; margin: 0;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Hosszú távú klimatikus trendek elemzése lineáris regresszióval és professzionális vizualizációkkal")
        subtitle.setFont(QFont("Arial", 11))
        subtitle.setStyleSheet("color: rgba(255,255,255,0.9); margin: 5px 0 0 0;")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        header.setLayout(layout)
        return header
    
    def create_controls_panel(self) -> QWidget:
        """🔥 ELEMZÉSI PARAMÉTEREK PANEL"""
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
        self.analyze_button = QPushButton("🚀 Trend Elemzés Indítása")
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
    
    def create_chart_container(self) -> QWidget:
        """Chart container létrehozása"""
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
        chart_title = QLabel("📈 Trend Vizualizáció")
        chart_title.setFont(QFont("Arial", 14, QFont.Bold))
        chart_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(chart_title)
        
        # Chart widget
        self.chart = ProfessionalTrendChart()
        layout.addWidget(self.chart)
        
        container.setLayout(layout)
        return container
    
    def create_scrollable_statistics_area(self) -> QScrollArea:
        """
        🔧 QScrollArea-BA CSOMAGOLT STATISZTIKAI TÁBLÁZAT (v3.3)
        
        Ez a metódus létrehozza a statisztikai táblázatot QScrollArea-ban,
        hogy kis képernyőkön is olvasható legyen minden adat.
        """
        # QScrollArea létrehozása
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)  # Tartalom automatikus méretezése
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
        
        # Belső widget a statisztikáknak
        stats_widget = QWidget()
        stats_layout = QVBoxLayout()
        stats_layout.setContentsMargins(10, 10, 10, 10)
        
        # Statistics címke
        stats_title = QLabel("📊 Statisztikai Mutatók")
        stats_title.setFont(QFont("Arial", 14, QFont.Bold))
        stats_title.setAlignment(Qt.AlignCenter)
        stats_title.setStyleSheet("color: #495057; margin-bottom: 10px;")
        stats_layout.addWidget(stats_title)
        
        # 🔧 STATISTICS TABLE HOZZÁADÁSA
        self.statistics_table = CompactSideStatisticsTable()
        stats_layout.addWidget(self.statistics_table, stretch=1)
        
        # Stretch spacer a végén
        stats_layout.addStretch()
        
        stats_widget.setLayout(stats_layout)
        scroll_area.setWidget(stats_widget)
        
        logger.info("✅ QScrollArea-ba csomagolt statisztikai terület létrehozva")
        return scroll_area
    
    def connect_signals(self):
        """Signal connections beállítása"""
        # Analyze button
        self.analyze_button.clicked.connect(self.start_trend_analysis)
        
        # Location selection
        self.location_combo.currentTextChanged.connect(self.on_location_changed)
    
    def on_location_changed(self, location_name: str):
        """Location selection kezelése"""
        if location_name and len(location_name.strip()) > 2:
            # Get coordinates for location
            processor = TrendDataProcessor()
            coordinates = processor.get_settlement_coordinates(location_name.strip())
            
            if coordinates:
                lat, lon = coordinates
                logger.info(f"📍 Location selected: {location_name} ({lat:.4f}, {lon:.4f})")
                self.location_selected.emit(location_name, lat, lon)
    
    def start_trend_analysis(self):
        """🔥 TREND ELEMZÉS INDÍTÁSA"""
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
            
            logger.info(f"🚀 TREND ANALYSIS START: {location} - {parameter} - {time_range}")
            
            # UI update
            self.analyze_button.setEnabled(False)
            self.analyze_button.setText("⏳ Elemzés folyamatban...")
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
            logger.error(f"❌ Trend analysis start hiba: {e}")
            self.on_analysis_error(f"Elemzés indítási hiba: {str(e)}")
    
    def on_analysis_completed(self, trend_results: Dict):
        """🎉 TREND ELEMZÉS BEFEJEZÉSE"""
        try:
            logger.info(f"🎉 TREND ANALYSIS COMPLETED: {trend_results['settlement_name']}")
            
            # Chart frissítése
            self.chart.update_chart(trend_results)
            logger.info("✅ Chart frissítve")
            
            # 🎯 STATISTICS FRISSÍTÉSE (QScrollArea-ban)
            logger.info("🎯 Teljes dinamikus statistics frissítése kezdése...")
            self.statistics_table.update_statistics(trend_results)
            logger.info("✅ Teljes dinamikus statistics frissítve (QScrollArea-ban)")
            
            # Signal emission
            self.analysis_completed.emit(trend_results)
            
        except Exception as e:
            logger.error(f"❌ Analysis completion handling hiba: {e}")
            self.on_analysis_error(f"Eredmény feldolgozási hiba: {str(e)}")
    
    def on_analysis_error(self, error_message: str):
        """❌ TREND ELEMZÉS HIBA KEZELÉSE"""
        logger.error(f"❌ TREND ANALYSIS ERROR: {error_message}")
        
        # Error display in chart
        self.chart.figure.clear()
        ax = self.chart.figure.add_subplot(111)
        ax.text(0.5, 0.5, f"❌ Hiba történt:\n{error_message}", 
               ha='center', va='center', transform=ax.transAxes,
               fontsize=14, color='red')
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1) 
        ax.set_xticks([])
        ax.set_yticks([])
        self.chart.canvas.draw()
        
        # Signal emission
        self.error_occurred.emit(error_message)
    
    def on_worker_finished(self):
        """Worker thread befejezése"""
        # UI reset
        self.analyze_button.setEnabled(True)
        self.analyze_button.setText("🚀 Trend Elemzés Indítása")
        self.progress_bar.setVisible(False)
        
        # Worker cleanup
        if self.current_worker:
            self.current_worker.deleteLater()
            self.current_worker = None
        
        logger.info("✅ Worker thread finished and cleaned up")
    
    def set_location(self, location_name: str, latitude: float, longitude: float):
        """External location setting (from other components)"""
        self.location_combo.setCurrentText(location_name)
        self.on_location_changed(location_name)
        
        logger.info(f"📍 External location set: {location_name} ({latitude:.4f}, {longitude:.4f})")


# Theme integration
def register_trend_analytics_theme(theme_manager: ThemeManager):
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
    window.setWindowTitle("🔧 Trend Analytics v3.3 - QSplitter Refaktor!")
    window.resize(1400, 900)
    window.show()
    
    sys.exit(app.exec())