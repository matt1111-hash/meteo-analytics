#!/usr/bin/env python3
# ruff: noqa: PLC0415

"""Tests for composition root factory."""

from __future__ import annotations

from unittest.mock import patch

from src.application.use_cases import AnalyzeMultiCityUseCase


def test_build_returns_analyze_multi_city_use_case() -> None:
    from src.infrastructure.container.composition_root import build_analyze_multi_city_use_case

    with (
        patch("src.infrastructure.container.factories.get_city_repository_port"),
        patch("src.infrastructure.container.factories.get_weather_client_port"),
    ):
        use_case = build_analyze_multi_city_use_case()
    assert isinstance(use_case, AnalyzeMultiCityUseCase)


def test_build_injects_region_resolver() -> None:
    from src.infrastructure.container.composition_root import build_analyze_multi_city_use_case

    with (
        patch("src.infrastructure.container.factories.get_city_repository_port"),
        patch("src.infrastructure.container.factories.get_weather_client_port"),
    ):
        use_case = build_analyze_multi_city_use_case()
    assert use_case.region_resolver is not None
