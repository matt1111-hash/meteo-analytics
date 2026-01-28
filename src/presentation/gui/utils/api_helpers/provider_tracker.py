#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API Helpers Provider Tracker - Track provider usage and costs.
"""

from typing import Any, Dict

from .source_selector import get_source_display_name


def format_provider_usage(usage_stats: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
    """
    Format provider usage statistics for GUI display.

    Args:
        usage_stats: Usage statistics from UsageTracker

    Returns:
        Formatted strings dictionary
    """
    formatted = {}

    for provider_name, stats in usage_stats.items():
        if provider_name == 'open-meteo':
            formatted[provider_name] = "🌍 Ingyenes (korlátlan)"
        else:
            requests = stats.get('requests', 0)
            limit = stats.get('limit', 10000)
            usage_percent = (requests / limit) * 100 if limit > 0 else 0
            formatted[provider_name] = f"💎 {requests:,}/{limit:,} ({usage_percent:.1f}%)"

    return formatted


def calculate_provider_costs(usage_stats: Dict[str, Dict[str, Any]]) -> Dict[str, float]:
    """
    Calculate provider costs based on usage.

    Args:
        usage_stats: Usage statistics

    Returns:
        Costs dictionary ($USD)
    """
    costs = {}

    for provider_name, stats in usage_stats.items():
        if provider_name == 'open-meteo':
            costs[provider_name] = 0.0
        elif provider_name == 'meteostat':
            requests = stats.get('requests', 0)
            cost_per_request = 10.0 / 10000
            costs[provider_name] = requests * cost_per_request
        else:
            costs[provider_name] = 0.0

    return costs


def get_provider_warning_level(provider_name: str, usage_stats: Dict[str, Dict[str, Any]]) -> str:
    """
    Determine provider usage warning level.

    Args:
        provider_name: Provider name
        usage_stats: Usage statistics

    Returns:
        Warning level or None
    """
    if provider_name == 'open-meteo':
        return None

    stats = usage_stats.get(provider_name, {})
    requests = stats.get('requests', 0)
    limit = stats.get('limit', 10000)

    if limit <= 0:
        return None

    usage_percent = (requests / limit) * 100

    if usage_percent >= 95:
        return "critical"
    elif usage_percent >= 80:
        return "warning"
    elif usage_percent >= 60:
        return "info"
    else:
        return None


def format_provider_status(provider_name: str, is_current: bool, usage_stats: Dict[str, Dict[str, Any]]) -> str:
    """
    Generate provider status string for GUI.

    Args:
        provider_name: Provider name
        is_current: Whether currently selected
        usage_stats: Usage statistics

    Returns:
        Formatted status string
    """
    display_name = get_source_display_name(provider_name)

    if provider_name == 'auto':
        return "🤖 Automatikus routing"

    status_parts = [display_name]

    if is_current:
        status_parts.append("(aktív)")

    if provider_name != 'open-meteo':
        warning_level = get_provider_warning_level(provider_name, usage_stats)
        if warning_level == "critical":
            status_parts.append("⚠️ LIMIT")
        elif warning_level == "warning":
            status_parts.append("⚠️")
        elif warning_level == "info":
            status_parts.append("📊")

    return " ".join(status_parts)


def get_provider_icon(provider_name: str) -> str:
    """
    Get provider icon.

    Args:
        provider_name: Provider name

    Returns:
        Emoji icon
    """
    icons = {
        'auto': '🤖',
        'open-meteo': '🌍',
        'meteostat': '💎'
    }

    return icons.get(provider_name, '🔧')


def format_cost_summary(usage_stats: Dict[str, Dict[str, Any]]) -> str:
    """
    Format cost summary.

    Args:
        usage_stats: Usage statistics

    Returns:
        Formatted cost string
    """
    costs = calculate_provider_costs(usage_stats)
    total_cost = sum(costs.values())

    if total_cost == 0:
        return "💰 Havi költség: $0.00 (csak ingyenes API-k)"
    else:
        return f"💰 Havi költség: ~${total_cost:.2f}"


def log_provider_usage_event(provider_name: str, use_case: str, success: bool) -> None:
    """
    Log provider usage event.

    Args:
        provider_name: Provider name
        use_case: Use case
        success: Whether successful
    """
    import logging
    logger = logging.getLogger(__name__)

    status = "SUCCESS" if success else "FAILED"
    display_name = get_source_display_name(provider_name)

    logger.info(f"PROVIDER USAGE: {display_name} for {use_case} - {status}")
