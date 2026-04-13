"""Universal query domain entity."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from src.domain.entities.analysis_type import AnalysisType
from src.domain.entities.location_types import LocationType
from src.domain.entities.universal_location import UniversalLocation
from src.domain.entities.universal_time_range import UniversalTimeRange
from src.domain.value_objects.enums import AnomalySeverity, DataSource


@dataclass
class UniversalQuery:
    """
    Universal query model - user-centric paradigm.
    """

    # Basic query components
    locations: list[UniversalLocation]
    time_range: UniversalTimeRange
    parameters: list[str]
    analysis_type: AnalysisType

    # Query metadata
    query_id: str = field(
        default_factory=lambda: f"universal_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    user_description: str = ""

    # Execution settings
    data_sources: list[DataSource] = field(default_factory=list)
    quality_threshold: float = 0.8
    max_results_per_location: int = 1000

    # Filter options
    anomaly_detection: bool = False
    statistical_analysis: bool = True
    trend_analysis: bool = False
    comparative_mode: bool = False

    # Anomaly specific settings
    anomaly_severity_filter: list[AnomalySeverity] = field(default_factory=list)
    anomaly_threshold_override: float | None = None

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str | None = None
    tags: list[str] = field(default_factory=list)

    # Execution status
    is_executed: bool = False
    execution_time: float | None = None
    total_data_points: int = 0

    def __post_init__(self):
        """Post-init validation and automatic settings."""
        if not self.user_description:
            self.user_description = self._generate_description()

        if len(self.locations) > 1:
            self.comparative_mode = True

        if not self.data_sources:
            self.data_sources = [DataSource.AUTO]

    def _generate_description(self) -> str:
        """Generate automatic user-friendly description."""
        if len(self.locations) == 1:
            location_desc = self.locations[0].display_name
        elif len(self.locations) <= 3:  # noqa: PLR2004
            location_desc = " vs ".join([loc.display_name for loc in self.locations])
        else:
            location_desc = f"{len(self.locations)} lokáció"

        if len(self.parameters) == 1:
            param_desc = self.parameters[0].replace("_", " ")
        elif len(self.parameters) <= 3:  # noqa: PLR2004
            param_desc = ", ".join([p.replace("_", " ") for p in self.parameters])
        else:
            param_desc = f"{len(self.parameters)} paraméter"

        time_desc = self.time_range.description
        analysis_desc = self.analysis_type.value.replace("_", " ")

        return f"{location_desc}: {param_desc} {analysis_desc} ({time_desc})"

    def __str__(self) -> str:
        """String representation."""
        return f"UniversalQuery[{self.query_id}]: {self.user_description}"

    def get_total_locations(self) -> int:
        """Get total locations count (with hierarchical breakdown)."""
        total = 0
        for location in self.locations:
            if location.type == LocationType.MULTIPLE:
                total += len(location.child_locations)
            else:
                total += 1
        return total

    def get_all_coordinates(self) -> list[tuple[float, float]]:
        """Get all coordinates from query."""
        all_coords = []
        for location in self.locations:
            all_coords.extend(location.get_coordinates_list())
        return all_coords

    def is_multi_location_query(self) -> bool:
        """Check if multi-location query."""
        return len(self.locations) > 1 or any(
            loc.type == LocationType.MULTIPLE for loc in self.locations
        )

    def is_long_term_analysis(self) -> bool:
        """Check if long-term analysis (>1 year)."""
        return self.time_range.total_days > 365  # noqa: PLR2004

    def is_historical_query(self) -> bool:
        """Check if historical query."""
        return self.time_range.is_historical

    def get_estimated_complexity(self) -> str:
        """Get estimated query complexity."""
        score = 0
        score += self.get_total_locations() * 2
        score += len(self.parameters) * 3
        score += min(self.time_range.total_days // 30, 50)

        if self.analysis_type in [
            AnalysisType.TREND_ANALYSIS,
            AnalysisType.ANOMALY_DETECTION,
        ]:
            score += 20
        elif self.analysis_type in [
            AnalysisType.PATTERN_RECOGNITION,
            AnalysisType.FORECAST,
        ]:
            score += 30

        if self.comparative_mode:
            score += 15

        if score < 20:  # noqa: PLR2004
            return "simple"
        elif score < 50:  # noqa: PLR2004
            return "medium"
        elif score < 100:  # noqa: PLR2004
            return "complex"
        else:
            return "very_complex"

    def validate(self) -> tuple[bool, list[str]]:
        """
        Validate query.

        Returns:
            (valid: bool, error_messages: List[str])
        """
        errors = []

        if not self.locations:
            errors.append("Legalább egy lokáció megadása kötelező!")

        if not self.parameters:
            errors.append("Legalább egy paraméter megadása kötelező!")

        if self.time_range.start_date > self.time_range.end_date:
            errors.append("A kezdő dátum nem lehet későbbi a záró dátumnál!")

        estimated_complexity = self.get_estimated_complexity()
        if (
            estimated_complexity == "very_complex" and self.max_results_per_location < 100  # noqa: PLR2004
        ):
            errors.append("Nagyon komplex query esetén növelje a max_results_per_location értékét!")

        if self.anomaly_detection:  # noqa: SIM102
            if self.anomaly_threshold_override and self.anomaly_threshold_override <= 0:
                errors.append("Anomália küszöb pozitív szám kell legyen!")

        return len(errors) == 0, errors

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "query_id": self.query_id,
            "user_description": self.user_description,
            "locations": [loc.to_dict() for loc in self.locations],
            "time_range": self.time_range.to_dict(),
            "parameters": self.parameters,
            "analysis_type": self.analysis_type.value,
            "data_sources": [ds.value for ds in self.data_sources],
            "quality_threshold": self.quality_threshold,
            "max_results_per_location": self.max_results_per_location,
            "anomaly_detection": self.anomaly_detection,
            "statistical_analysis": self.statistical_analysis,
            "trend_analysis": self.trend_analysis,
            "comparative_mode": self.comparative_mode,
            "estimated_complexity": self.get_estimated_complexity(),
            "total_locations": self.get_total_locations(),
            "is_multi_location": self.is_multi_location_query(),
            "is_long_term": self.is_long_term_analysis(),
            "is_historical": self.is_historical_query(),
            "created_at": self.created_at.isoformat(),
            "created_by": self.created_by,
            "tags": self.tags,
        }


__all__ = ["UniversalQuery"]
