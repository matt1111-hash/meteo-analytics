#!/usr/bin/env python3
"""
Global Weather Analyzer - Central Configuration (Legacy Re-export)

This file provides backward compatibility by re-exporting everything
from the modular config package.

New code should import directly from src.config instead.
"""

# Re-export everything from the config package
from src.config import (
    CACHE_DB_PATH,
    CACHE_DIR,
    CLIMATE_CACHE_DIR,
    DATA_DIR,
    EXPORTS_DIR,
    LEGACY_DB_PATH,
    LOGS_DIR,
    # Paths
    PROJECT_ROOT,
    PROVIDER_PREFS_FILE,
    USAGE_TRACKING_FILE,
    USER_PREFS_DIR,
    WEATHER_DB_PATH,
    # API and data
    APIConfig,
    APIConstants,
    AppInfo,
    DataConstants,
    # GUI/Hardware
    GUIConfig,
    HardwareConfig,
    MultiCityConfig,
    # Provider
    ProviderConfig,
    # Usage
    UsageTracker,
    UserPreferences,
    # Utils
    check_environment,
    ensure_directories,
    get_active_data_sources,
    get_fallback_source_chain,
    get_optimal_data_source,
    get_project_info,
    get_resolved_provider,
    get_source_display_name,
    validate_api_keys,
    validate_api_source_available,
    validate_config,
    validate_paths,
    validate_provider_selection,
)

__all__ = [
    "CACHE_DB_PATH",
    "CACHE_DIR",
    "CLIMATE_CACHE_DIR",
    "DATA_DIR",
    "EXPORTS_DIR",
    "LEGACY_DB_PATH",
    "LOGS_DIR",
    # Paths
    "PROJECT_ROOT",
    "PROVIDER_PREFS_FILE",
    "USAGE_TRACKING_FILE",
    "USER_PREFS_DIR",
    "WEATHER_DB_PATH",
    # API and data
    "APIConfig",
    "APIConstants",
    "AppInfo",
    "DataConstants",
    # GUI/Hardware
    "GUIConfig",
    "HardwareConfig",
    "MultiCityConfig",
    # Provider
    "ProviderConfig",
    # Usage
    "UsageTracker",
    "UserPreferences",
    # Utils
    "check_environment",
    "ensure_directories",
    "get_active_data_sources",
    "get_fallback_source_chain",
    "get_optimal_data_source",
    "get_project_info",
    "get_resolved_provider",
    "get_source_display_name",
    "validate_api_keys",
    "validate_api_source_available",
    "validate_config",
    "validate_paths",
    "validate_provider_selection",
]

# Initialize on import (backward compatibility)
ensure_directories()
