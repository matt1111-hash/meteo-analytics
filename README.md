# Meteo Analytics — Global Weather Analyzer

Multi-city weather analysis desktop application with Clean Architecture.

## Stack

| Layer | Technology |
|-------|------------|
| Backend API | Python 3.12, FastAPI, Pydantic |
| Data sources | Open-Meteo, Meteostat (OMA) |
| Database | SQLite (city database) |
| Frontend SPA | React 19, TypeScript, Recharts, Plotly |
| Desktop GUI | PySide6 |
| Quality tools | Ruff, Mypy, Pytest, ESLint, Vitest, import-linter |

## Quick Start

### Prerequisites

- Python >= 3.12
- Node.js >= 16
- (Optional) `zenity` for desktop launcher error dialogs

### 1. Backend Setup

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Start the API server
python3 -m uvicorn src.api.main:app --port 8003
```

The backend is live at `http://localhost:8003`. API docs: `http://localhost:8003/docs`.

### 2. Frontend Setup

```bash
cd frontend
npm install
npm start
```

The frontend opens at `http://localhost:5174` and proxies API requests to the backend.

### 3. Desktop GUI (PySide6)

```bash
python3 meteo_gui_starter.py
```

Or use the desktop launchers:

```bash
# Full-stack (backend + frontend)
./scripts/launch_meteo_analytics_fullstack.sh

# Frontend only (requires running backend)
./scripts/launch_meteo_analytics_frontend.sh
```

## Project Structure

```
src/
├── domain/          # Entities, ports, value objects (no I/O)
├── application/     # Use cases, DTOs, services
├── infrastructure/  # SQLite repos, DI container, external APIs
├── analytics/       # Weather analysis engines
├── data/            # Data managers, weather client
├── api/             # FastAPI routes, DTOs, auth middleware
├── config/          # Application configuration
└── presentation/    # PySide6 GUI components

frontend/
├── src/
│   ├── pages/       # Route-level page components
│   ├── components/  # Reusable UI components
│   ├── hooks/       # Custom React hooks
│   ├── services/    # API client, service modules
│   └── config/      # Frontend configuration
└── package.json

data/                # SQLite databases (git-tracked)
tests/               # Pytest test suite
```

## Development

### Quality Tools

```bash
# Backend linting
python3 -m ruff check src/

# Backend type checking
python3 -m mypy src/ --ignore-missing-imports

# Run all backend tests
python3 -m pytest tests/ -v

# Run with coverage
python3 -m pytest tests/ --cov=src --cov-report=term-missing

# Clean architecture validation
lint-imports
```

### Frontend

```bash
cd frontend

# Lint
npx eslint src --max-warnings=0

# Type check
npx tsc --noEmit

# Tests
npx vitest run

# Build
npm run build
```

### Full Quality Gate

```bash
./quality_gate.sh          # Local mode
./quality_gate.sh --ci     # CI mode (strict)
```

### Pre-commit Hooks

```bash
pre-commit install
pre-commit run --all-files
```

## API Endpoints (selected)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/api/cities/search?query=...` | City autocomplete |
| POST | `/api/weather/single-city` | Single city time series |
| POST | `/api/weather/single-city-detailed` | Multi-metric single city |
| POST | `/api/weather/multi-city` | Multi-city comparison |
| POST | `/api/weather/anomalies` | Anomaly detection |
| POST | `/api/analytics/trend` | Climate trend analysis |
| POST | `/api/wind-rose/wind-rose` | Wind rose data |
| GET | `/api/weather/metrics` | Available weather metrics |
| GET | `/api/providers/list` | Weather data providers |
| GET | `/api/hungary/counties` | Hungarian counties |

Full API documentation available at `/docs` when the backend is running.

## Testing

| Suite | Command | Count |
|-------|---------|-------|
| Backend unit/integration | `python3 -m pytest tests/ -v` | ~1595 tests |
| E2E smoke tests | `python3 -m pytest tests/e2e/ -v` | 11 tests |
| Frontend | `cd frontend && npx vitest run` | 342 tests |

## Configuration

| File | Purpose |
|------|---------|
| `pyproject.toml` | Python tool config (Ruff, Mypy, Pytest, Coverage) |
| `frontend/package.json` | Frontend dependencies, proxy config |
| `.importlinter` | Clean Architecture layer rules |
| `.pre-commit-config.yaml` | Pre-commit hooks |
| `quality_gate.sh` | Full quality gate script |
| `.env` | Environment variables (not tracked) |
| `frontend/src/config/apiConfig.ts` | API base URL config |
