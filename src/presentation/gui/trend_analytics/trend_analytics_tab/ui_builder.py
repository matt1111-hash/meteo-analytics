# mypy: ignore-errors
"""UI Builder - re-export for backward compatibility."""

from src.presentation.gui.trend_analytics.trend_analytics_tab.ui_builder import (
    create_controls_panel,
    create_dashboard_statistics_area,
    create_header,
    create_plotly_chart_container,
    setup_content_splitter,
)

__all__ = [
    "create_controls_panel",
    "create_dashboard_statistics_area",
    "create_header",
    "create_plotly_chart_container",
    "setup_content_splitter",
]
