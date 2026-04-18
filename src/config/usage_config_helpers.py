"""Monkeypatch-safe config helpers for usage tracking."""

from __future__ import annotations

import sys
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import cast


def _resolve_config_attr[T](attr: str, fallback: T) -> T:
    """Return config module attribute if it was monkeypatched in tests."""
    config_module = sys.modules.get("src.config")
    if config_module and hasattr(config_module, attr):
        return cast(T, getattr(config_module, attr))
    return fallback


def _get_usage_tracking_file(default_file: Path) -> Path:
    """Return the currently configured usage tracking file path."""
    return _resolve_config_attr("USAGE_TRACKING_FILE", default_file)


def _ensure_directories(default_fn: Callable[[], None]) -> None:
    """Call the (possibly monkeypatched) ensure_directories helper."""
    resolver: Callable[[], None] = _resolve_config_attr("ensure_directories", default_fn)
    resolver()


def _get_datetime_cls() -> type[datetime]:
    """Return datetime class from config for backward compatibility."""
    config_module = sys.modules.get("src.config")
    patched = getattr(config_module, "datetime", None) if config_module else None
    return patched or datetime


def _now() -> datetime:
    """Return current datetime honoring possible monkeypatches."""
    return _get_datetime_cls().now()
