#!/usr/bin/env python3
# mypy: ignore-errors

"""
Dialogs - Event Handlers

🖱️ Eseménykezelők

Képességek:
- Periódus típus változás kezelése

Fájl: src/presentation/gui/dialogs/event_handlers.py
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

from .calculation import _calculate_extremes


def _on_period_type_changed(self) -> None:
    """
    Periódus típus változásának kezelése.

    Args:
        self: ExtremeWeatherDialog instance
    """
    self.period_type = "daily" if self.daily_radio.isChecked() else "monthly"
    _calculate_extremes(self)
