#!/usr/bin/env python3
# mypy: ignore-errors

"""
GUI Component Interfaces - Dependency Injection Pattern
🚀 SOLID: Interface Segregation Principle
"""

from abc import ABC, abstractmethod


class IAnomalyConstants(ABC):
    """Abstract interface for anomaly constants."""

    @property
    @abstractmethod
    def WIND_HIGH_THRESHOLD(self) -> float:
        """High wind threshold in km/h."""
        pass

    @property
    @abstractmethod
    def WIND_EXTREME_THRESHOLD(self) -> float:
        """Extreme wind threshold in km/h."""
        pass

    @property
    @abstractmethod
    def WIND_HURRICANE_THRESHOLD(self) -> float:
        """Hurricane force wind threshold in km/h."""
        pass


class IConstantsProvider(ABC):
    """Abstract interface for constants provider."""

    @abstractmethod
    def get_wind_threshold(self, threshold_type: str) -> float:
        """Get wind threshold by type."""
        pass

    @abstractmethod
    def get_all_thresholds(self) -> dict[str, float]:
        """Get all available thresholds."""
        pass


class IWindspeedConstants(ABC):
    """Specific interface for wind constants."""

    @property
    @abstractmethod
    def HIGH(self) -> float:
        """High wind threshold."""
        pass

    @property
    @abstractmethod
    def EXTREME(self) -> float:
        """Extreme wind threshold."""
        pass
