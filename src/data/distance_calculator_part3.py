# ruff: noqa: F403, F405,noqa: I001
# mypy: ignore-errors
"""Mixin part 3 for DistanceCalculator."""

from __future__ import annotations

from .distance_calculator_support import *


class DistanceCalculatorPart3Mixin:  # noqa: D101
    def get_calculation_statistics(self) -> Dict[str, Any]:
        """Get calculation statistics."""
        return {
            "total_calculations": self.calculation_count,
            "default_unit": self.default_unit.value,
        }
