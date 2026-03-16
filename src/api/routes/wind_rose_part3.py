# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Split definitions from wind_rose.py."""

from __future__ import annotations

from .wind_rose_part1 import WindRoseRequest, WindRoseResponse
from .wind_rose_part2 import _process_wind_rose_data
from .wind_rose_support import *


def _resolve_city_coordinates(request: WindRoseRequest) -> tuple[float, float]:
    """Resolve city coordinates or raise HTTP 404."""
    city_manager = get_city_manager_port()
    coords = city_manager.find_city_by_name(request.city.strip())
    if not coords:
        raise HTTPException(status_code=404, detail=f"City not found: {request.city}")
    return coords


def _fetch_weather_records(
    request: WindRoseRequest, latitude: float, longitude: float
) -> list[dict[str, Any]]:
    """Fetch weather records for the requested city and date range."""
    weather_client = WeatherClient()
    weather_records = weather_client.get_weather_data(
        latitude=latitude,
        longitude=longitude,
        start_date=request.start,
        end_date=request.end,
    )
    if not weather_records:
        raise HTTPException(
            status_code=404,
            detail=f"No weather data found for {request.city} in the specified period",
        )
    return weather_records


def _extract_embedded_daily_data(
    weather_records: list[dict[str, Any]],
) -> dict[str, Any]:
    """Return embedded daily payload if present in the weather records."""
    for record in weather_records:
        if isinstance(record, dict) and "daily" in record:
            daily_data = record.get("daily")
            if isinstance(daily_data, dict):
                return daily_data
    return {}


def _collect_record_dates(weather_records: list[dict[str, Any]]) -> list[Any]:
    """Collect sorted distinct dates from flat weather records."""
    dated_records = [
        record
        for record in weather_records
        if isinstance(record, dict) and (record.get("date") or record.get("time"))
    ]
    return sorted(
        {
            record.get("date") or record.get("time")
            for record in dated_records
            if record.get("date") or record.get("time")
        }
    )


def _has_wind_direction_values(weather_records: list[dict[str, Any]]) -> bool:
    """Return whether flat records contain wind direction values."""
    return any("winddirection_10m_dominant" in record for record in weather_records)


def _extract_flat_series(weather_records: list[dict[str, Any]], key: str) -> list[Any]:
    """Extract a flat weather series for the given key."""
    return [record.get(key) for record in weather_records]


def _rebuild_daily_data_from_flat_records(
    weather_records: list[dict[str, Any]],
) -> dict[str, Any]:
    """Reconstruct daily payload from flat weather records."""
    if not _has_wind_direction_values(weather_records):
        return {}

    dates = _collect_record_dates(weather_records)
    return {
        "time": dates,
        "winddirection_10m_dominant": _extract_flat_series(
            weather_records, "winddirection_10m_dominant"
        ),
        "wind_gusts_10m_max": _extract_flat_series(
            weather_records, "wind_gusts_10m_max"
        ),
        "windspeed_10m_max": _extract_flat_series(weather_records, "windspeed_10m_max"),
    }


def _extract_daily_data(weather_records: list[dict[str, Any]]) -> dict[str, Any]:
    """Extract daily data from embedded or flat weather records."""
    daily_data = _extract_embedded_daily_data(weather_records)
    if daily_data:
        return daily_data

    daily_data = _rebuild_daily_data_from_flat_records(weather_records)
    if daily_data:
        return daily_data

    raise HTTPException(
        status_code=400, detail="No daily weather data available in response"
    )


def _build_response(
    request: WindRoseRequest, wind_rose_data: dict[str, Any]
) -> WindRoseResponse:
    """Build the WindRoseResponse from processed wind data."""
    return WindRoseResponse(
        city=request.city,
        start=request.start,
        end=request.end,
        directions=wind_rose_data["directions"],
        calms_percentage=wind_rose_data["calms_percentage"],
        total_observations=wind_rose_data["total_observations"],
        statistics=wind_rose_data["statistics"],
    )


@router.post("/wind-rose")
async def get_wind_rose(request: WindRoseRequest) -> WindRoseResponse:
    """
    Get wind rose data for a city and date range.

    Wind rose shows the distribution of wind speed and direction.
    Returns 16 compass directions, each with 6 speed buckets.

    Speed buckets (km/h):
    - 0-25: Calm to Light
    - 25-50: Light to Moderate
    - 50-70: Moderate to Fresh
    - 70-100: Fresh to Strong
    - 100-120: Strong to Very Strong
    - 120+: Extreme / Hurricane force

    Args:
        request: WindRoseRequest with city, start, and end dates

    Returns:
        WindRoseResponse with directions array and statistics
    """
    try:
        latitude, longitude = _resolve_city_coordinates(request)
        weather_records = _fetch_weather_records(request, latitude, longitude)
        daily_data = _extract_daily_data(weather_records)
        wind_rose_data = _process_wind_rose_data(daily_data)
        return _build_response(request, wind_rose_data)

    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.error("Unexpected error in wind-rose endpoint: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error") from exc
