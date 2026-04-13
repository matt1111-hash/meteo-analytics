# ruff: noqa: F403,noqa: I001
# mypy: ignore-errors
"""Mixin part 2 for AnalysisTypeWidget."""

from __future__ import annotations

from .analysis_type_widget_support import *


class AnalysisTypeWidgetPart2Mixin:  # noqa: D101
    def is_valid(self) -> bool:
        """
        Validáció - analysis type widget mindig valid.

        Returns:
            bool: Mindig True (valamelyik radio mindig be van jelölve)
        """
        return True

    def get_current_type(self) -> str:
        """
        Aktuális elemzési típus lekérdezése.

        Returns:
            str: "single_location", "region", vagy "county"
        """
        return self._current_type

    def set_current_type(self, analysis_type: str) -> bool:
        """
        Elemzési típus programozott beállítása.

        Args:
            analysis_type: Beállítandó típus

        Returns:
            bool: Sikeres volt-e
        """
        return self.set_state({"analysis_type": analysis_type})

    def set_enabled(self, enabled: bool) -> None:
        """
        Widget engedélyezése/letiltása.

        Args:
            enabled: Engedélyezett állapot
        """
        self.group.setEnabled(enabled)
        self.single_location_radio.setEnabled(enabled)
        self.region_radio.setEnabled(enabled)
        self.county_radio.setEnabled(enabled)

        print(f"🎯 DEBUG: AnalysisTypeWidget enabled state: {enabled}")

    # === SIZE HINT ===

    def sizeHint(self):
        """Preferált méret."""
        return self.group.sizeHint()

    def minimumSizeHint(self):
        """Minimum méret."""
        return self.group.minimumSizeHint()
