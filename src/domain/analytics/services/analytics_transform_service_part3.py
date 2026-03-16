# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Mixin part 3 for AnalyticsTransformService."""

from __future__ import annotations

from .analytics_transform_service_support import *


class AnalyticsTransformServicePart3Mixin:
    def _require_query_config(self, query_type: str) -> Dict[str, Any]:
        config = self.query_types.get(query_type)
        if not config:
            raise ValueError(f"Ismeretlen query_type: {query_type}")
        return config
