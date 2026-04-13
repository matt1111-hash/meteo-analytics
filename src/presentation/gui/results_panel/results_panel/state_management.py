#!/usr/bin/env python3
# mypy: ignore-errors

"""
Results Panel - State Management

🗃️ Állapot kezelése és emergency controls

Képességek:
- State management (get/set)
- Validation
- Emergency reset
- Enable/disable controls

Fájl: src/presentation/gui/results_panel/results_panel/state_management.py
"""

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


def get_state(self) -> dict[str, Any]:
    """
    ResultsPanel állapot lekérdezése.

    Args:
        self: ResultsPanel instance

    Returns:
        Dict[str, Any]: Állapot dictionary
    """
    from .public_api import is_loading
    from .signal_handlers import get_current_tab

    return {
        "is_loading": is_loading(self),
        "current_city": self.current_city,
        "has_data": self.current_data is not None,
        "current_tab": get_current_tab(self),
        "progress_visible": self.progress_indicator.isVisible(),
        "pandas_available": True,
        "dataframe_extractor_available": self.data_processor._dataframe_extractor_available,
        "is_valid": True,
    }


def set_state(self, state: dict[str, Any]) -> bool:
    """
    ResultsPanel állapot beállítása.

    Args:
        self: ResultsPanel instance
        state: Állapot dictionary

    Returns:
        bool: True ha sikeres
    """
    try:
        from .public_api import (
            hide_loading_indicator,
            show_loading_indicator,
            switch_to_tab,
        )

        if state.get("is_loading"):
            show_loading_indicator(self)
        elif "is_loading" in state:
            hide_loading_indicator(self)

        if "current_tab" in state:
            switch_to_tab(self, state["current_tab"])

        logger.debug("ResultsPanel state set successfully")
        return True
    except Exception as e:
        logger.error(f"ResultsPanel state set failed: {e}")
        return False


def is_valid(self) -> bool:  # noqa: ARG001
    """
    ResultsPanel validálása.

    Args:
        self: ResultsPanel instance

    Returns:
        bool: Always True
    """
    return True


def set_enabled(self, enabled: bool) -> None:
    """
    ResultsPanel engedélyezése/letiltása.

    Args:
        self: ResultsPanel instance
        enabled: Enabled flag
    """
    if self.tab_widget:
        self.tab_widget.setEnabled(enabled)
    self.global_export_btn.setEnabled(enabled)
    self.extreme_weather_btn.setEnabled(enabled)
    logger.debug(f"ResultsPanel enabled state: {enabled}")


def emergency_reset(self) -> None:
    """
    Emergency reset - teljes panel visszaállítása.

    Args:
        self: ResultsPanel instance
    """
    logger.warning("ResultsPanel emergency reset triggered")

    # Loading reset
    from .public_api import force_hide_loading

    force_hide_loading(self)

    # Data clear
    from .public_api import clear_data

    clear_data(self)

    # UI reset
    self.title_label.setText("📊 Időjárási Adatok Elemzése")
    self.switch_to_tab("overview")

    logger.warning("ResultsPanel emergency reset completed")


def cleanup(self) -> None:
    """
    ResultsPanel cleanup.

    Args:
        self: ResultsPanel instance
    """
    # Progress manager cleanup
    self.progress_manager.cleanup()

    # Tab cleanup
    self.tab_manager.cleanup()

    logger.debug("ResultsPanel cleanup completed")


def closeEvent(self, event) -> None:
    """
    Widget bezárása - cleanup hívás.

    Args:
        self: ResultsPanel instance
        event: Close event
    """
    cleanup(self)
    from PySide6.QtWidgets import QWidget

    QWidget.closeEvent(self, event)


def __del__(self) -> None:
    """
    Destruktor - cleanup.

    Args:
        self: ResultsPanel instance
    """
    try:
        cleanup(self)
    except Exception:
        logger.exception("ResultsPanel cleanup during destruction failed")
