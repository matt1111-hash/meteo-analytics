"""Regression coverage for the real extreme-weather menu and dialog import chain."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest
from PySide6.QtCore import QTimer
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QDialog, QMainWindow


@pytest.fixture
def qapp(monkeypatch: pytest.MonkeyPatch) -> QApplication:
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    return QApplication.instance() or QApplication([])


def test_dialog_package_exports_both_dialogs_and_builder() -> None:
    from src.presentation.gui.dialogs import (  # noqa: PLC0415
        AnomalySettingsDialog,
        ExtremeWeatherDialog,
    )
    from src.presentation.gui.dialogs.anomaly_settings_dialog.ui_builder import (  # noqa: PLC0415
        AnomalySettingsUIBuilder,
    )

    assert issubclass(AnomalySettingsDialog, QDialog)
    assert issubclass(ExtremeWeatherDialog, QDialog)
    assert callable(AnomalySettingsUIBuilder)


def test_menu_opens_real_dialog_with_loaded_weather(
    qapp: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    from src.presentation.gui.dialogs import ExtremeWeatherDialog  # noqa: PLC0415
    from src.presentation.gui.windows.main_window_actions import dialogs  # noqa: PLC0415
    from src.presentation.gui.windows.main_window_actions_mixin import (  # noqa: PLC0415
        MainWindowActionsMixin,
    )
    from src.presentation.gui.windows.menu_builder import create_menu_bar  # noqa: PLC0415

    class Window(MainWindowActionsMixin, QMainWindow):
        """Run the production menu actions without constructing unrelated services."""

    window = Window()
    window.results_panel = SimpleNamespace(
        current_city="Budapest",
        current_data={
            "daily": {
                "time": ["2026-09-24", "2026-09-25"],
                "temperature_2m_max": [20.0, 25.0],
                "temperature_2m_min": [10.0, 12.0],
                "precipitation_sum": [0.0, 5.0],
                "windspeed_10m_max": [15.0, 30.0],
            }
        },
    )
    errors: list[str] = []
    opened: list[Any] = []
    monkeypatch.setattr(dialogs, "show_error", lambda _window, message: errors.append(message))
    original_exec = ExtremeWeatherDialog.exec

    def close_modal(dialog: ExtremeWeatherDialog) -> int:
        opened.append(dialog)
        QTimer.singleShot(0, dialog.accept)
        return original_exec(dialog)

    monkeypatch.setattr(ExtremeWeatherDialog, "exec", close_modal)
    try:
        create_menu_bar(window)
        action = next(
            item for item in window.findChildren(QAction) if item.text() == "Szélsőséges Időjárás"
        )
        action.trigger()

        assert errors == []
        assert len(opened) == 1
        dialog = opened[0]
        assert "Budapest" in dialog.windowTitle()
        assert dialog.data is window.results_panel.current_data
        assert dialog.extreme_table.item(0, 1).text() == "25.0 °C"
        dialog.monthly_radio.setChecked(True)
        assert dialog.extreme_table.item(0, 0).text() == "Legmelegebb hónap (max)"
    finally:
        window.close()
        window.deleteLater()
        qapp.processEvents()


@pytest.mark.parametrize("panel", [None, SimpleNamespace(current_data=None)])
def test_no_data_reports_actionable_message(
    qapp: QApplication, monkeypatch: pytest.MonkeyPatch, panel: Any
) -> None:
    from src.presentation.gui.windows.main_window_actions import dialogs  # noqa: PLC0415

    errors: list[str] = []
    monkeypatch.setattr(dialogs, "show_error", lambda _window, message: errors.append(message))
    dialogs.show_extreme_weather(SimpleNamespace(results_panel=panel))

    assert errors == ["Nincs megjelenített eredmény a szélsőséges időjárás elemzéséhez."]
