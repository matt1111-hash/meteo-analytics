# ruff: noqa: F403, F405,noqa: I001  # noqa: RUF100
"""Split definitions from wind_rose.py."""

from __future__ import annotations

from typing import Any

from fastapi import Depends, HTTPException
from src.api.dependencies import ServiceRegistry, get_services
from starlette.concurrency import run_in_threadpool

from .wind_rose_part1 import WindRoseRequest, WindRoseResponse
from .wind_rose_part2 import _process_wind_rose_data
from .wind_rose_support import *


def _resolve_city_coordinates(request: WindRoseRequest, city_manager: Any) -> tuple[float, float]:
    """Resolve city coordinates or raise HTTP 404."""
    coords = city_manager.find_city_by_name(request.city.strip())
    if not coords:
        raise HTTPException(status_code=404, detail=f"City not found: {request.city}")
    return coords


def _fetch_weather_records(
    request: WindRoseRequest,
    latitude: float,
    longitude: float,
    weather_client: Any,
) -> list[dict[str, Any]]:
    """Fetch weather records for the requested city and date range.

    The weather client is injected by the caller (FIX-04) instead of being
    instantiated locally, so the route depends on the ServiceRegistry port and
    stays free of direct infrastructure coupling.
    """
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
        "wind_gusts_10m_max": _extract_flat_series(weather_records, "wind_gusts_10m_max"),
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

    raise HTTPException(status_code=400, detail="No daily weather data available in response")


def _build_response(request: WindRoseRequest, wind_rose_data: dict[str, Any]) -> WindRoseResponse:
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
async def get_wind_rose(
    request: WindRoseRequest,
    services: ServiceRegistry = Depends(get_services),
) -> WindRoseResponse:
    """Get wind rose data for a city and date range."""
    try:
        latitude, longitude = _resolve_city_coordinates(request, services.city_manager)
        weather_records = await run_in_threadpool(
            lambda: _fetch_weather_records(request, latitude, longitude, services.weather_client)
        )
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
