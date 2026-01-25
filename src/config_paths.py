#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Global Weather Analyzer - Path Configuration
Base paths and directory structure
"""

from pathlib import Path

# Project root directory (one level up from src/)
PROJECT_ROOT = Path(__file__).parent.parent

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
CACHE_DIR = DATA_DIR / "cache"
CLIMATE_CACHE_DIR = DATA_DIR / "climate_cache"
EXPORTS_DIR = PROJECT_ROOT / "exports"
LOGS_DIR = PROJECT_ROOT / "logs"

# Provider Selector: User preferences directory
USER_PREFS_DIR = DATA_DIR / "user_preferences"
PROVIDER_PREFS_FILE = USER_PREFS_DIR / "provider_preferences.json"
USAGE_TRACKING_FILE = USER_PREFS_DIR / "api_usage_tracking.json"

# Database paths
WEATHER_DB_PATH = DATA_DIR / "weather.db"
CACHE_DB_PATH = DATA_DIR / "cache.db"

# Legacy compatibility
LEGACY_DB_PATH = PROJECT_ROOT / "legacy" / "meteo_data.db"


def ensure_directories():
    """Create all necessary directories if they don't exist"""
    directories = [
        DATA_DIR,
        CACHE_DIR,
        CLIMATE_CACHE_DIR,
        EXPORTS_DIR,
        LOGS_DIR,
        USER_PREFS_DIR
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


__all__ = [
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
    'ensure_directories'
]
