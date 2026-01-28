#!/usr/bin/env python3
"""
Weather Client - Multi-Provider API Integration (Legacy Export)
Global Weather Analyzer project

This file now re-exports from the refactored modules for backward compatibility.

NEW STRUCTURE:
- weather_types.py - WeatherData dataclass, exceptions
- weather_provider_base.py - WeatherProvider abstract base class
- openmeteo_provider.py - OpenMeteoProvider class
- meteostat_provider.py - MeteostatProvider class
- weather_client_core.py - WeatherClient core class
- weather_client_extensions.py - Provider management and backward compatibility
- weather_test.py - Test code

HASZNÁLAT (Legacy - működik tovább):
from src.data.weather_client import WeatherClient, WeatherData

Javasolt új használat:
from src.data.weather_client_extensions import WeatherClientExtensions as WeatherClient
from src.data.weather_types import WeatherData
"""

# Re-export types
from src.data.meteostat_provider import MeteostatProvider

# Re-export providers
from src.data.openmeteo_provider import OpenMeteoProvider

# Also export core for those who want just the core functionality
from src.data.weather_client_core import WeatherClient as WeatherClientCore

# Re-export client with extensions (default export)
from src.data.weather_client_extensions import WeatherClientExtensions as WeatherClient

# Re-export base class
from src.data.weather_provider_base import WeatherProvider
from src.data.weather_types import (
    ProviderNotAvailableError,
    ProviderValidationError,
    WeatherAPIError,
    WeatherData,
)

__all__ = [
    # Types
    'WeatherData',
    'WeatherAPIError',
    'ProviderNotAvailableError',
    'ProviderValidationError',

    # Base class
    'WeatherProvider',

    # Providers
    'OpenMeteoProvider',
    'MeteostatProvider',

    # Main client (with extensions)
    'WeatherClient',

    # Core client (without extensions)
    'WeatherClientCore'
]
