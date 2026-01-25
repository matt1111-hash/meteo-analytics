#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Global Weather Analyzer - API Configuration
API endpoints, timeouts, and data source settings
"""

import os
from typing import Any, Dict, List


class APIConfig:
    """API endpoints and configuration - CLEAN DUAL-API SYSTEM"""

    # Open-Meteo API (primary global data source - FREE)
    OPEN_METEO_BASE = "https://api.open-meteo.com/v1"
    OPEN_METEO_ARCHIVE = "https://archive-api.open-meteo.com/v1/archive"
    OPEN_METEO_GEOCODING = "https://geocoding-api.open-meteo.com/v1/search"

    # Meteostat API (premium multi-city & historical data - 10k requests/month)
    METEOSTAT_BASE = "https://meteostat.p.rapidapi.com"
    METEOSTAT_API_KEY = os.getenv("METEOSTAT_API_KEY")
    METEOSTAT_MONTHLY_LIMIT = 10000  # 10k requests/month ($10 USD)
    METEOSTAT_RATE_LIMIT = 0.1  # 100ms minimum between requests

    # Request configuration
    REQUEST_TIMEOUT = 30  # seconds
    MAX_RETRIES = 3
    CACHE_DURATION = 3600  # 1 hour in seconds

    # Data source priority for different use cases
    SINGLE_CITY_SOURCE = "open-meteo"  # Free tier for single city queries
    MULTI_CITY_SOURCE = "meteostat"    # Premium tier for multi-city analytics
    HISTORICAL_SOURCE = "meteostat"    # Premium tier for rich historical data

    # Timeouts and settings
    DEFAULT_TIMEOUT = 30  # másodperc
    USER_AGENT = "Global Weather Analyzer/2.2.0 (Provider-Selector Edition)"

    # Rate Limiting Configuration
    OPENMETEO_RATE_LIMIT = 0.1  # 10 requests/second
    METEOSTAT_RATE_LIMIT = 0.1  # 100ms delay for premium API
    METEOSTAT_MONTHLY_LIMIT = 10000  # 10k requests/month

    # Source Display Names
    SOURCE_DISPLAY_NAMES = {
        "open-meteo": "🌍 Open-Meteo API",
        "meteostat": "💎 Meteostat API"
    }


def validate_api_keys() -> Dict[str, bool]:
    """
    Validate required API keys and configuration

    Returns:
        Dictionary with validation results
    """
    validation = {
        "meteostat_key_present": bool(APIConfig.METEOSTAT_API_KEY),
        "meteostat_key_valid": False,
        "openmeteo_available": True  # Open-Meteo doesn't require API key
    }

    # Meteostat API key validation
    if APIConfig.METEOSTAT_API_KEY:
        # Basic validation - check if it's not empty and has reasonable length
        key = APIConfig.METEOSTAT_API_KEY.strip()
        if len(key) >= 32:  # RapidAPI keys are typically 32+ characters
            validation["meteostat_key_valid"] = True

    return validation


__all__ = [
    'APIConfig',
    'validate_api_keys'
]
