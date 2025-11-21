#!/usr/bin/env python3
"""
Ultimate Project Analyzer with Clean Architecture Validation
=============================================================
Enhanced version with Layer Violation Detection and Coupling Metrics.

Features:
- AST-based static analysis for .py files.
- Metrics: LOC (Lines of Code), CC (Cyclomatic Complexity).
- Layer Analysis: Detects UI↔ML mixing, threading, and infra usage.
- **NEW**: Clean Architecture layer violation detection
- **NEW**: Robert C. Martin's coupling metrics (Ca, Ce, Instability)
- Hotspot Detection: Finds God Classes, Long/Complex Functions.
- Qt-Specific Analysis: Detects Signal() and .connect() calls.
- Import Graph: Calculates fan-in, fan-out, and detects cycles.

Output Formats (via --format flag):
- `html`: Interactive D3.js report with layer violations.
- `md`:   Human-readable Markdown summary with 6 sections.
- `json`: Detailed JSON dump of all collected data.
- `dot`:  Import graph in Graphviz DOT format (color-coded layers + red violation edges).
- `csv`:  CSV reports for hotspots and Qt signals/slots.
"""
from __future__ import annotations

import argparse
import ast
import csv
import json
import sys
import textwrap
import webbrowser
import dataclasses
import subprocess
from string import Template
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import (
    Any, Dict, List, Set, Tuple, Optional, DefaultDict
)

# ----- Configuration Constants -----
EXCLUDE_DIRS_DEFAULT = {
    "venv", ".venv", ".git", "__pycache__", ".pytest_cache", "analysis_out",
    "build", "dist", ".mypy_cache", ".ruff_cache", ".tox", "deepmap_out",
    "node_modules", ".ipynb_checkpoints"
}

LAYER_RULES = {
    "ui": {"PySide6", "PyQt6", "tkinter"},
    "ml": {"sklearn", "torch", "tensorflow", "keras", "xgboost", "lightgbm"},
    "infra": {"sqlalchemy", "requests", "httpx", "sqlite3", "psycopg2", "redis"},
    "threading": {"threading", "multiprocessing"},
}

GUI_PKGS = LAYER_RULES["ui"]
ML_PKGS = LAYER_RULES["ml"]
THREAD_PKGS = LAYER_RULES["threading"]
QT_THREAD_NAMES = {"QThread", "QRunnable", "QThreadPool"}

# ----- Clean Architecture Dependency Rules -----
# Based on Clean Architecture by Robert C. Martin
# Key principle: Dependencies point INWARD (from outer layers to inner layers)
# Layers (inner → outer): domain → application → infrastructure → gui → entrypoints

ALLOWED_DEPENDENCIES = {
    # Domain layer: Core business logic, NO dependencies on other layers
    "domain": {"domain"},
    
    # Application layer: Use cases, can depend on domain
    "application": {"domain", "application"},
    
    # Infrastructure layer: External services, APIs, persistence
    "infrastructure": {"domain", "application", "infrastructure"},
    
    # GUI layer: Presentation, can use application and infrastructure
    "gui": {"application", "infrastructure", "gui"},
    
    # Entrypoints: Composition root, can depend on everything
    "entrypoints": {"domain", "application", "infrastructure", "gui", "entrypoints"},
    
    # Tests: Can test everything
    "tests": {"domain", "application", "infrastructure", "gui"},
    
    # Unknown/external: Skip validation
    "unknown": set()
}

# Layer colors for DOT graph visualization
LAYER_COLORS = {
    "domain": "#4169E1",        # Blue (stable core)
    "application": "#32CD32",   # Green (orchestration)
    "infrastructure": "#FF6347", # Red (adapters)
    "gui": "#FFD700",           # Gold (presentation)
    "entrypoints": "#9370DB",   # Purple (composition root)
    "tests": "#A9A9A9",         # Gray
    "unknown": "#FFFFFF"        # White
}

# ----- Data Structures -----
@dataclass
class FunctionInfo:
    """Stores metrics for a single function or method."""
    name: str
    lineno: int
    end_lineno: int
    loc: int = 0
    complexity: int = 1
    is_public: bool = True
    is_async: bool = False
    docstring: str = ""

@dataclass
class ClassInfo:
    """Stores metrics for a single class."""
    name: str
    lineno: int
    end_lineno: int
    bases: List[str] = field(default_factory=list)
    methods: Dict[str, FunctionInfo] = field(default_factory=dict)
    qt_signals: List[Dict[str, Any]] = field(default_factory=list)
    loc: int = 0
    complexity: int = 1
    docstring: str = ""

@dataclass
class ModuleInfo:
    """Stores analysis results for a single .py file."""
    path: Path
    module_name: str
    loc: int = 0
    imports_external: Set[str] = field(default_factory=set)
    imports_internal: Set[str] = field(default_factory=set)
    functions: Dict[str, FunctionInfo] = field(default_factory=dict)
    classes: Dict[str, ClassInfo] = field(default_factory=dict)
    qt_signals: List[Dict[str, Any]] = field(default_factory=list)
    qt_connections: List[Dict[str, Any]] = field(default_factory=list)
    uses_threading: bool = False
    is_ui_ml_mixed: bool = False
    docstring: str = ""

@dataclass
class CouplingMetrics:
    """
    Robert C. Martin's Coupling Metrics.
    
    Ca (Afferent Coupling): Number of modules that depend ON this module (incoming)
    Ce (Efferent Coupling): Number of modules this module depends ON (outgoing)
    Instability (I): Ce / (Ca + Ce), range [0, 1]
        - I = 0: Maximally stable (many incoming, no outgoing)
        - I = 1: Maximally unstable (no incoming, many outgoing)
    
    Ideal: Domain = low I (stable), GUI = high I (unstable)
    """
    ca: int  # Afferent (incoming)
    ce: int  # Efferent (outgoing)
    instability: float  # I = Ce / (Ca + Ce)

@dataclass
class AnalysisResult:
    """Top-level container for the entire analysis."""
    root: Path
    modules: Dict[str, ModuleInfo] = field(default_factory=dict)
    graph: Dict[str, Set[str]] = field(default_factory=lambda: defaultdict(set))
    fan_in: DefaultDict[str, int] = field(default_factory=lambda: defaultdict(int))
    fan_out: DefaultDict[str, int] = field(default_factory=lambda: defaultdict(int))
    cycles: List[List[str]] = field(default_factory=list)
    hotspots_loc_cc: List[Tuple[str, Any]] = field(default_factory=list)
    hotspots_god_class: List[ModuleInfo] = field(default_factory=list)
    hotspots_mixed_layer: List[ModuleInfo] = field(default_factory=list)
    hotspots_threading: List[ModuleInfo] = field(default_factory=list)
    external_deps: Counter = field(default_factory=Counter)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # NEW: Layer violations and coupling metrics
    layer_violations: List[Tuple[str, str, str]] = field(default_factory=list)
    coupling_metrics: Dict[str, CouplingMetrics] = field(default_factory=dict)

