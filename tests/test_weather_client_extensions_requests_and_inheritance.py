"""WeatherClientExtensions tesztjei."""

from __future__ import annotations

from unittest.mock import patch

from src.data.weather_client_extensions import WeatherClientExtensions


class TestGetCurrentWeather:
    """get_current_weather metódus tesztjei."""

    def test_get_current_weather_returns_tuple(self) -> None:
        client = WeatherClientExtensions()
        with patch.object(client, "get_weather_data", return_value=[{"data_source": "open-meteo"}]):
            result = client.get_current_weather(47.4979, 19.0402)
            assert isinstance(result, tuple)
            assert len(result) == 2

    def test_get_current_weather_success_returns_data(self) -> None:
        client = WeatherClientExtensions()
        mock_data = [
            {
                "date": "2024-01-01",
                "temperature_2m_max": 5.0,
                "data_source": "open-meteo",
            }
        ]
        with patch.object(client, "get_weather_data", return_value=mock_data):
            weather, source = client.get_current_weather(47.4979, 19.0402)
            assert weather is not None
            assert weather == mock_data[0]
            assert source == "open-meteo"

    def test_get_current_weather_empty_data_returns_none(self) -> None:
        client = WeatherClientExtensions()
        with patch.object(client, "get_weather_data", return_value=[]):
            weather, source = client.get_current_weather(47.4979, 19.0402)
            assert weather is None
            assert source == "no_data"

    def test_get_current_weather_error_returns_error_status(self) -> None:
        client = WeatherClientExtensions()
        with patch.object(client, "get_weather_data", side_effect=Exception("API error")):
            weather, source = client.get_current_weather(47.4979, 19.0402)
            assert weather is None
            assert source == "error"

    def test_get_current_weather_passes_coordinates(self) -> None:
        client = WeatherClientExtensions()
        with patch.object(client, "get_weather_data") as mock_get:
            mock_get.return_value = [{"data_source": "open-meteo"}]
            client.get_current_weather(47.4979, 19.0402)
            call_args = mock_get.call_args
            assert call_args[0][0] == 47.4979
            assert call_args[0][1] == 19.0402

    def test_get_current_weather_uses_today_date(self) -> None:
        client = WeatherClientExtensions()
        with patch.object(client, "get_weather_data") as mock_get:
            mock_get.return_value = [{"data_source": "open-meteo"}]
            client.get_current_weather(47.4979, 19.0402)
            call_args = mock_get.call_args
            start_date = call_args[0][2]
            end_date = call_args[0][3]
            assert start_date == end_date

    def test_get_current_weather_with_provider_override(self) -> None:
        client = WeatherClientExtensions()
        with patch.object(client, "get_weather_data") as mock_get:
            mock_get.return_value = [{"data_source": "open-meteo"}]
            client.get_current_weather(47.4979, 19.0402, user_override_provider="open-meteo")
            assert mock_get.call_args.args[4] == "open-meteo"


class TestGetWeatherForDateRange:
    """get_weather_for_date_range metódus tesztjei."""

    def test_get_weather_for_date_range_returns_tuple(self) -> None:
        client = WeatherClientExtensions()
        with patch.object(client, "get_weather_data", return_value=[{"data_source": "open-meteo"}]):
            result = client.get_weather_for_date_range(47.4979, 19.0402)
            assert isinstance(result, tuple)
            assert len(result) == 2

    def test_get_weather_for_date_range_default_7_days(self) -> None:
        client = WeatherClientExtensions()
        with patch.object(client, "get_weather_data") as mock_get:
            mock_get.return_value = [{"data_source": "open-meteo"}]
            client.get_weather_for_date_range(47.4979, 19.0402)
            call_args = mock_get.call_args
            start_date_str = call_args[0][2]
            end_date_str = call_args[0][3]
            from datetime import datetime

            start_dt = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_dt = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            assert (end_dt - start_dt).days == 7

    def test_get_weather_for_date_range_custom_days(self) -> None:
        client = WeatherClientExtensions()
        with patch.object(client, "get_weather_data") as mock_get:
            mock_get.return_value = [{"data_source": "open-meteo"}]
            client.get_weather_for_date_range(47.4979, 19.0402, days_back=30)
            call_args = mock_get.call_args
            start_date_str = call_args[0][2]
            end_date_str = call_args[0][3]
            from datetime import datetime

            start_dt = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_dt = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            assert (end_dt - start_dt).days == 30

    def test_get_weather_for_date_range_success_returns_data(self) -> None:
        client = WeatherClientExtensions()
        mock_data = [
            {"date": "2024-01-01", "data_source": "open-meteo"},
            {"date": "2024-01-02", "data_source": "open-meteo"},
        ]
        with patch.object(client, "get_weather_data", return_value=mock_data):
            weather, source = client.get_weather_for_date_range(47.4979, 19.0402)
            assert weather == mock_data
            assert source == "open-meteo"

    def test_get_weather_for_date_range_empty_returns_no_data(self) -> None:
        client = WeatherClientExtensions()
        with patch.object(client, "get_weather_data", return_value=[]):
            weather, source = client.get_weather_for_date_range(47.4979, 19.0402)
            assert weather == []
            assert source == "no_data"

    def test_get_weather_for_date_range_passes_coordinates(self) -> None:
        client = WeatherClientExtensions()
        with patch.object(client, "get_weather_data") as mock_get:
            mock_get.return_value = [{"data_source": "open-meteo"}]
            client.get_weather_for_date_range(47.4979, 19.0402)
            call_args = mock_get.call_args
            assert call_args[0][0] == 47.4979
            assert call_args[0][1] == 19.0402

    def test_get_weather_for_date_range_with_provider_override(self) -> None:
        client = WeatherClientExtensions()
        with patch.object(client, "get_weather_data") as mock_get:
            mock_get.return_value = [{"data_source": "open-meteo"}]
            client.get_weather_for_date_range(47.4979, 19.0402, user_override_provider="open-meteo")
            assert mock_get.call_args.args[4] == "open-meteo"


class TestInheritance:
    """Öröklődés tesztek."""

    def test_inherits_from_weather_client(self) -> None:
        from src.data.weather_client_core import WeatherClient

        assert issubclass(WeatherClientExtensions, WeatherClient)

    def test_has_core_methods(self) -> None:
        client = WeatherClientExtensions()
        assert hasattr(client, "get_weather_data")
        assert hasattr(client, "_validate_inputs")
        assert hasattr(client, "_select_provider")
        assert hasattr(client, "_get_provider_fallback_chain")

    def test_initialization_same_as_core(self) -> None:
        client = WeatherClientExtensions(preferred_provider="auto")
        assert client.preferred_provider == "auto"
        assert hasattr(client, "providers")
        assert hasattr(client, "provider_usage_stats")
