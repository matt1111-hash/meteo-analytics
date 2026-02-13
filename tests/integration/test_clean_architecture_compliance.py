#!/usr/bin/env python3
"""Clean Architecture compliance tests using AST analysis."""

import ast
import os
from pathlib import Path
from typing import Set, List, Tuple

import pytest


def get_imports_from_file(file_path: Path) -> Set[str]:
    """Extract all imports from a Python file using AST."""
    imports = set()

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module)
                    for alias in node.names:
                        imports.add(f"{node.module}.{alias.name}")
    except SyntaxError:
        pass  # Skip files with syntax errors

    return imports


def get_all_python_files(directory: Path, exclude_dirs: Set[str] = None) -> List[Path]:
    """Get all Python files in a directory, excluding specified directories."""
    if exclude_dirs is None:
        exclude_dirs = {"__pycache__", ".git", "venv", ".venv", "node_modules"}

    python_files = []
    for root, dirs, files in os.walk(directory):
        # Filter out excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            if file.endswith(".py"):
                python_files.append(Path(root) / file)

    return python_files


class TestCleanArchitectureCompliance:
    """Tests to verify Clean Architecture rules using AST analysis."""

    @pytest.fixture
    def project_root(self) -> Path:
        """Get project root path."""
        return Path(__file__).parent.parent.parent

    @pytest.fixture
    def src_path(self, project_root: Path) -> Path:
        """Get src directory path."""
        return project_root / "src"

    def test_domain_does_not_import_data_layer(self, src_path: Path):
        """Domain layer must not import from data layer."""
        domain_path = src_path / "domain"
        if not domain_path.exists():
            pytest.skip("Domain directory not found")

        violations = []
        for py_file in get_all_python_files(domain_path):
            imports = get_imports_from_file(py_file)
            for imp in imports:
                if imp.startswith("src.data"):
                    violations.append((str(py_file.relative_to(src_path)), imp))

        assert not violations, (
            f"Domain layer should not import from data layer:\n"
            + "\n".join(f"  {f}: {i}" for f, i in violations)
        )

    def test_domain_does_not_import_infrastructure_layer(self, src_path: Path):
        """Domain layer must not import from infrastructure layer."""
        domain_path = src_path / "domain"
        if not domain_path.exists():
            pytest.skip("Domain directory not found")

        violations = []
        for py_file in get_all_python_files(domain_path):
            imports = get_imports_from_file(py_file)
            for imp in imports:
                if imp.startswith("src.infrastructure"):
                    violations.append((str(py_file.relative_to(src_path)), imp))

        assert not violations, (
            f"Domain layer should not import from infrastructure layer:\n"
            + "\n".join(f"  {f}: {i}" for f, i in violations)
        )

    def test_domain_does_not_import_presentation_layer(self, src_path: Path):
        """Domain layer must not import from presentation layer."""
        domain_path = src_path / "domain"
        if not domain_path.exists():
            pytest.skip("Domain directory not found")

        violations = []
        for py_file in get_all_python_files(domain_path):
            imports = get_imports_from_file(py_file)
            for imp in imports:
                if imp.startswith("src.presentation"):
                    violations.append((str(py_file.relative_to(src_path)), imp))

        assert not violations, (
            f"Domain layer should not import from presentation layer:\n"
            + "\n".join(f"  {f}: {i}" for f, i in violations)
        )

    def test_domain_does_not_import_application_layer(self, src_path: Path):
        """Domain layer must not import from application layer."""
        domain_path = src_path / "domain"
        if not domain_path.exists():
            pytest.skip("Domain directory not found")

        violations = []
        for py_file in get_all_python_files(domain_path):
            imports = get_imports_from_file(py_file)
            for imp in imports:
                if imp.startswith("src.application"):
                    violations.append((str(py_file.relative_to(src_path)), imp))

        assert not violations, (
            f"Domain layer should not import from application layer:\n"
            + "\n".join(f"  {f}: {i}" for f, i in violations)
        )

    def test_domain_does_not_import_api_layer(self, src_path: Path):
        """Domain layer must not import from api layer."""
        domain_path = src_path / "domain"
        if not domain_path.exists():
            pytest.skip("Domain directory not found")

        violations = []
        for py_file in get_all_python_files(domain_path):
            imports = get_imports_from_file(py_file)
            for imp in imports:
                if imp.startswith("src.api"):
                    violations.append((str(py_file.relative_to(src_path)), imp))

        assert not violations, (
            f"Domain layer should not import from api layer:\n"
            + "\n".join(f"  {f}: {i}" for f, i in violations)
        )

    def test_domain_does_not_import_analytics_layer(self, src_path: Path):
        """Domain layer must not import from analytics layer."""
        domain_path = src_path / "domain"
        if not domain_path.exists():
            pytest.skip("Domain directory not found")

        violations = []
        for py_file in get_all_python_files(domain_path):
            imports = get_imports_from_file(py_file)
            for imp in imports:
                if imp.startswith("src.analytics"):
                    violations.append((str(py_file.relative_to(src_path)), imp))

        assert not violations, (
            f"Domain layer should not import from analytics layer:\n"
            + "\n".join(f"  {f}: {i}" for f, i in violations)
        )

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
            f"Presentation layer should not import from data layer:\n"
            + "\n".join(f"  {f}: {i}" for f, i in violations)
        )

    def test_presentation_does_not_import_infrastructure_layer(self, src_path: Path):
        """Presentation layer must not import from infrastructure layer.

        NOTE: Factory functions are allowed from infrastructure.container
        as per Clean Architecture dependency injection pattern.
        """
        presentation_path = src_path / "presentation"
        if not presentation_path.exists():
            pytest.skip("Presentation directory not found")

        violations = []
        for py_file in get_all_python_files(presentation_path):
            imports = get_imports_from_file(py_file)
            for imp in imports:
                # Allow infrastructure.container (dependency injection)
                if imp.startswith("src.infrastructure") and not imp.startswith(
                    "src.infrastructure.container"
                ):
                    violations.append((str(py_file.relative_to(src_path)), imp))

        assert not violations, (
            f"Presentation layer should not import from infrastructure layer "
            f"(except container):\n"
            + "\n".join(f"  {f}: {i}" for f, i in violations)
        )

    def test_factory_functions_in_correct_location(self, src_path: Path):
        """Factory functions should be in infrastructure.container, not domain.ports."""
        domain_ports_file = src_path / "domain" / "ports" / "__init__.py"

        if not domain_ports_file.exists():
            pytest.skip("domain/ports/__init__.py not found")

        # Check that factory functions are NOT in domain.ports
        imports = get_imports_from_file(domain_ports_file)

        # These should NOT be imported/defined in domain.ports
        factory_names = [
            "get_city_manager_port",
            "get_weather_client_port",
            "get_city_repository_port",
            "get_anomaly_profile_port",
        ]

        # Read the file content to check for function definitions
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

        assert container_path.exists(), "infrastructure/container directory should exist"
        assert factories_file.exists(), "infrastructure/container/factories.py should exist"
        assert init_file.exists(), "infrastructure/container/__init__.py should exist"

        # Check that factory functions are exported
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
