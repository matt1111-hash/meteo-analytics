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
    return service


@pytest.fixture
def mock_use_case() -> MagicMock:
    """Create mock use case."""
    use_case = MagicMock()
    use_case.execute = MagicMock()
    return use_case


@pytest.fixture
def engine(
    mock_city_repository: MagicMock,
    mock_weather_client: MagicMock,
    mock_region_resolver: MagicMock,
    mock_weather_fetch_service: MagicMock,
    mock_analytics_transform_service: MagicMock,
    mock_use_case: MagicMock,
) -> MultiCityEngine:
    """Create MultiCityEngine with all mocks."""
    with (
        patch(
            "src.analytics.multi_city_engine_core.get_city_repository_port",
            return_value=mock_city_repository,
        ),
        patch(
            "src.analytics.multi_city_engine_core.get_weather_client_port",
            return_value=mock_weather_client,
        ),
        patch(
            "src.analytics.multi_city_engine_core.RegionResolverService",
            return_value=mock_region_resolver,
        ),
        patch(
            "src.analytics.multi_city_engine_core.WeatherFetchService",
            return_value=mock_weather_fetch_service,
        ),
        patch(
            "src.analytics.multi_city_engine_core.AnalyticsTransformService",
            return_value=mock_analytics_transform_service,
        ),
        patch(
            "src.analytics.multi_city_engine_core.AnalyzeMultiCityUseCase",
            return_value=mock_use_case,
        ),
    ):
        engine = MultiCityEngine(city_repository=mock_city_repository)
        engine.region_resolver = mock_region_resolver
        engine.weather_fetch_service = mock_weather_fetch_service
        engine.analytics_transform_service = mock_analytics_transform_service
        engine.use_case = mock_use_case
        return engine


class TestMultiCityEngineInit:
    """Test MultiCityEngine initialization."""

    def test_initializes_with_default_paths(self, mock_city_repository: MagicMock) -> None:
        """Should initialize with default database paths."""
        with (
            patch(
                "src.analytics.multi_city_engine_core.get_city_repository_port",
                return_value=mock_city_repository,
            ),
            patch(
                "src.analytics.multi_city_engine_core.get_weather_client_port",
                return_value=MagicMock(),
            ),
            patch("src.analytics.multi_city_engine_core.RegionResolverService"),
            patch("src.analytics.multi_city_engine_core.WeatherFetchService"),
            patch("src.analytics.multi_city_engine_core.AnalyticsTransformService"),
            patch("src.analytics.multi_city_engine_core.AnalyzeMultiCityUseCase"),
        ):
            engine = MultiCityEngine(city_repository=mock_city_repository)

            assert engine.db_path.name == "cities.db"
            assert engine.hungarian_db_path.name == "hungarian_settlements.db"

    def test_initializes_with_custom_paths(self, mock_city_repository: MagicMock) -> None:
        """Should accept custom database paths."""
        with (
            patch(
                "src.analytics.multi_city_engine_core.get_city_repository_port",
                return_value=mock_city_repository,
            ),
            patch(
                "src.analytics.multi_city_engine_core.get_weather_client_port",
                return_value=MagicMock(),
            ),
            patch("src.analytics.multi_city_engine_core.RegionResolverService"),
            patch("src.analytics.multi_city_engine_core.WeatherFetchService"),
            patch("src.analytics.multi_city_engine_core.AnalyticsTransformService"),
            patch("src.analytics.multi_city_engine_core.AnalyzeMultiCityUseCase"),
        ):
            engine = MultiCityEngine(
                db_path="/custom/cities.db",
                hungarian_db_path="/custom/hungarian.db",
                city_repository=mock_city_repository,
            )

            assert str(engine.db_path) == "/custom/cities.db"
            assert str(engine.hungarian_db_path) == "/custom/hungarian.db"

    def test_initializes_default_configuration(self, mock_city_repository: MagicMock) -> None:
        """Should have default configuration values."""
        with (
            patch(
                "src.analytics.multi_city_engine_core.get_city_repository_port",
                return_value=mock_city_repository,
            ),
            patch(
                "src.analytics.multi_city_engine_core.get_weather_client_port",
                return_value=MagicMock(),
            ),
            patch("src.analytics.multi_city_engine_core.RegionResolverService"),
            patch("src.analytics.multi_city_engine_core.WeatherFetchService"),
            patch("src.analytics.multi_city_engine_core.AnalyticsTransformService"),
            patch("src.analytics.multi_city_engine_core.AnalyzeMultiCityUseCase"),
        ):
            engine = MultiCityEngine(city_repository=mock_city_repository)

            assert engine.max_workers == 8
            assert engine.request_timeout == 90
            assert engine.max_retries == 2
            assert engine.retry_delay == 3.0

    def test_handles_weather_client_import_error(self, mock_city_repository: MagicMock) -> None:
        """Should handle ImportError when weather client is not available."""
        with (
            patch(
                "src.analytics.multi_city_engine_core.get_city_repository_port",
                return_value=mock_city_repository,
            ),
            patch(
                "src.analytics.multi_city_engine_core.get_weather_client_port",
                side_effect=ImportError("No module"),
            ),
            patch("src.analytics.multi_city_engine_core.RegionResolverService"),
            patch("src.analytics.multi_city_engine_core.WeatherFetchService"),
            patch("src.analytics.multi_city_engine_core.AnalyticsTransformService"),
            patch("src.analytics.multi_city_engine_core.AnalyzeMultiCityUseCase"),
        ):
            engine = MultiCityEngine(city_repository=mock_city_repository)

            assert engine.weather_client is None


