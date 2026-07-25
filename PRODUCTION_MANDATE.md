# PRODUCTION MANDATE
**Version: 2.3 (2026-05-24) | Scope: minden repository és agent**

> v2.2-höz képest: lock/dependency/security elvárások maturity-level szerint pontosítva.

---

## Az egyetlen teszt

> Meg tudod magyarázni, mi fog történni, ha elromlik — és bizonyítani tudod, hogy vissza tudod hozni?

Ha nem: **nem kész.**

---

## Mi a "kész"?

Release decision — nem abszolút állapot. Négy dimenzió egyszerre kell:

- **Üzletileg:** scope elfogadott, kritikus use case-ek működnek, hiányosságok dokumentáltak
- **Technikailag:** reprodukálható build, kritikus hibák zárva, rollback lehetséges
- **Üzemeltetésre:** monitorozható, hibakereshető, incidenskezelési alap megvan
- **Kockázatilag:** maradék hibák ismertek és vállaltak, security minimumok teljesülnek

---

## 26 kötelező kritérium

> **Solo desktop projekt esetén** (egy felhasználó, nincs szerver, git = backup):
> kötelező: **1–7, 13, 17, 20, 22, 26** — a többi N/A, de az agent tudja, miért.

### FUNKCIÓ ÉS MEGBÍZHATÓSÁG
1. ✅ Fő user flow-k végig működnek, edge case-ek kezelve, hibaüzenetek értelmezhetők
2. ✅ Nincs ismert blocker vagy kritikus bug
3. ✅ Graceful degradation: retry, timeout, circuit breaker megvan
4. ✅ Idempotencia ott, ahol kell; concurrency / race condition átnézve

### TESZTELÉS
5. ✅ Kritikus üzleti logika unit-tesztekkel fedett — kritikus ágak lefedése, nem coverage-szám
6. ✅ Integration teszt a határfelületeken, ha van ilyen határ (DB, queue, external API, fájlrendszer)
7. ✅ E2E smoke test launcholható app kritikus flow-ján; script/library esetén N/A indokkal
8. ⚪ Load teszt — N/A solo desktop projektnél

### OBSERVABILITY
9. ⚪ Strukturált logging (JSON), request_id — N/A
10. ⚪ Metrikák: latency, error rate, dashboard — N/A
11. ⚪ Alerting — N/A
12. ⚪ Distributed tracing — N/A

### DEPLOYMENT ÉS OPS
13. ✅ Reprodukálható build: aktív appnál lock file kötelező; egyszerű script/no-dependency/lokális segéd esetén pinned manifest vagy dokumentált install elég, N/A indoklással. CI és Dependabot: ajánlott aktív GitHub remote + dependency surface esetén; release előtt kötelező.
14. ⚪ Rollback stratégia tesztelt — N/A (git history = rollback, lásd GIT_WORKFLOW.md)
15. ⚪ Health check endpoint — N/A
16. ⚪ DB migráció backward compatible — N/A
17. ✅ Konfiguráció kódtól elválasztva, secretek env-ben

### BIZTONSÁG
18. ⚪ Auth/authz — N/A
19. ⚪ Input validáció külső végpontokon — N/A
20. ✅ Secret nem kerül repo-ba — dependency audit ott kell, ahol van dependency surface; gitleaks/pre-commit vagy dokumentált secret scan release előtt kötelező
21. ⚪ Rate limiting, audit log — N/A

### DOKUMENTÁCIÓ
22. ✅ README: lokális futtatás lépései
23. ⚪ API contract — N/A
24. ⚪ ADR-ek — N/A
25. ⚪ Operációs runbook — N/A

### CLEAN ARCHITECTURE
26. ✅ Dependency rule nem sérül: domain framework-agnosztikus, use case-ek csak portokat látnak, ORM model ≠ domain entity, HTTP típusok nem szivárognak use case-be

---

## Tévhitek — tilos ezekre hivatkozni "kész" indoklásaként

| ❌ Tévhit | ✅ Valóság |
|---|---|
| "Clean architecture van → production ready" | A rétegezés és az üzemeltetési érettség ortogonális |
| "Magas coverage → kész" | Coverage metrika, nem garancia |
| "Stagingen megy → production ready" | Stage nem tükrözi a valós komplexitást |
| "Maximális absztrakció = clean arch" | A cél a változások lokalizálása — abstraction theater nem clean arch |
| "Működik nálam → kész" | Mind a négy dimenzió egyszerre kell |
| "AI review zöld → kész" | AI review egy adat, nem garancia. Quality gate kötelező. |

---

## Tiltott gyakorlatok

- Tesztek gyengítése vagy törlése a zöld státusz eléréséhez
- Config fájlok módosítása gate-ek kikerülésére (lásd AGENTS.md: "Config manipuláció gate kikerülésére")
- "Dirty but probably fine" elfogadása
- TODO / placeholder hátrahagyása és "kész" jelzése
- False green elfogadása törött tool detection vagy hiányzó venv miatt
- Vague reporting: "looks fine", "mostly ready", "probably okay" — tilos (lásd HANDOFF.md)

---

## Riportálási standard

**Részletes formátum:** lásd `HANDOFF.md`.

Minimum minden agent-munka végén:

```
- Futtatott parancs: <exact command>
- Eredmény: <exact output>
- Megbízható-e: igen / nem (indok)
- Worktree: clean / dirty
- CI/CD: létezik / hiányzik / passing / failing
- Blokkoló fájlok: <list if any>
```

---

## Hivatkozott fájlok

- **AGENTS.md** — agent szerződés, SZKEA módszer, stack adapterek
- **GIT_WORKFLOW.md** — solo dev git szabályok
- **HANDOFF.md** — záró riport sablon (6 szekció, magyar)

---

## Végső elv

**Production-ready means defensible under scrutiny.**

Ha a standard nem teljesíthető egy menetben: dokumentáld a blokkert, folytasd a következő legnagyobb hatású javítással — a mércét nem csökkented.
