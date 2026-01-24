#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global Weather Analyzer - Configuration Module
Refactored from god class to modular architecture.

This module provides centralized configuration management split into
focused components following clean architecture principles.

Modules:
- api_config: API endpoints, data constants, validation
- paths_config: Directory paths and file management
- provider_config: Provider selector and user preferences
- usage_config: Usage tracking and monitoring

Usage:
    from src.config import (
        APIConfig, DataConstants, ProjectPaths,
        ProviderConfig, UserPreferences, UsageTracker
    )
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime as _datetime
from typing import ClassVar

# API and data configuration
from .api_config import (
    APIConfig,
    DataConstants,
    validate_api_keys,
    get_active_data_sources,
    APIConstants  # Backward compatibility
)

# Paths and directory management
from .paths_config import (
    PROJECT_ROOT,
    DATA_DIR,
    CACHE_DIR,
    CLIMATE_CACHE_DIR,
    EXPORTS_DIR,
    LOGS_DIR,
    USER_PREFS_DIR,
    PROVIDER_PREFS_FILE,
    USAGE_TRACKING_FILE,
    WEATHER_DB_PATH,
    CACHE_DB_PATH,
    LEGACY_DB_PATH,
    ensure_directories,
    validate_paths,
    get_project_info
)

# Provider selector and user preferences
from .provider_config import (
    ProviderConfig,
    UserPreferences,
    get_resolved_provider,
    validate_provider_selection
)

# Usage tracking
from .usage_config import UsageTracker

# Backward compatibility for tests monkeypatching datetime
datetime = _datetime

# GUI configuration (moved from original config.py)
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
    PROVIDER_SELECTOR_POSITION: str = "control_panel"  # or "status_bar" or "both"
    SHOW_USAGE_WARNINGS: bool = True
    SHOW_COST_ESTIMATES: bool = True
    AUTO_FALLBACK_ON_LIMIT: bool = True  # Automatic fallback when hitting limits


# Hardware configuration
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


# Multi-city configuration
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


# Application metadata
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


# Environment and validation functions
def check_environment() -> dict[str, bool | str | None]:
    """
    Check environment configuration and requirements.

    Returns:
        Environment status dictionary
    """
    env_status: dict[str, bool | str | None] = {
        "directories_created": False,
        "api_keys_valid": False,
        "write_permissions": False,
        "cache_available": False,
        "provider_selector_ready": False,
        "error": None,
    }

    try:
        ensure_directories()
        env_status["directories_created"] = True

        api_validation = validate_api_keys()
        env_status["api_keys_valid"] = api_validation["meteostat_key_valid"]

        test_file = DATA_DIR / "test_write.tmp"
        try:
            test_file.write_text("test")
            test_file.unlink()
            env_status["write_permissions"] = True
        except OSError:
            env_status["write_permissions"] = False

        env_status["cache_available"] = CACHE_DIR.exists() and CACHE_DIR.is_dir()
        env_status["provider_selector_ready"] = bool(
            env_status["directories_created"] and env_status["write_permissions"] and USER_PREFS_DIR.exists()
        )
    except Exception as exc:  # pragma: no cover - defensive guard
        env_status["error"] = str(exc)

    return env_status


def validate_config() -> dict[str, bool | str | None]:
    """
    Validate configuration and return status.

    Returns:
        Configuration validation status
    """
    status: dict[str, bool | str | None] = {
        "directories": True,
        "legacy_db": LEGACY_DB_PATH.exists(),
        "write_permissions": True,
        "api_configuration": False,
        "multi_city_ready": False,
        "provider_selector_ready": False,
        "validation_error": None,
    }

    try:
        ensure_directories()

        api_validation = validate_api_keys()
        status["api_configuration"] = api_validation["openmeteo_available"]
        status["multi_city_ready"] = bool(
            api_validation["meteostat_key_valid"] and status["api_configuration"]
        )
        status["provider_selector_ready"] = bool(
            status["directories"] and status["write_permissions"] and USER_PREFS_DIR.exists()
        )
    except PermissionError as exc:
        status["directories"] = False
        status["write_permissions"] = False
        status["provider_selector_ready"] = False
        status["validation_error"] = str(exc)
    except Exception as exc:  # pragma: no cover
        status["validation_error"] = str(exc)

    return status


