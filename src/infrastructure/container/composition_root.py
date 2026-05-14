#!/usr/bin/env python3
# ruff: noqa: PLC0415
"""Composition root — single factory for use cases and GUI services."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class GuiServices:
    """Pre-wired services for the GUI layer."""

    db_path: Path
    database_manager: Any
    provider_routing: Any
    worker_manager: Any
    provider_config: Any = field(default=None, repr=False)
    user_preferences: Any = field(default=None, repr=False)
    usage_tracker: Any = field(default=None, repr=False)


def build_gui_services() -> GuiServices:
    """Build all GUI services with their dependencies wired up."""
    from src.config import DATA_DIR, ProviderConfig, UserPreferences, build_usage_tracker
    from src.presentation.gui.controller.database_manager import DatabaseManager
    from src.presentation.gui.controller.provider_routing import ProviderRouting
    from src.presentation.gui.workers import WorkerManager

    db_path = DATA_DIR / "meteo_data.db"
    provider_config = ProviderConfig()
    user_preferences = UserPreferences()
    usage_tracker = build_usage_tracker()

    return GuiServices(
        db_path=db_path,
        database_manager=DatabaseManager(db_path),
        provider_config=provider_config,
        user_preferences=user_preferences,
        usage_tracker=usage_tracker,
        provider_routing=ProviderRouting(provider_config, user_preferences, usage_tracker),
        worker_manager=WorkerManager(),
    )


def _fetch_config():
    """Load weather fetch configuration (lazy to allow env var overrides at runtime)."""
    from src.config.config_settings import WeatherFetchConfig

    return WeatherFetchConfig()


def build_analyze_multi_city_use_case():
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


def build_detailed_city_use_case():
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
    "GuiServices",
    "build_analyze_multi_city_use_case",
    "build_detailed_city_use_case",
    "build_gui_services",
]
