#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mypy: ignore-errors

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

    @staticmethod
    def _debug_log(debug: bool, message: str) -> None:
        """Print debug messages only when debugging is enabled."""
        if debug:
            print(message)

    def _log_input_summary(
        self,
        debug: bool,
        data: Dict[str, Any],
        daily_data: Dict[str, Any],
        dates: list,
        wind_gusts_10m_max: list,
        windspeed_10m_max: list,
    ) -> None:
        """Emit structured debug information about the input payload."""
        self._debug_log(debug, "🌪️ DEBUG: _extract_wind_data() STARTED!!!")
        self._debug_log(debug, f"🌪️ DEBUG: data type: {type(data)}")
        self._debug_log(debug, f"🌪️ DEBUG: daily_data type: {type(daily_data)}")
        keys = list(daily_data.keys()) if isinstance(daily_data, dict) else "NOT DICT"
        self._debug_log(debug, f"🌪️ DEBUG: daily_data keys: {keys}")
        self._debug_log(debug, f"🌪️ DEBUG: dates: {len(dates) if dates else 0} elems")
        self._debug_log(
            debug,
            "🌪️ DEBUG: wind_gusts_10m_max: "
            f"{len(wind_gusts_10m_max) if wind_gusts_10m_max else 0} elems",
        )
        self._debug_log(
            debug,
            "🌪️ DEBUG: windspeed_10m_max: "
            f"{len(windspeed_10m_max) if windspeed_10m_max else 0} elems",
        )
        self._log_series_sample(debug, "wind_gusts_10m_max", wind_gusts_10m_max)
        self._log_series_sample(debug, "windspeed_10m_max", windspeed_10m_max)

    def _log_series_sample(self, debug: bool, label: str, values: list) -> None:
        """Print a short preview of a series for debugging."""
        if not debug or not values:
            return
        sample = values[:3] if len(values) >= 3 else values
        self._debug_log(debug, f"🌪️ DEBUG: {label} sample: {sample}")

    @staticmethod
    def _extract_daily_data(
        data: Dict[str, Any],
    ) -> tuple[Dict[str, Any], list, list, list]:
        """Extract daily payload and supported wind series from API data."""
        daily_data = data.get("daily", {})
        dates = daily_data.get("time", []) or daily_data.get("date", [])
        wind_gusts_10m_max = daily_data.get("windgusts_10m_max", []) or daily_data.get(
            "wind_gusts_max", []
        )
        windspeed_10m_max = daily_data.get("windspeed_10m_max", []) or daily_data.get(
            "wind_speed_max", []
        )
        return daily_data, dates, wind_gusts_10m_max, windspeed_10m_max

    def _build_dataframe(self, dates: list, windspeed_data: list) -> pd.DataFrame:
        """Create the normalized wind dataframe."""
        return pd.DataFrame(
            {
                "date": pd.to_datetime(dates),
                "windspeed": windspeed_data,
                "_data_source": self.data_source,
            }
        ).dropna()

    def _log_dataframe_summary(self, debug: bool, df: pd.DataFrame) -> None:
        """Print dataframe summary for debugging."""
        if df.empty:
            self._debug_log(
                debug, f"❌ DEBUG: Üres DataFrame {self.data_source} adatok után"
            )
            return
        max_wind = df["windspeed"].max()
        avg_wind = df["windspeed"].mean()
        self._debug_log(
            debug,
            "✅ DEBUG: WindChart DataFrame KÉSZ - "
            f"{self.data_source}, max: {max_wind:.1f} km/h, avg: {avg_wind:.1f} km/h",
        )

    def _use_selected_source(
        self, debug: bool, source: str, title: str, y_label: str, values: list
    ) -> list:
        """Store metadata for the selected data source and return its values."""
        self.data_source = source
        self.chart_title = title
        self.y_label = y_label
        self._debug_log(debug, f"✅ DEBUG: WindChart using source: {source}")
        return values

    def _is_usable_series(self, values: list, dates: list) -> bool:
        """Check whether a wind series is aligned with dates and contains data."""
        return bool(
            values and len(values) == len(dates) and self._has_valid_data(values)
        )

    def _log_unusable_sources(
        self, debug: bool, wind_gusts: list, windspeed: list, dates: list
    ) -> None:
        """Emit debug details when no suitable source is available."""
        self._debug_log(debug, "❌ DEBUG: Nincs használható szél adat")
        self._debug_log(
            debug,
            "   - wind_gusts_10m_max: "
            f"{len(wind_gusts) if wind_gusts else 0} elem, valid: "
            f"{self._has_valid_data(wind_gusts) if wind_gusts else False}",
        )
        self._debug_log(
            debug,
            "   - windspeed_10m_max: "
            f"{len(windspeed) if windspeed else 0} elem, valid: "
            f"{self._has_valid_data(windspeed) if windspeed else False}",
        )
        self._debug_log(debug, f"   - dates: {len(dates)} elem")

    def extract(self, data: Dict[str, Any], debug: bool = False) -> pd.DataFrame:
        """
        Extract wind data from API response.

        Args:
            data: API response dictionary
            debug: Enable debug logging

        Returns:
            DataFrame with date and windspeed columns
        """
        (
            daily_data,
            dates,
            wind_gusts_10m_max,
            windspeed_10m_max,
        ) = self._extract_daily_data(data)
        self._log_input_summary(
            debug,
            data,
            daily_data,
            dates,
            wind_gusts_10m_max,
            windspeed_10m_max,
        )

        # Validate dates
        if not dates:
            self._debug_log(
                debug, "⚠️ DEBUG: Nincs dátum adat - WindChart nem jeleníthető meg"
            )
            return pd.DataFrame()

        # PRIORITÁS KIÉRTÉKELÉS
        windspeed_data = self._select_wind_data_source(
            wind_gusts_10m_max, windspeed_10m_max, dates, debug
        )

        if not windspeed_data:
            self._debug_log(
                debug,
                "❌ DEBUG: Nincs használható szél adat - WindChart nem jeleníthető meg",
            )
            return pd.DataFrame()

        df = self._build_dataframe(dates, windspeed_data)
        self._log_dataframe_summary(debug, df)
        self._debug_log(debug, "🌪️ DEBUG: _extract_wind_data() FINISHED!")

        return df

    def _select_wind_data_source(
        self, wind_gusts: list, windspeed: list, dates: list, debug: bool
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
        self._debug_log(debug, "🌪️ DEBUG: Checking wind_gusts_10m_max priority...")
        if self._is_usable_series(wind_gusts, dates):
            return self._use_selected_source(
                debug,
                "wind_gusts_10m_max",
                "🌪️ Széllökések változása",
                "Széllökések (km/h)",
                wind_gusts,
            )
        if self._is_usable_series(windspeed, dates):
            self._debug_log(
                debug, "🌪️ DEBUG: wind_gusts_10m_max not suitable, checking fallback..."
            )
            return self._use_selected_source(
                debug,
                "windspeed_10m_max",
                "💨 Szélsebesség változása (Fallback)",
                "Szélsebesség (km/h)",
                windspeed,
            )
        self._log_unusable_sources(debug, wind_gusts, windspeed, dates)
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
