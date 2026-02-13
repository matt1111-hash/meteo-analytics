#!/usr/bin/env python3
"""
Infrastructure Container - Dependency Injection Container.

This module provides factory functions for creating port implementations.
Following Clean Architecture, these factories are in the infrastructure layer
because they create instances of outer layer (data) implementations.

Usage:
    from src.infrastructure.container import (
        get_city_manager_port,
        get_weather_client_port,
        get_city_repository_port,
        get_anomaly_profile_port,
    )

    # Get a city manager instance
    city_manager = get_city_manager_port()

Migration Guide:
    OLD: from src.domain.ports import get_city_manager_port
    NEW: from src.infrastructure.container import get_city_manager_port
"""

from .factories import (
    get_anomaly_profile_port,
    get_city_manager_port,
    get_city_repository_port,
    get_weather_client_port,
)

__all__ = [
    "get_anomaly_profile_port",
    "get_city_manager_port",
    "get_city_repository_port",
    "get_weather_client_port",
]
