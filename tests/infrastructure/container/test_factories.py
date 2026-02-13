#!/usr/bin/env python3
"""Tests for infrastructure container factory functions."""

import pytest

from src.infrastructure.container import (
    get_anomaly_profile_port,
    get_city_manager_port,
    get_city_repository_port,
    get_weather_client_port,
)
from src.infrastructure.container.factories import (
    get_city_repository_port as get_city_repo_port_direct,
)


class TestContainerFactories:
    """Tests for container factory functions."""

    def test_get_city_manager_port_returns_port(self):
        """Test that get_city_manager_port returns a valid port implementation."""
        port = get_city_manager_port()

        # Should have required methods from CityManagerPort protocol
        assert hasattr(port, "find_city_by_name")
        assert hasattr(port, "search_cities")
        # Note: actual method names may vary - just check it's not None
        assert port is not None

    def test_get_weather_client_port_returns_port(self):
        """Test that get_weather_client_port returns a valid port implementation."""
        port = get_weather_client_port()

        # Should have required methods from WeatherClientPort protocol
        assert hasattr(port, "get_weather_data")
        assert port is not None

    def test_get_city_repository_port_returns_port(self):
        """Test that get_city_repository_port returns a valid port implementation."""
        port = get_city_repository_port()

        # Should have required attributes from CityRepositoryPort protocol
        assert hasattr(port, "db_path")
        assert port is not None

    def test_get_city_repository_port_with_custom_paths(self, tmp_path):
        """Test get_city_repository_port with custom database paths."""
        # Create dummy database files
        db_path = tmp_path / "cities.db"
        hungarian_db_path = tmp_path / "hungarian_settlements.db"
        db_path.touch()
        hungarian_db_path.touch()

        port = get_city_repo_port_direct(db_path=db_path, hungarian_db_path=hungarian_db_path)

        assert str(port.db_path) == str(db_path)
        assert str(port.hungarian_db_path) == str(hungarian_db_path)

    def test_get_anomaly_profile_port_returns_port(self):
        """Test that get_anomaly_profile_port returns a valid port implementation."""
        port = get_anomaly_profile_port()

        # Should have required methods from AnomalyProfilePort protocol
        assert hasattr(port, "get_active_profile")
        assert port is not None

    def test_factories_are_importable_from_container(self):
        """Test that all factories are importable from the container package."""
        from src.infrastructure.container import (
            get_anomaly_profile_port,
            get_city_manager_port,
            get_city_repository_port,
            get_weather_client_port,
        )

        # Just check they are callable
        assert callable(get_city_manager_port)
        assert callable(get_weather_client_port)
        assert callable(get_city_repository_port)
        assert callable(get_anomaly_profile_port)

    def test_factories_not_in_domain_ports(self):
        """Test that factory functions are NOT exported from domain.ports."""
        import src.domain.ports as ports_module

        # These should NOT be in domain.ports anymore
        assert not hasattr(ports_module, "get_city_manager_port")
        assert not hasattr(ports_module, "get_weather_client_port")
        assert not hasattr(ports_module, "get_city_repository_port")
        assert not hasattr(ports_module, "get_anomaly_profile_port")
