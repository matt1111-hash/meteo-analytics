#!/usr/bin/env python3
# mypy: ignore-errors

"""
Quick Overview Tab - Wind Info Stats

Szél és info statisztikák számítása.

Fájl: src/presentation/gui/results_panel/quick_overview_tab/wind_info_stats.py
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


def _resolve_wind_series(df: pd.DataFrame) -> tuple[pd.Series | None, str]:
    """Resolve wind series with source priority."""
    candidates = [
        ("wind_gusts_10m_max", "wind_gusts_10m_max"),
        ("wind_gusts_max", "wind_gusts_max"),
        ("windspeed", "windspeed_10m_max"),
    ]
    for column, source in candidates:
        if column not in df.columns:
            continue
        series = df[column].dropna()
        if not series.empty:
            logger.debug("WIND STATS: %s használva", column)
            return series, source
    return None, "unknown"


def calculate_wind_stats(self, df: pd.DataFrame) -> None:
    """Szél statisztikák számítása."""
    try:
        from ..utils import WindGustsAnalyzer

        wind_series, wind_data_source = _resolve_wind_series(df)
        if wind_series is None or wind_series.empty:
            _clear_stats_range(self, ["avg_wind", "max_wind", "windy_days", "wind_direction"])
            return

        if "wind_data_source" in df.columns:
            source_from_df = df["wind_data_source"].iloc[0]
            if source_from_df and source_from_df != "unknown":
                wind_data_source = source_from_df
        avg_wind = wind_series.mean()
        self._stat_labels["avg_wind"].setText(f"{avg_wind:.1f}" if pd.notna(avg_wind) else "N/A")
        max_wind = wind_series.max()
        if pd.notna(max_wind):
            self._stat_labels["max_wind"].setText(f"{max_wind:.1f}")
            _log_wind_category(max_wind, wind_data_source)
        else:
            self._stat_labels["max_wind"].setText("N/A")
        windy_threshold = WindGustsAnalyzer.get_windy_days_threshold(wind_data_source)
        windy_days = len(wind_series[wind_series > windy_threshold])
        self._stat_labels["windy_days"].setText(f"{windy_days}")

        logger.info(
            f"Wind stats - Source: {wind_data_source}, Threshold: {windy_threshold} km/h, Windy days: {windy_days}"
        )

    except Exception as e:
        logger.error(f"Szél statisztika hiba: {e}")
        _clear_stats_range(self, ["avg_wind", "max_wind", "windy_days", "wind_direction"])


def update_info_labels(self, data: dict, city_name: str, df: pd.DataFrame) -> None:
    """Információs labelek frissítése."""
    try:
        from ...utils import get_source_display_name

        self.city_info_label.setText(f"Város: {city_name}")

        daily_data = data.get("daily", {})
        dates = daily_data.get("time", [])
        if dates:
            start_date = dates[0]
            end_date = dates[-1]
            days_count = len(dates)
            self.date_range_label.setText(f"Időszak: {start_date} - {end_date} ({days_count} nap)")
        else:
            self.date_range_label.setText("Időszak: -")

        # Adatforrás
        data_source = data.get("source_type", data.get("data_source", "unknown"))
        display_source = get_source_display_name(data_source)
        self.data_source_label.setText(f"Adatforrás: {display_source}")

        record_count = len(df) if not df.empty else 0
        self.record_count_label.setText(f"Rekordok: {record_count} sor")

        logger.debug(f"Info labels updated - Source: {data_source} -> {display_source}")

    except Exception as e:
        logger.error(f"Info labelek frissítési hiba: {e}")
        self.city_info_label.setText("Város: -")
        self.date_range_label.setText("Időszak: -")
        self.data_source_label.setText("Adatforrás: -")
        self.record_count_label.setText("Rekordok: -")


def clear_stats(self) -> None:
    """Statisztikák törlése."""
    try:
        for label in self._stat_labels.values():
            label.setText("N/A")

        self.city_info_label.setText("Város: -")
        self.date_range_label.setText("Időszak: -")
        self.data_source_label.setText("Adatforrás: -")
        self.record_count_label.setText("Rekordok: -")

    except Exception as e:
        logger.error(f"Statisztikák törlési hiba: {e}")


def _log_wind_category(max_wind: float, data_source: str) -> None:
    """Szél kategória logolása."""
    from ..utils import WindGustsAnalyzer

    analyzer = WindGustsAnalyzer()
    category = analyzer.categorize_wind_gust(max_wind, data_source)

    if category == "hurricane":
        logger.critical(f"KRITIKUS: Hurrikán erősségű széllökés: {max_wind:.1f} km/h")
    elif category == "extreme":
        logger.warning(f"Extrém széllökés: {max_wind:.1f} km/h")
    elif category == "strong":
        logger.warning(f"Erős széllökés: {max_wind:.1f} km/h")


def _clear_stats_range(self, keys: list) -> None:
    """Statisztika tartomány törlése."""
    for key in keys:
        if key in self._stat_labels:
            self._stat_labels[key].setText("N/A")

    if "wind_direction" in self._stat_labels:
        self._stat_labels["wind_direction"].setText("N/A")
