#!/usr/bin/env python3
# ruff: noqa: D102, D107, ARG002
"""
Multi-City Analytics Engine - Thin Facade

Delegates to AnalyzeMultiCityUseCase via composition_root.
Kept for backward compatibility with GUI and port consumers.
"""

from __future__ import annotations

import logging
from typing import Any, cast

from src.domain.analytics.models import MultiCityQuery
from src.domain.analytics.services import RegionResolverService
from src.domain.constants.query_types import QUERY_TYPES
from src.domain.constants.regions import HUNGARIAN_REGIONAL_MAPPING, REGIONS
from src.domain.entities.analytics_models import AnalyticsQuestion, AnalyticsResult
from src.domain.ports import CityRepositoryPort
from src.infrastructure.container.composition_root import build_analyze_multi_city_use_case

logger = logging.getLogger(__name__)


class MultiCityEngine:
    """Thin facade over AnalyzeMultiCityUseCase for backward compatibility."""

    QUERY_TYPES = QUERY_TYPES

    def __init__(
        self,
        db_path: str | None = None,
        hungarian_db_path: str | None = None,
        city_repository: CityRepositoryPort | None = None,
        use_case: Any | None = None,
    ) -> None:
        if use_case is not None:
            self.use_case = use_case
            self.city_repository = city_repository or use_case.city_repository
        else:
            self.use_case = build_analyze_multi_city_use_case()
            self.city_repository = self.use_case.city_repository

        self.region_resolver = RegionResolverService()
        self.analytics_transform_service = self.use_case.analytics_transform_service

    def analyze_multi_city(
        self,
        query_type: str,
        region: str,
        date: str,
        limit: int | None = None,
        question: AnalyticsQuestion | None = None,
    ) -> AnalyticsResult:
        query = MultiCityQuery(
            query_type=query_type,
            region=region,
            date=date,
            limit=limit,
            question=question,
            max_cities=50,
        )
        uc_result = self.use_case.execute(query)
        if uc_result.is_success and uc_result.data is not None:
            return uc_result.data
        return self.analytics_transform_service.create_empty_analytics_result(
            query.question, uc_result.error_message or "No results"
        )

    def execute_analytics_query(
        self,
        query: MultiCityQuery,
        progress_callback: Any | None = None,
    ) -> AnalyticsResult:
        uc_result = self.use_case.execute(query)
        if uc_result.is_success and uc_result.data is not None:
            return uc_result.data
        return self.analytics_transform_service.create_empty_analytics_result(
            query.question, uc_result.error_message or "Unknown error"
        )

    def get_cities_for_region(
        self,
        region: str,
        limit: int | None = None,
        max_cities: int | None = None,
    ) -> list[dict[str, Any]]:
        try:
            mapped_region = self.resolve_region_name(region)
            region_config = REGIONS[mapped_region]
            final_limit = max_cities or limit or int(str(region_config["max_cities"]))

            return self.city_repository.get_cities_for_region(
                mapped_region=mapped_region,
                original_region=region,
                country_codes=cast(list[str], region_config["country_codes"]),
                limit=int(final_limit),
                hungarian_mapping=HUNGARIAN_REGIONAL_MAPPING,
            )
        except Exception as exc:
            logger.error("Hiba városok lekérdezésénél: %s", exc, exc_info=True)
            return []

    def resolve_region_name(self, region_input: str) -> str:
        return self.region_resolver.resolve_region_name(region_input)


__all__ = ["MultiCityEngine"]
