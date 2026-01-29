#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Quick Overview Tab - Temp Precip Stats

Hőmérséklet és csapadék statisztikák számítása.

Fájl: src/presentation/gui/results_panel/quick_overview_tab/temp_precip_stats.py
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from src.presentation.gui.results_panel.quick_overview_tab.core import QuickOverviewTab

logger = logging.getLogger(__name__)


def calculate_temperature_stats(self, df: pd.DataFrame) -> None:
    """Hőmérséklet statisztikák számítása."""
    try:
        _set_stat_if_exists(self, df, 'temp_max', 'max_temp', lambda s: f"{s.max():.1f}")
        _set_stat_if_exists(self, df, 'temp_min', 'min_temp', lambda s: f"{s.min():.1f}")

        # Átlagos hőmérséklet
        avg_temp = None
        if 'temp_mean' in df.columns:
            mean_series = df['temp_mean'].dropna()
            if not mean_series.empty:
                avg_temp = mean_series.mean()

        if avg_temp is None or not pd.notna(avg_temp):
            if 'temp_max' in df.columns and 'temp_min' in df.columns:
                max_series = df['temp_max'].dropna()
                min_series = df['temp_min'].dropna()
                if not max_series.empty and not min_series.empty:
                    avg_temp = (max_series.mean() + min_series.mean()) / 2

        if avg_temp is not None and pd.notna(avg_temp):
            self._stat_labels['avg_temp'].setText(f"{avg_temp:.1f}")
        else:
            self._stat_labels['avg_temp'].setText("N/A")

        # Hőingás
        if 'temp_max' in df.columns and 'temp_min' in df.columns:
            max_series = df['temp_max'].dropna()
            min_series = df['temp_min'].dropna()
            if not max_series.empty and not min_series.empty:
                max_val = max_series.max()
                min_val = min_series.min()
                if pd.notna(max_val) and pd.notna(min_val):
                    temp_range = max_val - min_val
                    self._stat_labels['temp_range'].setText(f"{temp_range:.1f}")
                else:
                    self._stat_labels['temp_range'].setText("N/A")
            else:
                self._stat_labels['temp_range'].setText("N/A")
        else:
            self._stat_labels['temp_range'].setText("N/A")

    except Exception as e:
        logger.error(f"Hőmérséklet statisztika hiba: {e}")
        _clear_stats_range(self, ['avg_temp', 'max_temp', 'min_temp', 'temp_range'])


def calculate_precipitation_stats(self, df: pd.DataFrame) -> None:
    """Csapadék statisztikák számítása."""
    try:
        if 'precipitation' not in df.columns:
            _clear_stats_range(self, ['total_precip', 'avg_precip', 'max_precip', 'rainy_days'])
            return

        precip_series = df['precipitation'].dropna()

        if precip_series.empty:
            _clear_stats_range(self, ['total_precip', 'avg_precip', 'max_precip'])
            self._stat_labels['rainy_days'].setText("0")
            return

        total = precip_series.sum()
        self._stat_labels['total_precip'].setText(f"{total:.1f}" if pd.notna(total) else "N/A")

        avg_precip = precip_series.mean()
        self._stat_labels['avg_precip'].setText(f"{avg_precip:.1f}" if pd.notna(avg_precip) else "N/A")

        max_precip = precip_series.max()
        self._stat_labels['max_precip'].setText(f"{max_precip:.1f}" if pd.notna(max_precip) else "N/A")

        rainy_days = len(precip_series[precip_series > 0.1])
        self._stat_labels['rainy_days'].setText(f"{rainy_days}")

    except Exception as e:
        logger.error(f"Csapadék statisztika hiba: {e}")
        _clear_stats_range(self, ['total_precip', 'avg_precip', 'max_precip', 'rainy_days'])


def _set_stat_if_exists(
    self,
    df: pd.DataFrame,
    col: str,
    label_key: str,
    formatter
) -> None:
    """Statisztika beállítása ha az oszlop létezik."""
    if col not in df.columns:
        self._stat_labels[label_key].setText("N/A")
        return

    series = df[col].dropna()
    if series.empty:
        self._stat_labels[label_key].setText("N/A")
        return

    value = series.max() if 'max' in label_key else series.min()
    if pd.notna(value) and value != float('-inf') and value != float('inf'):
        self._stat_labels[label_key].setText(formatter(series))
    else:
        self._stat_labels[label_key].setText("N/A")


def _clear_stats_range(self, keys: list) -> None:
    """Statisztika tartomány törlése."""
    for key in keys:
        if key in self._stat_labels:
            self._stat_labels[key].setText("N/A")
