"""Adapter from API DTOs to application use case inputs."""
from __future__ import annotations

from typing import Optional

from src.api.dto.weather_request import WeatherAnalysisRequest
from src.domain.analytics.models import MultiCityQuery

DEFAULT_QUERY_TYPE = "windiest_today"
DEFAULT_REGION = "Global"


def to_multi_city_query(request: WeatherAnalysisRequest) -> MultiCityQuery:
    """Transform API request to MultiCityQuery with safe defaults."""
    date_value = _extract_date(request)
    limit = len(request.cities)
    return MultiCityQuery(
        query_type=DEFAULT_QUERY_TYPE,
        region=DEFAULT_REGION,
        date=date_value,
        limit=limit,
        max_cities=limit,
    )


def _extract_date(request: WeatherAnalysisRequest) -> str:
    date_value: Optional[str] = None
    for key in ("date", "start", "end"):
        raw = request.date_range.get(key)
        if raw:
            date_value = str(raw)
            break
    if not date_value:
        raise ValueError("date_range nem tartalmaz érvényes dátumot.")
    return date_value
