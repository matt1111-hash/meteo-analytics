"""Wind monthly statistics calculations."""

from __future__ import annotations

import logging

import pandas as pd
from src.domain.analytics.wind_models import MONTHS_HU, WindyDayStats

logger = logging.getLogger(__name__)


def _resolve_month_name(month: int) -> str:
    """Resolve month name safely."""
    return MONTHS_HU[month - 1] if 1 <= month <= 12 else f"Hónap {month}"  # noqa: PLR2004


def _prepare_monthly_stats_frame(windy_days_data: pd.DataFrame) -> pd.DataFrame:
    """Normalize dates and add year/month columns."""
    df = windy_days_data.copy()
    if not pd.api.types.is_datetime64_any_dtype(df["date"]):
        df["date"] = pd.to_datetime(df["date"])
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    return df


def _build_actual_monthly_data(
    df: pd.DataFrame,
) -> dict[tuple[int, int], pd.DataFrame]:
    """Build grouped monthly data lookup."""
    return {(year, month): group for (year, month), group in df.groupby(["year", "month"])}


def _collect_monthly_stats(
    all_months: list[tuple[int, int]],
    actual_monthly_data: dict[tuple[int, int], pd.DataFrame],
) -> list[WindyDayStats]:
    """Collect monthly stat objects for all months in range."""
    monthly_stats: list[WindyDayStats] = []
    for year, month in all_months:
        try:
            monthly_stats.append(
                _build_monthly_stat(year, month, actual_monthly_data.get((year, month)))
            )
        except Exception as error:
            logger.error("❌ Hiba a %s/%s hónap feldolgozásában: %s", year, month, error)
    return monthly_stats


def _generate_month_sequence(
    start_date: pd.Timestamp, end_date: pd.Timestamp
) -> list[tuple[int, int]]:
    """Generate inclusive month sequence between two dates."""
    all_months: list[tuple[int, int]] = []
    current = start_date.replace(day=1)
    while current <= end_date:
        all_months.append((current.year, current.month))
        if current.month == 12:  # noqa: PLR2004
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)
    return all_months


def _build_monthly_stat(
    year: int,
    month: int,
    group: pd.DataFrame | None,
) -> WindyDayStats:
    """Build one monthly windy-stat record."""
    if group is None:
        logger.debug("🔍 HIÁNYZÓ HÓNAP KITÖLTVE: %s/%s", year, month)
        return WindyDayStats(
            year=year,
            month=month,
            month_name=_resolve_month_name(month),
            windy_days_count=0,
            total_days=0,
            windy_percentage=0.0,
            max_wind_speed=0.0,
            avg_wind_speed=0.0,
            windy_days_list=[],
        )

    total_days = len(group)
    windy_days_count = group["is_windy"].sum()
    windy_percentage = (windy_days_count / total_days) * 100 if total_days > 0 else 0.0
    month_name = _resolve_month_name(month)
    stat = WindyDayStats(
        year=year,
        month=month,
        month_name=month_name,
        windy_days_count=windy_days_count,
        total_days=total_days,
        windy_percentage=windy_percentage,
        max_wind_speed=group["max_wind_speed_kmh"].max(),
        avg_wind_speed=group["max_wind_speed_kmh"].mean(),
        windy_days_list=group[group["is_windy"]]["date"].dt.date.tolist(),
    )
    if windy_days_count > 0:
        logger.debug(
            "📊 %s %s: %s szeles nap (%.1f%%)",
            year,
            month_name,
            windy_days_count,
            windy_percentage,
        )
    return stat


def calculate_monthly_windy_stats(windy_days_data: pd.DataFrame) -> list[WindyDayStats]:
    """
    🔥 JAVÍTÁS #2: Havi szeles nap statisztikák TELJES HÓNAPOS LISTÁVAL.

    VÁLTOZÁS: Hiányzó hónapok automatikusan kitöltve 0-val!

    Args:
        windy_days_data: DataFrame szeles napok jelölésével

    Returns:
        Lista WindyDayStats objektumokkal (MINDEN hónap garantált!)
    """
    try:
        if windy_days_data.empty:
            logger.warning("⚠️ Üres windy_days_data")
            return []

        df = _prepare_monthly_stats_frame(windy_days_data)
        start_date = df["date"].min()
        end_date = df["date"].max()

        logger.info(f"📅 Analízis időszak: {start_date.date()} - {end_date.date()}")
        all_months = _generate_month_sequence(start_date, end_date)
        logger.info(f"🗓️ TELJES HÓNAPOS LISTA: {len(all_months)} hónap generálva")
        actual_monthly_data = _build_actual_monthly_data(df)
        monthly_stats = _collect_monthly_stats(all_months, actual_monthly_data)

        logger.info(f"✅ Számított havi statisztikák: {len(monthly_stats)} hónap (TELJES LISTA)")

        monthly_stats.sort(key=lambda x: (x.year, x.month))

        return monthly_stats

    except Exception as e:
        logger.error(f"❌ Hiba a havi statisztikák számításában: {e}")
        return []
