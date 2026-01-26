#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Worker Manager - Central worker management class

Központi worker management osztály - kezeli az összes worker
thread életciklusát, signalokat és provider routinget.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QObject, Signal, QMutex, QWaitCondition, QThread

from .base_worker import BaseWorkerThread
from .geocoding_worker import GeocodingWorker
from .weather_data_worker import WeatherDataWorker
from .sql_query_worker import SQLQueryWorker


class WorkerManager(QObject):
    """
    🔧 CRITICAL FIX: WorkerManager teljes completion signal routing-gal.
    🌍 PROVIDER ROUTING + 🌪️ WIND GUSTS támogatás megtartva.

    ÚJ FUNKCIÓK:
    ✅ Explicit worker_completed és worker_cancelled signalok
    ✅ Comprehensive worker tracking és cleanup
    ✅ Provider state management
    ✅ Emergency shutdown procedures
    ✅ Thread-safe operations
    """

    # Központi signalok
    error_occurred = Signal(str)
    progress_updated = Signal(str, int)  # worker_type, progress
    worker_started = Signal(str)         # worker_type
    worker_finished = Signal(str)        # worker_type

    # 🚨 FIX: Explicit completion signalok UI auto-hide-hoz
    worker_completed = Signal(str)       # ← ÚJ: Worker befejezve (success)
    worker_cancelled = Signal(str)       # ← ÚJ: Worker megszakítva
    all_workers_completed = Signal()     # ← ÚJ: Összes worker befejezve

    # Specifikus worker signalok
    geocoding_completed = Signal(list)
    weather_data_completed = Signal(dict)  # 🌪️ Wind gusts data támogatás
    sql_query_completed = Signal(object)

    # 🌍 Provider routing signalok
    provider_changed = Signal(str)  # Új provider név
    provider_fallback_occurred = Signal(str, str)  # eredeti, fallback provider
    provider_validation_failed = Signal(str, str)  # provider, error message
    provider_usage_tracked = Signal(str, bool)  # provider, success

    def __init__(self, parent: Optional['QObject'] = None):
        super().__init__(parent)

        # Aktív worker threadek tárolása
        self.active_workers: Dict[str, BaseWorkerThread] = {}
        self.worker_counter = 0

        # 🌍 Provider state tracking
        self.provider_states: Dict[str, Dict[str, Any]] = {}
        self.last_successful_provider: Optional[str] = None

        # Thread safe mutex - PySide6 kompatibilis
        self.mutex = QMutex()
        self.wait_condition = QWaitCondition()

        print("✅ DEBUG: WorkerManager inicializálva (COMPLETION SIGNAL FIX + PROVIDER ROUTING + WIND GUSTS)")

    def _get_worker_id(self, worker_type: str) -> str:
        """Egyedi worker ID generálása."""
        self.worker_counter += 1
        return f"{worker_type}_{self.worker_counter}"

    def start_geocoding(self, worker: GeocodingWorker) -> str:
        """
        🔧 FIX: Geocoding worker indítása completion signal routing-gal.
        """
        worker_id = self._get_worker_id("geocoding")

        # Signal kapcsolatok
        worker.geocoding_completed.connect(self.geocoding_completed.emit)
        worker.error_occurred.connect(self._on_worker_error)
        worker.finished.connect(lambda worker_id=worker_id: self._on_worker_finished(worker_id))
        worker.completion_signal.connect(lambda worker_id=worker_id: self._on_worker_completion(worker_id))
        worker.progress_updated.connect(lambda p: self.progress_updated.emit("geocoding", p))

        # Thread safe worker tárolása és indítása
        self.mutex.lock()
        try:
            self.active_workers[worker_id] = worker
        finally:
            self.mutex.unlock()

        worker.start()
        self.worker_started.emit("geocoding")
        print(f"✅ DEBUG: Geocoding worker indítva COMPLETION SIGNAL FIX-szel - {worker_id}")
        return worker_id

    def start_weather_data_fetch(self, worker: WeatherDataWorker) -> str:
        """
        🔧 CRITICAL FIX: Weather data worker indítása teljes completion signal routing-gal.
        🌍 PROVIDER ROUTING + 🌪️ WIND GUSTS támogatás megtartva.
        """
        worker_id = self._get_worker_id("weather_data")

        # 🚨 FIX: Teljes signal kapcsolatok + completion
        worker.weather_data_completed.connect(self.weather_data_completed.emit)
        worker.error_occurred.connect(self._on_worker_error)
        worker.finished.connect(lambda worker_id=worker_id: self._on_worker_finished(worker_id))
        worker.completion_signal.connect(lambda worker_id=worker_id: self._on_worker_completion(worker_id))
        worker.progress_updated.connect(lambda p: self.progress_updated.emit("weather_data", p))
        worker.status_updated.connect(lambda s: print(f"📊 Weather worker status: {s}"))

        # 🌍 Provider routing signal kapcsolatok
        worker.provider_changed.connect(self._on_provider_changed)
        worker.provider_fallback_occurred.connect(self._on_provider_fallback)
        worker.provider_validation_failed.connect(self._on_provider_validation_failed)

        # Thread safe worker tárolása és indítása
        self.mutex.lock()
        try:
            self.active_workers[worker_id] = worker
        finally:
            self.mutex.unlock()

        worker.start()
        self.worker_started.emit("weather_data")
        print(f"✅ DEBUG: Weather worker indítva COMPLETION SIGNAL FIX + PROVIDER ROUTING + WIND GUSTS - {worker_id}")
        return worker_id

    def start_sql_query(self, worker: SQLQueryWorker) -> str:
        """
        🔧 FIX: SQL query worker indítása completion signal routing-gal.
        """
        worker_id = self._get_worker_id("sql_query")

        # Signal kapcsolatok
        worker.query_completed.connect(self.sql_query_completed.emit)
        worker.error_occurred.connect(self._on_worker_error)
        worker.finished.connect(lambda worker_id=worker_id: self._on_worker_finished(worker_id))
        worker.completion_signal.connect(lambda worker_id=worker_id: self._on_worker_completion(worker_id))
        worker.progress_updated.connect(lambda p: self.progress_updated.emit("sql_query", p))

        # Thread safe worker tárolása és indítása
        self.mutex.lock()
        try:
            self.active_workers[worker_id] = worker
        finally:
            self.mutex.unlock()

        worker.start()
        self.worker_started.emit("sql_query")
        print(f"✅ DEBUG: SQL query worker indítva COMPLETION SIGNAL FIX-szel - {worker_id}")
        return worker_id

    def _on_worker_completion(self, worker_id: str) -> None:
        """
        🚨 CRITICAL FIX: Explicit worker completion handling.

        Ez a metódus biztosítja, hogy a UI megkapja a completion signalt
        automatikus progress bar hide-hoz.

        Args:
            worker_id: Worker azonosító
        """
        print(f"🔧 DEBUG: Worker completion signal received - {worker_id}")

        self.mutex.lock()
        try:
            if worker_id in self.active_workers:
                worker_type = worker_id.split('_')[0]
                worker = self.active_workers[worker_id]

                # 🚨 FIX: Completion signal emission
                if worker.is_cancelled:
                    self.worker_cancelled.emit(worker_type)
                    print(f"🛑 DEBUG: Worker cancelled completion - {worker_id}")
                else:
                    self.worker_completed.emit(worker_type)
                    print(f"✅ DEBUG: Worker successful completion - {worker_id}")

                # Ellenőrizzük, hogy van-e még aktív worker
                if len(self.active_workers) <= 1:  # Ez az utolsó
                    # Kis delay után all_workers_completed signal
                    QThread.msleep(100)
                    self.all_workers_completed.emit()

        finally:
            self.mutex.unlock()

    def _on_worker_finished(self, worker_id: str) -> None:
        """
        🔧 FIX: Worker befejezés kezelése comprehensive cleanup-pal.

        Args:
            worker_id: Worker azonosító
        """
        print(f"🔧 DEBUG: Worker finished signal received - {worker_id}")

        self.mutex.lock()
        try:
            if worker_id in self.active_workers:
                worker_type = worker_id.split('_')[0]

                # Worker eltávolítása
                worker = self.active_workers.pop(worker_id)

                # 🌍 Provider usage tracking finalizálása
                if hasattr(worker, 'actual_provider') and worker.actual_provider:
                    self._track_provider_usage(worker.actual_provider, True)

                # Thread cleanup
                if worker.isRunning():
                    worker.quit()
                    worker.wait(3000)  # 3 másodperc timeout

                self.worker_finished.emit(worker_type)
                print(f"✅ DEBUG: Worker befejezve és cleanup: {worker_id}")
        finally:
            self.mutex.unlock()

    def cancel_worker(self, worker_id: str) -> bool:
        """
        🔧 FIX: Specifikus worker megszakítása explicit cancel-lel.

        Args:
            worker_id: Worker azonosító

        Returns:
            bool: Sikerült-e a cancel
        """
        print(f"🛑 DEBUG: Cancel worker requested - {worker_id}")

        self.mutex.lock()
        try:
            if worker_id in self.active_workers:
                worker = self.active_workers[worker_id]
                worker.cancel()  # ← Ez triggereli a BaseWorkerThread.cancel() metódust
                print(f"🛑 DEBUG: Worker cancel signal sent - {worker_id}")
                return True
            else:
                print(f"⚠️ DEBUG: Worker not found for cancel - {worker_id}")
                return False
        finally:
            self.mutex.unlock()

    def cancel_all_workers(self) -> None:
        """
        🔧 CRITICAL FIX: Összes aktív worker megszakítása.

        Ez a metódus minden aktív worker-re meghívja a cancel() metódust,
        ami graceful shutdown-t indít minden thread-ben.
        """
        print("🛑 DEBUG: Cancel all workers requested")

        self.mutex.lock()
        try:
            worker_ids = list(self.active_workers.keys())
            for worker_id in worker_ids:
                worker = self.active_workers[worker_id]
                worker.cancel()
                print(f"🛑 DEBUG: Cancel signal sent to worker: {worker_id}")
        finally:
            self.mutex.unlock()

        print(f"🛑 DEBUG: Cancel signals sent to {len(worker_ids)} workers")

    def stop_all_workers(self) -> None:
        """
        🔧 FIX: Alias a cancel_all_workers-hez backward compatibility-ért.
        """
        self.cancel_all_workers()

    # === 🌍 PROVIDER ROUTING METHODS ===

    def _on_provider_changed(self, new_provider: str) -> None:
        """Provider változás kezelése."""
        from .worker_utils import get_source_display_name

        print(f"🔄 DEBUG: Provider changed to: {get_source_display_name(new_provider)}")
        self.last_successful_provider = new_provider
        self.provider_changed.emit(new_provider)

    def _on_provider_fallback(self, original_provider: str, fallback_provider: str) -> None:
        """Provider fallback kezelése."""
        print(f"🔄 DEBUG: Provider fallback: {original_provider} → {fallback_provider}")

        # Provider state update
        self.provider_states[original_provider] = {
            "status": "failed",
            "last_attempt": datetime.now(),
            "fallback_used": fallback_provider
        }

        self.provider_fallback_occurred.emit(original_provider, fallback_provider)

    def _on_provider_validation_failed(self, provider: str, error_message: str) -> None:
        """Provider validálási hiba kezelése."""
        print(f"❌ DEBUG: Provider validation failed: {provider} - {error_message}")

        # Provider state update
        self.provider_states[provider] = {
            "status": "validation_failed",
            "last_attempt": datetime.now(),
            "error": error_message
        }

        self.provider_validation_failed.emit(provider, error_message)

    def _track_provider_usage(self, provider: str, success: bool) -> None:
        """Provider használat tracking."""
        print(f"📊 DEBUG: Provider usage tracked: {provider} - {'SUCCESS' if success else 'FAILED'}")

        # Provider state update
        if provider not in self.provider_states:
            self.provider_states[provider] = {}

        self.provider_states[provider].update({
            "last_usage": datetime.now(),
            "last_result": "success" if success else "failed"
        })

        if success:
            self.last_successful_provider = provider

        self.provider_usage_tracked.emit(provider, success)

    def _on_worker_error(self, error_message: str) -> None:
        """Worker hiba kezelése."""
        print(f"❌ DEBUG: Worker error: {error_message}")
        self.error_occurred.emit(error_message)

    # === 🌍 PROVIDER STATE MANAGEMENT ===

    def get_provider_states(self) -> Dict[str, Dict[str, Any]]:
        """Provider állapotok lekérdezése."""
        self.mutex.lock()
        try:
            return self.provider_states.copy()
        finally:
            self.mutex.unlock()

    def get_last_successful_provider(self) -> Optional[str]:
        """Utolsó sikeres provider lekérdezése."""
        return self.last_successful_provider

    def reset_provider_states(self) -> None:
        """Provider állapotok resetelése."""
        self.mutex.lock()
        try:
            self.provider_states.clear()
            self.last_successful_provider = None
            print("🔄 DEBUG: Provider states reset")
        finally:
            self.mutex.unlock()

    # === PUBLIC API ===

    def get_active_workers(self) -> List[str]:
        """Aktív worker ID-k listája."""
        self.mutex.lock()
        try:
            return list(self.active_workers.keys())
        finally:
            self.mutex.unlock()

    def is_worker_active(self, worker_type: str) -> bool:
        """Adott típusú worker aktív-e."""
        self.mutex.lock()
        try:
            return any(wid.startswith(worker_type) for wid in self.active_workers.keys())
        finally:
            self.mutex.unlock()

    def get_worker_count(self) -> int:
        """Aktív worker-ek száma."""
        self.mutex.lock()
        try:
            return len(self.active_workers)
        finally:
            self.mutex.unlock()

    def emergency_terminate_all(self) -> None:
        """
        🚨 EMERGENCY: Összes worker kényszerű leállítása.

        Ez a metódus csak emergency esetekre van, amikor a graceful
        cancel nem működik és kényszerű terminate szükséges.
        """
        print("🚨 DEBUG: Emergency terminate all workers requested")

        self.mutex.lock()
        try:
            for worker_id, worker in list(self.active_workers.items()):
                print(f"🚨 DEBUG: Emergency terminating worker: {worker_id}")

                if worker.isRunning():
                    worker.terminate()
                    worker.wait(1000)  # 1 sec timeout

                # Worker eltávolítása
                self.active_workers.pop(worker_id, None)

            # Provider states cleanup
            self.provider_states.clear()
            self.last_successful_provider = None

        finally:
            self.mutex.unlock()

        print("🚨 DEBUG: Emergency terminate completed")

    def shutdown(self) -> None:
        """
        🔧 CRITICAL FIX: WorkerManager proper shutdown.

        Graceful shutdown:
        1. Cancel all workers
        2. Wait for completion
        3. Emergency terminate if needed
        4. Cleanup
        """
        print("🛑 DEBUG: WorkerManager shutdown initiated...")

        # 1. Graceful cancel
        self.cancel_all_workers()

        # 2. Várakozás a worker-ek leállására
        self.mutex.lock()
        try:
            # Maximum 10 másodperc várakozás
            total_wait = 0
            while self.active_workers and total_wait < 10000:
                self.mutex.unlock()
                QThread.msleep(100)  # 100ms sleep
                total_wait += 100
                self.mutex.lock()

            # 3. Ha még vannak aktív worker-ek, emergency terminate
            if self.active_workers:
                print("⚠️ DEBUG: Some workers didn't stop gracefully, emergency terminating...")
                self.mutex.unlock()
                self.emergency_terminate_all()
                self.mutex.lock()

            # 4. Final cleanup
            self.active_workers.clear()
            self.provider_states.clear()
            self.last_successful_provider = None

        finally:
            self.mutex.unlock()

        print("✅ DEBUG: WorkerManager shutdown completed")
