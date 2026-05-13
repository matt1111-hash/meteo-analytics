#!/usr/bin/env python3
"""
Weather Client - Multi-Provider API Integration (Legacy Export)
Global Weather Analyzer project

BACKWARD COMPATIBILITY SHIM — Re-exports from src.infrastructure.weather.*

NEW STRUCTURE (moved to infrastructure):
- weather_types.py - WeatherData dataclass, exceptions
- weather_provider_base.py - WeatherProvider abstract base class
- openmeteo_provider.py - OpenMeteoProvider class
- meteostat_provider.py - MeteostatProvider class
- weather_client_core.py - WeatherClient core class
- weather_client_extensions.py - Provider management and backward compatibility

HASZNÁLAT (Legacy - működik tovább):
from src.data.weather_client import WeatherClient, WeatherData

Javasolt új használat:
from src.infrastructure.weather.weather_client_extensions import WeatherClientExtensions
from src.infrastructure.weather.weather_types import WeatherData
"""

# Re-export providers from infrastructure
from src.infrastructure.weather.meteostat_provider import MeteostatProvider
from src.infrastructure.weather.openmeteo_provider import OpenMeteoProvider

# Also export core for those who want just the core functionality
from src.infrastructure.weather.weather_client_core import WeatherClient as WeatherClientCore

# Re-export client with extensions (default export)
from src.infrastructure.weather.weather_client_extensions import (
    WeatherClientExtensions as WeatherClient,
)

# Re-export base class
from src.infrastructure.weather.weather_provider_base import WeatherProvider
from src.infrastructure.weather.weather_types import (
    ProviderNotAvailableError,
    ProviderValidationError,
    WeatherAPIError,
    WeatherData,
)

__all__ = [
    "MeteostatProvider",
    # Providers
    "OpenMeteoProvider",
    "ProviderNotAvailableError",
    "ProviderValidationError",
    "WeatherAPIError",
    # Main client (with extensions)
    "WeatherClient",
    # Core client (without extensions)
    "WeatherClientCore",
    # Types
    "WeatherData",
    # Base class
    "WeatherProvider",
]
