#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mypy: ignore-errors

"""
Analysis Handler - Core

🎯 AnalysisHandler main class

Képességek:
- Main class
- Signal definíciók
- Inicializáció

Fájl: src/presentation/gui/controller/analysis_handler/core.py
"""

import logging
from typing import Any, Dict

from PySide6.QtCore import QObject, Signal, Slot

from .request_handler import handle_analysis_request
from .slot_handlers import (
    on_analysis_cancelled,
    on_analysis_completed,
    on_analysis_failed,
    on_analysis_progress,
)
from .state_management import (
    get_current_analysis_info,
    is_analysis_running,
    set_active_worker,
    stop_current_analysis,
)

logger = logging.getLogger(__name__)


class AnalysisHandler(QObject):
    """
    Analysis request kezelése.

    Felelőségek:
    - Analysis request routing (single/multi-city/county)
    - Worker lifecycle management
    - Request validálás
    - Analysis state kezelés
    """

    # Signalok
    analysis_started = Signal(str)  # analysis_type
    analysis_progress = Signal(str, int)  # message, percentage
    analysis_completed = Signal(dict)  # result_data
    analysis_failed = Signal(str)  # error_message
    analysis_cancelled = Signal()  # megszakítás megerősítése
    status_updated = Signal(str)  # str - státusz üzenet

    def __init__(self, parent=None):
        """
        AnalysisHandler inicializálása.

        Args:
            parent: Szülő QObject (általában AppController)
        """
        super().__init__(parent)
        self._logger = logging.getLogger(__name__)

        # Analysis state
        self.active_analysis_worker = None
        self.analysis_state = {
            "is_running": False,
            "analysis_type": None,
            "start_time": None,
            "request_data": None,
        }

        logger.info("✅ AnalysisHandler inicializálva")

    # Public API methods
    def handle_analysis_request(
        self, request_data: Dict[str, Any], provider_routing, start_analysis_callback
    ) -> None:
        handle_analysis_request(
            self, request_data, provider_routing, start_analysis_callback
        )

    @Slot(str, int)
    def on_analysis_progress(self, message: str, percentage: int) -> None:
        on_analysis_progress(self, message, percentage)

    @Slot(dict)
    def on_analysis_completed(self, result_data: dict) -> None:
        on_analysis_completed(self, result_data)

    @Slot(str)
    def on_analysis_failed(self, error_message: str) -> None:
        on_analysis_failed(self, error_message)

    @Slot()
    def on_analysis_cancelled(self) -> None:
        on_analysis_cancelled(self)

    def stop_current_analysis(self) -> None:
        stop_current_analysis(self)

    def is_analysis_running(self) -> bool:
        return is_analysis_running(self)

    def get_current_analysis_info(self) -> Dict:
        return get_current_analysis_info(self)

    def set_active_worker(self, worker) -> None:
        set_active_worker(self, worker)
