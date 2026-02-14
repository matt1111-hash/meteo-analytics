#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Analysis Handler - State Management

🗃️ Állapot kezelése és cleanup

Képességek:
- State cleanup
- Worker cleanup
- Analysis leállítás

Fájl: src/presentation/gui/controller/analysis_handler/state_management.py
"""

import logging
from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


def _cleanup_analysis_state(self) -> None:
    """
    Analysis state és worker cleanup.

    Args:
        self: AnalysisHandler instance
    """
    try:
        # Worker cleanup
        if self.active_analysis_worker:
            if self.active_analysis_worker.isRunning():
                self.active_analysis_worker.stop_analysis()

            # Disconnect signalok
            try:
                self.active_analysis_worker.progress_updated.disconnect()
                self.active_analysis_worker.analysis_completed.disconnect()
                self.active_analysis_worker.analysis_failed.disconnect()
                self.active_analysis_worker.analysis_cancelled.disconnect()
            except Exception:
                pass

            # Worker törlése
            self.active_analysis_worker.deleteLater()
            self.active_analysis_worker = None

        # State reset
        self.analysis_state = {
            "is_running": False,
            "analysis_type": None,
            "start_time": None,
            "request_data": None,
        }

        logger.info("🧹 Analysis state cleaned up")

    except Exception as e:
        logger.error(f"Cleanup hiba: {e}")


def stop_current_analysis(self) -> None:
    """
    AKTUÁLIS ANALYSIS LEÁLLÍTÁSA
    Graceful shutdown - nem brutális terminálás.

    Args:
        self: AnalysisHandler instance
    """
    try:
        if not self.analysis_state["is_running"]:
            logger.info("🛑 Nincs futó analysis amit meg lehetne szakítani")
            return

        analysis_type = self.analysis_state.get("analysis_type", "unknown")
        logger.info(f"🛑 Analysis megszakítása: {analysis_type}")

        if self.active_analysis_worker:
            self.active_analysis_worker.stop_analysis()

        # State update
        self.status_updated.emit("🛑 Elemzés megszakítása...")

    except Exception as e:
        logger.error(f"Analysis stop hiba: {e}")


# === PUBLIC GETTEREK ===


def is_analysis_running(self) -> bool:
    """
    Analysis futási állapot lekérdezése.

    Args:
        self: AnalysisHandler instance

    Returns:
        bool: True ha fut analysis
    """
    return self.analysis_state.get("is_running", False)


def get_current_analysis_info(self) -> Dict:
    """
    Jelenlegi analysis információk lekérdezése.

    Args:
        self: AnalysisHandler instance

    Returns:
        Dict: Analysis információk
    """
    return self.analysis_state.copy()


def set_active_worker(self, worker) -> None:
    """
    Aktív analysis worker beállítása.

    Args:
        self: AnalysisHandler instance
        worker: AnalysisWorker példány
    """
    self.active_analysis_worker = worker
