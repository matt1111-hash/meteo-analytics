#!/usr/bin/env python3
# mypy: ignore-errors

"""
Results Panel Utils - Wind Constants

🌪️ Széllökés kategorizálási és küszöb konstansok

Képességek:
- Meteorológiai standardok (Beaufort skála)
- Széllökés kategóriák és küszöbök
- Magyar lokalizáció

Fájl: src/presentation/gui/results_panel/utils/wind_constants.py
"""


class WindGustsConstants:
    """
    🌪️ Széllökés kategorizálási és küszöb konstansok.
    METEOROLÓGIAI STANDARDOKRA KALIBRÁLT értékek.
    """

    # Széllökés kategóriák km/h-ban - ÉLETHŰ ÉRTÉKEK
    MODERATE_THRESHOLD = 50.0  # Mérsékelt széllökés (Beaufort 6-7)
    STRONG_THRESHOLD = 70.0  # Erős széllökés (Beaufort 8)
    EXTREME_THRESHOLD = 100.0  # Extrém széllökés (Beaufort 10)
    HURRICANE_THRESHOLD = 120.0  # Hurrikán erősségű (Beaufort 12)

    # Windy days küszöbök (data source alapján)
    # 🇭🇺 MAGYAR METEOROLÓGIAI STANDARD: 43 km/h-tól erősen szeles
    WINDY_THRESHOLD_GUSTS = 43.0  # wind_gusts_max esetén (széllökés)
    WINDY_THRESHOLD_WINDSPEED = 43.0  # windspeed_10m_max esetén (szélsebesség)

    # Kategória címkék - MAGYAR LOKALIZÁCIÓ
    CATEGORIES: dict[str, str] = {  # noqa: RUF012
        "moderate": "MÉRSÉKELT",
        "strong": "ERŐS",
        "extreme": "EXTRÉM",
        "hurricane": "HURRIKÁN ERŐSSÉGŰ",
    }

    # Kategória színek (ThemeManager kompatibilis)
    CATEGORY_COLORS: dict[str, str] = {  # noqa: RUF012
        "moderate": "success",  # Zöld - biztonságos
        "strong": "warning",  # Sárga - figyelem
        "extreme": "error",  # Piros - veszélyes
        "hurricane": "error",  # Piros - kritikus
    }

    # Emoji ikonok kategóriánként
    CATEGORY_EMOJIS: dict[str, str] = {  # noqa: RUF012
        "moderate": "💨",
        "strong": "🌪️",
        "extreme": "⚠️",
        "hurricane": "🚨",
    }
