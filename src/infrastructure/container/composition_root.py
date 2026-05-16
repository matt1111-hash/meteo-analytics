#!/usr/bin/env python3
# ruff: noqa: PLC0415
"""Composition root — single factory for use cases (non-GUI)."""

from __future__ import annotations

from typing import Any


def _fetch_config() -> Any:
    """Load weather fetch configuration (lazy to allow env var overrides at runtime)."""
    from src.config.config_settings import WeatherFetchConfig

    return WeatherFetchConfig()


def build_analyze_multi_city_use_case() -> Any:
    """Single composition root for multi-city use case."""
    from src.application.use_cases import AnalyzeMultiCityUseCase
    from src.domain.analytics.services import (
        AnalyticsTransformService,
        RegionResolverService,
        WeatherFetchService,
    )
    from src.domain.constants.query_types import QUERY_TYPES
    from src.domain.constants.regions import HUNGARIAN_REGIONAL_MAPPING, REGIONS
    from src.infrastructure.container.factories import (
        get_city_repository_port,
        get_weather_client_port,
    )

    cfg = _fetch_config()
    return AnalyzeMultiCityUseCase(
        region_resolver=RegionResolverService(),
        city_repository=get_city_repository_port(),
        weather_fetch_service=WeatherFetchService(
            weather_client=get_weather_client_port(),
            max_workers=cfg.max_workers,
            request_timeout=cfg.request_timeout,
            max_retries=cfg.max_retries,
            retry_delay=cfg.retry_delay,
        ),
        analytics_transform_service=AnalyticsTransformService(QUERY_TYPES),
        query_types=QUERY_TYPES,
        regions=REGIONS,
        hungarian_mapping=HUNGARIAN_REGIONAL_MAPPING,
    )


def build_detailed_city_use_case() -> Any:
    """Composition root for detailed single-city multi-metric use case."""
    from src.application.use_cases.detailed_city_use_case import DetailedCityUseCase
    from src.domain.analytics.services import (
        AnalyticsTransformService,
        WeatherFetchService,
    )
    from src.domain.constants.query_types import QUERY_TYPES
    from src.domain.constants.regions import REGIONS
    from src.infrastructure.container.factories import (
        get_city_repository_port,
        get_weather_client_port,
    )

    cfg = _fetch_config()
    return DetailedCityUseCase(
        city_repository=get_city_repository_port(),
        weather_fetch_service=WeatherFetchService(
            weather_client=get_weather_client_port(),
            max_workers=cfg.max_workers,
            request_timeout=cfg.request_timeout,
            max_retries=cfg.max_retries,
            retry_delay=cfg.retry_delay,
        ),
        analytics_transform_service=AnalyticsTransformService(QUERY_TYPES),
        query_types=QUERY_TYPES,
        regions=REGIONS,
    )


__all__ = [
    "build_analyze_multi_city_use_case",
    "build_detailed_city_use_case",
]
