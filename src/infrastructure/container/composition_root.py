#!/usr/bin/env python3
# ruff: noqa: PLC0415
# mypy: ignore-errors
"""Composition root — single factory for AnalyzeMultiCityUseCase."""

from __future__ import annotations


def build_analyze_multi_city_use_case():
    """Single composition root for multi-city use case."""
    from src.analytics.multi_city_engine_query_types import QUERY_TYPES
    from src.analytics.multi_city_types import HUNGARIAN_REGIONAL_MAPPING, REGIONS
    from src.application.use_cases import AnalyzeMultiCityUseCase
    from src.domain.analytics.services import (
        AnalyticsTransformService,
        RegionResolverService,
        WeatherFetchService,
    )
    from src.infrastructure.container.factories import (
        get_city_repository_port,
        get_weather_client_port,
    )

    return AnalyzeMultiCityUseCase(
        region_resolver=RegionResolverService(),
        city_repository=get_city_repository_port(),
        weather_fetch_service=WeatherFetchService(
            weather_client=get_weather_client_port(),
            max_workers=8,
            request_timeout=90,
            max_retries=2,
            retry_delay=3.0,
        ),
        analytics_transform_service=AnalyticsTransformService(QUERY_TYPES),
        query_types=QUERY_TYPES,
        regions=REGIONS,
        hungarian_mapping=HUNGARIAN_REGIONAL_MAPPING,
    )


def build_detailed_city_use_case():
    """Composition root for detailed single-city multi-metric use case."""
    from src.analytics.multi_city_engine_query_types import QUERY_TYPES
    from src.analytics.multi_city_types import REGIONS
    from src.application.use_cases.detailed_city_use_case import DetailedCityUseCase
    from src.domain.analytics.services import (
        AnalyticsTransformService,
        WeatherFetchService,
    )
    from src.infrastructure.container.factories import (
        get_city_repository_port,
        get_weather_client_port,
    )

    return DetailedCityUseCase(
        city_repository=get_city_repository_port(),
        weather_fetch_service=WeatherFetchService(
            weather_client=get_weather_client_port(),
            max_workers=8,
            request_timeout=90,
            max_retries=2,
            retry_delay=3.0,
        ),
        analytics_transform_service=AnalyticsTransformService(QUERY_TYPES),
        query_types=QUERY_TYPES,
        regions=REGIONS,
    )


__all__ = ["build_analyze_multi_city_use_case", "build_detailed_city_use_case"]
