"""
Global Weather Analyzer - Data Models (Legacy Export Module)
🎯 CLEAN ARCHITECTURE MIGRATION - Ez a fájl már csak re-exportálja a Domain entitásokat.

Használat (Legacy):
from src.data.models import AnalyticsResult  # Működik tovább

Javasolt új használat:
from src.domain.entities.analysis import AnalyticsResult
"""

# Re-export from Data Layer (City - data layer entity)
from src.data.city_types import City, CityDatabaseError, CityQuery
from src.domain.entities.analysis_factories import (
    create_analytics_question,
    create_universal_query,
    create_universal_time_range,
)
from src.domain.entities.analysis_type import AnalysisType
from src.domain.entities.analytics_models import (
    AnalyticsQuestion,
    AnalyticsResult,
    QueryResults,
)
from src.domain.entities.city_info import CityInfo
from src.domain.entities.location import Location
from src.domain.entities.location_factories import (
    create_location,
    create_location_from_coordinates,
    create_universal_location,
)

# Re-export from Domain Layer
from src.domain.entities.location_types import LocationType
from src.domain.entities.time_granularity import TimeGranularity
from src.domain.entities.universal_location import UniversalLocation
from src.domain.entities.universal_query import UniversalQuery
from src.domain.entities.universal_time_range import UniversalTimeRange
from src.domain.entities.weather import (
    AnomalyResult,
    CityWeatherResult,
    create_city_weather_result,
)

# Export all symbols
__all__ = [
    "AnalysisType",
    "AnalyticsQuestion",
    "AnalyticsResult",
    "AnomalyResult",
    # Data layer types
    "City",
    "CityDatabaseError",
    "CityInfo",
    "CityQuery",
    "CityWeatherResult",
    "Location",
    # Location types
    "LocationType",
    "QueryResults",
    "TimeGranularity",
    "UniversalLocation",
    "UniversalQuery",
    "UniversalTimeRange",
    "create_analytics_question",
    "create_city_weather_result",
    "create_location",
    "create_location_from_coordinates",
    "create_universal_location",
    "create_universal_query",
    "create_universal_time_range",
]
