"""
QueryControlWidget - Core implementation.

Ez a modul tartalmazza a QueryControlWidget fő osztályát.
"""

import logging
from typing import Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget

logger = logging.getLogger(__name__)

# Import handling
try:
    from ..hungarian_location_selector import HungarianLocationSelector
    _location_selector_available = True
    logger.debug("✅ HungarianLocationSelector import successful")
except ImportError:
    _location_selector_available = False
    HungarianLocationSelector = None

try:
    from ..data_widgets import DateRangeWidget, ParametersWidget, ProviderWidget
    _data_widgets_available = True
    logger.debug("✅ Data widgets import successful")
except ImportError:
    _data_widgets_available = False
    DateRangeWidget = ParametersWidget = ProviderWidget = None

try:
    from src.presentation.gui.theme_manager import get_theme_manager
    _theme_manager_available = True
    logger.debug("✅ ThemeManager import successful")
except ImportError:
    _theme_manager_available = False
    get_theme_manager = None

from .event_handlers import QueryControlEventHandlers
from .external_api import QueryControlExternalAPI
from .fallback_widgets import (
    FallbackDateRangeWidget,
    FallbackLocationSelector,
    FallbackParametersWidget,
    FallbackProviderWidget,
)
from .state_manager import QueryControlStateManager
from .ui_builder import QueryControlUIBuilder
from .validation import QueryValidator
from .widget_factory import WidgetFactory


class QueryControlWidget(QWidget):
    """
    Query control widget egyszerűsített validációval.

    FŐ FUNKCIÓK:
    - Location selection: magyar városok + koordináták
    - Date range picker: start/end dátum választó
    - Parameters selection: időjárási paraméterek
    - Provider selection: adatszolgáltató választás
    - Query execution: Lekérdezés gomb + progress tracking
    - Cancel support: Megszakítás gomb + auto-reset
    - State management: fetching/idle/error/success állapotok
    - External API: AppController integration
    """

    query_requested = Signal(dict)
    fetch_requested = Signal(dict)
    location_changed = Signal(str, str, float, float)
    cancel_requested = Signal()
    state_changed = Signal(str)
    validation_changed = Signal(bool)

    def __init__(self, parent: Optional[QWidget] = None):
        """QueryControlWidget inicializálása."""
        super().__init__(parent)
        logger.info("QueryControlWidget inicializálás START")

        self.theme_manager = get_theme_manager() if _theme_manager_available else None

        # Widget factory és widgetek
        self._widget_factory = WidgetFactory(
            real_widgets={
                'location': HungarianLocationSelector,
                'date_range': DateRangeWidget,
                'parameters': ParametersWidget,
                'provider': ProviderWidget
            },
            fallback_widgets={
                'location': FallbackLocationSelector,
                'date_range': FallbackDateRangeWidget,
                'parameters': FallbackParametersWidget,
                'provider': FallbackProviderWidget
            }
        )

        self.location_widget = self._widget_factory.create_location()
        self.date_range_widget = self._widget_factory.create_date_range()
        self.parameters_widget = self._widget_factory.create_parameters()
        self.provider_widget = self._widget_factory.create_provider()

        # UI builder
        self._ui_builder = QueryControlUIBuilder(self)
        self._ui_builder.build_ui(
            self.location_widget, self.date_range_widget,
            self.parameters_widget, self.provider_widget
        )

        # State manager, validator, event handlers
        self._state_manager = QueryControlStateManager(self._ui_builder, self.state_changed)
        self._validator = QueryValidator(
            self.location_widget, self.date_range_widget,
            self.parameters_widget, self.provider_widget
        )
        self._event_handlers = QueryControlEventHandlers(
            self._validator, self._state_manager, self._ui_builder
        )

        # Event handlers setup
        for attr, value in [
            ('location_widget', self.location_widget),
            ('date_range_widget', self.date_range_widget),
            ('parameters_widget', self.parameters_widget),
            ('provider_widget', self.provider_widget),
            ('query_requested', self.query_requested),
            ('fetch_requested', self.fetch_requested),
            ('location_changed', self.location_changed),
            ('cancel_requested', self.cancel_requested),
            ('validation_changed', self.validation_changed),
        ]:
            setattr(self._event_handlers, attr, value)

        # External API
        self._external_api = QueryControlExternalAPI(
            self._state_manager, self._ui_builder, self._event_handlers
        )

        # Connect signals
        self._event_handlers.connect_widget_signals()
        if self._ui_builder.query_button:
            self._ui_builder.query_button.clicked.connect(self._event_handlers.on_query_clicked)
        if self._ui_builder.cancel_button:
            self._ui_builder.cancel_button.clicked.connect(self._event_handlers.on_cancel_clicked)

        # Initial state
        self._state_manager.set_state(self._state_manager.STATE_IDLE)
        logger.info("QueryControlWidget inicializálás BEFEJEZVE")

    # === PUBLIC API (dinamikus delegálás) ===

    def __getattr__(self, name: str):
        """Dinamikus delegálás az external API-hoz."""
        if hasattr(self._external_api, name):
            return getattr(self._external_api, name)
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    # === INTERNAL METHODS ===

    def _is_query_valid(self) -> bool:
        """Query validálás (belső használatra)."""
        return self._validator.is_query_valid()

    def apply_theme(self, dark_theme: bool) -> None:
        """Téma alkalmazása."""
        logger.debug(f"apply_theme({dark_theme}) called")

    # === CLEANUP ===

    def cleanup(self) -> None:
        """Widget cleanup."""
        logger.debug("QueryControlWidget cleanup start")
        self._state_manager.cleanup()
        self._state_manager._is_fetching = False
        self._state_manager._cancel_requested = False

        for widget in [self.location_widget, self.date_range_widget,
                       self.parameters_widget, self.provider_widget]:
            if widget and hasattr(widget, 'cleanup'):
                widget.cleanup()

        logger.debug("QueryControlWidget cleanup completed")

    def closeEvent(self, event) -> None:
        self.cleanup()
        super().closeEvent(event)

    def __del__(self):
        try:
            self.cleanup()
        except:
            pass
