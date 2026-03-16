"""Analytics result helpers for the multi-city engine."""

from __future__ import annotations

import logging
from typing import Any

from src.domain.entities.analytics_models import AnalyticsQuestion, AnalyticsResult
from src.domain.value_objects.enums import AnalyticsMetric, QuestionType, RegionScope

logger = logging.getLogger(__name__)


def create_empty_analytics_result(
    question: AnalyticsQuestion | None,
    error_msg: str = "Ismeretlen hiba",
) -> AnalyticsResult:
    """Create a safe fallback analytics result."""
    return create_empty_analytics_result_with_types(
        question=question,
        error_msg=error_msg,
        analytics_question_cls=AnalyticsQuestion,
        analytics_result_cls=AnalyticsResult,
        question_type_weather_comparison=QuestionType.WEATHER_COMPARISON,
        question_type_temperature_max=QuestionType.TEMPERATURE_MAX,
        region_scope_global=RegionScope.GLOBAL,
        temperature_metric=AnalyticsMetric.TEMPERATURE_2M_MAX,
    )


def create_empty_analytics_result_with_types(
    question: AnalyticsQuestion | None,
    error_msg: str,
    analytics_question_cls: type[Any],
    analytics_result_cls: type[Any],
    question_type_weather_comparison: QuestionType,
    question_type_temperature_max: QuestionType,
    region_scope_global: RegionScope,
    temperature_metric: AnalyticsMetric,
) -> AnalyticsResult:
    """Create an empty result using injected model types for test compatibility."""
    try:
        fallback_question = question
        if not fallback_question:
            fallback_question = analytics_question_cls(
                question_text=f"Multi-city elemzés hiba: {error_msg}",
                question_type=question_type_weather_comparison,
                region_scope=region_scope_global,
                metric=temperature_metric,
            )

        empty_result = analytics_result_cls(
            question=fallback_question,
            city_results=[],
            execution_time=0.0,
            total_cities_found=0,
            data_sources_used=[],
            statistics={},
            provider_statistics={},
        )
        logger.info("✅ Empty AnalyticsResult created for error: %s", error_msg)
        return empty_result
    except Exception as exc:
        logger.error("⚠ Critical error creating empty AnalyticsResult: %s", exc)

    try:
        ultra_fallback_question = analytics_question_cls(
            question_text="Critical error",
            question_type=question_type_temperature_max,
            region_scope=region_scope_global,
            metric=temperature_metric,
        )
        return analytics_result_cls(
            question=ultra_fallback_question,
            city_results=[],
            execution_time=0.0,
            total_cities_found=0,
            data_sources_used=[],
            statistics={},
            provider_statistics={},
        )
    except Exception as exc:
        logger.error("⚠ ULTRA CRITICAL: Cannot create AnalyticsResult at all: %s", exc)
        raise RuntimeError(f"Cannot create AnalyticsResult: {exc}") from exc
