#!/usr/bin/env python3
"""
Global Weather Analyzer - Configuration Settings
GUI, Hardware, Multi-City and Application metadata configuration
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class GUIConfig:
    """GUI appearance and behavior settings."""

    # Window settings
    DEFAULT_WINDOW_SIZE: tuple[int, int] = (1200, 800)
    MIN_WINDOW_SIZE: tuple[int, int] = (900, 600)

    # Chart settings
    DPI: int = 100
    FIGURE_SIZE: tuple[int, int] = (5, 4)

    # Update intervals
    WEATHER_UPDATE_INTERVAL: int = 600  # 10 minutes
    WARNING_UPDATE_INTERVAL: int = 300  # 5 minutes

    # Provider selector GUI settings
    PROVIDER_SELECTOR_POSITION: str = "control_panel"
    SHOW_USAGE_WARNINGS: bool = True
    SHOW_COST_ESTIMATES: bool = True
    AUTO_FALLBACK_ON_LIMIT: bool = True


@dataclass(frozen=True)
class HardwareConfig:
    """Hardware-specific optimizations."""

    # Based on user's specs: Intel i5-13400, 32GB RAM, RTX 3050 8GB
    MAX_CONCURRENT_REQUESTS: int = 8
    CHART_CACHE_SIZE: int = 50  # Number of charts to keep in memory
    DATA_CHUNK_SIZE: int = 10000  # Rows per processing chunk

    # GPU acceleration (for future features)
    USE_GPU_ACCELERATION: bool = True
    GPU_MEMORY_LIMIT: int = 6  # GB (conservative limit for RTX 3050)


@dataclass(frozen=True)
class MultiCityConfig:
    """Multi-city analytics specific settings."""

    # Meteostat API optimization for multi-city
    MAX_CITIES_PER_BATCH: int = 20  # Cities to process in parallel
    STATION_SEARCH_RADIUS: int = 50000  # 50km radius for station search
    MAX_STATION_DISTANCE: float = 25.0  # 25km max distance from city center

    # Rate limiting for premium API
    METEOSTAT_CONCURRENT_REQUESTS: int = 5  # Conservative concurrent limit
    METEOSTAT_REQUEST_DELAY: float = 0.1  # 100ms delay between requests

    # Fallback configuration
    ENABLE_FALLBACK_TO_OPENMETEO: bool = True  # Fallback if Meteostat fails
    FALLBACK_THRESHOLD: float = 0.3  # Switch to fallback if >30% failures


@dataclass(frozen=True)
class AppInfo:
    """Application information and metadata."""

    NAME: str = "Global Weather Analyzer"
    VERSION: str = "2.2.0"  # Updated for Provider Selector feature
    DESCRIPTION: str = (
        "Advanced meteorological data analysis tool with user-controlled dual-API support"
    )
    AUTHOR: str = "Weather Analytics Team"

    API_ARCHITECTURE: str = "User-Controlled Dual-API System"
    PRIMARY_API: str = "Open-Meteo (Free)"
    PREMIUM_API: str = "Meteostat (Premium)"

    PROVIDER_SELECTOR_VERSION: str = "1.0.0"
    PROVIDER_SELECTOR_FEATURES: ClassVar[tuple[str, ...]] = (
        "User-controlled API selection",
        "Real-time usage tracking",
        "Cost monitoring",
        "Smart routing logic",
        "Automatic fallback",
    )

    LEGACY_NAME: str = "Meteo History"
    LEGACY_VERSION: str = "1.0.0"


__all__ = ["AppInfo", "GUIConfig", "HardwareConfig", "MultiCityConfig"]
