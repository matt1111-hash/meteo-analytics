"""Domain entities module."""

# Location types
from src.domain.entities.location_types import LocationType

# Location entities
from src.domain.entities.location import Location
from src.domain.entities.universal_location import UniversalLocation
from src.domain.entities.city_info import CityInfo

# Location factory functions
from src.domain.entities.location_factories import (
    create_universal_location,
    create_location,
    create_location_from_coordinates
)

# Time granularity
from src.domain.entities.time_granularity import TimeGranularity

# Analysis type
from src.domain.entities.analysis_type import AnalysisType

# Time range and query
from src.domain.entities.universal_time_range import UniversalTimeRange
from src.domain.entities.universal_query import UniversalQuery

# Analytics models
from src.domain.entities.analytics_models import (
    AnalyticsQuestion,
    AnalyticsResult,
    QueryResults
)

# Analysis factory functions
from src.domain.entities.analysis_factories import (
    create_universal_time_range,
    create_universal_query,
    create_analytics_question
)

# Other entities
from src.domain.entities.weather import CityWeatherResult, AnomalyResult, create_city_weather_result

__all__ = [
    # Location types
    'LocationType',

    # Location entities
    'Location',
    'UniversalLocation',
    'CityInfo',

    # Location factory functions
    'create_universal_location',
    'create_location',
    'create_location_from_coordinates',

    # Time granularity
    'TimeGranularity',

    # Analysis type
    'AnalysisType',

    # Time range and query
    'UniversalTimeRange',
    'UniversalQuery',

    # Analytics models
    'AnalyticsQuestion',
    'AnalyticsResult',
    'QueryResults',

    # Analysis factory functions
    'create_universal_time_range',
    'create_universal_query',
    'create_analytics_question',

    # Weather entities
    'CityWeatherResult',
    'AnomalyResult',
    'create_city_weather_result'
]
