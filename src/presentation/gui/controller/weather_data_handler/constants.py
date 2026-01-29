"""Weather data handler constants."""
# Required daily fields for processing
REQUIRED_DAILY_FIELDS = [
    'time',
    'temperature_2m_max',
    'temperature_2m_min',
    'precipitation_sum',
    'windspeed_10m_max'
]

# Optional daily fields
OPTIONAL_DAILY_FIELDS = [
    'windspeed_10m_mean',
    'winddirection_10m_dominant',
    'apparent_temperature_max',
    'apparent_temperature_min',
    'shortwave_radiation_sum',
    'et0_fao_evapotranspiration'
]

# Wind speed thresholds for logging
WIND_THRESHOLDS = {
    'hurricane': 120,
    'extreme': 100,
    'storm': 80,
    'strong': 60
}

# Field mappings for compatibility
WIND_DIRECTION_MAPPING = {
    'winddirection_10m_dominant': 'wind_direction_10m_dominant'
}
