#!/usr/bin/env python3

"""Runtime environment helpers for GUI startup decisions."""

from __future__ import annotations

import os
import sys


def is_headless_qt_platform() -> bool:
    """Return whether Qt is running without a real desktop display."""
    platform = os.environ.get("QT_QPA_PLATFORM", "").lower()
    if platform in {"minimal", "offscreen"}:
        return True

    has_display = bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))
    return sys.platform.startswith("linux") and not has_display


__all__ = ["is_headless_qt_platform"]
