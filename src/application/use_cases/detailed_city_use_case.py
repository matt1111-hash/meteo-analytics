"""Use case for detailed single-city analysis with multiple metrics.

Performs a single weather fetch and extracts four metrics from the same data,
eliminating the previous 4x redundant API calls.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any

from src.domain.analytics.models import CityWeatherData
from src.domain.analytics.services import AnalyticsTransformService
from src.domain.ports import CityRepositoryPort, WeatherFetchPort

logger = logging.getLogger(__name__)

METRIC_QUERY_TYPES: dict[str, str] = {
    "temperature": "temperature_mean",
    "wind": "windiest_today",
    "wind_gusts": "wind_gusts",
    "precipitation": "wettest_today",
}


@dataclass(frozen=True)
class DetailedCityResult:
    """Structured result for the four detailed metrics."""

    city: str
    start: str
    end: str
    temperature_data: list[dict[str, Any]]
    wind_data: list[dict[str, Any]]
    wind_gusts_data: list[dict[str, Any]]
    precipitation_data: list[dict[str, Any]]
    execution_time: float = 0.0


class DetailedCityUseCase:
    """Single-fetch multi-metric detailed city analysis."""

    def __init__(  # noqa: D107
        self,
        *,
        city_repository: CityRepositoryPort,
        weather_fetch_service: WeatherFetchPort,
        analytics_transform_service: AnalyticsTransformService,
        query_types: dict[str, dict[str, Any]],
        regions: dict[str, dict[str, Any]],
    ) -> None:
        self._city_repo = city_repository
        self._fetch_service = weather_fetch_service
        self._transform_service = analytics_transform_service
        self._query_types = query_types
        self._regions = regions

    def execute(self, city: str, start: str, end: str) -> DetailedCityResult:
        """Fetch once, extract four metrics from the same data."""
        t0 = time.time()

        cities = self._city_repo.get_cities_by_names([city])
        if not cities:
            raise ValueError(f"City not found: {city}")

        region_config = self._regions.get("Global", {})
        weather_data = self._fetch_service.fetch_weather_data_dual_api_batch(
            cities=cities,
            date=start,
            region_config=region_config,
            start_date=start,
            end_date=end,
        )

        metric_results: dict[str, list[dict[str, Any]]] = {}
        for key, query_type in METRIC_QUERY_TYPES.items():
            metric_results[key] = self._extract_metric(
                weather_data,
                query_type,
            )

        return DetailedCityResult(
            city=city,
            start=start,
            end=end,
            temperature_data=metric_results["temperature"],
            wind_data=metric_results["wind"],
            wind_gusts_data=metric_results["wind_gusts"],
            precipitation_data=metric_results["precipitation"],
            execution_time=time.time() - t0,
        )

    def _extract_metric(
        self,
        weather_data: list[CityWeatherData],
        query_type: str,
    ) -> list[dict[str, Any]]:
        """Process weather data for a single metric and return dicts."""
        processed = self._transform_service.process_weather_results(
            weather_data,
            query_type,
            aggregate=False,
        )
        results: list[dict[str, Any]] = []
        for idx, cd in enumerate(processed):
            if not cd.fetch_success:
                continue
            try:
                item = self._transform_service.transform_to_city_weather_result(
                    cd,
                    query_type,
                )
                item.rank = idx + 1
                results.append(item.to_dict())
            except Exception as exc:
                logger.error("Transform error for %s [%s]: %s", cd.city, query_type, exc)
        return results


__all__ = ["DetailedCityResult", "DetailedCityUseCase", "METRIC_QUERY_TYPES"]  # noqa: RUF022
