#!/usr/bin/env python3
"""Clean Architecture compliance tests using AST analysis."""

from pathlib import Path

import pytest

from tests.integration.clean_architecture_support import (
    TestCleanArchitectureCompliance,
    get_all_python_files,
    get_imports_from_file,
)


class TestPresentationAndStructure(TestCleanArchitectureCompliance):
    """Tests for presentation layer and structural Clean Architecture rules."""

    def test_presentation_does_not_import_data_layer(self, src_path: Path):
        """Presentation layer must not import from data layer."""
        presentation_path = src_path / "presentation"
        if not presentation_path.exists():
            pytest.skip("Presentation directory not found")

        violations = []
        for py_file in get_all_python_files(presentation_path):
            imports = get_imports_from_file(py_file)
            for imp in imports:
                if imp.startswith("src.data"):
                    violations.append((str(py_file.relative_to(src_path)), imp))

        assert not violations, (
            "Presentation layer should not import from data layer:\n"
            + "\n".join(f"  {f}: {i}" for f, i in violations)
        )

    def test_presentation_does_not_import_infrastructure_layer(self, src_path: Path):
        """Presentation layer must not import from infrastructure layer except container."""
        presentation_path = src_path / "presentation"
        if not presentation_path.exists():
            pytest.skip("Presentation directory not found")

        violations = []
        for py_file in get_all_python_files(presentation_path):
            imports = get_imports_from_file(py_file)
            for imp in imports:
                if imp.startswith("src.infrastructure") and not imp.startswith(
                    "src.infrastructure.container"
                ):
                    violations.append((str(py_file.relative_to(src_path)), imp))

        assert not violations, (
            "Presentation layer should not import from infrastructure layer (except container):\n"
            + "\n".join(f"  {f}: {i}" for f, i in violations)
        )

    def test_factory_functions_in_correct_location(self, src_path: Path):
        """Factory functions should be in infrastructure.container, not domain.ports."""
        domain_ports_file = src_path / "domain" / "ports" / "__init__.py"

        if not domain_ports_file.exists():
            pytest.skip("domain/ports/__init__.py not found")

        factory_names = [
            "get_city_manager_port",
            "get_weather_client_port",
            "get_city_repository_port",
            "get_anomaly_profile_port",
        ]

        with open(domain_ports_file, "r") as f:
            content = f.read()

        for factory in factory_names:
            assert f"def {factory}" not in content, (
                f"Factory function {factory} should not be defined in domain.ports. "
                f"Use src.infrastructure.container instead."
            )

    def test_infrastructure_container_exists(self, src_path: Path):
        """Infrastructure container should exist with factory functions."""
        container_path = src_path / "infrastructure" / "container"
        factories_file = container_path / "factories.py"
        init_file = container_path / "__init__.py"

        assert container_path.exists(), (
            "infrastructure/container directory should exist"
        )
        assert factories_file.exists(), (
            "infrastructure/container/factories.py should exist"
        )
        assert init_file.exists(), "infrastructure/container/__init__.py should exist"

        imports = get_imports_from_file(init_file)
        assert any("get_city_manager_port" in imp for imp in imports), (
            "get_city_manager_port should be exported from infrastructure.container"
        )

    def test_city_info_value_object_exists(self, src_path: Path):
        """CityInfo value object should exist in domain layer."""
        city_info_file = src_path / "domain" / "value_objects" / "city_info.py"

        assert city_info_file.exists(), (
            "domain/value_objects/city_info.py should exist for Clean Architecture compliance"
        )

    def test_city_adapter_exists(self, src_path: Path):
        """City adapter should exist to convert data.City to domain.CityInfo."""
        adapter_file = src_path / "infrastructure" / "adapters" / "city_adapter.py"

        assert adapter_file.exists(), (
            "infrastructure/adapters/city_adapter.py should exist to convert "
            "data layer City to domain CityInfo"
        )
