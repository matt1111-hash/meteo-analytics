#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API Helpers Source Selector - Select optimal data source.
"""

import logging
import os
from typing import List

from ..constants import APIConstants, DataConstants

logger = logging.getLogger(__name__)


def get_optimal_data_source(use_case: str, prefer_free: bool = True) -> str:
    """
    Determine optimal data source based on use case.

    Args:
        use_case: Use case ("single_city", "multi_city", etc.)
        prefer_free: Prefer free sources

    Returns:
        Optimal data source identifier
    """
    if use_case in DataConstants.USE_CASE_SOURCE_MAPPING:
        optimal_source = DataConstants.USE_CASE_SOURCE_MAPPING[use_case]

        if prefer_free and optimal_source == "meteostat":
            if DataConstants.SOURCE_CAPABILITIES["open-meteo"].get(
                use_case.replace("_", "-"), False
            ):
                return "open-meteo"

        return optimal_source

    return "open-meteo"


def get_source_display_name(source_id: str) -> str:
    """
    Get display name for data source.

    Args:
        source_id: Source identifier

    Returns:
        User-friendly display name
    """
    return APIConstants.SOURCE_DISPLAY_NAMES.get(
        source_id, f"Unknown Source ({source_id})"
    )


def validate_api_source_available(source_id: str) -> bool:
    """
    Validate API source availability.

    Args:
        source_id: Source identifier

    Returns:
        Whether the API is available
    """
    if source_id == "open-meteo":
        return True

    elif source_id == "meteostat":
        api_key = os.getenv("METEOSTAT_API_KEY")
        return bool(api_key and len(api_key.strip()) >= 32)

    return False


def get_fallback_source_chain(primary_source: str) -> List[str]:
    """
    Determine fallback source chain.

    Args:
        primary_source: Primary source

    Returns:
        List of fallback sources
    """
    available_sources = [
        source
        for source in DataConstants.DATA_SOURCE_PRIORITY
        if validate_api_source_available(source)
    ]

    if primary_source in available_sources:
        available_sources.remove(primary_source)
        available_sources.insert(0, primary_source)

    return available_sources


def log_api_source_selection(
    use_case: str, selected_source: str, reason: str = ""
) -> None:
    """
    Log API source selection.

    Args:
        use_case: Use case
        selected_source: Selected source
        reason: Reason for selection
    """
    display_name = get_source_display_name(selected_source)
    logger.info(f"API SOURCE SELECTION: {use_case} → {display_name} {reason}")
