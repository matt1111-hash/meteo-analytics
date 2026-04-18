#!/usr/bin/env python3

"""Wind rose domain service — pure computation, no HTTP dependencies."""

from __future__ import annotations

from typing import Any

_MAX_DIRECTION_DEGREES = 360
_CALM_SPEED_THRESHOLD = 5.0

# Direction configuration (16 compass points)
DIRECTION_BINS = [
    0,
    22.5,
    45,
    67.5,
    90,
    112.5,
    135,
    157.5,
    180,
    202.5,
    225,
    247.5,
    270,
    292.5,
    315,
    337.5,
    360,
]
DIRECTION_LABELS = [
    "N",
    "NNE",
    "NE",
    "ENE",
    "E",
    "ESE",
    "SE",
    "SSE",
    "S",
    "SSW",
    "SW",
    "WSW",
    "W",
    "WNW",
    "NW",
    "NNW",
]

# Speed buckets (km/h)
SPEED_BINS = [0, 25, 50, 70, 100, 120, 999]
SPEED_LABELS = ["0-25", "25-50", "50-70", "70-100", "100-120", "120+"]


class WindRoseCalculator:
    """Pure domain service for wind rose calculations."""

    def calculate(self, daily_data: dict[str, Any]) -> dict[str, Any]:
        """Process daily weather data into wind rose format.

        Raises:
            ValueError: If required data is missing or no valid wind data.
        """
        dates = daily_data.get("time", []) or daily_data.get("date", [])
        winddirection = daily_data.get("winddirection_10m_dominant", [])
        wind_gusts_max = daily_data.get("wind_gusts_10m_max", [])
        windspeed_10m_max = daily_data.get("windspeed_10m_max", [])

        if not dates or not winddirection:
            raise ValueError("Missing required data: dates or winddirection")

        windspeed_data, data_source = _select_wind_speed_data(
            dates, wind_gusts_max, windspeed_10m_max
        )
        paired_data = _build_paired_data(dates, winddirection, windspeed_data)

        if not paired_data:
            raise ValueError("No valid wind data after filtering")

        result = _build_statistics(paired_data, data_source)
        result["directions"] = _build_direction_counts(paired_data)
        return result


def _has_numeric_values(values: list[Any], expected_length: int) -> bool:
    return len(values) == expected_length and any(
        isinstance(v, (int, float)) and v is not None for v in values
    )


def _select_wind_speed_data(
    dates: list[Any],
    wind_gusts_max: list[Any],
    windspeed_10m_max: list[Any],
) -> tuple[list[Any], str]:
    if _has_numeric_values(wind_gusts_max, len(dates)):
        return wind_gusts_max, "wind_gusts_max"
    if _has_numeric_values(windspeed_10m_max, len(dates)):
        return windspeed_10m_max, "windspeed_10m_max"
    raise ValueError("No valid wind speed data available (wind_gusts_10m_max or windspeed_10m_max)")


def _build_paired_data(
    dates: list[Any],
    winddirection: list[Any],
    windspeed_data: list[Any],
) -> list[dict[str, float]]:
    paired: list[dict[str, float]] = []
    for i in range(len(dates)):
        item = _build_paired_item(i, winddirection, windspeed_data)
        if item is not None:
            paired.append(item)
    return paired


def _build_paired_item(
    index: int,
    winddirection: list[Any],
    windspeed_data: list[Any],
) -> dict[str, float] | None:
    if index >= len(winddirection) or index >= len(windspeed_data):
        return None
    direction = winddirection[index]
    speed = windspeed_data[index]
    if direction is None or speed is None:
        return None
    if not isinstance(direction, (int, float)) or not isinstance(speed, (int, float)):
        return None
    if not (0 <= direction <= _MAX_DIRECTION_DEGREES):
        return None
    return {"direction": float(direction), "speed": float(speed)}


def _count_speed_buckets(direction_observations: list[float]) -> list[int]:
    buckets = [0] * (len(SPEED_BINS) - 1)
    for speed in direction_observations:
        idx = _resolve_speed_bucket_index(speed)
        if idx is not None:
            buckets[idx] += 1
    return buckets


def _resolve_speed_bucket_index(speed: float) -> int | None:
    for i in range(len(SPEED_BINS) - 2):
        if SPEED_BINS[i] <= speed < SPEED_BINS[i + 1]:
            return i
    if speed >= SPEED_BINS[-2]:
        return len(SPEED_BINS) - 2
    return None


def _build_direction_counts(paired_data: list[dict[str, float]]) -> list[dict[str, Any]]:
    counts: list[dict[str, Any]] = []
    for i, dir_start in enumerate(DIRECTION_BINS[:-1]):
        dir_end = DIRECTION_BINS[i + 1]
        obs = [item["speed"] for item in paired_data if dir_start <= item["direction"] < dir_end]
        counts.append(
            {
                "direction": DIRECTION_LABELS[i],
                "angle": (dir_start + dir_end) / 2,
                "speed_buckets": _count_speed_buckets(obs),
            }
        )
    return counts


def _build_statistics(paired_data: list[dict[str, float]], data_source: str) -> dict[str, Any]:
    total = len(paired_data)
    calms = sum(1 for item in paired_data if item["speed"] < _CALM_SPEED_THRESHOLD)
    speeds = [item["speed"] for item in paired_data]
    avg_speed = sum(speeds) / len(speeds) if speeds else 0
    max_speed = max(speeds) if speeds else 0
    calms_pct = (calms / total * 100) if total > 0 else 0
    return {
        "calms_percentage": round(calms_pct, 1),
        "total_observations": total,
        "statistics": {
            "avg_speed": round(avg_speed, 1),
            "max_speed": round(max_speed, 1),
            "data_source": data_source,
            "calms_count": calms,
        },
    }


__all__ = ["DIRECTION_BINS", "DIRECTION_LABELS", "SPEED_BINS", "SPEED_LABELS", "WindRoseCalculator"]
