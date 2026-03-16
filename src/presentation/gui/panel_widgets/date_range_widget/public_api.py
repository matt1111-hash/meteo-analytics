#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mypy: ignore-errors

"""
Date Range Widget - Public API

📤 Publikus interface metódusok

Képességek:
- State management (get_state, set_state)
- Validation
- Date range query
- Widget enabled/disabled

Fájl: src/presentation/gui/panel_widgets/date_range_widget/public_api.py
"""

from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Tuple

from PySide6.QtCore import QDate, Qt

if TYPE_CHECKING:
    pass


def _set_manual_date_if_valid(
    widget: Any, attr_name: str, date_value: str | None
) -> None:
    """Set a manual QDateEdit value when the ISO date is valid."""
    if not date_value:
        return
    qdate = QDate.fromString(date_value, Qt.ISODate)
    if qdate.isValid():
        getattr(widget, attr_name).setDate(qdate)


def _apply_time_range_state(
    widget: Any, time_range: str | None, date_mode: str
) -> None:
    """Apply time-range selection state."""
    if not time_range or date_mode != "time_range":
        return
    index = widget.time_range_combo.findText(time_range)
    if index >= 0:
        widget.time_range_combo.setCurrentIndex(index)


def _apply_manual_date_state(
    widget: Any, state: Dict[str, Any], date_mode: str
) -> None:
    """Apply manual date state when active."""
    if date_mode != "manual_dates":
        return
    _set_manual_date_if_valid(widget, "start_date", state.get("start_date"))
    _set_manual_date_if_valid(widget, "end_date", state.get("end_date"))


class DateRangeWidgetPublicAPI:
    """
    Publikus interface metódusok delegeálása.

    Ez a mixin osztály tartalmazza a publikus metódusokat,
    amiket a DateRangeWidget 提供.
    """

    # State
    date_mode: str
    _updating_state: bool
    time_range_combo: any
    time_range_radio: any
    manual_dates_radio: any
    start_date: any
    end_date: any
    time_range_group: any
    manual_dates_group: any

    # Signal (delegált)
    date_range_changed: any
    date_mode_changed: any

    # Method from DateHandlerMixin
    _get_effective_date_range: any

    def get_state(self) -> Dict[str, Any]:
        """
        Aktuális állapot lekérdezése.

        Returns:
            Dict az aktuális állapottal
        """
        start_date, end_date = self._get_effective_date_range()

        return {
            "date_mode": self.date_mode,
            "time_range": self.time_range_combo.currentText()
            if self.date_mode == "time_range"
            else None,
            "start_date": start_date,
            "end_date": end_date,
            "is_valid": self.is_valid(),
        }

    def set_state(self, state: Dict[str, Any]) -> bool:
        """
        Állapot beállítása.

        Args:
            state: Beállítandó állapot dict

        Returns:
            bool: Sikeres volt-e a beállítás
        """
        try:
            self._updating_state = True
            date_mode = state.get("date_mode", "time_range")
            if date_mode == "time_range":
                self.time_range_radio.setChecked(True)
            else:
                self.manual_dates_radio.setChecked(True)

            self.date_mode = date_mode
            self._set_manual_dates_enabled(date_mode == "manual_dates")
            _apply_time_range_state(self, state.get("time_range"), date_mode)
            _apply_manual_date_state(self, state, date_mode)
            if date_mode == "time_range":
                self._update_computed_dates()

            print(f"✅ DEBUG: DateRangeWidget state set: {date_mode}")
            return True

        except Exception as e:
            print(f"❌ ERROR: Failed to set DateRangeWidget state: {e}")
            return False
        finally:
            self._updating_state = False

    def is_valid(self) -> bool:
        """
        Dátum tartomány validálása.

        Returns:
            bool: Valid-e a dátum tartomány
        """
        try:
            start_date, end_date = self._get_effective_date_range()
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")

            # Start <= End
            if start > end:
                return False

            # Minimum 1 nap
            if (end - start).days < 1:
                return False

            # Maximum 60 év (praktikus limit)
            if (end - start).days > 60 * 365:
                return False

            return True

        except ValueError:
            return False

    def get_date_range(self) -> Tuple[str, str]:
        """
        Dátum tartomány lekérdezése (compatibility).

        Returns:
            (start_date, end_date) tuple
        """
        return self._get_effective_date_range()

    def get_date_mode(self) -> str:
        """
        Date mode lekérdezése.

        Returns:
            "time_range" vagy "manual_dates"
        """
        return self.date_mode

    def set_enabled(self, enabled: bool) -> None:
        """
        Widget engedélyezése/letiltása.

        Args:
            enabled: Engedélyezett állapot
        """
        self.time_range_group.setEnabled(enabled)
        self.manual_dates_group.setEnabled(enabled)

        print(f"📅 DEBUG: DateRangeWidget enabled state: {enabled}")

    # === SIZE HINT ===

    def sizeHint(self):
        """Preferált méret."""
        return self.time_range_group.sizeHint()

    def minimumSizeHint(self):
        """Minimum méret."""
        return self.time_range_group.minimumSizeHint()
