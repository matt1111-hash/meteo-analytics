#!/usr/bin/env python3
# mypy: ignore-errors

"""
WorkerManager Shutdown - Shutdown and emergency procedures.
"""

from typing import TYPE_CHECKING

from PySide6.QtCore import QThread

if TYPE_CHECKING:
    from ..core import WorkerManager


class ShutdownManager:
    """Handle worker manager shutdown procedures."""

    def __init__(self, manager: "WorkerManager"):
        """
        Initialize shutdown manager.

        Args:
            manager: WorkerManager instance
        """
        self._manager = manager

    def emergency_terminate_all(self) -> None:
        """
        Emergency terminate all workers.

        This method should only be used in emergencies when graceful
        cancel doesn't work and forced terminate is necessary.
        """
        print("🚨 DEBUG: Emergency terminate all workers requested")

        self._manager.mutex.lock()
        try:
            for worker_id, worker in list(self._manager.active_workers.items()):
                print(f"🚨 DEBUG: Emergency terminating worker: {worker_id}")

                if worker.isRunning():
                    worker.terminate()
                    worker.wait(1000)

                # Remove worker
                self._manager.active_workers.pop(worker_id, None)

            # Cleanup provider states
            self._manager.provider_states.clear()
            self._manager.last_successful_provider = None

        finally:
            self._manager.mutex.unlock()

        print("🚨 DEBUG: Emergency terminate completed")

    def shutdown(self) -> None:
        """
        Proper shutdown of WorkerManager.

        Graceful shutdown:
        1. Cancel all workers
        2. Wait for completion
        3. Emergency terminate if needed
        4. Cleanup
        """
        print("🛑 DEBUG: WorkerManager shutdown initiated...")

        # 1. Graceful cancel
        self._manager._worker_handlers.cancel_all_workers()

        # 2. Wait for workers to stop
        self._manager.mutex.lock()
        try:
            total_wait = 0
            while self._manager.active_workers and total_wait < 10000:  # noqa: PLR2004
                self._manager.mutex.unlock()
                QThread.msleep(100)
                total_wait += 100
                self._manager.mutex.lock()

            # 3. Emergency terminate if still active
            if self._manager.active_workers:
                print("⚠️ DEBUG: Some workers didn't stop gracefully, emergency terminating...")
                self._manager.mutex.unlock()
                self.emergency_terminate_all()
                self._manager.mutex.lock()

            # 4. Final cleanup
            self._manager.active_workers.clear()
            self._manager.provider_states.clear()
            self._manager.last_successful_provider = None

        finally:
            self._manager.mutex.unlock()

        print("✅ DEBUG: WorkerManager shutdown completed")
