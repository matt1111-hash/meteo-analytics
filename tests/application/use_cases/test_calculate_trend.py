"""Tests for the trend calculation use case."""

from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock

import pytest
from src.application.commands.trend_command import TrendAnalysisCommand
from src.application.use_cases.calculate_trend import CalculateTrendUseCase
from src.domain.entities.trend_result import TrendAnalysisResult
from src.domain.value_objects.enums import AnalyticsMetric


def test_execute_uses_injected_dependencies() -> None:
    """Execute should use injected ports instead of infrastructure factories."""
    weather_client = MagicMock()
    weather_client.get_weather_data.return_value = [
        {"date": "2024-01-01", "temperature_2m_max": 10.0}
    ]
    city_manager = MagicMock()
    city_manager.find_city_by_name.return_value = (47.4979, 19.0402)
    trend_calculator = MagicMock()
    expected_result = TrendAnalysisResult(
        location_name="Budapest",
        metric=AnalyticsMetric.TEMPERATURE_2M_MAX,
        periods=[],
    )
    trend_calculator.calculate_multiple_periods.return_value = expected_result
    use_case = CalculateTrendUseCase(
        weather_client=weather_client,
        city_manager=city_manager,
        trend_calculator=trend_calculator,
    )
    command = TrendAnalysisCommand(
        location="Budapest",
        metric="temperature_2m_max",
        time_periods=[5],
        start_date="2024-01-01",
        end_date="2024-12-31",
    )

    result = use_case.execute(command)

    city_manager.find_city_by_name.assert_called_once_with("Budapest")
    weather_client.get_weather_data.assert_called()
    trend_calculator.calculate_multiple_periods.assert_called_once()
    assert result is expected_result


def test_execute_raises_for_unknown_location() -> None:
    """Execute should fail fast when city lookup returns no coordinates."""
    use_case = CalculateTrendUseCase(
        weather_client=MagicMock(),
        city_manager=MagicMock(find_city_by_name=MagicMock(return_value=None)),
    )
    command = TrendAnalysisCommand(
        location="Unknown", metric="temperature_2m_max", time_periods=[5]
    )

    with pytest.raises(ValueError, match="Location not found: Unknown"):
        use_case.execute(command)


def test_execute_returns_empty_result_when_weather_data_missing() -> None:
    """Execute should return an empty result when no weather rows are fetched."""
    weather_client = MagicMock()
    weather_client.get_weather_data.return_value = []
    city_manager = MagicMock(find_city_by_name=MagicMock(return_value=(47.4979, 19.0402)))
    use_case = CalculateTrendUseCase(
        weather_client=weather_client,
        city_manager=city_manager,
    )
    command = TrendAnalysisCommand(
        location="Budapest", metric="temperature_2m_max", time_periods=[5]
    )

    result = use_case.execute(command)

    assert result.location_name == "Budapest"
    assert result.periods == []
    assert result.total_data_points == 0


def test_get_coordinates_returns_none_on_city_manager_error() -> None:
    """City manager failures should be converted to missing coordinates."""
    use_case = CalculateTrendUseCase(
        weather_client=MagicMock(),
        city_manager=MagicMock(find_city_by_name=MagicMock(side_effect=RuntimeError("boom"))),
    )

    assert use_case._get_coordinates("Budapest") is None


def test_parse_date_returns_none_for_invalid_input() -> None:
    """Invalid date strings should not raise from the use case helper."""
    use_case = CalculateTrendUseCase(
        weather_client=MagicMock(),
        city_manager=MagicMock(),
    )

    assert use_case._parse_date("2026-99-99") is None


def test_fetch_weather_data_flattens_tuple_batches_and_skips_failed_batch() -> None:
    """Batch fetching should accept tuple payloads and continue after errors."""
    weather_client = MagicMock()
    weather_client.get_weather_data.side_effect = [
        ([{"date": "2025-01-01", "temperature_2m_max": 10.0}], {"meta": "ok"}),
        RuntimeError("temporary failure"),
    ]
    use_case = CalculateTrendUseCase(
        weather_client=weather_client,
        city_manager=MagicMock(),
    )

    result = use_case._fetch_weather_data(
        lat=47.5,
        lon=19.0,
        start_date=datetime(2025, 1, 1),
        end_date=datetime(2026, 2, 1),
    )

    assert result == [{"date": "2025-01-01", "temperature_2m_max": 10.0}]
