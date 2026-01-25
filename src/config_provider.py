#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Global Weather Analyzer - Provider Configuration
Provider selector and user preferences for API selection
"""

from typing import Any, Dict


class ProviderConfig:
    """Provider Selector configuration and user preferences"""

    # Supported providers
    PROVIDERS = {
        "auto": {
            "name": "Automatikus (Smart Routing)",
            "description": "Use-case alapú automatikus provider választás",
            "icon": "🤖",
            "cost": "Optimalizált",
            "routing_logic": {
                "single_city": "open-meteo",
                "multi_city": "meteostat",
                "historical_deep": "meteostat",
                "real_time": "open-meteo"
            }
        },
        "open-meteo": {
            "name": "Open-Meteo (Ingyenes)",
            "description": "Ingyenes globális időjárási API minden funkcióhoz",
            "icon": "🌍",
            "cost": "Ingyenes",
            "limitations": ["Limitált multi-city support", "Alapszintű történeti adatok"]
        },
        "meteostat": {
            "name": "Meteostat (Prémium)",
            "description": "Prémium API gazdag történeti adatokkal és station-based accuracy",
            "icon": "💎",
            "cost": "$10 USD/hónap",
            "features": ["10k request/hónap", "Gazdag történeti adatok", "Station-based accuracy"]
        }
    }

    # Default provider preference
    DEFAULT_PROVIDER = "auto"

    # Usage tracking settings
    USAGE_RESET_DAY = 1  # Monthly usage reset on 1st day
    WARNING_THRESHOLD = 0.8  # Warn at 80% usage
    CRITICAL_THRESHOLD = 0.95  # Critical warning at 95% usage

    # Cost calculation
    METEOSTAT_COST_PER_REQUEST = 0.001  # $0.001 per request (rough estimate)
    MONTHLY_BUDGET_USD = 10.0  # $10 monthly budget


__all__ = ['ProviderConfig']