# Backward compatibility utilities
def get_optimal_data_source(use_case: str, prefer_free: bool = True) -> str:
    """
    Optimális adatforrás meghatározása használati eset alapján.

    Args:
        use_case: Használati eset ("single_city", "multi_city", stb.)
        prefer_free: Ingyenes forrás preferálása

    Returns:
        Optimális data source azonosító
    """
    if use_case in DataConstants.USE_CASE_SOURCE_MAPPING:
        optimal_source = DataConstants.USE_CASE_SOURCE_MAPPING[use_case]

        # Ha ingyenes forrást preferálunk és az optimális fizetős
        if prefer_free and optimal_source == "meteostat":
            # Ellenőrizzük, hogy az open-meteo képes-e kezelni
            if DataConstants.SOURCE_CAPABILITIES["open-meteo"].get(use_case.replace("_", "-"), False):
                return "open-meteo"

        return optimal_source

    # Default fallback
    return "open-meteo"


def get_source_display_name(source_id: str) -> str:
    """
    Adatforrás megjelenítési neve.

    Args:
        source_id: Source azonosító

    Returns:
        Felhasználóbarát megjelenítési név
    """
    return APIConfig.SOURCE_DISPLAY_NAMES.get(source_id, f"Unknown Source ({source_id})")


def validate_api_source_available(source_id: str) -> bool:
    """
    API forrás elérhetőségének validálása.

    Args:
        source_id: Source azonosító

    Returns:
        Elérhető-e az API
    """
    import os

    if source_id == "open-meteo":
        return True  # Mindig elérhető (nincs API kulcs szükséges)

    elif source_id == "meteostat":
        # Environment variable ellenőrzése
        api_key = os.getenv("METEOSTAT_API_KEY")
        return bool(api_key and len(api_key.strip()) >= 32)

    return False


def get_fallback_source_chain(primary_source: str) -> list[str]:
    """
    Fallback forrás lánc meghatározása.

    Args:
        primary_source: Elsődleges forrás

    Returns:
        Fallback források listája
    """
    available_sources = [
        source for source in DataConstants.DATA_SOURCE_PRIORITY
        if validate_api_source_available(source)
    ]

    # Primary source előre helyezése
    if primary_source in available_sources:
        available_sources.remove(primary_source)
        available_sources.insert(0, primary_source)

    return available_sources


# Export all public interfaces
__all__ = [
    # API and data
    "APIConfig",
    "DataConstants",
    "APIConstants",  # Backward compatibility
    "validate_api_keys",
    "get_active_data_sources",

    # Paths
    "PROJECT_ROOT",
    "DATA_DIR",
    "CACHE_DIR",
    "CLIMATE_CACHE_DIR",
    "EXPORTS_DIR",
    "LOGS_DIR",
    "USER_PREFS_DIR",
    "PROVIDER_PREFS_FILE",
    "USAGE_TRACKING_FILE",
    "WEATHER_DB_PATH",
    "CACHE_DB_PATH",
    "LEGACY_DB_PATH",
    "ensure_directories",
    "validate_paths",
    "get_project_info",

    # Provider selector
    "ProviderConfig",
    "UserPreferences",
    "get_resolved_provider",
    "validate_provider_selection",

    # Usage tracking
    "UsageTracker",

    # GUI and hardware
    "GUIConfig",
    "HardwareConfig",
    "MultiCityConfig",
    "AppInfo",

    # Validation and utilities
    "check_environment",
    "validate_config",
    "get_optimal_data_source",
    "get_source_display_name",
    "validate_api_source_available",
    "get_fallback_source_chain"
]
