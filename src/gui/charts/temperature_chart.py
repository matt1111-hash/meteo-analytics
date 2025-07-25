#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global Weather Analyzer - Enhanced Temperature Chart
Fejlett hőmérséklet grafikon widget professzionális vizualizációval.

🌡️ ENHANCED TEMPERATURE CHART: Színes zónák, trend vonalak, statisztikai elemek
🎨 TÉMA INTEGRÁCIÓ: ColorPalette használata professzionális színekhez
🔧 KRITIKUS JAVÍTÁS: Robusztus update cycle duplikáció nélkül + LEGEND POZÍCIÓ JAVÍTVA
✅ Piros (#C43939) téma támogatás
✅ Professzionális nagy méretű diagramok
✅ Optimális legend elhelyezés
✅ Valódi API adatok használata (mock adatok tiltva)
"""

from typing import Optional, Dict, Any
import pandas as pd
import numpy as np
from datetime import datetime

from matplotlib.dates import DateFormatter, MonthLocator, DayLocator
import matplotlib.pyplot as plt

from PySide6.QtWidgets import QWidget

from .base_chart import WeatherChart
from ..theme_manager import get_current_colors


class EnhancedTemperatureChart(WeatherChart):
    """
    Fejlett hőmérséklet grafikon widget - PROFESSZIONÁLIS NAGY VERZIÓ + DUPLIKÁCIÓ BUGFIX + SIMPLIFIED THEMEMANAGER.
    Színes zónák, trend vonalak, statisztikai elemek.
    🎨 TÉMA INTEGRÁCIÓ: ColorPalette használata professzionális színekhez
    🔧 KRITIKUS JAVÍTÁS: Robusztus update cycle duplikáció nélkül + LEGEND POZÍCIÓ JAVÍTVA
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(figsize=(14, 8), parent=parent)  # NAGY MÉRET
        self.chart_title = "🌡️ Részletes Hőmérséklet Elemzés"
        self.y_label = "Hőmérséklet (°C)"
    
    def update_data(self, data: Dict[str, Any]) -> None:
        """
        🔧 KRITIKUS JAVÍTÁS: Duplikáció-mentes hőmérséklet chart frissítés + SIMPLIFIED THEMEMANAGER SZÍNEK.
        """
        print("🌡️ DEBUG: EnhancedTemperatureChart.update_data() - DUPLIKÁCIÓ BUGFIX + SIMPLIFIED THEMEMANAGER VERZIÓ")
        
        try:
            # Duplikáció ellenőrzés
            if self._is_updating:
                print("⚠️ DEBUG: Update már folyamatban, skip")
                return
            
            self._is_updating = True
            
            df = self._extract_temperature_data(data)
            if df.empty:
                print("⚠️ DEBUG: Üres DataFrame, chart törlése")
                self.clear_chart()
                return
            
            self.current_data = df
            self._last_update_data = data.copy()
            
            # === KRITIKUS: TELJES FIGURE TÖRLÉSE DUPLIKÁCIÓ ELLEN ===
            print("🧹 DEBUG: Figure.clear() hívása duplikáció ellen")
            self.figure.clear()
            self.ax = self.figure.add_subplot(111)
            
            # 🎨 TÉMA ALKALMAZÁSA
            self._apply_theme_to_chart()
            
            # Chart megrajzolása
            self._plot_enhanced_temperature(df)
            
            # Finalizálás
            self.draw()
            self._is_updating = False
            
            print("✅ DEBUG: EnhancedTemperatureChart frissítés kész - DUPLIKÁCIÓ MENTES + THEMED")
            
        except Exception as e:
            print(f"❌ DEBUG: Enhanced hőmérséklet chart hiba: {e}")
            self._is_updating = False
            self.clear_chart()
    
    def _extract_temperature_data(self, data: Dict[str, Any]) -> pd.DataFrame:
        """Hőmérséklet adatok kinyerése - CSAK VALÓDI API ADATOKKAL."""
        daily_data = data.get("daily", {})
        dates = daily_data.get("time", [])
        temp_max = daily_data.get("temperature_2m_max", [])
        temp_min = daily_data.get("temperature_2m_min", [])
        temp_mean = daily_data.get("temperature_2m_mean", [])
        
        # 🚨 KRITIKUS: CSAK VALÓDI API ADATOK! Számított átlag TILOS!
        if not dates or not temp_max or not temp_min or not temp_mean:
            print("⚠️ DEBUG: Hiányzó hőmérséklet adatok - chart nem jeleníthető meg")
            return pd.DataFrame()
        
        # Adatstruktúra hosszak ellenőrzése
        if len(dates) != len(temp_max) or len(dates) != len(temp_min) or len(dates) != len(temp_mean):
            print("❌ DEBUG: Eltérő hosszúságú hőmérséklet adatok - chart nem jeleníthető meg")
            return pd.DataFrame()
        
        df = pd.DataFrame({
            'date': pd.to_datetime(dates),
            'temp_max': temp_max,
            'temp_min': temp_min,
            'temp_mean': temp_mean  # CSAK VALÓDI API ADAT!
        })
        
        # Csak érvényes adatok megtartása
        df = df.dropna()
        
        if df.empty:
            print("⚠️ DEBUG: Nincs érvényes hőmérséklet adat - chart nem jeleníthető meg")
        
        return df
    
    def _plot_enhanced_temperature(self, df: pd.DataFrame) -> None:
        """
        Fejlett hőmérséklet grafikon rajzolása - PROFESSZIONÁLIS STÍLUS + SIMPLIFIED THEMEMANAGER SZÍNEK.
        🎨 SIMPLIFIED THEMEMANAGER INTEGRÁCIÓ: ColorPalette használata professzionális színválasztáshoz
        🔧 KRITIKUS JAVÍTÁS: Az ax.clear() már megtörtént a update_data()-ban.
        """
        print("🎨 DEBUG: _plot_enhanced_temperature() - DUPLIKÁCIÓ MENTES + SIMPLIFIED THEMEMANAGER")
        
        # 🔧 KRITIKUS JAVÍTÁS: HELYES API HASZNÁLAT - weather színpaletta
        temp_colors = {
            'cold': self.color_palette.get_color('info', 'dark') or '#6366f1',
            'moderate': self.color_palette.get_color('primary', 'base') or '#C43939',  # Piros téma
            'warm': self.color_palette.get_color('warning', 'base') or '#f59e0b',
            'hot': self.color_palette.get_color('error', 'base') or '#dc2626',
            'comfort': self.color_palette.get_color('success', 'light') or '#22c55e',
            'trend_up': self.color_palette.get_color('error', 'light') or '#ef4444',
            'trend_down': self.color_palette.get_color('info', 'light') or '#8b5cf6',
            'annotation_hot': self.color_palette.get_color('error', 'light') or '#fef2f2',
            'annotation_cold': self.color_palette.get_color('info', 'light') or '#eff6ff'
        }
        
        # Weather színpaletta integrálása
        weather_temp_colors = self.weather_colors.get('temperature', '#C43939')  # Piros téma
        temp_colors['moderate'] = weather_temp_colors
        
        semantic_colors = {
            'success': self.color_palette.get_color('success', 'base') or '#10b981',
            'warning': self.color_palette.get_color('warning', 'base') or '#f59e0b',
            'error': self.color_palette.get_color('error', 'base') or '#dc2626',
            'info': self.color_palette.get_color('info', 'base') or '#6b7280'
        }
        
        print(f"🎨 DEBUG: Using SimplifiedThemeManager colors: {temp_colors}")
        
        # === SZÍNES HÁTTÉR ZÓNÁK ===
        
        # Hideg zóna (< 0°C)
        self.ax.axhspan(-50, 0, alpha=0.1, color=temp_colors['cold'], label='Fagyzóna')
        
        # Meleg zóna (> 25°C)
        self.ax.axhspan(25, 50, alpha=0.1, color=temp_colors['hot'], label='Forró zóna')
        
        # Komfort zóna (15-25°C)
        self.ax.axhspan(15, 25, alpha=0.05, color=temp_colors['comfort'], label='Komfort zóna')
        
        # === FAGYÁS ÉS FORRÓSÁG VONALAK ===
        
        self.ax.axhline(y=0, color=temp_colors['cold'], linestyle='--', alpha=0.7, linewidth=2, label='Fagypont')
        self.ax.axhline(y=25, color=temp_colors['warm'], linestyle='--', alpha=0.7, linewidth=2, label='Nyári meleg')
        self.ax.axhline(y=30, color=temp_colors['hot'], linestyle='--', alpha=0.7, linewidth=2, label='Hőhullám')
        
        # === HŐMÉRSÉKLET VONALAK - VASTAGABB, SIMPLIFIED THEMEMANAGER SZÍNEKKEL ===
        
        # Minimum hőmérséklet
        self.ax.plot(df['date'], df['temp_min'], 'o-', color=temp_colors['cold'], linewidth=3, 
                    markersize=6, alpha=0.9, label='Minimum', markerfacecolor='white', markeredgewidth=2)
        
        # Maximum hőmérséklet
        self.ax.plot(df['date'], df['temp_max'], 'o-', color=temp_colors['hot'], linewidth=3, 
                    markersize=6, alpha=0.9, label='Maximum', markerfacecolor='white', markeredgewidth=2)
        
        # Átlag hőmérséklet
        self.ax.plot(df['date'], df['temp_mean'], 's-', color=temp_colors['moderate'], linewidth=2.5, 
                    markersize=5, alpha=0.8, label='Átlag', markerfacecolor='white', markeredgewidth=1.5)
        
        # === TERÜLETEK KITÖLTÉSE - SZÍNÁTMENETES ===
        
        # Min-Max tartomány kitöltése gradiens hatással
        self.ax.fill_between(df['date'], df['temp_min'], df['temp_max'], 
                            alpha=0.2, color=temp_colors['warm'], label='Napi hőingás')
        
        # === TREND VONALAK - ÚJ FUNKCIÓ ===
        
        # Lineáris trend számítása
        if len(df) > 3:
            x_numeric = np.arange(len(df))
            
            # Maximum trend
            max_trend = np.polyfit(x_numeric, df['temp_max'], 1)
            max_trend_line = np.poly1d(max_trend)(x_numeric)
            self.ax.plot(df['date'], max_trend_line, '--', color=temp_colors['trend_up'], alpha=0.6, linewidth=2, label='Max trend')
            
            # Minimum trend
            min_trend = np.polyfit(x_numeric, df['temp_min'], 1)
            min_trend_line = np.poly1d(min_trend)(x_numeric)
            self.ax.plot(df['date'], min_trend_line, '--', color=temp_colors['trend_down'], alpha=0.6, linewidth=2, label='Min trend')
        
        # === STATISZTIKAI ANNOTÁCIÓK ===
        
        # Extrém értékek kiemelése
        max_temp_idx = df['temp_max'].idxmax()
        min_temp_idx = df['temp_min'].idxmin()
        
        max_temp_date = df.loc[max_temp_idx, 'date']
        max_temp_val = df.loc[max_temp_idx, 'temp_max']
        min_temp_date = df.loc[min_temp_idx, 'date']
        min_temp_val = df.loc[min_temp_idx, 'temp_min']
        
        # 🔧 SIMPLIFIED THEMEMANAGER ANNOTÁCIÓ SZÍNEK
        current_colors = get_current_colors()
        
        # Annotációk a szélsőértékekhez
        self.ax.annotate(f'🔥 {max_temp_val:.1f}°C', 
                        xy=(max_temp_date, max_temp_val), 
                        xytext=(10, 20), textcoords='offset points',
                        bbox=dict(boxstyle='round,pad=0.5', fc=temp_colors['annotation_hot'], ec=temp_colors['hot'], alpha=0.8),
                        arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.2', color=temp_colors['hot']))
        
        self.ax.annotate(f'🧊 {min_temp_val:.1f}°C', 
                        xy=(min_temp_date, min_temp_val), 
                        xytext=(10, -30), textcoords='offset points',
                        bbox=dict(boxstyle='round,pad=0.5', fc=temp_colors['annotation_cold'], ec=temp_colors['cold'], alpha=0.8),
                        arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=-0.2', color=temp_colors['cold']))
        
        # === FORMÁZÁS - PROFESSZIONÁLIS ===
        
        self._format_enhanced_temperature_chart(df)
    
    def _format_enhanced_temperature_chart(self, df: pd.DataFrame) -> None:
        """
        Fejlett hőmérséklet chart formázása - PROFESSZIONÁLIS STÍLUS + LEGEND POZÍCIÓ JAVÍTVA + SIMPLIFIED THEMEMANAGER.
        🎯 KRITIKUS JAVÍTÁS: Legend kívülre helyezése, hogy ne fedje el a diagramtartalmat
        🎨 SIMPLIFIED THEMEMANAGER INTEGRÁCIÓ: Színek és formázás a centralizált rendszerből
        """
        # 🔧 AKTUÁLIS TÉMA SZÍNEK
        current_colors = get_current_colors()
        
        # Cím és címkék
        self.ax.set_title(self.chart_title, fontweight='bold', pad=25, fontsize=18, 
                         color=current_colors.get('on_surface', '#1f2937'))
        self.ax.set_xlabel(self.x_label, fontsize=14, fontweight='500',
                          color=current_colors.get('on_surface', '#1f2937'))
        self.ax.set_ylabel(self.y_label, fontsize=14, fontweight='500',
                          color=current_colors.get('on_surface', '#1f2937'))
        
        # Dátum formázás - INTELLIGENS
        total_days = len(df)
        if total_days <= 31:  # Egy hónap vagy kevesebb
            self.ax.xaxis.set_major_locator(DayLocator(interval=max(1, total_days // 10)))
            self.ax.xaxis.set_major_formatter(DateFormatter('%m-%d'))
        else:  # Több hónap
            self.ax.xaxis.set_major_locator(MonthLocator())
            self.ax.xaxis.set_major_formatter(DateFormatter('%Y-%m'))
        
        # Y tengely formázás - INTELLIGENS TARTOMÁNY
        temp_min = df['temp_min'].min()
        temp_max = df['temp_max'].max()
        temp_range = temp_max - temp_min
        padding = max(2, temp_range * 0.1)  # 10% padding vagy minimum 2°C
        
        self.ax.set_ylim(temp_min - padding, temp_max + padding)
        self.ax.yaxis.set_major_locator(plt.MaxNLocator(10))
        
        # Grid és legend - PROFESSZIONÁLIS + KRITIKUS JAVÍTÁS + SIMPLIFIED THEMEMANAGER SZÍNEK
        if self.grid_enabled:
            grid_color = current_colors.get('border', '#d1d5db')
            grid_alpha = 0.3 if self.theme_manager.get_current_theme() == "light" else 0.2
            self.ax.grid(True, alpha=grid_alpha, linestyle='-', linewidth=0.8, color=grid_color)
            self.ax.set_axisbelow(True)  # Grid a háttérben
        
        if self.legend_enabled:
            # 🎯 KRITIKUS JAVÍTÁS: Legend kívülre helyezése chart területen kívülre
            # bbox_to_anchor=(1.05, 1) - jobb oldalra, felső szélhez igazítva
            # ncol=1 - egy oszlop a jobb áttekinthetőségért
            legend = self.ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', 
                          framealpha=0.95, fancybox=True, shadow=True, 
                          ncol=1, fontsize=11)
            
            # 🎨 LEGEND SZÍNEK SIMPLIFIED THEMEMANAGER-REL
            legend.get_frame().set_facecolor(current_colors.get('surface', '#ffffff'))
            legend.get_frame().set_edgecolor(current_colors.get('border', '#d1d5db'))
            
            print("🎯 DEBUG: Legend pozíció javítva - kívülre helyezve (1.05, 1) + SimplifiedThemeManager színek")
        
        # Layout optimalizálás - EXTRA HELY A LEGEND-NEK
        # bbox_inches='tight' automatikusan alkalmazkodik a kívülre helyezett legend-hez
        self.figure.tight_layout(rect=[0, 0, 0.85, 1])  # 85%-ig a figure, 15% a legend-nek
        
        print("✅ DEBUG: Enhanced temperature chart formázva - LEGEND NEM FEDI EL A TARTALMAT + SIMPLIFIED THEMEMANAGER")