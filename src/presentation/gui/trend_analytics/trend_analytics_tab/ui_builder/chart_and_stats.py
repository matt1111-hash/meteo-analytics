# mypy: ignore-errors
"""UI Builder - Chart and Statistics sections."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QScrollArea,
    QSplitter,
    QVBoxLayout,
    QWidget,
)


def create_plotly_chart_container(parent_widget: QWidget) -> QWidget:
    """Plotly chart container létrehozása."""
    container = QFrame()
    container.setFrameStyle(QFrame.Box)
    container.setStyleSheet("""
        QFrame {
            background-color: white;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 10px;
        }
    """)

    layout = QVBoxLayout()

    chart_title = QLabel("📈 Interaktív Trend Vizualizáció")
    chart_title.setFont(QFont("Arial", 14, QFont.Bold))
    chart_title.setAlignment(Qt.AlignCenter)
    layout.addWidget(chart_title)

    from ...trend_widgets import InteractiveTrendChart  # noqa: PLC0415

    chart = InteractiveTrendChart()
    layout.addWidget(chart)

    container.setLayout(layout)
    parent_widget.layout().addWidget(container)

    return chart


def create_dashboard_statistics_area(parent_widget: QWidget) -> QWidget:
    """Dashboard KPI kártyák területe - QScrollArea-ban."""
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    scroll_area.setFrameStyle(QFrame.Box)
    scroll_area.setStyleSheet("""
        QScrollArea {
            background-color: white;
            border: 1px solid #dee2e6;
            border-radius: 8px;
        }
    """)

    stats_widget = QWidget()
    stats_layout = QVBoxLayout()
    stats_layout.setContentsMargins(10, 10, 10, 10)

    from ...trend_widgets import EnhancedStatisticsPanel  # noqa: PLC0415

    statistics_panel = EnhancedStatisticsPanel()
    stats_layout.addWidget(statistics_panel, stretch=1)

    stats_layout.addStretch()

    stats_widget.setLayout(stats_layout)
    scroll_area.setWidget(stats_widget)

    parent_widget.layout().addWidget(scroll_area)

    return statistics_panel


def setup_content_splitter(
    parent_widget: QWidget, chart_container: QWidget, stats_area: QWidget
) -> None:
    """QSplitter implementáció."""
    content_splitter = QSplitter(Qt.Horizontal)
    content_splitter.setChildrenCollapsible(False)

    chart_container.setMinimumHeight(400)
    chart_container.setMinimumWidth(600)
    content_splitter.addWidget(chart_container)

    stats_area.setMinimumWidth(400)
    content_splitter.addWidget(stats_area)

    content_splitter.setSizes([2, 1])
    content_splitter.setStretchFactor(0, 2)
    content_splitter.setStretchFactor(1, 1)

    content_splitter.setStyleSheet("""
        QSplitter {
            background-color: #f8f9fa;
            border: none;
        }
        QSplitter::handle {
            background-color: #dee2e6;
            width: 8px;
            margin: 2px;
            border-radius: 4px;
        }
        QSplitter::handle:hover {
            background-color: #6c757d;
        }
    """)

    parent_widget.layout().addWidget(content_splitter, stretch=1)
