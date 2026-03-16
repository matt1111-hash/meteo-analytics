#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mypy: ignore-errors

"""
Worker Utilities - Helper functions for the workers module

Validációs és segédfüggvények a worker-ekhez.
"""

from datetime import datetime
from typing import Any, Dict


def validate_coordinates(latitude: float, longitude: float) -> bool:
    """Koordináták validálása."""
    return (-90.0 <= latitude <= 90.0) and (-180.0 <= longitude <= 180.0)


def validate_date_string(date_str: str) -> bool:
    """Dátum string validálása YYYY-MM-DD formátumban."""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def calculate_date_range_days(start_date: str, end_date: str) -> int:
    """Dátum tartomány napokban."""
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        return (end - start).days
    except ValueError:
        return 0


def format_api_error(status_code: int, response_text: str) -> str:
    """API hiba formázása user-friendly módon."""
    error_messages = {
        400: "Hibás kérés - ellenőrizze a paramétereket",
        401: "Hitelesítési hiba - ellenőrizze az API kulcsot",
        403: "Hozzáférés megtagadva",
        404: "API endpoint nem található",
        429: "Túl sok kérés - próbálja újra később",
        500: "Szerver hiba - próbálja újra később",
        502: "Bad Gateway - szolgáltatás átmenetileg nem elérhető",
        503: "Szolgáltatás nem elérhető",
    }

    user_message = error_messages.get(status_code, f"HTTP {status_code} hiba")

    if len(response_text) < 200:
        user_message += f" ({response_text})"

    return user_message


def create_weather_worker_with_provider(
    latitude: float,
    longitude: float,
    start_date: str,
    end_date: str,
    preferred_provider: str = "auto",
):
    """
    🌍 Weather data worker létrehozása provider routing támogatással.

    Args:
        latitude: Szélességi fok
        longitude: Hosszúsági fok
        start_date: Kezdő dátum (YYYY-MM-DD)
        end_date: Befejező dátum (YYYY-MM-DD)
        preferred_provider: Preferált provider ("auto", "open-meteo", "meteostat")

    Returns:
        Konfigurált WeatherDataWorker instance
    """
    from .weather_data_worker import WeatherDataWorker

    worker = WeatherDataWorker(
        latitude=latitude,
        longitude=longitude,
        start_date=start_date,
        end_date=end_date,
        preferred_provider=preferred_provider,
    )

    print(f"🌍 DEBUG: Weather worker created with provider: {preferred_provider}")
    return worker


def get_worker_manager_provider_summary(manager) -> Dict[str, Any]:
    """
    🌍 WorkerManager provider összefoglaló lekérdezése.

    Args:
        manager: WorkerManager instance

    Returns:
        Provider summary dictionary
    """
    provider_states = manager.get_provider_states()
    last_successful = manager.get_last_successful_provider()

    summary = {
        "provider_states": provider_states,
        "last_successful_provider": last_successful,
        "active_workers": manager.get_active_workers(),
        "total_providers_tracked": len(provider_states),
        "worker_count": manager.get_worker_count(),
    }

    return summary


def create_comprehensive_worker_manager():
    """
    🔧 Comprehensive WorkerManager létrehozása teljes funkcionalitással.

    Returns:
        Fully configured WorkerManager instance
    """
    from .worker_manager import WorkerManager

    manager = WorkerManager()

    print("✅ DEBUG: Comprehensive WorkerManager created with:")
    print("  🔧 Completion signal routing")
    print("  🌍 Provider routing support")
    print("  🌪️ Wind gusts functionality")
    print("  🛑 Full cancellation support")
    print("  📊 Provider state tracking")
    print("  🚨 Emergency shutdown procedures")

    return manager
