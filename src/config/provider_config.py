# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Compatibility wrapper for provider_config.py."""

from __future__ import annotations

from .provider_config_part1 import (
    ProviderConfig,
    _ensure_directories,
    _freeze_value,
    _get_provider_prefs_file,
    _resolve_config_attr,
)
from .provider_config_part2 import (
    UserPreferences,
    get_resolved_provider,
    validate_provider_selection,
)
from .provider_config_support import *
