#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WorkerManager Core - Main worker management class with signals.
"""

from typing import Any, Dict, Optional

from PySide6.QtCore import QMutex, QObject, QWaitCondition, Signal

from .components.worker_starters import WorkerStarters
from .components.worker_handlers import WorkerHandlers
from .components.provider_manager import ProviderManager
from .components.shutdown import ShutdownManager


class WorkerManager(QObject):
    """
    🔧 CRITICAL FIX: WorkerManager with completion signal routing.

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

    # Explicit completion signalok
    worker_completed = Signal(str)       # Worker befejezve (success)
    worker_cancelled = Signal(str)       # Worker megszakítva
    all_workers_completed = Signal()     # Összes worker befejezve

    # Specifikus worker signalok
    geocoding_completed = Signal(list)
    weather_data_completed = Signal(dict)
    sql_query_completed = Signal(object)

    # Provider routing signalok
    provider_changed = Signal(str)
    provider_fallback_occurred = Signal(str, str)
    provider_validation_failed = Signal(str, str)
    provider_usage_tracked = Signal(str, bool)

    def __init__(self, parent: Optional['QObject'] = None):
        """
        Initialize WorkerManager.

        Args:
            parent: Parent QObject
        """
        super().__init__(parent)

        # Aktív worker threadek tárolása
        self.active_workers: Dict[str, 'BaseWorkerThread'] = {}
        self.worker_counter = 0

        # Provider state tracking
        self.provider_states: Dict[str, Dict[str, Any]] = {}
        self.last_successful_provider: Optional[str] = None

        # Thread safe mutex
        self.mutex = QMutex()
        self.wait_condition = QWaitCondition()

        # Helper components
        self._worker_starters = WorkerStarters(self)
        self._worker_handlers = WorkerHandlers(self)
        self._provider_manager = ProviderManager(self)
        self._shutdown_manager = ShutdownManager(self)

        print("✅ DEBUG: WorkerManager inicializálva (COMPLETION SIGNAL FIX + PROVIDER ROUTING)")

    def _get_worker_id(self, worker_type: str) -> str:
        """
        Generate unique worker ID.

        Args:
            worker_type: Type of worker

        Returns:
            Unique worker ID
        """
        self.worker_counter += 1
        return f"{worker_type}_{self.worker_counter}"

    # Worker starter methods (delegated to WorkerStarters)
    def start_geocoding(self, worker) -> str:
        """Start geocoding worker."""
        return self._worker_starters.start_geocoding(worker)

    def start_weather_data_fetch(self, worker) -> str:
        """Start weather data worker."""
        return self._worker_starters.start_weather_data_fetch(worker)

    def start_sql_query(self, worker) -> str:
        """Start SQL query worker."""
        return self._worker_starters.start_sql_query(worker)

    # Worker handler methods (delegated to WorkerHandlers)
    def cancel_worker(self, worker_id: str) -> bool:
        """Cancel specific worker."""
        return self._worker_handlers.cancel_worker(worker_id)

    def cancel_all_workers(self) -> None:
        """Cancel all active workers."""
        self._worker_handlers.cancel_all_workers()

    def stop_all_workers(self) -> None:
        """Alias for cancel_all_workers."""
        self.cancel_all_workers()

    # Provider management methods (delegated to ProviderManager)
    def get_provider_states(self) -> Dict[str, Dict[str, Any]]:
        """Get provider states."""
        return self._provider_manager.get_states()

    def get_last_successful_provider(self) -> Optional[str]:
        """Get last successful provider."""
        return self._provider_manager.get_last_successful()

    def reset_provider_states(self) -> None:
        """Reset provider states."""
        self._provider_manager.reset_states()

    # Public API methods
    def get_active_workers(self) -> list:
        """Get list of active worker IDs."""
        self.mutex.lock()
        try:
            return list(self.active_workers.keys())
        finally:
            self.mutex.unlock()

    def is_worker_active(self, worker_type: str) -> bool:
        """Check if worker type is active."""
        self.mutex.lock()
        try:
            return any(wid.startswith(worker_type) for wid in self.active_workers.keys())
        finally:
            self.mutex.unlock()

    def get_worker_count(self) -> int:
        """Get count of active workers."""
        self.mutex.lock()
        try:
            return len(self.active_workers)
        finally:
            self.mutex.unlock()

    # Shutdown methods (delegated to ShutdownManager)
    def emergency_terminate_all(self) -> None:
        """Emergency terminate all workers."""
        self._shutdown_manager.emergency_terminate_all()

    def shutdown(self) -> None:
        """Proper shutdown of WorkerManager."""
        self._shutdown_manager.shutdown()
