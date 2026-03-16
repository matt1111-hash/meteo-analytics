#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mypy: ignore-errors

"""
API Helpers Provider Recommender - Get provider recommendations.
"""

from typing import Any, Dict

from .provider_validator import validate_provider_selection
from .source_selector import get_fallback_source_chain, get_optimal_data_source


def get_provider_recommendation(
    use_case: str, usage_stats: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Get provider recommendation based on use case.

    Args:
        use_case: Use case
        usage_stats: Usage statistics

    Returns:
        Recommendation dictionary
    """
    optimal_source = get_optimal_data_source(use_case, prefer_free=True)

    is_valid, error_msg = validate_provider_selection(optimal_source, usage_stats)

    if not is_valid:
        fallback_sources = get_fallback_source_chain(optimal_source)
        for fallback in fallback_sources:
            is_fallback_valid, _ = validate_provider_selection(fallback, usage_stats)
            if is_fallback_valid:
                return {
                    "recommended": fallback,
                    "original": optimal_source,
                    "reason": f"Fallback due to: {error_msg}",
                    "is_fallback": True,
                }

        return {
            "recommended": "open-meteo",
            "original": optimal_source,
            "reason": "Forced fallback to free provider",
            "is_fallback": True,
        }

    return {
        "recommended": optimal_source,
        "original": optimal_source,
        "reason": f"Optimal for {use_case}",
        "is_fallback": False,
    }
