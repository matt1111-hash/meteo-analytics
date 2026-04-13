#!/usr/bin/env python3
# mypy: ignore-errors

"""
API Helpers Provider Validator - Validate provider selections.
"""

from .provider_tracker import get_provider_warning_level
from .source_selector import validate_api_source_available


def validate_provider_selection(provider_name: str, usage_stats) -> tuple[bool, str]:
    """
    Validate provider selection.

    Args:
        provider_name: Provider name
        usage_stats: Usage statistics

    Returns:
        (valid, error_message) tuple
    """
    if provider_name == "auto":
        return True, ""

    if provider_name == "open-meteo":
        return True, ""

    if not validate_api_source_available(provider_name):
        return False, f"{provider_name} API kulcs hiányzik vagy érvénytelen"

    warning_level = get_provider_warning_level(provider_name, usage_stats)
    if warning_level == "critical":
        return False, f"{provider_name} havi limit túllépve"

    return True, ""
