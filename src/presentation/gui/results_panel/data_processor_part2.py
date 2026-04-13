# ruff: noqa: F403, F405,noqa: I001
# mypy: ignore-errors
"""Mixin part 2 for DataProcessor."""

from __future__ import annotations

from .data_processor_support import *


class DataProcessorPart2Mixin:  # noqa: D101
    @staticmethod
    def _empty_dataframe_fallback() -> Any:
        """Üres DataFrame fallback."""
        try:
            import pandas as pd

            return pd.DataFrame()
        except Exception:
            return {}

    def process_windy_days_data(self, weather_df: Any, city_name: str, deliver_callback) -> None:
        """
        WindyDaysTab adatok feldolgozása és kézbesítése.

        Args:
            weather_df: DataFrame időjárási adatokkal
            city_name: Város neve
            deliver_callback: Callback az adatok kézbesítéséhez
        """
        if not hasattr(weather_df, "__len__"):
            self._logger.error("❌ INVALID RETURN TYPE from _convert_data_to_dataframe!")
            deliver_callback(self._empty_dataframe_fallback(), city_name)
            return

        self._logger.info(f"⚡ Konvertált adatok: {len(weather_df)} elem")

        if hasattr(weather_df, "empty"):
            self._handle_dataframe_weather_data(weather_df, city_name, deliver_callback)
            return

        self._logger.warning("⚠️ FALLBACK DICT - próbáljuk WindyDaysTab-bal")
        deliver_callback(weather_df, city_name)

    def _handle_dataframe_weather_data(
        self, weather_df: Any, city_name: str, deliver_callback
    ) -> None:
        """
        DataFrame típusú időjárási adatok kezelése.

        Args:
            weather_df: DataFrame
            city_name: Város neve
            deliver_callback: Callback az adatok kézbesítéséhez
        """
        if weather_df.empty:
            deliver_callback(self._empty_dataframe_fallback(), city_name)
            return

        self._logger.info(f"📧 DataFrame oszlopok: {list(weather_df.columns)}")

        if "wind_speed" in weather_df.columns:
            self._process_wind_speed_column(weather_df, city_name, deliver_callback)
            return

        self._logger.error("❌ NINCS WIND_SPEED OSZLOP!")
        if "wind_gusts_max" in weather_df.columns:
            self._logger.warning("⚠️ EMERGENCY FIX: wind_gusts_max → wind_speed konverzió!")
            weather_df["wind_speed"] = weather_df["wind_gusts_max"]
            deliver_callback(weather_df, city_name)
        else:
            deliver_callback(self._empty_dataframe_fallback(), city_name)

    def _process_wind_speed_column(self, weather_df: Any, city_name: str, deliver_callback) -> None:
        """
        Wind speed oszlop feldolgozása.

        Args:
            weather_df: DataFrame
            city_name: Város neve
            deliver_callback: Callback az adatok kézbesítéséhez
        """
        wind_data = weather_df["wind_speed"].dropna()
        if len(wind_data) == 0:
            deliver_callback(self._empty_dataframe_fallback(), city_name)
            return

        valid_winds = wind_data[wind_data > 0]
        if len(valid_winds) == 0:
            self._logger.warning("⚠️ Minden szélsebesség 0 vagy invalid!")
            deliver_callback(self._empty_dataframe_fallback(), city_name)
            return

        self._logger.info(
            f"📧 Wind speed range (km/h): {valid_winds.min():.1f} → {valid_winds.max():.1f}"
        )
        self._logger.info(f"📧 Valid wind records: {len(valid_winds)}/{len(wind_data)}")

        if "wind_data_source" in weather_df.columns:
            source = (
                weather_df["wind_data_source"].iloc[0]
                if not weather_df["wind_data_source"].empty
                else "unknown"
            )
            self._logger.info(f"🎯 DATAFRAME EXTRACTOR SOURCE: {source}")

        self._logger.info("🚨 KRITIKUS: WindyDaysTab.update_data() HÍVÁS...")
        deliver_callback(weather_df, city_name)
        self._logger.info("✅ WindyDaysTab.update_data() SIKERES!")
