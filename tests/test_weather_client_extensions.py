"""WeatherClientExtensions tesztjei."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from src.data.weather_client_extensions import WeatherClientExtensions


class TestSetPreferredProvider:
    """set_preferred_provider metódus tesztjei."""

    def test_set_auto_provider(self) -> None:
        """Auto provider beállítása."""
        client = WeatherClientExtensions()
        client.set_preferred_provider("auto")
        assert client.preferred_provider == "auto"

    def test_set_openmeteo_provider(self) -> None:
        """OpenMeteo provider beállítása."""
        client = WeatherClientExtensions()
        client.set_preferred_provider("open-meteo")
        assert client.preferred_provider == "open-meteo"

    def test_set_meteostat_provider(self) -> None:
        """Meteostat provider beállítása."""
        client = WeatherClientExtensions()
        client.set_preferred_provider("meteostat")
        assert client.preferred_provider == "meteostat"

    def test_set_unknown_provider_raises_error(self) -> None:
        """Ismeretlen provider beállítása ValueError-t dob."""
        client = WeatherClientExtensions()
        with pytest.raises(ValueError, match="Unknown provider"):
            client.set_preferred_provider("unknown_provider")


class TestGetCurrentProvider:
    """get_current_provider metódus tesztjei."""

    def test_get_current_provider_initially_none(self) -> None:
        """Kezdetben a current_provider None."""
        client = WeatherClientExtensions()
        assert client.get_current_provider() is None

    def test_get_current_provider_after_request(self) -> None:
        """Sikeres kérés után a current_provider be van állítva."""
        client = WeatherClientExtensions()
        # Mockoljuk a providert és a get_weather_data-t
        with patch.object(client, '_select_provider', return_value='open-meteo'):
            with patch.object(client, '_retry_weather_request', return_value=[{'data_source': 'open-meteo'}]):
                client.get_weather_data(47.4979, 19.0402, "2024-01-01", "2024-01-02")
                assert client.get_current_provider() == "open-meteo"


class TestGetAvailableProviders:
    """get_available_providers metódus tesztjei."""

    def test_get_available_providers_contains_openmeteo(self) -> None:
        """OpenMeteo mindig elérhető (nincs API key szükséges)."""
        client = WeatherClientExtensions()
        available = client.get_available_providers()
        assert "open-meteo" in available

    def test_get_available_providers_excludes_invalid(self) -> None:
        """A nem érvényes providerek nincsenek a listában."""
        client = WeatherClientExtensions()
        available = client.get_available_providers()
        # Meteostat API key nélkül nem elérhető
        assert "meteostat" not in available

    def test_get_available_providers_returns_list(self) -> None:
        """A visszatérési érték lista."""
        client = WeatherClientExtensions()
        available = client.get_available_providers()
        assert isinstance(available, list)


class TestGetProviderStatus:
    """get_provider_status metódus tesztjei."""

    def test_get_provider_status_returns_dict(self) -> None:
        """A visszatérési érték szótár."""
        client = WeatherClientExtensions()
        status = client.get_provider_status()
        assert isinstance(status, dict)

    def test_get_provider_status_contains_all_providers(self) -> None:
        """A státusz tartalmazza az összes providert."""
        client = WeatherClientExtensions()
        status = client.get_provider_status()
        assert "open-meteo" in status
        assert "meteostat" in status

    def test_get_provider_status_has_required_fields(self) -> None:
        """A státusz objektum tartalmazza a kötelező mezőket."""
        client = WeatherClientExtensions()
        status = client.get_provider_status()

        openmeteo_status = status["open-meteo"]
        required_fields = {
            "display_name",
            "available",
            "request_count",
            "usage_count",
            "is_current",
        }
        assert set(openmeteo_status.keys()) == required_fields

    def test_get_provider_status_openmeteo_available(self) -> None:
        """OpenMeteo státusz: available=True."""
        client = WeatherClientExtensions()
        status = client.get_provider_status()
        assert status["open-meteo"]["available"] is True

    def test_get_provider_status_meteostat_unavailable_without_key(self) -> None:
        """Meteostat státusz: available=False API key nélkül."""
        client = WeatherClientExtensions()
        status = client.get_provider_status()
        assert status["meteostat"]["available"] is False

    def test_get_provider_status_request_count_initial_zero(self) -> None:
        """Kezdeti request_count 0."""
        client = WeatherClientExtensions()
        status = client.get_provider_status()
        assert status["open-meteo"]["request_count"] == 0

    def test_get_provider_status_usage_count_initial_zero(self) -> None:
        """Kezdeti usage_count 0."""
        client = WeatherClientExtensions()
        status = client.get_provider_status()
        assert status["open-meteo"]["usage_count"] == 0

    def test_get_provider_status_is_current_initially_false(self) -> None:
        """Kezdetben is_current=False."""
        client = WeatherClientExtensions()
        status = client.get_provider_status()
        assert status["open-meteo"]["is_current"] is False

    def test_get_provider_status_display_name_correct(self) -> None:
        """A display_name helyes."""
        client = WeatherClientExtensions()
        status = client.get_provider_status()
        assert status["open-meteo"]["display_name"] == "Open-Meteo API"
        assert status["meteostat"]["display_name"] == "Meteostat API"


class TestResetProviderUsageStats:
    """reset_provider_usage_stats metódus tesztjei."""

    def test_reset_clears_usage_stats(self) -> None:
        """A usage_stats törlődik."""
        client = WeatherClientExtensions()
        client.provider_usage_stats["open-meteo"] = 5
        client.reset_provider_usage_stats()
        assert len(client.provider_usage_stats) == 0

    def test_reset_clears_provider_request_counts(self) -> None:
        """A provider request_count-k nullázódnak."""
        client = WeatherClientExtensions()
        # Először szimulálunk egy kérést, hogy növeljük a countert
        client.providers["open-meteo"]._update_request_tracking()
        assert client.providers["open-meteo"].get_request_count() > 0

        client.reset_provider_usage_stats()
        assert client.providers["open-meteo"].get_request_count() == 0

    def test_reset_works_with_empty_stats(self) -> None:
        """Üres statisztikáknál is működik."""
        client = WeatherClientExtensions()
        client.reset_provider_usage_stats()
        assert len(client.provider_usage_stats) == 0


class TestGetCurrentWeather:
    """get_current_weather metódus tesztjei."""

    def test_get_current_weather_returns_tuple(self) -> None:
        """A visszatérési érték tuple."""
        client = WeatherClientExtensions()
        with patch.object(client, 'get_weather_data', return_value=[{'data_source': 'open-meteo'}]):
            result = client.get_current_weather(47.4979, 19.0402)
            assert isinstance(result, tuple)
            assert len(result) == 2

    def test_get_current_weather_success_returns_data(self) -> None:
        """Sikeres kérésnél adatot ad vissza."""
        client = WeatherClientExtensions()
        mock_data = [
            {
                'date': '2024-01-01',
                'temperature_2m_max': 5.0,
                'data_source': 'open-meteo',
            }
        ]
        with patch.object(client, 'get_weather_data', return_value=mock_data):
            weather, source = client.get_current_weather(47.4979, 19.0402)
            assert weather is not None
            assert weather == mock_data[0]
            assert source == 'open-meteo'

    def test_get_current_weather_empty_data_returns_none(self) -> None:
        """Üres adatnál (None, "no_data") tuple."""
        client = WeatherClientExtensions()
        with patch.object(client, 'get_weather_data', return_value=[]):
            weather, source = client.get_current_weather(47.4979, 19.0402)
            assert weather is None
            assert source == "no_data"

    def test_get_current_weather_error_returns_error_status(self) -> None:
        """Kivételnél (None, "error") tuple."""
        client = WeatherClientExtensions()
        with patch.object(client, 'get_weather_data', side_effect=Exception("API error")):
            weather, source = client.get_current_weather(47.4979, 19.0402)
            assert weather is None
            assert source == "error"

    def test_get_current_weather_passes_coordinates(self) -> None:
        """A koordináták helyesen átmennek."""
        client = WeatherClientExtensions()
        with patch.object(client, 'get_weather_data') as mock_get:
            mock_get.return_value = [{'data_source': 'open-meteo'}]
            client.get_current_weather(47.4979, 19.0402)

            call_args = mock_get.call_args
            assert call_args[0][0] == 47.4979
            assert call_args[0][1] == 19.0402

    def test_get_current_weather_uses_today_date(self) -> None:
        """A mai dátumot használja."""
        client = WeatherClientExtensions()
        with patch.object(client, 'get_weather_data') as mock_get:
            mock_get.return_value = [{'data_source': 'open-meteo'}]
            client.get_current_weather(47.4979, 19.0402)

            call_args = mock_get.call_args
            # A start_date és end_date megegyezik (mai nap)
            start_date = call_args[0][2]
            end_date = call_args[0][3]
            assert start_date == end_date

    def test_get_current_weather_with_provider_override(self) -> None:
        """Provider override átadása."""
        client = WeatherClientExtensions()
        with patch.object(client, 'get_weather_data') as mock_get:
            mock_get.return_value = [{'data_source': 'open-meteo'}]
            client.get_current_weather(47.4979, 19.0402, user_override_provider="open-meteo")

            # A user_override_provider az 5. pozicionális paraméter
            assert mock_get.call_args.args[4] == "open-meteo"


class TestGetWeatherForDateRange:
    """get_weather_for_date_range metódus tesztjei."""

    def test_get_weather_for_date_range_returns_tuple(self) -> None:
        """A visszatérési érték tuple."""
        client = WeatherClientExtensions()
        with patch.object(client, 'get_weather_data', return_value=[{'data_source': 'open-meteo'}]):
            result = client.get_weather_for_date_range(47.4979, 19.0402)
            assert isinstance(result, tuple)
            assert len(result) == 2

    def test_get_weather_for_date_range_default_7_days(self) -> None:
        """Alapértelmezetten 7 napot kér le."""
        client = WeatherClientExtensions()
        with patch.object(client, 'get_weather_data') as mock_get:
            mock_get.return_value = [{'data_source': 'open-meteo'}]
            client.get_weather_for_date_range(47.4979, 19.0402)

            # Ellenőrizzük, hogy a dátumtartomány 7 nap (ma és az elmúlt 6 nap)
            call_args = mock_get.call_args
            start_date_str = call_args[0][2]
            end_date_str = call_args[0][3]

            from datetime import datetime
            start_dt = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_dt = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            # 7 nap = 7 nap különbség (end_date - start_date)
            assert (end_dt - start_dt).days == 7

    def test_get_weather_for_date_range_custom_days(self) -> None:
        """Egyedi nap szám megadása."""
        client = WeatherClientExtensions()
        with patch.object(client, 'get_weather_data') as mock_get:
            mock_get.return_value = [{'data_source': 'open-meteo'}]
            client.get_weather_for_date_range(47.4979, 19.0402, days_back=30)

            call_args = mock_get.call_args
            start_date_str = call_args[0][2]
            end_date_str = call_args[0][3]

            from datetime import datetime
            start_dt = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_dt = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            # 30 nap = 30 nap különbség (end_date - start_date)
            assert (end_dt - start_dt).days == 30

    def test_get_weather_for_date_range_success_returns_data(self) -> None:
        """Sikeres kérésnél adatot ad vissza."""
        client = WeatherClientExtensions()
        mock_data = [
            {'date': '2024-01-01', 'data_source': 'open-meteo'},
            {'date': '2024-01-02', 'data_source': 'open-meteo'},
        ]
        with patch.object(client, 'get_weather_data', return_value=mock_data):
            weather, source = client.get_weather_for_date_range(47.4979, 19.0402)
            assert weather == mock_data
            assert source == 'open-meteo'

    def test_get_weather_for_date_range_empty_returns_no_data(self) -> None:
        """Üres adatnál 'no_data' source."""
        client = WeatherClientExtensions()
        with patch.object(client, 'get_weather_data', return_value=[]):
            weather, source = client.get_weather_for_date_range(47.4979, 19.0402)
            assert weather == []
            assert source == 'no_data'

    def test_get_weather_for_date_range_passes_coordinates(self) -> None:
        """A koordináták helyesen átmennek."""
        client = WeatherClientExtensions()
        with patch.object(client, 'get_weather_data') as mock_get:
            mock_get.return_value = [{'data_source': 'open-meteo'}]
            client.get_weather_for_date_range(47.4979, 19.0402)

            call_args = mock_get.call_args
            assert call_args[0][0] == 47.4979
            assert call_args[0][1] == 19.0402

    def test_get_weather_for_date_range_with_provider_override(self) -> None:
        """Provider override átadása."""
        client = WeatherClientExtensions()
        with patch.object(client, 'get_weather_data') as mock_get:
            mock_get.return_value = [{'data_source': 'open-meteo'}]
            client.get_weather_for_date_range(47.4979, 19.0402, user_override_provider="open-meteo")

            # A user_override_provider az 5. pozicionális paraméter
            assert mock_get.call_args.args[4] == "open-meteo"


class TestInheritance:
    """Öröklődés tesztek."""

    def test_inherits_from_weather_client(self) -> None:
        """A WeatherClientExtensions a WeatherClient-ből származik."""
        from src.data.weather_client_core import WeatherClient
        assert issubclass(WeatherClientExtensions, WeatherClient)

    def test_has_core_methods(self) -> None:
        """Rendelkezik az ősi osztály metódusaival."""
        client = WeatherClientExtensions()
        assert hasattr(client, 'get_weather_data')
        assert hasattr(client, '_validate_inputs')
        assert hasattr(client, '_select_provider')
        assert hasattr(client, '_get_provider_fallback_chain')

    def test_initialization_same_as_core(self) -> None:
        """Az inicializáció megegyezik az ősi osztályéval."""
        client = WeatherClientExtensions(preferred_provider="auto")
        assert client.preferred_provider == "auto"
        assert hasattr(client, 'providers')
        assert hasattr(client, 'provider_usage_stats')
