#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools_archi_scan.py
Statikus architektúra-szkenner Python projektekhez.
Kimenet: Markdown összefoglaló, JSON index, DOT import gráf, hotspot lista.
"""

import ast
import argparse
import json
import os
from pathlib import Path
from typing import Dict, List, Tuple, Set
from collections import defaultdict, Counter

IGNORES_DEFAULT = {
    "__pycache__", ".git", "venv", ".env", ".mypy_cache",
    ".pytype", "build", "dist", "node_modules", ".ipynb_checkpoints"
}

def load_ignores(ignore_file: Path) -> Set[str]:
    ignores = set(IGNORES_DEFAULT)
    if ignore_file and ignore_file.exists():
        for line in ignore_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                ignores.add(line)
    return ignores

def iter_py_files(root: Path, ignores: Set[str]) -> List[Path]:
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        dp = Path(dirpath)
        # szűrés
        dirnames[:] = [d for d in dirnames if d not in ignores]
        for f in filenames:
            if f.endswith(".py"):
                p = dp / f
                # soros exclusion: ha valamelyik ignore részsztring a relatív path-ban
                rel = p.relative_to(root)
                if any(part in ignores for part in rel.parts):
                    continue
                files.append(p)
    return files

class ModuleInfo(ast.NodeVisitor):
    def __init__(self, module_name: str, rel_path: str):
        self.module_name = module_name
        self.rel_path = rel_path
        self.imports: Set[str] = set()
        self.from_imports: Set[str] = set()
        self.classes: Dict[str, Dict] = {}
        self.functions: Dict[str, Dict] = {}
        self.calls: Counter = Counter()  # heurisztikus: milyen neveket hívnak
        self.top_level_assigns: List[str] = []

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            self.imports.add(alias.name.split('.')[0])

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module:
            self.from_imports.add(node.module.split('.')[0])

    def visit_Assign(self, node: ast.Assign):
        # csak top-level assignment nevek
        if isinstance(node.parent, ast.Module):
            names = []
            for t in node.targets:
                if isinstance(t, ast.Name):
                    names.append(t.id)
                elif isinstance(t, ast.Tuple):
                    for e in t.elts:
                        if isinstance(e, ast.Name):
                            names.append(e.id)
            if names:
                self.top_level_assigns.extend(names)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        # heurisztikus hívásnév: foo(), mod.func(), Class.method()
        name = None
        if isinstance(node.func, ast.Name):
            name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            # megpróbáljuk a legutolsó tagot kivenni
            name = node.func.attr
        if name:
            self.calls[name] += 1
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        doc = ast.get_docstring(node) or ""
        args = [a.arg for a in node.args.args]
        self.functions[node.name] = {
            "args": args,
            "lineno": node.lineno,
            "doc": doc[:200].replace("\n", " ")
        }
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        doc = ast.get_docstring(node) or ""
        args = [a.arg for a in node.args.args]
        self.functions[node.name] = {
            "args": args,
            "lineno": node.lineno,
            "doc": doc[:200].replace("\n", " "),
            "async": True
        }
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef):
        bases = []
        for b in node.bases:
            if isinstance(b, ast.Name):
                bases.append(b.id)
            elif isinstance(b, ast.Attribute):
                bases.append(b.attr)
        methods = []
        for body in node.body:
            if isinstance(body, (ast.FunctionDef, ast.AsyncFunctionDef)):
                methods.append(body.name)
        doc = ast.get_docstring(node) or ""
        self.classes[node.name] = {
            "bases": bases,
            "methods": methods,
            "lineno": node.lineno,
            "doc": doc[:200].replace("\n", " ")
        }
        self.generic_visit(node)

def parse_module(root: Path, file: Path) -> ModuleInfo:
    rel_path = file.relative_to(root).as_posix()
    module_name = rel_path[:-3].replace("/", ".")  # egyszerű mappanév->modul
    code = file.read_text(encoding="utf-8", errors="ignore")
    try:
        tree = ast.parse(code)
    except SyntaxError:
        # szintaxis hibás fájlok: minimal index
        mi = ModuleInfo(module_name, rel_path)
        return mi

    # szülő referenciák a top-level assign felismeréshez
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            child.parent = node

    mi = ModuleInfo(module_name, rel_path)
    mi.visit(tree)
    return mi

def build_import_graph(modules: Dict[str, ModuleInfo]) -> Dict[str, Set[str]]:
    graph = defaultdict(set)
    module_names = set(modules.keys())
    for m, info in modules.items():
        for imp in (info.imports | info.from_imports):
            # csak belső modul él, ha név egyezik valamelyik modul prefixével
            for candidate in module_names:
                if candidate.split(".")[0] == imp:
                    graph[m].add(candidate)
    return graph

def guess_hotspots(files_info: Dict[str, Dict], top_n: int = 10) -> List[Tuple[str, int]]:
    sizes = [(m, d["lines"]) for m, d in files_info.items()]
    sizes.sort(key=lambda x: x[1], reverse=True)
    return sizes[:top_n]

def write_dot(graph: Dict[str, Set[str]], out_dot: Path):
    lines = ["digraph imports {", '  rankdir=LR;']
    for src, dsts in graph.items():
        for dst in dsts:
            lines.append(f'  "{src}" -> "{dst}";')
    lines.append("}")
    out_dot.write_text("\n".join(lines), encoding="utf-8")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, help="Kódgyökér (pl. src)")
    ap.add_argument("--ignore-file", default="", help="Ignore fájl útvonala")
    ap.add_argument("--out-dir", default="analysis_out/archi", help="Kimeneti könyvtár")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    ignores = load_ignores(Path(args.ignore_file)) if args.ignore_file else IGNORES_DEFAULT

    py_files = iter_py_files(root, ignores)
    modules: Dict[str, ModuleInfo] = {}
    files_info: Dict[str, Dict] = {}

    for pf in py_files:
        rel = pf.relative_to(root).as_posix()
        code = pf.read_text(encoding="utf-8", errors="ignore")
        lines = code.count("\n") + 1
        mi = parse_module(root, pf)
        modules[mi.module_name] = mi
        files_info[mi.module_name] = {
            "rel_path": rel,
            "lines": lines
        }

    graph = build_import_graph(modules)

    # JSON index
    index = {
        "root": str(root),
        "files": files_info,
        "modules": {
            m: {
                "rel_path": info.rel_path,
                "imports": sorted(info.imports),
                "from_imports": sorted(info.from_imports),
                "classes": info.classes,
                "functions": info.functions,
                "top_calls": info.calls.most_common(20),
                "top_level_assigns": info.top_level_assigns
            }
            for m, info in modules.items()
        },
        "import_graph": {k: sorted(list(v)) for k, v in graph.items()}
    }
    (out_dir / "arch_index.json").write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8")

    # DOT
    write_dot(graph, out_dir / "import_graph.dot")

    # Hotspots (nagy fájlok)
    hotspots = guess_hotspots(files_info, top_n=15)
    (out_dir / "hotspots.txt").write_text(
        "\n".join([f"{size:>7}  {mod}" for mod, size in hotspots]), encoding="utf-8"
    )

    # Markdown összegzés – ezt etesd be elsőnek a 4.1-nek
    md_lines = []
    md_lines.append(f"# Architektúra áttekintés – {root.name}\n")
    md_lines.append("## Cél\n"
                    "- Modulok közötti kapcsolatok és fő felelősségek megértése\n"
                    "- God modulok/forró pontok azonosítása\n"
                    "- Refaktor irányok előkészítése 4.1 elemzéshez\n")
    md_lines.append("## Összegzés\n")
    md_lines.append(f"- Fájlok száma: **{len(py_files)}**\n")
    md_lines.append("- Lásd még: `arch_index.json`, `import_graph.dot`/PNG, `hotspots.txt`\n")
    md_lines.append("## Top 10 import-hub (leginkább importáló modulok)\n")

    # import-hub heurisztika: bejövő él-szám
    indeg = Counter()
    for src, dsts in graph.items():
        for d in dsts:
            indeg[d] += 1
    for mod, deg in indeg.most_common(10):
        md_lines.append(f"- {mod}  (bejövő importok: {deg})")
    md_lines.append("\n## Hotspots (legnagyobb fájlok)\n")
    for mod, size in hotspots:
        md_lines.append(f"- {mod}  ~{size} sor")

    md_lines.append("\n## Modulrészletek (rövid)\n")
    for m, info in sorted(modules.items()):
        md_lines.append(f"### {m}\n")
        md_lines.append(f"- Fájl: `{info.rel_path}`")
        if info.imports or info.from_imports:
            imps = sorted(info.imports | info.from_imports)
            md_lines.append(f"- Importál: {', '.join(imps[:10])}" + (" ..." if len(imps) > 10 else ""))
        if info.classes:
            md_lines.append(f"- Osztályok: {', '.join(sorted(info.classes.keys())[:8])}" + (" ..." if len(info.classes)>8 else ""))
        if info.functions:
            md_lines.append(f"- Függvények: {', '.join(sorted(info.functions.keys())[:8])}" + (" ..." if len(info.functions)>8 else ""))
        if info.calls:
            topc = ", ".join([f"{n}({c})" for n,c in info.calls.most_common(5)])
            md_lines.append(f"- Gyakori hívások: {topc}")
        md_lines.append("")

    (out_dir / "arch_summary.md").write_text("\n".join(md_lines), encoding="utf-8")

    print(f"[OK] Kimenet: {out_dir}")
    print(" - arch_summary.md")
    print(" - arch_index.json")
    print(" - import_graph.dot (-> PNG-hez: dot -Tpng ...)")
    print(" - hotspots.txt")

if __name__ == "__main__":
    main()

