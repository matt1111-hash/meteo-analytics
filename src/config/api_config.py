#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""API endpoints and configuration for weather data providers."""

from __future__ import annotations

import os
from types import MappingProxyType
from typing import Any, ClassVar, Dict, Mapping


class APIConfig:
    """API endpoints and configuration - CLEAN DUAL-API SYSTEM."""

    OPEN_METEO_BASE: ClassVar[str] = "https://api.open-meteo.com/v1"
    OPEN_METEO_ARCHIVE: ClassVar[str] = "https://archive-api.open-meteo.com/v1/archive"
    OPEN_METEO_GEOCODING: ClassVar[str] = "https://geocoding-api.open-meteo.com/v1/search"

    METEOSTAT_BASE: ClassVar[str] = "https://meteostat.p.rapidapi.com"
    METEOSTAT_API_KEY: ClassVar[str | None] = os.getenv("METEOSTAT_API_KEY")
    METEOSTAT_MONTHLY_LIMIT: ClassVar[int] = 10000
    METEOSTAT_RATE_LIMIT: ClassVar[float] = 0.1

    REQUEST_TIMEOUT: ClassVar[int] = 30
    MAX_RETRIES: ClassVar[int] = 3
    CACHE_DURATION: ClassVar[int] = 3600

    SINGLE_CITY_SOURCE: ClassVar[str] = "open-meteo"
    MULTI_CITY_SOURCE: ClassVar[str] = "meteostat"
    HISTORICAL_SOURCE: ClassVar[str] = "meteostat"

    OPENMETEO_RATE_LIMIT: ClassVar[float] = 0.1
    METEOSTAT_MONTHLY_LIMIT_RATE: ClassVar[int] = METEOSTAT_MONTHLY_LIMIT

    SOURCE_DISPLAY_NAMES: ClassVar[Mapping[str, str]] = MappingProxyType(
        {
            "open-meteo": "🌍 Open-Meteo API",
            "meteostat": "💎 Meteostat API",
        }
    )

    USER_AGENT: ClassVar[str] = "Global Weather Analyzer/2.2.0 (Provider-Selector Edition)"


class DataConstants:
    """Data handling constants for dual-API system."""

    OPEN_METEO_DAILY_FIELDS: ClassVar[tuple[str, ...]] = (
        "temperature_2m_max",
        "temperature_2m_min",
        "temperature_2m_mean",
        "precipitation_sum",
        "windspeed_10m_max",
        "winddirection_10m_dominant",
        "weathercode",
    )

    OPEN_METEO_HOURLY_FIELDS: ClassVar[tuple[str, ...]] = (
        "wind_gusts_10m",
        "windspeed_10m",
    )

    METEOSTAT_DAILY_FIELDS: ClassVar[tuple[str, ...]] = (
        "tavg",
        "tmin",
        "tmax",
        "prcp",
        "snow",
        "wdir",
        "wspd",
        "wpgt",
        "pres",
        "tsun",
    )

    PROCESSED_DAILY_FIELDS: ClassVar[tuple[str, ...]] = (
        "temperature_2m_max",
        "temperature_2m_min",
        "temperature_2m_mean",
        "precipitation_sum",
        "windspeed_10m_max",
        "wind_gusts_max",
        "winddirection_10m_dominant",
        "weathercode",
    )

    SUPPORTED_EXPORT_FORMATS: ClassVar[tuple[str, ...]] = ("csv", "excel", "json", "pdf")

    DEFAULT_PAGE_SIZE: ClassVar[int] = 100
    MAX_PAGE_SIZE: ClassVar[int] = 1000

    CACHE_EXPIRY_HOURS: ClassVar[int] = 24
    MAX_CACHE_SIZE_MB: ClassVar[int] = 100

    USE_CASE_SOURCE_MAPPING: ClassVar[Mapping[str, str]] = MappingProxyType(
        {
            "single_city": "open-meteo",
            "multi_city": "meteostat",
            "historical_deep": "meteostat",
            "real_time": "open-meteo",
            "station_based": "meteostat",
            "interpolated": "open-meteo",
        }
    )

    DATA_SOURCE_PRIORITY: ClassVar[tuple[str, ...]] = ("open-meteo", "meteostat")

    SOURCE_CAPABILITIES: ClassVar[Mapping[str, Mapping[str, Any]]] = MappingProxyType(
        {
            "open-meteo": MappingProxyType(
                {
                    "historical": True,
                    "real_time": True,
                    "multi_city": True,
                    "station_based": False,
                    "cost": "free",
                    "rate_limit": "10/sec",
                    "wind_gusts": True,
                    "rich_params": False,
                }
            ),
            "meteostat": MappingProxyType(
                {
                    "historical": True,
                    "real_time": False,
                    "multi_city": True,
                    "station_based": True,
                    "cost": "premium",
                    "rate_limit": "10k/month",
                    "wind_gusts": True,
                    "rich_params": True,
                }
            ),
        }
    )


def validate_api_keys() -> Dict[str, bool]:
    """
    Validate required API keys and configuration.

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


def get_active_data_sources() -> Dict[str, Dict[str, Any]]:
    """
    Get information about active data sources.

    Returns:
        Dictionary with data source information
    """
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


# Backward compatibility alias
APIConstants = APIConfig
