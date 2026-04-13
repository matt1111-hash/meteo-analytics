"""Universal time range domain entity."""

from dataclasses import dataclass, field
from datetime import date
from typing import Any

from src.domain.entities.time_granularity import TimeGranularity


@dataclass
class UniversalTimeRange:
    """
    Universal time range model - complete time freedom.
    """

    start_date: date
    end_date: date
    granularity: TimeGranularity

    # Descriptive info
    description: str = ""

    # Special settings
    include_partial_periods: bool = True
    exclude_weekends: bool = False
    seasonal_filter: list[str] | None = None

    # Metadata
    total_days: int = field(init=False)
    is_historical: bool = field(init=False)
    is_future: bool = field(init=False)

    def __post_init__(self):
        """Post-init calculations."""
        self.total_days = (self.end_date - self.start_date).days + 1
        today = date.today()
        self.is_historical = self.end_date < today
        self.is_future = self.start_date > today

        if not self.description:
            self.description = self._generate_description()

    def _generate_description(self) -> str:
        """Generate automatic description."""
        if self.total_days == 1:
            return f"Egy nap ({self.start_date})"
        elif self.total_days <= 7:  # noqa: PLR2004
            return f"{self.total_days} nap ({self.start_date} - {self.end_date})"
        elif self.total_days <= 31:  # noqa: PLR2004
            return f"~{self.total_days // 7} hét ({self.start_date} - {self.end_date})"
        elif self.total_days <= 365:  # noqa: PLR2004
            return f"~{self.total_days // 30} hónap ({self.start_date} - {self.end_date})"
        else:
            years = self.total_days // 365
            return f"~{years} év ({self.start_date} - {self.end_date})"

    def __str__(self) -> str:
        """String representation."""
        return f"{self.description} [{self.granularity.value}]"

    def overlaps_with(self, other: "UniversalTimeRange") -> bool:
        """Check if overlaps with another time range."""
        return not (self.end_date < other.start_date or self.start_date > other.end_date)

    def contains_date(self, check_date: date) -> bool:
        """Check if contains the given date."""
        return self.start_date <= check_date <= self.end_date

    def get_months_list(self) -> list[str]:
        """Get affected months list (YYYY-MM format)."""
        months = []
        current = self.start_date.replace(day=1)

        while current <= self.end_date:
            months.append(current.strftime("%Y-%m"))
            if current.month == 12:  # noqa: PLR2004
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)

        return months

    def get_years_list(self) -> list[int]:
        """Get affected years list."""
        return list(range(self.start_date.year, self.end_date.year + 1))

    def split_by_years(self) -> list["UniversalTimeRange"]:
        """Split by years."""
        if self.start_date.year == self.end_date.year:
            return [self]

        yearly_ranges = []
        for year in self.get_years_list():
            year_start = max(self.start_date, date(year, 1, 1))
            year_end = min(self.end_date, date(year, 12, 31))

            yearly_range = UniversalTimeRange(
                start_date=year_start,
                end_date=year_end,
                granularity=TimeGranularity.YEARLY,
                description=f"{year} év részlet",
            )
            yearly_ranges.append(yearly_range)

        return yearly_ranges

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "granularity": self.granularity.value,
            "description": self.description,
            "total_days": self.total_days,
            "is_historical": self.is_historical,
            "is_future": self.is_future,
            "include_partial_periods": self.include_partial_periods,
            "exclude_weekends": self.exclude_weekends,
            "seasonal_filter": self.seasonal_filter,
        }


__all__ = ["UniversalTimeRange"]
