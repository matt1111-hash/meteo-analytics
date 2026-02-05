"""Weather data types and exceptions tests."""

from __future__ import annotations

import pytest

from src.data.weather_types import (
    ProviderNotAvailableError,
    ProviderValidationError,
    WeatherAPIError,
    WeatherData,
)


class TestWeatherData:
    """Tests for WeatherData dataclass."""

    def test_create_weather_data_with_required_fields(self) -> None:
        """WeatherData can be created with required date field only."""
        data = WeatherData(date="2024-01-01")
        assert data.date == "2024-01-01"
        assert data.temperature_2m_max is None
        assert data.temperature_2m_min is None

    def test_create_weather_data_with_all_fields(self) -> None:
        """WeatherData can be created with all fields."""
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
        """Temperature range is calculated from max and min."""
        data = WeatherData(
            date="2024-01-01", temperature_2m_max=25.0, temperature_2m_min=15.0
        )
        assert data.temperature_range == 10.0

    def test_post_init_calculates_mean_temperature(self) -> None:
        """Mean temperature is calculated when not provided."""
        data = WeatherData(
            date="2024-01-01", temperature_2m_max=25.0, temperature_2m_min=15.0
        )
        assert data.temperature_2m_mean == 20.0

    def test_post_init_preserves_existing_mean_temperature(self) -> None:
        """Existing mean temperature is not overridden."""
        data = WeatherData(
            date="2024-01-01",
            temperature_2m_max=25.0,
            temperature_2m_min=15.0,
            temperature_2m_mean=18.0,
        )
        assert data.temperature_2m_mean == 18.0

    def test_temperature_range_none_when_min_or_max_missing(self) -> None:
        """Temperature range is None when min or max is missing."""
        # Only max provided
        data = WeatherData(date="2024-01-01", temperature_2m_max=25.0)
        assert data.temperature_range is None

        # Only min provided
        data = WeatherData(date="2024-01-01", temperature_2m_min=15.0)
        assert data.temperature_range is None

        # Neither provided
        data = WeatherData(date="2024-01-01")
        assert data.temperature_range is None

    def test_temperature_mean_none_when_min_or_max_missing(self) -> None:
        """Mean temperature is None when min or max is missing."""
        # Only max provided
        data = WeatherData(date="2024-01-01", temperature_2m_max=25.0)
        assert data.temperature_2m_mean is None

        # Only min provided
        data = WeatherData(date="2024-01-01", temperature_2m_min=15.0)
        assert data.temperature_2m_mean is None

    def test_negative_temperatures(self) -> None:
        """Negative temperatures are handled correctly."""
        data = WeatherData(
            date="2024-01-01", temperature_2m_max=-5.0, temperature_2m_min=-15.0
        )
        assert data.temperature_range == 10.0
        assert data.temperature_2m_mean == -10.0

    def test_zero_temperature_values(self) -> None:
        """Zero temperature values are handled correctly."""
        data = WeatherData(
            date="2024-01-01", temperature_2m_max=0.0, temperature_2m_min=-10.0
        )
        assert data.temperature_range == 10.0
        assert data.temperature_2m_mean == -5.0

    def test_precipitation_fields(self) -> None:
        """Precipitation-related fields can be set."""
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
        """Wind-related fields can be set."""
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
        """Solar radiation fields can be set."""
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
        """Data source can be specified."""
        data = WeatherData(date="2024-01-01", data_source="meteostat")
        assert data.data_source == "meteostat"

        data = WeatherData(date="2024-01-01", data_source="open-meteo")
        assert data.data_source == "open-meteo"


class TestWeatherAPIError:
    """Tests for WeatherAPIError exception."""

    def test_weather_api_error_can_be_raised(self) -> None:
        """WeatherAPIError can be raised and caught."""
        with pytest.raises(WeatherAPIError):
            raise WeatherAPIError("API error occurred")

    def test_weather_api_error_message(self) -> None:
        """WeatherAPIError stores error message."""
        error = WeatherAPIError("Test error message")
        assert str(error) == "Test error message"
        assert error.args == ("Test error message",)


class TestProviderNotAvailableError:
    """Tests for ProviderNotAvailableError exception."""

    def test_provider_not_available_error_is_weather_api_error(self) -> None:
        """ProviderNotAvailableError is a subclass of WeatherAPIError."""
        assert issubclass(ProviderNotAvailableError, WeatherAPIError)

    def test_provider_not_available_error_can_be_raised(self) -> None:
        """ProviderNotAvailableError can be raised and caught."""
        with pytest.raises(ProviderNotAvailableError):
            raise ProviderNotAvailableError("Provider not available")

    def test_provider_not_available_error_caught_as_base(self) -> None:
        """ProviderNotAvailableError can be caught as WeatherAPIError."""
        with pytest.raises(WeatherAPIError):
            raise ProviderNotAvailableError("Provider not available")

    def test_provider_not_available_error_message(self) -> None:
        """ProviderNotAvailableError stores error message."""
        error = ProviderNotAvailableError("OpenMeteo is down")
        assert str(error) == "OpenMeteo is down"


class TestProviderValidationError:
    """Tests for ProviderValidationError exception."""

    def test_provider_validation_error_is_weather_api_error(self) -> None:
        """ProviderValidationError is a subclass of WeatherAPIError."""
        assert issubclass(ProviderValidationError, WeatherAPIError)

    def test_provider_validation_error_can_be_raised(self) -> None:
        """ProviderValidationError can be raised and caught."""
        with pytest.raises(ProviderValidationError):
            raise ProviderValidationError("Invalid API key")

    def test_provider_validation_error_caught_as_base(self) -> None:
        """ProviderValidationError can be caught as WeatherAPIError."""
        with pytest.raises(WeatherAPIError):
            raise ProviderValidationError("Validation failed")

    def test_provider_validation_error_message(self) -> None:
        """ProviderValidationError stores error message."""
        error = ProviderValidationError("Invalid configuration")
        assert str(error) == "Invalid configuration"


class TestExceptionHierarchy:
    """Tests for exception hierarchy."""

    def test_all_exceptions_inherit_from_weather_api_error(self) -> None:
        """All custom exceptions inherit from WeatherAPIError."""
        assert issubclass(ProviderNotAvailableError, WeatherAPIError)
        assert issubclass(ProviderValidationError, WeatherAPIError)

    def test_exception_hierarchy_for_catching(self) -> None:
        """Exceptions can be caught at different levels."""
        # Catch specific exception
        with pytest.raises(ProviderNotAvailableError):
            raise ProviderNotAvailableError("error")

        # Catch as base class
        with pytest.raises(WeatherAPIError) as exc_info:
            raise ProviderNotAvailableError("error")
        assert isinstance(exc_info.value, ProviderNotAvailableError)

        # Catch another specific exception
        with pytest.raises(ProviderValidationError):
            raise ProviderValidationError("error")

        # Catch as base class
        with pytest.raises(WeatherAPIError) as exc_info:
            raise ProviderValidationError("error")
        assert isinstance(exc_info.value, ProviderValidationError)
