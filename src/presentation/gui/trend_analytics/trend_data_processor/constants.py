"""Trend data processor constants."""
from datetime import timedelta

# Trend parameter mapping (API fields)
TREND_PARAMETERS = {
    "🥶 Minimum hőmérséklet": "temperature_2m_min",
    "🔥 Maximum hőmérséklet": "temperature_2m_max",
    "🌡️ Átlag hőmérséklet": "temperature_2m_mean",
    "🌧️ Csapadékmennyiség": "precipitation_sum",
    "💨 Szélsebesség": "windspeed_10m_max",
    "💨 Széllökések": "windgusts_10m_max"
}

# Time range options (multi-year)
TIME_RANGES = {
    "5 év": 5,
    "10 év": 10,
    "25 év": 25,
    "55 év (teljes)": 55
}

# Default timedelta for year calculation
ONE_YEAR = timedelta(days=365)
