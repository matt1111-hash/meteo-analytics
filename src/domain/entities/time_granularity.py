"""Time granularity enum for analysis entities."""

from enum import Enum


class TimeGranularity(Enum):
    """Time granularity for temporal analysis."""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    SEASONAL = "seasonal"
    CUSTOM_INTERVAL = "custom_interval"
    MULTI_YEAR = "multi_year"


__all__ = ["TimeGranularity"]
