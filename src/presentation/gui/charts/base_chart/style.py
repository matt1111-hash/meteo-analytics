# mypy: ignore-errors
"""Base chart style configuration."""

import matplotlib

from src.presentation.gui.charts.base_chart.constants import MATPLOTLIB_PARAMS


def setup_matplotlib_style() -> None:
    """Configure matplotlib global style settings."""
    matplotlib.rcParams.update(MATPLOTLIB_PARAMS)


def setup_emoji_fonts() -> None:
    """Setup emoji-compatible font configuration."""
    pass  # Already configured in MATPLOTLIB_PARAMS
