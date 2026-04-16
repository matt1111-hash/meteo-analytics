# mypy: ignore-errors
"""Use case orchestration for multi-city analytics."""

from __future__ import annotations

import logging
import time
from typing import Any

from src.domain.analytics.models import CityWeatherData, MultiCityQuery
from src.domain.analytics.repositories import CityRepositoryProtocol
from src.domain.analytics.services import (
    AnalyticsTransformService,
    RegionResolverService,
    WeatherFetchService,
)
from src.domain.entities.analytics_models import AnalyticsQuestion, AnalyticsResult
from src.domain.entities.weather import CityWeatherResult
from src.domain.value_objects.enums import (
    AnalyticsMetric,
    DataSource,
    QuestionType,
    RegionScope,
)

# Re-export everything from support so that star-imports from this module still work.
from .analyze_multi_city_support import *  # noqa: F403

# pylint: disable=too-few-public-methods,too-many-arguments,too-many-locals,broad-exception-caught

logger = logging.getLogger(__name__)


class AnalyzeMultiCityUseCase:
    """Run multi-city analytics by coordinating domain services."""

    def __init__(  # noqa: D107
        self,
        *,
        region_resolver: RegionResolverService,
        city_repository: CityRepositoryProtocol,
        weather_fetch_service: WeatherFetchService,
        analytics_transform_service: AnalyticsTransformService,
        query_types: dict[str, dict[str, Any]],
        regions: dict[str, dict[str, Any]],
        hungarian_mapping: dict[str, list[str]],
    ) -> None:
        if not query_types:
            raise ValueError("query_types mapping is required")
        if not regions:
            raise ValueError("regions mapping is required")

        self.region_resolver = region_resolver
        self.city_repository = city_repository
        self.weather_fetch_service = weather_fetch_service
        self.analytics_transform_service = analytics_transform_service
        self.query_types = query_types
        self.regions = regions
        self.hungarian_mapping = hungarian_mapping

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def execute(self, query: MultiCityQuery, aggregate: bool = True) -> AnalyticsResult:
        """Execute the multi-city analytics flow.

        Args:
            query: The multi-city query parameters
            aggregate: If True, aggregates multi-day data per city. If False, returns all daily records.
        """
        start_time = time.time()
        try:
            self._validate_query(query)
            query_config = self._require_query_config(query.query_type)

            mapped_region = self.region_resolver.resolve_region_name(query.region)
            region_config = self._require_region_config(mapped_region)
            city_limit = self._resolve_city_limit(query, region_config)

            # Use explicit city names if provided, otherwise query by region
            if query.cities:
                cities = self.city_repository.get_cities_by_names(query.cities)
            else:
                cities = self.city_repository.get_cities_for_region(
                    mapped_region=mapped_region,
                    original_region=query.region,
                    country_codes=region_config["country_codes"],
                    limit=city_limit,
                    hungarian_mapping=self.hungarian_mapping,
                )
            if not cities:
                return self._fallback_result(query, "Nincsenek városok a lekérdezéshez")

            # Pass both start_date and end_date to support date ranges
            weather_data = self.weather_fetch_service.fetch_weather_data_dual_api_batch(
                cities=cities,
                date=query.date,
                region_config=region_config,
                start_date=query.start_date,
                end_date=query.end_date,
            )
            processed_data = self.analytics_transform_service.process_weather_results(
                weather_data,
                query.query_type,
                aggregate=aggregate,
            )
            transformed_results = self._transform_results(processed_data, query.query_type)
            if not transformed_results:
                return self._fallback_result(query, "Nincsenek sikeres időjárási eredmények")

            # For daily time series (aggregate=False), don't limit results
            # For aggregated multi-city (aggregate=True), apply limit
            if aggregate:
                result_limit = query.limit if query.limit is not None else query.max_cities
            else:
                result_limit = None  # Return ALL daily records without limit

            stats = self.analytics_transform_service.calculate_statistics_for_results_none_safe(
                transformed_results
            )
            limited_results = self._apply_result_limit(transformed_results, result_limit)
            provider_stats = self.analytics_transform_service.get_provider_stats(weather_data)
            final_question = query.question or self._build_question(query_config, mapped_region)

            return AnalyticsResult(
                question=final_question,
                city_results=limited_results,
                execution_time=time.time() - start_time,
                total_cities_found=len(cities),
                data_sources_used=[DataSource.AUTO],
                statistics=stats,
                provider_statistics=provider_stats,
            )
        except Exception as exc:  # pragma: no cover - defensive fallback
            logger.error(
                "Kritikus hiba az analyze_multi_city use case-ben: %s",
                exc,
                exc_info=True,
            )
            return self._fallback_result(query, str(exc))

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _transform_results(
        self,
        processed_data: list[CityWeatherData],
        query_type: str,
    ) -> list[CityWeatherResult]:
        results: list[CityWeatherResult] = []
        for idx, city_data in enumerate(processed_data):
            if not city_data.fetch_success:
                continue
            try:
                result_item = self.analytics_transform_service.transform_to_city_weather_result(
                    city_data,
                    query_type,
                )
                result_item.rank = idx + 1
                results.append(result_item)
            except Exception as exc:
                logger.error("Transform error for %s: %s", city_data.city, exc)
        return results

    def _fallback_result(self, query: MultiCityQuery, error_msg: str) -> AnalyticsResult:
        return self.analytics_transform_service.create_empty_analytics_result(
            query.question,
            error_msg,
        )

    def _apply_result_limit(
        self,
        results: list[CityWeatherResult],
        limit: int | None,
    ) -> list[CityWeatherResult]:
        if limit is None:
            return results
        try:
            safe_limit = int(limit)
            if safe_limit <= 0:
                return results
            return results[:safe_limit]
        except (TypeError, ValueError):
            logger.warning("Invalid limit type: %s", type(limit))
            return results

    def _resolve_city_limit(self, query: MultiCityQuery, region_config: dict[str, Any]) -> int:
        candidate = query.max_cities
        try:
            if candidate is None or int(candidate) <= 0:
                return int(region_config["max_cities"])
            return int(candidate)
        except (TypeError, ValueError):
            return int(region_config["max_cities"])

    def _build_question(
        self,
        query_config: dict[str, Any],
        mapped_region: str,
    ) -> AnalyticsQuestion:
        region_display_name = self.regions.get(mapped_region, {}).get(
            "name",
            mapped_region,
        )
        region_scope = self._resolve_region_scope(mapped_region)
        metric_enum = query_config.get("metric_enum", AnalyticsMetric.TEMPERATURE_2M_MAX)
        question_text = query_config["question_template"].format(region=region_display_name)

        return AnalyticsQuestion(
            question_text=question_text,
            question_type=QuestionType.WEATHER_COMPARISON,
            region_scope=region_scope,
            metric=metric_enum,
        )

    def _resolve_region_scope(self, mapped_region: str) -> RegionScope:
        if mapped_region == "Global":
            return RegionScope.GLOBAL
        if mapped_region == "Hungary":
            return RegionScope.COUNTRY
        return RegionScope.CONTINENT

    def _validate_query(self, query: MultiCityQuery) -> None:
        if not query.query_type:
            raise ValueError("query_type hiányzik")
        if not query.region:
            raise ValueError("region hiányzik")
        if not query.date:
            raise ValueError("date hiányzik")

    def _require_query_config(self, query_type: str) -> dict[str, Any]:
        config = self.query_types.get(query_type)
        if not config:
            raise ValueError(f"Ismeretlen lekérdezés típus: {query_type}")
        return config

    def _require_region_config(self, mapped_region: str) -> dict[str, Any]:
        config = self.regions.get(mapped_region)
        if not config:
            raise ValueError(f"Ismeretlen régió: {mapped_region}")
        return config
