#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global Weather Analyzer - Precipitation Chart
Csapadék grafikon widget professzionális oszlopdiagram vizualizációval.

🌧️ PRECIPITATION CHART: Oszlopdiagram csapadék mennyiségekkel
🎨 TÉMA INTEGRÁCIÓ: ColorPalette precipitation színek használata
🔧 KRITIKUS JAVÍTÁS: Duplikáció-mentes frissítés + SIMPLIFIED THEMEMANAGER
✅ Piros (#C43939) téma támogatás
✅ Színkódolt oszlopok csapadék mennyiség alapján
✅ Statisztikai információk megjelenítése
✅ Valódi API adatok használata
"""

from typing import Optional, Dict, Any
import pandas as pd

from matplotlib.dates import DateFormatter, MonthLocator
import matplotlib.pyplot as plt

from PySide6.QtWidgets import QWidget

from .base_chart import WeatherChart
from ..theme_manager import get_current_colors


class PrecipitationChart(WeatherChart):
    """
    Csapadék grafikon widget - EREDETI MEGTARTVA + DUPLIKÁCIÓ BUGFIX + SIMPLIFIED THEMEMANAGER.
    🎨 TÉMA INTEGRÁCIÓ: ColorPalette precipitation színek használata
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(figsize=(12, 6), parent=parent)
        self.chart_title = "🌧️ Napi csapadék mennyisége"
        self.y_label = "Csapadék (mm)"
    
    def update_data(self, data: Dict[str, Any]) -> None:
        """
        🔧 KRITIKUS JAVÍTÁS: Duplikáció-mentes csapadék chart frissítés + SIMPLIFIED THEMEMANAGER.
        """
        print("🌧️ DEBUG: PrecipitationChart.update_data() - DUPLIKÁCIÓ BUGFIX + SIMPLIFIED THEMEMANAGER VERZIÓ")
        
        try:
            if self._is_updating:
                return
            
            self._is_updating = True
            
            df = self._extract_precipitation_data(data)
            if df.empty:
                print("⚠️ DEBUG: Üres DataFrame, csapadék chart törlése")
                self.clear_chart()
                return
            
            self.current_data = df
            
            # === KRITIKUS: TELJES FIGURE TÖRLÉSE ===
            print("🧹 DEBUG: Precipitation Figure.clear() - DUPLIKÁCIÓ ELLEN")
            self.figure.clear()
            self.ax = self.figure.add_subplot(111)
            
            # 🎨 TÉMA ALKALMAZÁSA
            self._apply_theme_to_chart()
            
            self._plot_precipitation(df)
            
            self.draw()
            self._is_updating = False
            
            print("✅ DEBUG: PrecipitationChart frissítés kész - DUPLIKÁCIÓ MENTES + THEMED")
            
        except Exception as e:
            print(f"❌ DEBUG: Csapadék chart hiba: {e}")
            self._is_updating = False
            self.clear_chart()
    
    def _extract_precipitation_data(self, data: Dict[str, Any]) -> pd.DataFrame:
        """Csapadék adatok kinyerése."""
        daily_data = data.get("daily", {})
        dates = daily_data.get("time", [])
        precipitation = daily_data.get("precipitation_sum", [])
        
        if not dates or not precipitation:
            return pd.DataFrame()
        
        df = pd.DataFrame({
            'date': pd.to_datetime(dates),
            'precipitation': precipitation
        })
        
        return df
    
    def _plot_precipitation(self, df: pd.DataFrame) -> None:
        """
        Csapadék grafikon rajzolása - DUPLIKÁCIÓ BUGFIX + SIMPLIFIED THEMEMANAGER.
        🎨 SIMPLIFIED THEMEMANAGER INTEGRÁCIÓ: ColorPalette precipitation színek használata
        """
        print("🎨 DEBUG: _plot_precipitation() - DUPLIKÁCIÓ MENTES + SIMPLIFIED THEMEMANAGER")
        
        # 🔧 KRITIKUS JAVÍTÁS: HELYES API HASZNÁLAT - csapadék színek
        precip_colors = {
            'none': self.color_palette.get_color('surface_variant', 'base') or '#f3f4f6',
            'light': self.color_palette.get_color('info', 'light') or '#93c5fd',
            'moderate': self.color_palette.get_color('info', 'base') or '#3b82f6',
            'heavy': self.color_palette.get_color('info', 'dark') or '#1e40af'
        }
        
        # Weather színpaletta integrálása
        weather_precip_color = self.weather_colors.get('precipitation', '#3b82f6')
        precip_colors['moderate'] = weather_precip_color
        
        current_colors = get_current_colors()
        
        print(f"🎨 DEBUG: Using SimplifiedThemeManager precipitation colors: {precip_colors}")
        
        # Oszlopdiagram alapszín
        bars = self.ax.bar(df['date'], df['precipitation'], 
                          color=precip_colors['moderate'], alpha=0.7, 
                          edgecolor=current_colors.get('border', '#d1d5db'), linewidth=0.5)
        
        # Színkódolás csapadék mennyiség alapján + SIMPLIFIED THEMEMANAGER
        for i, (date, precip) in enumerate(zip(df['date'], df['precipitation'])):
            if precip > 20:  # Erős csapadék
                bars[i].set_color(precip_colors['heavy'])
            elif precip > 10:  # Közepes csapadék
                bars[i].set_color(precip_colors['moderate'])
            elif precip > 1:  # Gyenge csapadék
                bars[i].set_color(precip_colors['light'])
            else:  # Száraz
                bars[i].set_color(precip_colors['none'])
        
        # Formázás
        self._format_precipitation_chart(df)
    
    def _format_precipitation_chart(self, df: pd.DataFrame) -> None:
        """Csapadék chart formázása + SIMPLIFIED THEMEMANAGER."""
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
        
        # Y tengely formázás
        max_precip = df['precipitation'].max() if not df.empty else 50
        self.ax.set_ylim(0, max_precip * 1.1)
        
        # Grid + SIMPLIFIED THEMEMANAGER
        if self.grid_enabled:
            grid_color = current_colors.get('border', '#d1d5db')
            grid_alpha = 0.3 if self.theme_manager.get_current_theme() == "light" else 0.2
            self.ax.grid(True, alpha=grid_alpha, axis='y', linestyle='-', linewidth=0.5, color=grid_color)
        
        # Statisztika szöveg hozzáadása + SIMPLIFIED THEMEMANAGER
        total_precip = df['precipitation'].sum()
        avg_precip = df['precipitation'].mean()
        self.ax.text(0.02, 0.98, f'Összesen: {total_precip:.1f} mm\nÁtlag: {avg_precip:.1f} mm/nap',
                    transform=self.ax.transAxes, verticalalignment='top', color=text_color,
                    bbox=dict(boxstyle='round', 
                             facecolor=current_colors.get('surface_variant', '#f9fafb'),
                             edgecolor=current_colors.get('border', '#d1d5db'), alpha=0.8))
        
        # Layout optimalizálás
        self.figure.autofmt_xdate()
        self.figure.tight_layout()