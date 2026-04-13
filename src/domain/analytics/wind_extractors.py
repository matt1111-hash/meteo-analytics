"""Wind analysis extractors and classification helpers."""

from __future__ import annotations

import logging

import pandas as pd
from src.domain.analytics.wind_models import WINDY_DAY_THRESHOLD_KMH

logger = logging.getLogger(__name__)


def _empty_wind_dataframe() -> pd.DataFrame:
    """Return empty normalized wind dataframe."""
    return pd.DataFrame(columns=["date", "max_wind_speed_kmh"])


def _select_wind_column(weather_data: pd.DataFrame) -> str | None:
    """Resolve preferred wind column from the incoming weather data."""
    if "wind_gusts_max" in weather_data.columns:
        logger.info("🌪️ HELYES OSZLOP: wind_gusts_max (széllökések) használva")
        return "wind_gusts_max"
    if "wind_speed" in weather_data.columns:
        logger.warning("⚠️ FALLBACK OSZLOP: wind_speed (átlagos) használva - lehet alulbecslés!")
        return "wind_speed"
    if "windspeed_10m_max" in weather_data.columns:
        logger.warning("⚠️ LEGACY OSZLOP: windspeed_10m_max használva")
        return "windspeed_10m_max"
    logger.error("❌ NINCS SZÉLSEBESSÉG OSZLOP a weather_data-ban!")
    logger.error("❌ Elérhető oszlopok: %s", list(weather_data.columns))
    return None


def _prepare_wind_source_frame(weather_data: pd.DataFrame, wind_column: str) -> pd.DataFrame:
    """Prepare normalized wind source frame."""
    df = weather_data.copy()
    if not pd.api.types.is_datetime64_any_dtype(df["date"]):
        df["date"] = pd.to_datetime(df["date"])
    wind_data = df[["date", wind_column]].copy()
    return wind_data.rename(columns={wind_column: "wind_speed"})


def _clean_wind_data(wind_data: pd.DataFrame) -> pd.DataFrame:
    """Drop invalid wind values and log cleanup count."""
    original_count = len(wind_data)
    cleaned = wind_data.dropna(subset=["wind_speed"])
    cleaned = cleaned[cleaned["wind_speed"] >= 0]
    cleaned_count = len(cleaned)
    if original_count > cleaned_count:
        logger.warning(
            "⚠️ ADATTISZTÍTÁS: %s invalid szélsebesség adat eltávolítva",
            original_count - cleaned_count,
        )
    return cleaned


def _aggregate_daily_wind(wind_data: pd.DataFrame) -> pd.DataFrame:
    """Aggregate max daily wind speed values."""
    daily_wind = (
        wind_data.groupby(wind_data["date"].dt.date).agg({"wind_speed": "max"}).reset_index()
    )
    daily_wind.columns = ["date", "max_wind_speed_kmh"]
    daily_wind["max_wind_speed_kmh"] = daily_wind["max_wind_speed_kmh"].fillna(0.0)
    return daily_wind


def _log_daily_wind_stats(daily_wind: pd.DataFrame, wind_column: str) -> None:
    """Log summary statistics for daily wind data."""
    valid_days = len(daily_wind[daily_wind["max_wind_speed_kmh"] > 0])
    max_speed = daily_wind["max_wind_speed_kmh"].max() if not daily_wind.empty else 0
    logger.info("✅ Feldolgozott %s napi szélsebesség adat", len(daily_wind))
    logger.info("📊 Érvényes napok: %s/%s", valid_days, len(daily_wind))
    logger.info(
        "🌪️ Maximum szélsebesség: %.1f km/h (%s alapján)",
        max_speed,
        wind_column,
    )


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
        wind_column = _select_wind_column(weather_data)
        if wind_column is None:
            return _empty_wind_dataframe()
        if "date" not in weather_data.columns:
            logger.error("❌ NINCS DATE OSZLOP a weather_data-ban")
            return _empty_wind_dataframe()

        wind_data = _prepare_wind_source_frame(weather_data, wind_column)
        daily_wind = _aggregate_daily_wind(_clean_wind_data(wind_data))
        _log_daily_wind_stats(daily_wind, wind_column)
        return daily_wind

    except Exception as e:
        logger.error(f"❌ Hiba a szélsebességi adatok kinyerésében: {e}")
        import traceback

        traceback.print_exc()
        return _empty_wind_dataframe()


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
