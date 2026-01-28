#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Constants - API endpoints, timeouts, rate limits.
"""

class APIConstants:
    """API constants - CLEAN DUAL-API VERSION"""

    # Open-Meteo API endpoints (FREE - Primary)
    OPEN_METEO_BASE = "https://api.open-meteo.com/v1"
    OPEN_METEO_ARCHIVE = "https://archive-api.open-meteo.com/v1/archive"
    OPEN_METEO_GEOCODING = "https://geocoding-api.open-meteo.com/v1/search"

    # Meteostat API endpoints (PREMIUM)
    METEOSTAT_BASE = "https://meteostat.p.rapidapi.com"
    METEOSTAT_STATIONS_NEARBY = f"{METEOSTAT_BASE}/stations/nearby"
    METEOSTAT_STATIONS_META = f"{METEOSTAT_BASE}/stations/meta"
    METEOSTAT_STATIONS_DAILY = f"{METEOSTAT_BASE}/stations/daily"
    METEOSTAT_POINT_DAILY = f"{METEOSTAT_BASE}/point/daily"

    # API Configuration
    DEFAULT_TIMEOUT = 30
    MAX_RETRIES = 3
    CACHE_DURATION = 3600
    USER_AGENT = "Global Weather Analyzer/2.1.0 (Dual-API Edition)"

    # Rate Limiting
    OPENMETEO_RATE_LIMIT = 0.1
    METEOSTAT_RATE_LIMIT = 0.1
    METEOSTAT_MONTHLY_LIMIT = 10000

    # Source Display Names
    SOURCE_DISPLAY_NAMES = {
        "open-meteo": "🌍 Open-Meteo API",
        "meteostat": "💎 Meteostat API"
    }
