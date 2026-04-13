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

    from .core import TrendAnalyticsTab  # noqa: PLC0415

    app = QApplication(sys.argv)

    # Test window
    window = TrendAnalyticsTab()
    window.setWindowTitle("🚀 Enhanced Trend Analytics v4.2 - KPI DASHBOARD KÉSZ!")
    window.resize(1600, 1000)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    run_demo()
