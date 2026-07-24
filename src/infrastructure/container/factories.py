#!/usr/bin/env python3
"""
Factory Functions for Port Implementations.

Clean Architecture compliant factory functions.
These factories create port implementations from outer layers (data/infrastructure).

IMPORTANT: These functions must be imported from infrastructure.container,
NOT from domain.ports (which only defines the abstract interfaces).

Example:
    from src.infrastructure.container import get_city_manager_port
    city_manager = get_city_manager_port()
"""

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.domain.analytics.services.trend_calculator import TrendCalculatorPort
    from src.domain.ports import (
        AnomalyProfilePort,
        CityManagerPort,
        CityRepositoryPort,
        WeatherClientPort,
        WeatherFetchPort,
    )


def get_city_manager_port() -> "CityManagerPort":
    """
    Factory function to get CityManagerPort implementation.

    Returns:
        CityManagerPort implementation from Data Layer
    """
    from src.infrastructure.city_manager.city_manager_stats import CityManagerStats  # noqa: PLC0415

    return CityManagerStats()  # type: ignore[return-value]


def get_weather_client_port() -> "WeatherClientPort":
    """
    Factory function to get WeatherClientPort implementation.

    Returns:
        WeatherClientPort implementation from Data Layer
    """
    from src.infrastructure.weather.weather_client_extensions import (  # noqa: PLC0415
        WeatherClientExtensions,
    )

    return WeatherClientExtensions()


def get_trend_calculator_port() -> "TrendCalculatorPort":
    """
    Factory function to get TrendCalculatorPort implementation.

    Returns:
        TrendCalculatorPort implementation from Infrastructure Layer
    """
    from src.infrastructure.analytics.trend_calculator import TrendCalculator  # noqa: PLC0415

    return TrendCalculator()


def get_weather_fetch_port() -> "WeatherFetchPort":
    """
    Factory function to get the WeatherFetchPort implementation.

    Builds the infrastructure-layer weather fetch orchestrator (ThreadPoolExecutor,
    retry, throttling) wired to a WeatherClientPort, configured via WeatherFetchConfig.
    Use cases receive this via the WeatherFetchPort Protocol, not the concrete class.

    Returns:
        WeatherFetchPort implementation from Infrastructure Layer
    """
    from src.config.config_settings import WeatherFetchConfig  # noqa: PLC0415
    from src.infrastructure.weather.weather_fetch_service import (  # noqa: PLC0415
        WeatherFetchService,
    )

    cfg = WeatherFetchConfig()
    return WeatherFetchService(
        weather_client=get_weather_client_port(),
        max_workers=cfg.max_workers,
        request_timeout=cfg.request_timeout,
        max_retries=cfg.max_retries,
        retry_delay=cfg.retry_delay,
    )


def get_city_repository_port(
    db_path: Path | None = None,
    hungarian_db_path: Path | None = None,
) -> "CityRepositoryPort":
    """
    Factory function to get CityRepositoryPort implementation.

    Args:
        db_path: Optional path to cities database
        hungarian_db_path: Optional path to Hungarian settlements database

    Returns:
        CityRepositoryPort implementation from Infrastructure Layer
    """
    from src.infrastructure.repositories.city_repository import CityRepository  # noqa: PLC0415

    if db_path is None:
        project_root = Path(__file__).parent.parent.parent.parent
        db_path = project_root / "data" / "cities.db"
        hungarian_db_path = project_root / "data" / "hungarian_settlements.db"

    return CityRepository(db_path, hungarian_db_path)  # type: ignore[abstract]


def get_anomaly_profile_port() -> "AnomalyProfilePort":
    """
    Factory function to get AnomalyProfilePort implementation.

    Returns:
        AnomalyProfilePort implementation from Data Layer
    """
    from src.infrastructure.anomaly_profile.manager import AnomalyProfileManager  # noqa: PLC0415

    return AnomalyProfileManager()  # type: ignore[return-value]
