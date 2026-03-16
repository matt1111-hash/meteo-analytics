"""Comprehensive tests for src/config/config_validation.py."""

from __future__ import annotations

import pytest


class TestGetOptimalDataSource:
    """Test cases for get_optimal_data_source() function."""

    def test_get_optimal_data_source_single_city(self) -> None:
        from src.config.config_validation import get_optimal_data_source

        assert get_optimal_data_source("single_city") == "open-meteo"

    def test_get_optimal_data_source_multi_city(self) -> None:
        from src.config.config_validation import get_optimal_data_source

        assert get_optimal_data_source("multi_city") == "meteostat"

    def test_get_optimal_data_source_multi_city_prefer_free(self) -> None:
        from src.config.config_validation import get_optimal_data_source

        assert get_optimal_data_source("multi_city", prefer_free=True) == "meteostat"

    def test_get_optimal_data_source_historical_deep(self) -> None:
        from src.config.config_validation import get_optimal_data_source

        assert get_optimal_data_source("historical_deep") == "meteostat"

    def test_get_optimal_data_source_real_time(self) -> None:
        from src.config.config_validation import get_optimal_data_source

        assert get_optimal_data_source("real_time") == "open-meteo"

    def test_get_optimal_data_source_station_based(self) -> None:
        from src.config.config_validation import get_optimal_data_source

        assert get_optimal_data_source("station_based") == "meteostat"

    def test_get_optimal_data_source_interpolated(self) -> None:
        from src.config.config_validation import get_optimal_data_source

        assert get_optimal_data_source("interpolated") == "open-meteo"

    def test_get_optimal_data_source_unknown_use_case(self) -> None:
        from src.config.config_validation import get_optimal_data_source

        assert get_optimal_data_source("unknown_use_case") == "open-meteo"


class TestGetSourceDisplayName:
    """Test cases for get_source_display_name() function."""

    def test_get_source_display_name_open_meteo(self) -> None:
        from src.config.config_validation import get_source_display_name

        result = get_source_display_name("open-meteo")
        assert "Open-Meteo" in result

    def test_get_source_display_name_meteostat(self) -> None:
        from src.config.config_validation import get_source_display_name

        result = get_source_display_name("meteostat")
        assert "Meteostat" in result

    def test_get_source_display_name_unknown(self) -> None:
        from src.config.config_validation import get_source_display_name

        assert (
            get_source_display_name("unknown_source")
            == "Unknown Source (unknown_source)"
        )


class TestValidateApiSourceAvailable:
    """Test cases for validate_api_source_available() function."""

    def test_validate_open_meteo_always_available(self) -> None:
        from src.config.config_validation import validate_api_source_available

        assert validate_api_source_available("open-meteo") is True

    def test_validate_meteostat_with_valid_key(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.config.config_validation import validate_api_source_available

        monkeypatch.setenv("METEOSTAT_API_KEY", "a" * 32)
        assert validate_api_source_available("meteostat") is True

    def test_validate_meteostat_with_short_key(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.config.config_validation import validate_api_source_available

        monkeypatch.setenv("METEOSTAT_API_KEY", "short")
        assert validate_api_source_available("meteostat") is False

    def test_validate_meteostat_with_whitespace_key(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.config.config_validation import validate_api_source_available

        monkeypatch.setenv("METEOSTAT_API_KEY", "  " + "a" * 32 + "  ")
        assert validate_api_source_available("meteostat") is True

    def test_validate_meteostat_no_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from src.config.config_validation import validate_api_source_available

        monkeypatch.delenv("METEOSTAT_API_KEY", raising=False)
        assert validate_api_source_available("meteostat") is False

    def test_validate_unknown_source(self) -> None:
        from src.config.config_validation import validate_api_source_available

        assert validate_api_source_available("unknown_source") is False


class TestGetFallbackSourceChain:
    """Test cases for get_fallback_source_chain() function."""

    def test_fallback_chain_open_meteo_primary(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.config.config_validation import get_fallback_source_chain

        monkeypatch.delenv("METEOSTAT_API_KEY", raising=False)
        assert get_fallback_source_chain("open-meteo") == ["open-meteo"]

    def test_fallback_chain_meteostat_primary_with_key(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.config.config_validation import get_fallback_source_chain

        monkeypatch.setenv("METEOSTAT_API_KEY", "a" * 32)
        result = get_fallback_source_chain("meteostat")
        assert "meteostat" in result
        assert "open-meteo" in result
        assert result[0] == "meteostat"

    def test_fallback_chain_only_open_meteo_available(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.config.config_validation import get_fallback_source_chain

        monkeypatch.delenv("METEOSTAT_API_KEY", raising=False)
        assert get_fallback_source_chain("any_source") == ["open-meteo"]

    def test_fallback_chain_both_available(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from src.config.config_validation import get_fallback_source_chain

        monkeypatch.setenv("METEOSTAT_API_KEY", "a" * 32)
        result = get_fallback_source_chain("open-meteo")
        assert len(result) == 2
        assert "open-meteo" in result
        assert "meteostat" in result
        assert result[0] == "open-meteo"