# ----- AST Parser -----
class AstParser:
    """
    Parses a single Python file using the AST module.
    Extracts metrics, imports, classes, functions, and Qt-specific patterns.
    """
    def __init__(
        self,
        path: Path,
        root: Path,
        internal_module_names: Set[str]
    ):
        self.path: Path = path
        self.root: Path = root
        self.internal_module_names: Set[str] = internal_module_names
        
        self.module_name: str = self._path_to_module(path, root)
        self.source_text: str = ""
        self.source_lines: List[str] = []
        
        self.module_info = ModuleInfo(
            path=path,
            module_name=self.module_name
        )

    @staticmethod
    def _path_to_module(path: Path, root: Path) -> str:
        """Helper: /path/to/src/foo/bar.py -> foo.bar"""
        try:
            rel = path.relative_to(root)
            parts = list(rel.parts)
            if parts[-1].endswith('.py'):
                parts[-1] = parts[-1][:-3]
            if parts[-1] == '__init__':
                parts.pop()
            return '.'.join(parts)
        except ValueError:
            return path.name

    def _get_loc(self, node: ast.AST) -> int:
        """Calculates non-empty, non-comment Lines of Code for a node."""
        # FIX: Module node (file-level) has no lineno attribute
        if isinstance(node, ast.Module):
            if not self.source_lines:
                return 0
            return len([
                line for line in self.source_lines
                if line.strip() and not line.strip().startswith('#')
            ])
        
        # For other nodes (Class, Function) - use lineno
        start = node.lineno
        end = node.end_lineno or start
        if not self.source_lines:
            return end - start + 1
        
        loc = 0
        for i in range(start - 1, min(end, len(self.source_lines))):
            line = self.source_lines[i].strip()
            if line and not line.startswith('#'):
                loc += 1
        return loc

    def _calculate_cc(self, node: ast.AST) -> int:
        """
        Calculates Cyclomatic Complexity for a function or method.
        CC = 1 + number of decision points.
        """
        cc = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                cc += 1
            elif isinstance(child, ast.BoolOp):
                cc += len(child.values) - 1
        return cc

    def parse(self) -> ModuleInfo:
        """Main entry point: Parse the file and return ModuleInfo."""
        try:
            self.source_text = self.path.read_text(encoding='utf-8', errors='ignore')
            self.source_lines = self.source_text.splitlines()
            
            tree = ast.parse(self.source_text, filename=str(self.path))
            self.module_info.docstring = ast.get_docstring(tree) or ""
            self.module_info.loc = self._get_loc(tree)
            
            visitor = _ModuleVisitor(self)
            visitor.visit(tree)
            
            self._detect_layer_mixing()
            
        except SyntaxError as e:
            print(f"   ⚠️  Szintaxis hiba: {self.path.name} ({e})", file=sys.stderr)
        except Exception as e:
            print(f"   ⚠️  Hiba: {self.path.name} ({e})", file=sys.stderr)
        
        return self.module_info

    def _detect_layer_mixing(self) -> None:
        """Checks if the module mixes UI and ML layers."""
        ext_imports = self.module_info.imports_external
        has_ui = bool(ext_imports & GUI_PKGS)
        has_ml = bool(ext_imports & ML_PKGS)
        
        if has_ui and has_ml:
            self.module_info.is_ui_ml_mixed = True

