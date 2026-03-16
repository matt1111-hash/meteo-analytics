# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Mixin part 2 for AnalyticsStatistics."""

from __future__ import annotations

from .analytics_statistics_support import *


class AnalyticsStatisticsPart2Mixin:
    @staticmethod
    def _build_single_day_record(
        values: List[Any],
        dates: List[str],
        record_key: str,
        formatter: str,
        selector: Any,
        *,
        require_positive: bool = False,
    ) -> Dict[str, Dict[str, str]]:
        """Build a single-day record entry when data is present."""
        if not values or len(values) != len(dates):
            return {}

        selected_value = selector(values)
        if selected_value is None:
            return {}
        if require_positive and selected_value <= 0:
            return {}

        selected_index = values.index(selected_value)
        return {
            record_key: {
                "value": formatter.format(selected_value),
                "date": dates[selected_index][:10],
            }
        }

    @staticmethod
    def _build_driest_record(
        precip_list: List[Any], dates: List[str]
    ) -> Dict[str, Dict[str, str]]:
        """Build driest streak record if available."""
        if not precip_list or len(precip_list) != len(dates):
            return {}

        dry_streak = AnalyticsStatistics._find_longest_dry_streak(precip_list, dates)
        if not dry_streak:
            return {}
        return {
            "driest": {
                "value": f"{dry_streak['days']} nap",
                "date": f"{dry_streak['start'][:5]}-{dry_streak['end'][:5]}",
            }
        }

    @staticmethod
    def _build_windiest_record(
        daily_data: Dict[str, Any], dates: List[str]
    ) -> Dict[str, Dict[str, str]]:
        """Build windiest record preferring gust data."""
        wind_data = daily_data.get("wind_gusts_max", []) or daily_data.get(
            "windspeed_10m_max", []
        )
        return AnalyticsStatisticsPart2Mixin._build_single_day_record(
            wind_data,
            dates,
            "windiest",
            "{:.1f}km/h",
            safe_max,
        )

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

            records: Dict[str, Dict[str, str]] = {}
            records.update(
                AnalyticsStatisticsPart2Mixin._build_single_day_record(
                    daily_data.get("temperature_2m_max", []),
                    dates,
                    "hottest",
                    "{:.1f}°C",
                    safe_max,
                )
            )
            records.update(
                AnalyticsStatisticsPart2Mixin._build_single_day_record(
                    daily_data.get("temperature_2m_min", []),
                    dates,
                    "coldest",
                    "{:.1f}°C",
                    safe_min,
                )
            )
            precip_list = daily_data.get("precipitation_sum", [])
            records.update(
                AnalyticsStatisticsPart2Mixin._build_single_day_record(
                    precip_list,
                    dates,
                    "wettest",
                    "{:.1f}mm",
                    safe_max,
                    require_positive=True,
                )
            )
            records.update(
                AnalyticsStatisticsPart2Mixin._build_driest_record(precip_list, dates)
            )
            records.update(
                AnalyticsStatisticsPart2Mixin._build_windiest_record(daily_data, dates)
            )

            logger.info(
                f"Napi rekordok számítva: {len(records)} kategória (max széllökés prioritással)"
            )
            return records

        except Exception as e:
            logger.error(f"Rekord számítási hiba: {e}", exc_info=True)
            return {}
