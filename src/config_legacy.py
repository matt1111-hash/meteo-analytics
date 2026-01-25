#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Global Weather Analyzer - Legacy Compatibility Aliases
Backward compatibility for utils.py and other legacy code
"""

import os
from typing import List

from .config_api import APIConfig
from .config_data import DataConstants


# Alias for APIConstants (used by utils.py)
APIConstants = APIConfig


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
    return APIConstants.SOURCE_DISPLAY_NAMES.get(source_id, f"Unknown Source ({source_id})")


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


def get_fallback_source_chain(primary_source: str) -> List[str]:
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
    'APIConstants',
    'get_optimal_data_source',
    'get_source_display_name',
    'validate_api_source_available',
    'get_fallback_source_chain'
]
