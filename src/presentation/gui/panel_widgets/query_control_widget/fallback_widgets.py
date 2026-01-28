"""
Fallback widgets for QueryControlWidget.

Ez a modul tartalmazza a fallback widget implementációkat,
amikor a valós widgetek nem elérhetőek.
"""

from typing import Optional
from datetime import timedelta, date
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Signal
import logging

logger = logging.getLogger(__name__)


class FallbackLocationSelector(QWidget):
    """Fallback location selector widget."""

    location_selected = Signal(str, str, float, float)
    selection_changed = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        label = QLabel("📍 Helység választó (Fallback)")
        layout.addWidget(label)

    def get_current_city(self) -> str:
        return "Budapest"

    def get_current_coordinates(self) -> tuple[float, float]:
        return (47.4979, 19.0402)

    def get_selected_location_data(self) -> dict:
        return {"city": "Budapest", "valid": True}

    def set_enabled(self, enabled: bool) -> None:
        pass


class FallbackDateRangeWidget(QWidget):
    """Fallback date range widget."""

    date_range_changed = Signal(object, object)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        label = QLabel("📅 Dátum tartomány (Fallback)")
        layout.addWidget(label)

    def get_date_range(self) -> tuple[date, date]:
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        return start_date, end_date

    def is_valid(self) -> bool:
        return True

    def set_enabled(self, enabled: bool) -> None:
        pass


class FallbackParametersWidget(QWidget):
    """Fallback parameters widget."""

    parameters_changed = Signal(list)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        label = QLabel("🌡️ Paraméterek (Fallback)")
        layout.addWidget(label)

    def get_selected_parameters(self) -> list[str]:
        return ["temperature_2m", "precipitation", "wind_speed_10m"]

    def is_valid(self) -> bool:
        return True

    def set_enabled(self, enabled: bool) -> None:
        pass


class FallbackProviderWidget(QWidget):
    """Fallback provider widget."""

    provider_changed = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        label = QLabel("🌐 Provider (Fallback)")
        layout.addWidget(label)

    def get_current_provider(self) -> str:
        return "openmeteo"

    def is_valid(self) -> bool:
        return True

    def set_enabled(self, enabled: bool) -> None:
        pass
