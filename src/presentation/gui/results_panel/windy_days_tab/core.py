# ruff: noqa: F403, F405,noqa: I001
# mypy: ignore-errors
"""Compatibility wrapper for core.py."""

from __future__ import annotations

from .core_part1 import WindyDaysTabPart1Mixin
from .core_part2 import WindyDaysTabPart2Mixin
from .core_support import *


class WindyDaysTab(WindyDaysTabPart1Mixin, WindyDaysTabPart2Mixin, QWidget):
    """
    Szeles napok analízis tab komponens.

    Megjeleníti a szeles napok havi eloszlását oszlopdiagramon,
    beállítható küszöbértékkel és részletes statisztikákkal.
    """

    # Signals
    analysis_completed = Signal(dict)
    error_occurred = Signal(str)
    export_requested = Signal(str, str)  # file_type, file_path
