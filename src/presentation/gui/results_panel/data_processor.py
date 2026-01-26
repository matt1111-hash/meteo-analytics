#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Data Processor - DataFrame konverzió és adatfeldolgozás

Kezeli az időjárási adatok DataFrame konverzióját,
a wind speed adatok feldolgozását és a WindyDaysTab
adatok előkészítését.
"""

import logging
from typing import Dict, Any, Optional

try:
    import pandas as pd
    _pandas_available = True
except ImportError:
    _pandas_available = False
    pd = None

from PySide6.QtCore import QObject


class DataProcessor(QObject):
    """
    Adatfeldolgozás és DataFrame konverzió kezelése.

    Felelőségek:
    - DataFrame konverzió API válaszból
    - Wind speed adatok feldolgozása
    - WindyDaysTab adatok előkészítése
    - Adat validálás
    """

    def __init__(self, parent=None):
        """
        DataProcessor inicializálása.

        Args:
            parent: Szülő QObject
        """
        super().__init__(parent)
        self._logger = logging.getLogger(__name__)
        self._dataframe_extractor_available = False

        # DataFrameExtractor import
        try:
            from ..utils import DataFrameExtractor
            self.DataFrameExtractor = DataFrameExtractor
            self._dataframe_extractor_available = True
            self._logger.info("✅ DataFrameExtractor import successful")
        except ImportError as e:
            self._logger.warning(f"⚠️ DataFrameExtractor import failed: {e}")

    def convert_data_to_dataframe(self, data: Dict[str, Any]) -> Any:
        """
        DataFrame konverzió API válaszból DataFrameExtractor-rel.

        Args:
            data: OpenMeteo API response

        Returns:
            pandas.DataFrame: Feldolgozott időjárási adatok
        """
        try:
            self._logger.info("🔥 DataFrameExtractor.extract_safely() használata...")

            if self._dataframe_extractor_available:
                df = self.DataFrameExtractor.extract_safely(data)

                if df.empty:
                    self._logger.error("❌ DataFrameExtractor üres DataFrame-et adott vissza!")
                    return self._empty_dataframe_fallback()

                # DataFrame tartalom ellenőrzése
                self._logger.info(f"🎯 DataFrame oszlopok: {list(df.columns)}")

                # Wind speed oszlop biztosítása
                df = self._ensure_wind_speed_column(df)

                self._logger.info("✅ DataFrameExtractor.extract_safely() sikeres!")
                return df
            else:
                # Fallback konverzió
                return self._fallback_conversion(data)

        except Exception as e:
            self._logger.error(f"❌ _convert_data_to_dataframe KRITIKUS hiba: {e}")
            import traceback
            traceback.print_exc()
            return self._empty_dataframe_fallback()

    def _ensure_wind_speed_column(self, df: Any) -> Any:
        """
        Wind speed oszlop biztosítása a DataFrame-ben.

        Args:
            df: DataFrame

        Returns:
            DataFrame wind_speed oszloppal
        """
        if 'wind_gusts_max' in df.columns:
            # WindyDaysTab wind_speed oszlopot vár!
            df['wind_speed'] = df['wind_gusts_max']
            self._logger.info("🔥 WIND_SPEED OSZLOP JAVÍTÁS: wind_gusts_max → wind_speed mapping!")

            wind_data = df['wind_speed'].dropna()
            if len(wind_data) > 0:
                valid_winds = wind_data[wind_data > 0]
                if len(valid_winds) > 0:
                    self._logger.info(f"🌪️ Wind speed range: {valid_winds.min():.1f} → {valid_winds.max():.1f} km/h")
                    self._logger.info(f"🌪️ Valid records: {len(valid_winds)}/{len(df)}")
            else:
                self._logger.error("❌ Nincs valid wind gust adat!")
        else:
            self._logger.error("❌ Nincs wind_gusts_max oszlop a DataFrame-ben!")
            # Próbáljuk meg windspeed oszlopból
            if 'windspeed' in df.columns:
                df['wind_speed'] = df['windspeed']
                self._logger.warning("⚠️ FALLBACK: windspeed → wind_speed mapping!")
            else:
                self._logger.error("❌ Nincs windspeed oszlop sem!")

        return df

    def _fallback_conversion(self, data: Dict[str, Any]) -> Any:
        """
        Fallback konverzió ha DataFrameExtractor nem elérhető.

        Args:
            data: Nyers API adatok

        Returns:
            DataFrame vagy üres dict
        """
        self._logger.error("❌ DataFrameExtractor nem elérhető - fallback konverzió")

        try:
            import pandas as pd
            self._logger.info("🔥 FALLBACK: Saját DataFrame konverzió...")

            daily_data = data.get('daily', {}) or data.get('hourly', {})

            if not daily_data:
                self._logger.error("❌ Nincs daily vagy hourly adat!")
                return pd.DataFrame()

            times = daily_data.get('time', [])
            if not times:
                self._logger.error("❌ Nincs time adat!")
                return pd.DataFrame()

            # Wind adatok keresése
            wind_data = None
            wind_source = None

            for key in ['wind_gusts_10m_max', 'windspeed_10m_max', 'wind_speed']:
                if key in daily_data and daily_data[key]:
                    wind_data = daily_data[key]
                    wind_source = key
                    break

            if wind_data is None:
                self._logger.error("❌ Nincs szél adat!")
                return pd.DataFrame()

            self._logger.info(f"🎯 FALLBACK wind source: {wind_source}")

            # DataFrame létrehozása
            df = pd.DataFrame({
                'date': times,
                'wind_speed': wind_data,
                'wind_gusts_max': wind_data,
                'wind_data_source': [wind_source] * len(times)
            })

            self._logger.info(f"🔄 FALLBACK DataFrame: {len(df)} sor, source: {wind_source}")
            return df

        except Exception as fallback_error:
            self._logger.error(f"❌ FALLBACK konverzió is sikertelen: {fallback_error}")
            return self._empty_dataframe_fallback()

    @staticmethod
    def _empty_dataframe_fallback() -> Any:
        """Üres DataFrame fallback."""
        try:
            import pandas as pd
            return pd.DataFrame()
        except Exception:
            return {}

    def process_windy_days_data(self, weather_df: Any, city_name: str,
                                deliver_callback) -> None:
        """
        WindyDaysTab adatok feldolgozása és kézbesítése.

        Args:
            weather_df: DataFrame időjárási adatokkal
            city_name: Város neve
            deliver_callback: Callback az adatok kézbesítéséhez
        """
        if not hasattr(weather_df, '__len__'):
            self._logger.error("❌ INVALID RETURN TYPE from _convert_data_to_dataframe!")
            deliver_callback(self._empty_dataframe_fallback(), city_name)
            return

        self._logger.info(f"⚡ Konvertált adatok: {len(weather_df)} elem")

        if hasattr(weather_df, 'empty'):
            self._handle_dataframe_weather_data(weather_df, city_name, deliver_callback)
            return

        self._logger.warning("⚠️ FALLBACK DICT - próbáljuk WindyDaysTab-bal")
        deliver_callback(weather_df, city_name)

    def _handle_dataframe_weather_data(self, weather_df: Any, city_name: str,
                                      deliver_callback) -> None:
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

        if 'wind_speed' in weather_df.columns:
            self._process_wind_speed_column(weather_df, city_name, deliver_callback)
            return

        self._logger.error("❌ NINCS WIND_SPEED OSZLOP!")
        if 'wind_gusts_max' in weather_df.columns:
            self._logger.warning("⚠️ EMERGENCY FIX: wind_gusts_max → wind_speed konverzió!")
            weather_df['wind_speed'] = weather_df['wind_gusts_max']
            deliver_callback(weather_df, city_name)
        else:
            deliver_callback(self._empty_dataframe_fallback(), city_name)

    def _process_wind_speed_column(self, weather_df: Any, city_name: str,
                                   deliver_callback) -> None:
        """
        Wind speed oszlop feldolgozása.

        Args:
            weather_df: DataFrame
            city_name: Város neve
            deliver_callback: Callback az adatok kézbesítéséhez
        """
        wind_data = weather_df['wind_speed'].dropna()
        if len(wind_data) == 0:
            deliver_callback(self._empty_dataframe_fallback(), city_name)
            return

        valid_winds = wind_data[wind_data > 0]
        if len(valid_winds) == 0:
            self._logger.warning("⚠️ Minden szélsebesség 0 vagy invalid!")
            deliver_callback(self._empty_dataframe_fallback(), city_name)
            return

        self._logger.info(f"📧 Wind speed range (km/h): {valid_winds.min():.1f} → {valid_winds.max():.1f}")
        self._logger.info(f"📧 Valid wind records: {len(valid_winds)}/{len(wind_data)}")

        if 'wind_data_source' in weather_df.columns:
            source = weather_df['wind_data_source'].iloc[0] if not weather_df['wind_data_source'].empty else 'unknown'
            self._logger.info(f"🎯 DATAFRAME EXTRACTOR SOURCE: {source}")

        self._logger.info("🚨 KRITIKUS: WindyDaysTab.update_data() HÍVÁS...")
        deliver_callback(weather_df, city_name)
        self._logger.info("✅ WindyDaysTab.update_data() SIKERES!")
