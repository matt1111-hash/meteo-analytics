#!/usr/bin/env python3
"""Clean Architecture compliance tests using AST analysis."""

from pathlib import Path

import pytest

from tests.integration.clean_architecture_support import (
    TestCleanArchitectureCompliance,
    get_all_python_files,
    get_imports_from_file,
)


class TestDomainLayerBoundaries(TestCleanArchitectureCompliance):
    """Tests for domain layer dependency boundaries."""

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
            "Domain layer should not import from data layer:\n"
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
            "Domain layer should not import from infrastructure layer:\n"
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
            "Domain layer should not import from presentation layer:\n"
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
            "Domain layer should not import from application layer:\n"
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
            "Domain layer should not import from api layer:\n"
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
            "Domain layer should not import from analytics layer:\n"
            + "\n".join(f"  {f}: {i}" for f, i in violations)
        )