class TestMultiCityEngineQueryTypes:
    """Test QUERY_TYPES configuration."""

    def test_query_types_exist(self) -> None:
        """QUERY_TYPES should be defined."""
        assert hasattr(MultiCityEngine, "QUERY_TYPES")
        assert isinstance(MultiCityEngine.QUERY_TYPES, dict)

    def test_query_types_has_required_entries(self) -> None:
        """QUERY_TYPES should have all required query types."""
        required_types = [
            "hottest_today",
            "coldest_today",
            "temperature_mean",
            "wettest_today",
            "windiest_today",
            "wind_gusts",
            "temperature_range",
        ]
        for qt in required_types:
            assert qt in MultiCityEngine.QUERY_TYPES, f"Missing query type: {qt}"

    def test_query_types_have_required_fields(self) -> None:
        """Each query type should have required fields."""
        required_fields = ["name", "metric", "unit", "sort_desc", "question_template", "metric_enum"]
        for qt_name, qt_config in MultiCityEngine.QUERY_TYPES.items():
            for field in required_fields:
                assert field in qt_config, f"Missing field {field} in {qt_name}"

    def test_hottest_today_config(self) -> None:
        """hottest_today should have correct configuration."""
        config = MultiCityEngine.QUERY_TYPES["hottest_today"]
        assert config["name"] == "Legmelegebb ma"
        assert config["metric"] == "temperature_2m_max"
        assert config["unit"] == "°C"
        assert config["sort_desc"] is True
        assert config["metric_enum"] == AnalyticsMetric.TEMPERATURE_2M_MAX

    def test_coldest_today_config(self) -> None:
        """coldest_today should have correct configuration."""
        config = MultiCityEngine.QUERY_TYPES["coldest_today"]
        assert config["name"] == "Leghidegebb ma"
        assert config["metric"] == "temperature_2m_min"
        assert config["sort_desc"] is False

    def test_wettest_today_config(self) -> None:
        """wettest_today should have correct configuration."""
        config = MultiCityEngine.QUERY_TYPES["wettest_today"]
        assert config["name"] == "Legcsapadékosabb ma"
        assert config["metric"] == "precipitation_sum"
        assert config["unit"] == "mm"

    def test_windiest_today_config(self) -> None:
        """windiest_today should have correct configuration."""
        config = MultiCityEngine.QUERY_TYPES["windiest_today"]
        assert config["name"] == "Legszelesebb ma"
        assert config["metric"] == "windspeed_10m_max"
        assert config["unit"] == "km/h"


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
        assert call_kwargs["limit"] == 20  # max_cities takes priority

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

        # Verify it was called with Hungarian region
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

    def test_passes_limit_to_query(
        self, engine: MultiCityEngine, mock_use_case: MagicMock
    ) -> None:
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


class TestMultiCityEngineTransformMethods:
    """Test transform methods."""

    def test_transform_to_city_weather_result_delegates(
        self, engine: MultiCityEngine, mock_analytics_transform_service: MagicMock
    ) -> None:
        """Should delegate to analytics_transform_service."""
        mock_city_data = MagicMock()
        mock_analytics_transform_service.transform_to_city_weather_result.return_value = (
            MagicMock()
        )

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
        with patch(
            "src.analytics.multi_city_engine_core.AnalyticsQuestion"
        ) as mock_question:
            # First call raises exception, second call succeeds
            mock_question.side_effect = [
                Exception("First error"),
                MagicMock(
                    question_text="Critical error",
                    question_type=QuestionType.TEMPERATURE_MAX,
                    region_scope=RegionScope.GLOBAL,
                    metric=AnalyticsMetric.TEMPERATURE_2M_MAX,
                ),
            ]

            with patch(
                "src.analytics.multi_city_engine_core.AnalyticsResult"
            ) as mock_result:
                mock_result.return_value = MagicMock(spec=AnalyticsResult)

                result = engine._create_empty_analytics_result(None, "Test error")

                assert result is not None

    def test_raises_runtime_error_on_total_failure(self, engine: MultiCityEngine) -> None:
        """Should raise RuntimeError when all attempts fail."""
        with patch(
            "src.analytics.multi_city_engine_core.AnalyticsQuestion"
        ) as mock_question:
            # All calls raise exception
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
