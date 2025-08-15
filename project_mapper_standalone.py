#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Mapper — Python codebase refactor helper (standalone)
=============================================================

What it does
------------
- Walks a project tree and indexes all *.py files
- Builds an import dependency graph at module level (AST-based)
- Computes metrics per module/class/function:
  - LOC (non-empty lines)
  - Approx Cyclomatic Complexity (CC) without external deps
  - Public API size (defs not starting with '_')
- Finds potential "god classes" and "long functions"
- PySide6/Qt heuristics:
  - Detects `Signal(...)` declarations
  - Detects `.connect(...)` calls and target slot expressions

Outputs
-------
- `summary.json` — full structured data
- `report.md` — human-readable summary with hotspots
- `dependency_graph.dot` — Graphviz DOT (render: `dot -Tpng dependency_graph.dot -o graph.png`)
- `hotspots.csv` — modules/classes/functions needing attention
- `qt_signals.csv` — detected signals and connections

Usage
-----
    python project_mapper.py --root ./src --out ./analysis_out

Notes
-----
- Pure-Python, no external libraries required.
- CC is an approximation: counts decision points from AST (If/For/While/Try/BoolOp/Comprehensions).
- Import graph is static; dynamic imports won't be detected.
"""
import argparse
import ast
import csv
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set

def rel_module_name(py_path: Path, root: Path) -> str:
    rel = py_path.relative_to(root)
    parts = list(rel.parts)
    if parts[-1].endswith('.py'):
        parts[-1] = parts[-1][:-3]
    if parts[-1] == '__init__':
        parts = parts[:-1]
    return '.'.join(p for p in parts if p)

def count_loc(source: str) -> int:
    return sum(1 for line in source.splitlines() if line.strip())

def approx_cc(node: ast.AST) -> int:
    decision_types = (
        ast.If, ast.For, ast.While, ast.Try, ast.ExceptHandler,
        ast.With, ast.BoolOp, ast.IfExp, ast.Assert,
        ast.comprehension,
    )
    count = 1
    for n in ast.walk(node):
        if isinstance(n, decision_types):
            count += 1
        if isinstance(n, ast.BoolOp) and getattr(n, 'values', None):
            count += max(0, len(n.values) - 1)
    return count

def detect_qt_signals_and_connects(tree: ast.AST, source: str) -> Tuple[List[Tuple[str,str,int]], List[Tuple[str,str,int]]]:
    signals = []
    connects = []
    class SignalVisitor(ast.NodeVisitor):
        def visit_Assign(self, node: ast.Assign):
            try:
                if isinstance(node.value, ast.Call) and getattr(node.value.func, 'id', None) == 'Signal':
                    target = node.targets[0]
                    if isinstance(target, ast.Name):
                        sig = ast.get_source_segment(source, node.value) or 'Signal(...)'
                        signals.append((target.id, sig, node.lineno))
            except Exception:
                pass
            self.generic_visit(node)

        def visit_Call(self, node: ast.Call):
            try:
                if isinstance(node.func, ast.Attribute) and node.func.attr == 'connect':
                    emitter = ast.get_source_segment(source, node.func.value) or '<expr>'
                    target = '<slot>'
                    if node.args:
                        target = ast.get_source_segment(source, node.args[0]) or '<slot>'
                    connects.append((emitter, target, node.lineno))
            except Exception:
                pass
            self.generic_visit(node)

    SignalVisitor().visit(tree)
    return signals, connects

class FunctionInfo:
    def __init__(self, name: str, lineno: int, loc: int, cc: int, is_public: bool):
        self.name = name
        self.lineno = lineno
        self.loc = loc
        self.cc = cc
        self.is_public = is_public

class ClassInfo:
    def __init__(self, name: str, lineno: int, loc: int, methods: List[FunctionInfo], signals: List[Tuple[str,str,int]]):
        self.name = name
        self.lineno = lineno
        self.loc = loc
        self.methods = methods
        self.signals = signals

class ModuleInfo:
    def __init__(self, module: str, path: str, loc: int, classes: List[ClassInfo], functions: List[FunctionInfo],
                 imports: Set[str], signals: List[Tuple[str,str,int]], connects: List[Tuple[str,str,int]]):
        self.module = module
        self.path = path
        self.loc = loc
        self.classes = classes
        self.functions = functions
        self.imports = imports
        self.signals = signals
        self.connects = connects

def parse_module(py_path: Path, root: Path) -> Optional[ModuleInfo]:
    try:
        src = py_path.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        return None
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return None

    module = rel_module_name(py_path, root)
    loc = count_loc(src)
    imports: Set[str] = set()

    class ImportVisitor(ast.NodeVisitor):
        def visit_Import(self, node: ast.Import):
            for n in node.names:
                imports.add(n.name.split('.')[0])
        def visit_ImportFrom(self, node: ast.ImportFrom):
            if node.module:
                imports.add(node.module.split('.')[0])

    ImportVisitor().visit(tree)

    functions: List[FunctionInfo] = []
    classes: List[ClassInfo] = []

    for n in tree.body:
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            fsrc = ast.get_source_segment(src, n) or ''
            finfo = FunctionInfo(
                name=n.name, lineno=n.lineno, loc=count_loc(fsrc), cc=approx_cc(n),
                is_public=not n.name.startswith('_')
            )
            functions.append(finfo)
        elif isinstance(n, ast.ClassDef):
            methods: List[FunctionInfo] = []
            class_src = ast.get_source_segment(src, n) or ''
            for b in n.body:
                if isinstance(b, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    msrc = ast.get_source_segment(src, b) or ''
                    methods.append(FunctionInfo(
                        name=b.name, lineno=b.lineno, loc=count_loc(msrc), cc=approx_cc(b),
                        is_public=not b.name.startswith('_')
                    ))
            sigs, _ = detect_qt_signals_and_connects(ast.Module(body=[n], type_ignores=[]), class_src)
            classes.append(ClassInfo(
                name=n.name, lineno=n.lineno, loc=count_loc(class_src), methods=methods, signals=sigs
            ))

    sigs_mod, connects_mod = detect_qt_signals_and_connects(tree, src)

    return ModuleInfo(
        module=module, path=str(py_path), loc=loc, classes=classes, functions=functions,
        imports=imports, signals=sigs_mod, connects=connects_mod
    )

def build_index(root: Path) -> Dict[str, ModuleInfo]:
    index: Dict[str, ModuleInfo] = {}
    for py in root.rglob('*.py'):
        if py.name.startswith('.') or 'venv' in py.parts or '__pycache__' in py.parts:
            continue
        mi = parse_module(py, root)
        if mi:
            index[mi.module] = mi
    return index

def compute_graph(index: Dict[str, ModuleInfo]) -> Dict[str, Set[str]]:
    graph: Dict[str, Set[str]] = {}
    mods = set(index.keys())
    for m, info in index.items():
        deps = set()
        for imp in info.imports:
            for cand in mods:
                if cand == imp or cand.startswith(imp + '.'):
                    deps.add(cand)
        graph[m] = deps - {m}
    return graph

def fan_in_out(graph: Dict[str, Set[str]]):
    fin = {m:0 for m in graph}
    fout = {m:len(deps) for m,deps in graph.items()}
    for m,deps in graph.items():
        for d in deps:
            fin[d] += 1
    return {m:(fin[m],fout[m]) for m in graph}

def find_cycles(graph: Dict[str, Set[str]]):
    visited = set()
    cycles = []

    def dfs(node, path):
        visited.add(node)
        path.append(node)
        for nxt in graph.get(node, []):
            if nxt in path:
                i = path.index(nxt)
                cycles.append(path[i:]+[nxt])
            elif nxt not in visited:
                dfs(nxt, path[:])

    for n in graph:
        if n not in visited:
            dfs(n, [])
    uniq = []
    seen = set()
    for c in cycles:
        edges = tuple(sorted((c[i], c[i+1]) for i in range(len(c)-1)))
        if edges not in seen:
            seen.add(edges)
            uniq.append(c)
    return uniq

def collect_hotspots(index: Dict[str, ModuleInfo], io_map):
    records = []
    for m, info in index.items():
        fin, fout = io_map.get(m, (0,0))
        records.append(('module', m, info.path, info.loc, '', fin, fout, ''))
        for c in info.classes:
            records.append(('class', f'{m}.{c.name}', info.path, c.loc, '', fin, fout, f'{len(c.methods)} methods'))
            for fn in c.methods:
                records.append(('method', f'{m}.{c.name}.{fn.name}', info.path, fn.loc, fn.cc, fin, fout, ''))
        for fn in info.functions:
            records.append(('function', f'{m}.{fn.name}', info.path, fn.loc, fn.cc, fin, fout, ''))
    return records

def write_dot(graph, out: Path):
    out.write_text('digraph G {\nrankdir=LR;\nnode [shape=box,fontsize=10];\n', encoding='utf-8')
    with out.open('a', encoding='utf-8') as f:
        for m,deps in graph.items():
            f.write(f'  "{m}" [label="{m}"];\n')
            for d in deps:
                f.write(f'  "{m}" -> "{d}";\n')
        f.write('}\n')

def write_csv_hotspots(records, out_csv: Path):
    with out_csv.open('w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['kind','name','path','loc','cc','fan_in','fan_out','extra'])
        def sort_key(r):
            kind = r[0]
            if kind == 'module':
                return (0, -r[5], -r[6], -r[3])
            elif kind == 'class':
                return (1, -r[3])
            else:
                cc = r[4] if isinstance(r[4], int) else 0
                return (2, -(cc), -r[3])
        for r in sorted(records, key=sort_key):
            w.writerow(r)

def write_qt_csv(index: Dict[str, ModuleInfo], out_csv: Path):
    with out_csv.open('w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['module','kind','emitter_or_name','target_or_signature','lineno','path'])
        for m, info in index.items():
            for name, sig, ln in info.signals:
                w.writerow([m,'signal',name,sig,ln,info.path])
            for emitter, target, ln in info.connects:
                w.writerow([m,'connect',emitter,target,ln,info.path])

def write_summary_json(index, graph, io_map, cycles, out_json: Path):
    def fn_info(obj: FunctionInfo):
        return {'name': obj.name, 'lineno': obj.lineno, 'loc': obj.loc, 'cc': obj.cc, 'is_public': obj.is_public}
    def cls_info(obj: ClassInfo):
        return {
            'name': obj.name, 'lineno': obj.lineno, 'loc': obj.loc,
            'methods': [fn_info(m) for m in obj.methods],
            'signals': [{'name': n, 'signature': s, 'lineno': ln} for (n,s,ln) in obj.signals]
        }
    data = {
        'modules': {
            m: {
                'path': info.path,
                'loc': info.loc,
                'imports_internal': sorted(list(graph.get(m, set()))),
                'fan_in': io_map.get(m,(0,0))[0],
                'fan_out': io_map.get(m,(0,0))[1],
                'classes': [cls_info(c) for c in info.classes],
                'functions': [fn_info(fn) for fn in info.functions],
                'qt': {
                    'signals': [{'name': n, 'signature': s, 'lineno': ln} for (n,s,ln) in info.signals],
                    'connects': [{'emitter': e, 'target': t, 'lineno': ln} for (e,t,ln) in info.connects],
                }
            }
            for m, info in index.items()
        },
        'cycles': cycles,
    }
    out_json.write_text(json.dumps(data, indent=2), encoding='utf-8')

def write_markdown_report(index: Dict[str, ModuleInfo], io_map, out_md: Path):
    top_fanin = sorted(index.values(), key=lambda mi: io_map.get(mi.module,(0,0))[0], reverse=True)[:10]
    top_loc = sorted(index.values(), key=lambda mi: mi.loc, reverse=True)[:10]
    lines = []
    lines.append('# Project Mapper Report\n')
    lines.append('## Top modules by fan-in (most depended-on)\n')
    for mi in top_fanin:
        fin, fout = io_map.get(mi.module,(0,0))
        lines.append(f'- `{mi.module}` — fan_in={fin}, fan_out={fout}, loc={mi.loc}')
    lines.append('\n## Top modules by LOC\n')
    for mi in top_loc:
        fin, fout = io_map.get(mi.module,(0,0))
        lines.append(f'- `{mi.module}` — loc={mi.loc}, fan_in={fin}, fan_out={fout}')
    lines.append('\n## Potential god classes\n')
    for mi in index.values():
        for c in mi.classes:
            if c.loc >= 400 or len(c.methods) >= 25:
                lines.append(f'- `{mi.module}.{c.name}` — loc={c.loc}, methods={len(c.methods)} (file: {mi.path})')
    lines.append('\n## Long / complex functions\n')
    for mi in index.values():
        for fn in mi.functions:
            if fn.loc >= 80 or fn.cc >= 15:
                lines.append(f'- `{mi.module}.{fn.name}` — loc={fn.loc}, cc={fn.cc}')
        for c in mi.classes:
            for fn in c.methods:
                if fn.loc >= 80 or fn.cc >= 15:
                    lines.append(f'- `{mi.module}.{c.name}.{fn.name}` — loc={fn.loc}, cc={fn.cc}')
    lines.append('\n## Qt Signals and connections (heuristic)\n')
    for mi in index.values():
        if mi.signals or mi.connects:
            lines.append(f'### {mi.module}')
            for name,sig,ln in mi.signals:
                lines.append(f'- Signal `{name}` at line {ln}: `{sig}`')
            for emitter, target, ln in mi.connects:
                lines.append(f'- Connect at line {ln}: `{emitter}.connect({target})`')
    out_md.write_text('\n'.join(lines), encoding='utf-8')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', required=True, help='Project root to scan (e.g., ./src)')
    ap.add_argument('--out', required=True, help='Output folder')
    args = ap.parse_args()

    root = Path(args.root).resolve()
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)

    index = build_index(root)
    graph = compute_graph(index)
    io_map = fan_in_out(graph)
    cycles = find_cycles(graph)

    write_dot(graph, out / 'dependency_graph.dot')
    write_summary_json(index, graph, io_map, cycles, out / 'summary.json')
    write_csv_hotspots(collect_hotspots(index, io_map), out / 'hotspots.csv')
    write_qt_csv(index, out / 'qt_signals.csv')
    write_markdown_report(index, io_map, out / 'report.md')

    print(f'[OK] Analyzed {len(index)} modules. Outputs in: {out}')

if __name__ == '__main__':
    main()
