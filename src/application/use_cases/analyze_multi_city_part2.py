# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Mixin part 2 for AnalyzeMultiCityUseCase."""

from __future__ import annotations

from .analyze_multi_city_support import *


class AnalyzeMultiCityUseCasePart2Mixin:
    def _resolve_city_limit(
        self, query: MultiCityQuery, region_config: Dict[str, Any]
    ) -> int:
        candidate = query.max_cities
        try:
            if candidate is None or int(candidate) <= 0:
                return int(region_config["max_cities"])
            return int(candidate)
        except (TypeError, ValueError):
            return int(region_config["max_cities"])

    def _build_question(
        self,
        query_config: Dict[str, Any],
        mapped_region: str,
    ) -> AnalyticsQuestion:
        region_display_name = self.regions.get(mapped_region, {}).get(
            "name",
            mapped_region,
        )
        region_scope = self._resolve_region_scope(mapped_region)
        metric_enum = query_config.get(
            "metric_enum", AnalyticsMetric.TEMPERATURE_2M_MAX
        )
        question_text = query_config["question_template"].format(
            region=region_display_name
        )

        return AnalyticsQuestion(
            question_text=question_text,
            question_type=QuestionType.WEATHER_COMPARISON,
            region_scope=region_scope,
            metric=metric_enum,
        )

    def _resolve_region_scope(self, mapped_region: str) -> RegionScope:
        if mapped_region == "Global":
            return RegionScope.GLOBAL
        if mapped_region == "Hungary":
            return RegionScope.COUNTRY
        return RegionScope.CONTINENT

    def _validate_query(self, query: MultiCityQuery) -> None:
        if not query.query_type:
            raise ValueError("query_type hiányzik")
        if not query.region:
            raise ValueError("region hiányzik")
        if not query.date:
            raise ValueError("date hiányzik")

    def _require_query_config(self, query_type: str) -> Dict[str, Any]:
        config = self.query_types.get(query_type)
        if not config:
            raise ValueError(f"Ismeretlen lekérdezés típus: {query_type}")
        return config

    def _require_region_config(self, mapped_region: str) -> Dict[str, Any]:
        config = self.regions.get(mapped_region)
        if not config:
            raise ValueError(f"Ismeretlen régió: {mapped_region}")
        return config
