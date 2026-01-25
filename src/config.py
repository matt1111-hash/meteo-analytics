#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Global Weather Analyzer - Central Configuration
Központi konfigurációs modul minden útvonal és beállítás számára

This module re-exports all configuration from focused sub-modules.
For backward compatibility, all original symbols remain available.
"""

# ============================================================================
# PATHS AND DIRECTORIES
# ============================================================================
from .config_paths import (
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
    ensure_directories
)

# ============================================================================
# API CONFIGURATION
# ============================================================================
from .config_api import (
    APIConfig,
    validate_api_keys
)

# ============================================================================
# DATA CONSTANTS
# ============================================================================
from .config_data import (
    DataConstants
)

# ============================================================================
# PROVIDER CONFIGURATION
# ============================================================================
from .config_provider import (
    ProviderConfig
)

# ============================================================================
# USER PREFERENCES AND USAGE TRACKING
# ============================================================================
from .config_usage import (
    UserPreferences,
    UsageTracker
)

# ============================================================================
# GUI AND HARDWARE CONFIGURATION
# ============================================================================
from .config_gui import (
    GUIConfig,
    HardwareConfig,
    MultiCityConfig,
    AppInfo
)

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================
from .config_utils import (
    check_environment,
    validate_config,
    get_active_data_sources,
    get_resolved_provider
)

# ============================================================================
# LEGACY COMPATIBILITY ALIASES
# ============================================================================
from .config_legacy import (
    APIConstants,
    get_optimal_data_source,
    get_source_display_name,
    validate_api_source_available,
    get_fallback_source_chain
)


__all__ = [
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

    # API
    'APIConfig',
    'validate_api_keys',

    # Data
    'DataConstants',

    # Provider
    'ProviderConfig',

    # Usage
    'UserPreferences',
    'UsageTracker',

    # GUI/Hardware
    'GUIConfig',
    'HardwareConfig',
    'MultiCityConfig',
    'AppInfo',

    # Utils
    'check_environment',
    'validate_config',
    'get_active_data_sources',
    'get_resolved_provider',

    # Legacy
    'APIConstants',
    'get_optimal_data_source',
    'get_source_display_name',
    'validate_api_source_available',
    'get_fallback_source_chain'
]


# Initialize on import (backward compatibility)
ensure_directories()
