#!/usr/bin/env python3
# mypy: ignore-errors

"""
Trend Analytics Tab - Demo

🧪 Standalone testing kód

Fájl: src/presentation/gui/trend_analytics/trend_analytics_tab/demo.py
"""

import sys


def run_demo():
    """
    Standalone testing - futtatható demo.
    """
    from PySide6.QtWidgets import QApplication  # noqa: PLC0415

    from src.presentation.gui.gui_composition_root import build_gui_services  # noqa: PLC0415

    from .core import TrendAnalyticsTab  # noqa: PLC0415

    app = QApplication(sys.argv)

    # Test window — ports wired via the composition root
    services = build_gui_services()
    window = TrendAnalyticsTab(services.city_manager, services.weather_client)
    window.setWindowTitle("🚀 Enhanced Trend Analytics v4.2 - KPI DASHBOARD KÉSZ!")
    window.resize(1600, 1000)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    run_demo()
