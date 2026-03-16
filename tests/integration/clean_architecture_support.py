#!/usr/bin/env python3
"""Clean Architecture compliance tests using AST analysis."""

import ast
import os
from pathlib import Path
from typing import List, Set

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
        pass

    return imports


def get_all_python_files(directory: Path, exclude_dirs: Set[str] = None) -> List[Path]:
    """Get all Python files in a directory, excluding specified directories."""
    if exclude_dirs is None:
        exclude_dirs = {"__pycache__", ".git", "venv", ".venv", "node_modules"}

    python_files = []
    for root, dirs, files in os.walk(directory):
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
