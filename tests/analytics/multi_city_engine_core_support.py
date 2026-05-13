#!/usr/bin/env python3
"""
Tests for src/analytics/multi_city_engine_core.py
Main MultiCityEngine class for multi-city weather analytics
"""

from unittest.mock import MagicMock, patch

import pytest
from src.analytics.multi_city_engine_core import MultiCityEngine
from src.domain.analytics.models import MultiCityQuery
from src.domain.entities.analytics_models import AnalyticsQuestion, AnalyticsResult
from src.domain.value_objects.enums import AnalyticsMetric, QuestionType, RegionScope

__all__ = [
    "AnalyticsMetric",
    "AnalyticsQuestion",
    "AnalyticsResult",
    "MultiCityEngine",
    "MultiCityQuery",
    "QuestionType",
    "RegionScope",
    "engine",
    "mock_analytics_transform_service",
    "mock_city_repository",
    "mock_region_resolver",
    "mock_use_case",
    "mock_weather_client",
    "mock_weather_fetch_service",
]


@pytest.fixture
def mock_city_repository() -> MagicMock:
    """Create mock city repository."""
    repo = MagicMock()
    repo.validate_paths = MagicMock()
    repo.get_cities_for_region = MagicMock(return_value=[])
    return repo


@pytest.fixture
def mock_weather_client() -> MagicMock:
    """Create mock weather client."""
    client = MagicMock()
    return client


@pytest.fixture
def mock_region_resolver() -> MagicMock:
    """Create mock region resolver."""
    resolver = MagicMock()
    resolver.resolve_region_name = MagicMock(return_value="Hungary")
    return resolver


@pytest.fixture
def mock_weather_fetch_service() -> MagicMock:
    """Create mock weather fetch service."""
    service = MagicMock()
    service.fetch_weather_data_dual_api_batch = MagicMock(return_value=[])
    service.fetch_single_city_weather_dual_api = MagicMock(return_value=None)
    service.create_empty_city_data = MagicMock(return_value=None)
    return service


@pytest.fixture
def mock_analytics_transform_service() -> MagicMock:
    """Create mock analytics transform service."""
    service = MagicMock()
    service.transform_to_city_weather_result = MagicMock(return_value=None)
    service.process_weather_results = MagicMock(return_value=[])
    service.calculate_statistics_for_results_none_safe = MagicMock(return_value={})
    service.get_provider_stats = MagicMock(return_value={})
    service.create_empty_analytics_result = MagicMock(
        return_value=AnalyticsResult(
            question=AnalyticsQuestion(
                question_text="empty",
                question_type=QuestionType.WEATHER_COMPARISON,
                region_scope=RegionScope.GLOBAL,
                metric=AnalyticsMetric.TEMPERATURE_2M_MAX,
            ),
            city_results=[],
            total_cities_found=0,
            execution_time=0.0,
            data_sources_used=[],
        )
    )
    return service


@pytest.fixture
def mock_use_case(
    mock_city_repository: MagicMock,
    mock_analytics_transform_service: MagicMock,
) -> MagicMock:
    """Create mock use case with required attributes."""
    use_case = MagicMock()
    use_case.execute = MagicMock()
    use_case.city_repository = mock_city_repository
    use_case.analytics_transform_service = mock_analytics_transform_service
    return use_case


@pytest.fixture
def engine(
    mock_use_case: MagicMock,
    mock_region_resolver: MagicMock,
) -> MultiCityEngine:
    """Create MultiCityEngine with all mocks."""
    with (
        patch(
            "src.analytics.multi_city_engine_core.build_analyze_multi_city_use_case",
            return_value=mock_use_case,
        ),
        patch(
            "src.analytics.multi_city_engine_core.RegionResolverService",
            return_value=mock_region_resolver,
        ),
    ):
        eng = MultiCityEngine()
        return eng
