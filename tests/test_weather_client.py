"""WeatherClient infrastructure module tests."""

from __future__ import annotations

from src.infrastructure.weather import (
    meteostat_provider,
    openmeteo_provider,
    weather_client_core,
    weather_client_extensions,
    weather_provider_base,
    weather_types,
)


class TestProviderInstantiation:
    """Provider peldanyositasi tesztek."""

    def test_openmeteo_provider_initialization(self) -> None:
        """OpenMeteoProvider helyesen inicializal."""
        provider = openmeteo_provider.OpenMeteoProvider()
        assert provider.provider_id == "open-meteo"
        assert provider.display_name == "Open-Meteo API"
        assert provider.validate_provider() is True

    def test_meteostat_provider_initialization(self) -> None:
        """MeteostatProvider helyesen inicializal (API key nelkul)."""
        provider = meteostat_provider.MeteostatProvider()
        assert provider.provider_id == "meteostat"
        assert provider.display_name == "Meteostat API"
        assert provider.validate_provider() is False

    def test_weather_client_has_providers_dict(self) -> None:
        """A WeatherClient rendelkezik providers szotarral."""
        client = weather_client_extensions.WeatherClientExtensions()
        assert hasattr(client, "providers")
        assert isinstance(client.providers, dict)
        assert "open-meteo" in client.providers
        assert "meteostat" in client.providers

    def test_providers_are_instantiable(self) -> None:
        """A provider osztalyok peldanyosithatoak."""
        openmeteo = openmeteo_provider.OpenMeteoProvider()
        assert openmeteo is not None
        assert openmeteo.provider_id == "open-meteo"

        meteostat = meteostat_provider.MeteostatProvider()
        assert meteostat is not None
        assert meteostat.provider_id == "meteostat"


class TestTypeAnnotations:
    """Tipusannotacio tesztek."""

    def test_weather_data_has_annotations(self) -> None:
        """A WeatherData rendelkezik tipusannotaciokkal."""
        assert hasattr(weather_types.WeatherData, "__annotations__")
        annotations = weather_types.WeatherData.__annotations__
        assert len(annotations) > 0

    def test_weather_client_core_annotations(self) -> None:
        """A WeatherClientCore rendelkezik metodusokkal."""
        assert hasattr(weather_client_core.WeatherClient, "__init__")
        assert hasattr(weather_client_core.WeatherClient, "get_weather_data")
        assert hasattr(weather_client_core.WeatherClient, "_validate_inputs")

    def test_weather_client_extensions_annotations(self) -> None:
        """A WeatherClientExtensions rendelkezik kiterjesztett metodusokkal."""
        assert hasattr(weather_client_extensions.WeatherClientExtensions, "set_preferred_provider")
        assert hasattr(weather_client_extensions.WeatherClientExtensions, "get_current_provider")
        assert hasattr(weather_client_extensions.WeatherClientExtensions, "get_available_providers")

    def test_weather_data_is_dataclass(self) -> None:
        """A WeatherData dataclass rendelkezik a szukseges mezokkel."""
        assert hasattr(weather_types.WeatherData, "__dataclass_fields__")

        fields = weather_types.WeatherData.__dataclass_fields__
        expected_fields = {
            "date",
            "temperature_2m_max",
            "temperature_2m_min",
            "data_source",
        }
        assert expected_fields.issubset(set(fields.keys()))

    def test_exceptions_inherit_correctly(self) -> None:
        """A kivetel osztalyok a helyes alaposztalybol szarmaznak."""
        assert issubclass(weather_types.WeatherAPIError, Exception)
        assert issubclass(weather_types.ProviderNotAvailableError, Exception)
        assert issubclass(weather_types.ProviderValidationError, Exception)

    def test_provider_classes_inherit_from_base(self) -> None:
        """A provider osztalyok a WeatherProvider-bol szarmaznak."""
        assert issubclass(
            openmeteo_provider.OpenMeteoProvider, weather_provider_base.WeatherProvider
        )
        assert issubclass(
            meteostat_provider.MeteostatProvider, weather_provider_base.WeatherProvider
        )
