"""Konfigurációs segédfüggvények izolált tesztjei."""

from __future__ import annotations

import json
from datetime import datetime

import pytest

from src import config


def test_user_preferences_loads_defaults_when_file_missing(config_fs: Dict[str, str]) -> None:
    """Hiányzó fájl esetén a default beállítások térnek vissza."""
    config_fs.pop("prefs", None)
    prefs = config.UserPreferences.load_provider_preferences()
    assert prefs["selected_provider"] == config.ProviderConfig.DEFAULT_PROVIDER
    assert prefs["auto_fallback_enabled"] is True
    assert prefs["warning_threshold"] == config.ProviderConfig.WARNING_THRESHOLD


def test_user_preferences_merges_saved_fields(config_fs: Dict[str, str]) -> None:
    """Meglévő JSON esetén a hiányzó kulcsok alapértékre esnek vissza."""
    config_fs["prefs"] = json.dumps(
        {"selected_provider": "meteostat", "auto_fallback_enabled": False}
    )
    prefs = config.UserPreferences.load_provider_preferences()
    assert prefs["selected_provider"] == "meteostat"
    assert prefs["auto_fallback_enabled"] is False
    assert prefs["monthly_budget_usd"] == config.ProviderConfig.MONTHLY_BUDGET_USD


def test_user_preferences_load_handles_corrupted_json(config_fs: Dict[str, str]) -> None:
    """Sérült tartalom esetén is default értékek érkeznek."""
    config_fs["prefs"] = "{ not valid json"
    prefs = config.UserPreferences.load_provider_preferences()
    assert prefs["selected_provider"] == config.ProviderConfig.DEFAULT_PROVIDER


def test_user_preferences_save_updates_timestamp(config_fs: Dict[str, str]) -> None:
    """Mentéskor bekerül a frissített időbélyeg és a JSON elérhető."""
    payload = {"selected_provider": "meteostat"}
    assert config.UserPreferences.save_provider_preferences(payload) is True
    saved = json.loads(config_fs["prefs"])
    assert saved["selected_provider"] == "meteostat"
    assert "last_updated" in saved


def test_user_preferences_save_handles_failure(monkeypatch: pytest.MonkeyPatch, config_fs: Dict[str, str]) -> None:
    """Mentési hiba esetén ne jöjjön létre fájl."""
    monkeypatch.setattr(config, "ensure_directories", lambda: (_ for _ in ()).throw(OSError("boom")))
    result = config.UserPreferences.save_provider_preferences({"selected_provider": "meteostat"})
    assert result is False
    assert "prefs" not in config_fs
# Lefedett ág: save_provider_preferences kivétel esetén (src/config.py:345-364)


def test_usage_tracker_load_resets_new_month(monkeypatch: pytest.MonkeyPatch, config_fs: Dict[str, str]) -> None:
    """Hónapváltáskor resetelődjön az API usage."""
    config_fs["usage"] = json.dumps({
        "current_month": "2024-06",
        "total_requests": 42,
        "meteostat": {"requests_this_month": 10, "estimated_cost_usd": 5.0, "daily_breakdown": {"2024-06-10": 10}},
        "open_meteo": {"requests_this_month": 5, "daily_breakdown": {"2024-06-10": 5}},
    })

    fixed_now = datetime(2024, 7, 15, 12, 0, 0)

    class FakeDatetime:
        @classmethod
        def now(cls):
            return fixed_now

        @staticmethod
        def strftime(value: str) -> str:
            return fixed_now.strftime(value)

    monkeypatch.setattr(config, "datetime", FakeDatetime)
    usage = config.UsageTracker.load_usage_data()
    assert usage["current_month"] == "2024-07"
    assert usage["total_requests"] == 0
    assert usage["meteostat"]["requests_this_month"] == 0
    assert usage["meteostat"]["estimated_cost_usd"] == 0.0
    assert usage["meteostat"]["daily_breakdown"] == {}
    assert usage["open_meteo"]["requests_this_month"] == 0
    assert usage["open_meteo"]["daily_breakdown"] == {}
# Lefedett ág: UsageTracker.load_usage_data hónapváltás reset (src/config.py:395–436)


def test_usage_tracker_load_handles_json_error(monkeypatch: pytest.MonkeyPatch, config_fs: Dict[str, str]) -> None:
    """JSON parse hiba esetén default usage térjen vissza."""
    config_fs["usage"] = "invalid"

    def fake_json_load(_):
        raise json.JSONDecodeError("boom", "xx", 0)

    fixed_now = datetime(2024, 7, 15, 12, 0, 0)

    class FakeDatetime:
        @classmethod
        def now(cls):
            return fixed_now

        @staticmethod
        def strftime(fmt: str) -> str:
            return fixed_now.strftime(fmt)

    monkeypatch.setattr(json, "load", fake_json_load)
    monkeypatch.setattr(config, "datetime", FakeDatetime)

    usage = config.UsageTracker.load_usage_data()
    assert usage["total_requests"] == 0
    assert usage["meteostat"]["requests_this_month"] == 0
    assert usage["meteostat"]["daily_breakdown"] == {}
    assert usage["open_meteo"]["requests_this_month"] == 0
    assert usage["current_month"] == "2024-07"
# Lefedett ág: UsageTracker.load_usage_data JSON hiba fallback (src/config.py:422–436)
def test_validate_api_keys_checks_length(monkeypatch: pytest.MonkeyPatch) -> None:
    """A Meteostat kulcs csak megfelelő hossz esetén tekinthető érvényesnek."""
    monkeypatch.setattr(config.APIConfig, "METEOSTAT_API_KEY", "a" * 40)
    valid = config.validate_api_keys()
    assert valid["meteostat_key_present"] is True
    assert valid["meteostat_key_valid"] is True

    monkeypatch.setattr(config.APIConfig, "METEOSTAT_API_KEY", "short")
    invalid = config.validate_api_keys()
    assert invalid["meteostat_key_valid"] is False


def test_usage_tracker_reset_clears_monthly_stats() -> None:
    """Új hónap esetén a számlálók nullázódnak."""
    usage = {
        "current_month": "2024-06",
        "month_start_date": "2024-06-01",
        "total_requests": 42,
        "meteostat": {"requests_this_month": 10, "estimated_cost_usd": 5.0, "daily_breakdown": {"2024-06-10": 10}},
        "open_meteo": {"requests_this_month": 5, "daily_breakdown": {"2024-06-10": 5}},
    }
    updated = config.UsageTracker._reset_monthly_usage(usage, "2024-07")
    assert updated["current_month"] == "2024-07"
    assert updated["meteostat"]["requests_this_month"] == 0
    assert updated["meteostat"]["estimated_cost_usd"] == 0.0
    assert updated["open_meteo"]["daily_breakdown"] == {}
    assert updated["total_requests"] == 0


def test_get_resolved_provider_prefers_override_and_auto(monkeypatch: pytest.MonkeyPatch) -> None:
    """Az override elsőbbséget élvez, egyébként az auto routing érvényesül."""
    monkeypatch.setattr(
        config.UserPreferences,
        "get_selected_provider",
        staticmethod(lambda: "auto"),
    )
    assert config.get_resolved_provider("multi_city") == "meteostat"
    assert config.get_resolved_provider("single_city", user_override="open-meteo") == "open-meteo"

    monkeypatch.setattr(
        config.UserPreferences,
        "get_selected_provider",
        staticmethod(lambda: "meteostat"),
    )
    assert config.get_resolved_provider("single_city") == "meteostat"
