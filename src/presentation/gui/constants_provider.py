#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mypy: ignore-errors

"""
Constants Provider - Dependency Injection Implementation
🎯 Single Responsibility Principle
"""

from typing import Dict

from src.presentation.gui.interfaces import IConstantsProvider, IWindspeedConstants


class ConstantsProvider(IConstantsProvider):
    """Concrete implementation of constants provider."""

    def __init__(self):
        # Wind thresholds (moved from utils to here)
        self._wind_thresholds = {
            "high": 70.0,  # WIND_HIGH_THRESHOLD
            "extreme": 100.0,  # WIND_EXTREME_THRESHOLD
            "hurricane": 120.0,  # WIND_HURRICANE_THRESHOLD
        }

    def get_wind_threshold(self, threshold_type: str) -> float:
        """Get wind threshold by type."""
        return self._wind_thresholds.get(threshold_type, 70.0)

    def get_all_thresholds(self) -> Dict[str, float]:
        """Get all available thresholds."""
        return self._wind_thresholds.copy()


class WindspeedConstantsAdapter(IWindspeedConstants):
    """Adapter to provide windspeed constants via interface."""

    @property
    def HIGH(self) -> float:
        """High wind threshold."""
        return 70.0

    @property
    def EXTREME(self) -> float:
        """Extreme wind threshold."""
        return 100.0
