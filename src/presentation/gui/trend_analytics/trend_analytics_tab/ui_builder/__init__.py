"""UI Builder - re-export for backward compatibility."""
from src.presentation.gui.trend_analytics.trend_analytics_tab.ui_builder.header_and_controls import (
    create_header,
    create_controls_panel,
)
from src.presentation.gui.trend_analytics.trend_analytics_tab.ui_builder.chart_and_stats import (
    create_plotly_chart_container,
    create_dashboard_statistics_area,
    setup_content_splitter,
)

__all__ = [
    "create_header",
    "create_controls_panel",
    "create_plotly_chart_container",
    "create_dashboard_statistics_area",
    "setup_content_splitter",
]
