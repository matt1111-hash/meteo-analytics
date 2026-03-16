# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Split definitions from analytics_models.py."""

from __future__ import annotations

from .analytics_models_support import *


@dataclass
class AnalyticsQuestion:
    """
    Analytics question definition.

    Multi-city analytics question specification.
    """

    question_text: str
    question_type: QuestionType
    region_scope: RegionScope
    metric: AnalyticsMetric

    # Query parameters
    region_value: Optional[str] = None
    date_filter: Optional[str] = None
    ascending_order: bool = False
    max_cities: int = 50

    # Additional filters
    min_population: Optional[int] = None
    include_capitals_only: bool = False
    exclude_islands: bool = False
    climate_zones: Optional[List[str]] = None

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    created_by: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        """String representation."""
        return self.question_text

    def get_region_display(self) -> str:
        """Get region display name."""
        if self.region_value:
            return f"{self.region_scope.value}: {self.region_value}"
        return self.region_scope.value

    def validate(self) -> Tuple[bool, List[str]]:
        """
        Validate question.

        Returns:
            (valid, error_messages)
        """
        errors = []

        if not self.question_text.strip():
            errors.append("Kérdés szövege nem lehet üres")

        if self.max_cities <= 0:
            errors.append("Maximum városok száma pozitív kell legyen")

        if self.max_cities > 1000:
            errors.append("Maximum városok száma nem lehet 1000-nél több")

        if (
            self.region_scope in [RegionScope.COUNTRY, RegionScope.REGION]
            and not self.region_value
        ):
            errors.append(
                f"{self.region_scope.value} scope esetén region_value kötelező"
            )

        return len(errors) == 0, errors

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "question_text": self.question_text,
            "question_type": self.question_type.value,
            "region_scope": self.region_scope.value,
            "metric": self.metric.value,
            "region_value": self.region_value,
            "date_filter": self.date_filter,
            "ascending_order": self.ascending_order,
            "max_cities": self.max_cities,
            "min_population": self.min_population,
            "include_capitals_only": self.include_capitals_only,
            "exclude_islands": self.exclude_islands,
            "climate_zones": self.climate_zones,
            "created_at": self.created_at.isoformat(),
            "created_by": self.created_by,
            "tags": self.tags,
        }
