"""Additional regression tests for the multi-city engine core."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from src.analytics.multi_city_engine_core import MultiCityEngine


def test_init_uses_repository_factory_when_repository_not_injected() -> None:
    """Engine should obtain the repository via the infrastructure factory."""
    mock_repository = MagicMock()
    mock_repository.validate_paths = MagicMock()

    with (
        patch(
            "src.analytics.multi_city_engine_core.get_city_repository_port",
            return_value=mock_repository,
        ) as repository_factory,
        patch(
            "src.analytics.multi_city_engine_core.get_weather_client_port",
            return_value=MagicMock(),
        ),
        patch("src.analytics.multi_city_engine_core.RegionResolverService"),
        patch("src.analytics.multi_city_engine_core.WeatherFetchService"),
        patch("src.analytics.multi_city_engine_core.AnalyticsTransformService"),
        patch("src.analytics.multi_city_engine_core.AnalyzeMultiCityUseCase"),
    ):
        engine = MultiCityEngine()

    repository_factory.assert_called_once_with()
    mock_repository.validate_paths.assert_called_once_with()
    assert engine.city_repository is mock_repository


def test_init_wires_weather_client_into_fetch_service() -> None:
    """Engine should pass the resolved weather client to the fetch service."""
    mock_repository = MagicMock(validate_paths=MagicMock())
    mock_weather_client = MagicMock()

    with (
        patch(
            "src.analytics.multi_city_engine_core.get_city_repository_port",
            return_value=mock_repository,
        ),
        patch(
            "src.analytics.multi_city_engine_core.get_weather_client_port",
            return_value=mock_weather_client,
        ),
        patch("src.analytics.multi_city_engine_core.RegionResolverService"),
        patch("src.analytics.multi_city_engine_core.AnalyticsTransformService"),
        patch("src.analytics.multi_city_engine_core.AnalyzeMultiCityUseCase"),
        patch("src.analytics.multi_city_engine_core.WeatherFetchService") as fetch_service,
    ):
        MultiCityEngine()

    fetch_service.assert_called_once()
    assert fetch_service.call_args.kwargs["weather_client"] is mock_weather_client
