#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Date Range Widget - Date Handlers

📅 Dátum kezelése és számítás

Képességek:
- Signal handling
- Dátum számítás (computed dates)
- Quick button handlers
- Date validation

Fájl: src/presentation/gui/panel_widgets/date_range_widget/date_handlers.py
"""

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Tuple

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import QLabel

if TYPE_CHECKING:
    pass


class DateHandlerMixin:
    """
    Dátum kezelése és számítás keverék osztály.

    Ez a mixin osztály tartalmazza a dátumhoz kapcsolódó
    metódusokat.
    """

    # These will be set when mixed into DateRangeWidget
    date_mode: str
    _updating_state: bool
    time_range_combo: any
    start_date: any
    end_date: any
    computed_dates_info: QLabel

    def _on_time_range_changed(self, time_range_text: str) -> None:
        """
        Time range combo változás kezelése.

        Args:
            time_range_text: Új időtartam szöveg
        """
        if self._updating_state:
            return

        print(f"📅 DEBUG: Time range changed: {time_range_text}")

        if self.date_mode == "time_range":
            self._update_computed_dates()

            # Date range signal
            start_date, end_date = self._get_effective_date_range()
            self.date_range_changed.emit(start_date, end_date)

    def _on_manual_date_changed(self) -> None:
        """Manual date változás kezelése."""
        if self._updating_state:
            return

        # Validation
        start = self.start_date.date()
        end = self.end_date.date()

        if start > end:
            # Auto-fix
            if self.sender() == self.start_date:
                self.end_date.setDate(start)
            else:
                self.start_date.setDate(end)

        # Signal csak manual mode-ban
        if self.date_mode == "manual_dates":
            start_date, end_date = self._get_effective_date_range()
            self.date_range_changed.emit(start_date, end_date)
            print(f"📅 DEBUG: Manual dates changed: {start_date} → {end_date}")

    def _update_computed_dates(self) -> None:
        """Computed dates frissítése."""
        try:
            time_range_text = self.time_range_combo.currentText()

            # Évek számának kinyerése
            if "1 év" in time_range_text:
                years = 1
            elif "55 év" in time_range_text:
                years = 55
            elif "25 év" in time_range_text:
                years = 25
            elif "10 év" in time_range_text:
                years = 10
            elif "5 év" in time_range_text:
                years = 5
            else:
                years = 1  # Default

            # Dátumok számítása
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=years * 365)

            # Info label frissítése
            self.computed_dates_info.setText(
                f"Számított időszak: {start_date.strftime('%Y-%m-%d')} → {end_date.strftime('%Y-%m-%d')} ({years} év)"
            )

            print(
                f"📅 DEBUG: Computed dates: {start_date} → {end_date} ({years} years)"
            )

        except Exception as e:
            print(f"❌ ERROR: Computed dates update error: {e}")
            self.computed_dates_info.setText("Dátum számítási hiba")

    def _get_effective_date_range(self) -> Tuple[str, str]:
        """
        Effektív dátum tartomány lekérdezése.

        Returns:
            (start_date, end_date) tuple in ISO format
        """
        if self.date_mode == "time_range":
            # Automatikus számítás
            time_range_text = self.time_range_combo.currentText()

            if "1 év" in time_range_text:
                years = 1
            elif "55 év" in time_range_text:
                years = 55
            elif "25 év" in time_range_text:
                years = 25
            elif "10 év" in time_range_text:
                years = 10
            elif "5 év" in time_range_text:
                years = 5
            else:
                years = 1  # Default

            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=years * 365)

            return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")

        else:
            # Manual dátumok
            start_date = self.start_date.date().toString(Qt.ISODate)
            end_date = self.end_date.date().toString(Qt.ISODate)

            return start_date, end_date

    def _set_last_month(self) -> None:
        """Előző hónap beállítása."""
        today = QDate.currentDate()
        last_month = today.addMonths(-1)
        self.start_date.setDate(last_month)
        self.end_date.setDate(today)

    def _set_last_year(self) -> None:
        """Előző év beállítása."""
        today = QDate.currentDate()
        last_year = today.addYears(-1)
        self.start_date.setDate(last_year)
        self.end_date.setDate(today)

    def _set_years_back(self, years: int) -> None:
        """
        N évet visszamenő dátum beállítása.

        Args:
            years: Évek száma
        """
        today = QDate.currentDate()
        start = today.addYears(-years)
        end = today

        self.start_date.setDate(start)
        self.end_date.setDate(end)

        print(
            f"📅 DEBUG: Set {years} years back: {start.toString()} → {end.toString()}"
        )

    def _set_manual_dates_enabled(self, enabled: bool) -> None:
        """
        Manual date controls engedélyezése/letiltása.

        Args:
            enabled: Engedélyezett-e a manual dátumok
        """
        self.start_date.setEnabled(enabled)
        self.end_date.setEnabled(enabled)

        # Quick buttons
        for btn in [
            self.last_month_btn,
            self.last_year_btn,
            self.last_1year_btn,
            self.last_5years_btn,
            self.last_10years_btn,
            self.last_25years_btn,
            self.last_55years_btn,
        ]:
            btn.setEnabled(enabled)

        # Time range combo ellenkező
        self.time_range_combo.setEnabled(not enabled)
