"""GUI headless bootstrap safeguards."""

import sys

import pytest
from src.presentation.gui.runtime_environment import is_headless_qt_platform


def _import_qt_widgets():
    """Import QtWidgets or skip when CI lacks Qt system libraries."""
    return pytest.importorskip(
        "PySide6.QtWidgets",
        reason="Qt system libraries are not available in this environment",
        exc_type=ImportError,
    )


def test_headless_detection_respects_offscreen_platform(monkeypatch) -> None:
    """Offscreen Qt platform is treated as headless."""
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")

    assert is_headless_qt_platform()


def test_trend_chart_uses_text_fallback_when_headless(monkeypatch) -> None:
    """Trend chart avoids QWebEngine construction in headless mode."""
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    qt_widgets = _import_qt_widgets()
    app = qt_widgets.QApplication.instance() or qt_widgets.QApplication(sys.argv)

    from src.presentation.gui.trend_analytics.trend_widgets.trend_chart import (  # noqa: PLC0415
        InteractiveTrendChart,
    )

    chart = InteractiveTrendChart()

    assert app is not None
    assert isinstance(chart.web_view, qt_widgets.QTextBrowser)
