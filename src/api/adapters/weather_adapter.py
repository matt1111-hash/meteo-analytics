"""Adapter from API DTOs to application use case inputs."""

from __future__ import annotations

from typing import Optional

from src.api.dto.weather_request import WeatherAnalysisRequest
from src.domain.analytics.models import MultiCityQuery

DEFAULT_QUERY_TYPE = "hottest_today"
DEFAULT_REGION = "Global"


def _metric_to_query_type(metric: str) -> str:
    """Map metric name to query_type for QUERY_TYPES lookup."""
    metric_to_query = {
        "temperature_2m_max": "hottest_today",
        "temperature_2m_min": "coldest_today",
        "temperature_2m_mean": "temperature_mean",
        "precipitation_sum": "wettest_today",
        "windspeed_10m_max": "windiest_today",
        "windgusts_10m_max": "wind_gusts",
        "temperature_range": "temperature_range",
    }
    return metric_to_query.get(metric, DEFAULT_QUERY_TYPE)


def to_multi_city_query(request: WeatherAnalysisRequest) -> MultiCityQuery:
    """Transform API request to MultiCityQuery with safe defaults."""
    date_info = _extract_date_range(request)
    limit = len(request.cities)

    # Use metric from request to determine query_type
    query_type = _metric_to_query_type(request.metric or "temperature_2m_max")

    return MultiCityQuery(
        query_type=query_type,
        region=DEFAULT_REGION,
        date=date_info["date"],
        start_date=date_info.get("start_date"),
        end_date=date_info.get("end_date"),
        limit=limit,
        max_cities=limit,
        cities=request.cities,  # Pass explicit city names
    )


def _extract_date_range(request: WeatherAnalysisRequest) -> dict[str, Optional[str]]:
    """Extract date or date range from request.

    Returns dict with:
    - date: primary date (single date or start date)
    - start_date: range start (if applicable)
    - end_date: range end (if applicable)
    """
    date_range = request.date_range

    # Single date mode
    if "date" in date_range and date_range["date"]:
        return {"date": str(date_range["date"]), "start_date": None, "end_date": None}

    # Date range mode
    if "start" in date_range and "end" in date_range:
        start = date_range.get("start")
        end = date_range.get("end")
        if start and end:
            return {
                "date": str(start),  # Use start as primary date for compatibility
                "start_date": str(start),
                "end_date": str(end),
            }

    # Fallback: try any available date
    for key in ("start", "end"):
        raw = date_range.get(key)
        if raw:
            return {"date": str(raw), "start_date": None, "end_date": None}

    raise ValueError("date_range nem tartalmaz érvényes dátumot.")
