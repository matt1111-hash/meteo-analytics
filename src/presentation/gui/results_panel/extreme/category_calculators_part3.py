# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Mixin part 3 for CategoryCalculators."""

from __future__ import annotations

from .category_calculators_support import *


def _get_uv_category(uv_value: float) -> str:
    """Return the UV category label for a value."""
    if uv_value >= 11:
        return "Extrém"
    if uv_value >= 8:
        return "Nagyon erős"
    if uv_value >= 6:
        return "Erős"
    if uv_value >= 3:
        return "Mérsékelt"
    return "Gyenge"


class CategoryCalculatorsPart3Mixin:
    def calculate_uv_records(
        self, daily_data: Dict[str, List], dates: List[str]
    ) -> List[ExtremeRecord]:
        """UV index rekordok."""
        records = []

        try:
            uv_max = daily_data.get("uv_index_max", [])
            clean_uv = self._get_clean_uv_values(uv_max, dates)
            if clean_uv:
                max_idx, max_uv = max(clean_uv, key=lambda x: x[1])
                uv_cat = _get_uv_category(max_uv)
                records.append(
                    ExtremeRecord(
                        category="🟡 UV Index",
                        record_type=f"☀️ Legmagasabb UV ({uv_cat})",
                        value=f"{max_uv:.1f}",
                        date=dates[max_idx],
                        raw_value=float(max_uv),
                    )
                )
        except Exception as e:
            logger.error(f"UV index rekordok hiba: {e}")

        return records

    @staticmethod
    def _get_clean_uv_values(uv_max: List, dates: List[str]) -> list[tuple[int, Any]]:
        """Return cleaned UV values when lengths are compatible."""
        if not uv_max or len(uv_max) != len(dates):
            return []
        return [
            (index, value) for index, value in enumerate(uv_max) if value is not None
        ]
