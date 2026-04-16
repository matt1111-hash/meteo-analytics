# Security Audit Report (AppSec / SAST)

**Repository:** `meteo-analytics`
**Audit date:** 2026-04-15 (UTC)
**Method:** targeted static code review + dependency audit attempts (`pip-audit`, `npm audit`)

---

## Executive Summary

The codebase has a generally good baseline in backend API-key checks and parameterized SQL for most repository/database access paths. The most notable risk is a GUI SQL worker that executes raw SQL strings with a weak keyword blacklist, which can be bypassed and enables arbitrary SQL reads and potentially state-changing operations in edge cases.

Additional medium-risk issues include:
- authentication being **optional** by environment (`API_KEY_ENABLED = bool(API_KEY)`),
- frontend design that encourages embedding an API key into client-side JavaScript,
- verbose SQL error logging that may expose query content and sensitive runtime context,
- plaintext local persistence of user settings/usage data without at-rest protection.

Dependency CVE verification could not be completed from this environment due package-advisory endpoint restrictions.

---

## Findings by Requested Focus Area

## 1) Input validation és injection

### 1.1 Raw SQL execution via user-supplied query (weak blacklist)
- **Severity:** **MAGAS**
- **CWE:** CWE-89 (SQL Injection), CWE-20 (Improper Input Validation)
- **Evidence:** `SQLQueryWorker` executes `worker.query` directly via `pandas.read_sql_query(query, conn)` and fallback `cursor.execute(query)`, while only checking a keyword blacklist (`DROP`, `DELETE`, `INSERT`, `UPDATE`, `ALTER`, `CREATE`). This pattern is bypass-prone (comments/obfuscation/other mutating statements, pragma misuse, etc.).
  - `src/presentation/gui/workers/sql_query_worker.py:25-31,35-44,66-73,118-123`.
- **Remediation:**
  1. Replace free-form SQL with a strict allowlist of pre-defined query templates.
  2. If ad-hoc querying must remain, parse SQL AST and allow only single `SELECT` statements.
  3. Open DB in read-only mode (`sqlite3.connect("file:path?mode=ro", uri=True)`) for this worker.
  4. Remove fallback raw execution path and enforce parameter binding for user-provided values.

### 1.2 Dynamic SQL composition with interpolated `LIMIT`
- **Severity:** **KÖZEPES**
- **CWE:** CWE-89
- **Evidence:** SQL strings in city search paths append `LIMIT` via f-string, then execute dynamically. Current call sites use typed integer params, but there is no hard cap or explicit integer coercion at query boundary.
  - `src/data/city_manager_search.py:156,184,207,223` and execution sink in `src/data/city_manager_db.py:163-176`.
- **Remediation:**
  1. Parameterize `LIMIT` where possible (`LIMIT ?`) and pass validated ints.
  2. Add central validator: `limit = max(1, min(int(limit), MAX_LIMIT))`.
  3. Reject non-int values at API/domain boundary before repository calls.

### 1.3 Command injection / eval / exec
- **Severity:** **ALACSONY** (no direct sink found)
- **CWE:** CWE-78 / CWE-94 (not observed)
- **Evidence:** No `subprocess`/`shell=True`/`eval`/`exec` usage found under `src/` in this audit pass.
- **Remediation:** Keep policy in CI (Bandit/Semgrep rules) to fail on introducing such sinks.

### 1.4 Path traversal possibilities
- **Severity:** **ALACSONY-KÖZEPES**
- **CWE:** CWE-22
- **Evidence:** Runtime path can be influenced by `WEATHER_ANALYZER_DATA_DIR` and then used to resolve DB files. Existence is checked, but canonical path/root restriction is not enforced.
  - `src/infrastructure/repositories/city_repository_paths.py:22-29,44-54`.
- **Remediation:**
  1. Canonicalize (`resolve(strict=True)`) and enforce trusted base directory allowlist.
  2. Disallow symlink traversal outside approved roots.
  3. Add startup warning/fail-fast for non-whitelisted DB locations in production mode.

### 1.5 Template injection
- **Severity:** **ALACSONY** (no server-side template engine sink observed)
- **CWE:** CWE-1336 (not observed)
- **Evidence:** No Jinja2/template rendering path identified in audited server code.
- **Remediation:** Maintain deny-by-default for server template rendering, sanitize any future dynamic template features.

