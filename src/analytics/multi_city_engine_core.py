#!/usr/bin/env python3
# mypy: ignore-errors
"""
Multi-City Analytics Engine - Core Engine
Main MultiCityEngine class for multi-city weather analytics
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from src.application.use_cases.analyze_multi_city import AnalyzeMultiCityUseCase
from src.domain.analytics.models import CityWeatherData, MultiCityQuery
from src.domain.analytics.repositories import CityRepositoryProtocol
from src.domain.analytics.services import (
    AnalyticsTransformService,
    RegionResolverService,
    WeatherFetchService,
)
from src.domain.entities.analytics_models import AnalyticsQuestion, AnalyticsResult
from src.domain.entities.weather import CityWeatherResult
from src.domain.value_objects.enums import AnalyticsMetric, QuestionType, RegionScope
from src.infrastructure.container import (
    get_city_repository_port,
    get_weather_client_port,
)

from .multi_city_engine_query_types import QUERY_TYPES
from .multi_city_engine_region_ops import get_cities_for_region
from .multi_city_engine_result_factory import create_empty_analytics_result_with_types
from .multi_city_types import HUNGARIAN_REGIONAL_MAPPING, REGIONS

logger = logging.getLogger(__name__)


class MultiCityEngine:
    """
    Multi-city időjárás elemzés koordinátor.

    Felelősségek:
    - DUAL-API ROUTING
    - Országválasztás kezelése
    - BATCH PROCESSING
    - PROGRESS TRACKING
    - ADAT TRANSZFORMÁCIÓ (CityWeatherData -> CityWeatherResult)
    - NONE-SAFE STATISZTIKÁK
    - RÉGIÓ/MEGYE MAPPING TELJES
    - ERROR HANDLING
    - VALÓDI REGIONÁLIS SZŰRÉS
    """

    QUERY_TYPES = QUERY_TYPES

    def __init__(
        self,
        db_path: str | None = None,
        hungarian_db_path: str | None = None,
        city_repository: CityRepositoryProtocol | None = None,
    ):
        """MultiCityEngine inicializálása repository injekcióval (CA compliant - uses ports)."""
        project_root = Path(__file__).parent.parent.parent
        default_db = project_root / "data" / "cities.db"
        default_hu_db = project_root / "data" / "hungarian_settlements.db"

        self.db_path = Path(db_path) if db_path else default_db
        self.hungarian_db_path = Path(hungarian_db_path) if hungarian_db_path else default_hu_db

        # Use port for city repository (CA compliant)
        self.city_repository: CityRepositoryProtocol = city_repository or get_city_repository_port()
        self.city_repository.validate_paths()
        self.region_resolver = RegionResolverService()

        self.max_workers = 8
        self.request_timeout = 90
        self.max_retries = 2
        self.retry_delay = 3.0

        # Use port for weather client (CA compliant)
        try:
            self.weather_client = get_weather_client_port()
            logger.info("✅ WeatherClient dual-api integráció sikeres (port-based)")
        except ImportError as e:
            logger.warning(f"⚠ WeatherClient import hiba: {e}")
            self.weather_client = None

        self.weather_fetch_service = WeatherFetchService(
            weather_client=self.weather_client,
            max_workers=self.max_workers,
            request_timeout=self.request_timeout,
            max_retries=self.max_retries,
            retry_delay=self.retry_delay,
        )
        self.analytics_transform_service = AnalyticsTransformService(self.QUERY_TYPES)
        self.use_case = AnalyzeMultiCityUseCase(
            region_resolver=self.region_resolver,
            city_repository=self.city_repository,
            weather_fetch_service=self.weather_fetch_service,
            analytics_transform_service=self.analytics_transform_service,
            query_types=self.QUERY_TYPES,
            regions=REGIONS,
            hungarian_mapping=HUNGARIAN_REGIONAL_MAPPING,
        )

        logger.info("🚀 Multi-city engine inicializálva")

    def execute_analytics_query(
        self,
        query: MultiCityQuery,
        progress_callback: callable | None = None,  # noqa: ARG002
    ) -> AnalyticsResult:
        """Execute analytics query with optional progress callback."""
        return self.use_case.execute(query)

    def get_cities_for_region(
        self, region: str, limit: int | None = None, max_cities: int | None = None
    ) -> list[dict[str, Any]]:
        """
        Get cities for a given region with proper regional filtering.

        Args:
            region: Region name (e.g. "Észak-Magyarország")
            limit: Result limit
            max_cities: Maximum number of cities

        Returns:
            List of cities (filtered by region if applicable)
        """
        return get_cities_for_region(self, region, limit, max_cities)

    def analyze_multi_city(
        self,
        query_type: str,
        region: str,
        date: str,
        limit: int | None = None,
        question: AnalyticsQuestion | None = None,
    ) -> AnalyticsResult:
        """Analyze multi-city weather data."""
        query = MultiCityQuery(
            query_type=query_type,
            region=region,
            date=date,
            limit=limit,
            question=question,
            max_cities=None,
        )
        return self.use_case.execute(query)

    def _transform_to_city_weather_result(
        self, city_data: CityWeatherData, query_type: str
    ) -> CityWeatherResult:
        """Transform CityWeatherData to CityWeatherResult."""
        return self.analytics_transform_service.transform_to_city_weather_result(
            city_data, query_type
        )

    def _fetch_weather_data_dual_api_batch(
        self, cities: list[dict[str, Any]], date: str, region: str
    ) -> list[CityWeatherData]:
        """Fetch weather data for multiple cities in parallel."""
        region_config = REGIONS[region]
        return self.weather_fetch_service.fetch_weather_data_dual_api_batch(
            cities=cities,
            date=date,
            region_config=region_config,
        )

    def _process_dual_api_batch(
        self,
        batch: list[dict[str, Any]],
        date: str,
        rate_limit_delay: float,  # noqa: ARG002
    ) -> list[CityWeatherData]:
        """Process a batch of cities."""
        return self.weather_fetch_service.process_dual_api_batch(batch, date)

    def _fetch_single_city_weather_dual_api(
        self, city: dict[str, Any], date: str
    ) -> CityWeatherData:
        """Fetch weather data for a single city."""
        return self.weather_fetch_service.fetch_single_city_weather_dual_api(city, date)

    def _create_empty_city_data(
        self, city: dict[str, Any], error_msg: str = "Ismeretlen hiba"
    ) -> CityWeatherData:
        """Create empty CityWeatherData for error cases."""
        return self.weather_fetch_service.create_empty_city_data(city, error_msg)

    def _process_weather_results(
        self, weather_data: list[CityWeatherData], query_type: str
    ) -> list[CityWeatherData]:
        """Process and sort weather results."""
        return self.analytics_transform_service.process_weather_results(weather_data, query_type)

    def _calculate_statistics_for_results_none_safe(
        self, results: list[CityWeatherResult]
    ) -> dict[str, float]:
        """Calculate statistics for results."""
        return self.analytics_transform_service.calculate_statistics_for_results_none_safe(results)

    def _get_provider_stats(self, weather_data: list[CityWeatherData]) -> dict[str, int]:
        """Get provider statistics."""
        return self.analytics_transform_service.get_provider_stats(weather_data)

    def _create_empty_analytics_result(
        self, question: AnalyticsQuestion | None, error_msg: str = "Ismeretlen hiba"
    ) -> AnalyticsResult:
        """Create empty AnalyticsResult for error cases."""
        return create_empty_analytics_result_with_types(
            question=question,
            error_msg=error_msg,
            analytics_question_cls=AnalyticsQuestion,
            analytics_result_cls=AnalyticsResult,
            question_type_weather_comparison=QuestionType.WEATHER_COMPARISON,
            question_type_temperature_max=QuestionType.TEMPERATURE_MAX,
            region_scope_global=RegionScope.GLOBAL,
            temperature_metric=AnalyticsMetric.TEMPERATURE_2M_MAX,
        )

    def resolve_region_name(self, region_input: str) -> str:
        """Resolve region name to canonical form."""
        return self.region_resolver.resolve_region_name(region_input)


__all__ = ["MultiCityEngine"]
