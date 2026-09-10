# 07 — SA-1 dry-run: árva `weather_data` sorok (döntéskész riport)

**RUN_ID:** `20260910T092914Z` · **Dátum:** 2026-09-10 · **Mód:** read-only a valós DB-n (minden mérés **másolaton**)
**Eszköz:** `scripts/sa1_orphan_weather_migration.py` (alapból dry-run)
**Kapcsolódó tételek:** RT-2 / L-01 (megelőzés — kész), SA-1 (ez a riport), L-10 (nincs olvasó), Q-09 (connection hygiene)

---

## 1. Mi történt (röviden)

A GUI `save_city_to_database` `INSERT OR REPLACE INTO cities`-szel írt. Név-ütközéskor az SQLite **törölte** a régi sort és **új `id`-vel** szúrta be; a korábban írt `weather_data` sorok a törölt `id`-re mutatnak. Mivel a `PRAGMA foreign_keys` a kapcsolatnyitáskor **0**, ez csendben megtörtént. Az RT-2 commit (`ab65ec7`) ezt **megállította**, de a már keletkezett sorok megmaradtak.

## 2. Mért tények (a `data/meteo_data.db` másolatán)

| Metrika | Érték |
|---|---|
| `cities` sorok | 60 (id 1 … 452) |
| `weather_data` sorok | **79 824** |
| **árva sorok** (`city_id` nem létező `cities.id`) | **62 957 (78,9 %)** |
| árva `city_id`-k száma | **118** |
| duplikált `(city_id, date)` az árvákon belül | 0 |
| árva sorok, amelyek **dátuma máshol nem szerepel** | **4 271** |
| `PRAGMA foreign_keys` | 0 (nincs enforcement) |

Legnagyobb árva csoportok: `city_id=424` → 3 651 sor (2015-08-04 … 2025-08-01), `city_id=440` → 2 069 sor (1986-01-01 … 1991-08-31), `406`/`410` → 1 827 sor (5 év), `404` → 1 826 sor. Ezek **valódi, hosszú idősorok**, nem törmelék.

## 3. Visszapárosíthatóság (relink) — **nem lehetséges a DB-ből**

- `cities` oszlopai: `id, name, latitude, longitude, country, region, created_at` — nincs `former_id` / `merged_from` / alias tábla.
- `weather_data` oszlopai: nincs `lat`/`lon`, tehát koordináta-alapú visszafejtés sincs.
- A `INSERT OR REPLACE` az **azonos nevű** sort cserélte, tehát egy árva id „gazdája” névben ma is létezik — de hogy **melyik** mai sor, a törölt sor adatai nélkül nem bizonyítható. A dátum-tartomány/`created_at` heurisztika tipp, nem bizonyíték → **nem** építünk rá migrációt.

## 4. Lehetőségek

| # | Opció | Hatás | Kockázat |
|---|---|---|---|
| **A** | Nincs teendő (status quo) | 78,9 % inert sor a táblában; a mai kód **nem olvassa** a `weather_data`-t (L-10: `rg FROM weather_data src/` → 0) | Nulla. Bármely jövőbeli olvasónak szűrnie kell |
| **B** | **Archiválás + purge** (a mellékelt eszköz) | 79 824 → **16 867** sor; `VACUUM` után fájl **12,5 MB → 2,5 MB** (−79,7 %); az árva sorok CSV-ben megőrizve | A **4 271** árva-only dátum eltűnik a live táblából; visszaállítás a backupból/CSV-ből lehetséges |
| **C** | B után séma-rebuild `FOREIGN KEY` + `PRAGMA foreign_keys=ON` mellett | Megelőzi a jövőbeli árvákat DB-szinten | Séma/migráció + a `weather_data` írási útjának újratesztelése; **külön döntés** |
| **D** | Relink pokol | — | **Elvetve:** a 3. pont szerint nem bizonyítható |

## 5. Az eszköz (bizonyítottan működik, a valós DB-t nem érinti)

```bash
# 1) dry-run (csak számol, nem ír)
python scripts/sa1_orphan_weather_migration.py --db data/meteo_data.db

# 2) árva sorok mentése CSV-be
python scripts/sa1_orphan_weather_migration.py --db data/meteo_data.db --export /tmp/sa1-orphans.csv

# 3) éles törlés CSAK backup birtokában (a szkript megköveteli)
cp data/meteo_data.db /tmp/meteo_data.db.bak
python scripts/sa1_orphan_weather_migration.py --db data/meteo_data.db \
    --apply --backup /tmp/meteo_data.db.bak --vacuum
```

**Biztonsági tulajdonságok (tesztelve):** alapból read-only (`mode=ro`); `--apply` visszautasít, ha nincs létező `--backup` vagy ha az a `--db`-vel azonos fájl; a törlés egy tranzakcióban fut.

**Futtatott bizonyíték (másolatokon):**

| Teszt | Eredmény |
|---|---|
| dry-run a másolaton | `weather_data: 79824`, `orphan_rows: 62957`, `orphan_city_ids: 118`, `orphan_unique_dates: 4271` |
| `--export /tmp/sa1-orphans.csv` | 62 957 sor kiírva (62 958 sor a fájlban, fejléccel) |
| `--apply` backup nélkül | `--apply requires an existing --backup file copy of the database`, exit=1 |
| `--apply --backup --vacuum` eldobható másolaton | `deleted_rows: 62957`; utána 16 867 sor, 0 árva; `VACUUM` után 12 455 936 → **2 527 232 byte** |
| backup másolat érintetlensége | 79 824 sor / 62 957 árva (változatlan) |
| **valós `data/meteo_data.db`** | sha256 `e5b7d635…` — **változatlan**, hozzá nem nyúltam |

## 6. Javaslat

1. **Most:** A vagy B. Adathiány nincs (nincs olvasó), ezért a döntés ízlés kérdése: ha a történeti idősorok megőrzése fontos → **A**; ha a tiszta tábla és a kisebb DB fontos → **B** (előtte `--export`, hogy a 4 271 egyedi dátum is meglegyen olvasható formában).
2. **B esetén utána:** C (sémarobusztítás + `foreign_keys=ON`) — ez önmagában is véd a jövőbeni árváktól, de érinti az írási utat, ezért külön tétel.
3. Az eszköz a repóban marad (`scripts/`), hogy a döntés bármikor egy paranccsal végrehajtható legyen.

**Amit ez a kör NEM tett meg:** a valós adatbázist nem módosította, migrációt nem futtatott, kódot nem változtatott a `scripts/sa1_orphan_weather_migration.py`-n kívül.
