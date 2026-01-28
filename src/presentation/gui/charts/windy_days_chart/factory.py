#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Windy Days Chart - Factory

🏭 Factory és demo függvények

Képességek:
- Factory függvény
- Demo függvény

Fájl: src/presentation/gui/charts/windy_days_chart/factory.py
"""

import logging
from typing import Optional

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

logger = logging.getLogger(__name__)


def create_windy_days_chart(parent: Optional[QWidget] = None):
    """
    WindyDaysChart példány létrehozása.

    Args:
        parent: Szülő widget

    Returns:
        WindyDaysChart példány
    """
    from .core import WindyDaysChart
    return WindyDaysChart(parent)


# Demo és tesztelési funkciók
def demo_windy_days_chart():
    """Demo a WindyDaysChart tesztelésére."""
    import sys

    app = QApplication(sys.argv)

    # Test adatok
    demo_data = {
        'chart_data': {
            'months': ['Január', 'Február', 'Március', 'Április', 'Május', 'Június'],
            'counts': [12, 8, 15, 6, 3, 9],
            'percentages': [38.7, 28.6, 48.4, 20.0, 9.7, 30.0],
            'labels': [
                'Január: 12 szeles nap (38.7%)',
                'Február: 8 szeles nap (28.6%)',
                'Március: 15 szeles nap (48.4%)',
                'Április: 6 szeles nap (20.0%)',
                'Május: 3 szeles nap (9.7%)',
                'Június: 9 szeles nap (30.0%)'
            ]
        },
        'threshold_kmh': 43.0,
        'location_name': 'Budapest'
    }

    # Main window
    window = QMainWindow()
    central_widget = QWidget()
    layout = QVBoxLayout(central_widget)

    # Chart
    chart = create_windy_days_chart()
    chart.update_data(demo_data)

    layout.addWidget(chart)
    window.setCentralWidget(central_widget)
    window.setWindowTitle("WindyDaysChart Demo")
    window.resize(800, 600)
    window.show()

    sys.exit(app.exec())
