"""
QueryControlWidget - Core implementation (SIMPLIFIED).

Egyszerűsített verzió: csak a vezérlőgombokat és állapotkezelést tartalmazza.
A widgetek (location, date_range, parameters, provider) a ControlPanel-ben vannak.
"""

import logging
from typing import Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget

from .event_handlers import QueryControlEventHandlers
from .external_api import QueryControlExternalAPI
from .state_manager import QueryControlStateManager
from .ui_builder import QueryControlUIBuilder


logger = logging.getLogger(__name__)


class QueryControlWidget(QWidget):
    """
    Query control widget - egyszerűsített verzió.

    FŐ FUNKCIÓK:
    - Query execution: Lekérdezés gomb + progress tracking
    - Cancel support: Megszakítás gomb + auto-reset
    - State management: fetching/idle/error/success állapotok
    - External API: AppController integration

    A widgetek (location, date_range, parameters, provider) a ControlPanel-ben vannak.
    """

    query_requested = Signal(dict)
    fetch_requested = Signal(dict)
    cancel_requested = Signal()
    state_changed = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        """QueryControlWidget inicializálása."""
        super().__init__(parent)
        logger.info("QueryControlWidget inicializálás START (simplified)")

        # UI builder
        self._ui_builder = QueryControlUIBuilder(self)
        self._ui_builder.build_ui()

        # State manager
        self._state_manager = QueryControlStateManager(self._ui_builder, self.state_changed)

        # Event handlers (egyszerűsített - csak gombokat kezel)
        self._event_handlers = QueryControlEventHandlers(
            self._state_manager, self._ui_builder
        )

        # Event handlers setup
        self._event_handlers.query_requested = self.query_requested
        self._event_handlers.fetch_requested = self.fetch_requested
        self._event_handlers.cancel_requested = self.cancel_requested

        # Connect button signals
        if self._ui_builder.query_button:
            self._ui_builder.query_button.clicked.connect(self._event_handlers.on_query_clicked)
        if self._ui_builder.cancel_button:
            self._ui_builder.cancel_button.clicked.connect(self._event_handlers.on_cancel_clicked)

        # External API
        self._external_api = QueryControlExternalAPI(
            self._state_manager, self._ui_builder, self._event_handlers
        )

        # Initial state
        self._state_manager.set_state(self._state_manager.STATE_IDLE)
        logger.info("QueryControlWidget inicializálás BEFEJEZVE (simplified)")

    # === PUBLIC API ===

    @property
    def is_fetching(self) -> bool:
        """Fetching állapot lekérdezése."""
        return self._state_manager.is_fetching

    @property
    def _is_fetching(self) -> bool:
        """Internal fetching state (backward compatibility)."""
        return self._state_manager.is_fetching

    @property
    def query_button(self):
        """Query button elérése."""
        return self._ui_builder.query_button

    @property
    def cancel_button(self):
        """Cancel button elérése."""
        return self._ui_builder.cancel_button

    @property
    def status_label(self):
        """Status label elérése."""
        return self._ui_builder.status_label

    def __getattr__(self, name: str):
        """Dinamikus delegálás az external API-hoz."""
        if hasattr(self._external_api, name):
            return getattr(self._external_api, name)
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    # === CLEANUP ===

    def cleanup(self) -> None:
        """Widget cleanup."""
        logger.debug("QueryControlWidget cleanup start")
        self._state_manager.cleanup()
        logger.debug("QueryControlWidget cleanup completed")

    def closeEvent(self, event) -> None:
        self.cleanup()
        super().closeEvent(event)

    def __del__(self):
        try:
            self.cleanup()
        except:
            pass
