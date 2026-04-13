"""Enum-oriented domain ports."""

from __future__ import annotations

from typing import Protocol

from src.domain.value_objects.enums import AnalyticsMetric, DataSource, RegionScope
from src.domain.value_objects.enums import QuestionType as DomainQuestionType


class AnalyticsMetricPort(Protocol):
    """Port for analytics metric operations."""

    @staticmethod
    def get_metric_enum(value: str) -> AnalyticsMetric: ...  # noqa: D102

    @staticmethod
    def get_metric_display_name(metric: AnalyticsMetric) -> str: ...  # noqa: D102

    @staticmethod
    def get_metric_unit(metric: AnalyticsMetric) -> str: ...  # noqa: D102

    @staticmethod
    def validate_metric(metric: AnalyticsMetric) -> bool: ...  # noqa: D102


class QuestionTypePort(Protocol):
    """Port for question type operations."""

    @staticmethod
    def get_question_type_enum(value: str) -> DomainQuestionType: ...  # noqa: D102

    @staticmethod
    def get_question_type_display_name(question_type: DomainQuestionType) -> str: ...  # noqa: D102

    @staticmethod
    def get_available_metrics_for_question_type(  # noqa: D102
        question_type: DomainQuestionType,
    ) -> list[AnalyticsMetric]: ...


class DataSourcePort(Protocol):
    """Port for data source operations."""

    @staticmethod
    def get_data_source_enum(value: str) -> DataSource: ...  # noqa: D102

    @staticmethod
    def get_data_source_display_name(source: DataSource) -> str: ...  # noqa: D102


class RegionScopePort(Protocol):
    """Port for region scope operations."""

    @staticmethod
    def get_region_scope_enum(value: str) -> RegionScope: ...  # noqa: D102

    @staticmethod
    def get_region_scope_display_name(scope: RegionScope) -> str: ...  # noqa: D102

    @staticmethod
    def validate_region_scope(scope: RegionScope) -> bool: ...  # noqa: D102
