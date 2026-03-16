"""Enum-oriented domain ports."""

from __future__ import annotations

from typing import List, Protocol

from src.domain.value_objects.enums import AnalyticsMetric, DataSource, RegionScope
from src.domain.value_objects.enums import QuestionType as DomainQuestionType


class AnalyticsMetricPort(Protocol):
    """Port for analytics metric operations."""

    @staticmethod
    def get_metric_enum(value: str) -> AnalyticsMetric: ...

    @staticmethod
    def get_metric_display_name(metric: AnalyticsMetric) -> str: ...

    @staticmethod
    def get_metric_unit(metric: AnalyticsMetric) -> str: ...

    @staticmethod
    def validate_metric(metric: AnalyticsMetric) -> bool: ...


class QuestionTypePort(Protocol):
    """Port for question type operations."""

    @staticmethod
    def get_question_type_enum(value: str) -> DomainQuestionType: ...

    @staticmethod
    def get_question_type_display_name(question_type: DomainQuestionType) -> str: ...

    @staticmethod
    def get_available_metrics_for_question_type(
        question_type: DomainQuestionType,
    ) -> List[AnalyticsMetric]: ...


class DataSourcePort(Protocol):
    """Port for data source operations."""

    @staticmethod
    def get_data_source_enum(value: str) -> DataSource: ...

    @staticmethod
    def get_data_source_display_name(source: DataSource) -> str: ...


class RegionScopePort(Protocol):
    """Port for region scope operations."""

    @staticmethod
    def get_region_scope_enum(value: str) -> RegionScope: ...

    @staticmethod
    def get_region_scope_display_name(scope: RegionScope) -> str: ...

    @staticmethod
    def validate_region_scope(scope: RegionScope) -> bool: ...
