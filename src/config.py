#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Global Weather Analyzer - Central Configuration (Legacy Re-export)

This file provides backward compatibility by re-exporting everything
from the modular config package.

New code should import directly from src.config instead.
"""

# Re-export everything from the config package
from src.config import (
    # API and data
    APIConfig,
    DataConstants,
    APIConstants,
    validate_api_keys,
    get_active_data_sources,

    # Paths
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
    get_project_info,

    # Provider
    ProviderConfig,
    UserPreferences,
    get_resolved_provider,
    validate_provider_selection,

    # Usage
    UsageTracker,

    # GUI/Hardware
    GUIConfig,
    HardwareConfig,
    MultiCityConfig,
    AppInfo,

    # Utils
    check_environment,
    validate_config,
    get_optimal_data_source,
    get_source_display_name,
    validate_api_source_available,
    get_fallback_source_chain
)


__all__ = [
    # API and data
    'APIConfig',
    'DataConstants',
    'APIConstants',
    'validate_api_keys',
    'get_active_data_sources',

    # Paths
    'PROJECT_ROOT',
    'DATA_DIR',
    'CACHE_DIR',
    'CLIMATE_CACHE_DIR',
    'EXPORTS_DIR',
    'LOGS_DIR',
    'USER_PREFS_DIR',
    'PROVIDER_PREFS_FILE',
    'USAGE_TRACKING_FILE',
    'WEATHER_DB_PATH',
    'CACHE_DB_PATH',
    'LEGACY_DB_PATH',
    'ensure_directories',
    'validate_paths',
    'get_project_info',

    # Provider
    'ProviderConfig',
    'UserPreferences',
    'get_resolved_provider',
    'validate_provider_selection',

    # Usage
    'UsageTracker',

    # GUI/Hardware
    'GUIConfig',
    'HardwareConfig',
    'MultiCityConfig',
    'AppInfo',

    # Utils
    'check_environment',
    'validate_config',
    'get_optimal_data_source',
    'get_source_display_name',
    'validate_api_source_available',
    'get_fallback_source_chain'
]

# Initialize on import (backward compatibility)
ensure_directories()
