#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Universal Weather Research Platform - Analytics Statistics Module.
Statisztika számító és megjelenítő függvények.

📊 STATISZTIKA SZÁMÍTÁSOK:
✅ Hőmérséklet statisztikák
✅ Csapadék statisztikák
✅ Szél statisztikák (BEAUFORT)
✅ Időszak statisztikák
✅ Rekord számítások
"""

import logging
from typing import Any, Dict, List, Optional

from .analytics_helpers import safe_avg, safe_count, safe_max, safe_min, safe_sum

logger = logging.getLogger(__name__)


class AnalyticsStatistics:
    """📊 Analytics statisztika számító osztály"""

    @staticmethod
    def calculate_statistics_data(
        data: Dict[str, Any], total_days: int
    ) -> Dict[str, Any]:
        """📊 STATISZTIKAI ADATOK KISZÁMÍTÁSA - KÁRTYÁS RENDSZERHEZ"""
        try:
            daily_data = data.get("daily", {})
            dates = daily_data.get("time", [])

            if not daily_data or not dates:
                return {}

            stats: Dict[str, Any] = {}
            stats.update(AnalyticsStatistics._compute_temperature_stats(daily_data))
            stats.update(
                AnalyticsStatistics._compute_precipitation_stats(daily_data, dates)
            )
            stats.update(AnalyticsStatistics._compute_wind_stats(daily_data))
            stats.update(AnalyticsStatistics._compute_period_stats(dates, total_days))

            return stats

        except Exception as e:
            logger.error(f"Statisztikai adatok számítási hiba: {e}")
            return {}

    @staticmethod
    def _compute_temperature_stats(daily_data: Dict[str, List[Any]]) -> Dict[str, Any]:
        stats: Dict[str, Any] = {}
        temp_mean_list = daily_data.get("temperature_2m_mean", [])
        temp_max_list = daily_data.get("temperature_2m_max", [])
        temp_min_list = daily_data.get("temperature_2m_min", [])

        if not temp_mean_list:
            return stats

        stats["temp_avg"] = safe_avg(temp_mean_list)
        stats["temp_min"] = safe_min(temp_min_list) if temp_min_list else None
        stats["temp_max"] = safe_max(temp_max_list) if temp_max_list else None

        stats["freezing_days"] = (
            safe_count(temp_min_list, lambda x: x < 0) if temp_min_list else 0
        )
        stats["hot_days"] = (
            safe_count(temp_max_list, lambda x: x > 30) if temp_max_list else 0
        )

        if temp_max_list and temp_min_list:
            daily_ranges = []
            for index in range(min(len(temp_max_list), len(temp_min_list))):
                max_val = temp_max_list[index]
                min_val = temp_min_list[index]
                if max_val is not None and min_val is not None:
                    daily_ranges.append(max_val - min_val)
            stats["temp_range_avg"] = safe_avg(daily_ranges) if daily_ranges else None

        return stats

    @staticmethod
    def _compute_precipitation_stats(
        daily_data: Dict[str, List[Any]], dates: List[str]
    ) -> Dict[str, Any]:
        stats: Dict[str, Any] = {}
        precip_list = daily_data.get("precipitation_sum", [])
        if not precip_list:
            return stats

        stats["precip_avg"] = safe_avg(precip_list)
        stats["precip_total"] = safe_sum(precip_list)
        stats["dry_days"] = safe_count(precip_list, lambda x: x <= 0.1)
        stats["rainy_days"] = len(precip_list) - stats["dry_days"]
        stats["dry_percentage"] = (stats["dry_days"] / len(precip_list)) * 100
        stats["rainy_percentage"] = (stats["rainy_days"] / len(precip_list)) * 100

        years = len(set(date[:4] for date in dates))
        stats["annual_precip"] = (
            stats["precip_total"] / years if years > 0 else stats["precip_total"]
        )

        dry_streak = AnalyticsStatistics._find_longest_dry_streak(precip_list, dates)
        stats["longest_dry_streak"] = dry_streak["days"] if dry_streak else 0
        return stats

    @staticmethod
    def _compute_wind_stats(daily_data: Dict[str, List[Any]]) -> Dict[str, Any]:
        stats: Dict[str, Any] = {}
        wind_list = daily_data.get("windspeed_10m_max", [])
        windgust_list = daily_data.get("wind_gusts_max", [])

        if wind_list:
            stats["wind_avg"] = safe_avg(wind_list)
            stats["wind_max"] = safe_max(wind_list)
            stats["wind_calm"] = safe_count(wind_list, lambda x: x <= 1)
            stats["wind_light"] = safe_count(wind_list, lambda x: 1 < x <= 11)
            stats["wind_moderate"] = safe_count(wind_list, lambda x: 11 < x <= 29)
            stats["wind_strong"] = safe_count(wind_list, lambda x: x > 29)

        if windgust_list:
            stats["windgust_max"] = safe_max(windgust_list)
        return stats

    @staticmethod
    def _compute_period_stats(dates: List[str], total_days: int) -> Dict[str, Any]:
        stats: Dict[str, Any] = {}
        stats["start_date"] = dates[0][:10] if dates else "N/A"
        stats["end_date"] = dates[-1][:10] if dates else "N/A"
        stats["total_days"] = total_days
        stats["bin_size"] = max(1, total_days // 365)
        stats["years"] = len(set(date[:4] for date in dates)) if dates else 0
        return stats

    @staticmethod
    def _find_longest_dry_streak(
        precip_list: List[float], dates: List[str]
    ) -> Optional[Dict[str, Any]]:
        """Leghosszabb száraz időszak keresése"""
        try:
            if not precip_list or not dates:
                return None

            max_streak = 0
            current_streak = 0
            max_start_idx = 0
            max_end_idx = 0
            current_start_idx = 0

            for i, precip in enumerate(precip_list):
                if precip is not None and precip <= 0.1:
                    if current_streak == 0:
                        current_start_idx = i
                    current_streak += 1
                else:
                    if current_streak > max_streak:
                        max_streak = current_streak
                        max_start_idx = current_start_idx
                        max_end_idx = i - 1
                    current_streak = 0

            # Utolsó streak ellenőrzése
            if current_streak > max_streak:
                max_streak = current_streak
                max_start_idx = current_start_idx
                max_end_idx = len(precip_list) - 1

            if max_streak >= 3:
                return {
                    "days": max_streak,
                    "start": dates[max_start_idx],
                    "end": dates[max_end_idx],
                }

            return None

        except Exception as e:
            logger.error(f"Száraz időszak keresési hiba: {e}")
            return None

    @staticmethod
    def calculate_records(data: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
        """🏆 5 rekord kategória számítása - MINDIG NAPI SZINTEN (MAX SZÉLLÖKÉSEKKEL)"""
        try:
            daily_data = data.get("daily", {})

            if not daily_data:
                return {}

            dates = daily_data.get("time", [])
            if not dates:
                return {}

            records = {}

            # 🔥 1. LEGMELEGEBB NAP
            temp_max_list = daily_data.get("temperature_2m_max", [])
            if temp_max_list and len(temp_max_list) == len(dates):
                max_temp = safe_max(temp_max_list)
                if max_temp is not None:
                    max_idx = temp_max_list.index(max_temp)
                    records["hottest"] = {
                        "value": f"{max_temp:.1f}°C",
                        "date": dates[max_idx][:10],
                    }

            # 🧊 2. LEGHIDEGEBB NAP
            temp_min_list = daily_data.get("temperature_2m_min", [])
            if temp_min_list and len(temp_min_list) == len(dates):
                min_temp = safe_min(temp_min_list)
                if min_temp is not None:
                    min_idx = temp_min_list.index(min_temp)
                    records["coldest"] = {
                        "value": f"{min_temp:.1f}°C",
                        "date": dates[min_idx][:10],
                    }

            # 🌧️ 3. LEGCSAPADÉKOSABB NAP
            precip_list = daily_data.get("precipitation_sum", [])
            if precip_list and len(precip_list) == len(dates):
                max_precip = safe_max(precip_list)
                if max_precip is not None and max_precip > 0:
                    max_precip_idx = precip_list.index(max_precip)
                    records["wettest"] = {
                        "value": f"{max_precip:.1f}mm",
                        "date": dates[max_precip_idx][:10],
                    }

            # 🏜️ 4. LEGSZÁRAZABB IDŐSZAK
            if precip_list and len(precip_list) == len(dates):
                dry_streak = AnalyticsStatistics._find_longest_dry_streak(
                    precip_list, dates
                )
                if dry_streak:
                    records["driest"] = {
                        "value": f"{dry_streak['days']} nap",
                        "date": f"{dry_streak['start'][:5]}-{dry_streak['end'][:5]}",  # Rövidebb
                    }

            # 💨 5. LEGSZELESEBB NAP (VALÓS API NEVEK)
            # Előnyben részesítjük a széllökéseket (wind_gusts_max), ha elérhető
            wind_data = daily_data.get("wind_gusts_max", []) or daily_data.get(
                "windspeed_10m_max", []
            )
            if wind_data and len(wind_data) == len(dates):
                max_wind = safe_max(wind_data)
                if max_wind is not None:
                    max_wind_idx = wind_data.index(max_wind)
                    records["windiest"] = {
                        "value": f"{max_wind:.1f}km/h",
                        "date": dates[max_wind_idx][:10],
                    }

            logger.info(
                f"Napi rekordok számítva: {len(records)} kategória (max széllökés prioritással)"
            )
            return records

        except Exception as e:
            logger.error(f"Rekord számítási hiba: {e}", exc_info=True)


__all__ = [
    "AnalyticsStatistics",
]
