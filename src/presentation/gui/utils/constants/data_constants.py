#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mypy: ignore-errors

"""
Constants - Data handling constants - fields, formats, pagination.
"""


class DataConstants:
    """Data handling constants - CLEAN DUAL-API VERSION."""

    # Open-Meteo API fields
    OPEN_METEO_DAILY_FIELDS = [
        "temperature_2m_max",
        "temperature_2m_min",
        "temperature_2m_mean",
        "precipitation_sum",
        "windspeed_10m_max",
        "winddirection_10m_dominant",
        "weathercode",
    ]

    OPEN_METEO_HOURLY_FIELDS = ["wind_gusts_10m", "windspeed_10m"]

    # Meteostat API fields
    METEOSTAT_DAILY_FIELDS = [
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
    ]

    # Processed fields with wind gusts support
    PROCESSED_DAILY_FIELDS = [
        "temperature_2m_max",
        "temperature_2m_min",
        "temperature_2m_mean",
        "precipitation_sum",
        "windspeed_10m_max",
        "wind_gusts_max",
        "winddirection_10m_dominant",
        "weathercode",
    ]

    # Export formats
    SUPPORTED_EXPORT_FORMATS = ["csv", "excel", "json", "pdf"]

    # Pagination
    DEFAULT_PAGE_SIZE = 100
    MAX_PAGE_SIZE = 1000

    # Cache settings
    CACHE_EXPIRY_HOURS = 24
    MAX_CACHE_SIZE_MB = 100

    # Dual-API data source strategy
    USE_CASE_SOURCE_MAPPING = {
        "single_city": "open-meteo",
        "multi_city": "meteostat",
        "historical_deep": "meteostat",
        "real_time": "open-meteo",
        "station_based": "meteostat",
        "interpolated": "open-meteo",
    }

    # Source priority
    DATA_SOURCE_PRIORITY = ["open-meteo", "meteostat"]

    # Source capabilities
    SOURCE_CAPABILITIES = {
        "open-meteo": {
            "historical": True,
            "real_time": True,
            "multi_city": True,
            "station_based": False,
            "cost": "free",
            "rate_limit": "10/sec",
            "wind_gusts": True,
            "rich_params": False,
        },
        "meteostat": {
            "historical": True,
            "real_time": False,
            "multi_city": True,
            "station_based": True,
            "cost": "premium",
            "rate_limit": "10k/month",
            "wind_gusts": True,
            "rich_params": True,
        },
    }
