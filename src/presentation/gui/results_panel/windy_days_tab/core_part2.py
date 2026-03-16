# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Mixin part 2 for WindyDaysTab."""

from __future__ import annotations

from .core_support import *


class WindyDaysTabPart2Mixin:
    def update_data(
        self, weather_data: pd.DataFrame, location: str = "Ismeretlen helyszín"
    ) -> None:
        """Adatok frissítése."""
        update_data(self, weather_data, location)

    def clear_data(self) -> None:
        """Adatok és UI tartalom törlése."""
        clear_data(self)

    def get_current_threshold(self) -> float:
        """Aktuális küszöbérték lekérdezése."""
        return get_current_threshold(self)

    def set_threshold(self, threshold: float) -> None:
        """Küszöbérték beállítása."""
        set_threshold(self, threshold)
