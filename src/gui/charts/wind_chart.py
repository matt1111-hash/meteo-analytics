#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global Weather Analyzer - Wind Gusts Chart
Széllökés grafikon widget professzionális vizualizációval.

🌪️ MAGYAR METEOROLÓGIAI SZABVÁNY: 43-61-90-119 km/h küszöbök
🎨 TÉMA INTEGRÁCIÓ: ColorPalette wind színek használata
🔧 KRITIKUS JAVÍTÁS: Magyar szélsebesség-kategóriák + SIMPLIFIED THEMEMANAGER
✅ wind_gusts_max prioritás → windspeed_10m_max fallback rendszer
✅ Magyar szélkategóriák: Erős szél (43), Viharos szél (61), Erős vihar (90), Orkán (119)
✅ Piros (#C43939) téma támogatás
✅ Élethű széllökés megjelenítés VALÓDI API adatokkal
✅ Professzionális kategorizálás magyar terminológiával
"""

from typing import Optional, Dict, Any
import pandas as pd

from matplotlib.dates import DateFormatter, MonthLocator
import matplotlib.pyplot as plt

from PySide6.QtWidgets import QWidget

from .base_chart import WeatherChart
from ..theme_manager import get_current_colors


class WindChart(WeatherChart):
    """
    🌪️ MAGYAR METEOROLÓGIAI SZABVÁNY: Széllökés grafikon widget - MAGYAR SZÉLKATEGÓRIÁK + SIMPLIFIED THEMEMANAGER.
    🎨 TÉMA INTEGRÁCIÓ: ColorPalette wind színek használata
    ✅ wind_gusts_max prioritás → windspeed_10m_max fallback rendszer
    ✅ Magyar szélkategóriák: Erős szél (43), Viharos szél (61), Erős vihar (90), Orkán (119)
    ✅ Élethű széllökés megjelenítés VALÓDI API adatokkal
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(figsize=(12, 6), parent=parent)
        self.chart_title = "🌪️ Széllökések változása"  # 🌪️ WIND GUSTS CÍM
        self.y_label = "Széllökések (km/h)"  # 🌪️ WIND GUSTS LABEL
    
    def update_data(self, data: Dict[str, Any]) -> None:
        """
        🔧 KRITIKUS JAVÍTÁS: Duplikáció-mentes szél chart frissítés + SIMPLIFIED THEMEMANAGER.
        """
        print("💨 DEBUG: WindChart.update_data() - MAGYAR SZABVÁNY + SIMPLIFIED THEMEMANAGER VERZIÓ")
        
        try:
            if self._is_updating:
                return
            
            self._is_updating = True
            
            df = self._extract_wind_data(data)
            if df.empty:
                print("⚠️ DEBUG: Üres DataFrame, szél chart törlése")
                self.clear_chart()
                return
            
            self.current_data = df
            
            # === KRITIKUS: TELJES FIGURE TÖRLÉSE ===
            print("🧹 DEBUG: Wind Figure.clear() - DUPLIKÁCIÓ ELLEN")
            self.figure.clear()
            self.ax = self.figure.add_subplot(111)
            
            # 🎨 TÉMA ALKALMAZÁSA
            self._apply_theme_to_chart()
            
            self._plot_wind(df)
            
            self.draw()
            self._is_updating = False
            
            print("✅ DEBUG: WindChart frissítés kész - MAGYAR SZABVÁNY + THEMED")
            
        except Exception as e:
            print(f"❌ DEBUG: Szél chart hiba: {e}")
            self._is_updating = False
            self.clear_chart()
    
    def _extract_wind_data(self, data: Dict[str, Any]) -> pd.DataFrame:
        """
        🌪️ KRITIKUS JAVÍTÁS: Széllökés adatok kinyerése - WIND GUSTS PRIORITÁS + FALLBACK.
        
        PRIORITÁS RENDSZER:
        1. wind_gusts_max (óránkénti→napi max széllökések) ⭐ ELSŐDLEGES
        2. windspeed_10m_max (napi max szélsebesség) ⭐ FALLBACK
        3. Hibaüzenet ha egyik sem elérhető
        """
        daily_data = data.get("daily", {})
        dates = daily_data.get("time", [])
        
        # 🌪️ WIND GUSTS PRIORITÁS: wind_gusts_max ELSŐDLEGESEN
        wind_gusts_max = daily_data.get("wind_gusts_max", [])
        windspeed_10m_max = daily_data.get("windspeed_10m_max", [])  # Fallback
        
        print(f"🌪️ DEBUG: WindChart data sources - wind_gusts_max: {len(wind_gusts_max) if wind_gusts_max else 0}, windspeed_10m_max: {len(windspeed_10m_max) if windspeed_10m_max else 0}")
        
        # Elérhető adatok ellenőrzése
        if not dates:
            print("⚠️ DEBUG: Nincs dátum adat - WindChart nem jeleníthető meg")
            return pd.DataFrame()
        
        # PRIORITÁS KIÉRTÉKELÉS
        windspeed_data = []
        data_source = ""
        
        if wind_gusts_max and len(wind_gusts_max) == len(dates):
            # 🌪️ ELSŐDLEGES: wind_gusts_max használata
            windspeed_data = wind_gusts_max
            data_source = "wind_gusts_max"
            self.chart_title = "🌪️ Széllökések változása"  # Dinamikus cím
            self.y_label = "Széllökések (km/h)"
            print(f"✅ DEBUG: WindChart using PRIMARY source: {data_source}")
        elif windspeed_10m_max and len(windspeed_10m_max) == len(dates):
            # ⚠️ FALLBACK: windspeed_10m_max használata
            windspeed_data = windspeed_10m_max  
            data_source = "windspeed_10m_max"
            self.chart_title = "💨 Szélsebesség változása (Fallback)"  # Jelzés a fallback-ről
            self.y_label = "Szélsebesség (km/h)"
            print(f"⚠️ DEBUG: WindChart using FALLBACK source: {data_source}")
        else:
            print(f"❌ DEBUG: Nincs használható szél adat - WindChart nem jeleníthető meg")
            print(f"   - wind_gusts_max: {len(wind_gusts_max) if wind_gusts_max else 0} elem")
            print(f"   - windspeed_10m_max: {len(windspeed_10m_max) if windspeed_10m_max else 0} elem") 
            print(f"   - dates: {len(dates)} elem")
            return pd.DataFrame()
        
        # DataFrame létrehozása
        df = pd.DataFrame({
            'date': pd.to_datetime(dates),
            'windspeed': windspeed_data,
            '_data_source': data_source  # Debug info
        })
        
        # NaN értékek kezelése
        df = df.dropna()
        
        if df.empty:
            print(f"❌ DEBUG: Üres DataFrame {data_source} adatok után - WindChart nem jeleníthető meg")
        else:
            max_wind = df['windspeed'].max()
            avg_wind = df['windspeed'].mean()
            print(f"✅ DEBUG: WindChart DataFrame kész - {data_source}, max: {max_wind:.1f} km/h, avg: {avg_wind:.1f} km/h")
        
        return df
    
    def _plot_wind(self, df: pd.DataFrame) -> None:
        """
        🌪️ MAGYAR METEOROLÓGIAI SZABVÁNY: Széllökés grafikon rajzolása - MAGYAR SZÉLKATEGÓRIÁK + SIMPLIFIED THEMEMANAGER.
        🎨 SIMPLIFIED THEMEMANAGER INTEGRÁCIÓ: ColorPalette wind színek használata
        ✅ Magyar szélkategóriák: Erős szél (43), Viharos szél (61), Erős vihar (90), Orkán (119)
        """
        print("🎨 DEBUG: _plot_wind() - MAGYAR SZÉLKATEGÓRIÁK + SIMPLIFIED THEMEMANAGER")
        
        # 🔧 KRITIKUS JAVÍTÁS: HELYES API HASZNÁLAT - magyar szélkategória színek
        wind_colors = {
            'moderate': self.color_palette.get_color('success', 'base') or '#10b981',      # Gyenge-mérsékelt szél
            'light': self.color_palette.get_color('success', 'light') or '#86efac',       # Kitöltés szín
            'strong': self.color_palette.get_color('warning', 'base') or '#f59e0b',       # Erős szél (43)
            'stormy': self.color_palette.get_color('warning', 'dark') or '#d97706',       # Viharos szél (61)
            'severe_storm': self.color_palette.get_color('error', 'light') or '#f87171',  # Erős vihar (90)
            'hurricane': self.color_palette.get_color('error', 'base') or '#dc2626'       # Orkán (119)
        }
        
        # Weather színpaletta integrálása
        weather_wind_color = self.weather_colors.get('wind', '#10b981')
        wind_colors['moderate'] = weather_wind_color
        
        current_colors = get_current_colors()
        
        print(f"🎨 DEBUG: Using Magyar szabvány wind colors: {wind_colors}")
        
        # Adatforrás ellenőrzése
        data_source = df['_data_source'].iloc[0] if '_data_source' in df.columns else 'unknown'
        
        # === SZÉLLÖKÉS VONAL + TERÜLET DIAGRAM ===
        
        # Alapvonal és kitöltés
        line_label = "Max széllökések" if data_source == "wind_gusts_max" else "Max szélsebesség (fallback)"
        self.ax.plot(df['date'], df['windspeed'], color=wind_colors['moderate'], linewidth=2.5, alpha=0.9, label=line_label)
        self.ax.fill_between(df['date'], 0, df['windspeed'], alpha=0.3, color=wind_colors['light'])
        
        # === 🌪️ MAGYAR METEOROLÓGIAI SZABVÁNY - SZÉLKATEGÓRIÁK ===
        
        max_wind = df['windspeed'].max() if not df.empty else 50
        
        # 43 km/h - Erős szél (magyar szabvány szerint)
        if max_wind >= 30:  # Csak akkor jelenítjük meg, ha releváns
            self.ax.axhline(y=43, color=wind_colors['strong'], linestyle='--', alpha=0.8, linewidth=2, 
                           label='🌬️ Erős szél (43 km/h)')
        
        # 61 km/h - Viharos szél (magyar szabvány)
        if max_wind >= 45:
            self.ax.axhline(y=61, color=wind_colors['stormy'], linestyle='--', alpha=0.8, linewidth=2, 
                           label='🌪️ Viharos szél (61 km/h)')
        
        # 90 km/h - Erős vihar (magyar szabvány)
        if max_wind >= 70:
            self.ax.axhline(y=90, color=wind_colors['severe_storm'], linestyle='--', alpha=0.8, linewidth=2, 
                           label='⚠️ Erős vihar (90 km/h)')
        
        # 119 km/h - Orkán (magyar szabvány)
        if max_wind >= 100:
            self.ax.axhline(y=119, color=wind_colors['hurricane'], linestyle='--', alpha=0.9, linewidth=2.5, 
                           label='🚨 Orkán (119 km/h)')
        
        # === MAGYAR SZÉLKATEGÓRIÁK ANNOTÁCIÓ ===
        
        # Maximum széllökés kiemelése magyar kategóriával
        if not df.empty:
            max_wind_idx = df['windspeed'].idxmax()
            max_wind_date = df.loc[max_wind_idx, 'date']
            max_wind_val = df.loc[max_wind_idx, 'windspeed']
            
            # Magyar kategorizálás
            if max_wind_val >= 119:
                category_icon = "🚨"
                category_text = "ORKÁN"
                annotation_color = wind_colors['hurricane']
            elif max_wind_val >= 90:
                category_icon = "⚠️"
                category_text = "ERŐS VIHAR"
                annotation_color = wind_colors['severe_storm']
            elif max_wind_val >= 61:
                category_icon = "🌪️"  
                category_text = "VIHAROS SZÉL"
                annotation_color = wind_colors['stormy']
            elif max_wind_val >= 43:
                category_icon = "🌬️"
                category_text = "ERŐS SZÉL"
                annotation_color = wind_colors['strong']
            else:
                category_icon = "💨"
                category_text = "MÉRSÉKELT SZÉL"
                annotation_color = wind_colors['moderate']
            
            # Annotáció a csúcsponthoz
            self.ax.annotate(f'{category_icon} {max_wind_val:.1f} km/h\n({category_text})', 
                            xy=(max_wind_date, max_wind_val), 
                            xytext=(15, 25), textcoords='offset points',
                            bbox=dict(boxstyle='round,pad=0.5', facecolor=current_colors.get('surface_variant', '#f9fafb'), 
                                     edgecolor=annotation_color, alpha=0.9),
                            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.2', color=annotation_color, lw=2))
        
        # Formázás
        self._format_wind_chart(df)
    
    def _format_wind_chart(self, df: pd.DataFrame) -> None:
        """Szél chart formázása + SIMPLIFIED THEMEMANAGER."""
        # 🔧 SIMPLIFIED THEMEMANAGER SZÍNEK
        current_colors = get_current_colors()
        text_color = current_colors.get('on_surface', '#1f2937')
        
        self.ax.set_title(self.chart_title, fontweight='bold', pad=20, color=text_color)
        self.ax.set_xlabel(self.x_label, color=text_color)
        self.ax.set_ylabel(self.y_label, color=text_color)
        
        # Tick színek
        self.ax.tick_params(colors=text_color)
        
        # Dátum formázás
        self.ax.xaxis.set_major_locator(MonthLocator())
        self.ax.xaxis.set_major_formatter(DateFormatter('%Y-%m'))
        
        # Y tengely formázás - magyar szélkategóriákhoz optimalizált
        max_wind = df['windspeed'].max() if not df.empty else 50
        
        # Y-tengely tartomány optimalizálása magyar küszöbökhöz
        if max_wind >= 119:
            y_max = max_wind * 1.1  # Orkán feletti értékekhez
        elif max_wind >= 90:
            y_max = 130  # Orkán küszöbig
        elif max_wind >= 61:
            y_max = 100  # Erős vihar küszöbig
        elif max_wind >= 43:
            y_max = 75   # Viharos szél küszöbig
        else:
            y_max = 55   # Erős szél küszöbig
        
        self.ax.set_ylim(0, y_max)
        
        # Grid és legend + SIMPLIFIED THEMEMANAGER
        if self.grid_enabled:
            grid_color = current_colors.get('border', '#d1d5db')
            grid_alpha = 0.3 if self.theme_manager.get_current_theme() == "light" else 0.2
            self.ax.grid(True, alpha=grid_alpha, linestyle='-', linewidth=0.5, color=grid_color)
        
        if self.legend_enabled:
            legend = self.ax.legend(loc='upper left', framealpha=0.9)
            legend.get_frame().set_facecolor(current_colors.get('surface', '#ffffff'))
            legend.get_frame().set_edgecolor(current_colors.get('border', '#d1d5db'))
        
        # Layout optimalizálás
        self.figure.autofmt_xdate()
        self.figure.tight_layout()