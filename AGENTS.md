# AGENTS.md — Jules (Google AI) Edition
**Version: 1.0 (2026-02-13)**
**Based on: AI CODING RULES v2.4**

---

## Project Context

Meteo Analytics — Időjárási adatok elemzése és vizualizálása Clean Architecture alapokon. PySide6 GUI, OpenMeteo és Meteostat API integráció, trend analízis, anomália detektálás, szél analytics és hőmérséklet grafikonok.

---

## Architecture

src/
├── domain/           # Entities, value objects, repository interfaces (NO I/O!)
│   ├── analytics/    # Analytics services, statistics
│   ├── entities/     # Domain entities
│   └── services/     # Domain services (anomaly detection)
├── application/      # Use cases
│   └── use_cases/    # Application business logic
├── infrastructure/   # External services, repositories
│   └── repositories/ # Data access implementations
├── data/             # Weather providers, clients
│   ├── openmeteo_provider.py
│   └── meteostat_provider.py
├── presentation/     # GUI layer
│   └── gui/          # PySide6 components, charts, widgets
├── config/           # Configuration management
└── api/              # REST API routes

tests/
└── test_*.py         # Mirror src/ structure

**Rules:**
- Dependencies point INWARD only (domain ← application ← infrastructure/presentation)
- Domain NEVER imports infrastructure or presentation
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
- Test file mirrors source: `src/domain/foo.py` → `tests/domain/test_foo.py`
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

```bash
pip install -r requirements.txt
pip install ruff pytest pytest-cov mypy
```

---

## Repo-specific notes

- Clean Architecture — szigorú dependency rule
- PySide6 GUI — QThread workers a háttérfolyamatokhoz
- OpenMeteo API (ingyenes) és Meteostat API
- Chart rendering: matplotlib + PySide6 integration
- `.env` fájl az API kulcsokhoz
