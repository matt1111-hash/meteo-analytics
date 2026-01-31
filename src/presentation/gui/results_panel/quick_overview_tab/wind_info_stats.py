#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Quick Overview Tab - Wind Info Stats

Szél és info statisztikák számítása.

Fájl: src/presentation/gui/results_panel/quick_overview_tab/wind_info_stats.py
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Dict, Optional, Tuple

import pandas as pd

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


def _select_wind_column(df: pd.DataFrame, wind_data_source: str) -> Tuple[Optional[str], str]:
    """Szél oszlop kiválasztása a DataFrame-ből elérhető adatok alapján."""
    if wind_data_source == 'windspeed':
        candidates = ['windspeed']
    elif wind_data_source == 'wind_gusts_10m_max':
        candidates = ['wind_gusts_10m_max', 'windgusts_10m_max', 'wind_gusts_max']
    elif wind_data_source == 'no_data':
        candidates = ['windspeed']
    else:
        candidates = ['wind_gusts_10m_max', 'windgusts_10m_max', 'wind_gusts_max', 'windspeed']

    for col in candidates:
        if col in df.columns:
            non_null = df[col].dropna()
            if not non_null.empty:
                normalized_source = wind_data_source
                if col in ['wind_gusts_10m_max', 'windgusts_10m_max']:
                    normalized_source = 'wind_gusts_10m_max'
                elif col == 'wind_gusts_max':
                    normalized_source = 'wind_gusts_max'
                elif col == 'windspeed':
                    normalized_source = 'windspeed'
                return col, normalized_source

    for col in candidates:
        if col in df.columns:
            if col in ['wind_gusts_10m_max', 'windgusts_10m_max']:
                return col, 'wind_gusts_10m_max'
            if col == 'wind_gusts_max':
                return col, 'wind_gusts_max'
            if col == 'windspeed':
                return col, 'windspeed'

    return None, wind_data_source


def calculate_wind_stats(self, df: pd.DataFrame) -> None:
    """Szél statisztikák számítása."""
    try:
        from ..utils import WindGustsAnalyzer

        print(f"🌪️ DEBUG: calculate_wind_stats() - df.columns: {list(df.columns)}")
        print(f"🌪️ DEBUG: df.shape: {df.shape}")
        print(f"🌪️ DEBUG: windspeed in columns: {'windspeed' in df.columns}")

        wind_data_source = 'unknown'
        if 'wind_data_source' in df.columns and not df['wind_data_source'].empty:
            wind_data_source = df['wind_data_source'].iloc[0]
            print(f"🔍 DEBUG: wind_data_source = '{wind_data_source}'")

        wind_column, wind_data_source = _select_wind_column(df, wind_data_source)
        if wind_data_source == 'wind_gusts_10m_max' and wind_column != 'wind_gusts_10m_max':
            print(f"⚠️ DEBUG: wind_gusts_10m_max source, fallback column = {wind_column}")

        if wind_column is None:
            print("❌ DEBUG: NO WIND DATA FOUND in df.columns!")
            print(f"❌ DEBUG: Available wind columns: {[c for c in df.columns if 'wind' in c.lower()]}")
            _clear_stats_range(self, ['avg_wind', 'max_wind', 'windy_days', 'wind_direction'])
            return

        print(f"✅ DEBUG: {wind_column} column FOUND!")
        print(f"🌪️ DEBUG: {wind_column} sample (first 5): {df[wind_column].head().tolist()}")

        wind_series = df[wind_column].dropna()

        # 🔥 KRITIKUS JAVÍTÁS: Ellenőrizzük, hogy van-e érvényes adat a wind_series-ben
        if wind_series.empty:
            print(f"❌ DEBUG: {wind_column} column is EMPTY after dropna()!")
            print("❌ DEBUG: All values are None or NaN")

            # 🔄 FALLBACK: Ha bármelyik széllökés oszlop üres, próbáljuk a windspeed oszlopot
            if wind_column in ['wind_gusts_max', 'wind_gusts_10m_max', 'windgusts_10m_max'] and 'windspeed' in df.columns:
                print("🔄 DEBUG: Trying fallback to 'windspeed' column...")
                wind_column = 'windspeed'
                wind_data_source = 'windspeed'
                wind_series = df[wind_column].dropna()

                if wind_series.empty:
                    print("❌ DEBUG: 'windspeed' column is also EMPTY!")
                    _clear_stats_range(self, ['avg_wind', 'max_wind'])
                    self._stat_labels['windy_days'].setText("0")
                    return
                else:
                    print("✅ DEBUG: Fallback to 'windspeed' SUCCESSFUL!")
            else:
                _clear_stats_range(self, ['avg_wind', 'max_wind'])
                self._stat_labels['windy_days'].setText("0")
                return

        if wind_series.empty:
            _clear_stats_range(self, ['avg_wind', 'max_wind'])
            self._stat_labels['windy_days'].setText("0")
            return

        # Adatforrás (már beállítva fentebb)
        # wind_data_source = 'unknown'
        # if 'wind_data_source' in df.columns:
        #     wind_data_source = df['wind_data_source'].iloc[0]

        # Átlagos szél
        avg_wind = wind_series.mean()
        self._stat_labels['avg_wind'].setText(f"{avg_wind:.1f}" if pd.notna(avg_wind) else "N/A")

        # Maximum szél
        max_wind = wind_series.max()
        if pd.notna(max_wind):
            self._stat_labels['max_wind'].setText(f"{max_wind:.1f}")
            _log_wind_category(max_wind, wind_data_source)
        else:
            self._stat_labels['max_wind'].setText("N/A")

        # Szeles napok
        windy_threshold = WindGustsAnalyzer.get_windy_days_threshold(wind_data_source)
        windy_days = len(wind_series[wind_series > windy_threshold])
        self._stat_labels['windy_days'].setText(f"{windy_days}")

        # 🧭 Uralkodó szélirány kiszámítása
        dominant_direction = _calculate_dominant_direction(df)
        self._stat_labels['wind_direction'].setText(dominant_direction)

        logger.info(f"Wind stats - Source: {wind_data_source}, Threshold: {windy_threshold} km/h, Windy days: {windy_days}")

    except Exception as e:
        logger.error(f"Szél statisztika hiba: {e}")
        _clear_stats_range(self, ['avg_wind', 'max_wind', 'windy_days', 'wind_direction'])


