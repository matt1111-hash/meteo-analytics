#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Analysis Handler - Slot Handlers

🔌 Slot signal kezelők

Képességek:
- Progress handler
- Completed handler
- Failed handler
- Cancelled handler

Fájl: src/presentation/gui/controller/analysis_handler/slot_handlers.py
"""

import logging
from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


def on_analysis_progress(self, message: str, percentage: int) -> None:
    """
    Analysis progress frissítése.

    Args:
        self: AnalysisHandler instance
        message: Progress üzenet
        percentage: Progress százalék
    """
    self.analysis_progress.emit(message, percentage)
    self.status_updated.emit(f"📊 {message} ({percentage}%)")
    logger.debug(f"📊 Analysis progress: {message} - {percentage}%")


def on_analysis_completed(self, result_data: Dict) -> None:
    """
    Analysis befejezése sikeresen.

    Args:
        self: AnalysisHandler instance
        result_data: Eredmény adatok
    """
    from .result_processor import (
        _calculate_analysis_duration,
        _process_analysis_result,
    )
    from .state_management import _cleanup_analysis_state

    try:
        logger.info("✅ Analysis completed successfully")

        # Eredmény feldolgozása típus alapján
        processed_result = _process_analysis_result(self, result_data)

        # State cleanup
        analysis_type = self.analysis_state.get('analysis_type', 'unknown')
        duration = _calculate_analysis_duration(self)

        # Success signalok
        self.analysis_completed.emit(processed_result)
        self.status_updated.emit(f"✅ {analysis_type.replace('_', ' ').title()} elemzés befejezve ({duration:.1f}s)")

        # Cleanup
        _cleanup_analysis_state(self)

    except Exception as e:
        logger.error(f"Analysis result processing hiba: {e}")
        self.analysis_failed.emit(f"Eredmény feldolgozási hiba: {e}")


def on_analysis_failed(self, error_message: str) -> None:
    """
    Analysis hiba kezelése.

    Args:
        self: AnalysisHandler instance
        error_message: Error üzenet
    """
    from .state_management import _cleanup_analysis_state

    logger.error(f"❌ Analysis failed: {error_message}")
    self.analysis_failed.emit(error_message)
    self.status_updated.emit(f"❌ Elemzési hiba: {error_message}")
    _cleanup_analysis_state(self)


def on_analysis_cancelled(self) -> None:
    """
    Analysis megszakítás kezelése.

    Args:
        self: AnalysisHandler instance
    """
    from .state_management import _cleanup_analysis_state

    logger.info("ℹ️ Analysis cancelled")
    self.analysis_cancelled.emit()
    self.status_updated.emit("ℹ️ Elemzés megszakítva")
    _cleanup_analysis_state(self)
