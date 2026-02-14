#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Constants - Anomaly detection thresholds - Wind gusts optimized.
"""


class AnomalyConstants:
    """
    Anomaly detection constants - WIND GUSTS OPTIMIZED.

    Küszöbértékek és kategóriák élethű széllökés értékekhez.
    Balatonfüredi 130+ km/h széllökések alapján kalibrálva.
    """

    # Temperature anomalies (Celsius)
    TEMP_HOT_THRESHOLD = 35.0
    TEMP_COLD_THRESHOLD = -10.0
    TEMP_EXTREME_HOT = 40.0
    TEMP_EXTREME_COLD = -20.0

    # Precipitation anomalies (mm)
    PRECIP_HIGH_THRESHOLD = 100.0
    PRECIP_LOW_THRESHOLD = 10.0
    PRECIP_EXTREME_HIGH = 200.0
    PRECIP_DAILY_EXTREME = 50.0

    # Wind anomalies (km/h) - WIND GUSTS OPTIMIZED
    WIND_HIGH_THRESHOLD = 70.0
    WIND_EXTREME_THRESHOLD = 100.0
    WIND_HURRICANE_THRESHOLD = 120.0

    # Wind gusts specific thresholds
    WIND_GUSTS_CALM = 0.0
    WIND_GUSTS_LIGHT = 10.0
    WIND_GUSTS_MODERATE = 30.0
    WIND_GUSTS_STRONG = 50.0
    WIND_GUSTS_STORMY = 70.0
    WIND_GUSTS_EXTREME = 100.0
    WIND_GUSTS_HURRICANE = 120.0
    WIND_GUSTS_CATASTROPHIC = 150.0

    # Windspeed thresholds (backward compatibility)
    WINDSPEED_HIGH_THRESHOLD = 50.0
    WINDSPEED_EXTREME_THRESHOLD = 80.0

    # Wind gusts specific thresholds (exported for backward compatibility)
    WIND_GUSTS_EXTREME = WIND_GUSTS_EXTREME
    WIND_GUSTS_HURRICANE = WIND_GUSTS_HURRICANE

    # Statistics constants
    STANDARD_DEVIATION_MULTIPLIER = 2.0
    MIN_DATA_POINTS = 30

    # Anomaly categories
    ANOMALY_CATEGORIES = {
        "NORMAL": {"threshold": 1.0, "color": "#10b981", "label": "Normális"},
        "MILD": {"threshold": 1.5, "color": "#f59e0b", "label": "Enyhe anomália"},
        "MODERATE": {"threshold": 2.0, "color": "#ef4444", "label": "Közepes anomália"},
        "SEVERE": {"threshold": 3.0, "color": "#dc2626", "label": "Súlyos anomália"},
        "EXTREME": {"threshold": 4.0, "color": "#7c2d12", "label": "Extrém anomália"},
    }

    # Wind gusts categories - METEOROLOGICAL STANDARDS
    WIND_GUSTS_CATEGORIES = {
        "CALM": {
            "threshold": 0.0,
            "max": 10.0,
            "color": "#a3a3a3",
            "label": "Szélcsend",
            "emoji": "🌤️",
        },
        "LIGHT": {
            "threshold": 10.0,
            "max": 30.0,
            "color": "#86efac",
            "label": "Enyhe szél",
            "emoji": "🍃",
        },
        "MODERATE": {
            "threshold": 30.0,
            "max": 50.0,
            "color": "#f59e0b",
            "label": "Mérsékelt szél",
            "emoji": "💨",
        },
        "STRONG": {
            "threshold": 50.0,
            "max": 70.0,
            "color": "#f87171",
            "label": "Erős szél",
            "emoji": "🌪️",
        },
        "STORMY": {
            "threshold": 70.0,
            "max": 100.0,
            "color": "#dc2626",
            "label": "Viharos szél",
            "emoji": "⚠️",
        },
        "EXTREME": {
            "threshold": 100.0,
            "max": 120.0,
            "color": "#991b1b",
            "label": "Extrém széllökés",
            "emoji": "🚨",
        },
        "HURRICANE": {
            "threshold": 120.0,
            "max": 150.0,
            "color": "#7c2d12",
            "label": "Hurrikán erősségű",
            "emoji": "☢️",
        },
        "CATASTROPHIC": {
            "threshold": 150.0,
            "max": 999.0,
            "color": "#450a0a",
            "label": "Katasztrofális",
            "emoji": "💀",
        },
    }

    # Color codes
    NORMAL_COLOR = "#10b981"
    WARNING_COLOR = "#f59e0b"
    DANGER_COLOR = "#dc2626"
    EXTREME_COLOR = "#7c2d12"

    # Wind gusts specific colors
    WIND_GUSTS_COLORS = {
        "normal": "#10b981",
        "moderate": "#f59e0b",
        "strong": "#f87171",
        "stormy": "#dc2626",
        "extreme": "#991b1b",
        "hurricane": "#7c2d12",
        "catastrophic": "#450a0a",
    }
