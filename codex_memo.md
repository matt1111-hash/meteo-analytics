## Codex Memo – 2025-11-22

### Állapot
- Phase 4 application layer kész: AnalyzeMultiCityUseCase delegáció MultiCityEngine-ben; DetectAnomaliesUseCase bevezetve, GUI anomaly_detector most application→domain hívást használ.
- FastAPI backend létrehozva (`src/api/main.py`, routes/adapters/dto), POST `/api/weather/multi-city` az AnalyzeMultiCityUseCase-re épül, alapértelmezett query_type=windiest_today, region=Global.
- FastAPI szerver fut háttérben port 8001-en (PID 509550), log: `uvicorn.log`.
- React frontend inicializálva `frontend` mappában (CRA TS, axios + recharts), egyszerű hero UI (`Global Weather Analyzer`, “Analyze Weather” gomb). `npm start` lokálisan EPERM miatt nem fut (port bind korlát); próbálva 3000/3001/3002 host=127.0.0.1 – sikertelen.

### Teszt/Quality
- pytest: 92/92 PASS.
- Coverage: ~86% (`--cov=src/application --cov=src/domain`), hiányok főként analyze_multi_city, detect_anomalies, analytics_transform_service, statistics, anomaly_threshold, anomaly_detector.
- Pylint (src/application): 10.00/10 (PYTHONPATH=.).

### Git
- Commitok:
  1) `Phase 4: Application Layer - Pylint 10/10, 90 tests PASS`
  2) `chore: remove pycache artifacts`
  3) `fix: GUI layer violation - DetectAnomaliesUseCase added`
  4) `chore: drop pycache from repo`
  5) `feat(api): add FastAPI entrypoint and weather route`
- Staging tiszta; `.coverage`, `src/analytics/multi_city_engine.py`, `SESSION_MEMORY_2025_11_21_FINAL.md` továbbra is munkaterületen módosult/untracked.

### Futó szolgáltatás
- uvicorn háttérben: `uvicorn src.api.main:app --reload --port 8001` (PID 509550). Leállítás: `kill 509550` vagy `pkill -f "uvicorn src.api.main:app"`.

### Teendők/figyelmeztetések
- Frontend dev szerver indítási hiba (EPERM). Próbáld más port/hosttal vagy jogosultság ellenőrzésével.
- Coverage javítás: application use case ágak, analytics_transform_service, statistics, anomaly_threshold, anomaly_detector.
- `.coverage` és `src/analytics/multi_city_engine.py` diff nincs commitban; döntsd el, kell-e tisztítás.
- API adapter most default query_type/region-t használ; ha explicit régió/query szükséges, adapter/request módosítandó.
