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

            dates = daily_data.get("time", []) or daily_data.get("date", [])
            if not dates:
                logger.warning("Nincs 'time' vagy 'date' adat a daily adatokban")
                return pd.DataFrame()

            logger.debug(f"Extracting {len(dates)} napok adatai...")

            # === HŐMÉRSÉKLET ADATOK ===
            temp_max = daily_data.get("temperature_2m_max", [])
            temp_min = daily_data.get("temperature_2m_min", [])
            temp_mean = daily_data.get("temperature_2m_mean", [])

            # === CSAPADÉK ADATOK ===
            precip = daily_data.get("precipitation_sum", [])

            # === 🔥 KRITIKUS JAVÍTÁS: API KONZISZTENS MEZŐNEVEK ===
            # OpenMeteo mezőnevek (API válasz) + KOMPATIBILITÁSI KULCSOK (data_converter után)
            # API returns: wind_gusts_10m_max → Converter creates: wind_gusts_max, windgusts_10m_max
            # API returns: windspeed_10m_max → Converter creates: wind_speed_max
            wind_gusts_10m_max = (
                daily_data.get("wind_gusts_10m_max", [])
                or daily_data.get("windgusts_10m_max", [])
                or daily_data.get("wind_gusts_max", [])
            )
            windspeed_10m_max = daily_data.get(
                "windspeed_10m_max", []
            ) or daily_data.get("wind_speed_max", [])
            winddirection = daily_data.get(
                "winddirection_10m_dominant", []
            ) or daily_data.get("wind_direction_10m_dominant", [])

            # Hiányzó temp_mean számítása ha nincs
            if not temp_mean and temp_max and temp_min:
                logger.debug("Temp_mean számítása temp_max és temp_min alapján...")
                temp_mean = [
                    round((t_max + t_min) / 2, 1)
                    if t_max is not None and t_min is not None
                    else None
                    for t_max, t_min in zip(temp_max, temp_min)
                ]

            max_length = len(dates)

            # === DATAFRAME ÖSSZEÁLLÍTÁSA ===
            df_data = {
                "date": dates,
                "temp_max": DataFrameExtractor._ensure_length(temp_max, max_length),
                "temp_min": DataFrameExtractor._ensure_length(temp_min, max_length),
                "precipitation": DataFrameExtractor._ensure_length(precip, max_length),
            }

            # Temp_mean hozzáadása ha van
            if temp_mean:
                df_data["temp_mean"] = DataFrameExtractor._ensure_length(
                    temp_mean, max_length
                )

            # === 🔥 KRITIKUS JAVÍTÁS: SZÉLLÖKÉS ÉS SZÉLSEBESSÉG KÜLÖN ===
            # 🌪️ VALIDÁCIÓ: Csak érvényes numerikus adatok használata
            has_valid_wind_gusts = (
                wind_gusts_10m_max
                and DataFrameExtractor._has_valid_data(wind_gusts_10m_max)
            )

            # 🔥 KRITIKUS JAVÍTÁS: Ha van wind_gusts_10m_max adat, de a validáció nem talál érvényes értékeket,
            # akkor is használjuk az adatokat, de figyelmeztetünk
            if wind_gusts_10m_max and len(wind_gusts_10m_max) > 0:
                # 🌪️ ELSŐDLEGES: wind_gusts_10m_max (VALÓDI széllökések)
                df_data["wind_gusts_max"] = DataFrameExtractor._ensure_length(
                    wind_gusts_10m_max, max_length
                )
                df_data["wind_data_source"] = ["wind_gusts_10m_max"] * max_length

                if has_valid_wind_gusts:
                    logger.info(
                        f"✅ SZÉLLÖKÉS: wind_gusts_10m_max ({len(wind_gusts_10m_max)} values)"
                    )
                else:
                    # ⚠️ FIGYELMEZTETÉS: Adatok vannak, de nem érvényes numerikus formátum
                    logger.warning(
                        f"⚠️ SZÉLLÖKÉS: wind_gusts_10m_max adat van ({len(wind_gusts_10m_max)} values), de nem érvényes numerikus formátum"
                    )
                    logger.warning(
                        "⚠️ Az adatok mégis felhasználásra kerülnek (fallback mód)"
                    )

            else:
                # ❌ NINCS SZÉLLÖKÉS ADAT
                df_data["wind_gusts_max"] = [None] * max_length
                df_data["wind_data_source"] = ["no_data"] * max_length
                logger.warning("❌ Nincs széllökés adat")

            # 💨 SZÉLSEBESSÉG KÜLÖN OSZLOP (QuickOverviewTab számára)
            has_valid_windspeed = (
                windspeed_10m_max
                and DataFrameExtractor._has_valid_data(windspeed_10m_max)
            )
            has_valid_wind_gusts_for_fallback = (
                wind_gusts_10m_max
                and DataFrameExtractor._has_valid_data(wind_gusts_10m_max)
            )

            if has_valid_windspeed:
                df_data["windspeed"] = DataFrameExtractor._ensure_length(
                    windspeed_10m_max, max_length
                )
                logger.debug(
                    f"✅ SZÉLSEBESSÉG: windspeed_10m_max ({len(windspeed_10m_max)} values)"
                )
            elif has_valid_wind_gusts_for_fallback:
                # Fallback: széllökés használata szélsebességként
                df_data["windspeed"] = df_data["wind_gusts_max"]
                logger.debug(
                    f"⚠️ SZÉLSEBESSÉG fallback to széllökés ({len(wind_gusts_10m_max)} values)"
                )
            else:
                df_data["windspeed"] = [None] * max_length
                logger.debug("❌ SZÉLSEBESSÉG: NO DATA!")

            # 🧭 SZÉLIRÁNY hozzáadása ha van
            if winddirection:
                df_data["winddirection"] = DataFrameExtractor._ensure_length(
                    winddirection, max_length
                )
                logger.debug(
                    f"🧭 SZÉLIRÁNY: winddirection_10m_dominant ({len(winddirection)} values)"
                )

            # DataFrame létrehozása
            df = pd.DataFrame(df_data)

            # 🔥 KRITIKUS JAVÍTÁS: Típuskonverzió a szél oszlopokhoz
            # Ez biztosítja, hogy a windspeed, wind_gusts_max oszlopok numerikus típusúak legyenek
            # és ne tartalmazzanak stringeket, ami '>' összehasonlítási hibát okozna
            numeric_columns = ["windspeed", "wind_gusts_max", "winddirection"]
            for col in numeric_columns:
                if col in df.columns:
                    # pd.to_numeric() konvertálja az értékeket, a nem numerikusokat NaN-nak tekinti
                    df[col] = pd.to_numeric(df[col], errors="coerce")
                    logger.debug(f"✅ Típuskonverzió: {col} → numerikus")

            logger.info(f"✅ DataFrame extracted successfully: {df.shape} (rows, cols)")
            logger.debug(f"Columns: {list(df.columns)}")

            # 🔍 DEBUG: Széladatok tartománya
            if "wind_gusts_max" in df.columns:
                wind_data = df["wind_gusts_max"].dropna()
                if len(wind_data) > 0:
                    source = (
                        df["wind_data_source"].iloc[0]
                        if "wind_data_source" in df.columns
                        else "unknown"
                    )
                    logger.info(f"🌪️ Wind stats - Source: {source}")
                    logger.info(
                        f"🌪️ Wind range: {wind_data.min():.1f} → {wind_data.max():.1f} km/h"
                    )

            return df

        except Exception as e:
            logger.error(f"❌ DataFrame extract hiba: {e}")
            import traceback

            traceback.print_exc()
            return pd.DataFrame()

    @staticmethod
    def _has_valid_data(data_list: list) -> bool:
        """
        Check if list contains valid numeric data (not just None values).

        🔥 KRITIKUS JAVÍTÁS: Bővített validáció, hogy kezelje a különböző adatformátumokat

        Args:
            data_list: List to check

        Returns:
            True if list contains valid numeric data
        """
        if not data_list:
            print("🔍 DEBUG: _has_valid_data - EMPTY list")
            return False

        # 🔥 KRITIKUS JAVÍTÁS: Bővített validáció, hogy kezelje a különböző számformátumokat
        valid_count = 0
        invalid_samples = []

        # 🔥 KRITIKUS JAVÍTÁS: Ellenőrizzük az összes elemet, ne csak az első 10-et
        # Ez megakadályozza, hogy az érvényes adatok elvesznek, ha csak a kezdeti elemek érvénytelenek
        for i, x in enumerate(data_list):
            if x is None:
                continue

            # 🔥 KRITIKUS JAVÍTÁS: Kiterjesztett típusellenőrzés
            # Kezeljük a float, int, és string számokat is
            is_valid = False

            if isinstance(x, (int, float)):
                is_valid = True
            elif isinstance(x, str):
                try:
                    # Próbáljuk konvertálni stringet számmá
                    float(x)
                    is_valid = True
                except (ValueError, TypeError):
                    is_valid = False
                    if i < 10:  # Only collect first 10 invalid samples for debugging
                        invalid_samples.append(f"'{x}' (string, nem konvertálható)")
            else:
                if i < 10:  # Only collect first 10 invalid samples for debugging
                    invalid_samples.append(f"{type(x).__name__}: {x}")

            if is_valid:
                valid_count += 1

        # 🔥 KRITIKUS JAVÍTÁS: Ha van legalább 1 érvényes érték, akkor válaszunk True
        # Ez megakadályozza, hogy az összes adat elveszzen, ha csak néhány érték érvénytelen
        return valid_count > 0

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
                    "columns": 0,
                }

            # Alapvető statisztikák
            stats = {
                "valid": True,
                "rows": len(df),
                "columns": len(df.columns),
                "date_range": None,
                "missing_data": {},
                "wind_source": "unknown",
            }

            # Dátum tartomány
            if "date" in df.columns and not df["date"].empty:
                stats["date_range"] = f"{df['date'].iloc[0]} - {df['date'].iloc[-1]}"

            # Hiányzó adatok számlálása
            for col in df.columns:
                missing_count = df[col].isna().sum()
                if missing_count > 0:
                    stats["missing_data"][col] = missing_count

            # Szél adatforrás detektálása
            if "wind_data_source" in df.columns and not df["wind_data_source"].empty:
                stats["wind_source"] = df["wind_data_source"].iloc[0]

            logger.debug(f"DataFrame validation: {stats}")
            return stats

        except Exception as e:
            logger.error(f"DataFrame validation hiba: {e}")
            return {"valid": False, "error": str(e), "rows": 0, "columns": 0}
