# ruff: noqa: D102, ARG001
"""Multi-city analytics ports."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from src.domain.analytics.models import MultiCityQuery
from src.domain.entities.analytics_models import AnalyticsQuestion, AnalyticsResult
from src.domain.ports import CityRepositoryPort


class MultiCityEnginePort(Protocol):
    """Port for multi-city analytics operations."""

    def analyze_multi_city(
        self,
        query_type: str,
        region: str,
        date: str,
        limit: int | None = None,
        question: AnalyticsQuestion | None = None,
    ) -> AnalyticsResult: ...

    def execute_analytics_query(
        self,
        query: MultiCityQuery,
        progress_callback: Any | None = None,
    ) -> AnalyticsResult: ...

    def get_cities_for_region(
        self,
        region: str,
        limit: int | None = None,
        max_cities: int | None = None,
    ) -> list[dict[str, Any]]: ...

    def resolve_region_name(self, region_input: str) -> str: ...


@dataclass
class MultiCityEngineConfig:
    """Configuration for MultiCityEngine."""

    max_workers: int = 8
    request_timeout: int = 90
    max_retries: int = 2
    retry_delay: float = 3.0


def get_multi_city_engine_port(
    city_repository: CityRepositoryPort | None = None,
    weather_client: object | None = None,
    config: MultiCityEngineConfig | None = None,
) -> MultiCityEnginePort:
    """Factory — creates MultiCityEngine via composition_root."""
    from src.analytics.multi_city_engine_core import MultiCityEngine  # noqa: PLC0415

    return MultiCityEngine(city_repository=city_repository)
