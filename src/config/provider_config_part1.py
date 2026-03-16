# ruff: noqa: F401,F403,F405,noqa: I001
# mypy: ignore-errors
"""Split definitions from provider_config.py."""

from __future__ import annotations

from .provider_config_support import *


def _resolve_config_attr(attr: str, fallback: T) -> T:
    """Return config module attribute if tests monkeypatch it."""
    config_module = sys.modules.get("src.config")
    if config_module and hasattr(config_module, attr):
        return cast(T, getattr(config_module, attr))
    return fallback


def _get_provider_prefs_file() -> Path:
    """Return current provider preferences path."""
    return _resolve_config_attr("PROVIDER_PREFS_FILE", DEFAULT_PROVIDER_PREFS_FILE)


def _ensure_directories() -> None:
    """Invoke the potentially monkeypatched ensure_directories helper."""
    resolver = _resolve_config_attr("ensure_directories", default_ensure_directories)
    resolver()


def _freeze_value(value: Any) -> Any:
    """Recursively freeze nested provider metadata structures."""
    if isinstance(value, dict):
        return MappingProxyType({key: _freeze_value(val) for key, val in value.items()})
    if isinstance(value, list):
        return tuple(_freeze_value(item) for item in value)
    return value


class ProviderConfig:
    """Provider Selector configuration and settings."""

    _PROVIDER_DATA: Dict[str, Dict[str, Any]] = {
        "auto": {
            "name": "Automatikus (Smart Routing)",
            "description": "Use-case alapú automatikus provider választás",
            "icon": "🤖",
            "cost": "Optimalizált",
            "routing_logic": {
                "single_city": "open-meteo",
                "multi_city": "meteostat",
                "historical_deep": "meteostat",
                "real_time": "open-meteo",
            },
        },
        "open-meteo": {
            "name": "Open-Meteo (Ingyenes)",
            "description": "Ingyenes globális időjárási API minden funkcióhoz",
            "icon": "🌍",
            "cost": "Ingyenes",
            "limitations": [
                "Limitált multi-city support",
                "Alapszintű történeti adatok",
            ],
        },
        "meteostat": {
            "name": "Meteostat (Prémium)",
            "description": "Prémium API gazdag történeti adatokkal és station-based accuracy",
            "icon": "💎",
            "cost": "$10 USD/hónap",
            "features": [
                "10k request/hónap",
                "Gazdag történeti adatok",
                "Station-based accuracy",
            ],
        },
    }

    PROVIDERS: Mapping[str, Mapping[str, Any]] = MappingProxyType(
        {key: _freeze_value(value) for key, value in _PROVIDER_DATA.items()}
    )

    DEFAULT_PROVIDER: str = "auto"
    USAGE_RESET_DAY: int = 1
    WARNING_THRESHOLD: float = 0.8
    CRITICAL_THRESHOLD: float = 0.95
    METEOSTAT_COST_PER_REQUEST: float = 0.001
    MONTHLY_BUDGET_USD: float = 10.0
