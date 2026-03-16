# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Compatibility wrapper for signal_manager.py."""

from __future__ import annotations

from .signal_manager_part1 import SignalManagerPart1Mixin
from .signal_manager_part2 import SignalManagerPart2Mixin
from .signal_manager_support import *


class SignalManager(SignalManagerPart1Mixin, SignalManagerPart2Mixin):
    """
    Kezeli az alkalmazás összes signal-slot kapcsolatát.

    Ez az osztály felelős a különböző UI komponensek (ControlPanel, ResultsPanel, stb.)
    és az AppController közötti kommunikáció létrehozásáért.
    """


# Export
__all__ = ["SignalManager"]
