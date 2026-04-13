#!/usr/bin/env python3
# mypy: ignore-errors

"""
WorkerManager Worker Handlers - Handle worker completion, finished, errors.
"""

from typing import TYPE_CHECKING

from PySide6.QtCore import QThread

if TYPE_CHECKING:
    from ..core import WorkerManager


class WorkerHandlers:
    """Handle worker lifecycle events."""

    def __init__(self, manager: "WorkerManager"):
        """
        Initialize worker handlers.

        Args:
            manager: WorkerManager instance
        """
        self._manager = manager

    def _on_worker_completion(self, worker_id: str) -> None:
        """
        Handle worker completion signal.

        Args:
            worker_id: Worker identifier
        """
        print(f"🔧 DEBUG: Worker completion signal received - {worker_id}")

        self._manager.mutex.lock()
        try:
            if worker_id in self._manager.active_workers:
                worker_type = worker_id.split("_")[0]
                worker = self._manager.active_workers[worker_id]

                # Emit completion signal based on cancellation status
                if worker.is_cancelled:
                    self._manager.worker_cancelled.emit(worker_type)
                    print(f"🛑 DEBUG: Worker cancelled - {worker_id}")
                else:
                    self._manager.worker_completed.emit(worker_type)
                    print(f"✅ DEBUG: Worker completed - {worker_id}")

                # Check if last worker
                if len(self._manager.active_workers) <= 1:
                    QThread.msleep(100)
                    self._manager.all_workers_completed.emit()

        finally:
            self._manager.mutex.unlock()

    def _on_worker_finished(self, worker_id: str) -> None:
        """
        Handle worker finished signal with cleanup.

        Args:
            worker_id: Worker identifier
        """
        print(f"🔧 DEBUG: Worker finished signal received - {worker_id}")

        self._manager.mutex.lock()
        try:
            if worker_id in self._manager.active_workers:
                worker_type = worker_id.split("_")[0]

                # Remove worker
                worker = self._manager.active_workers.pop(worker_id)

                # Provider usage tracking
                if hasattr(worker, "actual_provider") and worker.actual_provider:
                    self._manager._provider_manager._track_provider_usage(
                        worker.actual_provider, True
                    )

                # Thread cleanup
                if worker.isRunning():
                    worker.quit()
                    worker.wait(3000)

                self._manager.worker_finished.emit(worker_type)
                print(f"✅ DEBUG: Worker befejezve és cleanup: {worker_id}")
        finally:
            self._manager.mutex.unlock()

    def _on_worker_error(self, error_message: str) -> None:
        """
        Handle worker error.

        Args:
            error_message: Error message
        """
        print(f"❌ DEBUG: Worker error: {error_message}")
        self._manager.error_occurred.emit(error_message)

    def cancel_worker(self, worker_id: str) -> bool:
        """
        Cancel specific worker.

        Args:
            worker_id: Worker identifier

        Returns:
            True if cancel successful
        """
        print(f"🛑 DEBUG: Cancel worker requested - {worker_id}")

        self._manager.mutex.lock()
        try:
            if worker_id in self._manager.active_workers:
                worker = self._manager.active_workers[worker_id]
                worker.cancel()
                print(f"🛑 DEBUG: Worker cancel signal sent - {worker_id}")
                return True
            else:
                print(f"⚠️ DEBUG: Worker not found for cancel - {worker_id}")
                return False
        finally:
            self._manager.mutex.unlock()

    def cancel_all_workers(self) -> None:
        """Cancel all active workers."""
        print("🛑 DEBUG: Cancel all workers requested")

        self._manager.mutex.lock()
        try:
            worker_ids = list(self._manager.active_workers.keys())
            for worker_id in worker_ids:
                worker = self._manager.active_workers[worker_id]
                worker.cancel()
                print(f"🛑 DEBUG: Cancel signal sent to worker: {worker_id}")
        finally:
            self._manager.mutex.unlock()

        print(f"🛑 DEBUG: Cancel signals sent to {len(worker_ids)} workers")
