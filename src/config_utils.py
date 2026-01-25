#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Global Weather Analyzer - Configuration Utilities
Helper functions for configuration management
"""

from typing import Any, Dict

from .config_paths import (
    DATA_DIR, CACHE_DIR, USER_PREFS_DIR, LEGACY_DB_PATH,
    ensure_directories
)
from .config_api import validate_api_keys


def check_environment() -> Dict[str, Any]:
    """
    Check environment configuration and requirements

    Returns:
        Environment status dictionary
    """
    env_status = {
        "directories_created": False,
        "api_keys_valid": False,
        "write_permissions": False,
        "cache_available": False,
        "provider_selector_ready": False
    }

    try:
        # Check directories
        ensure_directories()
        env_status["directories_created"] = True

        # Check API keys
        api_validation = validate_api_keys()
        env_status["api_keys_valid"] = api_validation["meteostat_key_valid"]

        # Check write permissions
        test_file = DATA_DIR / "test_write.tmp"
        try:
            test_file.write_text("test")
            test_file.unlink()
            env_status["write_permissions"] = True
        except Exception:
            pass

        # Check cache availability
        env_status["cache_available"] = CACHE_DIR.exists() and CACHE_DIR.is_dir()

        # Check Provider Selector readiness
        env_status["provider_selector_ready"] = (
            env_status["directories_created"] and
            env_status["write_permissions"] and
            USER_PREFS_DIR.exists()
        )

    except Exception as e:
        env_status["error"] = str(e)

    return env_status


def validate_config() -> Dict[str, Any]:
    """Validate configuration and return status"""
    status = {
        "directories": True,
        "legacy_db": LEGACY_DB_PATH.exists(),
        "write_permissions": True,
        "api_configuration": False,
        "multi_city_ready": False,
        "provider_selector_ready": False
    }

    try:
        ensure_directories()

        # API configuration validation
        api_validation = validate_api_keys()
        status["api_configuration"] = api_validation["openmeteo_available"]

        # Multi-city readiness check
        status["multi_city_ready"] = (
            api_validation["meteostat_key_valid"] and
            status["api_configuration"]
        )

        # Provider Selector readiness check
        status["provider_selector_ready"] = (
            status["directories"] and
            status["write_permissions"] and
            USER_PREFS_DIR.exists()
        )

    except PermissionError:
        status["directories"] = False
        status["write_permissions"] = False
        status["provider_selector_ready"] = False
    except Exception as e:
        status["validation_error"] = str(e)

    return status


def get_active_data_sources() -> Dict[str, Dict[str, Any]]:
    """
    Get information about active data sources

    Returns:
        Dictionary with data source information
    """
    from .config_api import APIConfig

    sources = {
        "open-meteo": {
            "name": "Open-Meteo API",
            "type": "free",
            "status": "active",
            "use_cases": ["single-city", "basic-historical", "real-time"],
            "rate_limit": "10 requests/second",
            "cost": "Free"
        }
    }

    # Add Meteostat if API key is available
    api_validation = validate_api_keys()
    if api_validation["meteostat_key_valid"]:
        sources["meteostat"] = {
            "name": "Meteostat API",
            "type": "premium",
            "status": "active",
            "use_cases": ["multi-city", "rich-historical", "station-based"],
            "rate_limit": f"{APIConfig.METEOSTAT_MONTHLY_LIMIT} requests/month",
            "cost": "$10 USD/month"
        }
    else:
        sources["meteostat"] = {
            "name": "Meteostat API",
            "type": "premium",
            "status": "inactive - API key required",
            "use_cases": ["multi-city", "rich-historical", "station-based"],
            "rate_limit": "10000 requests/month",
            "cost": "$10 USD/month"
        }

    return sources


def get_resolved_provider(use_case: str, user_override: str = None) -> str:
    """
    Get resolved provider for specific use case

    Args:
        use_case: Use case ("single_city", "multi_city", "historical_deep", "real_time")
        user_override: User's provider preference override

    Returns:
        Resolved provider name
    """
    from .config_usage import UserPreferences
    from .config_provider import ProviderConfig

    # User override has highest priority
    if user_override and user_override != "auto":
        return user_override

    # Get user's selected provider
    selected_provider = UserPreferences.get_selected_provider()

    if selected_provider == "auto":
        # Use smart routing
        routing = ProviderConfig.PROVIDERS["auto"]["routing_logic"]
        return routing.get(use_case, "open-meteo")
    else:
        # Use user's fixed selection
        return selected_provider


__all__ = [
    'check_environment',
    'validate_config',
    'get_active_data_sources',
    'get_resolved_provider'
]
