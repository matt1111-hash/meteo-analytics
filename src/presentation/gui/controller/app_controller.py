#!/usr/bin/env python3
# mypy: ignore-errors

"""
AppController - Clean Architecture Refactor

Alkalmazás központi logikai vezérlője - refaktorált moduláris struktúrával.

A fő AppController osztály most már moduláris felépítésű,
külön handler osztályokra bontva a funkcionális területek szerint.
"""

import logging
from typing import Any

from PySide6.QtCore import QObject, Signal

from src.config import (
    DATA_DIR,
    ProviderConfig,
    UserPreferences,
    build_usage_tracker,
)

from ..workers import WorkerManager
from .analysis_handler import AnalysisHandler
from .app_controller_analysis import AppControllerAnalysisMixin
from .app_controller_lifecycle import AppControllerLifecycleMixin
from .app_controller_signals import AppControllerSignalsMixin
from .database_manager import DatabaseManager
from .geocoding_handler import GeocodingHandler
from .provider_routing import ProviderRouting
from .weather_data_handler import WeatherDataHandler


class AppController(
    AppControllerAnalysisMixin,
    AppControllerSignalsMixin,
    AppControllerLifecycleMixin,
    QObject,
):
    """
    CLEAN ARCHITECTURE CONTROLLER - Központi logikai agy (Refactored)

    A controller moduláris felépítésű:
    - DatabaseManager: Adatbázis műveletek
    - ProviderRouting: Provider selection és routing
    - GeocodingHandler: Település keresés és kiválasztás
    - WeatherDataHandler: Időjárási adat feldolgozás
    - AnalysisHandler: Analysis request kezelés és worker lifecycle

    Signalok:
        analysis_started, analysis_progress, analysis_completed, analysis_failed, analysis_cancelled
        geocoding_results_ready, weather_data_ready, error_occurred, status_updated
        city_saved_to_db, weather_saved_to_db
        provider_selected, provider_usage_updated, provider_warning, provider_fallback
        progress_updated
    """

    # === CLEAN ARCHITECTURE SIGNALS ===

    # Analysis lifecycle signalok
    analysis_started = Signal(str)  # analysis_type
    analysis_progress = Signal(str, int)  # message, percentage
    analysis_completed = Signal(dict)  # result_data
    analysis_failed = Signal(str)  # error_message
    analysis_cancelled = Signal()  # megszakítás megerősítése

    # Eredeti signalok (backwards compatibility)
    geocoding_results_ready = Signal(list)  # List[Dict] - település találatok
    weather_data_ready = Signal(dict)  # Dict - API válasz adatok
    error_occurred = Signal(str)  # str - hibaüzenet
    status_updated = Signal(str)  # str - státusz üzenet
    progress_updated = Signal(str, int)  # worker_type, progress

    # Adatbázis műveletek eredményei
    city_saved_to_db = Signal(dict)  # Dict - elmentett település adatok
    weather_saved_to_db = Signal(bool)  # bool - sikeres mentés

    # PROVIDER ROUTING SIGNALOK
    provider_selected = Signal(str)  # str - választott provider neve
    provider_usage_updated = Signal(dict)  # Dict - usage statistics
    provider_warning = Signal(str, int)  # provider_name, usage_percent
    provider_fallback = Signal(str, str)  # from_provider, to_provider

    def __init__(self, parent: QObject | None = None, gui_services: Any = None):
        """Controller inicializálása CLEAN ARCHITECTURE támogatással."""
        super().__init__(parent)

        self._logger = logging.getLogger(__name__)
        self._logger.info("🎯 AppController __init__ started (CLEAN ARCHITECTURE REFACTORED)")

        # === CLEAN ARCHITECTURE STATE ===
        self.current_city_data: dict[str, Any] | None = None
        self.current_weather_data: dict[str, Any] | None = None
        self.active_search_query: str | None = None

        # === KOMPONENSEK INICIALIZÁLÁSA ===

        if gui_services is not None:
            # DI path — services pre-built by composition root
            self.db_path = gui_services.db_path
            self.database_manager = gui_services.database_manager
            self.provider_config = gui_services.provider_config
            self.user_preferences = gui_services.user_preferences
            self.usage_tracker = gui_services.usage_tracker
            self.provider_routing = gui_services.provider_routing
            self.worker_manager = gui_services.worker_manager
            self._logger.info("✅ AppController initialized via GuiServices (DI)")
        else:
            # Legacy path — direct construction (backward compatible)
            self.db_path = DATA_DIR / "meteo_data.db"
            self.database_manager = DatabaseManager(self.db_path)
            self.provider_config = ProviderConfig()
            self.user_preferences = UserPreferences()
            self.usage_tracker = build_usage_tracker()
            self.provider_routing = ProviderRouting(
                self.provider_config, self.user_preferences, self.usage_tracker
            )
            self.worker_manager = WorkerManager()
            self._logger.info("✅ AppController initialized via direct construction")

        # 4. Geocoding Handler
        self.geocoding_handler = GeocodingHandler(self.worker_manager, self.database_manager, self)
        self._connect_geocoding_signals()
        self._logger.info("✅ GeocodingHandler initialized")

        # 5. Weather Data Handler
        self.weather_data_handler = WeatherDataHandler(self.database_manager, self)
        self._connect_weather_data_signals()
        self._logger.info("✅ WeatherDataHandler initialized")

        # 6. Analysis Handler
        self.analysis_handler = AnalysisHandler(self)
        self._connect_analysis_signals()
        self._logger.info("✅ AnalysisHandler initialized")

        # Provider preferences betöltése
        self._load_user_preferences()

        self._logger.info("✅ AppController inicializálva (CLEAN ARCHITECTURE REFACTORED)")
