#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Global Weather Analyzer - GUI and Hardware Configuration
GUI settings, hardware optimizations, and application metadata
"""


class GUIConfig:
    """GUI appearance and behavior settings"""

    # Window settings
    DEFAULT_WINDOW_SIZE = (1200, 800)
    MIN_WINDOW_SIZE = (900, 600)

    # Chart settings
    DPI = 100
    FIGURE_SIZE = (5, 4)

    # Update intervals
    WEATHER_UPDATE_INTERVAL = 600  # 10 minutes
    WARNING_UPDATE_INTERVAL = 300  # 5 minutes

    # Provider Selector: GUI-specific settings
    PROVIDER_SELECTOR_POSITION = "control_panel"  # or "status_bar" or "both"
    SHOW_USAGE_WARNINGS = True
    SHOW_COST_ESTIMATES = True
    AUTO_FALLBACK_ON_LIMIT = True  # Automatic fallback when hitting limits


class HardwareConfig:
    """Hardware-specific optimizations"""

    # Based on user's specs: Intel i5-13400, 32GB RAM, RTX 3050 8GB
    MAX_CONCURRENT_REQUESTS = 8
    CHART_CACHE_SIZE = 50  # Number of charts to keep in memory
    DATA_CHUNK_SIZE = 10000  # Rows per processing chunk

    # GPU acceleration (for future features)
    USE_GPU_ACCELERATION = True
    GPU_MEMORY_LIMIT = 6  # GB (conservative limit for RTX 3050)


class MultiCityConfig:
    """Multi-city analytics specific settings"""

    # Meteostat API optimization for multi-city
    MAX_CITIES_PER_BATCH = 20  # Cities to process in parallel
    STATION_SEARCH_RADIUS = 50000  # 50km radius for station search
    MAX_STATION_DISTANCE = 25.0  # 25km max distance from city center

    # Rate limiting for premium API
    METEOSTAT_CONCURRENT_REQUESTS = 5  # Conservative concurrent limit
    METEOSTAT_REQUEST_DELAY = 0.1  # 100ms delay between requests

    # Fallback configuration
    ENABLE_FALLBACK_TO_OPENMETEO = True  # Fallback if Meteostat fails
    FALLBACK_THRESHOLD = 0.3  # Switch to fallback if >30% failures


class AppInfo:
    """Application information and metadata"""

    NAME = "Global Weather Analyzer"
    VERSION = "2.2.0"  # Updated for Provider Selector feature
    DESCRIPTION = "Advanced meteorological data analysis tool with user-controlled dual-API support"
    AUTHOR = "Weather Analytics Team"

    # API Architecture info
    API_ARCHITECTURE = "User-Controlled Dual-API System"
    PRIMARY_API = "Open-Meteo (Free)"
    PREMIUM_API = "Meteostat (Premium)"

    # Provider Selector info
    PROVIDER_SELECTOR_VERSION = "1.0.0"
    PROVIDER_SELECTOR_FEATURES = [
        "User-controlled API selection",
        "Real-time usage tracking",
        "Cost monitoring",
        "Smart routing logic",
        "Automatic fallback"
    ]

    # Legacy compatibility
    LEGACY_NAME = "Meteo History"
    LEGACY_VERSION = "1.0.0"


__all__ = [
    'GUIConfig',
    'HardwareConfig',
    'MultiCityConfig',
    'AppInfo'
]
