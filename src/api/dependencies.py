"""FastAPI dependency injection — lifespan-managed service registry."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from fastapi import Request

if TYPE_CHECKING:
    from src.application.use_cases.analyze_multi_city import AnalyzeMultiCityUseCase
    from src.application.use_cases.calculate_trend import CalculateTrendUseCase
    from src.application.use_cases.detailed_city_use_case import DetailedCityUseCase
    from src.domain.ports import CityManagerPort, CityRepositoryPort, WeatherClientPort


@dataclass(frozen=True)
class ServiceRegistry:
    """Pre-built services shared across all requests via app.state."""

    analyze_multi_city_use_case: AnalyzeMultiCityUseCase
    detailed_city_use_case: DetailedCityUseCase
    calculate_trend_use_case: CalculateTrendUseCase
    city_manager: CityManagerPort
    city_repository: CityRepositoryPort
    weather_client: WeatherClientPort


def build_service_registry() -> ServiceRegistry:
    """Build all application services once at startup."""
    from src.application.use_cases.calculate_trend import CalculateTrendUseCase  # noqa: PLC0415
    from src.infrastructure.container.composition_root import (  # noqa: PLC0415
        build_analyze_multi_city_use_case,
        build_detailed_city_use_case,
    )
    from src.infrastructure.container.factories import (  # noqa: PLC0415
        get_city_manager_port,
        get_city_repository_port,
        get_weather_client_port,
    )

    city_manager = get_city_manager_port()
    city_repository = get_city_repository_port()
    weather_client = get_weather_client_port()

    return ServiceRegistry(
        analyze_multi_city_use_case=build_analyze_multi_city_use_case(),
        detailed_city_use_case=build_detailed_city_use_case(),
        calculate_trend_use_case=CalculateTrendUseCase(
            weather_client=weather_client,
            city_manager=city_manager,
        ),
        city_manager=city_manager,
        city_repository=city_repository,
        weather_client=weather_client,
    )


def get_services(request: Request) -> ServiceRegistry:
    """FastAPI Depends-compatible getter for the service registry."""
    return request.app.state.services


def get_analyze_multi_city_uc(request: Request) -> AnalyzeMultiCityUseCase:
    """Convenience getter: multi-city analysis use case."""
    return request.app.state.services.analyze_multi_city_use_case


def get_detailed_city_uc(request: Request) -> DetailedCityUseCase:
    """Convenience getter: detailed city analysis use case."""
    return request.app.state.services.detailed_city_use_case


def get_calculate_trend_uc(request: Request) -> CalculateTrendUseCase:
    """Convenience getter: trend calculation use case."""
    return request.app.state.services.calculate_trend_use_case


def get_city_manager(request: Request) -> CityManagerPort:
    """Convenience getter: city manager port."""
    return request.app.state.services.city_manager


def get_city_repository(request: Request) -> CityRepositoryPort:
    """Convenience getter: city repository port."""
    return request.app.state.services.city_repository


def get_weather_client(request: Request) -> WeatherClientPort:
    """Convenience getter: weather client port."""
    return request.app.state.services.weather_client
