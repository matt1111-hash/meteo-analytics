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
- config_settings: GUI, Hardware, Multi-City, AppInfo classes
- config_validation: Environment checking and validation functions

Usage:
    from src.config import (
        APIConfig, DataConstants, ProjectPaths,
        ProviderConfig, UserPreferences, UsageTracker,
        GUIConfig, HardwareConfig, AppInfo
    )
"""

from __future__ import annotations

from datetime import datetime as _datetime

# API and data configuration
from .api_config import (
    APIConfig,
    APIConstants,  # Backward compatibility
    DataConstants,
    get_active_data_sources,
    validate_api_keys,
)

# GUI, Hardware, Multi-City, and Application settings
from .config_settings import AppInfo, GUIConfig, HardwareConfig, MultiCityConfig

# Validation and utility functions
from .config_validation import (
    check_environment,
    get_fallback_source_chain,
    get_optimal_data_source,
    get_source_display_name,
    validate_api_source_available,
    validate_config,
)

# Paths and directory management
from .paths_config import (
    CACHE_DB_PATH,
    CACHE_DIR,
    CLIMATE_CACHE_DIR,
    DATA_DIR,
    EXPORTS_DIR,
    LEGACY_DB_PATH,
    LOGS_DIR,
    PROJECT_ROOT,
    PROVIDER_PREFS_FILE,
    USAGE_TRACKING_FILE,
    USER_PREFS_DIR,
    WEATHER_DB_PATH,
    ensure_directories,
    get_project_info,
    validate_paths,
)

# Provider selector and user preferences
from .provider_config import (
    ProviderConfig,
    UserPreferences,
    get_resolved_provider,
    validate_provider_selection,
)

# Usage tracking
from .usage_config import UsageTracker

# Backward compatibility for tests monkeypatching datetime
datetime = _datetime


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
    "get_fallback_source_chain",

    # Backward compatibility
    "datetime"
]
