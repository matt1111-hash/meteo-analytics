#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Path configuration and directory management for the application."""

from __future__ import annotations

from pathlib import Path
from typing import Any


# Project root directory (one level up from src/)
PROJECT_ROOT: Path = Path(__file__).parent.parent.parent

# Data directories
DATA_DIR: Path = PROJECT_ROOT / "data"
CACHE_DIR: Path = DATA_DIR / "cache"
CLIMATE_CACHE_DIR: Path = DATA_DIR / "climate_cache"
EXPORTS_DIR: Path = PROJECT_ROOT / "exports"
LOGS_DIR: Path = PROJECT_ROOT / "logs"

# User preferences directory for provider selector
USER_PREFS_DIR: Path = DATA_DIR / "user_preferences"
PROVIDER_PREFS_FILE: Path = USER_PREFS_DIR / "provider_preferences.json"
USAGE_TRACKING_FILE: Path = USER_PREFS_DIR / "api_usage_tracking.json"

# Database paths
WEATHER_DB_PATH: Path = DATA_DIR / "weather.db"
CACHE_DB_PATH: Path = DATA_DIR / "cache.db"

# Legacy compatibility
LEGACY_DB_PATH: Path = PROJECT_ROOT / "legacy" / "meteo_data.db"


def ensure_directories() -> None:
    """Create all necessary directories if they don't exist."""
    directories: list[Path] = [
        DATA_DIR,
        CACHE_DIR,
        CLIMATE_CACHE_DIR,
        EXPORTS_DIR,
        LOGS_DIR,
        USER_PREFS_DIR  # Provider Selector preferences
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


def validate_paths() -> dict[str, Any]:
    """
    Validate that all necessary paths exist and are accessible.

    Returns:
        Dictionary with path validation status
    """
    status: dict[str, Any] = {
        "directories_valid": True,
        "write_permissions": True,
        "legacy_db_exists": False,
        "issues": []
    }

    try:
        # Try to create directories
        ensure_directories()

        # Test write permissions
        test_file = DATA_DIR / "test_write.tmp"
        try:
            test_file.write_text("test")
            test_file.unlink()
        except PermissionError:
            status["write_permissions"] = False
            status["issues"].append("No write permissions to data directory")

        # Check legacy database
        status["legacy_db_exists"] = LEGACY_DB_PATH.exists()

        # Check critical directories
        critical_dirs: list[Path] = [DATA_DIR, CACHE_DIR, USER_PREFS_DIR]
        for directory in critical_dirs:
            if not directory.exists() or not directory.is_dir():
                status["directories_valid"] = False
                status["issues"].append(f"Missing directory: {directory}")

    except Exception as e:
        status["directories_valid"] = False
        status["issues"].append(f"Path validation error: {e}")

    return status


def get_project_info() -> dict[str, str]:
    """
    Get basic project path information.

    Returns:
        Dictionary with project paths
    """
    return {
        "project_root": str(PROJECT_ROOT),
        "data_dir": str(DATA_DIR),
        "cache_dir": str(CACHE_DIR),
        "exports_dir": str(EXPORTS_DIR),
        "logs_dir": str(LOGS_DIR),
        "weather_db": str(WEATHER_DB_PATH),
        "cache_db": str(CACHE_DB_PATH)
    }


# Initialize directories on import
ensure_directories()
