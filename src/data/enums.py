#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global Weather Analyzer - Shared Enums
🎯 CLEAN ARCHITECTURE - Központi enum definíciók

REFAKTOR CÉL:
- city_analytics.py függőségek megszüntetése
- Tiszta enum separation
- Import chaos felszámolása
- SOLID principles alkalmazása

HASZNÁLAT:
```python
from src.data.enums import RegionScope, AnalyticsMetric, QuestionType, AnomalySeverity
```
"""

from enum import Enum
from typing import Dict, List


class RegionScope(Enum):
    """
    Régió hatókör enum.
    
    Analytics lekérdezések földrajzi hatókörének meghatározásához.
    """
    COUNTRY = "country"
    CONTINENT = "continent"
    GLOBAL = "global"
    REGION = "region"        # Pl. Balkán, Skandinávia
    CUSTOM = "custom"        # Felhasználó által definiált


class AnalyticsMetric(Enum):
    """
    Analytics metrika enum.
    
    Időjárási paraméterek standardizált megnevezései.
    """
    # Hőmérséklet metrikák
    TEMPERATURE_2M_MAX = "temperature_2m_max"
    TEMPERATURE_2M_MIN = "temperature_2m_min"
    TEMPERATURE_2M_MEAN = "temperature_2m_mean"
    APPARENT_TEMPERATURE_MAX = "apparent_temperature_max"
    APPARENT_TEMPERATURE_MIN = "apparent_temperature_min"
    
    # Csapadék metrikák
    PRECIPITATION_SUM = "precipitation_sum"
    PRECIPITATION_HOURS = "precipitation_hours"
    RAIN_SUM = "rain_sum"
    SNOWFALL_SUM = "snowfall_sum"
    SHOWERS_SUM = "showers_sum"
    
    # Szél metrikák
    WINDSPEED_10M_MAX = "windspeed_10m_max"
    WINDGUSTS_10M_MAX = "windgusts_10m_max"
    WINDDIRECTION_10M_DOMINANT = "winddirection_10m_dominant"
    
    # Légköri metrikák
    PRESSURE_MSL_MIN = "pressure_msl_min"
    PRESSURE_MSL_MAX = "pressure_msl_max"
    CLOUDCOVER_MEAN = "cloudcover_mean"
    HUMIDITY_2M_MEAN = "relative_humidity_2m"
    
    # UV és napfény
    UV_INDEX_MAX = "uv_index_max"
    SUNSHINE_DURATION = "sunshine_duration"
    
    # Derived metrikák
    TEMPERATURE_RANGE = "temperature_range"  # max - min
    WIND_CHILL = "wind_chill"
    HEAT_INDEX = "heat_index"


class QuestionType(Enum):
    """
    Analytics kérdés típus enum.
    
    Multi-city analytics kérdések kategorizálásához.
    """
    # Hőmérséklet kérdések
    TEMPERATURE_MAX = "temperature_max"
    TEMPERATURE_MIN = "temperature_min"
    TEMPERATURE_RANGE = "temperature_range"
    HEAT_WAVE = "heat_wave"
    COLD_SNAP = "cold_snap"
    
    # Csapadék kérdések  
    PRECIPITATION_MAX = "precipitation_max"
    PRECIPITATION_TOTAL = "precipitation_total"
    DROUGHT_ANALYSIS = "drought_analysis"
    FLOOD_RISK = "flood_risk"
    
    # Szél kérdések
    WIND_MAX = "wind_max"
    STORM_ANALYSIS = "storm_analysis"
    CALM_WEATHER = "calm_weather"
    
    # Kombinált kérdések
    EXTREME_WEATHER = "extreme_weather"
    WEATHER_COMPARISON = "weather_comparison"
    SEASONAL_ANALYSIS = "seasonal_analysis"
    CLIMATE_RANKING = "climate_ranking"
    
    # Speciális kérdések
    COMFORT_INDEX = "comfort_index"
    TOURISM_WEATHER = "tourism_weather"
    AGRICULTURE_ANALYSIS = "agriculture_analysis"


class AnomalySeverity(Enum):
    """
    Anomália súlyosság enum.
    
    Időjárási anomáliák besorolásához.
    """
    LOW = "low"              # Enyhe eltérés (1-2 sigma)
    MODERATE = "moderate"    # Közepes eltérés (2-2.5 sigma)
    HIGH = "high"           # Magas eltérés (2.5-3 sigma)
    EXTREME = "extreme"     # Extrém eltérés (3+ sigma)
    RECORD = "record"       # Rekordérték


class AnomalyType(Enum):
    """
    Anomália típus enum.
    
    Anomália irány meghatározásához.
    """
    HIGH = "high"           # Magas értékű anomália
    LOW = "low"             # Alacsony értékű anomália
    BOTH = "both"           # Mindkét irányú anomália


class DataSource(Enum):
    """
    Adatforrás enum.
    
    Weather API források megkülönböztetéshez.
    """
    OPEN_METEO = "open-meteo"
    METEOSTAT = "meteostat"
    ECMWF = "ecmwf"
    NOAA = "noaa"
    AUTO = "auto"           # Automatikus kiválasztás


class RegionType(Enum):
    """
    Régió típus enum.
    
    City Manager adatbázis lekérdezésekhez.
    """
    COUNTRY = "country"
    CONTINENT = "continent"
    ADMINISTRATIVE = "administrative"  # Állam/tartomány
    METROPOLITAN = "metropolitan"      # Nagyváros agglomeráció
    CUSTOM = "custom"


class AnalyticsMode(Enum):
    """
    Analytics mód enum.
    
    GUI analytics panel módok megkülönböztetéshez.
    """
    SINGLE_CITY = "single_city"
    MULTI_CITY = "multi_city"
    PARAMETER_BASED = "parameter_based"


# UTILITY FUNKCIÓK

def get_metric_display_name(metric: AnalyticsMetric) -> str:
    """
    Metrika display név lekérdezése.
    
    Args:
        metric: AnalyticsMetric enum érték
        
    Returns:
        Magyar display név
    """
    display_names = {
        AnalyticsMetric.TEMPERATURE_2M_MAX: "Maximum hőmérséklet",
        AnalyticsMetric.TEMPERATURE_2M_MIN: "Minimum hőmérséklet", 
        AnalyticsMetric.TEMPERATURE_2M_MEAN: "Átlagos hőmérséklet",
        AnalyticsMetric.PRECIPITATION_SUM: "Csapadékösszeg",
        AnalyticsMetric.WINDSPEED_10M_MAX: "Maximum szélsebesség",
        AnalyticsMetric.WINDGUSTS_10M_MAX: "Maximum széllökés",
        AnalyticsMetric.PRESSURE_MSL_MIN: "Minimum légnyomás",
        AnalyticsMetric.HUMIDITY_2M_MEAN: "Átlagos páratartalom",
        AnalyticsMetric.UV_INDEX_MAX: "Maximum UV index",
        AnalyticsMetric.SUNSHINE_DURATION: "Napsütés időtartama"
    }
    
    return display_names.get(metric, metric.value)


def get_metric_unit(metric: AnalyticsMetric) -> str:
    """
    Metrika mértékegység lekérdezése.
    
    Args:
        metric: AnalyticsMetric enum érték
        
    Returns:
        Mértékegység string
    """
    units = {
        AnalyticsMetric.TEMPERATURE_2M_MAX: "°C",
        AnalyticsMetric.TEMPERATURE_2M_MIN: "°C",
        AnalyticsMetric.TEMPERATURE_2M_MEAN: "°C",
        AnalyticsMetric.PRECIPITATION_SUM: "mm",
        AnalyticsMetric.WINDSPEED_10M_MAX: "km/h",
        AnalyticsMetric.WINDGUSTS_10M_MAX: "km/h",
        AnalyticsMetric.PRESSURE_MSL_MIN: "hPa",
        AnalyticsMetric.HUMIDITY_2M_MEAN: "%",
        AnalyticsMetric.UV_INDEX_MAX: "",
        AnalyticsMetric.SUNSHINE_DURATION: "h"
    }
    
    return units.get(metric, "")


def get_region_scope_display_name(scope: RegionScope) -> str:
    """
    RegionScope display név lekérdezése.
    
    Args:
        scope: RegionScope enum érték
        
    Returns:
        Magyar display név
    """
    display_names = {
        RegionScope.COUNTRY: "Ország",
        RegionScope.CONTINENT: "Kontinens", 
        RegionScope.GLOBAL: "Globális",
        RegionScope.REGION: "Régió",
        RegionScope.CUSTOM: "Egyedi"
    }
    
    return display_names.get(scope, scope.value)


def get_question_type_display_name(question_type: QuestionType) -> str:
    """
    QuestionType display név lekérdezése.
    
    Args:
        question_type: QuestionType enum érték
        
    Returns:
        Magyar display név
    """
    display_names = {
        QuestionType.TEMPERATURE_MAX: "Legmagasabb hőmérséklet",
        QuestionType.TEMPERATURE_MIN: "Legalacsonyabb hőmérséklet",
        QuestionType.PRECIPITATION_MAX: "Legtöbb csapadék",
        QuestionType.WIND_MAX: "Legerősebb szél",
        QuestionType.EXTREME_WEATHER: "Szélsőséges időjárás",
        QuestionType.WEATHER_COMPARISON: "Időjárás összehasonlítás"
    }
    
    return display_names.get(question_type, question_type.value)


def get_severity_color(severity: AnomalySeverity) -> str:
    """
    Anomália súlyosság színkód lekérdezése.
    
    Args:
        severity: AnomalySeverity enum érték
        
    Returns:
        CSS színkód
    """
    colors = {
        AnomalySeverity.LOW: "#fbbf24",      # Sárga
        AnomalySeverity.MODERATE: "#f97316", # Narancs
        AnomalySeverity.HIGH: "#ef4444",     # Piros
        AnomalySeverity.EXTREME: "#dc2626",  # Sötét piros
        AnomalySeverity.RECORD: "#7c2d12"    # Bordó
    }
    
    return colors.get(severity, "#6b7280")


# VALIDATION FUNKCIÓK

def validate_analytics_metric(metric_str: str) -> bool:
    """
    Analytics metrika validálása.
    
    Args:
        metric_str: Metrika string reprezentáció
        
    Returns:
        Érvényes metrika-e
    """
    return metric_str in [m.value for m in AnalyticsMetric]


def validate_region_scope(scope_str: str) -> bool:
    """
    RegionScope validálása.
    
    Args:
        scope_str: Scope string reprezentáció
        
    Returns:
        Érvényes scope-e
    """
    return scope_str in [s.value for s in RegionScope]


def get_available_metrics_for_question_type(question_type: QuestionType) -> List[AnalyticsMetric]:
    """
    Kérdéstípushoz elérhető metrikák lekérdezése.
    
    Args:
        question_type: QuestionType enum érték
        
    Returns:
        Releváns metrikák listája
    """
    metric_mapping = {
        QuestionType.TEMPERATURE_MAX: [
            AnalyticsMetric.TEMPERATURE_2M_MAX,
            AnalyticsMetric.APPARENT_TEMPERATURE_MAX
        ],
        QuestionType.TEMPERATURE_MIN: [
            AnalyticsMetric.TEMPERATURE_2M_MIN,
            AnalyticsMetric.APPARENT_TEMPERATURE_MIN
        ],
        QuestionType.PRECIPITATION_MAX: [
            AnalyticsMetric.PRECIPITATION_SUM,
            AnalyticsMetric.RAIN_SUM,
            AnalyticsMetric.SNOWFALL_SUM
        ],
        QuestionType.WIND_MAX: [
            AnalyticsMetric.WINDSPEED_10M_MAX,
            AnalyticsMetric.WINDGUSTS_10M_MAX
        ]
    }
    
    return metric_mapping.get(question_type, [])


# EXPORT API
__all__ = [
    'RegionScope',
    'AnalyticsMetric', 
    'QuestionType',
    'AnomalySeverity',
    'AnomalyType',
    'DataSource',
    'RegionType',
    'AnalyticsMode',
    'get_metric_display_name',
    'get_metric_unit',
    'get_region_scope_display_name',
    'get_question_type_display_name',
    'get_severity_color',
    'validate_analytics_metric',
    'validate_region_scope',
    'get_available_metrics_for_question_type'
]
