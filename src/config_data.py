#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Global Weather Analyzer - Data Constants
Data field definitions and source capabilities
"""

from typing import Any, Dict, List


class DataConstants:
    """Adatkezelés konstansai - CLEAN DUAL-API VERZIÓ"""

    # API válasz mezők - Open-Meteo
    OPEN_METEO_DAILY_FIELDS = [
        "temperature_2m_max",
        "temperature_2m_min",
        "temperature_2m_mean",  # ÚJ: átlag hőmérséklet
        "precipitation_sum",
        "windspeed_10m_max",
        "winddirection_10m_dominant",  # ÚJ: szélirány
        "weathercode"
    ]

    # WIND GUSTS mezők hozzáadása
    OPEN_METEO_HOURLY_FIELDS = [
        "wind_gusts_10m",        # ÚJ: óránkénti széllökések
        "windspeed_10m"          # ÚJ: óránkénti szélsebesség
    ]

    # Meteostat API mezők
    METEOSTAT_DAILY_FIELDS = [
        "tavg",  # Átlag hőmérséklet
        "tmin",  # Min hőmérséklet
        "tmax",  # Max hőmérséklet
        "prcp",  # Csapadék
        "snow",  # Hó
        "wdir",  # Szélirány
        "wspd",  # Szélsebesség
        "wpgt",  # Széllökés (KRITIKUS MEZŐ!)
        "pres",  # Légnyomás
        "tsun"   # Napsütés
    ]

    # Processed mezők wind gusts támogatással
    PROCESSED_DAILY_FIELDS = [
        "temperature_2m_max",
        "temperature_2m_min",
        "temperature_2m_mean",
        "precipitation_sum",
        "windspeed_10m_max",      # Backward compatibility
        "wind_gusts_max",         # ÚJ: napi maximum széllökések
        "winddirection_10m_dominant",
        "weathercode"
    ]

    # Export formátumok
    SUPPORTED_EXPORT_FORMATS = ["csv", "excel", "json", "pdf"]

    # Pagination
    DEFAULT_PAGE_SIZE = 100
    MAX_PAGE_SIZE = 1000

    # Cache beállítások
    CACHE_EXPIRY_HOURS = 24
    MAX_CACHE_SIZE_MB = 100

    # === ÚJ: DUAL-API ADATFORRÁS STRATÉGIA ===

    # Primary data source selection based on use case
    USE_CASE_SOURCE_MAPPING = {
        "single_city": "open-meteo",     # Free tier for single city
        "multi_city": "meteostat",       # Premium tier for multi-city
        "historical_deep": "meteostat",  # Rich historical data
        "real_time": "open-meteo",       # Real-time weather
        "station_based": "meteostat",    # Station-based accuracy
        "interpolated": "open-meteo"     # Grid-based interpolation
    }

    # Source priority order (fallback chain)
    DATA_SOURCE_PRIORITY = [
        "open-meteo",    # Elsődleges: Open-Meteo API (ingyenes)
        "meteostat"      # Másodlagos: Meteostat API (prémium backup)
    ]

    # Source capabilities matrix
    SOURCE_CAPABILITIES = {
        "open-meteo": {
            "historical": True,
            "real_time": True,
            "multi_city": True,
            "station_based": False,
            "cost": "free",
            "rate_limit": "10/sec",
            "wind_gusts": True,
            "rich_params": False
        },
        "meteostat": {
            "historical": True,
            "real_time": False,
            "multi_city": True,
            "station_based": True,
            "cost": "premium",
            "rate_limit": "10k/month",
            "wind_gusts": True,
            "rich_params": True  # pressure, sunshine, etc.
        }
    }


__all__ = ['DataConstants']
