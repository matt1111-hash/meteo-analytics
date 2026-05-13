"""Weather data types and exceptions tests."""

from __future__ import annotations

import pytest
from src.infrastructure.weather.weather_types import (
    ProviderNotAvailableError,
    ProviderValidationError,
    WeatherAPIError,
)


class TestWeatherAPIError:
    """Tests for WeatherAPIError exception."""

    def test_weather_api_error_can_be_raised(self) -> None:
        with pytest.raises(WeatherAPIError):
            raise WeatherAPIError("API error occurred")

    def test_weather_api_error_message(self) -> None:
        error = WeatherAPIError("Test error message")
        assert str(error) == "Test error message"
        assert error.args == ("Test error message",)


class TestProviderNotAvailableError:
    """Tests for ProviderNotAvailableError exception."""

    def test_provider_not_available_error_is_weather_api_error(self) -> None:
        assert issubclass(ProviderNotAvailableError, WeatherAPIError)

    def test_provider_not_available_error_can_be_raised(self) -> None:
        with pytest.raises(ProviderNotAvailableError):
            raise ProviderNotAvailableError("Provider not available")

    def test_provider_not_available_error_caught_as_base(self) -> None:
        with pytest.raises(WeatherAPIError):
            raise ProviderNotAvailableError("Provider not available")

    def test_provider_not_available_error_message(self) -> None:
        error = ProviderNotAvailableError("OpenMeteo is down")
        assert str(error) == "OpenMeteo is down"


class TestProviderValidationError:
    """Tests for ProviderValidationError exception."""

    def test_provider_validation_error_is_weather_api_error(self) -> None:
        assert issubclass(ProviderValidationError, WeatherAPIError)

    def test_provider_validation_error_can_be_raised(self) -> None:
        with pytest.raises(ProviderValidationError):
            raise ProviderValidationError("Invalid API key")

    def test_provider_validation_error_caught_as_base(self) -> None:
        with pytest.raises(WeatherAPIError):
            raise ProviderValidationError("Validation failed")

    def test_provider_validation_error_message(self) -> None:
        error = ProviderValidationError("Invalid configuration")
        assert str(error) == "Invalid configuration"


class TestExceptionHierarchy:
    """Tests for exception hierarchy."""

    def test_all_exceptions_inherit_from_weather_api_error(self) -> None:
        assert issubclass(ProviderNotAvailableError, WeatherAPIError)
        assert issubclass(ProviderValidationError, WeatherAPIError)

    def test_exception_hierarchy_for_catching(self) -> None:
        with pytest.raises(ProviderNotAvailableError):
            raise ProviderNotAvailableError("error")

        with pytest.raises(WeatherAPIError) as exc_info:
            raise ProviderNotAvailableError("error")
        assert isinstance(exc_info.value, ProviderNotAvailableError)

        with pytest.raises(ProviderValidationError):
            raise ProviderValidationError("error")

        with pytest.raises(WeatherAPIError) as exc_info:
            raise ProviderValidationError("error")
        assert isinstance(exc_info.value, ProviderValidationError)
