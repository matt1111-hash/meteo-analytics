"""
Global Weather Analyzer - Data Models (Legacy Export Module)
🎯 CLEAN ARCHITECTURE MIGRATION - Ez a fájl már csak re-exportálja a Domain entitásokat.

Használat (Legacy):
from src.data.models import AnalyticsResult  # Működik tovább

Javasolt új használat:
from src.domain.entities.analysis import AnalyticsResult
"""

# Re-export from Domain Layer
from src.domain.entities.location import (
    LocationType,
    Location,
    UniversalLocation,
    CityInfo,
    create_location,
    create_location_from_coordinates,
    create_universal_location
)

from src.domain.entities.weather import (
    CityWeatherResult,
    AnomalyResult,
    create_city_weather_result
)

from src.domain.entities.analysis import (
    TimeGranularity,
    AnalysisType,
    UniversalTimeRange,
    UniversalQuery,
    AnalyticsQuestion,
    AnalyticsResult,
    QueryResults,
    create_universal_time_range,
    create_universal_query,
    create_analytics_question
)

# Export all symbols
__all__ = [
    'LocationType',
    'Location',
    'UniversalLocation',
    'CityInfo',
    'create_location',
    'create_location_from_coordinates',
    'create_universal_location',
    'CityWeatherResult',
    'AnomalyResult',
    'create_city_weather_result',
    'TimeGranularity',
    'AnalysisType',
    'UniversalTimeRange',
    'UniversalQuery',
    'AnalyticsQuestion',
    'AnalyticsResult',
    'QueryResults',
    'create_universal_time_range',
    'create_universal_query',
    'create_analytics_question'
]
