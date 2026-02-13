#!/usr/bin/env python3
"""
Port Provider - Application-level port access.

This module re-exports port factory functions at the application layer level.
Presentation layer should import from here instead of infrastructure.container
to maintain proper dependency direction in Clean Architecture.

Usage:
    from src.application.services import get_city_manager_port
    city_manager = get_city_manager_port()
"""

# Re-export from infrastructure container
# This is acceptable because application layer can depend on infrastructure
# through dependency injection patterns
from src.infrastructure.container import (
    get_anomaly_profile_port,
    get_city_manager_port,
    get_city_repository_port,
    get_weather_client_port,
)

__all__ = [
    "get_city_manager_port",
    "get_weather_client_port",
    "get_city_repository_port",
    "get_anomaly_profile_port",
]
