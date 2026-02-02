#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Wind Chart Data Extractor - Extract wind data from API responses.
🔧 KRITIKUS FIX v4.7: API KULCSOK KONZISZTENCIA JAVÍTÁS!
"""

from typing import Any, Dict

import pandas as pd


class WindDataExtractor:
    """
    Extract and validate wind data from API responses.

    PRIORITÁS RENDSZER:
    1. wind_gusts_10m_max (óránkénti→napi max széllökések) ⭐ ELSŐDLEGES
    2. windspeed_10m_max (napi max szélsebesség) ⭐ FALLBACK
    3. Hibaüzenet ha egyik sem elérhető
    """

    def __init__(self):
        """Initialize the data extractor."""
        self.chart_title = "🌪️ Széllökések változása"
        self.y_label = "Széllökések (km/h)"
        self.data_source = "unknown"

    def extract(self, data: Dict[str, Any], debug: bool = False) -> pd.DataFrame:
        """
        Extract wind data from API response.

        Args:
            data: API response dictionary
            debug: Enable debug logging

        Returns:
            DataFrame with date and windspeed columns
        """
        if debug:
            print("🌪️ DEBUG: _extract_wind_data() STARTED!!!")
            print(f"🌪️ DEBUG: data type: {type(data)}")

        daily_data = data.get("daily", {})

        if debug:
            print(f"🌪️ DEBUG: daily_data type: {type(daily_data)}")
            print(f"🌪️ DEBUG: daily_data keys: {list(daily_data.keys()) if isinstance(daily_data, dict) else 'NOT DICT'}")

        dates = daily_data.get("time", []) or daily_data.get("date", [])

        if debug:
            print(f"🌪️ DEBUG: dates: {len(dates) if dates else 0} elems")

        # API KULCSOK KONZISZTENCIA - OpenMeteo + KOMPATIBILITÁSI KULCSOK
        wind_gusts_10m_max = daily_data.get("windgusts_10m_max", []) or daily_data.get("wind_gusts_max", [])
        windspeed_10m_max = daily_data.get("windspeed_10m_max", []) or daily_data.get("wind_speed_max", [])

        if debug:
            print(f"🌪️ DEBUG: wind_gusts_10m_max: {len(wind_gusts_10m_max) if wind_gusts_10m_max else 0} elems")
            print(f"🌪️ DEBUG: windspeed_10m_max: {len(windspeed_10m_max) if windspeed_10m_max else 0} elems")
            if wind_gusts_10m_max:
                sample = wind_gusts_10m_max[:3] if len(wind_gusts_10m_max) >= 3 else wind_gusts_10m_max
                print(f"🌪️ DEBUG: wind_gusts_10m_max sample: {sample}")
            if windspeed_10m_max:
                sample = windspeed_10m_max[:3] if len(windspeed_10m_max) >= 3 else windspeed_10m_max
                print(f"🌪️ DEBUG: windspeed_10m_max sample: {sample}")

        # Validate dates
        if not dates:
            if debug:
                print("⚠️ DEBUG: Nincs dátum adat - WindChart nem jeleníthető meg")
            return pd.DataFrame()

        # PRIORITÁS KIÉRTÉKELÉS
        windspeed_data = self._select_wind_data_source(
            wind_gusts_10m_max,
            windspeed_10m_max,
            dates,
            debug
        )

        if not windspeed_data:
            if debug:
                print("❌ DEBUG: Nincs használható szél adat - WindChart nem jeleníthető meg")
            return pd.DataFrame()

        # DataFrame létrehozása
        df = pd.DataFrame({
            'date': pd.to_datetime(dates),
            'windspeed': windspeed_data,
            '_data_source': self.data_source
        })

        # NaN értékek kezelése
        df = df.dropna()

        if df.empty:
            if debug:
                print(f"❌ DEBUG: Üres DataFrame {self.data_source} adatok után")
        elif debug:
            max_wind = df['windspeed'].max()
            avg_wind = df['windspeed'].mean()
            print(f"✅ DEBUG: WindChart DataFrame KÉSZ - {self.data_source}, max: {max_wind:.1f} km/h, avg: {avg_wind:.1f} km/h")

        if debug:
            print("🌪️ DEBUG: _extract_wind_data() FINISHED!")

        return df

    def _select_wind_data_source(
        self,
        wind_gusts: list,
        windspeed: list,
        dates: list,
        debug: bool
    ) -> list:
        """
        Select the best available wind data source.

        Args:
            wind_gusts: wind_gusts_10m_max data
            windspeed: windspeed_10m_max data
            dates: Date list for length validation
            debug: Enable debug logging

        Returns:
            Selected wind data list or empty list
        """
        if debug:
            print("🌪️ DEBUG: Checking wind_gusts_10m_max priority...")

        # ELSŐDLEGES: wind_gusts_10m_max
        if wind_gusts and len(wind_gusts) == len(dates) and self._has_valid_data(wind_gusts):
            if debug:
                print(f"✅ DEBUG: WindChart using PRIMARY source: wind_gusts_10m_max")
            self.data_source = "wind_gusts_10m_max"
            self.chart_title = "🌪️ Széllökések változása"
            self.y_label = "Széllökések (km/h)"
            return wind_gusts

        # FALLBACK: windspeed_10m_max
        if windspeed and len(windspeed) == len(dates) and self._has_valid_data(windspeed):
            if debug:
                print("🌪️ DEBUG: wind_gusts_10m_max not suitable, checking fallback...")
                print(f"⚠️ DEBUG: WindChart using FALLBACK source: windspeed_10m_max")
            self.data_source = "windspeed_10m_max"
            self.chart_title = "💨 Szélsebesség változása (Fallback)"
            self.y_label = "Szélsebesség (km/h)"
            return windspeed

        if debug:
            print("❌ DEBUG: Nincs használható szél adat")
            print(f"   - wind_gusts_10m_max: {len(wind_gusts) if wind_gusts else 0} elem, valid: {self._has_valid_data(wind_gusts) if wind_gusts else False}")
            print(f"   - windspeed_10m_max: {len(windspeed) if windspeed else 0} elem, valid: {self._has_valid_data(windspeed) if windspeed else False}")
            print(f"   - dates: {len(dates)} elem")

        return []

    @staticmethod
    def _has_valid_data(data_list: list) -> bool:
        """
        Check if list contains valid numeric data (not just None values).

        Args:
            data_list: List to check

        Returns:
            True if list contains valid numeric data
        """
        return any(x is not None and isinstance(x, (int, float)) for x in data_list)
