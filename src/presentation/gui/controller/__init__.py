#!/usr/bin/env python3
# mypy: ignore-errors

"""
AppController Module - Clean Architecture Refactor

Ez a modul tartalmazza az alkalmazás központi vezérlő logikáját,
szétbontva funkcionális területek szerint.

Modul struktúra:
- app_controller: Fő controller osztály
- analysis_handler: Analysis request kezelés
- provider_routing: Provider kiválasztás és routing
- geocoding_handler: Geocoding és keresési logika
- weather_data_handler: Időjárási adat feldolgozás
- database_manager: Adatbázis műveletek
"""

from .analysis_handler import AnalysisHandler
from .app_controller import AppController
from .database_manager import DatabaseManager
from .geocoding_handler import GeocodingHandler
from .provider_routing import ProviderRouting
from .weather_data_handler import WeatherDataHandler

__all__ = [
    "AnalysisHandler",
    "AppController",
    "DatabaseManager",
    "GeocodingHandler",
    "ProviderRouting",
    "WeatherDataHandler",
]
