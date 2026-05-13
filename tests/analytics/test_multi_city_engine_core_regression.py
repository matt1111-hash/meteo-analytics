"""Additional regression tests for the multi-city engine core."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from src.analytics.multi_city_engine_core import MultiCityEngine


def test_facade_delegates_to_build_use_case() -> None:
    """When no use_case is injected, the facade should call build_analyze_multi_city_use_case."""
    mock_use_case = MagicMock()
    mock_use_case.city_repository = MagicMock()
    mock_use_case.analytics_transform_service = MagicMock()

    with (
        patch(
            "src.analytics.multi_city_engine_core.build_analyze_multi_city_use_case",
            return_value=mock_use_case,
        ) as build_fn,
        patch("src.analytics.multi_city_engine_core.RegionResolverService"),
    ):
        engine = MultiCityEngine()

    build_fn.assert_called_once()
    assert engine.use_case is mock_use_case
    assert engine.city_repository is mock_use_case.city_repository


def test_facade_uses_injected_use_case_when_provided() -> None:
    """When use_case is injected, the facade should NOT call build_analyze_multi_city_use_case."""
    mock_use_case = MagicMock()
    mock_use_case.city_repository = MagicMock()
    mock_use_case.analytics_transform_service = MagicMock()

    with (
        patch(
            "src.analytics.multi_city_engine_core.build_analyze_multi_city_use_case",
        ) as build_fn,
        patch("src.analytics.multi_city_engine_core.RegionResolverService"),
    ):
        engine = MultiCityEngine(use_case=mock_use_case)

    build_fn.assert_not_called()
    assert engine.use_case is mock_use_case


def test_facade_prefers_explicit_repo_over_use_case_repo() -> None:
    """Explicit city_repository should override use_case.city_repository."""
    mock_use_case = MagicMock()
    mock_use_case.city_repository = MagicMock()
    explicit_repo = MagicMock()
    mock_use_case.analytics_transform_service = MagicMock()

    with patch("src.analytics.multi_city_engine_core.RegionResolverService"):
        engine = MultiCityEngine(
            use_case=mock_use_case,
            city_repository=explicit_repo,
        )

    assert engine.city_repository is explicit_repo
    assert engine.city_repository is not mock_use_case.city_repository


def test_facade_exposes_transform_service_from_use_case() -> None:
    """analytics_transform_service should come from the use case."""
    mock_transform = MagicMock()
    mock_use_case = MagicMock()
    mock_use_case.city_repository = MagicMock()
    mock_use_case.analytics_transform_service = mock_transform

    with patch("src.analytics.multi_city_engine_core.RegionResolverService"):
        engine = MultiCityEngine(use_case=mock_use_case)

    assert engine.analytics_transform_service is mock_transform
