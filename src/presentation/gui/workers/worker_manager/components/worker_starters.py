#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mypy: ignore-errors

"""
WorkerManager Worker Starters - Start different worker types.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core import WorkerManager


class WorkerStarters:
    """Handle starting different worker types."""

    def __init__(self, manager: "WorkerManager"):
        """
        Initialize worker starters.

        Args:
            manager: WorkerManager instance
        """
        self._manager = manager

    def start_geocoding(self, worker) -> str:
        """
        Start geocoding worker with signal connections.

        Args:
            worker: GeocodingWorker instance

        Returns:
            Worker ID
        """
        worker_id = self._manager._get_worker_id("geocoding")

        # Signal connections
        worker.geocoding_completed.connect(self._manager.geocoding_completed.emit)
        worker.error_occurred.connect(self._manager._worker_handlers._on_worker_error)
        worker.finished.connect(
            lambda wid=worker_id: self._manager._worker_handlers._on_worker_finished(
                wid
            )
        )
        worker.completion_signal.connect(
            lambda wid=worker_id: self._manager._worker_handlers._on_worker_completion(
                wid
            )
        )
        worker.progress_updated.connect(
            lambda p: self._manager.progress_updated.emit("geocoding", p)
        )

        # Thread-safe worker storage and start
        self._manager.mutex.lock()
        try:
            self._manager.active_workers[worker_id] = worker
        finally:
            self._manager.mutex.unlock()

        worker.start()
        self._manager.worker_started.emit("geocoding")
        print(f"✅ DEBUG: Geocoding worker indítva - {worker_id}")
        return worker_id

    def start_weather_data_fetch(self, worker) -> str:
        """
        Start weather data worker with signal connections.

        Args:
            worker: WeatherDataWorker instance

        Returns:
            Worker ID
        """
        worker_id = self._manager._get_worker_id("weather_data")

        # Signal connections
        worker.weather_data_completed.connect(self._manager.weather_data_completed.emit)
        worker.error_occurred.connect(self._manager._worker_handlers._on_worker_error)
        worker.finished.connect(
            lambda wid=worker_id: self._manager._worker_handlers._on_worker_finished(
                wid
            )
        )
        worker.completion_signal.connect(
            lambda wid=worker_id: self._manager._worker_handlers._on_worker_completion(
                wid
            )
        )
        worker.progress_updated.connect(
            lambda p: self._manager.progress_updated.emit("weather_data", p)
        )
        worker.status_updated.connect(lambda s: print(f"📊 Weather worker status: {s}"))

        # Provider routing signal connections
        worker.provider_changed.connect(
            self._manager._provider_manager._on_provider_changed
        )
        worker.provider_fallback_occurred.connect(
            self._manager._provider_manager._on_provider_fallback
        )
        worker.provider_validation_failed.connect(
            self._manager._provider_manager._on_provider_validation_failed
        )

        # Thread-safe worker storage and start
        self._manager.mutex.lock()
        try:
            self._manager.active_workers[worker_id] = worker
        finally:
            self._manager.mutex.unlock()

        worker.start()
        self._manager.worker_started.emit("weather_data")
        print(f"✅ DEBUG: Weather worker indítva - {worker_id}")
        return worker_id

    def start_sql_query(self, worker) -> str:
        """
        Start SQL query worker with signal connections.

        Args:
            worker: SQLQueryWorker instance

        Returns:
            Worker ID
        """
        worker_id = self._manager._get_worker_id("sql_query")

        # Signal connections
        worker.query_completed.connect(self._manager.sql_query_completed.emit)
        worker.error_occurred.connect(self._manager._worker_handlers._on_worker_error)
        worker.finished.connect(
            lambda wid=worker_id: self._manager._worker_handlers._on_worker_finished(
                wid
            )
        )
        worker.completion_signal.connect(
            lambda wid=worker_id: self._manager._worker_handlers._on_worker_completion(
                wid
            )
        )
        worker.progress_updated.connect(
            lambda p: self._manager.progress_updated.emit("sql_query", p)
        )

        # Thread-safe worker storage and start
        self._manager.mutex.lock()
        try:
            self._manager.active_workers[worker_id] = worker
        finally:
            self._manager.mutex.unlock()

        worker.start()
        self._manager.worker_started.emit("sql_query")
        print(f"✅ DEBUG: SQL query worker indítva - {worker_id}")
        return worker_id
