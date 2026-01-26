#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Global Weather Analyzer - GUI Constants Module.
GUI konstansok: API, GUI, Anomália és Adatkezelés konstansai.

🌍 DUAL-API SYSTEM:
✅ Open-Meteo API (FREE - Primary)
✅ Meteostat API (PREMIUM - Multi-city & Historical)
✅ Smart source routing
✅ Multi-city támogatás

🌪️ WIND GUSTS ANOMALY CONSTANTS:
✅ WIND_HIGH_THRESHOLD 70.0 km/h (erős széllökés)
✅ WIND_EXTREME_THRESHOLD 100.0 km/h (extrém széllökés)
✅ WIND_HURRICANE_THRESHOLD 120.0 km/h (hurrikán erősségű)
✅ Élethű széllökés kategorizálás Balatonfüred 130+ km/h adatokhoz
✅ Backward compatibility windspeed_10m_max küszöbökkel

🚀 PROFESSZIONÁLIS KÓDOLÁSI ELVEK:
✅ DRY: Központosított konstansok
✅ KISS: Egyszerű, érthető kategorizálás
✅ YAGNI: Csak szükséges funkcionalitás
✅ SOLID: Egyszeres felelősség
✅ Type hints: Minden érték explicit típussal
"""

from typing import Any, Dict

# Import types from parent module
from src.presentation.gui.types import ColorVariant, ThemeType


class APIConstants:
    """API konstansok - URL-ek, timeoutok, retry beállítások - CLEAN DUAL-API VERZIÓ"""

    # === CLEAN DUAL-API SYSTEM ===

    # Open-Meteo API endpoints (FREE - Primary)
    OPEN_METEO_BASE = "https://api.open-meteo.com/v1"
    OPEN_METEO_ARCHIVE = "https://archive-api.open-meteo.com/v1/archive"
    OPEN_METEO_GEOCODING = "https://geocoding-api.open-meteo.com/v1/search"

    # Meteostat API endpoints (PREMIUM - Multi-city & Historical)
    METEOSTAT_BASE = "https://meteostat.p.rapidapi.com"
    METEOSTAT_STATIONS_NEARBY = f"{METEOSTAT_BASE}/stations/nearby"
    METEOSTAT_STATIONS_META = f"{METEOSTAT_BASE}/stations/meta"
    METEOSTAT_STATIONS_DAILY = f"{METEOSTAT_BASE}/stations/daily"
    METEOSTAT_POINT_DAILY = f"{METEOSTAT_BASE}/point/daily"

    # API Configuration
    DEFAULT_TIMEOUT = 30  # másodperc
    MAX_RETRIES = 3
    CACHE_DURATION = 3600  # 1 óra másodpercben
    USER_AGENT = "Global Weather Analyzer/2.1.0 (Dual-API Edition)"

    # Rate Limiting Configuration
    OPENMETEO_RATE_LIMIT = 0.1  # 10 requests/second
    METEOSTAT_RATE_LIMIT = 0.1  # 100ms delay for premium API
    METEOSTAT_MONTHLY_LIMIT = 10000  # 10k requests/month

    # Source Display Names
    SOURCE_DISPLAY_NAMES = {
        "open-meteo": "🌍 Open-Meteo API",
        "meteostat": "💎 Meteostat API"
    }


class GUIConstants:
    """GUI konstansok - méretek, pozíciók, betűtípusok - BŐVÍTETT"""

    # Fő ablak beállítások
    MAIN_WINDOW_WIDTH = 1200
    MAIN_WINDOW_HEIGHT = 800
    MAIN_WINDOW_MIN_WIDTH = 900
    MAIN_WINDOW_MIN_HEIGHT = 600
    MAIN_WINDOW_X = 100
    MAIN_WINDOW_Y = 100

    # Dialog beállítások
    DIALOG_MIN_WIDTH = 600
    DIALOG_MIN_HEIGHT = 400

    # Panel beállítások - JAVÍTOTT SPLITTER KONSTANSOK
    CONTROL_PANEL_MIN_WIDTH = 280
    CONTROL_PANEL_MAX_WIDTH = 400
    CONTROL_PANEL_MARGINS = (10, 10, 10, 10)
    RESULTS_PANEL_MARGINS = (10, 10, 10, 10)

    # Layout beállítások
    LAYOUT_SPACING = 10
    MAIN_LAYOUT_MARGINS = (10, 10, 10, 10)

    # Widget beállítások - SPLITTER JAVÍTÁSOK
    BUTTON_HEIGHT = 32
    SPLITTER_HANDLE_WIDTH = 8  # KRITIKUS: Splitter handle méret
    SPLITTER_MIN_SIZE = 200    # ÚJ: Minimum panel méret
    CHART_MIN_HEIGHT = 300
    TABLE_MIN_HEIGHT = 200
    CONTROL_BAR_HEIGHT = 50

    # Font beállítások
    DEFAULT_FONT_FAMILY = "Segoe UI, Arial, sans-serif"
    DEFAULT_FONT_SIZE = 10
    TITLE_FONT_SIZE = 12
    HEADER_FONT_SIZE = 14

    # === ÚJ: SEMANTIC COLOR SYSTEM ALAPJAI ===
    # Színkonstansok semantic névekkel
    PRIMARY_COLOR = "#2563eb"      # Fő brand szín (kék)
    SUCCESS_COLOR = "#10b981"      # Sikeres műveletek (zöld)
    WARNING_COLOR = "#f59e0b"      # Figyelmeztetések (sárga)
    ERROR_COLOR = "#dc2626"        # Hibák, törlés (piros)
    INFO_COLOR = "#6b7280"         # Információs üzenetek (szürke)

    # Surface színek (background-ok)
    SURFACE_LIGHT = "#ffffff"      # Light mode háttér
    SURFACE_DARK = "#1f2937"       # Dark mode háttér
    ON_SURFACE_LIGHT = "#1f2937"   # Light mode szöveg
    ON_SURFACE_DARK = "#f9fafb"    # Dark mode szöveg


class AnomalyConstants:
    """
    🌪️ KRITIKUS JAVÍTÁS: Anomália detektálás konstansai - WIND GUSTS ÉLETHŰ KÜSZÖBÖKKEL.

    Küszöbértékek és kategóriák élethű széllökés értékekhez optimalizálva.
    Balatonfüredi 130+ km/h széllökések alapján kalibrálva.

    🚀 PROFESSZIONÁLIS KÓDOLÁSI ELVEK:
    ✅ DRY: Központosított konstansok
    ✅ KISS: Egyszerű, érthető kategorizálás
    ✅ SOLID: Egyszeres felelősség
    ✅ Type safety: Minden érték explicit típussal
    """

    # Hőmérséklet anomáliák (Celsius) - VÁLTOZATLAN
    TEMP_HOT_THRESHOLD = 35.0      # Szokatlanul meleg
    TEMP_COLD_THRESHOLD = -10.0    # Szokatlanul hideg
    TEMP_EXTREME_HOT = 40.0        # Extrém meleg
    TEMP_EXTREME_COLD = -20.0      # Extrém hideg

    # Csapadék anomáliák (mm) - VÁLTOZATLAN
    PRECIP_HIGH_THRESHOLD = 100.0  # Szokatlanul csapadékos (időszakban)
    PRECIP_LOW_THRESHOLD = 10.0    # Szokatlanul száraz (időszakban)
    PRECIP_EXTREME_HIGH = 200.0    # Extrém csapadékos
    PRECIP_DAILY_EXTREME = 50.0    # Extrém napi csapadék

    # 🌪️ KRITIKUS JAVÍTÁS: Szél anomáliák (km/h) - ÉLETHŰ WIND GUSTS KÜSZÖBÖK
    WIND_HIGH_THRESHOLD = 70.0     # 50.0 → 70.0 km/h - Erős széllökés
    WIND_EXTREME_THRESHOLD = 100.0  # 80.0 → 100.0 km/h - Extrém széllökés
    WIND_HURRICANE_THRESHOLD = 120.0  # 120.0 (változatlan) - Hurrikán erősségű szél

    # 🌪️ KRITIKUS JAVÍTÁS: ÚJ WIND GUSTS SPECIFIKUS KÜSZÖBÖK - METEOROLÓGIAI STANDARDOKRA KALIBRÁLVA
    WIND_GUSTS_CALM = 0.0          # Szélcsend
    WIND_GUSTS_LIGHT = 10.0        # Enyhe szél
    WIND_GUSTS_MODERATE = 30.0     # 40.0 → 30.0 - Mérsékelt szél
    WIND_GUSTS_STRONG = 50.0       # 70.0 → 50.0 - Erős szél (Beaufort 7-8)
    WIND_GUSTS_STORMY = 70.0       # ÚJ KATEGÓRIA - Viharos szél
    WIND_GUSTS_EXTREME = 100.0     # Extrém széllökés
    WIND_GUSTS_HURRICANE = 120.0   # Hurrikán erősségű
    WIND_GUSTS_CATASTROPHIC = 150.0  # Katasztrofális (tornadó szintű)

    # 🌪️ KRITIKUS JAVÍTÁS: Windspeed vs Wind Gusts különbönető küszöbök
    # Backward compatibility windspeed_10m_max-hoz
    WINDSPEED_HIGH_THRESHOLD = 50.0    # Eredeti küszöb windspeed-hez
    WINDSPEED_EXTREME_THRESHOLD = 80.0  # Eredeti küszöb windspeed-hez

    # Statisztikai konstansok - VÁLTOZATLAN
    STANDARD_DEVIATION_MULTIPLIER = 2.0  # Hány szórás az anomália küszöb
    MIN_DATA_POINTS = 30                 # Minimum adatpont az anomália detektáláshoz

    # === ÚJ: ANOMÁLIA KATEGÓRIÁK ===
    ANOMALY_CATEGORIES = {
        "NORMAL": {"threshold": 1.0, "color": "#10b981", "label": "Normális"},
        "MILD": {"threshold": 1.5, "color": "#f59e0b", "label": "Enyhe anomália"},
        "MODERATE": {"threshold": 2.0, "color": "#ef4444", "label": "Közepes anomália"},
        "SEVERE": {"threshold": 3.0, "color": "#dc2626", "label": "Súlyos anomália"},
        "EXTREME": {"threshold": 4.0, "color": "#7c2d12", "label": "Extrém anomália"}
    }

    # 🌪️ KRITIKUS JAVÍTÁS: Széllökés kategóriák METEOROLÓGIAI STANDARDOKRA KALIBRÁLVA
    WIND_GUSTS_CATEGORIES = {
        "CALM": {"threshold": 0.0, "max": 10.0, "color": "#a3a3a3", "label": "Szélcsend", "emoji": "🌤️"},
        "LIGHT": {"threshold": 10.0, "max": 30.0, "color": "#86efac", "label": "Enyhe szél", "emoji": "🍃"},
        "MODERATE": {"threshold": 30.0, "max": 50.0, "color": "#f59e0b", "label": "Mérsékelt szél", "emoji": "💨"},
        "STRONG": {"threshold": 50.0, "max": 70.0, "color": "#f87171", "label": "Erős szél", "emoji": "🌪️"},
        "STORMY": {"threshold": 70.0, "max": 100.0, "color": "#dc2626", "label": "Viharos szél", "emoji": "⚠️"},
        "EXTREME": {"threshold": 100.0, "max": 120.0, "color": "#991b1b", "label": "Extrém széllökés", "emoji": "🚨"},
        "HURRICANE": {"threshold": 120.0, "max": 150.0, "color": "#7c2d12", "label": "Hurrikán erősségű", "emoji": "☢️"},
        "CATASTROPHIC": {"threshold": 150.0, "max": 999.0, "color": "#450a0a", "label": "Katasztrofális", "emoji": "💀"}
    }

    # Színkódok az anomáliákhoz - SEMANTIC COLORS
    NORMAL_COLOR = "#10b981"       # Zöld - normális
    WARNING_COLOR = "#f59e0b"      # Sárga - figyelmeztetés
    DANGER_COLOR = "#dc2626"       # Piros - veszélyes
    EXTREME_COLOR = "#7c2d12"      # Sötét piros - extrém

    # 🌪️ KRITIKUS JAVÍTÁS: Széllökés specifikus színek - METEOROLÓGIAI STANDARDOKKAL
    WIND_GUSTS_COLORS = {
        "normal": "#10b981",       # Zöld - normális (0-30 km/h)
        "moderate": "#f59e0b",     # Sárga - mérsékelt (30-50 km/h)
        "strong": "#f87171",       # Narancs - erős (50-70 km/h)
        "stormy": "#dc2626",       # Piros - viharos (70-100 km/h)
        "extreme": "#991b1b",      # Sötét piros - extrém (100-120 km/h)
        "hurricane": "#7c2d12",    # Legbordó - hurrikán (120-150 km/h)
        "catastrophic": "#450a0a"  # Legdörgebbsötét - katasztrofális (150+ km/h)
    }


class DataConstants:
    """Adatkezelés konstansai - CLEAN DUAL-API VERZIÓ"""

    # API válasz mezők - Open-Meteo
    OPEN_METEO_DAILY_FIELDS = [
        "temperature_2m_max",
        "temperature_2m_min",
        "temperature_2m_mean",  # ÚJ: átlag hőmérséklet
        "precipitation_sum",
        "windspeed_10m_max",
        "winddirection_10m_dominant",  # ÚJ: szélirány
        "weathercode"
    ]

    # 🌪️ KRITIKUS JAVÍTÁS: WIND GUSTS mezők hozzáadása
    OPEN_METEO_HOURLY_FIELDS = [
        "wind_gusts_10m",        # ÚJ: óránkénti széllökések
        "windspeed_10m"          # ÚJ: óránkénti szélsebesség
    ]

    # Meteostat API mezők
    METEOSTAT_DAILY_FIELDS = [
        "tavg",  # Átlag hőmérséklet
        "tmin",  # Min hőmérséklet
        "tmax",  # Max hőmérséklet
        "prcp",  # Csapadék
        "snow",  # Hó
        "wdir",  # Szélirány
        "wspd",  # Szélsebesség
        "wpgt",  # Széllökés (KRITIKUS MEZŐ!)
        "pres",  # Légnyomás
        "tsun"   # Napsütés
    ]

    # 🌪️ KRITIKUS JAVÍTÁS: Processed mezők wind gusts támogatással
    PROCESSED_DAILY_FIELDS = [
        "temperature_2m_max",
        "temperature_2m_min",
        "temperature_2m_mean",
        "precipitation_sum",
        "windspeed_10m_max",      # Backward compatibility
        "wind_gusts_max",         # ÚJ: napi maximum széllökések
        "winddirection_10m_dominant",
        "weathercode"
    ]

    # Export formátumok
    SUPPORTED_EXPORT_FORMATS = ["csv", "excel", "json", "pdf"]  # PDF hozzáadva

    # Pagination
    DEFAULT_PAGE_SIZE = 100
    MAX_PAGE_SIZE = 1000

    # Cache beállítások
    CACHE_EXPIRY_HOURS = 24
    MAX_CACHE_SIZE_MB = 100

    # === ÚJ: DUAL-API ADATFORRÁS STRATÉGIA ===

    # Primary data source selection based on use case
    USE_CASE_SOURCE_MAPPING = {
        "single_city": "open-meteo",     # Free tier for single city
        "multi_city": "meteostat",       # Premium tier for multi-city
        "historical_deep": "meteostat",  # Rich historical data
        "real_time": "open-meteo",       # Real-time weather
        "station_based": "meteostat",    # Station-based accuracy
        "interpolated": "open-meteo"     # Grid-based interpolation
    }

    # Source priority order (fallback chain)
    DATA_SOURCE_PRIORITY = [
        "open-meteo",    # Elsődleges: Open-Meteo API (ingyenes)
        "meteostat"      # Másodlagos: Meteostat API (prémium backup)
    ]

    # Source capabilities matrix
    SOURCE_CAPABILITIES = {
        "open-meteo": {
            "historical": True,
            "real_time": True,
            "multi_city": True,
            "station_based": False,
            "cost": "free",
            "rate_limit": "10/sec",
            "wind_gusts": True,
            "rich_params": False
        },
        "meteostat": {
            "historical": True,
            "real_time": False,
            "multi_city": True,
            "station_based": True,
            "cost": "premium",
            "rate_limit": "10k/month",
            "wind_gusts": True,
            "rich_params": True  # pressure, sunshine, etc.
        }
    }


# Re-export types for backward compatibility
__all__ = [
    "APIConstants",
    "GUIConstants",
    "AnomalyConstants",
    "DataConstants",
    "ThemeType",
    "ColorVariant",
]
