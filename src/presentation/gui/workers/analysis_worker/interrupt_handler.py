"""
AnalysisWorker Interrupt Handler - Handle interruption requests.
"""

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .core import AnalysisWorker


class InterruptHandler:
    """Handle thread interruption checks and requests."""

    def __init__(self, worker: "AnalysisWorker"):
        """
        Initialize interrupt handler.

        Args:
            worker: AnalysisWorker instance
        """
        self._worker = worker
        self._logger = logging.getLogger(__name__)

    def check(self, operation: str) -> bool:
        """
        Check if interruption was requested.

        Args:
            operation: Current operation name (for debugging)

        Returns:
            True if should interrupt
        """
        if self._worker.isInterruptionRequested():
            self._logger.info(f"Megszakítás kérve művelet közben: {operation}")
            self._worker._emit_progress("Megszakítás...", 0)
            self._worker.analysis_cancelled.emit()
            return True
        return False

    def request(self) -> None:
        """Request interruption."""
        self._logger.info("Worker megszakítás kérve...")
        self._worker.requestInterruption()

    def wait_for_shutdown(self, timeout_ms: int = 5000) -> bool:
        """
        Wait for graceful shutdown.

        Args:
            timeout_ms: Maximum time to wait in milliseconds

        Returns:
            True if worker stopped gracefully
        """
        if not self._worker.wait(timeout_ms):
            self._logger.warning(f"Worker nem állt le {timeout_ms}ms alatt")
            return False
        return True
