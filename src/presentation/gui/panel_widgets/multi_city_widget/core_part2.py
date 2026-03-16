# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Mixin part 2 for MultiCityWidget."""

from __future__ import annotations

from .core_support import *


class MultiCityWidgetPart2Mixin:
    def _clear_current_selection(self) -> None:
        """Aktuális mode selection törlése."""
        if self._current_mode == "region":
            self._selected_region = None
            print("🏞️ DEBUG: Régió selection törölve")
        else:
            self._selected_county = None
            print("🏛️ DEBUG: Megye selection törölve")

        self._combo_handler.update_info_label(
            self._current_mode, self._get_current_selection()
        )
        self._update_clear_button()
        self._emit_selection_changed()

    def _emit_selection_changed(self) -> None:
        """Selection changed signal kibocsátása."""
        current_selection = self._get_current_selection()

        selection_data = {
            "mode": self._current_mode,
            "selected": current_selection,
            "is_valid": self.is_valid(),
            "selection_text": self._get_selection_display_text(),
        }

        self.selection_changed.emit(selection_data)
        print(f"📡 DEBUG: selection_changed signal emitted: {selection_data}")

    # === CONTROL BUTTON HANDLERS ===

    def _clear_selection(self) -> None:
        """Kiválasztás törlése."""
        if self._updating_state:
            return

        print(f"❌ DEBUG: Selection törlése - {self._current_mode} mode")

        self._updating_state = True

        try:
            # ComboBox-ot placeholder-re állítás
            self.combo_box.setCurrentIndex(0)

            # State törlése
            self._clear_current_selection()

        finally:
            self._updating_state = False

    # === SIZE HINT ===

    def sizeHint(self):
        """Preferált méret."""
        return self.group.sizeHint()

    def minimumSizeHint(self):
        """Minimum méret."""
        return self.group.minimumSizeHint()
