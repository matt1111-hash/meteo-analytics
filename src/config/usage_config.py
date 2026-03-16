# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Compatibility wrapper for usage_config.py."""

from __future__ import annotations

from .usage_config_part1 import (
    _ensure_directories,
    _get_datetime_cls,
    _get_usage_tracking_file,
    _now,
    _resolve_config_attr,
)
from .usage_config_part2 import UsageTracker
from .usage_config_support import *
