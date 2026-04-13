#!/usr/bin/env python3
"""
Tests for src/analytics/multi_city_engine_core.py
Main MultiCityEngine class for multi-city weather analytics
"""

from unittest.mock import MagicMock, patch

import pytest

from tests.analytics.multi_city_engine_core_support import (
    AnalyticsMetric,
    AnalyticsQuestion,
    AnalyticsResult,
    MultiCityEngine,
    QuestionType,
    RegionScope,
)

pytest_plugins = ("tests.analytics.multi_city_engine_core_support",)


class TestMultiCityEngineTransformMethods:
    """Test transform methods."""

    def test_transform_to_city_weather_result_delegates(
        self, engine: MultiCityEngine, mock_analytics_transform_service: MagicMock
    ) -> None:
        """Should delegate to analytics_transform_service."""
        mock_city_data = MagicMock()
        mock_analytics_transform_service.transform_to_city_weather_result.return_value = MagicMock()

        engine._transform_to_city_weather_result(mock_city_data, "hottest_today")

        mock_analytics_transform_service.transform_to_city_weather_result.assert_called_once_with(
            mock_city_data, "hottest_today"
        )

    def test_process_weather_results_delegates(
        self, engine: MultiCityEngine, mock_analytics_transform_service: MagicMock
    ) -> None:
        """Should delegate to analytics_transform_service."""
        mock_weather_data = [MagicMock()]
        mock_analytics_transform_service.process_weather_results.return_value = []

        engine._process_weather_results(mock_weather_data, "hottest_today")

        mock_analytics_transform_service.process_weather_results.assert_called_once_with(
            mock_weather_data, "hottest_today"
        )

    def test_calculate_statistics_delegates(
        self, engine: MultiCityEngine, mock_analytics_transform_service: MagicMock
    ) -> None:
        """Should delegate to analytics_transform_service."""
        mock_results = [MagicMock()]
        mock_analytics_transform_service.calculate_statistics_for_results_none_safe.return_value = {
            "mean": 10.0
        }

        engine._calculate_statistics_for_results_none_safe(mock_results)

        mock_analytics_transform_service.calculate_statistics_for_results_none_safe.assert_called_once_with(
            mock_results
        )

    def test_get_provider_stats_delegates(
        self, engine: MultiCityEngine, mock_analytics_transform_service: MagicMock
    ) -> None:
        """Should delegate to analytics_transform_service."""
        mock_weather_data = [MagicMock()]
        mock_analytics_transform_service.get_provider_stats.return_value = {"openmeteo": 10}

        engine._get_provider_stats(mock_weather_data)

        mock_analytics_transform_service.get_provider_stats.assert_called_once_with(
            mock_weather_data
        )


class TestMultiCityEngineFetchMethods:
    """Test fetch methods."""

    def test_fetch_weather_data_dual_api_batch_delegates(
        self, engine: MultiCityEngine, mock_weather_fetch_service: MagicMock
    ) -> None:
        """Should delegate to weather_fetch_service."""
        cities = [{"name": "Budapest"}]
        mock_weather_fetch_service.fetch_weather_data_dual_api_batch.return_value = []

        engine._fetch_weather_data_dual_api_batch(cities, "2026-02-13", "Hungary")

        mock_weather_fetch_service.fetch_weather_data_dual_api_batch.assert_called_once()

    def test_process_dual_api_batch_delegates(
        self, engine: MultiCityEngine, mock_weather_fetch_service: MagicMock
    ) -> None:
        """Should delegate to weather_fetch_service.process_dual_api_batch."""
        batch = [{"name": "Budapest"}, {"name": "Debrecen"}]
        mock_weather_fetch_service.process_dual_api_batch.return_value = []

        engine._process_dual_api_batch(batch, "2026-02-13", 0.2)

        mock_weather_fetch_service.process_dual_api_batch.assert_called_once_with(
            batch, "2026-02-13"
        )

    def test_fetch_single_city_weather_delegates(
        self, engine: MultiCityEngine, mock_weather_fetch_service: MagicMock
    ) -> None:
        """Should delegate to weather_fetch_service."""
        city = {"name": "Budapest"}
        mock_weather_fetch_service.fetch_single_city_weather_dual_api.return_value = MagicMock()

        engine._fetch_single_city_weather_dual_api(city, "2026-02-13")

        mock_weather_fetch_service.fetch_single_city_weather_dual_api.assert_called_once_with(
            city, "2026-02-13"
        )

    def test_create_empty_city_data_delegates(
        self, engine: MultiCityEngine, mock_weather_fetch_service: MagicMock
    ) -> None:
        """Should delegate to weather_fetch_service."""
        city = {"name": "Budapest"}
        mock_weather_fetch_service.create_empty_city_data.return_value = MagicMock()

        engine._create_empty_city_data(city, "Test error")

        mock_weather_fetch_service.create_empty_city_data.assert_called_once_with(
            city, "Test error"
        )


