"""Multi-City Analytics Engine - Types and re-exports from domain."""

from src.domain.constants.regions import (
    HUNGARIAN_REGIONAL_MAPPING,
    REGIONS,
)

Number = float | int
NumberOrNone = Number | None

__all__ = ["HUNGARIAN_REGIONAL_MAPPING", "REGIONS", "Number", "NumberOrNone"]
