# ruff: noqa: F403, F405,noqa: I001  # noqa: RUF100
# mypy: ignore-errors
"""Split definitions from wind_rose.py."""

from __future__ import annotations

from .wind_rose_part1 import DIRECTION_BINS, DIRECTION_LABELS, SPEED_BINS
from .wind_rose_support import *


def _has_numeric_values(values: list[Any], expected_length: int) -> bool:
    """Return whether the values match the expected size and include numerics."""
    return len(values) == expected_length and any(
        isinstance(value, (int, float)) and value is not None
        for value in values  # noqa: RUF100, UP038
    )


def _select_wind_speed_data(
    dates: list[Any], wind_gusts_max: list[Any], windspeed_10m_max: list[Any]
) -> tuple[list[Any], str]:
    """Pick the best available wind speed series."""
    if _has_numeric_values(wind_gusts_max, len(dates)):
        return wind_gusts_max, "wind_gusts_max"
    if _has_numeric_values(windspeed_10m_max, len(dates)):
        return windspeed_10m_max, "windspeed_10m_max"
    raise HTTPException(
        status_code=400,
        detail="No valid wind speed data available (wind_gusts_10m_max or windspeed_10m_max)",
    )


def _build_paired_data(
    dates: list[Any], winddirection: list[Any], windspeed_data: list[Any]
) -> list[dict[str, float]]:
    """Pair and validate direction and speed observations."""
    paired_data: list[dict[str, float]] = []
    for index, _date in enumerate(dates):
        item = _build_paired_item(index, winddirection, windspeed_data)
        if item is not None:
            paired_data.append(item)
    return paired_data


def _build_paired_item(
    index: int, winddirection: list[Any], windspeed_data: list[Any]
) -> dict[str, float] | None:
    """Build one validated paired wind observation."""
    if not _is_valid_observation_index(index, winddirection, windspeed_data):
        return None
    direction = winddirection[index]
    speed = windspeed_data[index]
    if not _is_supported_observation_pair(direction, speed):
        return None
    if not _is_valid_direction(direction):
        return None
    return {"direction": float(direction), "speed": float(speed)}


def _is_valid_observation_index(
    index: int, winddirection: list[Any], windspeed_data: list[Any]
) -> bool:
    """Return whether the index exists in both source lists."""
    return index < len(winddirection) and index < len(windspeed_data)


def _is_supported_observation_pair(direction: Any, speed: Any) -> bool:
    """Return whether direction/speed values are present and numeric."""
    return (
        direction is not None
        and speed is not None
        and isinstance(direction, (int, float))
        and isinstance(speed, (int, float))
    )


def _is_valid_direction(direction: float) -> bool:
    """Return whether direction is within expected meteorological range."""
    return 0 <= direction <= 360  # noqa: PLR2004


def _count_speed_buckets(direction_observations: list[float]) -> list[int]:
    """Count observations for a direction across speed buckets."""
    speed_buckets = [0] * (len(SPEED_BINS) - 1)
    for speed in direction_observations:
        bucket_index = _resolve_speed_bucket_index(speed)
        if bucket_index is not None:
            speed_buckets[bucket_index] += 1
    return speed_buckets


def _resolve_speed_bucket_index(speed: float) -> int | None:
    """Resolve the target speed bucket index for one observation."""
    for index in range(len(SPEED_BINS) - 2):
        if SPEED_BINS[index] <= speed < SPEED_BINS[index + 1]:
            return index
    if speed >= SPEED_BINS[-2]:
        return len(SPEED_BINS) - 2
    return None


def _build_direction_counts(
    paired_data: list[dict[str, float]],
) -> list[dict[str, Any]]:
    """Aggregate valid observations by direction bins."""
    direction_counts: list[dict[str, Any]] = []
    for index, dir_start in enumerate(DIRECTION_BINS[:-1]):
        dir_end = DIRECTION_BINS[index + 1]
        direction_observations = [
            item["speed"] for item in paired_data if dir_start <= item["direction"] < dir_end
        ]
        direction_counts.append(
            {
                "direction": DIRECTION_LABELS[index],
                "angle": (dir_start + dir_end) / 2,
                "speed_buckets": _count_speed_buckets(direction_observations),
            }
        )
    return direction_counts


def _build_statistics(paired_data: list[dict[str, float]], data_source: str) -> dict[str, Any]:
    """Build summary statistics for wind rose output."""
    total_observations = len(paired_data)
    calms_count = sum(1 for item in paired_data if item["speed"] < 5)  # noqa: PLR2004
    speeds = [item["speed"] for item in paired_data]
    calms_percentage = _calculate_percentage(calms_count, total_observations)
    avg_speed, max_speed = _summarize_speeds(speeds)
    return {
        "calms_percentage": round(calms_percentage, 1),
        "total_observations": total_observations,
        "statistics": {
            "avg_speed": round(avg_speed, 1),
            "max_speed": round(max_speed, 1),
            "data_source": data_source,
            "calms_count": calms_count,
        },
    }


def _calculate_percentage(part: int, total: int) -> float:
    """Calculate percentage safely."""
    return (part / total * 100) if total > 0 else 0


def _summarize_speeds(speeds: list[float]) -> tuple[float, float]:
    """Return average and maximum speed summary."""
    if not speeds:
        return 0, 0
    return sum(speeds) / len(speeds), max(speeds)


def _process_wind_rose_data(daily_data: dict) -> dict:
    """
    Process daily weather data into wind rose format.

    Args:
        daily_data: Dictionary with daily weather data including:
                   - winddirection_10m_dominant: list of wind directions
                   - wind_gusts_10m_max or windspeed_10m_max: list of wind speeds

    Returns:
        Dictionary with directions array, calms_percentage, and statistics
    """
    dates = daily_data.get("time", []) or daily_data.get("date", [])
    winddirection = daily_data.get("winddirection_10m_dominant", [])
    wind_gusts_max = daily_data.get("wind_gusts_10m_max", [])
    windspeed_10m_max = daily_data.get("windspeed_10m_max", [])

    # Validate we have data
    if not dates or not winddirection:
        raise HTTPException(status_code=400, detail="Missing required data: dates or winddirection")

    windspeed_data, data_source = _select_wind_speed_data(dates, wind_gusts_max, windspeed_10m_max)
    paired_data = _build_paired_data(dates, winddirection, windspeed_data)

    if not paired_data:
        raise HTTPException(status_code=400, detail="No valid wind data after filtering")

    result = _build_statistics(paired_data, data_source)
    result["directions"] = _build_direction_counts(paired_data)
    return result
