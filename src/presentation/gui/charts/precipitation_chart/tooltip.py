# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Compatibility wrapper for tooltip.py."""

from __future__ import annotations

from .tooltip_part1 import _find_closest_chart_point
from .tooltip_part2 import _format_tooltip_text
from .tooltip_part3 import _hide_tooltip, _show_tooltip
from .tooltip_support import *
