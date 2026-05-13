#!/usr/bin/env python3
"""
Tests for src/analytics/multi_city_engine_core.py
MultiCityEngine facade methods — analyze, execute, resolve_region, get_cities
"""

from unittest.mock import MagicMock

from src.domain.analytics.models import MultiCityQuery
from src.domain.entities.analytics_models import AnalyticsQuestion, AnalyticsResult
from src.domain.value_objects.enums import (
    AnalyticsMetric,
    QuestionType,
    RegionScope,
)

from tests.analytics.multi_city_engine_core_support import MultiCityEngine

pytest_plugins = ("tests.analytics.multi_city_engine_core_support",)


class TestMultiCityEngineAnalyzeMultiCity:
    """Test analyze_multi_city facade method."""

    def test_delegates_to_use_case_execute(
        self,
        engine: MultiCityEngine,
        mock_use_case: MagicMock,
    ) -> None:
        """Should delegate to use_case.execute and return data on success."""
        expected = MagicMock(spec=AnalyticsResult)
        uc_result = MagicMock()
        uc_result.is_success = True
        uc_result.data = expected
        mock_use_case.execute.return_value = uc_result

        result = engine.analyze_multi_city("hottest_today", "Hungary", "2026-01-01")

        mock_use_case.execute.assert_called_once()
        assert result is expected

    def test_returns_empty_result_on_failure(
        self,
        engine: MultiCityEngine,
        mock_use_case: MagicMock,
        mock_analytics_transform_service: MagicMock,
    ) -> None:
        """Should return empty result via transform service on failure."""
        uc_result = MagicMock()
        uc_result.is_success = False
        uc_result.data = None
        uc_result.error_message = "Something failed"
        mock_use_case.execute.return_value = uc_result

        mock_analytics_transform_service.create_empty_analytics_result.return_value = MagicMock(
            spec=AnalyticsResult
        )

        engine.analyze_multi_city("hottest_today", "Hungary", "2026-01-01")

        mock_analytics_transform_service.create_empty_analytics_result.assert_called_once()

    def test_passes_question_to_use_case(
        self,
        engine: MultiCityEngine,
        mock_use_case: MagicMock,
    ) -> None:
        """Should pass question to use case via MultiCityQuery."""
        question = AnalyticsQuestion(
            question_text="Test",
            question_type=QuestionType.WEATHER_COMPARISON,
            region_scope=RegionScope.GLOBAL,
            metric=AnalyticsMetric.TEMPERATURE_2M_MAX,
        )
        uc_result = MagicMock()
        uc_result.is_success = True
        uc_result.data = MagicMock(spec=AnalyticsResult)
        mock_use_case.execute.return_value = uc_result

        engine.analyze_multi_city(
            "hottest_today",
            "Hungary",
            "2026-01-01",
            question=question,
        )

        call_args = mock_use_case.execute.call_args[0][0]
        assert isinstance(call_args, MultiCityQuery)
        assert call_args.question is question


class TestMultiCityEngineExecuteAnalyticsQuery:
    """Test execute_analytics_query facade method."""

    def test_delegates_to_use_case_execute(
        self,
        engine: MultiCityEngine,
        mock_use_case: MagicMock,
    ) -> None:
        """Should delegate to use_case.execute."""
        expected = MagicMock(spec=AnalyticsResult)
        uc_result = MagicMock()
        uc_result.is_success = True
        uc_result.data = expected
        mock_use_case.execute.return_value = uc_result

        query = MultiCityQuery(
            query_type="hottest_today",
            region="Hungary",
            date="2026-01-01",
            limit=None,
            question=None,
            max_cities=None,
        )
        result = engine.execute_analytics_query(query)

        mock_use_case.execute.assert_called_once_with(query)
        assert result is expected

    def test_returns_empty_result_on_failure(
        self,
        engine: MultiCityEngine,
        mock_use_case: MagicMock,
        mock_analytics_transform_service: MagicMock,
    ) -> None:
        """Should return empty result on use case failure."""
        uc_result = MagicMock()
        uc_result.is_success = False
        uc_result.data = None
        uc_result.error_message = "Error"
        mock_use_case.execute.return_value = uc_result

        mock_analytics_transform_service.create_empty_analytics_result.return_value = MagicMock(
            spec=AnalyticsResult
        )

        query = MultiCityQuery(
            query_type="hottest_today",
            region="Hungary",
            date="2026-01-01",
            limit=None,
            question=None,
            max_cities=None,
        )
        engine.execute_analytics_query(query)

        mock_analytics_transform_service.create_empty_analytics_result.assert_called_once()


class TestMultiCityEngineResolveRegionName:
    """Test resolve_region_name delegation."""

    def test_delegates_to_region_resolver(
        self,
        engine: MultiCityEngine,
        mock_region_resolver: MagicMock,
    ) -> None:
        """Should delegate to region_resolver.resolve_region_name."""
        mock_region_resolver.resolve_region_name.return_value = "Hungary"

        result = engine.resolve_region_name("Magyarorszag")

        mock_region_resolver.resolve_region_name.assert_called_once_with("Magyarorszag")
        assert result == "Hungary"


class TestMultiCityEngineGetCitiesForRegion:
    """Test get_cities_for_region."""

    def test_calls_city_repository(
        self,
        engine: MultiCityEngine,
        mock_city_repository: MagicMock,
    ) -> None:
        """Should call city_repository.get_cities_for_region."""
        mock_city_repository.get_cities_for_region.return_value = [
            {"name": "Budapest"},
        ]

        result = engine.get_cities_for_region("Hungary")

        assert len(result) == 1
        assert result[0]["name"] == "Budapest"

    def test_returns_empty_list_on_exception(
        self,
        engine: MultiCityEngine,
        mock_city_repository: MagicMock,
    ) -> None:
        """Should return empty list when repository raises."""
        mock_city_repository.get_cities_for_region.side_effect = Exception("DB error")

        result = engine.get_cities_for_region("InvalidRegion")

        assert result == []


class TestMultiCityEngineExports:
    """Test module exports."""

    def test_all_exports_exist(self) -> None:
        """All items in __all__ should be accessible."""
        from src.analytics import multi_city_engine_core  # noqa: PLC0415

        assert hasattr(multi_city_engine_core, "MultiCityEngine")
        assert "MultiCityEngine" in multi_city_engine_core.__all__
