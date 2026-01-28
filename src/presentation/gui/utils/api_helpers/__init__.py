#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API Helpers - Dual-API and Provider tracking functions.

🌍 DUAL-API SYSTEM:
✅ Open-Meteo API (FREE - Primary)
✅ Meteostat API (PREMIUM - Multi-city & Historical)
✅ Smart source routing
✅ Provider usage tracking
✅ Cost calculation
✅ Warning level detection
"""

# Source selection
from .source_selector import (
    get_optimal_data_source,
    get_source_display_name,
    validate_api_source_available,
    get_fallback_source_chain,
    log_api_source_selection,
)

# Provider tracking
from .provider_tracker import (
    format_provider_usage,
    calculate_provider_costs,
    get_provider_warning_level,
    format_provider_status,
    get_provider_icon,
    format_cost_summary,
    log_provider_usage_event,
)

# Provider validation
from .provider_validator import validate_provider_selection

# Provider recommendation
from .provider_recommender import get_provider_recommendation

__all__ = [
    # Source selection
    "get_optimal_data_source",
    "get_source_display_name",
    "validate_api_source_available",
    "get_fallback_source_chain",
    "log_api_source_selection",
    # Provider tracking
    "format_provider_usage",
    "calculate_provider_costs",
    "get_provider_warning_level",
    "format_provider_status",
    "get_provider_icon",
    "format_cost_summary",
    "log_provider_usage_event",
    # Provider validation
    "validate_provider_selection",
    # Provider recommendation
    "get_provider_recommendation",
]
