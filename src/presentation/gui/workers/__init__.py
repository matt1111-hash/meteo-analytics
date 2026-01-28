#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Workers Module - Background Threads Module (Refactored)

Háttérszálak és aszinkron munkák modulja - szétbontva.

Modul struktúra:
- base_worker: BaseWorkerThread base class
- geocoding_worker: Geocoding API worker
- weather_data_worker: Weather data API worker
- sql_query_worker: SQL query worker
- worker_manager: WorkerManager central class
"""

from .base_worker import BaseWorkerThread
from .geocoding_worker import GeocodingWorker
from .sql_query_worker import SQLQueryWorker
from .weather_data_worker import WeatherDataWorker
from .worker_manager import WorkerManager

# Utility functions re-export
from .worker_utils import (
    calculate_date_range_days,
    create_comprehensive_worker_manager,
    create_weather_worker_with_provider,
    format_api_error,
    get_worker_manager_provider_summary,
    validate_coordinates,
    validate_date_string,
)

__all__ = [
    "BaseWorkerThread",
    "GeocodingWorker",
    "WeatherDataWorker",
    "SQLQueryWorker",
    "WorkerManager",
    # Utility functions
    "validate_coordinates",
    "validate_date_string",
    "calculate_date_range_days",
    "format_api_error",
    "create_weather_worker_with_provider",
    "get_worker_manager_provider_summary",
    "create_comprehensive_worker_manager",
]