class _ModuleVisitor(ast.NodeVisitor):
    """
    AST visitor that collects:
    - Imports (external and internal)
    - Functions (with LOC and CC)
    - Classes (with methods, LOC, CC)
    - Qt signals and connections
    """
    def __init__(self, parser: AstParser):
        self.parser = parser
        self.current_class: Optional[str] = None

    def visit_Import(self, node: ast.Import):
        """Handle `import foo` - collect FULL module path for internal imports"""
        for alias in node.names:
            full_module_name = alias.name
            root_pkg = full_module_name.split('.')[0]
            
            if root_pkg in self.parser.internal_module_names:
                # Add FULL module path (e.g., "src.domain.services.rsi_calculator")
                self.parser.module_info.imports_internal.add(full_module_name)
            else:
                # For external imports, keep only top-level package
                self.parser.module_info.imports_external.add(root_pkg)
                
                if root_pkg in THREAD_PKGS:
                    self.parser.module_info.uses_threading = True
        
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Handle `from foo import bar` - collect FULL module path for internal imports"""
        
        # Handle relative imports (from . import utils, from ..data import models)
        if node.level > 0:
            # Relative import: calculate absolute path from current module
            current_parts = self.parser.module_name.split(".")
            
            # Go back node.level steps
            if node.level <= len(current_parts):
                base_parts = current_parts[:-node.level]
            else:
                base_parts = []
            
            # Add the module part if exists
            if node.module:
                full_module = ".".join(base_parts + [node.module])
            else:
                full_module = ".".join(base_parts) if base_parts else ""
            
            if full_module:
                root_pkg = full_module.split('.')[0]
                if root_pkg in self.parser.internal_module_names:
                    self.parser.module_info.imports_internal.add(full_module)
                else:
                    self.parser.module_info.imports_external.add(root_pkg)
            
            self.generic_visit(node)
            return
        
        # Absolute imports (from src.domain import ...)
        if not node.module:
            self.generic_visit(node)
            return
        
        base_module = node.module
        root_pkg = base_module.split('.')[0]
        
        if root_pkg in self.parser.internal_module_names:
            # Add the base module path (e.g., "src.domain.services.rsi_calculator")
            self.parser.module_info.imports_internal.add(base_module)
        else:
            # For external imports, keep only top-level package
            self.parser.module_info.imports_external.add(root_pkg)
            
            if root_pkg in THREAD_PKGS:
                self.parser.module_info.uses_threading = True
        
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Extract function/method metrics."""
        func_info = FunctionInfo(
            name=node.name,
            lineno=node.lineno,
            end_lineno=node.end_lineno or node.lineno,
            is_public=not node.name.startswith('_'),
            is_async=False
        )
        
        func_info.loc = self.parser._get_loc(node)
        func_info.complexity = self.parser._calculate_cc(node)
        func_info.docstring = ast.get_docstring(node) or ""
        
        if self.current_class:
            class_info = self.parser.module_info.classes[self.current_class]
            class_info.methods[node.name] = func_info
        else:
            self.parser.module_info.functions[node.name] = func_info
        
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        """Extract async function/method metrics."""
        func_info = FunctionInfo(
            name=node.name,
            lineno=node.lineno,
            end_lineno=node.end_lineno or node.lineno,
            is_public=not node.name.startswith('_'),
            is_async=True
        )
        
        func_info.loc = self.parser._get_loc(node)
        func_info.complexity = self.parser._calculate_cc(node)
        func_info.docstring = ast.get_docstring(node) or ""
        
        if self.current_class:
            class_info = self.parser.module_info.classes[self.current_class]
            class_info.methods[node.name] = func_info
        else:
            self.parser.module_info.functions[node.name] = func_info
        
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef):
        """Extract class metrics and Qt signals."""
        bases = [self._get_base_name(b) for b in node.bases]
        
        class_info = ClassInfo(
            name=node.name,
            lineno=node.lineno,
            end_lineno=node.end_lineno or node.lineno,
            bases=bases
        )
        
        class_info.loc = self.parser._get_loc(node)
        class_info.docstring = ast.get_docstring(node) or ""
        
        self.parser.module_info.classes[node.name] = class_info
        self.current_class = node.name
        
        # Detect Qt signals
        for item in node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        if isinstance(item.value, ast.Call):
                            if self._is_qt_signal(item.value):
                                signal_info = {
                                    "name": target.id,
                                    "class": node.name,
                                    "lineno": item.lineno
                                }
                                class_info.qt_signals.append(signal_info)
                                self.parser.module_info.qt_signals.append(signal_info)
        
        self.generic_visit(node)
        self.current_class = None

    def _get_base_name(self, node: ast.expr) -> str:
        """Extract base class name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return node.attr
        return "Unknown"

    def _is_qt_signal(self, node: ast.Call) -> bool:
        """Check if a Call node is a Qt Signal."""
        if isinstance(node.func, ast.Name):
            return node.func.id == "Signal"
        elif isinstance(node.func, ast.Attribute):
            return node.func.attr == "Signal"
        return False

    def visit_Attribute(self, node: ast.Attribute):
        """Detect .connect() calls for Qt signals."""
        if node.attr == "connect":
            qt_conn_info = {
                "lineno": node.lineno,
                "class": self.current_class or "module-level",
            }
            self.parser.module_info.qt_connections.append(qt_conn_info)
        
        self.generic_visit(node)

# ----- Main Analyzer -----
class ProjectAnalyzer:
    """
    Main orchestrator: Collects all Python files, runs AST parsing,
    builds import graph, detects cycles, and identifies hotspots.
    """
    def __init__(self, root: Path, out_dir: Path, ignore_file: Optional[str] = None):
        self.root = root
        self.out_dir = out_dir
        self.out_dir.mkdir(parents=True, exist_ok=True)
        
        self.exclude_dirs = EXCLUDE_DIRS_DEFAULT.copy()
        if ignore_file and Path(ignore_file).exists():
            with open(ignore_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        self.exclude_dirs.add(line)
        
        self.result = AnalysisResult(root=root)

    def run_analysis(self) -> AnalysisResult:
        """Main analysis pipeline."""
        print(f"🔍 Projekt analízis indul: {self.root}")
        
        py_files = self._collect_py_files()
        print(f"📂 {len(py_files)} Python fájl találva")
        
        internal_modules = self._extract_internal_module_names(py_files)
        
        print("🔬 AST parsing folyamatban...")
        for py_file in py_files:
            parser = AstParser(py_file, self.root, internal_modules)
            module_info = parser.parse()
            self.result.modules[module_info.module_name] = module_info
        
        print("🕸️  Import gráf építése...")
        self._build_import_graph()
        
        print("🔄 Ciklus detektálás...")
        self._detect_cycles()
        
        print("🔥 Hotspot keresés...")
        self._detect_hotspots()
        
        print("🏛️  Clean Architecture ellenőrzés...")
        self._detect_layer_violations()
        
        print("📊 Coupling metrikák számítása...")
        self._calculate_coupling_metrics()
        
        # Debug info
        total_edges = sum(len(deps) for deps in self.result.graph.values())
        unknown_count = sum(1 for m in self.result.modules.keys() if self._get_layer(m) == "unknown")
        
        print(f"✅ Analízis kész!")
        print(f"   📊 {len(self.result.modules)} modul, {total_edges} függőség")
        print(f"   🚨 {len(self.result.layer_violations)} layer violation")
        if unknown_count > 0:
            print(f"   ⚠️  {unknown_count} modul 'unknown' layer-ben (nem ellenőrizve)")
        
        return self.result

    def _collect_py_files(self) -> List[Path]:
        """Recursively collect all .py files, excluding specified directories."""
        py_files = []
        for path in self.root.rglob("*.py"):
            if any(excl in path.parts for excl in self.exclude_dirs):
                continue
            py_files.append(path)
        return py_files

    def _extract_internal_module_names(self, py_files: List[Path]) -> Set[str]:
        """Extract top-level package names from collected files."""
        internal = set()
        for py_file in py_files:
            try:
                rel = py_file.relative_to(self.root)
                if rel.parts:
                    internal.add(rel.parts[0].replace('.py', ''))
            except ValueError:
                pass
        return internal

    def _build_import_graph(self) -> None:
        """Build directed import graph and calculate fan-in/fan-out."""
        for module_name, module_info in self.result.modules.items():
            # Internal imports
            for imp in module_info.imports_internal:
                if imp in self.result.modules:
                    self.result.graph[module_name].add(imp)
                    self.result.fan_out[module_name] += 1
                    self.result.fan_in[imp] += 1
            
            # External dependencies
            for ext in module_info.imports_external:
                self.result.external_deps[ext] += 1

    def _detect_cycles(self) -> None:
        """Detect circular dependencies using DFS."""
        visited = set()
        rec_stack = set()
        
        def dfs(node: str, path: List[str]) -> None:
            if node in rec_stack:
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                if cycle not in self.result.cycles:
                    self.result.cycles.append(cycle)
                return
            
            if node in visited:
                return
            
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in self.result.graph.get(node, set()):
                dfs(neighbor, path + [node])
            
            rec_stack.remove(node)
        
        for module in self.result.modules.keys():
            if module not in visited:
                dfs(module, [])

    def _detect_hotspots(self) -> None:
        """Identify hotspots: God Classes, Long/Complex Functions, etc."""
        loc_cc_items = []
        god_class_modules = set()  # Track modules already added as god classes
        
        for module_name, module_info in self.result.modules.items():
            # God Classes (LOC > 300)
            for cls_name, cls_info in module_info.classes.items():
                if cls_info.loc > 300 and module_name not in god_class_modules:
                    self.result.hotspots_god_class.append(module_info)
                    god_class_modules.add(module_name)
                
                # Class-level LOC/CC
                loc_cc_items.append((
                    f"{module_name}.{cls_name}",
                    cls_info
                ))
                
                # Method-level LOC/CC
                for method_name, method_info in cls_info.methods.items():
                    loc_cc_items.append((
                        f"{module_name}.{cls_name}.{method_name}",
                        method_info
                    ))
            
            # Function-level LOC/CC
            for func_name, func_info in module_info.functions.items():
                loc_cc_items.append((
                    f"{module_name}.{func_name}",
                    func_info
                ))
            
            # Mixed layers
            if module_info.is_ui_ml_mixed:
                self.result.hotspots_mixed_layer.append(module_info)
            
            # Threading usage
            if module_info.uses_threading:
                self.result.hotspots_threading.append(module_info)
        
        # Sort by LOC + CC (combined score)
        loc_cc_items.sort(key=lambda x: (x[1].loc + x[1].complexity * 10), reverse=True)
        self.result.hotspots_loc_cc = loc_cc_items

    def _get_layer(self, module_name: str) -> str:
        """
        Determines which architectural layer a module belongs to.
        
        Based on Clean Architecture conventions:
        - domain: Core business logic (entities, value objects, domain services)
        - application: Use cases, application services, interpreters
        - infrastructure: External adapters (API clients, repositories, DI)
        - gui: Presentation layer (views, controllers, widgets)
        - entrypoints: Composition root (main.py, app.py)
        - tests: Test modules
        - unknown: Everything else (utilities, scripts, etc.)
        
        NOTE: No trailing dot in startswith() - "src.gui" should match "src.gui"!
        """
        if module_name.startswith("src.domain") or module_name.startswith("domain"):
            return "domain"
        elif module_name.startswith("src.application") or module_name.startswith("application"):
            return "application"
        elif module_name.startswith("src.infrastructure") or module_name.startswith("infrastructure"):
            return "infrastructure"
        elif module_name.startswith("src.gui") or module_name.startswith("gui") or module_name.startswith("src.ui") or module_name.startswith("ui"):
            return "gui"
        elif module_name in ("main", "src.main", "app", "src.app"):
            return "entrypoints"
        elif module_name.startswith("tests") or module_name.startswith("test_"):
            return "tests"
        else:
            return "unknown"

    def _detect_layer_violations(self) -> None:
        """
        Detects architectural layer violations based on Clean Architecture rules.
        
        Returns a list of tuples: (from_module, to_module, reason)
        """
        violations = []
        
        for module, deps in self.result.graph.items():
            from_layer = self._get_layer(module)
            
            # Skip tests and unknown modules
            if from_layer in ("tests", "unknown"):
                continue
            
            allowed_layers = ALLOWED_DEPENDENCIES.get(from_layer, set())
            
            for dep in deps:
                to_layer = self._get_layer(dep)
                
                # Skip if target is unknown
                if to_layer == "unknown":
                    continue
                
                # Check if dependency is allowed
                if to_layer not in allowed_layers:
                    reason = f"'{from_layer}' layer CANNOT depend on '{to_layer}' layer (Clean Architecture violation)"
                    violations.append((module, dep, reason))
        
        self.result.layer_violations = violations

    def _calculate_coupling_metrics(self) -> None:
        """
        Calculates Robert C. Martin's coupling metrics for each module.
        
        Ca (Afferent Coupling): Number of modules depending ON this module
        Ce (Efferent Coupling): Number of modules this module depends ON
        Instability (I): Ce / (Ca + Ce), range [0, 1]
        
        Interpretation:
        - I = 0: Maximally stable (many incoming, no outgoing) → Ideal for Domain
        - I = 1: Maximally unstable (no incoming, many outgoing) → Typical for GUI
        """
        metrics = {}
        
        for module in self.result.modules.keys():
            ca = self.result.fan_in.get(module, 0)
            ce = self.result.fan_out.get(module, 0)
            
            # Instability: I = Ce / (Ca + Ce)
            # Handle division by zero
            instability = ce / (ca + ce) if (ca + ce) > 0 else 0.0
            
            metrics[module] = CouplingMetrics(
                ca=ca,
                ce=ce,
                instability=instability
            )
        
        self.result.coupling_metrics = metrics

# ----- Report Generator -----
class ReportGenerator:
    """Generates output reports in multiple formats: MD, JSON, HTML, DOT, CSV."""
    def __init__(self, result: AnalysisResult, out_dir: Path):
        self.result = result
        self.out_dir = out_dir

    def generate(self, format_choice: str, open_html: bool = False) -> None:
        """Generate reports based on format choice."""
        formats = [format_choice] if format_choice != "all" else ["md", "json", "html", "dot", "csv"]
        
        html_file = None
        for fmt in formats:
            if fmt == "md":
                self._write_markdown()
            elif fmt == "json":
                self._write_json()
            elif fmt == "html":
                html_file = self._write_html()
            elif fmt == "dot":
                self._write_dot()
            elif fmt == "csv":
                self._write_csv()
        
        if open_html and html_file:
            print(f"🌐 HTML riport megnyitása böngészőben...")
            webbrowser.open(f"file://{html_file.resolve()}")

    def _write_markdown(self) -> None:
        """Generate comprehensive Markdown report with 6 sections."""
        md_file = self.out_dir / "analysis_summary.md"
        
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(f"# Projekt Analízis Riport: {self.result.root.name}\n\n")
            f.write(f"**Generálva:** {self.result.timestamp}\n\n")
            f.write("---\n\n")
            
            # SECTION 1: Quick Summary
            f.write("## 1. 📊 Gyors Összegzés\n\n")
            
            total_modules = len(self.result.modules)
            total_loc = sum(m.loc for m in self.result.modules.values())
            total_classes = sum(len(m.classes) for m in self.result.modules.values())
            total_functions = sum(len(m.functions) for m in self.result.modules.values())
            
            f.write(f"- **Modulok:** {total_modules}\n")
            f.write(f"- **LOC (összesen):** {total_loc:,}\n")
            f.write(f"- **Osztályok:** {total_classes}\n")
            f.write(f"- **Függvények:** {total_functions}\n")
            f.write(f"- **Ciklusok:** {len(self.result.cycles)}\n")
            f.write(f"- **External deps:** {len(self.result.external_deps)}\n")
            f.write(f"- **Layer violations:** {len(self.result.layer_violations)}\n\n")
            
            # SECTION 2: Refactoring Priorities (Hotspots)
            f.write("## 2. 🔥 Refaktorációs Prioritások (Hotspotok)\n\n")
            
            f.write("### God Classes (LOC > 300)\n")
            if not self.result.hotspots_god_class:
                f.write("✅ Nem találtunk God Class-okat.\n\n")
            else:
                for mod in self.result.hotspots_god_class[:10]:
                    for cls_name, cls_info in mod.classes.items():
                        if cls_info.loc > 300:
                            f.write(f"- **{mod.module_name}.{cls_name}**: {cls_info.loc} LOC\n")
                f.write("\n")
            
            f.write("### Complex Functions/Methods (Top 10)\n")
            for name, info in self.result.hotspots_loc_cc[:10]:
                f.write(f"- **{name}**: LOC={info.loc}, CC={info.complexity}\n")
            f.write("\n")
            
            f.write("### Mixed Layers (UI + ML)\n")
            if not self.result.hotspots_mixed_layer:
                f.write("✅ Nem találtunk réteg keveredést.\n\n")
            else:
                for mod in self.result.hotspots_mixed_layer[:5]:
                    f.write(f"- {mod.module_name}\n")
                f.write("\n")
            
            # SECTION 3: Import Graph Overview
            f.write("## 3. 🕸️  Import Gráf Áttekintés\n\n")
            
            f.write("### Top 10 Fan-In (Legtöbb bejövő függőség)\n")
            sorted_fan_in = sorted(
                self.result.fan_in.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
            
            for module, count in sorted_fan_in:
                f.write(f"- **{module}**: {count} bejövő\n")
            f.write("\n")
            
            f.write("### Top 10 Fan-Out (Legtöbb kimenő függőség)\n")
            sorted_fan_out = sorted(
                self.result.fan_out.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
            
            for module, count in sorted_fan_out:
                f.write(f"- **{module}**: {count} kimenő\n")
            f.write("\n")
            
            f.write("### Circular Dependencies\n")
            if not self.result.cycles:
                f.write("✅ Nem találtunk körkörös függőségeket.\n\n")
            else:
                f.write(f"⚠️ **{len(self.result.cycles)} ciklus találva:**\n\n")
                for cycle in self.result.cycles[:5]:
                    f.write(f"- {' → '.join(cycle)}\n")
                if len(self.result.cycles) > 5:
                    f.write(f"- ...és még {len(self.result.cycles) - 5} ciklus\n")
                f.write("\n")
            
            # SECTION 4: Detailed Module Breakdown
            f.write("## 4. 📦 Részletes Modul Breakdown (Top 50)\n\n")
            
            modules_sorted = sorted(
                self.result.modules.values(),
                key=lambda m: m.loc,
                reverse=True
            )[:50]
            
            for mod in modules_sorted:
                f.write(f"### {mod.module_name}\n")
                f.write(f"- **LOC:** {mod.loc}\n")
                f.write(f"- **Classes:** {len(mod.classes)}\n")
                f.write(f"- **Functions:** {len(mod.functions)}\n")
                f.write(f"- **Fan-In:** {self.result.fan_in.get(mod.module_name, 0)}\n")
                f.write(f"- **Fan-Out:** {self.result.fan_out.get(mod.module_name, 0)}\n")
                
                if mod.classes:
                    f.write(f"- **Classes:**\n")
                    for cls_name, cls_info in list(mod.classes.items())[:5]:
                        f.write(f"  - `{cls_name}`: {cls_info.loc} LOC, {cls_info.complexity} CC\n")
                
                if mod.functions:
                    f.write(f"- **Functions:**\n")
                    for func_name, func_info in list(mod.functions.items())[:5]:
                        f.write(f"  - `{func_name}`: {func_info.loc} LOC, {func_info.complexity} CC\n")
                
                f.write("\n")
            
            # SECTION 5: Layer Violations (NEW!)
            f.write("## 5. 🚨 Réteg Sértések (Layer Violations)\n\n")
            
            # Count unknown modules
            unknown_modules = [
                mod for mod in self.result.modules.keys()
                if self._get_layer(mod) == "unknown"
            ]
            
            if unknown_modules:
                f.write(f"⚠️ **FIGYELEM:** {len(unknown_modules)} modul nem kategorizálható (unknown layer).\n")
                f.write("Ezek a modulok nem lesznek ellenőrizve Clean Architecture szabályok ellen.\n")
                f.write(f"Példák: {', '.join(list(unknown_modules)[:5])}\n\n")
            
            if not self.result.layer_violations:
                f.write("✅ **Nem találtunk réteg sértéseket!** Clean Architecture OK.\n\n")
                f.write("A projekt követi a Clean Architecture Dependency Rule-t:\n")
                f.write("- Domain réteg NEM függ senkitől ✅\n")
                f.write("- Application csak Domain-től függ ✅\n")
                f.write("- Infrastructure Domain + Application-től függ ✅\n")
                f.write("- GUI Application + Infrastructure-től függ ✅\n\n")
            else:
                f.write(f"⚠️ **{len(self.result.layer_violations)} réteg sértés találva:**\n\n")
                f.write("A Clean Architecture Dependency Rule alapján ezek a függőségek TILOSAK:\n\n")
                
                # Group by from_layer
                by_layer = defaultdict(list)
                for from_mod, to_mod, reason in self.result.layer_violations:
                    from_layer = self._get_layer(from_mod)
                    by_layer[from_layer].append((from_mod, to_mod, reason))
                
                for layer, items in sorted(by_layer.items()):
                    f.write(f"### ❌ {layer.upper()} réteg sértései:\n\n")
                    for from_mod, to_mod, reason in items[:20]:  # Max 20 per layer
                        f.write(f"- **{from_mod}** → **{to_mod}**\n")
                        f.write(f"  - ⚠️ {reason}\n")
                    if len(items) > 20:
                        f.write(f"  - ...és még {len(items) - 20} sértés\n")
                    f.write("\n")
            
            # SECTION 6: Coupling Metrics (NEW!)
            f.write("## 6. 📈 Coupling Metrics (Robert C. Martin)\n\n")
            
            f.write("**Instability (I) = Ce / (Ca + Ce)** ahol:\n")
            f.write("- **Ca** (Afferent): Bejövő függőségek száma\n")
            f.write("- **Ce** (Efferent): Kimenő függőségek száma\n")
            f.write("- **I = 0**: Maximálisan stabil (sok bejövő, nincs kimenő)\n")
            f.write("- **I = 1**: Maximálisan instabil (nincs bejövő, sok kimenő)\n\n")
            
            f.write("**Ideális állapot:**\n")
            f.write("- Domain modulok: I ≈ 0 (stabil core)\n")
            f.write("- GUI modulok: I ≈ 1 (változékony presentation)\n\n")
            
            f.write("### Top 10 Leginstabilabb Modulok\n\n")
            
            sorted_modules = sorted(
                self.result.coupling_metrics.items(),
                key=lambda x: x[1].instability,
                reverse=True
            )[:10]
            
            f.write("| Modul | Ca (in) | Ce (out) | Instability | Értékelés |\n")
            f.write("|-------|---------|----------|-------------|------------|\n")
            
            for module, metrics in sorted_modules:
                if metrics.instability > 0.8:
                    assessment = "⚠️ Nagyon instabil"
                elif metrics.instability > 0.5:
                    assessment = "🟡 Instabil"
                else:
                    assessment = "✅ Stabil"
                
                f.write(f"| `{module}` | {metrics.ca} | {metrics.ce} | "
                        f"{metrics.instability:.2f} | {assessment} |\n")
            
            f.write("\n")
            
            f.write("### Top 10 Legstabilabb Modulok\n\n")
            
            sorted_stable = sorted(
                self.result.coupling_metrics.items(),
                key=lambda x: x[1].instability
            )[:10]
            
            f.write("| Modul | Ca (in) | Ce (out) | Instability | Értékelés |\n")
            f.write("|-------|---------|----------|-------------|------------|\n")
            
            for module, metrics in sorted_stable:
                if metrics.instability < 0.2:
                    assessment = "✅ Nagyon stabil"
                elif metrics.instability < 0.5:
                    assessment = "✅ Stabil"
                else:
                    assessment = "🟡 Közepesen stabil"
                
                f.write(f"| `{module}` | {metrics.ca} | {metrics.ce} | "
                        f"{metrics.instability:.2f} | {assessment} |\n")
            
            f.write("\n")
        
        print(f"✅ Markdown riport létrehozva: {md_file}")

    def _get_layer(self, module_name: str) -> str:
        """Helper method for markdown report - determines layer (NO trailing dot!)"""
        if module_name.startswith("src.domain") or module_name.startswith("domain"):
            return "domain"
        elif module_name.startswith("src.application") or module_name.startswith("application"):
            return "application"
        elif module_name.startswith("src.infrastructure") or module_name.startswith("infrastructure"):
            return "infrastructure"
        elif module_name.startswith("src.gui") or module_name.startswith("gui") or module_name.startswith("src.ui") or module_name.startswith("ui"):
            return "gui"
        elif module_name in ("main", "src.main", "app", "src.app"):
            return "entrypoints"
        elif module_name.startswith("tests") or module_name.startswith("test_"):
            return "tests"
        else:
            return "unknown"

    def _write_json(self) -> None:
        """Generate detailed JSON structure dump."""
        json_file = self.out_dir / "structure.json"
        
        # Custom JSON encoder for dataclasses
        def default_encoder(obj):
            if isinstance(obj, Path):
                return str(obj)
            if isinstance(obj, set):
                return sorted(list(obj))  # Convert set to sorted list for proper JSON
            if dataclasses.is_dataclass(obj):
                return dataclasses.asdict(obj)
            return obj.__dict__
        
        data = {
            "timestamp": self.result.timestamp,
            "root": str(self.result.root),
            "summary": {
                "total_modules": len(self.result.modules),
                "total_loc": sum(m.loc for m in self.result.modules.values()),
                "total_classes": sum(len(m.classes) for m in self.result.modules.values()),
                "total_functions": sum(len(m.functions) for m in self.result.modules.values()),
                "cycles_count": len(self.result.cycles),
                "external_deps_count": len(self.result.external_deps),
                "layer_violations_count": len(self.result.layer_violations)
            },
            "modules": {
                name: dataclasses.asdict(mod)
                for name, mod in self.result.modules.items()
            },
            "graph": {
                module: list(deps)
                for module, deps in self.result.graph.items()
            },
            "fan_in": dict(self.result.fan_in),
            "fan_out": dict(self.result.fan_out),
            "cycles": self.result.cycles,
            "external_deps": dict(self.result.external_deps),
            "hotspots": {
                "god_classes": [m.module_name for m in self.result.hotspots_god_class],
                "mixed_layers": [m.module_name for m in self.result.hotspots_mixed_layer],
                "threading": [m.module_name for m in self.result.hotspots_threading],
                "loc_cc_top_20": [
                    {"name": name, "loc": info.loc, "complexity": info.complexity}
                    for name, info in self.result.hotspots_loc_cc[:20]
                ]
            },
            "layer_violations": [
                {"from": from_mod, "to": to_mod, "reason": reason}
                for from_mod, to_mod, reason in self.result.layer_violations
            ],
            "coupling_metrics": {
                module: dataclasses.asdict(metrics)
                for module, metrics in self.result.coupling_metrics.items()
            }
        }
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=default_encoder, ensure_ascii=False)
        
        print(f"✅ JSON struktura létrehozva: {json_file}")

    def _write_dot(self) -> None:
        """
        Generate Graphviz DOT file with:
        - Layer-based node coloring
        - Red edges for layer violations
        - Automatic PNG generation via Graphviz
        """
        dot_file = self.out_dir / "import_graph.dot"
        
        # Build violations set for quick lookup
        violations_set = {(v[0], v[1]) for v in self.result.layer_violations}
        
        with open(dot_file, 'w', encoding='utf-8') as f:
            f.write('digraph ImportGraph {\n')
            f.write('  rankdir=LR;\n')
            f.write('  node [shape=box, style=filled];\n')
            f.write('  edge [color=gray];\n\n')
            
            # Apply layer-based colors to nodes
            for module in self.result.graph.keys():
                layer = self._get_layer(module)
                color = LAYER_COLORS.get(layer, "#FFFFFF")
                f.write(f'  "{module}" [fillcolor="{color}"];\n')
            
            f.write("\n")
            
            # Draw edges (red for violations, gray for normal)
            for module, deps in self.result.graph.items():
                for dep in deps:
                    if (module, dep) in violations_set:
                        # RED edge for violations
                        f.write(f'  "{module}" -> "{dep}" [color=red, penwidth=2.5];\n')
                    else:
                        # Normal edge
                        f.write(f'  "{module}" -> "{dep}";\n')
            
            f.write('}\n')
        
        print(f"✅ DOT gráf létrehozva: {dot_file}")
        
        # Try to generate PNG using Graphviz
        png_file = self.out_dir / "import_graph.png"
        try:
            result = subprocess.run(
                ['dot', '-Tpng', str(dot_file), '-o', str(png_file)],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                print(f"✅ PNG gráf generálva: {png_file}")
            else:
                print(f"⚠️  PNG generálás sikertelen (Graphviz hiba): {result.stderr}")
        except FileNotFoundError:
            print("⚠️  Graphviz nincs telepítve. PNG generálás kihagyva.")
        except subprocess.TimeoutExpired:
            print("⚠️  PNG generálás timeout (túl nagy gráf?).")
        except Exception as e:
            print(f"⚠️  PNG generálás hiba: {e}")

    def _write_csv(self) -> None:
        """Generate CSV reports for hotspots and Qt signals/slots."""
        # Hotspots CSV
        hotspots_csv = self.out_dir / "hotspots.csv"
        with open(hotspots_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Type", "Module", "Name", "LOC", "Complexity"])
            
            # God Classes
            for mod in self.result.hotspots_god_class[:30]:
                for cls_name, cls_info in mod.classes.items():
                    if cls_info.loc > 300:
                        writer.writerow([
                            "GodClass",
                            mod.module_name,
                            cls_name,
                            cls_info.loc,
                            cls_info.complexity
                        ])
            
            # Long/Complex Functions
            for name, info in self.result.hotspots_loc_cc[:50]:
                parts = name.rsplit('.', 1)
                module = parts[0] if len(parts) > 1 else name
                func_name = parts[1] if len(parts) > 1 else name
                writer.writerow([
                    "Function",
                    module,
                    func_name,
                    info.loc,
                    info.complexity
                ])
        
        print(f"✅ Hotspots CSV létrehozva: {hotspots_csv}")
        
        # Qt Signals/Slots CSV
        qt_csv = self.out_dir / "qt_signals_slots.csv"
        with open(qt_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Module", "Class", "Signal", "Line"])
            
            for mod in self.result.modules.values():
                for signal_info in mod.qt_signals:
                    writer.writerow([
                        mod.module_name,
                        signal_info.get("class", ""),
                        signal_info.get("name", ""),
                        signal_info.get("lineno", "")
                    ])
        
        print(f"✅ Qt signals CSV létrehozva: {qt_csv}")

    def _write_html(self) -> Path:
        """Generate interactive HTML report with D3.js visualization."""
        html_file = self.out_dir / "analysis_report.html"
        
        # Prepare D3.js nodes - EVERY module should be a node (not just those with outgoing edges)
        nodes = [{"id": module_name} for module_name in self.result.modules.keys()]
        
        links = []
        violations_set = {(v[0], v[1]) for v in self.result.layer_violations}
        
        for module, deps in self.result.graph.items():
            for dep in deps:
                is_violation = (module, dep) in violations_set
                links.append({
                    "source": module,
                    "target": dep,
                    "violation": is_violation
                })
        
        # Prepare hotspots table HTML
        hotspot_rows = []
        
        # Add God Classes
        for mod in self.result.hotspots_god_class[:30]:
            for cls_name, cls_info in mod.classes.items():
                hotspot_rows.append(
                    f'<tr><td>GodClass</td><td>{mod.module_name}</td>'
                    f'<td>{cls_name}</td><td>{cls_info.loc}</td><td>{cls_info.complexity}</td></tr>'
                )
        
        # Add long/complex functions
        for name, info in self.result.hotspots_loc_cc[:50]:
            parts = name.rsplit('.', 1)
            module = parts[0] if len(parts) > 1 else name
            func_name = parts[1] if len(parts) > 1 else name
            hotspot_rows.append(
                f'<tr><td>method</td><td>{module}</td>'
                f'<td>{func_name}</td><td>{info.loc}</td><td>{info.complexity}</td></tr>'
            )
        
        hotspots_html = '\n'.join(hotspot_rows)
        
        # Prepare violations table HTML
        violations_html = ""
        if self.result.layer_violations:
            violations_rows = []
            for from_mod, to_mod, reason in self.result.layer_violations[:50]:
                violations_rows.append(
                    f'<tr><td>{from_mod}</td><td>{to_mod}</td><td>{reason}</td></tr>'
                )
            violations_html = '\n'.join(violations_rows)
        
        violations_section = ""
        if self.result.layer_violations:
            violations_section = f"""
        <div class="table-container">
            <h2>🚨 Layer Violations ({len(self.result.layer_violations)})</h2>
            <table>
                <thead>
                    <tr><th>From Module</th><th>To Module</th><th>Reason</th></tr>
                </thead>
                <tbody>{violations_html}</tbody>
            </table>
        </div>
        """
        
        html_content = f"""<!DOCTYPE html>
