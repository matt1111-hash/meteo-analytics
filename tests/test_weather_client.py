"""WeatherClient re-export modul tesztjei."""

from __future__ import annotations

from src.data import (
    meteostat_provider,
    openmeteo_provider,
    weather_client,
    weather_client_core,
    weather_client_extensions,
    weather_provider_base,
)


class TestWeatherClientReexports:
    """Teszteli, hogy a weather_client.py modul helyesen re-exportálja az összes komponenst."""

    def test_reexports_types(self) -> None:
        """A weather_types modul összes típusa elérhető."""
        assert hasattr(weather_client, "WeatherData")
        assert hasattr(weather_client, "WeatherAPIError")
        assert hasattr(weather_client, "ProviderNotAvailableError")
        assert hasattr(weather_client, "ProviderValidationError")

    def test_reexports_base_class(self) -> None:
        """A WeatherProvider base class elérhető."""
        assert hasattr(weather_client, "WeatherProvider")
        assert weather_client.WeatherProvider is weather_provider_base.WeatherProvider

    def test_reexports_providers(self) -> None:
        """A provider osztályok elérhetőek."""
        assert hasattr(weather_client, "OpenMeteoProvider")
        assert hasattr(weather_client, "MeteostatProvider")
        assert weather_client.OpenMeteoProvider is openmeteo_provider.OpenMeteoProvider
        assert weather_client.MeteostatProvider is meteostat_provider.MeteostatProvider

    def test_reexports_main_client(self) -> None:
        """A fő WeatherClient (WeatherClientExtensions) elérhető."""
        assert hasattr(weather_client, "WeatherClient")
        assert weather_client.WeatherClient is weather_client_extensions.WeatherClientExtensions

    def test_reexports_core_client(self) -> None:
        """A WeatherClientCore elérhető külön is."""
        assert hasattr(weather_client, "WeatherClientCore")
        assert weather_client.WeatherClientCore is weather_client_core.WeatherClient

    def test_all_exports_defined(self) -> None:
        """A __all__ lista tartalmazza az összes exportot."""
        expected_all = {
            "WeatherData",
            "WeatherAPIError",
            "ProviderNotAvailableError",
            "ProviderValidationError",
            "WeatherProvider",
            "OpenMeteoProvider",
            "MeteostatProvider",
            "WeatherClient",
            "WeatherClientCore",
        }
        actual_all = set(weather_client.__all__)
        assert actual_all == expected_all

    def test_all_exports_actually_exist(self) -> None:
        """A __all__-ban felsorolt exportok tényleg léteznek."""
        for name in weather_client.__all__:
            assert hasattr(weather_client, name), f"Missing export: {name}"

    def test_types_are_correct_classes(self) -> None:
        """A típusok megfelelő osztályok."""
        assert isinstance(weather_client.WeatherData, type)
        assert isinstance(weather_client.WeatherAPIError, type)
        assert isinstance(weather_client.ProviderNotAvailableError, type)
        assert isinstance(weather_client.ProviderValidationError, type)

    def test_exceptions_inherit_correctly(self) -> None:
        """A kivétel osztályok a helyes alaposztályból származnak."""
        assert issubclass(weather_client.WeatherAPIError, Exception)
        assert issubclass(weather_client.ProviderNotAvailableError, Exception)
        assert issubclass(weather_client.ProviderValidationError, Exception)

    def test_provider_classes_inherit_from_base(self) -> None:
        """A provider osztályok a WeatherProvider-ból származnak."""
        assert issubclass(weather_client.OpenMeteoProvider, weather_provider_base.WeatherProvider)
        assert issubclass(weather_client.MeteostatProvider, weather_provider_base.WeatherProvider)

    def test_weather_client_is_instantiable(self) -> None:
        """A WeatherClient példányosítható."""
        client = weather_client.WeatherClient(preferred_provider="auto")
        assert client is not None
        assert client.preferred_provider == "auto"

    def test_weather_client_core_is_instantiable(self) -> None:
        """A WeatherClientCore példányosítható."""
        client = weather_client.WeatherClientCore(preferred_provider="open-meteo")
        assert client is not None
        assert client.preferred_provider == "open-meteo"

    def test_providers_are_instantiable(self) -> None:
        """A provider osztályok példányosíthatóak."""
        openmeteo = weather_client.OpenMeteoProvider()
        assert openmeteo is not None
        assert openmeteo.provider_id == "open-meteo"

        # Meteostat API key nélkül is példányosítható, de validate_provider() False
        meteostat = weather_client.MeteostatProvider()
        assert meteostat is not None
        assert meteostat.provider_id == "meteostat"

    def test_weather_data_is_dataclass(self) -> None:
        """A WeatherData dataclass rendelkezik a szükséges mezőkkel."""
        assert hasattr(weather_client.WeatherData, "__dataclass_fields__")

        # Néhány kötelező mező létezése
        fields = weather_client.WeatherData.__dataclass_fields__
        expected_fields = {
            "date",
            "temperature_2m_max",
            "temperature_2m_min",
            "data_source",
        }
        assert expected_fields.issubset(set(fields.keys()))

    def test_module_docstring_exists(self) -> None:
        """A modul rendelkezik dokumentációval."""
        assert weather_client.__doc__ is not None
        assert len(weather_client.__doc__) > 0

    def test_module_structure_matches_documentation(self) -> None:
        """A modul dokumentációja alapján ellenőrizzük a struktúrát."""
        doc = weather_client.__doc__
        assert "weather_types.py" in doc
        assert "weather_provider_base.py" in doc
        assert "openmeteo_provider.py" in doc
        assert "meteostat_provider.py" in doc
        assert "weather_client_core.py" in doc
        assert "weather_client_extensions.py" in doc


