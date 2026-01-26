#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global Weather Analyzer - GUI API Helpers Module.
Dual-API és Provider tracking funkciók.

🌍 DUAL-API SYSTEM:
✅ Open-Meteo API (FREE - Primary)
✅ Meteostat API (PREMIUM - Multi-city & Historical)
✅ Smart source routing
✅ Provider usage tracking
✅ Cost calculation
✅ Warning level detection
"""

import logging
import os
from typing import Any, Dict, List, Optional, Tuple

from .constants import APIConstants, DataConstants

logger = logging.getLogger(__name__)


def get_optimal_data_source(use_case: str, prefer_free: bool = True) -> str:
    """
    Optimális adatforrás meghatározása használati eset alapján.

    Args:
        use_case: Használati eset ("single_city", "multi_city", stb.)
        prefer_free: Ingyenes forrás preferálása

    Returns:
        Optimális data source azonosító
    """
    if use_case in DataConstants.USE_CASE_SOURCE_MAPPING:
        optimal_source = DataConstants.USE_CASE_SOURCE_MAPPING[use_case]

        # Ha ingyenes forrást preferálunk és az optimális fizetős
        if prefer_free and optimal_source == "meteostat":
            # Ellenőrizzük, hogy az open-meteo képes-e kezelni
            if DataConstants.SOURCE_CAPABILITIES["open-meteo"].get(use_case.replace("_", "-"), False):
                return "open-meteo"

        return optimal_source

    # Default fallback
    return "open-meteo"


def get_source_display_name(source_id: str) -> str:
    """
    Adatforrás megjelenítési neve.

    Args:
        source_id: Source azonosító

    Returns:
        Felhasználóbarát megjelenítési név
    """
    return APIConstants.SOURCE_DISPLAY_NAMES.get(source_id, f"Unknown Source ({source_id})")


def validate_api_source_available(source_id: str) -> bool:
    """
    API forrás elérhetőségének validálása.

    Args:
        source_id: Source azonosító

    Returns:
        Elérhető-e az API
    """
    if source_id == "open-meteo":
        return True  # Mindig elérhető (nincs API kulcs szükséges)

    elif source_id == "meteostat":
        # Environment variable ellenőrzése
        api_key = os.getenv("METEOSTAT_API_KEY")
        return bool(api_key and len(api_key.strip()) >= 32)

    return False


def get_fallback_source_chain(primary_source: str) -> List[str]:
    """
    Fallback forrás lánc meghatározása.

    Args:
        primary_source: Elsődleges forrás

    Returns:
        Fallback források listája
    """
    available_sources = [
        source for source in DataConstants.DATA_SOURCE_PRIORITY
        if validate_api_source_available(source)
    ]

    # Primary source előre helyezése
    if primary_source in available_sources:
        available_sources.remove(primary_source)
        available_sources.insert(0, primary_source)

    return available_sources


def log_api_source_selection(use_case: str, selected_source: str, reason: str = "") -> None:
    """
    API forrás kiválasztás naplózása.

    Args:
        use_case: Használati eset
        selected_source: Kiválasztott forrás
        reason: Kiválasztás indoka
    """
    display_name = get_source_display_name(selected_source)
    logger.info(f"API SOURCE SELECTION: {use_case} → {display_name} {reason}")


# === ÚJ: PROVIDER TRACKING FUNCTIONS ===

def format_provider_usage(usage_stats: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
    """
    🌍 Provider usage statistics formázása GUI megjelenítéshez.

    Args:
        usage_stats: Usage statistics a UsageTracker-ből

    Returns:
        Formázott strings dictionary
    """
    formatted = {}

    for provider_name, stats in usage_stats.items():
        if provider_name == 'open-meteo':
            # Free provider - no limits
            formatted[provider_name] = "🌍 Ingyenes (korlátlan)"
        else:
            # Premium provider - show usage/limit
            requests = stats.get('requests', 0)
            limit = stats.get('limit', 10000)
            usage_percent = (requests / limit) * 100 if limit > 0 else 0

            formatted[provider_name] = f"💎 {requests:,}/{limit:,} ({usage_percent:.1f}%)"

    return formatted


def calculate_provider_costs(usage_stats: Dict[str, Dict[str, Any]]) -> Dict[str, float]:
    """
    🌍 Provider costs számítása usage alapján.

    Args:
        usage_stats: Usage statistics

    Returns:
        Költségek dictionary ($USD)
    """
    costs = {}

    for provider_name, stats in usage_stats.items():
        if provider_name == 'open-meteo':
            costs[provider_name] = 0.0  # Free
        elif provider_name == 'meteostat':
            # $10/month for 10k requests
            requests = stats.get('requests', 0)
            cost_per_request = 10.0 / 10000  # $0.001 per request
            costs[provider_name] = requests * cost_per_request
        else:
            costs[provider_name] = 0.0

    return costs


def get_provider_warning_level(provider_name: str, usage_stats: Dict[str, Dict[str, Any]]) -> Optional[str]:
    """
    🌍 Provider usage warning level meghatározása.

    Args:
        provider_name: Provider neve
        usage_stats: Usage statistics

    Returns:
        Warning level vagy None
    """
    if provider_name == 'open-meteo':
        return None  # Free provider, no warnings

    stats = usage_stats.get(provider_name, {})
    requests = stats.get('requests', 0)
    limit = stats.get('limit', 10000)

    if limit <= 0:
        return None

    usage_percent = (requests / limit) * 100

    if usage_percent >= 95:
        return "critical"  # 95%+ usage
    elif usage_percent >= 80:
        return "warning"   # 80%+ usage
    elif usage_percent >= 60:
        return "info"      # 60%+ usage
    else:
        return None        # Normal usage


def format_provider_status(provider_name: str, is_current: bool, usage_stats: Dict[str, Dict[str, Any]]) -> str:
    """
    🌍 Provider status string generálása GUI-hoz.

    Args:
        provider_name: Provider neve
        is_current: Jelenleg kiválasztott-e
        usage_stats: Usage statistics

    Returns:
        Formázott status string
    """
    display_name = get_source_display_name(provider_name)

    if provider_name == 'auto':
        return "🤖 Automatikus routing"

    status_parts = [display_name]

    if is_current:
        status_parts.append("(aktív)")

    # Usage info hozzáadása
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
    🌍 Provider icon visszaadása.

    Args:
        provider_name: Provider neve

    Returns:
        Emoji icon
    """
    icons = {
        'auto': '🤖',
        'open-meteo': '🌍',
        'meteostat': '💎'
    }

    return icons.get(provider_name, '🔧')


