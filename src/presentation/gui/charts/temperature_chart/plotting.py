#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Temperature Chart - Plotting

🎨 Hőmérséklet grafikon rajzolása

Képességek:
- Színes zónák rajzolása
- Hőmérséklet vonalak rajzolása
- Trend vonalak
- Extrém értékek annotálása

Fájl: src/presentation/gui/charts/temperature_chart/plotting.py
"""

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    import pandas as pd


class TemperaturePlottingMixin:
    """
    🎨 Hőmérséklet grafikon rajzolása keverék osztály.
    """

    def _plot_enhanced_temperature(self, df: "pd.DataFrame") -> None:
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
