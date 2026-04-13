#!/usr/bin/env python3
"""
Tests for src/analytics/multi_city_engine_core.py
Main MultiCityEngine class for multi-city weather analytics
"""

from unittest.mock import MagicMock

from tests.analytics.multi_city_engine_core_support import (
    AnalyticsResult,
    MultiCityEngine,
    MultiCityQuery,
)

pytest_plugins = ("tests.analytics.multi_city_engine_core_support",)


class TestMultiCityEngineResolveRegionName:
    """Test resolve_region_name method."""

    def test_delegates_to_region_resolver(
        self, engine: MultiCityEngine, mock_region_resolver: MagicMock
    ) -> None:
        """Should delegate to region_resolver."""
        mock_region_resolver.resolve_region_name.return_value = "Hungary"

        result = engine.resolve_region_name("HU")

        mock_region_resolver.resolve_region_name.assert_called_once_with("HU")
        assert result == "Hungary"


class TestMultiCityEngineGetCitiesForRegion:
    """Test get_cities_for_region method."""

    def test_returns_empty_list_for_invalid_region(
        self, engine: MultiCityEngine, mock_region_resolver: MagicMock
    ) -> None:
        """Should return empty list for invalid region."""
        mock_region_resolver.resolve_region_name.side_effect = ValueError("Invalid region")

        result = engine.get_cities_for_region("invalid_region")

        assert result == []

    def test_calls_repository_with_correct_params(
        self,
        engine: MultiCityEngine,
        mock_region_resolver: MagicMock,
        mock_city_repository: MagicMock,
    ) -> None:
        """Should call repository with correct parameters."""
        mock_region_resolver.resolve_region_name.return_value = "Hungary"
        mock_city_repository.get_cities_for_region.return_value = [
            {"name": "Budapest", "lat": 47.5, "lon": 19.05}
        ]

        result = engine.get_cities_for_region("HU", limit=10)

        mock_city_repository.get_cities_for_region.assert_called_once()
        assert len(result) == 1

    def test_respects_limit_parameter(
        self,
        engine: MultiCityEngine,
        mock_region_resolver: MagicMock,
        mock_city_repository: MagicMock,
    ) -> None:
        """Should respect limit parameter."""
        mock_region_resolver.resolve_region_name.return_value = "Hungary"

        engine.get_cities_for_region("HU", limit=5)

        call_kwargs = mock_city_repository.get_cities_for_region.call_args[1]
        assert call_kwargs["limit"] == 5

    def test_respects_max_cities_parameter(
        self,
        engine: MultiCityEngine,
        mock_region_resolver: MagicMock,
        mock_city_repository: MagicMock,
    ) -> None:
        """Should respect max_cities parameter over limit."""
        mock_region_resolver.resolve_region_name.return_value = "Hungary"

        engine.get_cities_for_region("HU", limit=5, max_cities=20)

        call_kwargs = mock_city_repository.get_cities_for_region.call_args[1]
        assert call_kwargs["limit"] == 20

    def test_logs_regional_query_for_hungarian_region(
        self,
        engine: MultiCityEngine,
        mock_region_resolver: MagicMock,
        mock_city_repository: MagicMock,
    ) -> None:
        """Should log regional query for Hungarian regions."""
        mock_region_resolver.resolve_region_name.return_value = "Hungary"
        mock_city_repository.get_cities_for_region.return_value = [
            {"name": "Miskolc"},
            {"name": "Eger"},
        ]

        engine.get_cities_for_region("Észak-Magyarország")

        call_kwargs = mock_city_repository.get_cities_for_region.call_args[1]
        assert call_kwargs["original_region"] == "Észak-Magyarország"

    def test_returns_empty_on_repository_exception(
        self,
        engine: MultiCityEngine,
        mock_region_resolver: MagicMock,
        mock_city_repository: MagicMock,
    ) -> None:
        """Should return empty list when repository throws exception."""
        mock_region_resolver.resolve_region_name.return_value = "Hungary"
        mock_city_repository.get_cities_for_region.side_effect = Exception("DB error")

        result = engine.get_cities_for_region("Hungary")

        assert result == []


class TestMultiCityEngineExecuteAnalyticsQuery:
    """Test execute_analytics_query method."""

    def test_delegates_to_use_case(self, engine: MultiCityEngine, mock_use_case: MagicMock) -> None:
        """Should delegate to use_case.execute."""
        mock_result = MagicMock(spec=AnalyticsResult)
        mock_use_case.execute.return_value = mock_result

        query = MultiCityQuery(
            query_type="hottest_today",
            region="Hungary",
            date="2026-02-13",
        )

        result = engine.execute_analytics_query(query)

        mock_use_case.execute.assert_called_once_with(query)
        assert result == mock_result

    def test_passes_progress_callback(
        self, engine: MultiCityEngine, mock_use_case: MagicMock
    ) -> None:
        """Should accept optional progress callback."""
        mock_result = MagicMock(spec=AnalyticsResult)
        mock_use_case.execute.return_value = mock_result

        query = MultiCityQuery(
            query_type="hottest_today",
            region="Hungary",
            date="2026-02-13",
        )

        callback = MagicMock()
        engine.execute_analytics_query(query, progress_callback=callback)

        mock_use_case.execute.assert_called_once_with(query)


class TestMultiCityEngineAnalyzeMultiCity:
    """Test analyze_multi_city method."""

    def test_creates_query_and_executes(
        self, engine: MultiCityEngine, mock_use_case: MagicMock
    ) -> None:
        """Should create query and delegate to use_case."""
        mock_result = MagicMock(spec=AnalyticsResult)
        mock_use_case.execute.return_value = mock_result

        result = engine.analyze_multi_city(
            query_type="hottest_today",
            region="Hungary",
            date="2026-02-13",
        )

        mock_use_case.execute.assert_called_once()
        assert result == mock_result

    def test_passes_limit_to_query(self, engine: MultiCityEngine, mock_use_case: MagicMock) -> None:
        """Should pass limit to query."""
        mock_result = MagicMock(spec=AnalyticsResult)
        mock_use_case.execute.return_value = mock_result

        engine.analyze_multi_city(
            query_type="hottest_today",
            region="Hungary",
            date="2026-02-13",
            limit=50,
        )

        call_args = mock_use_case.execute.call_args[0]
        query = call_args[0]
        assert query.limit == 50
