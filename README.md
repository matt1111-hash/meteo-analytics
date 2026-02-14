# Code Health Toolkit v3.1 (Merged Edition)

v2.2 Ruff-alapok + Solo kiegészítések = A legjobb mindkét világból.

## Tartalom

| Forrás | Funkció |
|--------|---------|
| **v2.2** | Ruff (lint+format), Mypy, Bandit, file size check |
| **Solo** | import-linter, radon/xenon, wily trends, vulture, mutmut |

## Setup

```bash
pip install -e ".[dev]"
pre-commit install
detect-secrets scan > .secrets.baseline  # első alkalommal
chmod +x quality_gate.sh
```

## Napi Workflow

```bash
# Munka közben - gyors fix
make check

# Commit előtt - teljes gate
make quality

# Vagy automatikusan
git commit -m "feature"  # pre-commit fut
```

## Parancsok

| Parancs | Leírás |
|---------|--------|
| `make check` | Gyors lint+format |
| `make quality` | Teljes quality gate |
| `make ci` | CI mód (strict thresholds) |
| `make strict` | Strict: MINDEN warning → fail |
| `make test` | Tesztek |
| `make coverage` | Coverage report |
| `make trend` | Wily trendek |
| `make health` | Full health report |
| `make mutation` | Mutation testing |

## Quality Gate Script

```bash
./quality_gate.sh --quick    # Gyors lint
./quality_gate.sh --full     # Teljes (default)
./quality_gate.sh --ci       # CI mód (strict)
./quality_gate.sh --strict   # MINDEN warning → fail
./quality_gate.sh --trend    # Wily trendek
./quality_gate.sh --health   # Full report
```

## Strictness Levels

| Check | Local | CI | Strict |
|-------|-------|----|--------|
| Ruff lint | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| Ruff format | ⚠️ warn | ❌ FAIL | ❌ FAIL |
| Mypy | ⚠️ warn | ❌ FAIL | ❌ FAIL |
| Bandit security | ⚠️ warn | ❌ FAIL | ❌ FAIL |
| Dead code | ⚠️ warn | ⚠️ warn | ❌ FAIL |
| Complexity | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| Architecture | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| File sizes | ❌ FAIL | ❌ FAIL | ❌ FAIL |
| Tests/coverage | ❌ FAIL | ❌ FAIL | ❌ FAIL |

## Thresholds

| Metrika | Local | CI/Strict |
|---------|-------|-----------|
| Coverage | 85% | 90% |
| Max file lines | 300 | 250 |
| Complexity | max B | max B |
| Max args | 5 | 5 |

Testreszabás: `.quality_gate.conf`

## Dynamic Source Detection

A toolkit automatikusan detektálja a forráskönyvtárat: `src/` → `app/` → `lib/` → `.`

A Makefile-ban felülírható: `make lint SRC_DIR=app`

## Clean Architecture

Ha van `src/domain/` könyvtárad, az `.importlinter` kikényszeríti:

```
✅ infrastructure → adapters → application → domain
❌ domain → infrastructure (TILOS)
```

Ha nincs Clean Architecture struktúrád, töröld az `.importlinter` fájlt.

## Fájlok

```
.
├── pyproject.toml          # Minden tool config
├── quality_gate.sh         # Fő script
├── Makefile                # Parancsok
├── .pre-commit-config.yaml # Pre-commit hooks
├── .importlinter           # Architecture rules (törölhető)
├── .quality_gate.conf      # Thresholds
└── .gitignore
```

## v3.1 Changelog

- **FIX**: `detect_src_dir` glob bug (`[ -f "*.py" ]` → `compgen -G`)
- **FIX**: Üres src_dir guard (FATAL early exit)
- **FIX**: Ruff/mypy dependency check (tool guard mint xenon-nál)
- **FIX**: `set -uo pipefail` (undefined variable védelem)
- **FIX**: pyproject.toml D100 select+ignore conflict
- **FIX**: Makefile hardcoded `src/` → dinamikus `SRC_DIR`
- **FIX**: pre-commit ruff verzió szinkron (v0.4.8 → v0.8.6)
- **NEW**: `--strict` mód (minden warning → fail)
- **NEW**: Skipped check counter a summary-ban
- **CHANGE**: CI módban format/security/mypy FAIL (volt: warn)

---

*„A jó kód nem véletlen."*
