# mypy: ignore-errors
"""Multi-city analytics ports."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from src.domain.analytics.models import MultiCityQuery
from src.domain.entities.analytics_models import AnalyticsQuestion, AnalyticsResult
from src.domain.ports import CityRepositoryPort


class MultiCityEnginePort(Protocol):
    """Port for multi-city analytics operations."""

    def analyze_multi_city(  # noqa: D102
        self,
        query_type: str,
        region: str,
        date: str,
        limit: int | None = None,
        question: AnalyticsQuestion | None = None,
    ) -> AnalyticsResult: ...

    def execute_analytics_query(  # noqa: D102
        self,
        query: MultiCityQuery,
        progress_callback: callable | None = None,
    ) -> AnalyticsResult: ...

    def get_cities_for_region(  # noqa: D102
        self,
        region: str,
        limit: int | None = None,
        max_cities: int | None = None,
    ) -> list[dict[str, Any]]: ...

    def resolve_region_name(self, region_input: str) -> str: ...  # noqa: D102


@dataclass
class MultiCityEngineConfig:
    """Configuration for MultiCityEngine."""

    max_workers: int = 8
    request_timeout: int = 90
    max_retries: int = 2
    retry_delay: float = 3.0


def get_multi_city_engine_port(
    city_repository: CityRepositoryPort | None = None,
    weather_client: object | None = None,  # noqa: ARG001
    config: MultiCityEngineConfig | None = None,  # noqa: ARG001
) -> MultiCityEnginePort:
    """Factory function to get a MultiCityEnginePort implementation."""
    from pathlib import Path

    from src.analytics.multi_city_engine_core import MultiCityEngine

    project_root = Path(__file__).parent.parent.parent
    db_path = project_root / "data" / "cities.db"
    hungarian_db_path = project_root / "data" / "hungarian_settlements.db"

    return MultiCityEngine(
        db_path=str(db_path),
        hungarian_db_path=str(hungarian_db_path),
        city_repository=city_repository,
    )
