"""Bridge constants and configurations."""
from src.data.enums import AnalyticsMetric


# 🔧 KRITIKUS: METRIC_MAP - AnalyticsMetric → Display Parameter Mapping
METRIC_MAP = {
    # Hőmérséklet metrikák
    AnalyticsMetric.TEMPERATURE_2M_MAX: 'temperature',
    AnalyticsMetric.TEMPERATURE_2M_MIN: 'temperature',
    AnalyticsMetric.TEMPERATURE_2M_MEAN: 'temperature',
    AnalyticsMetric.TEMPERATURE_RANGE: 'temperature',

    # Csapadék metrikák
    AnalyticsMetric.PRECIPITATION_SUM: 'precipitation',

    # Szél metrikák - KRITIKUS JAVÍTÁS
    AnalyticsMetric.WINDSPEED_10M_MAX: 'wind_speed',
    AnalyticsMetric.WINDGUSTS_10M_MAX: 'wind_gusts',
}

# Metrika → Overlay típus mapping (kompatibilitás)
METRIC_TO_OVERLAY = METRIC_MAP

# Overlay konfigurációk
OVERLAY_CONFIGS = {
    'temperature': {
        'name': 'Hőmérséklet',
        'unit': '°C',
        'color_scale': 'RdYlBu_r',
        'default_range': (-20, 40),
        'icon': '🌡️'
    },
    'precipitation': {
        'name': 'Csapadék',
        'unit': 'mm',
        'color_scale': 'Blues',
        'default_range': (0, 50),
        'icon': '🌧️'
    },
    'wind_speed': {
        'name': 'Szélsebesség',
        'unit': 'km/h',
        'color_scale': 'Greens',
        'default_range': (0, 60),
        'icon': '💨'
    },
    'wind_gusts': {
        'name': 'Széllökések',
        'unit': 'km/h',
        'color_scale': 'Oranges',
        'default_range': (0, 100),
        'icon': '🌪️'
    }
}

# Display parameter normalizálási map
DISPLAY_PARAMETER_MAP = {
    "Hőmérséklet": "temperature",
    "Szél": "wind_speed",
    "Széllökés": "wind_gusts",
    "Csapadék": "precipitation",
    "Páratartalom": "humidity",
    "Légnyomás": "pressure"
}
