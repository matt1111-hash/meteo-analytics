"""Wind Rose API route - wind direction and speed distribution analysis."""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.data.weather_client_core import WeatherClient
from src.infrastructure.container import get_city_manager_port

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/weather", tags=["weather", "wind"])


# Pydantic models for request/response
class WindRoseRequest(BaseModel):
    """Request for wind rose analysis."""

    city: str = Field(..., description="City name to analyze")
    start: str = Field(..., description="Start date (YYYY-MM-DD)")
    end: str = Field(..., description="End date (YYYY-MM-DD)")


class DirectionData(BaseModel):
    """Wind direction data with speed buckets."""

    direction: str = Field(..., description="Compass direction (N, NNE, NE, etc.)")
    angle: float = Field(..., description="Direction angle in degrees")
    speed_buckets: List[int] = Field(
        ...,
        description="Count of observations in each speed category: "
        "[0-25, 25-50, 50-70, 70-100, 100-120, 120+] km/h",
    )


class WindRoseResponse(BaseModel):
    """Wind rose analysis response."""

    city: str = Field(..., description="City name")
    start: str = Field(..., description="Start date")
    end: str = Field(..., description="End date")
    directions: List[DirectionData] = Field(
        ..., description="16 compass directions with speed data"
    )
    calms_percentage: float = Field(
        ..., description="Percentage of calm winds (< 5 km/h)"
    )
    total_observations: int = Field(
        ..., description="Total number of wind observations"
    )
    statistics: Dict[str, Any] = Field(
        ..., description="Additional statistics (avg_speed, max_speed, data_source)"
    )


# Direction configuration (16 compass points)
DIRECTION_BINS = [
    0,
    22.5,
    45,
    67.5,
    90,
    112.5,
    135,
    157.5,
    180,
    202.5,
    225,
    247.5,
    270,
    292.5,
    315,
    337.5,
    360,
]
DIRECTION_LABELS = [
    "N",
    "NNE",
    "NE",
    "ENE",
    "E",
    "ESE",
    "SE",
    "SSE",
    "S",
    "SSW",
    "SW",
    "WSW",
    "W",
    "WNW",
    "NW",
    "NNW",
]

# Speed buckets (Beaufort-based categories)
SPEED_BINS = [0, 25, 50, 70, 100, 120, 999]  # Last bucket is 120+
SPEED_LABELS = ["0-25", "25-50", "50-70", "70-100", "100-120", "120+"]


def _process_wind_rose_data(daily_data: dict) -> dict:
    """
    Process daily weather data into wind rose format.

    Args:
        daily_data: Dictionary with daily weather data including:
                   - winddirection_10m_dominant: list of wind directions
                   - wind_gusts_10m_max or windspeed_10m_max: list of wind speeds

    Returns:
        Dictionary with directions array, calms_percentage, and statistics
    """
    dates = daily_data.get("time", []) or daily_data.get("date", [])
    winddirection = daily_data.get("winddirection_10m_dominant", [])
    wind_gusts_max = daily_data.get("wind_gusts_10m_max", [])
    windspeed_10m_max = daily_data.get("windspeed_10m_max", [])

    # Validate we have data
    if not dates or not winddirection:
        raise HTTPException(
            status_code=400, detail="Missing required data: dates or winddirection"
        )

    # Determine which speed metric to use (wind gusts prioritized)
    windspeed_data = []
    data_source = ""

    if wind_gusts_max and len(wind_gusts_max) == len(dates):
        # Check if we have valid numeric data
        if any(isinstance(x, (int, float)) and x is not None for x in wind_gusts_max):
            windspeed_data = wind_gusts_max
            data_source = "wind_gusts_max"
        elif windspeed_10m_max and len(windspeed_10m_max) == len(dates):
            if any(
                isinstance(x, (int, float)) and x is not None for x in windspeed_10m_max
            ):
                windspeed_data = windspeed_10m_max
                data_source = "windspeed_10m_max"

    if not windspeed_data:
        # Fallback to windspeed if no gusts
        if windspeed_10m_max and len(windspeed_10m_max) == len(dates):
            if any(
                isinstance(x, (int, float)) and x is not None for x in windspeed_10m_max
            ):
                windspeed_data = windspeed_10m_max
                data_source = "windspeed_10m_max"

    if not windspeed_data:
        raise HTTPException(
            status_code=400,
            detail="No valid wind speed data available (wind_gusts_10m_max or windspeed_10m_max)",
        )

    # Pair up the data and filter out invalid entries
    paired_data = []
    for i, date in enumerate(dates):
        if i >= len(winddirection) or i >= len(windspeed_data):
            continue

        direction = winddirection[i]
        speed = windspeed_data[i]

        # Skip invalid data
        if direction is None or speed is None:
            continue
        if not isinstance(direction, (int, float)):
            continue
        if not isinstance(speed, (int, float)):
            continue
        if direction < 0 or direction > 360:
            continue

        paired_data.append({"direction": direction, "speed": speed})

    if not paired_data:
        raise HTTPException(
            status_code=400, detail="No valid wind data after filtering"
        )

    total_observations = len(paired_data)

    # Initialize direction buckets
    direction_counts = []
    for i in range(len(DIRECTION_BINS) - 1):
        dir_start = DIRECTION_BINS[i]
        dir_end = DIRECTION_BINS[i + 1]

        # Filter observations for this direction
        direction_observations = [
            d["speed"]
            for d in paired_data
            if d["direction"] >= dir_start and d["direction"] < dir_end
        ]

        # Count observations in each speed bucket
        speed_buckets = [0] * (len(SPEED_BINS) - 1)
        if direction_observations:
            for speed in direction_observations:
                for j in range(len(SPEED_BINS) - 2):
                    if SPEED_BINS[j] <= speed < SPEED_BINS[j + 1]:
                        speed_buckets[j] += 1
                        break
                else:
                    # Last bucket (120+)
                    if speed >= SPEED_BINS[-2]:
                        speed_buckets[-1] += 1

        direction_counts.append(
            {
                "direction": DIRECTION_LABELS[i],
                "angle": (dir_start + dir_end) / 2,
                "speed_buckets": speed_buckets,
            }
        )

    # Calculate calms (wind speed < 5 km/h)
    calms_count = sum(1 for d in paired_data if d["speed"] < 5)
    calms_percentage = (
        (calms_count / total_observations * 100) if total_observations > 0 else 0
    )

    # Statistics
    speeds = [d["speed"] for d in paired_data]
    avg_speed = sum(speeds) / len(speeds) if speeds else 0
    max_speed = max(speeds) if speeds else 0

    return {
        "directions": direction_counts,
        "calms_percentage": round(calms_percentage, 1),
        "total_observations": total_observations,
        "statistics": {
            "avg_speed": round(avg_speed, 1),
            "max_speed": round(max_speed, 1),
            "data_source": data_source,
            "calms_count": calms_count,
        },
    }


