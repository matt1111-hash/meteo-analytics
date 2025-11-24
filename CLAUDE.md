# CLAUDE - Global Weather Analyzer Frontend Development

## HAROLD WORKFLOW - KRITIKUS! 🎯
1. **Webes Claude (TE):** Architecture + Codex instructions
2. **Gépi Claude (computer use - TE):** Debug, inspect files, terminal commands
3. **Codex (PIHEN):** Code writing execution
4. **Harold:** CSAK visual feedback, ZERO manual coding!

## PROJECT PHASE - WEB TRANSITION 🚀
Desktop (Qt/PySide6) → Web (FastAPI + React TypeScript)

**Backend:** FastAPI Python
- Port: 8001 ✅ RUNNING (PID 509550)
- Endpoint: POST /api/weather/multi-city
- Clean Architecture: Domain layer REUSABLE

**Frontend:** React 18 + TypeScript
- Port: 3000 ⚠️ RUNNING but 500 ERROR
- Updated: App.tsx, App.css (Codex session)
- Libs: axios, recharts

## CURRENT PROBLEM 🔴
**500 Internal Error** on localhost:3000

**Need:**
1. Browser console log (F12 → Console)
2. Frontend terminal errors
3. Inspect App.tsx/App.css content

## DIRECTORY STRUCTURE
```
frontend/
├── src/
│   ├── App.tsx         # Main component (Codex updated)
│   ├── App.css         # Blue gradient, hero card
│   ├── index.tsx
│   └── ...
├── package.json
└── tsconfig.json
```

## QUALITY GATES (Backend)
- ✅ Tests: 92/92 PASS
- ✅ Coverage: 86%
- ✅ Pylint: 10.00/10
- ✅ Layer Violations: 0

## SERVICES RUNNING
```bash
# Backend
uvicorn src.api.main:app --reload --port 8001  # PID 509550

# Frontend
cd frontend && npm start  # Port 3000
```

## NEXT STEPS
1. **DEBUG 500 error** (gépi Claude inspects App.tsx)
2. Fix syntax/import issues
3. Verify hot reload works
4. Build weather analysis form component

## GIT STATUS
- Last commit: FastAPI entrypoint
- Unstaged: .coverage, SESSION_MEMORY files

## HAROLD PREFERENCES
- Simple text editor (gedit)
- Immediate visual feedback (hot reload)
- NO IDE, NO manual coding
- Codex writes, Harold sees results
