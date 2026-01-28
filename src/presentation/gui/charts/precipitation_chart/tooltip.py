#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Precipitation Chart - Tooltip

💬 Tooltip funkciók

Képességek:
- Legközelebbi pont keresése
- Tooltip szöveg formázás
- Tooltip megjelenítés/elrejtés

Fájl: src/presentation/gui/charts/precipitation_chart/tooltip.py
"""

from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    pass

from ..theme_manager import get_current_colors


def _find_closest_chart_point(self, event) -> Optional[Dict[str, Any]]:
    """
    🎯 BAR CHART SPECIFIKUS PONT KERESÉS - TOOLTIP MIXIN OVERRIDE

    🔧 PRECIPITATION BAR CHART KOMPATIBILITÁS:
    - Bar objektumok hit detection
    - X koordináta alapú oszlop keresés
    - Professional precipitation tooltip adatok

    Args:
        self: PrecipitationChart instance
        event: Matplotlib mouse event

    Returns:
        Dict with point data or None
    """
    try:
        if not hasattr(self, 'current_data') or self.current_data is None or self.current_data.empty:
            return None

        if not hasattr(self, 'bar_data') or not self.bar_data:
            return None

        if event.xdata is None or event.ydata is None:
            return None

        # 🎯 BAR CHART LOGIKA: X koordináta alapú oszlop keresés
        import matplotlib.dates as mdates
        mouse_x = event.xdata

        closest_idx = None
        min_distance = float('inf')

        # Minden bar-höz távolság számítás X koordináta alapján
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

    Args:
        self: PrecipitationChart instance
        point_data: Point data dict

    Returns:
        Formatted tooltip text
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

    Args:
        self: PrecipitationChart instance
        event: Matplotlib mouse event
        point_data: Point data dict
    """
    if not hasattr(self, 'ax'):
        return

    # Előző tooltip törlése
    _hide_tooltip(self)

    # Tooltip szöveg formázása
    tooltip_text = _format_tooltip_text(self, point_data)

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

    Args:
        self: PrecipitationChart instance
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
