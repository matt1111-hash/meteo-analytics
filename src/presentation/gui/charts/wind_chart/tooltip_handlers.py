# ruff: noqa: F403,noqa: I001
# mypy: ignore-errors
"""Compatibility wrapper for tooltip_handlers.py."""

from __future__ import annotations

from .tooltip_handlers_part1 import WindTooltipHandlerPart1Mixin
from .tooltip_handlers_part2 import WindTooltipHandlerPart2Mixin
from .tooltip_handlers_support import *


class WindTooltipHandler(WindTooltipHandlerPart1Mixin, WindTooltipHandlerPart2Mixin):
    """
    Handle tooltip display for wind chart.

    💨 PROFESSIONAL WIND TOOLTIP:
    - Magyar szélkategóriák és Beaufort skála
    - Széljárás leírások
    - Meteorológiai hatások
    - Smart positioning
    """
