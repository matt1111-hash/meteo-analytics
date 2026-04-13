"""Domain models for multi-city analytics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.domain.entities.analytics_models import AnalyticsQuestion
from src.domain.value_objects.enums import RegionScope


@dataclass
class MultiCityQuery:
    """Query descriptor for multi-city analytics."""

    query_type: str
    region: str
    date: str  # Single date or start date for compatibility
    max_cities: int = 50
    limit: int | None = None
    question: AnalyticsQuestion | None = None
    region_scope: RegionScope | None = None
    cities: list[str] | None = None  # Explicit city names (bypasses region lookup)
    start_date: str | None = None  # Date range start (if applicable)
    end_date: str | None = None  # Date range end (if applicable)


@dataclass
class CityWeatherData:
    """Structure holding weather data for a single city."""

    city: str
    country: str
    country_code: str
    lat: float
    lon: float
    population: int | None = None
    date: str | None = None
    temperature_2m_max: float | None = None
    temperature_2m_min: float | None = None
    temperature_2m_mean: float | None = None
    precipitation_sum: float | None = None
    windspeed_10m_max: float | None = None
    windgusts_10m_max: float | None = None
    meteostat_station_id: str | None = None
    data_quality_score: float | None = None
    data_source: str = "dual-api"
    fetch_timestamp: str | None = None
    fetch_success: bool = True
    error_message: str | None = None
    retry_count: int = 0
    temperature_range: float | None = None

    def to_dict(self) -> dict[str, Any]:
        """Export to dict for adapters/wrappers."""
        return self.__dict__.copy()
