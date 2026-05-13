"""Weather data types and exceptions tests."""

from __future__ import annotations

from src.infrastructure.weather.weather_types import WeatherData


class TestWeatherData:
    """Tests for WeatherData dataclass."""

    def test_create_weather_data_with_required_fields(self) -> None:
        data = WeatherData(date="2024-01-01")
        assert data.date == "2024-01-01"
        assert data.temperature_2m_max is None
        assert data.temperature_2m_min is None

    def test_create_weather_data_with_all_fields(self) -> None:
        data = WeatherData(
            date="2024-01-01",
            temperature_2m_max=25.0,
            temperature_2m_min=15.0,
            temperature_2m_mean=20.0,
            apparent_temperature_max=27.0,
            apparent_temperature_min=14.0,
            precipitation_sum=5.0,
            rain_sum=3.0,
            snowfall_sum=2.0,
            precipitation_hours=6,
            windspeed_10m_max=30.0,
            wind_gusts_10m_max=50.0,
            winddirection_10m_dominant=180.0,
            shortwave_radiation_sum=15000.0,
            sunshine_duration=8.0,
            uv_index_max=7.0,
            uv_index_clear_sky_max=9.0,
            data_source="open-meteo",
        )
        assert data.date == "2024-01-01"
        assert data.temperature_2m_max == 25.0
        assert data.precipitation_sum == 5.0
        assert data.data_source == "open-meteo"

    def test_post_init_calculates_temperature_range(self) -> None:
        data = WeatherData(date="2024-01-01", temperature_2m_max=25.0, temperature_2m_min=15.0)
        assert data.temperature_range == 10.0

    def test_post_init_calculates_mean_temperature(self) -> None:
        data = WeatherData(date="2024-01-01", temperature_2m_max=25.0, temperature_2m_min=15.0)
        assert data.temperature_2m_mean == 20.0

    def test_post_init_preserves_existing_mean_temperature(self) -> None:
        data = WeatherData(
            date="2024-01-01",
            temperature_2m_max=25.0,
            temperature_2m_min=15.0,
            temperature_2m_mean=18.0,
        )
        assert data.temperature_2m_mean == 18.0

    def test_temperature_range_none_when_min_or_max_missing(self) -> None:
        data = WeatherData(date="2024-01-01", temperature_2m_max=25.0)
        assert data.temperature_range is None
        data = WeatherData(date="2024-01-01", temperature_2m_min=15.0)
        assert data.temperature_range is None
        data = WeatherData(date="2024-01-01")
        assert data.temperature_range is None

    def test_temperature_mean_none_when_min_or_max_missing(self) -> None:
        data = WeatherData(date="2024-01-01", temperature_2m_max=25.0)
        assert data.temperature_2m_mean is None
        data = WeatherData(date="2024-01-01", temperature_2m_min=15.0)
        assert data.temperature_2m_mean is None

    def test_negative_temperatures(self) -> None:
        data = WeatherData(date="2024-01-01", temperature_2m_max=-5.0, temperature_2m_min=-15.0)
        assert data.temperature_range == 10.0
        assert data.temperature_2m_mean == -10.0

    def test_zero_temperature_values(self) -> None:
        data = WeatherData(date="2024-01-01", temperature_2m_max=0.0, temperature_2m_min=-10.0)
        assert data.temperature_range == 10.0
        assert data.temperature_2m_mean == -5.0

    def test_precipitation_fields(self) -> None:
        data = WeatherData(
            date="2024-01-01",
            precipitation_sum=10.5,
            rain_sum=8.0,
            snowfall_sum=2.5,
            precipitation_hours=12,
        )
        assert data.precipitation_sum == 10.5
        assert data.rain_sum == 8.0
        assert data.snowfall_sum == 2.5
        assert data.precipitation_hours == 12

    def test_wind_fields(self) -> None:
        data = WeatherData(
            date="2024-01-01",
            windspeed_10m_max=35.5,
            wind_gusts_10m_max=55.0,
            winddirection_10m_dominant=225.0,
        )
        assert data.windspeed_10m_max == 35.5
        assert data.wind_gusts_10m_max == 55.0
        assert data.winddirection_10m_dominant == 225.0

    def test_radiation_fields(self) -> None:
        data = WeatherData(
            date="2024-01-01",
            shortwave_radiation_sum=18000.0,
            sunshine_duration=10.5,
            uv_index_max=8.0,
            uv_index_clear_sky_max=10.0,
        )
        assert data.shortwave_radiation_sum == 18000.0
        assert data.sunshine_duration == 10.5
        assert data.uv_index_max == 8.0
        assert data.uv_index_clear_sky_max == 10.0

    def test_data_source_field(self) -> None:
        data = WeatherData(date="2024-01-01", data_source="meteostat")
        assert data.data_source == "meteostat"
        data = WeatherData(date="2024-01-01", data_source="open-meteo")
        assert data.data_source == "open-meteo"
