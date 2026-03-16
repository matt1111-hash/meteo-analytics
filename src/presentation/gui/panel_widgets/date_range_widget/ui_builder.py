# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Compatibility wrapper for ui_builder.py."""

from __future__ import annotations

from .ui_builder_part1 import create_manual_dates_group, create_time_range_group
from .ui_builder_part2 import apply_label_styling, register_for_theming
from .ui_builder_support import *
