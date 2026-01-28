#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global Weather Analyzer - Precipitation Chart
Csapadék grafikon widget professzionális oszlopdiagram vizualizációval.

🌧️ PRECIPITATION CHART: Oszlopdiagram csapadék mennyiségekkel
🎨 TÉMA INTEGRÁCIÓ: ColorPalette precipitation színek használata
🔧 KRITIKUS JAVÍTÁS: Duplikáció-mentes frissítés + SIMPLIFIED THEMEMANAGER
🎯 TOOLTIP INTEGRÁCIÓ: WeatherTooltipMixin - BAR CHART SPECIFIKUS LOGIKA!
✅ Piros (#C43939) téma támogatás
✅ Színkódolt oszlopok csapadék mennyiség alapján
✅ Statisztikai információk megjelenítése
✅ Valódi API adatok használata
✅ INTERAKTÍV TOOLTIP FUNKCIÓK: Hover oszlopokra + Click eventi
"""

from datetime import datetime
from typing import Any, Dict, Optional

import pandas as pd
from matplotlib.dates import DateFormatter, MonthLocator
from PySide6.QtWidgets import QWidget

from ..theme_manager import get_current_colors
from .base_chart import WeatherChart
from .tooltip_mixin import WeatherTooltipMixin  # 🎯 TOOLTIP MIXIN IMPORT


class PrecipitationChart(WeatherChart, WeatherTooltipMixin):  # 🎯 MIXIN HOZZÁADÁSA
    """
    Csapadék grafikon widget - EREDETI MEGTARTVA + DUPLIKÁCIÓ BUGFIX + SIMPLIFIED THEMEMANAGER + TOOLTIP INTEGRÁCIÓ.
    🎨 TÉMA INTEGRÁCIÓ: ColorPalette precipitation színek használata
    🎯 TOOLTIP ENHANCEMENT: WeatherTooltipMixin integráció - BAR CHART HOVER FUNKCIÓK
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(figsize=(12, 6), parent=parent)
        self.chart_title = "🌧️ Napi csapadék mennyisége"
        self.y_label = "Csapadék (mm)"

        # 🎯 TOOLTIP AKTIVÁLÁS - OPT-IN RENDSZER
        self.enable_tooltips(hover_tolerance=20)  # Bar chart-hoz nagyobb tolerance
        print("🎯 DEBUG: PrecipitationChart tooltip-ok aktiválva!")

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

            print("✅ DEBUG: PrecipitationChart frissítés kész - DUPLIKÁCIÓ MENTES + THEMED + TOOLTIP READY")

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
        self.bars = self.ax.bar(df['date'], df['precipitation'],
                               color=precip_colors['moderate'], alpha=0.7,
                               edgecolor=current_colors.get('border', '#d1d5db'), linewidth=0.5)

        # 🎯 TOOLTIP TRACKING: Bar objektumok tárolása
        self.bar_data = []  # Bar-hoz tartozó adatok tooltip-hoz

        # Színkódolás csapadék mennyiség alapján + SIMPLIFIED THEMEMANAGER
        for i, (date, precip) in enumerate(zip(df['date'], df['precipitation'])):
            # Bar-hoz tartozó adat tárolása
            self.bar_data.append({
                'index': i,
                'date': date,
                'precipitation': precip,
                'bar': self.bars[i]
            })

            if precip > 20:  # Erős csapadék
                self.bars[i].set_color(precip_colors['heavy'])
            elif precip > 10:  # Közepes csapadék
                self.bars[i].set_color(precip_colors['moderate'])
            elif precip > 1:  # Gyenge csapadék
                self.bars[i].set_color(precip_colors['light'])
            else:  # Száraz
                self.bars[i].set_color(precip_colors['none'])

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

        print("✅ DEBUG: Precipitation chart formázva + TOOLTIP READY")

    def _find_closest_chart_point(self, event) -> Optional[Dict[str, Any]]:
        """
        🎯 BAR CHART SPECIFIKUS PONT KERESÉS - TOOLTIP MIXIN OVERRIDE
        
        🔧 PRECIPITATION BAR CHART KOMPATIBILITÁS:
        - Bar objektumok hit detection
        - X koordináta alapú oszlop keresés
        - Professional precipitation tooltip adatok
        """
        try:
            if not hasattr(self, 'current_data') or self.current_data is None or self.current_data.empty:
                return None

            if not hasattr(self, 'bar_data') or not self.bar_data:
                return None

            if event.xdata is None or event.ydata is None:
                return None

            df = self.current_data

            # 🎯 BAR CHART LOGIKA: X koordináta alapú oszlop keresés
            import matplotlib.dates as mdates
            mouse_x = event.xdata

            closest_idx = None
            min_distance = float('inf')

            # Minden bar-hoz távolság számítás X koordináta alapján
            for i, bar_info in enumerate(self.bar_data):
                bar_date = bar_info['date']
                bar_x = mdates.date2num(bar_date)

                # X távolság (időben)
                x_distance = abs(mouse_x - bar_x)

                if x_distance < min_distance:
                    min_distance = x_distance
                    closest_idx = i

            # 🎯 BAR CHART TOLERANCE: Nagyobb tolerance bar chart-hoz
            # Egy nap = 1.0 matplotlib units
            day_tolerance = 0.5  # Fél nap tolerance

            if closest_idx is not None and min_distance <= day_tolerance:

                bar_info = self.bar_data[closest_idx]

                # Pont adatok összeállítása - PRECIPITATION SPECIFIKUS
                point_data = {
                    'index': closest_idx,
                    'date': bar_info['date'],
                    'precipitation': bar_info['precipitation'],
                    'primary_temp': bar_info['precipitation'],  # Mixin kompatibilitás
                    'primary_temp_column': 'precipitation',     # Mixin kompatibilitás
                    'pixel_distance': min_distance,
                    'chart_type': 'precipitation_bar'
                }

                return point_data

        except Exception as e:
            print(f"⚠️ DEBUG: Precipitation point calculation error: {e}")

        return None

    def _format_tooltip_text(self, point_data: Dict[str, Any]) -> str:
        """
        📝 PRECIPITATION CHART TOOLTIP FORMÁZÁS
        
        🌧️ PROFESSIONAL PRECIPITATION TOOLTIP:
        - Csapadék mennyiség és kategória
        - Meteorológiai jellemzők
        - Magyar weather ikonok
        - Intenzitás kategóriák
        """
        date = point_data['date']
        precipitation = point_data['precipitation']

        # Dátum formázás
        if isinstance(date, datetime):
            date_str = date.strftime('%Y-%m-%d (%A)')
        else:
            date_str = str(date)

        # 🌧️ CSAPADÉK KATEGÓRIÁK ÉS IKONOK - METEOROLÓGIAI
        if precipitation > 50:
            precip_icon = "⛈️"
            category = "Viharos zápor"
            intensity = "Rendkívül erős"
        elif precipitation > 20:
            precip_icon = "🌧️"
            category = "Erős esőzés"
            intensity = "Erős"
        elif precipitation > 10:
            precip_icon = "🌦️"
            category = "Közepes esőzés"
            intensity = "Mérsékelt"
        elif precipitation > 5:
            precip_icon = "🌤️"
            category = "Gyenge esőzés"
            intensity = "Gyenge"
        elif precipitation > 1:
            precip_icon = "💧"
            category = "Szitálás"
            intensity = "Nagyon gyenge"
        elif precipitation > 0.1:
            precip_icon = "💦"
            category = "Harmat/köd"
            intensity = "Minimális"
        else:
            precip_icon = "☀️"
            category = "Száraz nap"
            intensity = "Nincs csapadék"

        # 🌧️ METEOROLÓGIAI JELLEMZŐK
        meteorological_info = []

        if precipitation > 25:
            meteorological_info.append("⚠️ Árvízveszély lehetséges")
        elif precipitation > 15:
            meteorological_info.append("🚗 Közlekedési nehézségek")
        elif precipitation > 10:
            meteorological_info.append("☂️ Esernyő szükséges")
        elif precipitation > 1:
            meteorological_info.append("🌱 Jó a növényeknek")

        # 📊 HAVI/ÉVES KONTEXTUS (ha elérhető)
        contextual_info = []
        if hasattr(self, 'current_data') and not self.current_data.empty:
            df = self.current_data
            total_precip = df['precipitation'].sum()
            avg_precip = df['precipitation'].mean()

            # Napi érték vs átlag összehasonlítás
            if precipitation > avg_precip * 2:
                contextual_info.append(f"📈 Átlag feletti ({avg_precip:.1f} mm)")
            elif precipitation < avg_precip * 0.5:
                contextual_info.append(f"📉 Átlag alatti ({avg_precip:.1f} mm)")
            else:
                contextual_info.append(f"📊 Átlagos tartomány ({avg_precip:.1f} mm)")

        # Tooltip szöveg összeállítása
        tooltip_lines = [
            f"📅 {date_str}",
            "",  # Üres sor a strukturáláshoz
            f"{precip_icon} Csapadék: {precipitation:.1f} mm",
            f"🏷️ {category}",
            f"📊 Intenzitás: {intensity}",
        ]

        # Meteorológiai információk hozzáadása
        if meteorological_info:
            tooltip_lines.append("")
            tooltip_lines.extend(meteorological_info)

        # Kontextuális információk hozzáadása
        if contextual_info:
            tooltip_lines.append("")
            tooltip_lines.extend(contextual_info)

        return '\n'.join(tooltip_lines)

    def _show_tooltip(self, event, point_data: Dict[str, Any]) -> None:
        """
        💬 PRECIPITATION BAR CHART TOOLTIP POSITIONING
        
        🎨 BAR CHART SPECIFIC TOOLTIP:
        - Professional design
        - Precipitation-specific formatting
        - 🎯 BAR CHART POSITIONING: Above bars, smart edge detection
        """
        if not hasattr(self, 'ax'):
            return

        # Előző tooltip törlése
        self._hide_tooltip()

        # Tooltip szöveg formázása
        tooltip_text = self._format_tooltip_text(point_data)

        # Koordináták meghatározása - BAR CHART SPECIFIC
        import matplotlib.dates as mdates
        x_pos = mdates.date2num(point_data['date'])
        y_pos = point_data['precipitation']

        # 🎯 BAR CHART SMART POSITIONING
        # Chart területének boundaries
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()

        # Pont pozíciója a chart területen (0-1 scale)
        x_relative = (x_pos - xlim[0]) / (xlim[1] - xlim[0])
        y_relative = (y_pos - ylim[0]) / (ylim[1] - ylim[0])

        # 🌧️ BAR CHART POSITIONING LOGIC
        # Bar chart-nál alapértelmezett: felfelé (oszlop teteje felett)
        if y_relative > 0.7:  # Magas oszlop
            # Tooltip lefelé vagy oldalra
            if x_relative > 0.8:  # Jobb szélen
                offset_x = -120
                offset_y = -30
                ha_align = 'right'
                va_align = 'top'
                print("🔽⬅️ DEBUG: Tooltip balra-lefelé - magas oszlop jobb szélen")
            else:
                offset_x = 40
                offset_y = -50
                ha_align = 'left'
                va_align = 'top'
                print("🔽 DEBUG: Tooltip lefelé - magas oszlop")
        else:
            # Tooltip felfelé (oszlop felett)
            if x_relative > 0.8:  # Jobb szélen
                offset_x = -120
                offset_y = 30
                ha_align = 'right'
                va_align = 'bottom'
                print("🔼⬅️ DEBUG: Tooltip balra-felfelé - jobb szélen")
            else:
                offset_x = 40
                offset_y = 30
                ha_align = 'left'
                va_align = 'bottom'
                print("🔼 DEBUG: Tooltip felfelé - oszlop felett")

        # Current colors
        current_colors = get_current_colors()

        # 🌧️ PRECIPITATION THEMED TOOLTIP
        self.tooltip_annotation = self.ax.annotate(
            tooltip_text,
            xy=(x_pos, y_pos),
            xytext=(offset_x, offset_y),  # 🎯 DYNAMIC OFFSET
            textcoords='offset points',
            bbox=dict(
                boxstyle='round,pad=1.0',
                facecolor='lightcyan',  # 🌧️ Precipitation theme
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
        if hasattr(self, '_tooltip_annotation') and self._tooltip_annotation:
            try:
                self._tooltip_annotation.remove()
            except Exception as e:
                print(f"⚠️ DEBUG: Precipitation tooltip remove error: {e}")

            self._tooltip_annotation = None
            self._tooltip_visible = False

            # Canvas frissítése
            if hasattr(self, 'draw_idle'):
                self.draw_idle()
