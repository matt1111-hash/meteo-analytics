#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global Weather Analyzer - Enhanced Temperature Chart
Fejlett hőmérséklet grafikon widget professzionális vizualizációval.

🌡️ ENHANCED TEMPERATURE CHART: Színes zónák, trend vonalak, statisztikai elemek
🎨 TÉMA INTEGRÁCIÓ: ColorPalette használata professzionális színekhez
🔧 KRITIKUS JAVÍTÁS: Robusztus update cycle duplikáció nélkül + LEGEND POZÍCIÓ JAVÍTVA
🎯 TOOLTIP INTEGRÁCIÓ: WeatherTooltipMixin - SZUPER KONZERVATÍV MEGKÖZELÍTÉS!
✅ Piros (#C43939) téma támogatás
✅ Professzionális nagy méretű diagramok
✅ Optimális legend elhelyezés
✅ Valódi API adatok használata (mock adatok tiltva)
✅ INTERAKTÍV TOOLTIP FUNKCIÓK: Hover + Click eventi
✅ SMART TOOLTIP POSITIONING: Dynamic placement, nem lóg ki
"""

from typing import Optional, Dict, Any
import pandas as pd
import numpy as np
from datetime import datetime

from matplotlib.dates import DateFormatter, MonthLocator, DayLocator
import matplotlib.pyplot as plt

from PySide6.QtWidgets import QWidget

from .base_chart import WeatherChart
from .tooltip_mixin import WeatherTooltipMixin  # 🎯 TOOLTIP MIXIN IMPORT
from ..theme_manager import get_current_colors


class EnhancedTemperatureChart(WeatherChart, WeatherTooltipMixin):  # 🎯 MIXIN HOZZÁADÁSA
    """
    Fejlett hőmérséklet grafikon widget - PROFESSZIONÁLIS NAGY VERZIÓ + DUPLIKÁCIÓ BUGFIX + SIMPLIFIED THEMEMANAGER.
    Színes zónák, trend vonalak, statisztikai elemek.
    🎨 TÉMA INTEGRÁCIÓ: ColorPalette használata professzionális színválasztáshoz
    🔧 KRITIKUS JAVÍTÁS: Robusztus update cycle duplikáció nélkül + LEGEND POZÍCIÓ JAVÍTVA
    🎯 TOOLTIP ENHANCEMENT: WeatherTooltipMixin integráció - INTERAKTÍV HOVER/CLICK FUNKCIÓK
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(figsize=(14, 8), parent=parent)  # NAGY MÉRET
        self.chart_title = "🌡️ Részletes Hőmérséklet Elemzés"
        self.y_label = "Hőmérséklet (°C)"
        
        # 🎯 TOOLTIP AKTIVÁLÁS - OPT-IN RENDSZER
        self.enable_tooltips(hover_tolerance=15)
        print("🎯 DEBUG: EnhancedTemperatureChart tooltip-ok aktiválva!")
    
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
            
            print("✅ DEBUG: EnhancedTemperatureChart frissítés kész - DUPLIKÁCIÓ MENTES + THEMED + TOOLTIP READY")
            
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
        
        print("✅ DEBUG: Enhanced temperature chart formázva - LEGEND NEM FEDI EL A TARTALMAT + SIMPLIFIED THEMEMANAGER + TOOLTIP READY")
    
    def _find_closest_chart_point(self, event) -> Optional[Dict[str, Any]]:
        """
        🎯 MULTI-LINE TOOLTIP DETECTION - MINDEN VONALRA REAGÁL!
        
        🔧 ENHANCED LOGIC:
        - temp_mean, temp_max, temp_min ÖSSZES vonal ellenőrzése
        - Legközelebbi pont bármelyik vonalról
        - Professional tooltip adatok minden hőmérséklet típussal
        """
        try:
            if not hasattr(self, 'current_data') or self.current_data is None or self.current_data.empty:
                return None
            
            df = self.current_data
            
            # Matplotlib dátum koordináták
            if 'date' not in df.columns:
                return None
                
            import matplotlib.dates as mdates
            plot_dates = mdates.date2num(df['date'])
            
            # Elérhető hőmérséklet oszlopok - MINDEN VONAL
            temp_columns = []
            if 'temp_mean' in df.columns:
                temp_columns.append('temp_mean')
            if 'temp_max' in df.columns:
                temp_columns.append('temp_max')
            if 'temp_min' in df.columns:
                temp_columns.append('temp_min')
                
            if not temp_columns:
                return None
            
            # Mouse pozíció display koordinátákban
            mouse_x_display, mouse_y_display = self.ax.transData.transform((event.xdata, event.ydata))
            
            closest_idx = None
            min_distance = float('inf')
            closest_temp_col = None
            closest_temp_value = None
            
            # ⭐ ÚJ LOGIKA: MINDEN HŐMÉRSÉKLET VONALAT ELLENŐRIZ
            for temp_col in temp_columns:
                temperatures = df[temp_col]
                
                # Minden adatponthoz távolság számítás ezen a vonalon
                for i, (x_val, y_val) in enumerate(zip(plot_dates, temperatures)):
                    if pd.isna(y_val):  # Skip NaN values
                        continue
                        
                    # Adatpont display koordinátái
                    point_x_display, point_y_display = self.ax.transData.transform((x_val, y_val))
                    
                    # Pixel távolság
                    distance = np.sqrt((mouse_x_display - point_x_display)**2 + 
                                     (mouse_y_display - point_y_display)**2)
                    
                    if distance < min_distance:
                        min_distance = distance
                        closest_idx = i
                        closest_temp_col = temp_col
                        closest_temp_value = y_val
            
            # Tolerance check
            if closest_idx is not None and min_distance <= self._hover_tolerance:
                
                # Pont adatok összeállítása - TELJES NAPI ADAT
                point_data = {
                    'index': closest_idx,
                    'date': df.iloc[closest_idx]['date'],
                    'primary_temp': closest_temp_value,
                    'primary_temp_column': closest_temp_col,
                    'pixel_distance': min_distance,
                    'closest_line': closest_temp_col  # Melyik vonalra kattintott
                }
                
                # ÖSSZES hőmérséklet oszlop hozzáadása
                for col in temp_columns:
                    if col in df.columns:
                        point_data[col] = df.iloc[closest_idx][col]
                
                return point_data
        
        except Exception as e:
            print(f"⚠️ DEBUG: Temperature point calculation error: {e}")
        
        return None
    
    def _format_tooltip_text(self, point_data: Dict[str, Any]) -> str:
        """
        📝 ENHANCED MULTI-LINE TOOLTIP FORMÁZÁS
        
        🌡️ INTELLIGENT TOOLTIP:
        - Kiemeli a legközelebbi vonalat (closest_line)
        - Összes hőmérséklet adat megjelenítése 
        - Magyar weather ikonok és kategóriák
        - Professional formatting
        """
        date = point_data['date']
        primary_temp = point_data['primary_temp']
        closest_line = point_data.get('closest_line', 'temp_mean')
        
        # Dátum formázás
        if isinstance(date, datetime):
            date_str = date.strftime('%Y-%m-%d (%A)')
        else:
            date_str = str(date)
        
        # Hőmérséklet kategória és ikon - ENHANCED
        if primary_temp > 35:
            temp_icon = "🔥"
            category = "Extrém forró"
        elif primary_temp > 30:
            temp_icon = "☀️"
            category = "Forró nap"
        elif primary_temp > 25:
            temp_icon = "🌞"
            category = "Meleg nap"
        elif primary_temp > 15:
            temp_icon = "🌡️"
            category = "Mérsékelt nap"
        elif primary_temp > 0:
            temp_icon = "🧊"
            category = "Hideg nap"
        elif primary_temp > -10:
            temp_icon = "❄️"
            category = "Fagyos nap"
        else:
            temp_icon = "🥶"
            category = "Extrém hideg"
        
        # Tooltip szöveg összeállítása
        tooltip_lines = [
            f"📅 {date_str}",
            "",  # Üres sor a strukturáláshoz
        ]
        
        # ⭐ KIEMELT VONAL - AMELYIKRE HOVER-ELÜNK
        line_names = {
            'temp_max': 'Maximum',
            'temp_min': 'Minimum', 
            'temp_mean': 'Átlag'
        }
        
        line_icons = {
            'temp_max': '🔺',
            'temp_min': '🔻',
            'temp_mean': '🎯'
        }
        
        # Legközelebbi vonal kiemelése
        if closest_line in point_data:
            line_name = line_names.get(closest_line, closest_line)
            line_icon = line_icons.get(closest_line, '🌡️')
            tooltip_lines.append(f"➤ {line_icon} {line_name}: {point_data[closest_line]:.1f}°C ← HOVER")
        
        # További hőmérséklet adatok - NEM KIEMELT
        for col in ['temp_max', 'temp_min', 'temp_mean']:
            if col in point_data and col != closest_line:
                line_name = line_names.get(col, col)
                line_icon = line_icons.get(col, '🌡️')
                tooltip_lines.append(f"  {line_icon} {line_name}: {point_data[col]:.1f}°C")
        
        # Napi hőingás számítása
        if 'temp_max' in point_data and 'temp_min' in point_data:
            temp_range = point_data['temp_max'] - point_data['temp_min']
            tooltip_lines.append(f"📊 Napi hőingás: {temp_range:.1f}°C")
        
        # Kategória
        tooltip_lines.extend([
            "",  # Üres sor
            f"🏷️ {category}"
        ])
        
        return '\n'.join(tooltip_lines)
    
    def _show_tooltip(self, event, point_data: Dict[str, Any]) -> None:
        """
        💬 SMART TOOLTIP POSITIONING - DYNAMIC PLACEMENT
        
        🎨 INTELLIGENT TOOLTIP:
        - Professional design
        - Weather-specific formatting
        - 🎯 SMART POSITIONING: Automatically avoids chart edges
        """
        if not hasattr(self, 'ax'):
            return
            
        # Előző tooltip törlése
        self._hide_tooltip()
        
        # Tooltip szöveg formázása
        tooltip_text = self._format_tooltip_text(point_data)
        
        # Koordináták meghatározása
        import matplotlib.dates as mdates
        x_pos = mdates.date2num(point_data['date'])
        y_pos = point_data['primary_temp']
        
        # 🎯 SMART POSITIONING LOGIC
        # Chart területének boundaries
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        
        # Pont pozíciója a chart területen (0-1 scale)
        x_relative = (x_pos - xlim[0]) / (xlim[1] - xlim[0])
        y_relative = (y_pos - ylim[0]) / (ylim[1] - ylim[0])
        
        # Dynamic offset számítás
        if y_relative > 0.7:  # Felső 30%-ban
            # Tooltip lefelé
            offset_y = -80
            va_align = 'top'
            print(f"🔽 DEBUG: Tooltip lefelé - y_relative: {y_relative:.2f}")
        else:
            # Tooltip felfelé (alapértelmezett)
            offset_y = 50
            va_align = 'bottom'
            print(f"🔼 DEBUG: Tooltip felfelé - y_relative: {y_relative:.2f}")
        
        if x_relative > 0.8:  # Jobb 20%-ban
            # Tooltip balra
            offset_x = -100
            ha_align = 'right'
            print(f"⬅️ DEBUG: Tooltip balra - x_relative: {x_relative:.2f}")
        else:
            # Tooltip jobbra (alapértelmezett)
            offset_x = 40
            ha_align = 'left'
            print(f"➡️ DEBUG: Tooltip jobbra - x_relative: {x_relative:.2f}")
        
        # Current colors
        current_colors = get_current_colors()
        
        # ENHANCED TOOLTIP ANNOTATION - SMART POSITIONED
        self.tooltip_annotation = self.ax.annotate(
            tooltip_text,
            xy=(x_pos, y_pos),
            xytext=(offset_x, offset_y),  # 🎯 DYNAMIC OFFSET
            textcoords='offset points',
            bbox=dict(
                boxstyle='round,pad=1.0',
                facecolor='lightyellow',
                edgecolor=current_colors.get('border', '#34495E'),
                linewidth=2,
                alpha=0.95
            ),
            arrowprops=dict(
                arrowstyle='->',
                color=current_colors.get('border', '#34495E'),
                lw=2,
                alpha=0.8
            ),
            fontsize=10,
            fontweight='bold',
            ha=ha_align,      # 🎯 DYNAMIC HORIZONTAL ALIGNMENT
            va=va_align,      # 🎯 DYNAMIC VERTICAL ALIGNMENT  
            zorder=1000       # Top layer
        )
        
        self._tooltip_visible = True
        self._tooltip_annotation = self.tooltip_annotation
        
        # Canvas frissítése
        if hasattr(self, 'draw_idle'):
            self.draw_idle()
    
    def _hide_tooltip(self) -> None:
        """
        🙈 Tooltip elrejtése - CLEAN HIDING
        """
        if self._tooltip_annotation:
            try:
                self._tooltip_annotation.remove()
            except Exception as e:
                print(f"⚠️ DEBUG: Tooltip remove error: {e}")
            
            self._tooltip_annotation = None
            self._tooltip_visible = False
            
            # Canvas frissítése
            if hasattr(self, 'draw_idle'):
                self.draw_idle()