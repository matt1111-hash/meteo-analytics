# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Compatibility wrapper for signal_handlers.py."""

from __future__ import annotations

from .signal_handlers_part1 import SignalHandlersMixinPart1Mixin
from .signal_handlers_part2 import SignalHandlersMixinPart2Mixin
from .signal_handlers_support import *


class SignalHandlersMixin(SignalHandlersMixinPart1Mixin, SignalHandlersMixinPart2Mixin):
    """
    🔗 Signal handler mixin a HungarianLocationSelector számára.
    """