<html lang="hu">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Projekt Analízis Riport - {self.result.root.name}</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 0; background-color: #f9f9f9; }}
        header {{ background-color: #333; color: white; padding: 15px 30px; }}
        h1 {{ margin: 0; }}
        .summary {{ padding: 20px 30px; background-color: #fff; margin: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}
        .summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 15px; }}
        .summary-card {{ padding: 15px; background-color: #f7f7f7; border-radius: 6px; text-align: center; }}
        .summary-card h3 {{ margin: 0 0 10px 0; font-size: 24px; color: #333; }}
        .summary-card p {{ margin: 0; font-size: 14px; color: #666; }}
        main {{ display: flex; flex-wrap: wrap; padding: 20px; }}
        .chart-container {{
            border: 1px solid #ddd; background-color: #fff;
            border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            flex-basis: 60%; min-width: 500px; margin: 10px;
        }}
        .table-container {{
            border: 1px solid #ddd; background-color: #fff;
            border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            flex-basis: 35%; min-width: 300px; margin: 10px;
            max-height: 80vh; overflow-y: auto;
        }}
        h2 {{ border-bottom: 2px solid #eee; padding: 15px 20px; margin: 0; }}
        svg {{ display: block; width: 100%; height: 70vh; }}
        .node circle {{
            stroke: #fff; stroke-width: 1.5px;
            r: 6px; fill: #1f77b4;
            cursor: pointer;
        }}
        .node text {{
            font-size: 10px; font-family: sans-serif;
            pointer-events: none;
            fill: #333;
        }}
        .link {{ stroke: #999; stroke-opacity: 0.6; }}
        .link.violation {{ stroke: red; stroke-width: 2px; stroke-opacity: 0.8; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border-bottom: 1px solid #ddd; padding: 12px 15px; text-align: left; font-size: 14px; }}
        th {{ background-color: #f7f7f7; position: sticky; top: 0; }}
        tr:hover {{ background-color: #f1f1f1; }}
        .legend {{ padding: 15px 20px; background-color: #f9f9f9; border-top: 2px solid #eee; }}
        .legend-item {{ display: inline-block; margin-right: 20px; }}
        .legend-color {{ display: inline-block; width: 15px; height: 15px; margin-right: 5px; vertical-align: middle; }}
    </style>
</head>
<body>
    <header>
        <h1>Projekt Analízis: {self.result.root.name}</h1>
    </header>
    
    <div class="summary">
        <h2>Gyors Összegzés</h2>
        <div class="summary-grid">
            <div class="summary-card">
                <h3>{len(self.result.modules)}</h3>
                <p>Modulok</p>
            </div>
            <div class="summary-card">
                <h3>{sum(m.loc for m in self.result.modules.values()):,}</h3>
                <p>LOC (összesen)</p>
            </div>
            <div class="summary-card">
                <h3>{len(self.result.cycles)}</h3>
                <p>Ciklusok</p>
            </div>
            <div class="summary-card">
                <h3>{len(self.result.layer_violations)}</h3>
                <p>Layer Violations</p>
            </div>
        </div>
    </div>
    
    <main>
        <div class="chart-container">
            <h2>Import Gráf (D3.js)</h2>
            <div class="legend">
                <div class="legend-item"><span class="legend-color" style="background-color: #4169E1;"></span>Domain</div>
                <div class="legend-item"><span class="legend-color" style="background-color: #32CD32;"></span>Application</div>
                <div class="legend-item"><span class="legend-color" style="background-color: #FF6347;"></span>Infrastructure</div>
                <div class="legend-item"><span class="legend-color" style="background-color: #FFD700;"></span>GUI</div>
                <div class="legend-item"><span class="legend-color" style="background-color: #9370DB;"></span>Entrypoints</div>
                <div class="legend-item"><span class="legend-color" style="background-color: red;"></span>Violation Edge</div>
            </div>
            <svg id="d3-graph"></svg>
        </div>
        
        <div class="table-container">
            <h2>Top Hotspotok (CC/LOC)</h2>
            <table>
                <thead>
                    <tr><th>Típus</th><th>Modul</th><th>Név</th><th>LOC</th><th>CC</th></tr>
                </thead>
                <tbody>{hotspots_html}</tbody>
            </table>
        </div>
        
        {violations_section}
    </main>
    
    <script>
        const nodes = {json.dumps(nodes)};
        const links = {json.dumps(links)};
        
        // Layer detection function (matches Python implementation)
        function getLayer(moduleName) {{
            if (moduleName.startsWith("src.domain.") || moduleName.startsWith("domain.")) return "domain";
            if (moduleName.startsWith("src.application.") || moduleName.startsWith("application.")) return "application";
            if (moduleName.startsWith("src.infrastructure.") || moduleName.startsWith("infrastructure.")) return "infrastructure";
            if (moduleName.startsWith("src.gui.") || moduleName.startsWith("gui.")) return "gui";
            if (moduleName === "main" || moduleName === "src.main" || moduleName === "app") return "entrypoints";
            if (moduleName.startsWith("tests.") || moduleName.startsWith("test_")) return "tests";
            return "unknown";
        }}
        
        const layerColors = {{
            "domain": "#4169E1",
            "application": "#32CD32",
            "infrastructure": "#FF6347",
            "gui": "#FFD700",
            "entrypoints": "#9370DB",
            "tests": "#A9A9A9",
            "unknown": "#FFFFFF"
        }};
        
        // Apply layer colors to nodes
        nodes.forEach(node => {{
            node.layer = getLayer(node.id);
            node.color = layerColors[node.layer];
        }});
        
        const svg = d3.select("svg#d3-graph");
        const width = svg.node().getBoundingClientRect().width;
        const height = svg.node().getBoundingClientRect().height;

        // Create zoomable group FIRST
        const g = svg.append("g");
        
        // Create links in zoomable group
        const link = g.append("g")
            .selectAll("line")
            .data(links)
            .enter().append("line")
            .attr("class", d => d.violation ? "link violation" : "link");

        // Create nodes in zoomable group
        const node = g.append("g")
            .attr("class", "node")
            .selectAll("g")
            .data(nodes)
            .enter().append("g");

        node.append("circle")
            .style("fill", d => d.color);
        
        node.append("text")
            .attr("x", 8)
            .attr("y", 3)
            .text(d => d.id);

        // Setup force simulation
        const simulation = d3.forceSimulation(nodes)
            .force("link", d3.forceLink(links).id(d => d.id).distance(80))
            .force("charge", d3.forceManyBody().strength(-250))
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("x", d3.forceX(width / 2).strength(0.05))
            .force("y", d3.forceY(height / 2).strength(0.05));

        // Tick function - update positions
        simulation.on("tick", () => {{
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);

            node.attr("transform", d => `translate(${{d.x}},${{d.y}})`);
        }});

        // Drag functions
        function dragstarted(event) {{
            if (!event.active) simulation.alphaTarget(0.3).restart();
            event.subject.fx = event.subject.x;
            event.subject.fy = event.subject.y;
        }}
        function dragged(event) {{
            event.subject.fx = event.x;
            event.subject.fy = event.y;
        }}
        function dragended(event) {{
            if (!event.active) simulation.alphaTarget(0);
            event.subject.fx = null;
            event.subject.fy = null;
        }}
        
        // Enable drag on nodes
        node.call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended));
        
        // Enable zoom/pan
        svg.call(d3.zoom()
            .extent([[0, 0], [width, height]])
            .scaleExtent([0.1, 8])
            .on("zoom", ({{transform}}) => {{
                g.attr("transform", transform);
            }}));
    </script>
</body>
</html>"""
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ HTML riport létrehozva: {html_file}")
        return html_file

# ----- CLI -----
def main():
    parser = argparse.ArgumentParser(
        description="Ultimate Project Analyzer - Clean Architecture Validation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
        Példák:
          %(prog)s --root ./src                           # Minden formátum (MD, JSON, HTML, DOT, CSV)
          %(prog)s --root ./myproject --open              # Minden formátum + HTML megnyitás
          %(prog)s --root . --format md                   # Csak Markdown
          %(prog)s --root . --format json --out results   # Csak JSON, custom kimenet
        
        Layer Detection:
          - domain: src.domain.*
          - application: src.application.*
          - infrastructure: src.infrastructure.*
          - gui: src.gui.*
          - entrypoints: main.py, app.py
        
        Clean Architecture Validation:
          - Detects layer violations (e.g., GUI → Domain direct call)
          - Calculates coupling metrics (Ca, Ce, Instability)
          - Color-coded visualization (Blue=Domain, Green=Application, etc.)
        """)
    )
    
    parser.add_argument(
        "--root",
        type=str,
        default=".",
        help="A projekt gyökérkönyvtára (default: aktuális könyvtár)"
    )
    
    parser.add_argument(
        "--format",
        type=str,
        choices=["all", "html", "md", "json", "dot", "csv"],
        default="all",
        help="Kimeneti formátum (default: all = minden formátum)"
    )
    
    parser.add_argument(
        "--out",
        type=str,
        default="analysis_out",
        help="Kimeneti könyvtár (default: analysis_out)"
    )
    
    parser.add_argument(
        "--open",
        action="store_true",
        help="HTML riport automatikus megnyitása böngészőben"
    )
    
    parser.add_argument(
        "--ignore-file",
        type=str,
        help="Kizárandó könyvtárak listája (soronként egy név)"
    )
    
    args = parser.parse_args()
    
    root_path = Path(args.root).resolve()
    out_dir = Path(args.out)
    
    analyzer = ProjectAnalyzer(root_path, out_dir, args.ignore_file)
    result = analyzer.run_analysis()
    
    generator = ReportGenerator(result, out_dir)
    generator.generate(args.format, args.open)

if __name__ == "__main__":
    main()
