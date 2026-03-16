# mypy: ignore-errors
"""Support helpers for WeatherFetchService."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from src.domain.analytics.models import CityWeatherData


def split_batches(
    cities: List[Dict[str, Any]], batch_size: int
) -> List[List[Dict[str, Any]]]:
    """Split cities into fixed-size batches."""
    return [
        cities[index : index + batch_size]
        for index in range(0, len(cities), batch_size)
    ]


def resolve_effective_dates(
    date: str, start_date: Optional[str], end_date: Optional[str]
) -> tuple[str, str]:
    """Resolve effective date range for a query."""
    return start_date or date, end_date or date


def normalize_weather_result(weather_result: Any) -> tuple[Any, str]:
    """Normalize weather client result and source."""
    if isinstance(weather_result, tuple) and len(weather_result) == 2:
        weather_data, source = weather_result
        return weather_data, source
    return weather_result, "auto"


def calculate_temperature_range(temp_max: Any, temp_min: Any) -> Any:
    """Calculate temperature range safely."""
    if temp_max is None or temp_min is None:
        return None
    try:
        return temp_max - temp_min
    except (TypeError, ValueError):
        return None


def build_city_weather_record(
    city: Dict[str, Any],
    daily_data: Dict[str, Any],
    start_date: str,
    source: str,
    attempt: int,
) -> CityWeatherData:
    """Build CityWeatherData from one daily payload."""
    temp_max = daily_data.get("temperature_2m_max")
    temp_min = daily_data.get("temperature_2m_min")
    return CityWeatherData(
        city=city["city"],
        country=city["country"],
        country_code=city["country_code"],
        lat=city["lat"],
        lon=city["lon"],
        population=city.get("population"),
        date=daily_data.get("date") or start_date,
        temperature_2m_max=temp_max,
        temperature_2m_min=temp_min,
        temperature_2m_mean=daily_data.get("temperature_2m_mean"),
        precipitation_sum=daily_data.get("precipitation_sum"),
        windspeed_10m_max=daily_data.get("windspeed_10m_max"),
        windgusts_10m_max=daily_data.get("wind_gusts_10m_max"),
        meteostat_station_id=city.get("meteostat_station_id"),
        data_quality_score=city.get("data_quality_score"),
        data_source=source,
        fetch_timestamp=datetime.now().isoformat(),
        fetch_success=True,
        retry_count=attempt,
        temperature_range=calculate_temperature_range(temp_max, temp_min),
    )


def create_city_results(
    city: Dict[str, Any],
    weather_data: List[Dict[str, Any]],
    start_date: str,
    source: str,
    attempt: int,
) -> List[CityWeatherData]:
    """Create result records for a single city query."""
    return [
        build_city_weather_record(city, daily_data, start_date, source, attempt)
        for daily_data in weather_data
    ]


def create_empty_city_data(
    city: Dict[str, Any], error_msg: str = "Ismeretlen hiba"
) -> CityWeatherData:
    """Return empty CityWeatherData for failure cases."""
    return CityWeatherData(
        city=city.get("city", "Ismeretlen"),
        country=city.get("country", "Ismeretlen"),
        country_code=city.get("country_code", "XX"),
        lat=city.get("lat", 0.0),
        lon=city.get("lon", 0.0),
        population=city.get("population"),
        data_source="error",
        fetch_success=False,
        error_message=error_msg,
    )
