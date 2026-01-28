#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Temperature Chart - Tooltip Handler

🎯 Tooltip kezelése hőmérséklet chartokhoz

Képességek:
- Multi-line tooltip detection
- Smart tooltip positioning
- Enhanced tooltip text formatting
- Dynamic placement to avoid edges

Fájl: src/presentation/gui/charts/temperature_chart/tooltip_handler.py
"""

from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Optional

import numpy as np
import pandas as pd

from ...theme_manager import get_current_colors

if TYPE_CHECKING:
    pass


class TemperatureTooltipHandlerMixin:
    """
    🎯 Tooltip kezelése keverék osztály.
    """

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

        # Hőmérséklet kategória - ENHANCED
        if primary_temp > 35:
            category = "Extrém forró"
        elif primary_temp > 30:
            category = "Forró nap"
        elif primary_temp > 25:
            category = "Meleg nap"
        elif primary_temp > 15:
            category = "Mérsékelt nap"
        elif primary_temp > 0:
            category = "Hideg nap"
        elif primary_temp > -10:
            category = "Fagyos nap"
        else:
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