def update_info_labels(self, data: Dict, city_name: str, df: pd.DataFrame) -> None:
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

    if category == 'hurricane':
        logger.critical(f"KRITIKUS: Hurrikán erősségű széllökés: {max_wind:.1f} km/h")
    elif category == 'extreme':
        logger.warning(f"Extrém széllökés: {max_wind:.1f} km/h")
    elif category == 'strong':
        logger.warning(f"Erős széllökés: {max_wind:.1f} km/h")


def _calculate_dominant_direction(df: pd.DataFrame) -> str:
    """
    Uralkodó szélirány kiszámítása a DataFrame alapján.

    Args:
        df: DataFrame szélirány adatokkal

    Returns:
        str: Uralkodó irány (pl. "ÉK", "D") vagy "N/A" ha nincs adat
    """
    direction_col = None
    for col in ['winddirection', 'winddirection_10m_dominant', 'wind_direction_10m_dominant']:
        if col in df.columns:
            direction_col = col
            break

    if direction_col is None:
        return "N/A"

    direction_series = df[direction_col].dropna()
    if direction_series.empty:
        return "N/A"

    # Szélirányok kategorizálása 8 fő irányba
    # 0° = É, 90° = K, 180° = D, 270° = NY
    def degrees_to_direction(deg: float) -> str:
        if pd.isna(deg):
            return "N/A"
        # 8 fő irány: É, ÉK, K, DK, D, DN, NY, ÉNY
        # Határok: 0-22.5, 22.5-67.5, 67.5-112.5, stb.
        directions = ["É", "ÉK", "K", "DK", "D", "DN", "NY", "ÉNY"]
        index = round(deg / 45) % 8
        return directions[index]

    # Minden értéket iránnyá konvertálunk
    directions = [degrees_to_direction(d) for d in direction_series]

    # Leggyakoribb irány megtalálása (N/A kizárásával)
    valid_directions = [d for d in directions if d != "N/A"]
    if not valid_directions:
        return "N/A"

    from collections import Counter
    direction_counts = Counter(valid_directions)
    dominant = direction_counts.most_common(1)[0][0]

    return dominant


def _clear_stats_range(self, keys: list) -> None:
    """Statisztika tartomány törlése."""
    for key in keys:
        if key in self._stat_labels:
            self._stat_labels[key].setText("N/A")

    if 'wind_direction' in self._stat_labels:
        self._stat_labels['wind_direction'].setText("N/A")
