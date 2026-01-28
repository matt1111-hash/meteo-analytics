#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WeatherDataWorker Provider Selector - Select optimal data provider.
"""

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .core import WeatherDataWorker


class ProviderSelector:
    """Select optimal data provider."""

    def __init__(self, worker: 'WeatherDataWorker'):
        """
        Initialize provider selector.

        Args:
            worker: WeatherDataWorker instance
        """
        self._worker = worker

    def select_optimal(self) -> Optional[str]:
        """
        Select optimal provider based on preference and availability.

        Returns:
            Selected provider name or None
        """
        from ...utils import (
            get_optimal_data_source,
            validate_api_source_available,
            get_fallback_source_chain,
        )

        if self._worker.preferred_provider == "auto":
            # Automatic routing
            optimal = get_optimal_data_source("single_city", prefer_free=True)

            if validate_api_source_available(optimal):
                return optimal
            else:
                # Fallback to first available provider
                fallback_chain = get_fallback_source_chain(optimal)
                for provider in fallback_chain:
                    if validate_api_source_available(provider):
                        return provider
                return None
        else:
            # Explicit provider selection
            if validate_api_source_available(self._worker.preferred_provider):
                return self._worker.preferred_provider
            else:
                self._worker.provider_validation_failed.emit(
                    self._worker.preferred_provider,
                    "Provider nem elérhető vagy API kulcs hiányzik"
                )
                # Auto fallback
                return self.select_optimal() if self._worker.preferred_provider != "auto" else None
