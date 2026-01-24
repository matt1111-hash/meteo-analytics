"""Wind monthly statistics calculations."""

from __future__ import annotations

import logging

import pandas as pd

from src.domain.analytics.wind_models import MONTHS_HU, WindyDayStats

logger = logging.getLogger(__name__)


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

        df = windy_days_data.copy()

        # Date konverzió ha szükséges
        if not pd.api.types.is_datetime64_any_dtype(df["date"]):
            df["date"] = pd.to_datetime(df["date"])

        # Év és hónap oszlopok
        df["year"] = df["date"].dt.year
        df["month"] = df["date"].dt.month

        # 🔥 KRITIKUS JAVÍTÁS: Teljes időszak meghatározása
        start_date = df["date"].min()
        end_date = df["date"].max()

        logger.info(f"📅 Analízis időszak: {start_date.date()} - {end_date.date()}")

        # 🗓️ TELJES HÓNAPOS LISTA GENERÁLÁSA
        all_months = []
        current = start_date.replace(day=1)

        while current <= end_date:
            all_months.append((current.year, current.month))

            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)

        logger.info(f"🗓️ TELJES HÓNAPOS LISTA: {len(all_months)} hónap generálva")

        # Valós adatok hónap szerinti csoportosítása
        actual_monthly_data = {}
        for (year, month), group in df.groupby(["year", "month"]):
            actual_monthly_data[(year, month)] = group

        monthly_stats = []

        # 🔥 KRITIKUS: MINDEN hónapra statisztika (hiányzók 0-val)
        for year, month in all_months:
            try:
                if (year, month) in actual_monthly_data:
                    group = actual_monthly_data[(year, month)]

                    total_days = len(group)
                    windy_days_count = group["is_windy"].sum()
                    windy_percentage = (
                        (windy_days_count / total_days) * 100 if total_days > 0 else 0.0
                    )

                    max_wind_speed = group["max_wind_speed_kmh"].max()
                    avg_wind_speed = group["max_wind_speed_kmh"].mean()

                    windy_days_list = group[group["is_windy"]]["date"].dt.date.tolist()

                else:
                    total_days = 0
                    windy_days_count = 0
                    windy_percentage = 0.0
                    max_wind_speed = 0.0
                    avg_wind_speed = 0.0
                    windy_days_list = []

                    logger.debug(f"🔍 HIÁNYZÓ HÓNAP KITÖLTVE: {year}/{month}")

                month_name = MONTHS_HU[month - 1] if 1 <= month <= 12 else f"Hónap {month}"

                stat = WindyDayStats(
                    year=year,
                    month=month,
                    month_name=month_name,
                    windy_days_count=windy_days_count,
                    total_days=total_days,
                    windy_percentage=windy_percentage,
                    max_wind_speed=max_wind_speed,
                    avg_wind_speed=avg_wind_speed,
                    windy_days_list=windy_days_list,
                )

                monthly_stats.append(stat)

                if windy_days_count > 0:
                    logger.debug(
                        f"📊 {year} {month_name}: {windy_days_count} szeles nap "
                        f"({windy_percentage:.1f}%)"
                    )

            except Exception as e:
                logger.error(f"❌ Hiba a {year}/{month} hónap feldolgozásában: {e}")
                continue

        logger.info(
            f"✅ Számított havi statisztikák: {len(monthly_stats)} hónap (TELJES LISTA)"
        )

        monthly_stats.sort(key=lambda x: (x.year, x.month))

        return monthly_stats

    except Exception as e:
        logger.error(f"❌ Hiba a havi statisztikák számításában: {e}")
        import traceback

        traceback.print_exc()
        return []
