#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Results Panel Utils - DataFrame Extractor

🔥 Adatok DataFrame-be konvertálásáért felelős utility osztály

Képességek:
- API válasz feldolgozása
- DataFrame létrehozása
- Validáció és minőség ellenőrzés

Fájl: src/presentation/gui/results_panel/utils/dataframe_extractor.py
"""

import logging
from typing import Any, Dict, List

import pandas as pd

logger = logging.getLogger(__name__)


class DataFrameExtractor:
    """
    🔥 JAVÍTOTT: Adatok DataFrame-be konvertálásáért felelős utility osztály.
    🎯 API KONZISZTENCIA: Helyes mezőnevek használata
    🌪️ WIND GUSTS TÁMOGATÁS: wind_gusts_10m_max prioritással, windspeed_10m_max fallback-kel
    """

    @staticmethod
    def extract_safely(data: Dict[str, Any]) -> pd.DataFrame:
        """
        🔥 KRITIKUS JAVÍTÁS: Adatok DataFrame-be konvertálása - API KONZISZTENS mezőnevekkel.

        JAVÍTÁS: wind_gusts_10m_max → wind_gusts_max API konzisztencia

        Args:
            data: OpenMeteo API válasz

        Returns:
            pandas.DataFrame: Feldolgozott időjárási adatok

        Raises:
            ValueError: Ha az adatok nem megfelelő formátumúak
        """
        try:
            logger.debug("DataFrameExtractor.extract_safely() - START")

            daily_data = data.get("daily", {})
            if not daily_data:
                logger.warning("Nincs 'daily' adat a válaszban")
                return pd.DataFrame()

            dates = daily_data.get("time", [])
            if not dates:
                logger.warning("Nincs 'time' adat a daily adatokban")
                return pd.DataFrame()

            logger.debug(f"Extracting {len(dates)} napok adatai...")

            # === HŐMÉRSÉKLET ADATOK ===
            temp_max = daily_data.get("temperature_2m_max", [])
            temp_min = daily_data.get("temperature_2m_min", [])
            temp_mean = daily_data.get("temperature_2m_mean", [])

            # === CSAPADÉK ADATOK ===
            precip = daily_data.get("precipitation_sum", [])

            # === 🔥 KRITIKUS JAVÍTÁS: API KONZISZTENS MEZŐNEVEK ===
            # Az OpenMeteo API ezeket a mezőneveket használja:
            wind_gusts_10m_max = daily_data.get("wind_gusts_10m_max", [])  # 🌪️ SZÉLLÖKÉSEK (ELSŐDLEGES)
            windspeed_10m_max = daily_data.get("windspeed_10m_max", [])    # 💨 SZÉLSEBESSÉG (FALLBACK)

            # Hiányzó temp_mean számítása ha nincs
            if not temp_mean and temp_max and temp_min:
                logger.debug("Temp_mean számítása temp_max és temp_min alapján...")
                temp_mean = [
                    round((t_max + t_min) / 2, 1) if t_max is not None and t_min is not None else None
                    for t_max, t_min in zip(temp_max, temp_min)
                ]

            max_length = len(dates)

            # === DATAFRAME ÖSSZEÁLLÍTÁSA ===
            df_data = {
                'date': dates,
                'temp_max': DataFrameExtractor._ensure_length(temp_max, max_length),
                'temp_min': DataFrameExtractor._ensure_length(temp_min, max_length),
                'precipitation': DataFrameExtractor._ensure_length(precip, max_length)
            }

            # Temp_mean hozzáadása ha van
            if temp_mean:
                df_data['temp_mean'] = DataFrameExtractor._ensure_length(temp_mean, max_length)

            # === 🔥 KRITIKUS JAVÍTÁS: HELYES SZÉLLÖKÉS PRIORITÁS ===
            if wind_gusts_10m_max:
                # 🌪️ ELSŐDLEGES: wind_gusts_10m_max (VALÓDI széllökések 10-87 km/h)
                df_data['wind_gusts_max'] = DataFrameExtractor._ensure_length(wind_gusts_10m_max, max_length)
                df_data['wind_data_source'] = ['wind_gusts_10m_max'] * max_length
                logger.info(f"✅ HELYES SZÉLLÖKÉS FORRÁS: wind_gusts_10m_max ({len(wind_gusts_10m_max)} values)")

            elif windspeed_10m_max:
                # 💨 FALLBACK: windspeed_10m_max (átlagos szélsebesség 3-41 km/h)
                df_data['wind_gusts_max'] = DataFrameExtractor._ensure_length(windspeed_10m_max, max_length)
                df_data['wind_data_source'] = ['windspeed_10m_max'] * max_length
                logger.warning(f"⚠️ FALLBACK TO SZÉLSEBESSÉG: windspeed_10m_max ({len(windspeed_10m_max)} values)")

            else:
                # ❌ NINCS SZÉL ADAT
                logger.error("❌ Nincs szél adat sem wind_gusts_10m_max, sem windspeed_10m_max")
                df_data['wind_gusts_max'] = [None] * max_length
                df_data['wind_data_source'] = ['no_data'] * max_length

            # BACKWARD COMPATIBILITY: windspeed oszlop is (régi kódok számára)
            if 'wind_gusts_max' in df_data:
                df_data['windspeed'] = df_data['wind_gusts_max']

            # DataFrame létrehozása
            df = pd.DataFrame(df_data)

            logger.info(f"✅ DataFrame extracted successfully: {df.shape} (rows, cols)")
            logger.debug(f"Columns: {list(df.columns)}")

            # 🔍 DEBUG: Széladatok tartománya
            if 'wind_gusts_max' in df.columns:
                wind_data = df['wind_gusts_max'].dropna()
                if len(wind_data) > 0:
                    source = df['wind_data_source'].iloc[0] if 'wind_data_source' in df.columns else 'unknown'
                    logger.info(f"🌪️ Wind stats - Source: {source}")
                    logger.info(f"🌪️ Wind range: {wind_data.min():.1f} → {wind_data.max():.1f} km/h")

            return df

        except Exception as e:
            logger.error(f"❌ DataFrame extract hiba: {e}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()

    @staticmethod
    def _ensure_length(lst: List, target: int) -> List:
        """
        Lista hosszának biztosítása célérték szerint.

        Args:
            lst: Input lista
            target: Célhossz

        Returns:
            List: Megfelelő hosszúságú lista
        """
        if not lst:
            return [None] * target

        current_len = len(lst)

        if current_len == target:
            return lst
        elif current_len < target:
            # Kiegészítés None értékekkel
            return lst + [None] * (target - current_len)
        else:
            # Levágás célhosszra
            return lst[:target]

    @staticmethod
    def validate_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
        """
        DataFrame validálása és minőség ellenőrzése.

        Args:
            df: Validálandó DataFrame

        Returns:
            Validációs eredmények dictionary
        """
        try:
            if df.empty:
                return {
                    "valid": False,
                    "error": "DataFrame üres",
                    "rows": 0,
                    "columns": 0
                }

            # Alapvető statisztikák
            stats = {
                "valid": True,
                "rows": len(df),
                "columns": len(df.columns),
                "date_range": None,
                "missing_data": {},
                "wind_source": "unknown"
            }

            # Dátum tartomány
            if 'date' in df.columns and not df['date'].empty:
                stats["date_range"] = f"{df['date'].iloc[0]} - {df['date'].iloc[-1]}"

            # Hiányzó adatok számlálása
            for col in df.columns:
                missing_count = df[col].isna().sum()
                if missing_count > 0:
                    stats["missing_data"][col] = missing_count

            # Szél adatforrás detektálása
            if 'wind_data_source' in df.columns and not df['wind_data_source'].empty:
                stats["wind_source"] = df['wind_data_source'].iloc[0]

            logger.debug(f"DataFrame validation: {stats}")
            return stats

        except Exception as e:
            logger.error(f"DataFrame validation hiba: {e}")
            return {
                "valid": False,
                "error": str(e),
                "rows": 0,
                "columns": 0
            }
