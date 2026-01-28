"""Domain entities module."""

# Location types
# Analysis factory functions
from src.domain.entities.analysis_factories import (
    create_analytics_question,
    create_universal_query,
    create_universal_time_range,
)

# Analysis type
from src.domain.entities.analysis_type import AnalysisType

# Analytics models
from src.domain.entities.analytics_models import (
    AnalyticsQuestion,
    AnalyticsResult,
    QueryResults,
)
from src.domain.entities.city_info import CityInfo

# Location entities
from src.domain.entities.location import Location

# Location factory functions
from src.domain.entities.location_factories import (
    create_location,
    create_location_from_coordinates,
    create_universal_location,
)
from src.domain.entities.location_types import LocationType

# Time granularity
from src.domain.entities.time_granularity import TimeGranularity
from src.domain.entities.universal_location import UniversalLocation
from src.domain.entities.universal_query import UniversalQuery

# Time range and query
from src.domain.entities.universal_time_range import UniversalTimeRange

# Other entities
from src.domain.entities.weather import (
    AnomalyResult,
    CityWeatherResult,
    create_city_weather_result,
)

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
