#!/usr/bin/env python3
# mypy: ignore-errors

"""
Results Panel Components - Clean Architecture Refactor.

This package exposes the public results panel API without importing Qt-heavy
modules during package initialization. Headless tests can therefore import
submodules from this package without requiring desktop GUI libraries.
"""

from __future__ import annotations

from importlib import import_module
from typing import Any

__all__ = ["DataProcessor", "ProgressManager", "ResultsPanel", "TabManager"]


def __getattr__(name: str) -> Any:
    """Lazily import public results-panel classes on first access."""
    module_map = {
        "ResultsPanel": ".results_panel",
        "ProgressManager": ".progress_manager",
        "TabManager": ".tab_manager",
        "DataProcessor": ".data_processor",
    }
    module_name = module_map.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module = import_module(module_name, __name__)
    return getattr(module, name)
