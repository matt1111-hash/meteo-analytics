# ruff: noqa: F403, F405,noqa: I001
# mypy: ignore-errors
"""Mixin part 1 for CategoryCalculators."""

from __future__ import annotations

from .category_calculators_support import *


def _get_clean_indexed_values(values: List) -> list[tuple[int, Any]]:
    """Return indexed non-null values."""
    return [(index, value) for index, value in enumerate(values) if value is not None]


def _append_record(
    records: list[ExtremeRecord],
    category: str,
    record_type: str,
    value: str,
    date: str,
    raw_value: float,
) -> None:
    """Append a normalized extreme record."""
    records.append(
        ExtremeRecord(
            category=category,
            record_type=record_type,
            value=value,
            date=date,
            raw_value=raw_value,
        )
    )


def _append_temperature_extremes(
    records: list[ExtremeRecord],
    temp_max_list: List,
    temp_min_list: List,
    dates: List[str],
) -> None:
    """Append max and min temperature records when available."""
    if temp_max_list and len(temp_max_list) == len(dates):
        clean_max = _get_clean_indexed_values(temp_max_list)
        if clean_max:
            max_idx, max_temp = max(clean_max, key=lambda x: x[1])
            _append_record(
                records,
                "🌡️ Hőmérséklet",
                "🔥 Legmelegebb nap",
                f"{max_temp:.1f}°C",
                dates[max_idx],
                float(max_temp),
            )

    if temp_min_list and len(temp_min_list) == len(dates):
        clean_min = _get_clean_indexed_values(temp_min_list)
        if clean_min:
            min_idx, min_temp = min(clean_min, key=lambda x: x[1])
            _append_record(
                records,
                "🌡️ Hőmérséklet",
                "🧊 Leghidegebb nap",
                f"{min_temp:.1f}°C",
                dates[min_idx],
                float(min_temp),
            )


def _build_daily_ranges(temp_max_list: List, temp_min_list: List) -> list[tuple[int, float]]:
    """Build daily temperature ranges for days with complete data."""
    daily_ranges: list[tuple[int, float]] = []
    for i in range(min(len(temp_max_list), len(temp_min_list))):
        if temp_max_list[i] is not None and temp_min_list[i] is not None:
            daily_ranges.append((i, temp_max_list[i] - temp_min_list[i]))  # noqa: PERF401
    return daily_ranges


class CategoryCalculatorsPart1Mixin:  # noqa: D101
    def calculate_temperature_records(
        self, daily_data: Dict[str, List], dates: List[str]
    ) -> List[ExtremeRecord]:
        """Hőmérséklet rekordok számítása."""
        records = []

        try:
            temp_max_list = daily_data.get("temperature_2m_max", [])
            temp_min_list = daily_data.get("temperature_2m_min", [])
            _append_temperature_extremes(records, temp_max_list, temp_min_list, dates)

            if temp_max_list and temp_min_list:
                daily_ranges = _build_daily_ranges(temp_max_list, temp_min_list)
                if daily_ranges:
                    max_range_idx, max_range = max(daily_ranges, key=lambda x: x[1])
                    _append_record(
                        records,
                        "🌡️ Hőmérséklet",
                        "📊 Legnagyobb napi hőingás",
                        f"{max_range:.1f}°C",
                        dates[max_range_idx],
                        float(max_range),
                    )

        except Exception as e:
            logger.error(f"Hőmérséklet rekordok hiba: {e}")

        return records

    def calculate_precipitation_records(
        self, daily_data: Dict[str, List], dates: List[str]
    ) -> List[ExtremeRecord]:
        """Csapadék rekordok számítása."""
        records = []

        try:
            precip_list = daily_data.get("precipitation_sum", [])
            if precip_list and len(precip_list) == len(dates):
                clean_precip = _get_clean_indexed_values(precip_list)
                if clean_precip:
                    max_precip_idx, max_precip = max(clean_precip, key=lambda x: x[1])
                    _append_record(
                        records,
                        "🌧️ Csapadék",
                        "💧 Legcsapadékosabb nap",
                        f"{max_precip:.1f}mm",
                        dates[max_precip_idx],
                        float(max_precip),
                    )

        except Exception as e:
            logger.error(f"Csapadék rekordok hiba: {e}")

        return records

    def calculate_wind_records(
        self, daily_data: Dict[str, List], dates: List[str]
    ) -> List[ExtremeRecord]:
        """Széllökés rekordok számítása."""
        records = []

        try:
            wind_data, wind_source = self._get_wind_data(daily_data)

            if wind_data and len(wind_data) == len(dates):
                clean_wind = _get_clean_indexed_values(wind_data)
                if clean_wind:
                    max_wind_idx, max_wind = max(clean_wind, key=lambda x: x[1])

                    from ..utils import WindGustsAnalyzer, WindGustsConstants

                    if wind_source == "wind_gusts_max":
                        analyzer = WindGustsAnalyzer()
                        category = analyzer.categorize_wind_gust(max_wind, wind_source)
                        category_info = WindGustsConstants.CATEGORIES.get(category, "ISMERETLEN")
                        _append_record(
                            records,
                            "🌪️ Széllökés",
                            f"🚨 Legerősebb ({category_info})",
                            f"{max_wind:.1f}km/h",
                            dates[max_wind_idx],
                            float(max_wind),
                        )
                    else:
                        _append_record(
                            records,
                            "💨 Szél",
                            "🌪️ Legszelesebb nap",
                            f"{max_wind:.1f}km/h",
                            dates[max_wind_idx],
                            float(max_wind),
                        )

        except Exception as e:
            logger.error(f"Széllökés rekordok hiba: {e}")

        return records

    @staticmethod
    def _get_wind_data(daily_data: Dict[str, List]) -> Tuple[Optional[List], str]:
        """Széladatok prioritás alapú kiválasztása."""
        wind_gusts_max = daily_data.get("wind_gusts_max", [])
        windspeed_10m_max = daily_data.get("windspeed_10m_max", [])
        windspeed = daily_data.get("windspeed", [])

        if wind_gusts_max:
            return wind_gusts_max, "wind_gusts_max"
        if windspeed_10m_max:
            return windspeed_10m_max, "windspeed_10m_max"
        if windspeed:
            return windspeed, "windspeed"
        return None, "no_data"
