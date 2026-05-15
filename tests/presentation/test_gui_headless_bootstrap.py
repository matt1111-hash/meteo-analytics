"""GUI headless bootstrap safeguards."""

from PySide6.QtWidgets import QTextBrowser
from src.presentation.gui.runtime_environment import is_headless_qt_platform


def test_headless_detection_respects_offscreen_platform(monkeypatch) -> None:
    """Offscreen Qt platform is treated as headless."""
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")

    assert is_headless_qt_platform()


def test_trend_chart_uses_text_fallback_when_headless(qapp, monkeypatch) -> None:
    """Trend chart avoids QWebEngine construction in headless mode."""
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")

    from src.presentation.gui.trend_analytics.trend_widgets.trend_chart import (  # noqa: PLC0415
        InteractiveTrendChart,
    )

    chart = InteractiveTrendChart()

    assert isinstance(chart.web_view, QTextBrowser)
