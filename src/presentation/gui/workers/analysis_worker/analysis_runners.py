# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Compatibility wrapper for analysis_runners.py."""

from __future__ import annotations

from .analysis_runners_part1 import AnalysisRunnersPart1Mixin
from .analysis_runners_part2 import AnalysisRunnersPart2Mixin
from .analysis_runners_support import *


class AnalysisRunners(AnalysisRunnersPart1Mixin, AnalysisRunnersPart2Mixin):
    """Run different analysis types based on request."""
