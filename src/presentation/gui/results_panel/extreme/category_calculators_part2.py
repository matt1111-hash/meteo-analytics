# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Mixin part 2 for CategoryCalculators."""

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


def _is_valid_series(values: List, dates: List[str]) -> bool:
    """Return whether values exist and align with the date list."""
    return bool(values) and len(values) == len(dates)


def _get_pressure_series(
    daily_data: Dict[str, List], max_key: str, min_key: str
) -> tuple[List, List]:
    """Prefer sea-level pressure and fall back to surface pressure."""
    pressure_max = daily_data.get(max_key, [])
    pressure_min = daily_data.get(min_key, [])
    if pressure_max or pressure_min:
        return pressure_max, pressure_min
    return (
        daily_data.get("surface_pressure_max", []),
        daily_data.get("surface_pressure_min", []),
    )


def _append_max_record(
    records: list[ExtremeRecord],
    values: List,
    dates: List[str],
    category: str,
    record_type: str,
    formatter: Callable[[Any], str],
) -> None:
    """Append maximum-value record for a validated series."""
    if not _is_valid_series(values, dates):
        return
    clean_values = _get_clean_indexed_values(values)
    if not clean_values:
        return
    max_idx, max_value = max(clean_values, key=lambda item: item[1])
    _append_record(
        records,
        category,
        record_type,
        formatter(max_value),
        dates[max_idx],
        float(max_value),
    )


def _append_min_record(
    records: list[ExtremeRecord],
    values: List,
    dates: List[str],
    category: str,
    record_type: str,
    formatter: Callable[[Any], str],
) -> None:
    """Append minimum-value record for a validated series."""
    if not _is_valid_series(values, dates):
        return
    clean_values = _get_clean_indexed_values(values)
    if not clean_values:
        return
    min_idx, min_value = min(clean_values, key=lambda item: item[1])
    _append_record(
        records,
        category,
        record_type,
        formatter(min_value),
        dates[min_idx],
        float(min_value),
    )


class CategoryCalculatorsPart2Mixin:
    def calculate_wind_speed_records(
        self, daily_data: Dict[str, List], dates: List[str]
    ) -> List[ExtremeRecord]:
        """Átlagszél rekordok (külön a széllökéstől)."""
        records = []

        try:
            speed_list = daily_data.get("windspeed_10m_max", []) or daily_data.get(
                "windspeed", []
            )
            _append_max_record(
                records,
                speed_list,
                dates,
                "💨 Átlagszél",
                "🌬️ Legszelesebb nap",
                lambda value: f"{value:.1f}km/h",
            )
        except Exception as e:
            logger.error(f"Átlagszél rekordok hiba: {e}")

        return records

    def calculate_humidity_records(
        self, daily_data: Dict[str, List], dates: List[str]
    ) -> List[ExtremeRecord]:
        """Páratartalom rekordok."""
        records = []

        try:
            humidity_max = daily_data.get("relative_humidity_2m_max", [])
            humidity_min = daily_data.get("relative_humidity_2m_min", [])
            _append_max_record(
                records,
                humidity_max,
                dates,
                "💧 Páratartalom",
                "🌫️ Legmagasabb páratartalom",
                lambda value: f"{value:.0f}%",
            )
            _append_min_record(
                records,
                humidity_min,
                dates,
                "💧 Páratartalom",
                "🏜️ Legalacsonyabb páratartalom",
                lambda value: f"{value:.0f}%",
            )
        except Exception as e:
            logger.error(f"Páratartalom rekordok hiba: {e}")

        return records

    def calculate_pressure_records(
        self, daily_data: Dict[str, List], dates: List[str]
    ) -> List[ExtremeRecord]:
        """Légnyomás rekordok."""
        records = []

        try:
            pressure_max, pressure_min = _get_pressure_series(
                daily_data, "pressure_msl_max", "pressure_msl_min"
            )
            _append_max_record(
                records,
                pressure_max,
                dates,
                "🔵 Légnyomás",
                "⬆️ Legmagasabb nyomás",
                lambda value: f"{value:.0f}hPa",
            )
            _append_min_record(
                records,
                pressure_min,
                dates,
                "🔵 Légnyomás",
                "⬇️ Legalacsonyabb nyomás",
                lambda value: f"{value:.0f}hPa",
            )
        except Exception as e:
            logger.error(f"Légnyomás rekordok hiba: {e}")

        return records

    def calculate_sunshine_records(
        self, daily_data: Dict[str, List], dates: List[str]
    ) -> List[ExtremeRecord]:
        """Napsütés rekordok."""
        records = []

        try:
            sunshine = daily_data.get("sunshine_duration", [])
            clean_sun = self._get_positive_sunshine_values(sunshine, dates)
            if clean_sun:
                max_idx, max_sun = max(clean_sun, key=lambda item: item[1])
                hours = max_sun / 3600
                _append_record(
                    records,
                    "☀️ Napsütés",
                    "🌞 Leghosszabb napsütés",
                    f"{hours:.1f}óra",
                    dates[max_idx],
                    float(max_sun),
                )
        except Exception as e:
            logger.error(f"Napsütés rekordok hiba: {e}")

        return records

    @staticmethod
    def _get_positive_sunshine_values(
        sunshine: List, dates: List[str]
    ) -> list[tuple[int, Any]]:
        """Return positive sunshine values when lengths align."""
        if not _is_valid_series(sunshine, dates):
            return []
        return [
            (index, value)
            for index, value in enumerate(sunshine)
            if value is not None and value > 0
        ]