class TestBackwardCompatibility:
    """Teszteli a visszafelé kompatibilitást."""

    def test_legacy_import_pattern_works(self) -> None:
        """A dokumentációban leírt legacy import működik."""
        # Ez a régi import minta, amit a dokumentáció említ
        from src.data.weather_client import (  # noqa: PLC0415
            WeatherClient,
            WeatherData,
        )

        assert WeatherClient is not None
        assert WeatherData is not None

    def test_recommended_import_pattern_works(self) -> None:
        """A dokumentációban javasolt új import minta működik."""
        from src.data.weather_client_extensions import WeatherClientExtensions  # noqa: PLC0415
        from src.data.weather_types import WeatherData  # noqa: PLC0415

        assert WeatherClientExtensions is not None
        assert WeatherData is not None

    def test_both_imports_reference_same_class(self) -> None:
        """A WeatherClient mindkét import módszerrel ugyanazt az osztályt adja."""
        from src.data.weather_client import WeatherClient as LegacyClient  # noqa: PLC0415
        from src.data.weather_client_extensions import WeatherClientExtensions  # noqa: PLC0415

        assert LegacyClient is WeatherClientExtensions


class TestProviderInstantiation:
    """Provider példányosítási tesztek."""

    def test_openmeteo_provider_initialization(self) -> None:
        """OpenMeteoProvider helyesen inicializál."""
        provider = weather_client.OpenMeteoProvider()
        assert provider.provider_id == "open-meteo"
        assert provider.display_name == "Open-Meteo API"
        assert provider.validate_provider() is True

    def test_meteostat_provider_initialization(self) -> None:
        """MeteostatProvider helyesen inicializál (API key nélkül)."""
        provider = weather_client.MeteostatProvider()
        assert provider.provider_id == "meteostat"
        assert provider.display_name == "Meteostat API"
        # API key nélkül False
        assert provider.validate_provider() is False

    def test_weather_client_has_providers_dict(self) -> None:
        """A WeatherClient rendelkezik providers szótárral."""
        client = weather_client.WeatherClient()
        assert hasattr(client, "providers")
        assert isinstance(client.providers, dict)
        assert "open-meteo" in client.providers
        assert "meteostat" in client.providers


class TestTypeAnnotations:
    """Típusannotáció tesztek."""

    def test_weather_data_has_annotations(self) -> None:
        """A WeatherData rendelkezik típusannotációkkal."""
        assert hasattr(weather_client.WeatherData, "__annotations__")
        annotations = weather_client.WeatherData.__annotations__
        assert len(annotations) > 0

    def test_weather_client_core_annotations(self) -> None:
        """A WeatherClientCore rendelkezik típusannotációkkal vagy metódusokkal."""
        # A WeatherClientCore osztály létezése és működőképessége a fontosabb
        assert hasattr(weather_client.WeatherClientCore, "__init__")
        assert hasattr(weather_client.WeatherClientCore, "get_weather_data")
        assert hasattr(weather_client.WeatherClientCore, "_validate_inputs")

    def test_weather_client_extensions_annotations(self) -> None:
        """A WeatherClientExtensions (WeatherClient) rendelkezik kiterjesztett metódusokkal."""
        # A WeatherClientExtensions WeatherClient-ként van re-exportálva
        assert hasattr(weather_client.WeatherClient, "set_preferred_provider")
        assert hasattr(weather_client.WeatherClient, "get_current_provider")
        assert hasattr(weather_client.WeatherClient, "get_available_providers")
