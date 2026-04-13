"""City info domain entity."""

from dataclasses import dataclass
from typing import Any


@dataclass
class CityInfo:
    """
    City information model.

    CityManager database record representation.
    """

    id: int
    city: str
    latitude: float
    longitude: float
    country: str
    country_code: str

    # Optional fields
    population: int | None = None
    continent: str | None = None
    admin_name: str | None = None
    capital: str | None = None
    timezone: str | None = None

    def get_display_name(self) -> str:
        """Get display name."""
        return f"{self.city}, {self.country}"

    def get_coordinates(self) -> tuple[float, float]:
        """Get coordinates."""
        return (self.latitude, self.longitude)

    def is_capital(self) -> bool:
        """Check if capital."""
        return self.capital == "primary"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "city": self.city,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "country": self.country,
            "country_code": self.country_code,
            "population": self.population,
            "continent": self.continent,
            "admin_name": self.admin_name,
            "capital": self.capital,
            "timezone": self.timezone,
        }


__all__ = ["CityInfo"]
