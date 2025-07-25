#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global Weather Analyzer - Multi-Year Comparison Chart
Több év összehasonlító chart widget trend elemzéssel.

📊 MULTI-YEAR COMPARISON CHART: Azonos időszakok összehasonlítása különböző évekből
🎨 TÉMA INTEGRÁCIÓ: ColorPalette trend elemzési színek használata
🔧 KRITIKUS JAVÍTÁS: Duplikáció-mentes frissítés + SIMPLIFIED THEMEMANAGER
✅ Piros (#C43939) téma támogatás
✅ Trend vonalak minden évhez
✅ Szezonális vonalak (tavasz, nyár, ősz, tél)
✅ Statisztikai információk
✅ Optimális legend pozícionálás
"""

from typing import Optional, Dict, Any
import pandas as pd
import numpy as np

from matplotlib.dates import DateFormatter, MonthLocator, DayLocator
import matplotlib.pyplot as plt

from PySide6.QtWidgets import QWidget

from .base_chart import WeatherChart
from ..theme_manager import get_current_colors


class MultiYearComparisonChart(WeatherChart):
    """
    Több év összehasonlító chart - TREND ELEMZÉS + DUPLIKÁCIÓ BUGFIX + SIMPLIFIED THEMEMANAGER.
    Azonos időszakok összehasonlítása különböző évekből.
    🎨 TÉMA INTEGRÁCIÓ: ColorPalette trend elemzési színek használata
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(figsize=(14, 8), parent=parent)
        self.chart_title = "📊 Évek Közötti Összehasonlítás"
        self.comparison_years = []  # Összehasonlítandó évek listája
    
    def update_data(self, data: Dict[str, Any]) -> None:
        """
        🔧 KRITIKUS JAVÍTÁS: Duplikáció-mentes multi-year comparison frissítés + SIMPLIFIED THEMEMANAGER.
        """
        print("📊 DEBUG: MultiYearComparisonChart.update_data() - DUPLIKÁCIÓ BUGFIX + SIMPLIFIED THEMEMANAGER VERZIÓ")
        
        try:
            if self._is_updating:
                return
            
            self._is_updating = True
            
            df = self._extract_yearly_data(data)
            if df.empty:
                print("⚠️ DEBUG: Üres DataFrame, comparison törlése")
                self.clear_chart()
                return
            
            self.current_data = df
            
            # === KRITIKUS: TELJES FIGURE TÖRLÉSE ===
            print("🧹 DEBUG: MultiYear Figure.clear() - DUPLIKÁCIÓ ELLEN")
            self.figure.clear()
            self.ax = self.figure.add_subplot(111)
            
            # 🎨 TÉMA ALKALMAZÁSA
            self._apply_theme_to_chart()
            
            self._plot_multi_year_comparison(df)
            
            self.draw()
            self._is_updating = False
            
            print("✅ DEBUG: MultiYearComparisonChart frissítés kész - DUPLIKÁCIÓ MENTES + THEMED")
            
        except Exception as e:
            print(f"❌ DEBUG: Multi-year comparison chart hiba: {e}")
            self._is_updating = False
            self._plot_comparison_placeholder()
    
    def _extract_yearly_data(self, data: Dict[str, Any]) -> pd.DataFrame:
        """Többévi adatok kinyerése - CSAK VALÓDI API ADATOKKAL."""
        daily_data = data.get("daily", {})
        dates = daily_data.get("time", [])
        temp_max = daily_data.get("temperature_2m_max", [])
        temp_min = daily_data.get("temperature_2m_min", [])
        temp_mean = daily_data.get("temperature_2m_mean", [])
        
        # 🚨 KRITIKUS: CSAK VALÓDI API ADATOK! Számított átlag TILOS!
        if not dates or not temp_max or not temp_min or not temp_mean:
            print("⚠️ DEBUG: Hiányzó többévi adatok - chart nem jeleníthető meg")
            return pd.DataFrame()
        
        # Adatstruktúra hosszak ellenőrzése
        if len(dates) != len(temp_max) or len(dates) != len(temp_min) or len(dates) != len(temp_mean):
            print("❌ DEBUG: Eltérő hosszúságú többévi adatok - chart nem jeleníthető meg")
            return pd.DataFrame()
        
        df = pd.DataFrame({
            'date': pd.to_datetime(dates),
            'temp_max': temp_max,
            'temp_min': temp_min,
            'temp_mean': temp_mean  # CSAK VALÓDI API ADAT!
        })
        
        # Év és nap az évben oszlopok - ezek valódi dátumból számoltak, OK
        df['year'] = df['date'].dt.year
        df['day_of_year'] = df['date'].dt.dayofyear
        df['month_day'] = df['date'].dt.strftime('%m-%d')
        
        # Csak érvényes adatok megtartása
        df = df.dropna()
        
        if df.empty:
            print("⚠️ DEBUG: Nincs érvényes többévi adat - chart nem jeleníthető meg")
        
        return df
    
    def _plot_multi_year_comparison(self, df: pd.DataFrame) -> None:
        """
        Többévi összehasonlítás megrajzolása - DUPLIKÁCIÓ BUGFIX + SIMPLIFIED THEMEMANAGER.
        🎨 SIMPLIFIED THEMEMANAGER INTEGRÁCIÓ: ColorPalette trend színek használata
        """
        print("🎨 DEBUG: _plot_multi_year_comparison() - DUPLIKÁCIÓ MENTES + SIMPLIFIED THEMEMANAGER")
        
        # Évek azonosítása
        years = sorted(df['year'].unique())
        
        if len(years) < 2:
            self._plot_comparison_placeholder()
            return
        
        # 🔧 KRITIKUS JAVÍTÁS: HELYES API HASZNÁLAT - trend színek generálása
        trend_colors = {
            'year_comparison': [
                self.color_palette.get_color('primary', 'base') or '#C43939',  # Piros téma
                self.color_palette.get_color('success', 'base') or '#10b981',
                self.color_palette.get_color('warning', 'base') or '#f59e0b',
                self.color_palette.get_color('error', 'base') or '#dc2626',
                self.color_palette.get_color('info', 'base') or '#6366f1',
                self.color_palette.get_color('primary', 'light') or '#3b82f6'
            ],
            'average_trend': self.color_palette.get_color('info', 'dark') or '#4338ca'
        }
        
        current_colors = get_current_colors()
        text_color = current_colors.get('on_surface', '#1f2937')
        
        print(f"🎨 DEBUG: Using SimplifiedThemeManager trend colors: {trend_colors}")
        
        # Minden év megrajzolása
        for i, year in enumerate(years):
            year_data = df[df['year'] == year].copy()
            color = trend_colors['year_comparison'][i % len(trend_colors['year_comparison'])]
            
            # Átlag hőmérséklet vonala évente
            self.ax.plot(year_data['day_of_year'], year_data['temp_mean'], 
                        color=color, linewidth=2.5, alpha=0.8, label=f'{year}')
            
            # Min-Max tartomány kitöltése (csak az első 2 évnél, hogy ne legyen túl zsúfolt)
            if i < 2:
                self.ax.fill_between(year_data['day_of_year'], 
                                   year_data['temp_min'], year_data['temp_max'],
                                   color=color, alpha=0.1)
        
        # === TREND VONALAK + SIMPLIFIED THEMEMANAGER ===
        
        # Összes év összevont trendje
        if len(df) > 30:  # Csak ha van elég adat
            trend_data = df.groupby('day_of_year')['temp_mean'].mean().reset_index()
            self.ax.plot(trend_data['day_of_year'], trend_data['temp_mean'], 
                        '--', linewidth=3, alpha=0.6, label='Átlagos trend',
                        color=trend_colors['average_trend'])
        
        # === SZEZONÁLIS VONALAK + SIMPLIFIED THEMEMANAGER ===
        
        # 🔧 KRITIKUS JAVÍTÁS: HELYES API HASZNÁLAT - szezonális színek
        seasonal_colors = {
            'spring': self.color_palette.get_color('success', 'light') or '#86efac',
            'summer': self.color_palette.get_color('warning', 'light') or '#fde047',
            'autumn': self.color_palette.get_color('error', 'light') or '#fb7185',
            'winter': self.color_palette.get_color('info', 'light') or '#a5b4fc'
        }
        
        # Tavasz kezdete (március 20.)
        spring_day = 79  # Kb. március 20.
        self.ax.axvline(x=spring_day, color=seasonal_colors['spring'], 
                       linestyle=':', alpha=0.7, label='Tavasz')
        
        # Nyár kezdete (június 21.)
        summer_day = 172  # Kb. június 21.
        self.ax.axvline(x=summer_day, color=seasonal_colors['summer'], 
                       linestyle=':', alpha=0.7, label='Nyár')
        
        # Ősz kezdete (szeptember 23.)
        autumn_day = 266  # Kb. szeptember 23.
        self.ax.axvline(x=autumn_day, color=seasonal_colors['autumn'], 
                       linestyle=':', alpha=0.7, label='Ősz')
        
        # Tél kezdete (december 21.)
        winter_day = 355  # Kb. december 21.
        self.ax.axvline(x=winter_day, color=seasonal_colors['winter'], 
                       linestyle=':', alpha=0.7, label='Tél')
        
        # === FORMÁZÁS + SIMPLIFIED THEMEMANAGER ===
        
        self.ax.set_title(f"{self.chart_title} ({min(years)}-{max(years)})", 
                         fontsize=16, fontweight='bold', pad=20, color=text_color)
        self.ax.set_xlabel("Nap az évben", fontsize=12, color=text_color)
        self.ax.set_ylabel("Átlag hőmérséklet (°C)", fontsize=12, color=text_color)
        
        # Tick színek
        self.ax.tick_params(colors=text_color)
        
        # X tengely hónap címkék
        month_starts = [1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335]
        month_names = ['Jan', 'Feb', 'Már', 'Ápr', 'Máj', 'Jún', 
                      'Júl', 'Aug', 'Szep', 'Okt', 'Nov', 'Dec']
        
        self.ax.set_xticks(month_starts)
        self.ax.set_xticklabels(month_names)
        self.ax.set_xlim(1, 366)
        
        # Grid és legend + SIMPLIFIED THEMEMANAGER
        if self.grid_enabled:
            grid_color = current_colors.get('border', '#d1d5db')
            grid_alpha = 0.3 if self.theme_manager.get_current_theme() == "light" else 0.2
            self.ax.grid(True, alpha=grid_alpha, color=grid_color)
        
        if self.legend_enabled:
            # JAVÍTOTT LEGEND POZÍCIÓ + SIMPLIFIED THEMEMANAGER SZÍNEK
            legend = self.ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', 
                          ncol=1, fontsize=10, framealpha=0.9)
            legend.get_frame().set_facecolor(current_colors.get('surface', '#ffffff'))
            legend.get_frame().set_edgecolor(current_colors.get('border', '#d1d5db'))
        
        # Statisztikai információ + SIMPLIFIED THEMEMANAGER
        stats_text = f"📊 {len(years)} év összehasonlítva\n"
        stats_text += f"📅 Időszak: {years[0]}-{years[-1]}\n"
        stats_text += f"📈 Rekordok száma: {len(df)}"
        
        self.ax.text(0.02, 0.98, stats_text, transform=self.ax.transAxes, 
                    fontsize=10, verticalalignment='top', color=text_color,
                    bbox=dict(boxstyle="round,pad=0.3", 
                             facecolor=current_colors.get('surface_variant', '#f9fafb'),
                             edgecolor=current_colors.get('border', '#d1d5db'), alpha=0.8))
        
        # Layout optimalizálás legend-del
        self.figure.tight_layout(rect=[0, 0, 0.85, 1])
    
    def _plot_comparison_placeholder(self) -> None:
        """Placeholder ha nincs elég valódi adat az összehasonlításhoz - MOCK ADATOK NÉLKÜL + SIMPLIFIED THEMEMANAGER."""
        # Biztosítjuk, hogy az ax standard subplot legyen
        if not hasattr(self, 'ax') or self.ax is None:
            self.ax = self.figure.add_subplot(111)
        
        # 🔧 SIMPLIFIED THEMEMANAGER SZÍNEK
        current_colors = get_current_colors()
        text_color = current_colors.get('on_surface', '#1f2937')
        surface_color = current_colors.get('surface_variant', '#f9fafb')
        
        placeholder_text = "📊 Évek Közötti Összehasonlítás\n\n"
        placeholder_text += "❌ Nincs elég valódi adat\n\n"
        placeholder_text += "Legalább 2 különböző év\n"
        placeholder_text += "valódi adataira van szükség az\n"
        placeholder_text += "összehasonlításhoz.\n\n"
        placeholder_text += "🚨 Mock adatok használata TILOS!"
        
        self.ax.text(0.5, 0.5, placeholder_text, ha='center', va='center', 
                    transform=self.ax.transAxes, fontsize=14, color=text_color,
                    bbox=dict(boxstyle="round,pad=0.5", facecolor=surface_color,
                             edgecolor=current_colors.get('border', '#d1d5db'), alpha=0.8))
        
        self.ax.set_title(self.chart_title, fontsize=16, fontweight='bold', pad=20, color=text_color)
        
        # Tengelyek elrejtése placeholder módban
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        for spine in self.ax.spines.values():
            spine.set_visible(False)