def validate_provider_selection(provider_name: str, usage_stats: Dict[str, Dict[str, Any]]) -> Tuple[bool, str]:
    """
    🌍 Provider választás validálása.

    Args:
        provider_name: Provider neve
        usage_stats: Usage statistics

    Returns:
        (valid, error_message) tuple
    """
    if provider_name == 'auto':
        return True, ""

    if provider_name == 'open-meteo':
        return True, ""  # Always available

    # Check API availability
    if not validate_api_source_available(provider_name):
        return False, f"{provider_name} API kulcs hiányzik vagy érvénytelen"

    # Check usage limits
    warning_level = get_provider_warning_level(provider_name, usage_stats)
    if warning_level == "critical":
        return False, f"{provider_name} havi limit túllépve"

    return True, ""


def get_provider_recommendation(use_case: str, usage_stats: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    🌍 Provider recommendation use case alapján.

    Args:
        use_case: Használati eset
        usage_stats: Usage statistics

    Returns:
        Recommendation dictionary
    """
    optimal_source = get_optimal_data_source(use_case, prefer_free=True)

    # Fallback if optimal source not available
    is_valid, error_msg = validate_provider_selection(optimal_source, usage_stats)

    if not is_valid:
        fallback_sources = get_fallback_source_chain(optimal_source)
        for fallback in fallback_sources:
            is_fallback_valid, _ = validate_provider_selection(fallback, usage_stats)
            if is_fallback_valid:
                return {
                    'recommended': fallback,
                    'original': optimal_source,
                    'reason': f"Fallback due to: {error_msg}",
                    'is_fallback': True
                }

        # No valid providers available
        return {
            'recommended': 'open-meteo',  # Always available
            'original': optimal_source,
            'reason': "Forced fallback to free provider",
            'is_fallback': True
        }

    return {
        'recommended': optimal_source,
        'original': optimal_source,
        'reason': f"Optimal for {use_case}",
        'is_fallback': False
    }


def format_cost_summary(usage_stats: Dict[str, Dict[str, Any]]) -> str:
    """
    🌍 Költség összefoglaló formázása.

    Args:
        usage_stats: Usage statistics

    Returns:
        Formázott költség string
    """
    costs = calculate_provider_costs(usage_stats)
    total_cost = sum(costs.values())

    if total_cost == 0:
        return "💰 Havi költség: $0.00 (csak ingyenes API-k)"
    else:
        return f"💰 Havi költség: ~${total_cost:.2f}"


def log_provider_usage_event(provider_name: str, use_case: str, success: bool) -> None:
    """
    🌍 Provider usage esemény naplózása.

    Args:
        provider_name: Provider neve
        use_case: Használati eset
        success: Sikeres volt-e
    """
    status = "SUCCESS" if success else "FAILED"
    display_name = get_source_display_name(provider_name)

    logger.info(f"PROVIDER USAGE: {display_name} for {use_case} - {status}")


__all__ = [
    "get_optimal_data_source",
    "get_source_display_name",
    "validate_api_source_available",
    "get_fallback_source_chain",
    "log_api_source_selection",
    "format_provider_usage",
    "calculate_provider_costs",
    "get_provider_warning_level",
    "format_provider_status",
    "get_provider_icon",
    "validate_provider_selection",
    "get_provider_recommendation",
    "format_cost_summary",
    "log_provider_usage_event",
]
