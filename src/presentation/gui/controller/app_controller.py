#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AppController - Clean Architecture Refactor

Alkalmazás központi logikai vezérlője - refaktorált moduláris struktúrával.

A fő AppController osztály most már moduláris felépítésű,
külön handler osztályokra bontva a funkcionális területek szerint.
"""

import logging
from typing import Any, Dict, Optional

from PySide6.QtCore import QObject, Signal, Slot

from src.config import (
    DATA_DIR,
    ProviderConfig,
    UsageTracker,
    UserPreferences,
)

from ..workers import WorkerManager
from ..workers.analysis_worker import AnalysisWorker
from .analysis_handler import AnalysisHandler
from .database_manager import DatabaseManager
from .geocoding_handler import GeocodingHandler
from .provider_routing import ProviderRouting
from .weather_data_handler import WeatherDataHandler


class AppController(QObject):
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
    analysis_started = Signal(str)              # analysis_type
    analysis_progress = Signal(str, int)        # message, percentage
    analysis_completed = Signal(dict)           # result_data
    analysis_failed = Signal(str)               # error_message
    analysis_cancelled = Signal()               # megszakítás megerősítése

    # Eredeti signalok (backwards compatibility)
    geocoding_results_ready = Signal(list)      # List[Dict] - település találatok
    weather_data_ready = Signal(dict)           # Dict - API válasz adatok
    error_occurred = Signal(str)                # str - hibaüzenet
    status_updated = Signal(str)                # str - státusz üzenet
    progress_updated = Signal(str, int)         # worker_type, progress

    # Adatbázis műveletek eredményei
    city_saved_to_db = Signal(dict)             # Dict - elmentett település adatok
    weather_saved_to_db = Signal(bool)          # bool - sikeres mentés

    # PROVIDER ROUTING SIGNALOK
    provider_selected = Signal(str)             # str - választott provider neve
    provider_usage_updated = Signal(dict)       # Dict - usage statistics
    provider_warning = Signal(str, int)         # provider_name, usage_percent
    provider_fallback = Signal(str, str)        # from_provider, to_provider

    def __init__(self, parent: Optional[QObject] = None):
        """Controller inicializálása CLEAN ARCHITECTURE támogatással."""
        super().__init__(parent)

        self._logger = logging.getLogger(__name__)
        self._logger.info("🎯 AppController __init__ started (CLEAN ARCHITECTURE REFACTORED)")

        # === CLEAN ARCHITECTURE STATE ===
        self.current_city_data: Optional[Dict[str, Any]] = None
        self.current_weather_data: Optional[Dict[str, Any]] = None
        self.active_search_query: Optional[str] = None

        # === KOMPONENSEK INICIALIZÁLÁSA ===

        # 1. Database Manager
        self.db_path = DATA_DIR / "meteo_data.db"
        self.database_manager = DatabaseManager(self.db_path)
        self._logger.info("✅ DatabaseManager initialized")

        # 2. Provider Routing
        self.provider_config = ProviderConfig()
        self.user_preferences = UserPreferences()
        self.usage_tracker = UsageTracker()
        self.provider_routing = ProviderRouting(
            self.provider_config, self.user_preferences, self.usage_tracker
        )
        self._logger.info("✅ ProviderRouting initialized")

        # 3. Worker Manager
        self.worker_manager = WorkerManager()
        self._logger.info("✅ WorkerManager created")

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

    def _connect_geocoding_signals(self) -> None:
        """Geocoding handler signaljainak bekötése."""
        self.geocoding_handler.geocoding_results_ready.connect(self.geocoding_results_ready)
        self.geocoding_handler.city_saved_to_db.connect(self.city_saved_to_db)
        self.geocoding_handler.error_occurred.connect(self.error_occurred)
        self.geocoding_handler.status_updated.connect(self.status_updated)

    def _connect_weather_data_signals(self) -> None:
        """Weather data handler signaljainak bekötése."""
        self.weather_data_handler.weather_data_ready.connect(self.weather_data_ready)
        self.weather_data_handler.weather_saved_to_db.connect(self.weather_saved_to_db)
        self.weather_data_handler.error_occurred.connect(self.error_occurred)
        self.weather_data_handler.status_updated.connect(self.status_updated)

    def _connect_analysis_signals(self) -> None:
        """Analysis handler signaljainak bekötése."""
        self.analysis_handler.analysis_started.connect(self.analysis_started)
        self.analysis_handler.analysis_progress.connect(self.analysis_progress)
        self.analysis_handler.analysis_completed.connect(self._on_analysis_completed_forward)
        self.analysis_handler.analysis_failed.connect(self.analysis_failed)
        self.analysis_handler.analysis_cancelled.connect(self.analysis_cancelled)
        self.analysis_handler.status_updated.connect(self.status_updated)

        # Worker manager signal bekötése
        self.worker_manager.weather_data_completed.connect(self.weather_data_handler.on_weather_data_completed)
        self.worker_manager.error_occurred.connect(self.error_occurred)
        self.worker_manager.progress_updated.connect(self.progress_updated.emit)

    # === 🎯 KÖZPONTI ANALYSIS REQUEST HANDLER ===

    @Slot(dict)
    def handle_analysis_request(self, request_data: Dict[str, Any]) -> None:
        """
        Központi elemzési kérés kezelő.

        Args:
            request_data: Teljes elemzési kérés minden paraméterre
        """
        print("=" * 80)
        print("🚨 DEBUG: AppController.handle_analysis_request() MEGHÍVVA!")
        print(f"🚨 DEBUG: Request data: {request_data}")
        print(f"🚨 DEBUG: Analysis type: {request_data.get('analysis_type', 'unknown')}")
        print("=" * 80)

        def start_analysis_callback(enhanced_request, handler):
            """Callback az analysis worker elindításához."""
            print("=" * 80)
            print("🚨 DEBUG: start_analysis_callback() MEGHÍVVA!")
            print(f"🚨 DEBUG: enhanced_request={enhanced_request}")
            print("=" * 80)

            worker = AnalysisWorker(parent=self)
            handler.set_active_worker(worker)

            # Signal bekötések
            worker.progress_updated.connect(handler.on_analysis_progress)
            worker.analysis_completed.connect(handler.on_analysis_completed)
            worker.analysis_failed.connect(handler.on_analysis_failed)
            worker.analysis_cancelled.connect(handler.on_analysis_cancelled)

            print("🚨 DEBUG: worker.start_analysis() HÍVÁS ELŐTT")
            result = worker.start_analysis(enhanced_request)
            print(f"🚨 DEBUG: worker.start_analysis() VISSZATÉRT: result={result}")
            return result

        print("🚨 DEBUG: analysis_handler.handle_analysis_request() HÍVÁS ELŐTT")
        self.analysis_handler.handle_analysis_request(
            request_data, self.provider_routing, start_analysis_callback
        )
        print("🚨 DEBUG: analysis_handler.handle_analysis_request() VISSZATÉRT")

    @Slot(dict)
    def _on_analysis_completed_forward(self, result_data: dict):
        """Analysis befejezésének továbbítása."""
        print("=" * 80)
        print("🚨 DEBUG: AppController._on_analysis_completed_forward() ELEJE")
        print(f"🚨 DEBUG: result_data keys: {list(result_data.keys())}")
        print("=" * 80)

        analysis_type = self.analysis_handler.analysis_state.get('analysis_type', 'unknown')

        # 🚨 KRITIKUS FIX: Az analysis_completed signal ELMUST, hogy elérjen a MainWindow-ig!
        self.analysis_completed.emit(result_data)

        # Típus-specifikus eredmény továbbítás (backwards compatibility)
        if analysis_type == 'single_location':
            self.weather_data_ready.emit(result_data)
        elif analysis_type in ['multi_city', 'county_analysis']:
            # Multi-city eredmény kezelése
            pass

    # === ANALYSIS CONTROL METHODS ===

    def stop_current_analysis(self) -> None:
        """AKTUÁLIS ANALYSIS LEÁLLÍTÁSA"""
        self.analysis_handler.stop_current_analysis()

    def is_analysis_running(self) -> bool:
        """Analysis futási állapot lekérdezése"""
        return self.analysis_handler.is_analysis_running()

    def get_current_analysis_info(self) -> Dict[str, Any]:
        """Jelenlegi analysis információk lekérdezése"""
        return self.analysis_handler.get_current_analysis_info()

    # === TELEPÜLÉS KERESÉS LOGIKA ===

    @Slot(str)
    def handle_search_request(self, search_query: str) -> None:
        """
        Település keresési kérés kezelése.

        Args:
            search_query: Keresési kifejezés
        """
        self.geocoding_handler.handle_search_request(search_query)

    @Slot(str, float, float, dict)
    def handle_city_selection(self, city_name: str, latitude: float,
                              longitude: float, metadata: Dict[str, Any]) -> None:
        """
        Település kiválasztás kezelése.

        Args:
            city_name: Település neve
            latitude: Földrajzi szélesség
            longitude: Földrajzi hosszúság
            metadata: További metaadatok
        """
        self.current_city_data = self.geocoding_handler.handle_city_selection(
            city_name, latitude, longitude, metadata
        )
        self.weather_data_handler.set_current_city(self.current_city_data)

    # === EREDETI WEATHER DATA REQUEST (DEPRECATED) ===

    @Slot(float, float, str, str, dict)
    def handle_weather_data_request(self, latitude: float, longitude: float,
                                   start_date: str, end_date: str, params: Dict[str, Any]) -> None:
        """
        DEPRECATED: Időjárási adatok lekérdezés (használd handle_analysis_request-et helyette)

        Args:
            latitude: Földrajzi szélesség
            longitude: Földrajzi hosszúság
            start_date: Kezdő dátum (YYYY-MM-DD)
            end_date: Befejező dátum (YYYY-MM-DD)
            params: API paraméterek
        """
        self._logger.warning("🌐🌪️ DEPRECATED: handle_weather_data_request használata.")

        # Konvertálás új formátumra
        analysis_request = {
            'analysis_type': 'single_location',
            'location_data': {
                'lat': latitude,
                'lon': longitude,
                'name': self.current_city_data.get('name', 'Unknown') if self.current_city_data else 'Unknown'
            },
            'date_range': {
                'start_date': start_date,
                'end_date': end_date
            },
            'api_params': params
        }

        self.handle_analysis_request(analysis_request)

    # === PROVIDER ROUTING ===

    @Slot(str)
    def handle_provider_change(self, provider_name: str) -> None:
        """
        Provider változás kezelése GUI-ból.

        Args:
            provider_name: Új provider neve
        """
        status_msg = self.provider_routing.handle_provider_change(provider_name)
        self.provider_selected.emit(provider_name)
        self.status_updated.emit(status_msg)

    def get_provider_info(self) -> Dict[str, Any]:
        """Provider információk lekérdezése GUI számára."""
        return self.provider_routing.get_provider_info()

    # === PUBLIKUS API ===

    def get_current_city(self) -> Optional[Dict[str, Any]]:
        """Jelenlegi kiválasztott város adatainak lekérdezése."""
        return self.current_city_data.copy() if self.current_city_data else None

    def get_current_weather_data(self) -> Optional[Dict[str, Any]]:
        """Jelenlegi időjárási adatok lekérdezése."""
        return self.weather_data_handler.get_current_weather_data()

    def cancel_all_operations(self) -> None:
        """Összes aktív művelet megszakítása."""
        try:
            self._logger.info("🛑 Cancelling all operations...")

            if self.is_analysis_running():
                self.stop_current_analysis()

            self.worker_manager.cancel_all()

            self.status_updated.emit("🛑 Műveletek megszakítva")
            self._logger.info("✅ Összes művelet megszakítva")

        except Exception as e:
            self._logger.error(f"Műveletek megszakítási hiba: {e}")

    def shutdown(self) -> None:
        """Controller leállítása és cleanup."""
        try:
            self._logger.info("🛑 AppController leállítása...")

            self.cancel_all_operations()

            # AnalysisHandler cleanup - use the module-level function
            from .analysis_handler.state_management import _cleanup_analysis_state
            _cleanup_analysis_state(self.analysis_handler)

            self.worker_manager.shutdown()

            # Preferences mentése
            self.provider_routing.save_preferences()

            # Állapot tisztítása
            self.current_city_data = None
            self.current_weather_data = None
            self.active_search_query = None

            self._logger.info("✅ AppController leállítva (CLEAN ARCHITECTURE REFACTORED)")

        except Exception as e:
            self._logger.warning(f"⚠️ Controller leállítási hiba: {e}")
            import traceback
            traceback.print_exc()

    def _load_user_preferences(self) -> None:
        """User preferences betöltése és signalok küldése."""
        try:
            prefs_data = self.provider_routing.load_user_preferences()

            # Provider selection signal
            self.provider_selected.emit(prefs_data['selected_provider'])

            # Usage statistics signal
            self.provider_usage_updated.emit(prefs_data['usage_data'])

            # Warning ellenőrzés
            if prefs_data['warning_data']:
                self.provider_warning.emit(*prefs_data['warning_data'])

            self._logger.info("✅ User preferences betöltve és signalok elküldve")

        except Exception as e:
            self._logger.error(f"User preferences betöltési hiba: {e}")
