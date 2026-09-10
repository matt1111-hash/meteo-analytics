# 08 — SA-döntések rögzítése és a repair plan lezárása

**RUN_ID:** `20260910T092914Z` · **Dátum:** 2026-09-10 · **Szignó:** emberi „mehet" a 06/07 HANDOFF következő-lépés listájára

Ez a dokumentum rögzíti a `06_REPAIR_PLAN.md` §5 `SPEC_AMBIGUITY` tételeinek sorsát.
A „konzervatív" feloldás itt azt jelenti: **a megfigyelt viselkedés igazoltan áll, de
változtatására nincs igény és nincs sérülő szerződés** — a döntés a status quo
mellett, explicit indoklással. Bármelyik visszavonható, ha igény jelentkezik.

## 1. Végrehajtva (kód/adat változott)

| Tétel | Döntés | Commit |
|---|---|---|
| SA-1 | **B**: árva sorok archiválása (CSV + bájthű backup) és törlése az élő DB-n; **C**: `PRAGMA foreign_keys = ON` minden `DatabaseManager`-kapcsolaton | B: `359ef05`/`8c0e18a`; C: `15c42cc` |
| SA-2 | Részleges mentés (`0 < saved < N`) = **siker** (`True`); a zéró eset RT-3 óta `False` | `b152aa5` (docstring) |
| SA-9 | Az API-kulcs auth réteg **törlése** a HEAD-en (loopback-only launcherek, frontend nem küld kulcsot, crit 18 solo desktop N/A); visszaállítás: `git revert 34d6474` | `34d6474` |
| SA-10 | `.secrets.baseline` **tracked + review-olt** politika (ki a gitignore-ból); agent-tool állapot ignore-olva | `56c8900` |

## 2. Konzervatívan feloldva (nincs kódváltozás)

| Tétel | Döntés | Indok |
|---|---|---|
| SA-4 | Az API-fetch továbbra is a **use-case mapping** szerint választ providert; a `POST /providers/{id}/select` a GUI prefs-t perzisztálja | A prefs `WeatherClient`-be kötése a bizonyított `RecursionError`-csapdával (H1: `preferred_provider="meteostat"` + `_select_provider(None)`) nem atomi; solo desktopon nincs igény az újrakötésre |
| SA-5 | Vegyes hibajelentés marad: 502 a `raise_for_use_case_result`-ot használó route-okon, 200 + explicit hibamező a többin | Mindkét viselkedést meglévő tesztek rögzítik; egységesítés = API-szerződés-törés frontenden, igény nélkül |
| SA-6 | A usage/status végpont **placeholder** marad (default nullák) | A GET mezői nem ígérik a fedett adatot; a GUI `UsageTracker`-e eltérő rendszer — bekötésük feature-munka |
| SA-7 | A két városfeloldó-változat (repo exact-IN vs manager koordináta) **szándékosan párhuzamos** marad | Nincs közös feloldó-spec; mindkettő működik a maga hívóján; egységesítés viselkedésváltozás lenne tesztekkel rögzített végpontokon |
| SA-8 | A `/health` **liveness** marad (`{"status":"ok"}`, teszt rögzíti); olvasó/retenció a `weather_data`-re **nem épül** | Post SA-1 B/C a tábla tiszta és FK-védett; retenciós spec értelmét csak egy jövőbeli olvasó adja meg |
| SA-11 | A provider-prefs RMW-ablakára **nem** kerül folyamat-szintű lock | Asztali, egyfelhasználós kontextus; last-write-wins elfogadott; az írás maga atomi (`atomic_write_json`) |
| SA-12 | Trend-CPU költségvetés **nem rögzített** → a vektorizálás nem kötelező | Helyes eredmény lassan is spec-kompatibilis; a P-02/Q-01 vektorizálás a §7 backlogban marad |

## 3. Elvetett / elhalasztott javaslatok

- **`data/meteo_data.db` untrackelése — ELVETVE.** A `src/`-ben nincs séma-auto-create
  (csak a settlements dump SQL-ben van `CREATE TABLE`), a tesztek nem hivatkoznak a
  fájlra — tehát a tracked DB a **friss clone seed- és backup-csatornája** (a GitHub a
  DB egyetlen mentési helye). Untrack előtt séma-inicializáló kód kellene; a mellékhatás
  (minden GUI-mentés dirty worktree) ismert és viselt.
- **§7 karbantartási lista (L-05, L-09, L-11, P-02…P-05, Q-01…Q-10)** — **backlog**
  marad, a terv szándéka szerint nem a hibajavítási sorban. Legjobb első jelöltek:
  Q-03 (11 árnyékolt `.py` törlése, 0 runtime-hatás) és P-05 (injektálható sleep,
  ~26 s CI-megtakarítás).

## 4. Állapot a lezáráskor

- `main` tiszta worktree; a teljes `20260910T092914Z` terv: RT-1…RT-3, NE-1, SA-3,
  SA-1 (B+C), SA-2, SA-9, SA-10 **kész**; SA-4…SA-8, SA-11, SA-12 **rögzített
  konzervatív döntéssel** zárva; §7 backlog.
- Élő DB: 16 867 sor / 0 árva / FK-enforcement a GUI írási útjain; backup
  `data/meteo_data_backup_20260910.db` (sha256 `e5b7d635…`), CSV-archívum
  `data/sa1_orphans_archive_20260910.csv`.
