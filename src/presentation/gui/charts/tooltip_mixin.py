#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 TOOLTIP MIXIN - SZUPER KONZERVATÍV INTEGRÁCIÓ + BUGFIX
🛡️ ZERO RISK - Újrafelhasználható tooltip funkcionalitás chart-okhoz

🚨 KRITIKUS JAVÍTÁS: KeyError 'primary_temp' fix
- Temperature chart: {'primary_temp': value} 
- Heatmap chart: {'value': value, 'parameter': 'temperature_2m_mean'}
- Wind/Precipitation: {'value': value, 'parameter': 'wind_speed_10m_max'}

🔧 EXPERIMENTAL PROTOTÍPUS ALAPJÁN:
- Pixel-based távolság számítás ✅
- Matplotlib dátum koordináták ✅
- 15px hover tolerance ✅
- Enhanced tooltip design ✅
- Event detection algoritmus ✅
- FLEXIBLE point_data handling ✅

🚨 KONZERVATÍV ELVEK:
- Opcionális mixin - nem kötelező használat
- Backward compatible - meglévő chart-ok változatlanok
- Izolált logika - nem érinti a base chart működést
- Easy rollback - egyszerű eltávolítás

Fájl helye: src/gui/charts/tooltip_mixin.py
"""

import datetime
from typing import Any, Dict, Optional

import matplotlib.dates as mdates
import numpy as np

from ..theme_manager import get_current_colors


class WeatherTooltipMixin:
    """
    🎯 TOOLTIP MIXIN - WORKING PROTOTÍPUS ALAPJÁN + BUGFIX
    
    🛡️ SZUPER KONZERVATÍV DESIGN:
    - Mixin pattern - opt-in használat
    - Self-contained logic - nem függőség
    - Clean interface - egyszerű aktiválás
    - Rollback ready - könnyen eltávolítható
    - Flexible point_data handling - chart-független
    
    HASZNÁLAT:
    ```python
    class MyChart(WeatherChart, WeatherTooltipMixin):
        def __init__(self):
            super().__init__()
            self.enable_tooltips()  # OPT-IN aktiválás
    ```
    """

    def __init__(self):
        """
        🔧 Mixin inicializálás - KONZERVATÍV
        
        FIGYELEM: Ez egy mixin, nem hívható direkt!
        """
        # Tooltip state változók
        self._tooltip_enabled = False
        self._tooltip_visible = False
        self._tooltip_annotation = None
        self._last_tooltip_point = None
        self._hover_tolerance = 15  # pixel távolság

        # Event connection tracking
        self._tooltip_event_connections = []

    def enable_tooltips(self, hover_tolerance: int = 15) -> None:
        """
        🎯 TOOLTIP AKTIVÁLÁS - OPT-IN RENDSZER
        
        Args:
            hover_tolerance: Hover érzékenység pixelekben (alapértelmezett: 15)
        """
        if self._tooltip_enabled:
            print("⚠️ DEBUG: Tooltips már aktiválva")
            return

        self._hover_tolerance = hover_tolerance
        self._tooltip_enabled = True

        # Event handlers kapcsolása
        self._connect_tooltip_events()

        print(f"✅ DEBUG: Tooltips aktiválva - {hover_tolerance}px tolerance")

    def disable_tooltips(self) -> None:
        """
        🛑 TOOLTIP KIKAPCSOLÁS - CLEAN SHUTDOWN
        """
        if not self._tooltip_enabled:
            return

        # Event handlers lekapcsolása
        self._disconnect_tooltip_events()

        # Tooltip elrejtése
        self._hide_tooltip()

        self._tooltip_enabled = False
        print("🛑 DEBUG: Tooltips kikapcsolva")

    def _connect_tooltip_events(self) -> None:
        """
        🔗 EVENT HANDLERS KAPCSOLÁSA - WORKING PROTOTÍPUS ALAPJÁN
        """
        if not hasattr(self, 'mpl_connect'):
            print("⚠️ DEBUG: mpl_connect nem elérhető - tooltip events skipped")
            return

        # Event connections tárolása a clean disconnect-hez
        connections = [
            self.mpl_connect('motion_notify_event', self._on_tooltip_mouse_move),
            self.mpl_connect('figure_leave_event', self._on_tooltip_figure_leave),
            self.mpl_connect('button_press_event', self._on_tooltip_mouse_click)
        ]

        self._tooltip_event_connections.extend(connections)
        print(f"🔗 DEBUG: {len(connections)} tooltip event handler kapcsolva")

    def _disconnect_tooltip_events(self) -> None:
        """
        🔌 EVENT HANDLERS LEKAPCSOLÁSA - CLEAN DISCONNECT
        """
        if not hasattr(self, 'mpl_disconnect'):
            return

        for connection in self._tooltip_event_connections:
            try:
                self.mpl_disconnect(connection)
            except Exception as e:
                print(f"⚠️ DEBUG: Event disconnect hiba: {e}")

        self._tooltip_event_connections.clear()
        print("🔌 DEBUG: Tooltip event handlers lekapcsolva")

    def _on_tooltip_figure_leave(self, event) -> None:
        """
        🖱️ Egér elhagyja a figure-t - tooltip elrejtése
        """
        if not self._tooltip_enabled:
            return

        self._hide_tooltip()

    def _on_tooltip_mouse_move(self, event) -> None:
        """
        🖱️ TOOLTIP HOVER LOGIC - WORKING PROTOTÍPUS ALAPJÁN
        
        🔧 KOORDINÁTA RENDSZER FIX:
        - Pixel-based távolság számítás
        - Matplotlib dátum koordináták
        - Event detection algoritmus
        """
        if not self._tooltip_enabled:
            return

        if not hasattr(self, 'ax') or event.inaxes != self.ax:
            self._hide_tooltip()
            return

        if event.xdata is None or event.ydata is None:
            self._hide_tooltip()
            return

        # Legközelebbi adatpont keresése
        closest_point = self._find_closest_chart_point(event)

        if closest_point:
            print(f"🎯 DEBUG: Tooltip FOUND point - index: {closest_point.get('index')}")

            # Új pont esetén tooltip update
            if (not self._last_tooltip_point or
                self._last_tooltip_point.get('index') != closest_point.get('index')):

                print("🎯 DEBUG: Tooltip megjelenítés indul...")
                self._show_tooltip(event, closest_point)
                print("🎯 DEBUG: Tooltip megjelenítés kész!")
                self._last_tooltip_point = closest_point
            else:
                print("🔄 DEBUG: Tooltip ugyanaz a pont - skip update")
        else:
            print("🚫 DEBUG: Tooltip nincs közeli pont")
            # Nincs közeli pont - tooltip elrejtése
            if self._tooltip_visible:
                print("🙈 DEBUG: Tooltip elrejtése...")
                self._hide_tooltip()
                self._last_tooltip_point = None

    def _on_tooltip_mouse_click(self, event) -> None:
        """
        👆 CLICK EVENT - részletes információ konzolra
        """
        if not self._tooltip_enabled:
            return

        if not hasattr(self, 'ax') or event.inaxes != self.ax:
            return

        closest_point = self._find_closest_chart_point(event)
        if closest_point:
            self._log_detailed_point_info(closest_point)

    def _find_closest_chart_point(self, event) -> Optional[Dict[str, Any]]:
        """
        🎯 LEGKÖZELEBBI PONT ALGORITMUS - WORKING PROTOTÍPUS ALAPJÁN
        
        🔧 PIXEL-BASED TÁVOLSÁG SZÁMÍTÁS:
        - Display koordináták az összes ponthoz
        - Mouse pozíció vs adatpont távolságok
        - Tolerance check pixel alapon
        
        Returns:
            Dict vagy None - legközelebbi pont adatai vagy semmi
        """
        if not hasattr(self, 'ax') or not hasattr(self, 'current_data'):
            return None

        # Chart-specifikus implementáció szükséges
        # Ez a metódus felüldefiniálandó a specifikus chart osztályokban
        return self._find_closest_temperature_point(event)

    def _find_closest_temperature_point(self, event) -> Optional[Dict[str, Any]]:
        """
        🌡️ TEMPERATURE CHART SPECIFIKUS PONT KERESÉS
        
        LOGIC:
        - DataFrame alapú adatkeresés
        - Dátum koordináták matplotlib formátumban
        - Pixel távolság számítás
        """
        try:
            if not hasattr(self, 'current_data') or self.current_data is None or self.current_data.empty:
                return None

            df = self.current_data

            # Matplotlib dátum koordináták
            if 'date' not in df.columns:
                return None

            plot_dates = mdates.date2num(df['date'])

            # Elérhető hőmérséklet oszlopok
            temp_columns = [col for col in ['temp_mean', 'temp_max', 'temp_min'] if col in df.columns]
            if not temp_columns:
                return None

            # Elsődleges hőmérséklet oszlop (mean > max > min)
            primary_temp_col = temp_columns[0]
            temperatures = df[primary_temp_col]

            # Mouse pozíció display koordinátákban
            mouse_x_display, mouse_y_display = self.ax.transData.transform((event.xdata, event.ydata))

            closest_idx = None
            min_distance = float('inf')

            # Minden adatponthoz távolság számítás
            for i, (x_val, y_val) in enumerate(zip(plot_dates, temperatures)):
                # Adatpont display koordinátái
                point_x_display, point_y_display = self.ax.transData.transform((x_val, y_val))

                # Pixel távolság
                distance = np.sqrt((mouse_x_display - point_x_display)**2 +
                                 (mouse_y_display - point_y_display)**2)

                if distance < min_distance:
                    min_distance = distance
                    closest_idx = i

            # Tolerance check
            if closest_idx is not None and min_distance <= self._hover_tolerance:

                # Pont adatok összeállítása
                point_data = {
                    'index': closest_idx,
                    'date': df.iloc[closest_idx]['date'],
                    'primary_temp': temperatures.iloc[closest_idx],
                    'primary_temp_column': primary_temp_col,
                    'pixel_distance': min_distance
                }

                # További hőmérséklet oszlopok hozzáadása
                for col in temp_columns:
                    if col != primary_temp_col:
                        point_data[col] = df.iloc[closest_idx][col]

                return point_data

        except Exception as e:
            print(f"⚠️ DEBUG: Point calculation error: {e}")

        return None

    def _show_tooltip(self, event, point_data: Dict[str, Any]) -> None:
        """
        💬 TOOLTIP MEGJELENÍTÉS - WORKING PROTOTÍPUS DESIGN + BUGFIX
        
        🚨 KRITIKUS JAVÍTÁS: Flexible Y koordináta pozicionálás
        - Temperature chart: 'primary_temp' kulcs
        - Heatmap chart: 'value' kulcs
        - Wind/Precipitation: 'value' kulcs
        
        🎨 ENHANCED TOOLTIP:
        - Professional design
        - Weather-specific formatting
        - Dynamic positioning
        """
        if not hasattr(self, 'ax'):
            return

        # Előző tooltip törlése
        self._hide_tooltip()

        # Tooltip szöveg formázása
        tooltip_text = self._format_tooltip_text(point_data)

        # 🚨 BUGFIX: FLEXIBLE Y KOORDINÁTA POZICIONÁLÁS
        # Koordináták meghatározása chart-típus független módon

        # X koordináta (dátum)
        if 'date' in point_data:
            x_pos = mdates.date2num(point_data['date'])
        else:
            print("⚠️ DEBUG: Nincs 'date' kulcs a point_data-ban")
            return

        # Y koordináta - FLEXIBLE KULCS KERESÉS
        y_pos = None

        # 1. Temperature chart: 'primary_temp'
        if 'primary_temp' in point_data:
            y_pos = point_data['primary_temp']
            print(f"🌡️ DEBUG: Temperature chart Y pozíció: {y_pos}")

        # 2. Heatmap/Wind/Precipitation: 'value'
        elif 'value' in point_data:
            y_pos = point_data['value']
            print(f"📊 DEBUG: Generic chart Y pozíció: {y_pos}")

        # 3. Fallback: első numerikus érték
        else:
            for key, value in point_data.items():
                if isinstance(value, (int, float)) and not key.endswith('_index'):
                    y_pos = value
                    print(f"🔍 DEBUG: Fallback Y pozíció ({key}): {y_pos}")
                    break

        # Y koordináta validálás
        if y_pos is None:
            print("❌ DEBUG: Nem találtunk érvényes Y koordinátát!")
            print(f"📋 DEBUG: point_data kulcsok: {list(point_data.keys())}")
            return

        print(f"🎯 DEBUG: Tooltip koordináták: x={x_pos}, y={y_pos}")

        # Current colors
        current_colors = get_current_colors()

        # ENHANCED TOOLTIP ANNOTATION
        try:
            self.tooltip_annotation = self.ax.annotate(
                tooltip_text,
                xy=(x_pos, y_pos),
                xytext=(40, 50),  # Offset pontokban
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
                ha='left',
                va='bottom',
                zorder=1000  # Top layer
            )

            self._tooltip_visible = True
            self._tooltip_annotation = self.tooltip_annotation

            print("✅ DEBUG: Tooltip annotation létrehozva!")
            print(f"📍 DEBUG: Tooltip visible: {self._tooltip_visible}")

            # FORCE CANVAS REFRESH - TÖBB MÓDSZER
            try:
                # 1. draw_idle()
                if hasattr(self, 'draw_idle'):
                    self.draw_idle()
                    print("🔄 DEBUG: draw_idle() hívva")

                # 2. draw() force
                if hasattr(self, 'draw'):
                    self.draw()
                    print("🔄 DEBUG: draw() force hívva")

                # 3. Figure refresh
                if hasattr(self.figure, 'canvas') and hasattr(self.figure.canvas, 'draw'):
                    self.figure.canvas.draw()
                    print("🔄 DEBUG: figure.canvas.draw() hívva")

                # 4. Qt widget update
                if hasattr(self, 'update'):
                    self.update()
                    print("🔄 DEBUG: widget.update() hívva")

            except Exception as refresh_error:
                print(f"⚠️ DEBUG: Canvas refresh hiba: {refresh_error}")

        except Exception as e:
            print(f"❌ DEBUG: Tooltip annotation létrehozási hiba: {e}")
            return

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

    def _format_tooltip_text(self, point_data: Dict[str, Any]) -> str:
        """
        📝 TOOLTIP SZÖVEG FORMÁZÁS - WEATHER SPECIFIC + FLEXIBLE
        
        🔧 CHART-FÜGGETLEN FORMÁZÁS:
        - Temperature chart specifikus
        - Heatmap chart specifikus (override)
        - Wind/Precipitation chart specifikus (override)
        """
        # Default: Temperature chart formázás
        if 'primary_temp' in point_data:
            return self._format_temperature_tooltip(point_data)
        else:
            # Általános formázás other chart-oknak
            return self._format_generic_tooltip(point_data)

    def _format_temperature_tooltip(self, point_data: Dict[str, Any]) -> str:
        """
        🌡️ TEMPERATURE CHART SPECIFIKUS TOOLTIP FORMÁZÁS
        """
        date = point_data['date']
        primary_temp = point_data['primary_temp']

        # Dátum formázás
        if isinstance(date, datetime.date):
            date_str = date.strftime('%Y-%m-%d (%A)')
        else:
            date_str = str(date)

        # Hőmérséklet kategória és ikon
        if primary_temp > 30:
            temp_icon = "🔥"
            category = "Forró nap"
        elif primary_temp < 0:
            temp_icon = "❄️"
            category = "Fagyos nap"
        elif primary_temp < 10:
            temp_icon = "🧊"
            category = "Hideg nap"
        elif primary_temp > 25:
            temp_icon = "☀️"
            category = "Meleg nap"
        else:
            temp_icon = "🌡️"
            category = "Mérsékelt nap"

        # Alap tooltip szöveg
        tooltip_lines = [
            f"📅 {date_str}",
            f"{temp_icon} {point_data['primary_temp_column'].replace('temp_', '').replace('_', ' ').title()}: {primary_temp:.1f}°C"
        ]

        # További hőmérséklet oszlopok hozzáadása
        for key, value in point_data.items():
            if key.startswith('temp_') and key != point_data['primary_temp_column']:
                column_name = key.replace('temp_', '').replace('_', ' ').title()
                tooltip_lines.append(f"🌡️ {column_name}: {value:.1f}°C")

        # Kategória hozzáadása
        tooltip_lines.extend([
            "",  # Üres sor
            f"🏷️ {category}"
        ])

        return '\n'.join(tooltip_lines)

    def _format_generic_tooltip(self, point_data: Dict[str, Any]) -> str:
        """
        📊 ÁLTALÁNOS TOOLTIP FORMÁZÁS - más chart típusokhoz
        """
        tooltip_lines = []

        # Dátum hozzáadása ha van
        if 'date' in point_data:
            date = point_data['date']
            if isinstance(date, datetime.date):
                date_str = date.strftime('%Y-%m-%d (%A)')
            else:
                date_str = str(date)
            tooltip_lines.append(f"📅 {date_str}")

        # Érték hozzáadása
        if 'value' in point_data:
            parameter = point_data.get('parameter', 'Ismeretlen')
            value = point_data['value']

            # Parameter alapú ikon és egység
            if 'temperature' in parameter:
                icon = "🌡️"
                unit = "°C"
            elif 'precipitation' in parameter:
                icon = "🌧️"
                unit = "mm"
            elif 'wind' in parameter:
                icon = "💨"
                unit = "km/h"
            else:
                icon = "📊"
                unit = ""

            tooltip_lines.append(f"{icon} Érték: {value:.1f} {unit}")
            tooltip_lines.append(f"📋 Parameter: {parameter}")

        # Ha nincsenek felismert kulcsok, minden kulcs-érték pair megjelenítése
        if not tooltip_lines:
            for key, value in point_data.items():
                if key not in ['index', 'pixel_distance']:
                    tooltip_lines.append(f"{key}: {value}")

        return '\n'.join(tooltip_lines) if tooltip_lines else "📊 Chart adat"

    def _log_detailed_point_info(self, point_data: Dict[str, Any]) -> None:
        """
        📋 RÉSZLETES PONT INFORMÁCIÓ KONZOLRA - DEBUG CÉLRA + FLEXIBLE
        """
        print("\n" + "="*60)
        print("🎯 TOOLTIP CLICK - RÉSZLETES ADATOK")
        print("="*60)

        for key, value in point_data.items():
            if key == 'date':
                print(f"📅 Dátum: {value}")
            elif key in ['primary_temp', 'value']:
                print(f"📊 Fő érték ({key}): {value:.1f}")
            elif key.startswith('temp_'):
                print(f"🌡️ {key}: {value:.1f}°C")
            elif key == 'parameter':
                print(f"📋 Parameter: {value}")
            elif key == 'pixel_distance':
                print(f"🎯 Pixel távolság: {value:.1f}px")
            elif key == 'index':
                print(f"📊 Index: {value}")
            else:
                print(f"🔧 {key}: {value}")

        print("="*60 + "\n")


# TOOLTIP AKTIVÁLÁSI HELPER FÜGGVÉNY
def add_tooltips_to_chart(chart_instance, hover_tolerance: int = 15) -> None:
    """
    🎯 TOOLTIP AKTIVÁLÁS HELPER - KONZERVATÍV INTEGRÁCIÓ
    
    Args:
        chart_instance: WeatherChart instance (+ WeatherTooltipMixin)
        hover_tolerance: Hover érzékenység pixelekben
    
    Usage:
        ```python
        # Bármely chart-nál használható
        add_tooltips_to_chart(my_temperature_chart, hover_tolerance=20)
        ```
    """
    if hasattr(chart_instance, 'enable_tooltips'):
        chart_instance.enable_tooltips(hover_tolerance)
        print(f"✅ DEBUG: Tooltips aktiválva - {chart_instance.__class__.__name__}")
    else:
        print(f"⚠️ DEBUG: {chart_instance.__class__.__name__} nem támogatja a tooltip-okat")


# Module export
__all__ = ['WeatherTooltipMixin', 'add_tooltips_to_chart']
