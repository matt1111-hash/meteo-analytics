#!/usr/bin/env python3
# mypy: ignore-errors

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
# Provider recommendation
from .provider_recommender import get_provider_recommendation

# Provider tracking
from .provider_tracker import (
    calculate_provider_costs,
    format_cost_summary,
    format_provider_status,
    format_provider_usage,
    get_provider_icon,
    get_provider_warning_level,
    log_provider_usage_event,
)

# Provider validation
from .provider_validator import validate_provider_selection
from .source_selector import (
    get_fallback_source_chain,
    get_optimal_data_source,
    get_source_display_name,
    log_api_source_selection,
    validate_api_source_available,
)

__all__ = [
    "calculate_provider_costs",
    "format_cost_summary",
    "format_provider_status",
    # Provider tracking
    "format_provider_usage",
    "get_fallback_source_chain",
    # Source selection
    "get_optimal_data_source",
    "get_provider_icon",
    # Provider recommendation
    "get_provider_recommendation",
    "get_provider_warning_level",
    "get_source_display_name",
    "log_api_source_selection",
    "log_provider_usage_event",
    "validate_api_source_available",
    # Provider validation
    "validate_provider_selection",
]
