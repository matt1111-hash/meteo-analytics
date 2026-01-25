"""Domain models for multi-city analytics."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from src.domain.value_objects.enums import RegionScope
from src.domain.entities.analytics_models import AnalyticsQuestion


@dataclass
class MultiCityQuery:
    """Query descriptor for multi-city analytics."""

    query_type: str
    region: str
    date: str  # Single date or start date for compatibility
    max_cities: int = 50
    limit: Optional[int] = None
    question: Optional[AnalyticsQuestion] = None
    region_scope: Optional[RegionScope] = None
    cities: Optional[list[str]] = None  # Explicit city names (bypasses region lookup)
    start_date: Optional[str] = None  # Date range start (if applicable)
    end_date: Optional[str] = None  # Date range end (if applicable)


@dataclass
class CityWeatherData:
    """Structure holding weather data for a single city."""

    city: str
    country: str
    country_code: str
    lat: float
    lon: float
    population: Optional[int] = None
    date: Optional[str] = None
    temperature_2m_max: Optional[float] = None
    temperature_2m_min: Optional[float] = None
    temperature_2m_mean: Optional[float] = None
    precipitation_sum: Optional[float] = None
    windspeed_10m_max: Optional[float] = None
    windgusts_10m_max: Optional[float] = None
    meteostat_station_id: Optional[str] = None
    data_quality_score: Optional[float] = None
    data_source: str = "dual-api"
    fetch_timestamp: Optional[str] = None
    fetch_success: bool = True
    error_message: Optional[str] = None
    retry_count: int = 0
    temperature_range: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Export to dict for adapters/wrappers."""
        return self.__dict__.copy()
