#!/usr/bin/env python3
"""
Tests for src/domain/analytics/services/trend_data_processor.py
Trend data processor for DataFrame preparation and aggregation
"""

import pytest

from src.domain.analytics.services.trend_data_processor import TrendDataProcessor


class TestTrendDataProcessor:
    """Test TrendDataProcessor class."""

    @pytest.fixture
    def processor(self) -> TrendDataProcessor:
        """Create a TrendDataProcessor instance."""
        return TrendDataProcessor()
