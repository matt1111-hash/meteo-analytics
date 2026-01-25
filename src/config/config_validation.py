#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Global Weather Analyzer - Configuration Validation
Environment checking, configuration validation, and utility functions
"""

import os
from typing import Optional

# Import from sibling modules
from .api_config import APIConfig, DataConstants, validate_api_keys
from .paths_config import (
    DATA_DIR,
    CACHE_DIR,
    USER_PREFS_DIR,
    LEGACY_DB_PATH,
    ensure_directories,
)


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


__all__ = [
    'check_environment',
    'validate_config',
    'get_optimal_data_source',
    'get_source_display_name',
    'validate_api_source_available',
    'get_fallback_source_chain'
]
