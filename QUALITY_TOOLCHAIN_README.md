# Python Quality Toolchain

## Gyors Setup

```bash
# 1. Venv létrehozása
python3 -m venv .venv
source .venv/bin/activate

# 2. Dev dependencies telepítése
pip install -r requirements-dev.txt

# 3. Pre-commit hooks aktiválása
pre-commit install

# 4. Quality gate futtatása
./quality_gate.sh
```

## Tool Összefoglaló

| Tool | Funkció | Target | Parancs |
|------|---------|--------|---------|
| **pytest** | Tesztelés | 100% pass | `pytest tests/ -v` |
| **coverage** | Lefedettség | ≥95% | `pytest --cov=src` |
| **pylint** | Linting | ≥9.0 | `pylint src/` |
| **ruff** | Fast linting + format | 0 error | `ruff check src/` |
| **mypy** | Type checking | 0 error | `mypy src/` |
| **bandit** | Security | 0 high | `bandit -r src/` |
| **black** | Formatting | - | `black src/` |

## Melyiket Használd?

### Minimál (kötelező)
```
pytest + coverage + pylint + mypy
```

### Modern (ajánlott)
```
pytest + coverage + ruff + mypy + bandit + pre-commit
```

### Ruff vs Black/Flake8/isort

**Ruff** egyedül helyettesíti:
- flake8 (linting)
- isort (import sorting)  
- black (formatting) - `ruff format`
- + sok más plugin

**10-100x gyorsabb** mint a hagyományos toolok.

```bash
# Régi módszer (3 tool)
black src/
isort src/
flake8 src/

# Új módszer (1 tool)
ruff check --fix src/
ruff format src/
```

## Fájlok a Projektben

```
projekt/
├── .quality_gate.conf      # Quality gate config
├── quality_gate.sh         # Main script
├── requirements-dev.txt    # Dev dependencies
├── pyproject.toml          # Tool configs (merge pyproject.quality.toml)
├── .pre-commit-config.yaml # Pre-commit hooks
└── AGENTS.md               # AI agent instructions (add QUALITY_GATE_AGENTS.md)
```

## Pre-commit Workflow

```bash
# Telepítés (egyszer)
pre-commit install

# Ezután minden commit-nál automatikusan fut:
# - ruff check + fix
# - ruff format
# - mypy
# - bandit
# - trailing whitespace fix
# - stb.

# Manuális futtatás
pre-commit run --all-files
```

## Gyakori Parancsok

```bash
# Teljes quality check
./quality_gate.sh

# Csak tesztek
pytest tests/ -v

# Coverage report
pytest --cov=src --cov-report=html
open htmlcov/index.html

# Linting (részletes)
pylint src/ --output-format=colorized

# Type check
mypy src/ --ignore-missing-imports

# Format (ruff)
ruff format src/ tests/

# Lint + autofix (ruff)
ruff check --fix src/ tests/

# Security scan
bandit -r src/ -ll

# Complexity check
radon cc src/ -a -s
xenon src/ --max-absolute B --max-modules A --max-average A
```

## Thresholds

| Metric | Minimum | Target |
|--------|---------|--------|
| Coverage | 95% | 98%+ |
| Pylint | 9.0 | 9.5+ |
| Cyclomatic Complexity | ≤10 | ≤5 |
| File size | 250 lines | 150 lines |
| Function size | 50 lines | 20 lines |

## CI/CD Integration

### GitHub Actions
```yaml
- name: Quality Gate
  run: |
    pip install -r requirements-dev.txt
    ./quality_gate.sh --strict
```

### GitLab CI
```yaml
quality:
  script:
    - pip install -r requirements-dev.txt
    - ./quality_gate.sh --strict
```
