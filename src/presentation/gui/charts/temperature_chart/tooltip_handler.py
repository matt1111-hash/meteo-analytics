# ruff: noqa: F403,noqa: I001
# mypy: ignore-errors
"""Compatibility wrapper for tooltip_handler.py."""

from __future__ import annotations

from .tooltip_handler_part1 import TemperatureTooltipHandlerMixinPart1Mixin
from .tooltip_handler_part2 import TemperatureTooltipHandlerMixinPart2Mixin
from .tooltip_handler_support import *


class TemperatureTooltipHandlerMixin(
    TemperatureTooltipHandlerMixinPart1Mixin,
    TemperatureTooltipHandlerMixinPart2Mixin,
):
    """
    Tooltip handler mixin.
    """