---

## 2) Hitelesítés és authorizáció

### 2.1 Authentication is optional by configuration
- **Severity:** **MAGAS**
- **CWE:** CWE-306 (Missing Authentication for Critical Function)
- **Evidence:** Backend allows all non-public endpoints when `API_KEY` is unset (`API_KEY_ENABLED=False`).
  - `src/config/api_config.py:26-27`
  - `src/api/main.py:85-87`
- **Risk context:** Production misconfiguration (empty API key) disables auth globally.
- **Remediation:**
  1. Add mandatory production guard (`ENV=prod` requires non-empty strong API_KEY).
  2. Fail application startup if production auth prerequisites are not met.
  3. Prefer scoped JWT/OAuth2 over single shared API key.

### 2.2 Client-side API key exposure pattern
- **Severity:** **MAGAS**
- **CWE:** CWE-798 (Use of Hard-coded Credentials) / CWE-522 (Insufficiently Protected Credentials)
- **Evidence:** Frontend reads `VITE_API_KEY` and sends it from browser headers. Any Vite env variable shipped client-side is inspectable by users.
  - `frontend/src/config/apiConfig.ts:19-21,34-36,44-47`
- **Remediation:**
  1. Do not place privileged API keys in browser bundles.
  2. Use backend-for-frontend/session auth; keep upstream secrets server-side only.
  3. Rotate existing keys if this pattern has been used in real environments.

### 2.3 Authorization granularity / RBAC
- **Severity:** **KÖZEPES**
- **CWE:** CWE-862 (Missing Authorization)
- **Evidence:** Single global API key gate is applied, but no role/scope checks per endpoint.
  - `src/api/main.py:74-108,126-135`
- **Remediation:** Introduce claims/scopes (read-only analytics vs. admin/provider config changes), and enforce per-route authorization dependencies.

### 2.4 Hardcoded credentials
- **Severity:** **ALACSONY**
- **CWE:** CWE-798
- **Evidence:** `.env.example` contains placeholders only; no real key observed.
  - `.env.example:1-5`
- **Remediation:** Continue using placeholders; enforce secret scanning in CI pre-merge.

---

## 3) Adatkezelés

### 3.1 Sensitive data in logs (SQL text leakage)
- **Severity:** **KÖZEPES**
- **CWE:** CWE-532 (Insertion of Sensitive Information into Log File)
- **Evidence:** On DB exceptions, entire SQL query is logged (`SQL query error: {sql}`). If query contains user-originated strings, logs can leak sensitive data or operational details.
  - `src/data/city_manager_db.py:189-191`
- **Remediation:**
  1. Log query identifiers/templates, not full SQL text.
  2. Redact literals before logging.
  3. Separate debug logs from production logs and enforce retention controls.

### 3.2 Plaintext local storage of preferences/usage/settings
- **Severity:** **KÖZEPES**
- **CWE:** CWE-312 (Cleartext Storage of Sensitive Information)
- **Evidence:** JSON settings and usage files are written without encryption or explicit file mode hardening.
  - `src/data/anomaly_storage.py:93-94,141-143,160-164`
  - `src/config/provider_config_part2.py:65-66`
  - `src/config/usage_config_part2.py:77-78`
- **Remediation:**
  1. Store sensitive values in OS keychain/secret store.
  2. Set restrictive permissions (`0o600`) for local files.
  3. Encrypt at rest where threat model includes local compromise.

### 3.3 Insecure deserialization
- **Severity:** **ALACSONY** (not observed)
- **CWE:** CWE-502
- **Evidence:** JSON parsing is used; no unsafe pickle/yaml object deserialization sink identified in audited files.
- **Remediation:** Keep forbidding `pickle.loads` and unsafe `yaml.load` in CI rules.

---

## 4) Függőség-biztonság

### 4.1 Known CVEs by exact versions — verification blocked in environment
- **Severity:** **KÖZEPES** (process risk)
- **Evidence:** Dependency manifests are present and pinned for Python/frontend.
  - `requirements.txt:1-22`
  - `frontend/package.json:6-25,68-75`
