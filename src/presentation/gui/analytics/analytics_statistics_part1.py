# ruff: noqa: F403, F405,noqa: I001
# mypy: ignore-errors
"""Mixin part 1 for AnalyticsStatistics."""

from __future__ import annotations

from .analytics_statistics_support import *


def _build_daily_ranges(temp_max_list: List[Any], temp_min_list: List[Any]) -> list[Any]:
    """Build valid daily temperature ranges."""
    daily_ranges: list[Any] = []
    for index in range(min(len(temp_max_list), len(temp_min_list))):
        max_val = temp_max_list[index]
        min_val = temp_min_list[index]
        if max_val is not None and min_val is not None:
            daily_ranges.append(max_val - min_val)
    return daily_ranges


def _build_precipitation_percentages(precip_list: List[Any], dry_days: int) -> dict[str, float]:
    """Build precipitation day ratios."""
    rainy_days = len(precip_list) - dry_days
    return {
        "rainy_days": rainy_days,
        "dry_percentage": (dry_days / len(precip_list)) * 100,
        "rainy_percentage": (rainy_days / len(precip_list)) * 100,
    }


def _update_streak_state(
    precip: float | None,
    index: int,
    current_streak: int,
    current_start_idx: int,
    max_streak: int,
    max_start_idx: int,
    max_end_idx: int,
) -> tuple[int, int, int, int, int]:
    """Update dry streak counters for one precipitation value."""
    if precip is not None and precip <= 0.1:  # noqa: PLR2004
        if current_streak == 0:
            current_start_idx = index
        return (
            current_streak + 1,
            current_start_idx,
            max_streak,
            max_start_idx,
            max_end_idx,
        )
    if current_streak > max_streak:
        return 0, current_start_idx, current_streak, current_start_idx, index - 1
    return 0, current_start_idx, max_streak, max_start_idx, max_end_idx


class AnalyticsStatisticsPart1Mixin:  # noqa: D101
    @staticmethod
    def calculate_statistics_data(data: Dict[str, Any], total_days: int) -> Dict[str, Any]:
        """📊 STATISZTIKAI ADATOK KISZÁMÍTÁSA - KÁRTYÁS RENDSZERHEZ"""
        try:
            daily_data = data.get("daily", {})
            dates = daily_data.get("time", [])

            if not daily_data or not dates:
                return {}

            stats: Dict[str, Any] = {}
            stats.update(AnalyticsStatistics._compute_temperature_stats(daily_data))
            stats.update(AnalyticsStatistics._compute_precipitation_stats(daily_data, dates))
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

        stats["freezing_days"] = safe_count(temp_min_list, lambda x: x < 0) if temp_min_list else 0
        stats["hot_days"] = (
            safe_count(temp_max_list, lambda x: x > 30) if temp_max_list else 0  # noqa: PLR2004
        )

        if temp_max_list and temp_min_list:
            daily_ranges = _build_daily_ranges(temp_max_list, temp_min_list)
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
        stats["dry_days"] = safe_count(precip_list, lambda x: x <= 0.1)  # noqa: PLR2004
        stats.update(_build_precipitation_percentages(precip_list, stats["dry_days"]))

        years = len({date[:4] for date in dates})
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
            stats["wind_light"] = safe_count(wind_list, lambda x: 1 < x <= 11)  # noqa: PLR2004
            stats["wind_moderate"] = safe_count(wind_list, lambda x: 11 < x <= 29)  # noqa: PLR2004
            stats["wind_strong"] = safe_count(wind_list, lambda x: x > 29)  # noqa: PLR2004

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
        stats["years"] = len({date[:4] for date in dates}) if dates else 0
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
                (
                    current_streak,
                    current_start_idx,
                    max_streak,
                    max_start_idx,
                    max_end_idx,
                ) = _update_streak_state(
                    precip,
                    i,
                    current_streak,
                    current_start_idx,
                    max_streak,
                    max_start_idx,
                    max_end_idx,
                )

            # Utolsó streak ellenőrzése
            if current_streak > max_streak:
                max_streak = current_streak
                max_start_idx = current_start_idx
                max_end_idx = len(precip_list) - 1

            if max_streak >= 3:  # noqa: PLR2004
                return {
                    "days": max_streak,
                    "start": dates[max_start_idx],
                    "end": dates[max_end_idx],
                }

            return None

        except Exception as e:
            logger.error(f"Száraz időszak keresési hiba: {e}")
            return None
