"""Factory functions for analysis entities."""

from datetime import date, datetime
from typing import TYPE_CHECKING, List, Union

if TYPE_CHECKING:
    from src.domain.entities.universal_query import UniversalQuery

from src.domain.entities.analysis_type import AnalysisType
from src.domain.entities.analytics_models import AnalyticsQuestion
from src.domain.entities.time_granularity import TimeGranularity
from src.domain.entities.universal_location import UniversalLocation
from src.domain.entities.universal_time_range import UniversalTimeRange
from src.domain.value_objects.enums import AnalyticsMetric, QuestionType, RegionScope


def create_universal_time_range(
    start_date: Union[str, date],
    end_date: Union[str, date],
    granularity: Union[TimeGranularity, str] = TimeGranularity.DAILY,
    **kwargs,
) -> UniversalTimeRange:
    """
    UniversalTimeRange factory - user-friendly.
    """
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

    if isinstance(granularity, str):
        granularity = TimeGranularity(granularity.lower())

    return UniversalTimeRange(
        start_date=start_date, end_date=end_date, granularity=granularity, **kwargs
    )


def create_universal_query(
    locations: List[UniversalLocation],
    time_range: UniversalTimeRange,
    parameters: List[str],
    analysis_type: Union[AnalysisType, str] = AnalysisType.CURRENT_CONDITIONS,
    **kwargs,
) -> "UniversalQuery":
    """
    UniversalQuery factory - user-friendly.
    """
    from src.domain.entities.universal_query import UniversalQuery

    if isinstance(analysis_type, str):
        analysis_type = AnalysisType(analysis_type.lower())

    return UniversalQuery(
        locations=locations,
        time_range=time_range,
        parameters=parameters,
        analysis_type=analysis_type,
        **kwargs,
    )


def create_analytics_question(
    question_text: str,
    question_type: QuestionType,
    region_scope: RegionScope,
    metric: AnalyticsMetric,
    **kwargs,
) -> AnalyticsQuestion:
    """
    AnalyticsQuestion factory function.
    """
    return AnalyticsQuestion(
        question_text=question_text,
        question_type=question_type,
        region_scope=region_scope,
        metric=metric,
        **kwargs,
    )


__all__ = [
    "create_universal_time_range",
    "create_universal_query",
    "create_analytics_question",
]
