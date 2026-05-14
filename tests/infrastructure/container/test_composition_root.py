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


def test_build_detailed_city_use_case_returns_correct_type() -> None:
    from src.application.use_cases.detailed_city_use_case import DetailedCityUseCase
    from src.infrastructure.container.composition_root import build_detailed_city_use_case

    with (
        patch("src.infrastructure.container.factories.get_city_repository_port"),
        patch("src.infrastructure.container.factories.get_weather_client_port"),
    ):
        use_case = build_detailed_city_use_case()
    assert isinstance(use_case, DetailedCityUseCase)


def test_build_detailed_city_use_case_injects_dependencies() -> None:
    from src.infrastructure.container.composition_root import build_detailed_city_use_case

    with (
        patch("src.infrastructure.container.factories.get_city_repository_port"),
        patch("src.infrastructure.container.factories.get_weather_client_port"),
    ):
        use_case = build_detailed_city_use_case()
    assert use_case._city_repo is not None
    assert use_case._fetch_service is not None
    assert use_case._transform_service is not None


def test_build_gui_services_returns_gui_services() -> None:
    from src.infrastructure.container.composition_root import GuiServices, build_gui_services

    with (
        patch("src.presentation.gui.controller.database_manager.DatabaseManager"),
        patch("src.presentation.gui.controller.provider_routing.ProviderRouting"),
        patch("src.presentation.gui.workers.WorkerManager"),
    ):
        services = build_gui_services()
    assert isinstance(services, GuiServices)
    assert services.database_manager is not None
    assert services.provider_routing is not None
    assert services.worker_manager is not None


def test_build_gui_services_wires_dependencies() -> None:
    from src.infrastructure.container.composition_root import build_gui_services

    with (
        patch("src.presentation.gui.controller.database_manager.DatabaseManager"),
        patch("src.presentation.gui.controller.provider_routing.ProviderRouting"),
        patch("src.presentation.gui.workers.WorkerManager"),
    ):
        services = build_gui_services()
    assert services.provider_config is not None
    assert services.user_preferences is not None
    assert services.usage_tracker is not None
