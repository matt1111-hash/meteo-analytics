#!/usr/bin/env python3
# mypy: ignore-errors
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
    from src.domain.ports import (
        AnomalyProfilePort,
        CityManagerPort,
        CityRepositoryPort,
        WeatherClientPort,
    )


def get_city_manager_port() -> "CityManagerPort":
    """
    Factory function to get CityManagerPort implementation.

    Returns:
        CityManagerPort implementation from Data Layer
    """
    from src.data.city_manager_stats import CityManagerStats

    return CityManagerStats()


def get_weather_client_port() -> "WeatherClientPort":
    """
    Factory function to get WeatherClientPort implementation.

    Returns:
        WeatherClientPort implementation from Data Layer
    """
    from src.data.weather_client_extensions import WeatherClientExtensions

    return WeatherClientExtensions()


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
    from src.infrastructure.repositories.city_repository import CityRepository

    if db_path is None:
        project_root = Path(__file__).parent.parent.parent.parent
        db_path = project_root / "data" / "cities.db"
        hungarian_db_path = project_root / "data" / "hungarian_settlements.db"

    return CityRepository(db_path, hungarian_db_path)


def get_anomaly_profile_port() -> "AnomalyProfilePort":
    """
    Factory function to get AnomalyProfilePort implementation.

    Returns:
        AnomalyProfilePort implementation from Data Layer
    """
    from src.data.anomaly_profile.manager import AnomalyProfileManager

    return AnomalyProfileManager()
