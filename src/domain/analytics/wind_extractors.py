"""Wind analysis extractors and classification helpers."""

from __future__ import annotations

import logging

import pandas as pd

from src.domain.analytics.wind_models import WINDY_DAY_THRESHOLD_KMH

logger = logging.getLogger(__name__)


def extract_daily_wind_data(weather_data: pd.DataFrame) -> pd.DataFrame:
    """
    🔥 KRITIKUS JAVÍTÁS: Napi széllökési adatok kinyerése HELYES OSZLOPPAL.

    PRIORITÁS: wind_gusts_max → wind_speed (fallback)

    Args:
        weather_data: Weather DataFrame időjárási adatokkal

    Returns:
        DataFrame napi max szélsebességekkel (date, max_wind_speed_kmh)
    """
    try:
        # 🎯 KRITIKUS OSZLOP VÁLASZTÁS: széllökések prioritással!
        wind_column = None

        # 🔥 KRITIKUS JAVÍTÁS: HELYES OSZLOPNEVEK KERESÉSE
        # 1. Elsődleges: széllökések (utils.py wind_gusts_max oszlopa)
        if "wind_gusts_max" in weather_data.columns:
            wind_column = "wind_gusts_max"
            logger.info("🌪️ HELYES OSZLOP: wind_gusts_max (széllökések) használva")

        # 2. Másodlagos: átlagos szélsebesség (wind_speed)
        elif "wind_speed" in weather_data.columns:
            wind_column = "wind_speed"
            logger.warning(
                "⚠️ FALLBACK OSZLOP: wind_speed (átlagos) használva - lehet alulbecslés!"
            )

        # 3. Harmadlagos: régi névkonvenció
        elif "windspeed_10m_max" in weather_data.columns:
            wind_column = "windspeed_10m_max"
            logger.warning("⚠️ LEGACY OSZLOP: windspeed_10m_max használva")

        else:
            logger.error("❌ NINCS SZÉLSEBESSÉG OSZLOP a weather_data-ban!")
            available_cols = list(weather_data.columns)
            logger.error(f"❌ Elérhető oszlopok: {available_cols}")
            return pd.DataFrame(columns=["date", "max_wind_speed_kmh"])

        # Biztosítsuk hogy van date oszlop
        if "date" not in weather_data.columns:
            logger.error("❌ NINCS DATE OSZLOP a weather_data-ban")
            return pd.DataFrame(columns=["date", "max_wind_speed_kmh"])

        # Másolat készítése
        df = weather_data.copy()

        # Date konverzió ha szükséges
        if not pd.api.types.is_datetime64_any_dtype(df["date"]):
            df["date"] = pd.to_datetime(df["date"])

        # Csak a szükséges oszlopok
        wind_data = df[["date", wind_column]].copy()
        wind_data = wind_data.rename(columns={wind_column: "wind_speed"})

        # 🔥 NONE-SAFETY: Invalid értékek tisztítása
        original_count = len(wind_data)
        wind_data = wind_data.dropna(subset=["wind_speed"])
        wind_data = wind_data[wind_data["wind_speed"] >= 0]  # Negatív értékek kiszűrése
        cleaned_count = len(wind_data)

        if original_count > cleaned_count:
            logger.warning(
                "⚠️ ADATTISZTÍTÁS: "
                f"{original_count - cleaned_count} invalid szélsebesség adat eltávolítva"
            )

        # Napi maximum számítás
        daily_wind = (
            wind_data.groupby(wind_data["date"].dt.date)
            .agg({"wind_speed": "max"})
            .reset_index()
        )

        daily_wind.columns = ["date", "max_wind_speed_kmh"]

        # NaN értékek kezelése
        daily_wind["max_wind_speed_kmh"] = daily_wind["max_wind_speed_kmh"].fillna(0.0)

        # Statisztikák
        valid_days = len(daily_wind[daily_wind["max_wind_speed_kmh"] > 0])
        max_speed = (
            daily_wind["max_wind_speed_kmh"].max() if not daily_wind.empty else 0
        )

        logger.info(f"✅ Feldolgozott {len(daily_wind)} napi szélsebesség adat")
        logger.info(f"📊 Érvényes napok: {valid_days}/{len(daily_wind)}")
        logger.info(
            f"🌪️ Maximum szélsebesség: {max_speed:.1f} km/h ({wind_column} alapján)"
        )

        return daily_wind

    except Exception as e:
        logger.error(f"❌ Hiba a szélsebességi adatok kinyerésében: {e}")
        import traceback

        traceback.print_exc()
        return pd.DataFrame(columns=["date", "max_wind_speed_kmh"])


def identify_windy_days(
    daily_wind_data: pd.DataFrame, threshold_kmh: float = WINDY_DAY_THRESHOLD_KMH
) -> pd.DataFrame:
    """
    Szeles napok azonosítása küszöbérték alapján.

    Args:
        daily_wind_data: Napi szélsebességi adatok
        threshold_kmh: Küszöbérték km/h-ban

    Returns:
        DataFrame szeles napok jelölésével (date, max_wind_speed_kmh, is_windy)
    """
    try:
        if daily_wind_data.empty:
            logger.warning("⚠️ Üres daily_wind_data")
            return pd.DataFrame(columns=["date", "max_wind_speed_kmh", "is_windy"])

        df = daily_wind_data.copy()

        # Szeles nap jelölés
        df["is_windy"] = df["max_wind_speed_kmh"] > threshold_kmh

        windy_count = df["is_windy"].sum()
        total_count = len(df)

        logger.info(
            "🌪️ Azonosított szeles napok: "
            f"{windy_count}/{total_count} "
            f"({windy_count / total_count * 100:.1f}%) threshold: {threshold_kmh} km/h"
        )

        # Részletes statisztikák
        if windy_count > 0:
            windy_speeds = df[df["is_windy"]]["max_wind_speed_kmh"]
            logger.info(
                "🌪️ Szeles napok szélsebesség tartomány: "
                f"{windy_speeds.min():.1f} - {windy_speeds.max():.1f} km/h"
            )

        return df

    except Exception as e:
        logger.error(f"❌ Hiba a szeles napok azonosításában: {e}")
        return pd.DataFrame(columns=["date", "max_wind_speed_kmh", "is_windy"])