@router.post("/wind-rose")
async def get_wind_rose(request: WindRoseRequest) -> WindRoseResponse:
    """
    Get wind rose data for a city and date range.

    Wind rose shows the distribution of wind speed and direction.
    Returns 16 compass directions, each with 6 speed buckets.

    Speed buckets (km/h):
    - 0-25: Calm to Light
    - 25-50: Light to Moderate
    - 50-70: Moderate to Fresh
    - 70-100: Fresh to Strong
    - 100-120: Strong to Very Strong
    - 120+: Extreme / Hurricane force

    Args:
        request: WindRoseRequest with city, start, and end dates

    Returns:
        WindRoseResponse with directions array and statistics
    """
    try:
        city_manager = get_city_manager_port()
        weather_client = WeatherClient()

        # Get city coordinates from city manager
        # find_city_by_name returns (latitude, longitude) tuple or None
        coords = city_manager.find_city_by_name(request.city.strip())
        if not coords:
            raise HTTPException(
                status_code=404, detail=f"City not found: {request.city}"
            )

        latitude, longitude = coords

        # Fetch weather data directly from Open-Meteo
        # The OpenMeteoProvider returns data with winddirection_10m_dominant included
        weather_records = weather_client.get_weather_data(
            latitude=latitude,
            longitude=longitude,
            start_date=request.start,
            end_date=request.end,
        )

        if not weather_records:
            raise HTTPException(
                status_code=404,
                detail=f"No weather data found for {request.city} in the specified period",
            )

        # Extract daily data from weather records
        # The records have a "daily" field with the Open-Meteo daily response
        daily_data = {}
        for record in weather_records:
            if isinstance(record, dict) and "daily" in record:
                daily_data = record["daily"]
                break

        if not daily_data:
            # Try alternate format - some records might be flat
            # In this case, we need to aggregate from individual records
            dates = list(
                set(
                    [
                        r.get("date") or r.get("time")
                        for r in weather_records
                        if r.get("date") or r.get("time")
                    ]
                )
            )
            dates.sort()

            # If no daily data found, check individual records
            if any(
                "winddirection_10m_dominant" in r
                for r in weather_records
                if isinstance(r, dict)
            ):
                # Reconstruct daily data from individual records
                daily_data = {
                    "time": dates,
                    "winddirection_10m_dominant": [
                        r.get("winddirection_10m_dominant") for r in weather_records
                    ],
                    "wind_gusts_10m_max": [
                        r.get("wind_gusts_10m_max") for r in weather_records
                    ],
                    "windspeed_10m_max": [
                        r.get("windspeed_10m_max") for r in weather_records
                    ],
                }

        if not daily_data:
            raise HTTPException(
                status_code=400, detail="No daily weather data available in response"
            )

        # Process data into wind rose format
        wind_rose_data = _process_wind_rose_data(daily_data)

        return WindRoseResponse(
            city=request.city,
            start=request.start,
            end=request.end,
            directions=wind_rose_data["directions"],
            calms_percentage=wind_rose_data["calms_percentage"],
            total_observations=wind_rose_data["total_observations"],
            statistics=wind_rose_data["statistics"],
        )

    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.error("Unexpected error in wind-rose endpoint: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error") from exc
