# ruff: noqa: F401, F403,noqa: I001
# mypy: ignore-errors
"""Compatibility wrapper for ui_builder.py."""

from __future__ import annotations

from .ui_builder_part1 import (
    _create_results_group,
    _create_search_group,
    _create_selection_group,
    _get_group_box_style,
    _get_search_input_style,
    create_universal_location_selector_ui,
)
from .ui_builder_part2 import (
    _get_confirm_button_style,
    _get_results_list_style,
    _get_status_label_style,
)
from .ui_builder_support import *
