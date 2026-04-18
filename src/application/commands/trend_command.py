#!/usr/bin/env python3

"""Application command for trend analysis — framework-agnostic."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TrendAnalysisCommand:
    """Pure application-layer request for trend analysis."""

    location: str
    metric: str
    time_periods: list[int]
    start_date: str | None = None
    end_date: str | None = None


__all__ = ["TrendAnalysisCommand"]