- **Audit limitation:**
  - `python -m pip_audit -r requirements.txt` failed (`No module named pip_audit`), and install failed due proxy/403.
  - `npm audit --omit=dev --json` failed with `403 Forbidden` from npm advisory endpoint.
- **Remediation:**
  1. Run `pip-audit` and `npm audit` in CI with unrestricted advisory DB access.
  2. Export SBOM (CycloneDX) and gate merges on critical/high vulnerabilities.

### 4.2 Dev/test packages in production Python requirements
- **Severity:** **KÖZEPES**
- **CWE:** CWE-1104 (Use of Unmaintained/Unnecessary Third Party Components)
- **Evidence:** `requirements.txt` includes test tooling (`pytest`, `pytest-*`) suggesting potential overbroad production install surface.
  - `requirements.txt:17-21`
- **Remediation:** Split runtime and dev requirements strictly; ensure deployment only installs runtime lock.

### 4.3 Typosquatting suspicion candidate
- **Severity:** **ALACSONY**
- **CWE:** CWE-1104 (supply-chain hardening context)
- **Evidence:** `PyQtDarkTheme2` is a less common package name that warrants provenance verification.
  - `requirements.txt:6`
- **Remediation:** Verify maintainer/source integrity (hash pinning, trusted index, provenance checks), and add hash-locked requirements.

---

## 5) Konfiguráció és infrastruktúra

### 5.1 CORS configuration can become overly broad if env mis-set
- **Severity:** **KÖZEPES**
- **CWE:** CWE-942 (Permissive Cross-domain Policy)
- **Evidence:** CORS origins are env-driven and credentials are enabled. If operators set broad origins, credentialed cross-origin exposure risk increases.
  - `src/config/api_config.py:30-34`
  - `src/api/main.py:32-38`
- **Remediation:**
  1. Enforce strict allowlist validation (no wildcard with credentials).
  2. Add startup validation rejecting insecure CORS combos.

### 5.2 Exposed admin endpoints
- **Severity:** **ALACSONY** (no dedicated `/admin` endpoint observed)
- **Evidence:** No obvious admin route namespace found in audited API router registrations.
  - `src/api/main.py:126-135`
- **Remediation:** Keep admin features isolated and separately authenticated if introduced.

### 5.3 Debug mode in production code
- **Severity:** **ALACSONY-KÖZEPES**
- **CWE:** CWE-489 (Active Debug Code)
- **Evidence:** `print` debug traces in SQL worker cancellation path.
  - `src/presentation/gui/workers/sql_query_worker.py:56,81`
- **Remediation:** Replace prints with structured logger at debug level and disable verbose debug output in production profiles.

---

## Recommended Priority Fix Plan

1. **Immediate (P0):** Lock down raw SQL worker to read-only + SELECT-only allowlist.
2. **Immediate (P0):** Enforce mandatory auth in production startup.
3. **Immediate (P1):** Remove browser-side API key model; move to server-side/session-based auth.
4. **Near term (P1):** Redact SQL from logs; implement sensitive log policy.
5. **Near term (P1):** Separate runtime/dev dependencies and enable advisory scans in CI.
6. **Near term (P2):** Harden file permissions and optional encryption for local persisted data.
7. **Near term (P2):** Validate CORS settings strictly at startup.

---

## Audit Commands Executed

- `rg -n "(execute\(|executemany\(|subprocess|shell=True|eval\(|exec\(|pickle\.loads|yaml\.load\(|jinja2|Template\(|open\(|Path\(|send_file|CORS|debug=|SECRET|API_KEY|token|password|passwd|Authorization|os\.system|sqlite3|f-string|format\()" src tests frontend -g '!*.min.*'`
- `rg -n "_execute_query\(|cursor.execute\(|read_sql_query\(|f\"SELECT|LIKE \{|ORDER BY \{|shell=True|subprocess\.|eval\(|exec\(|pickle\.loads|yaml\.load\(" src`
- `python -m pip_audit -r requirements.txt` (failed: module unavailable)
- `python -m pip install pip-audit -q` (failed: package index/network restriction)
- `cd frontend && npm audit --omit=dev --json` (failed: npm advisory endpoint 403)