class TestMultiCityEngineCreateEmptyAnalyticsResult:
    """Test _create_empty_analytics_result method."""

    def test_creates_result_with_provided_question(self, engine: MultiCityEngine) -> None:
        """Should create result with provided question."""
        question = AnalyticsQuestion(
            question_text="Test question",
            question_type=QuestionType.WEATHER_COMPARISON,
            region_scope=RegionScope.GLOBAL,
            metric=AnalyticsMetric.TEMPERATURE_2M_MAX,
        )

        result = engine._create_empty_analytics_result(question, "Test error")

        assert result.question == question
        assert result.city_results == []
        assert result.total_cities_found == 0
        assert result.execution_time == 0.0

    def test_creates_result_with_fallback_question(self, engine: MultiCityEngine) -> None:
        """Should create fallback question when None provided."""
        result = engine._create_empty_analytics_result(None, "Test error")

        assert "Multi-city elemzés hiba" in result.question.question_text
        assert result.question.question_type == QuestionType.WEATHER_COMPARISON

    def test_returns_analytics_result_instance(self, engine: MultiCityEngine) -> None:
        """Should return AnalyticsResult instance."""
        result = engine._create_empty_analytics_result(None, "Test error")

        assert isinstance(result, AnalyticsResult)

    def test_uses_ultra_fallback_on_critical_error(self, engine: MultiCityEngine) -> None:
        """Should use ultra-fallback when first attempt fails."""
        with patch("src.analytics.multi_city_engine_core.AnalyticsQuestion") as mock_question:
            mock_question.side_effect = [
                Exception("First error"),
                MagicMock(
                    question_text="Critical error",
                    question_type=QuestionType.TEMPERATURE_MAX,
                    region_scope=RegionScope.GLOBAL,
                    metric=AnalyticsMetric.TEMPERATURE_2M_MAX,
                ),
            ]

            with patch("src.analytics.multi_city_engine_core.AnalyticsResult") as mock_result:
                mock_result.return_value = MagicMock(spec=AnalyticsResult)

                result = engine._create_empty_analytics_result(None, "Test error")

                assert result is not None

    def test_raises_runtime_error_on_total_failure(self, engine: MultiCityEngine) -> None:
        """Should raise RuntimeError when all attempts fail."""
        with patch("src.analytics.multi_city_engine_core.AnalyticsQuestion") as mock_question:
            mock_question.side_effect = Exception("Total failure")

            with pytest.raises(RuntimeError, match="Cannot create AnalyticsResult"):
                engine._create_empty_analytics_result(None, "Test error")


class TestMultiCityEngineExports:
    """Test module exports."""

    def test_all_exports_exist(self) -> None:
        """All items in __all__ should be accessible."""
        from src.analytics import multi_city_engine_core

        assert hasattr(multi_city_engine_core, "MultiCityEngine")
        assert "MultiCityEngine" in multi_city_engine_core.__all__
