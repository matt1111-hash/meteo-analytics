# Claude Code CLI feladat: Jules AGENTS.md deploy

## Feladat

Az alábbi 7 GitHub repóban csináld meg a következőt:

1. `git clone` (ha nincs lokálisan) vagy `git pull` (ha van)
2. Ha létezik `AGENTS.md` a gyökérben → nevezd át `AGENTS_cli.md`-re
3. Hozd létre az új `AGENTS.md`-t az alábbi SABLON alapján
4. A "Project Context" szekciót írd át repónként — nézd meg a README.md-t vagy a fő forrásfájlokat
5. Az "Environment Setup" szekciót is igazítsd ha van speciális setup (pl. `.env`, CUDA, PySide6)
6. `git add AGENTS.md AGENTS_cli.md && git commit -m "Add Jules AGENTS.md, rename CLI version" && git push`

## Repók:

1. matt1111-hash/health_explorer
2. matt1111-hash/Wiseprofi
3. matt1111-hash/wiseprofi-rtx3050-benchmark
4. matt1111-hash/energia_monitoring
5. matt1111-hash/weather_energy_analyzer
6. matt1111-hash/meteo-analytics
7. matt1111-hash/budget

## SABLON (AGENTS.md — Jules Edition):

```markdown
# AGENTS.md — Jules (Google AI) Edition
**Version: 1.0 (2026-02-13)**
**Based on: AI CODING RULES v2.4**

---

## Project Context

<!-- ⚠️ IDE ÍRD A PROJEKT LEÍRÁSÁT — 2-3 mondat -->

---

## Architecture

src/
├── domain/          # Entities, repository interfaces (NO I/O!)
├── application/     # Use cases, services
├── infrastructure/  # SQLite, APIs, external services
└── presentation/    # CLI, GUI (PySide6)

tests/
└── test_*.py        # Mirror src/ structure

**Rules:**
- Dependencies point INWARD only
- Domain NEVER imports infrastructure
- One file = one responsibility
- Max 300 lines per file, max 200 lines per class, max 50 lines per function
- Cyclomatic complexity < 8, nesting depth ≤ 3

---

## Coding Standards

**Type hints:** Required on ALL functions — parameters AND return types.
**Docstrings:** Required on all public functions — brief, 1-2 lines.
**Imports:** Alphabetical order: stdlib → third-party → internal. Use relative imports within packages.
**Naming:** Hungarian variable/function names in domain layer are acceptable.

**FORBIDDEN:**
- `eval()`, `exec()`, `os.system()` — security risk
- f-string SQL queries — use parameterized queries only
- Hardcoded API keys or passwords — use environment variables
- Placeholder code: `# TODO`, `// FIXME`, `pass` in production code
- God classes over 300 lines

---

## Quality Gate

**These thresholds MUST be met before any PR:**

| Metric | Threshold |
|--------|-----------|
| Test coverage | ≥ 85% |
| Max lines per file | 300 |
| Ruff errors | 0 |
| Mypy | Pass (ignore-missing-imports) |

**Validation commands (run in this order):**
```
python -m ruff check src/
python -m ruff format --check src/
python -m mypy src/ --ignore-missing-imports
python -m pytest tests/ -v --cov=src --cov-report=term-missing
```

If any check fails, fix the issues before completing the task.

---

## Testing Rules

- Tests are MANDATORY — no exceptions
- One test = one behavior (Arrange-Act-Assert)
- Test file mirrors source: `src/domain/foo.py` → `tests/test_foo.py`
- Mock external dependencies (APIs, databases, file system)
- Test edge cases and error paths
- NEVER modify existing tests — tests define the specification
- NEVER modify quality gate config files (`quality_gate.sh`, `pyproject.toml`, `.quality_gate.conf`)

---

## Security

- SQL: parameterized queries ONLY (`cursor.execute("... WHERE id = ?", (id,))`)
- Secrets: environment variables ONLY, never hardcode
- No `eval/exec/os.system`

---

## Task Execution Guidelines

When Jules receives a task:

1. **Understand scope** — read related files before making changes
2. **Minimal changes** — only modify what the task requires
3. **Complete files** — never truncate, never use `...` or "rest unchanged"
4. **Run quality checks** — execute the validation commands above
5. **Fix what you break** — if changes cause test failures, fix them (without modifying existing tests)

**If a task is ambiguous or too large:**
- Implement the clearest interpretation
- Note assumptions in the PR description
- Prefer smaller, focused changes over sweeping refactors

---

## Environment Setup

```
python -m pip install -r requirements.txt
python -m pip install ruff pytest pytest-cov mypy
```

<!-- ⚠️ Egyedi setup ide -->
```

## FONTOS SZABÁLYOK:

- Ha a repóban NINCS `src/` struktúra, igazítsd az Architecture szekciót a tényleges struktúrához
- Ha NINCS `requirements.txt`, nézd meg mi van (`setup.py`, `pyproject.toml`, `Pipfile`) és írd át az Environment Setup-ot
- Ha a repó NEM Python (pl. blackjack ha JS lenne), igazítsd a toolchain-t
- NE változtass semmilyen forráskódot — CSAK az AGENTS.md fájlokkal dolgozz!
- Minden repóra külön commit
