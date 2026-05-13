# meteo-analytics — Logika & Architektúra Audit
Dátum: 2026-05-12 | Model: GLM-5.1

---

## 1. Architekturális minta azonosítása

### Megállapított minta: **Clean Architecture (részleges implementáció)**

A projekt kijelentetten Clean Architecture-t követ, és a könyvtárstruktúra (`domain/`, `application/`, `infrastructure/`, `presentation/`) ezt tükrözi. Azonban a megvalósítás **inkonzisztens**: a `src/data/` könyvtár párhuzamosan létezik az `src/infrastructure/` mellett, és a kettő között átfedés van.

#### Explicit réteghatárok:
- **Protocol-ok**: `src/domain/ports/` — `CityRepositoryPort`, `WeatherClientPort`, `AnomalyProfilePort`, `WeatherDataProtocol`, stb. Ezek jól definiált függőségi töréspontok.
- **ABC-k**: `src/data/weather_provider_base.py:20` — `WeatherProvider(ABC)` a provider rétegben.
- **Protocol-ok a domain analytics-ben**: `src/domain/analytics/repositories.py:8` — `CityRepositoryProtocol(Protocol)`.
- **GUI interfészek**: `src/presentation/gui/interfaces.py:12` — `IAnomalyConstants(ABC)`, `IConstantsProvider(ABC)`, `IWindspeedConstants(ABC)`.

#### Hiányzó réteghatárok:
1. **`src/data/` vs `src/infrastructure/` kettősség** — Nincs explicit határ a két könyvtár között. A `src/data/` tartalmazza a `CityManager`-t, `WeatherClient`-et, circuit breakert, anomaly managert — mind infrastruktúra felelősség, de nem az `infrastructure/` könyvtárban. ⚠️
2. **`src/analytics/` réteghatár** — Az `src/analytics/` modul foglalatoskodik Use Case orchestrációval (`MultiCityEngine`), ami application layer felelősség, de az `src/application/use_cases/` alatt van egy másik, párhuzamos implementáció (`AnalyzeMultiCityUseCase`). ⚠️
3. **`src/config/`** — Nincs mögötte interfész vagy port; a config modul közvetlenül van importálva minden rétegből.

#### Következetességi problémák:
- A domain réteg `CityRepositoryProtocol`-t használja (`src/domain/analytics/repositories.py`), míg a port réteg `CityRepositoryPort`-ot (`src/domain/ports/repository_ports.py`) — **két párhuzamos, hasonló célú interfész** ugyanarra a fogalomra. ⚠️
- A `WeatherClientPort` (`src/domain/ports/city_weather_ports.py:90`) metódusaláírása **nem kompatibilis** a tényleges `WeatherClient`/`WeatherClientExtensions` implementációval (`src/data/weather_client_core.py:28`). A port `get_weather_data`-ja `WeatherDataProtocol | None`-ot ad vissza, a valós implementáció `list[dict[str, Any]]`-t. ⚠️

---

## 2. Végrehajtási útvonalak feltérképezése

### Entrypoint-ok:
1. **GUI** — `meteo_gui_starter.py` → `WeatherAnalyzerApp` → `AppController` → szolgáltatások
2. **API** — `uvicorn src.api.main:app` → FastAPI routes → use case-ek / direct infra hívások
3. **CLI/Demo** — `src/analytics/multi_city_demo.py:109` (`if __name__ == "__main__"`)

### Útvonal 1: Multi-city analytics (GUI-ból)
```
GUI controller → MultiCityEngine (src/analytics/)
  → AnalyzeMultiCityUseCase (src/application/)
    → RegionResolverService (domain)
    → CityRepositoryProtocol → CityRepository (infrastructure)
    → WeatherFetchService → WeatherClient (data/)
    → AnalyticsTransformService (domain)
```

**Megkerült réteg**: A `MultiCityEngine` az `src/analytics/`-ben **közvetlenül importálja** `src/infrastructure/container`-t (composition_root + factory), ami azt jelenti, hogy az analytics modul tud az infrastructure-ról. ⚠️

### Útvonal 2: Multi-city analytics (API-ból)
```
API route (weather.py) → build_analyze_multi_city_use_case() (composition_root)
  → AnalyzeMultiCityUseCase (src/application/)
    → Ugyanaz a lánc mint fent
```

**Ágazás**: Két különböző entrypoint, de mindkettő ugyanahhoz a `AnalyzeMultiCityUseCase`-hez fut be — de különböző way-ken:
- A GUI a `MultiCityEngine`-en keresztül (ami egy extra wrapper)
- Az API a composition_root-ot közvetlenül hívja

### Útvonal 3: Wind rose (API)
```
wind_rose.py → src.data.weather_client_core.WeatherClient (KÖZVETLEN IMPORT!)
```
⚠️ **Réteg megkerülése**: Az API route közvetlenül importál `src.data.weather_client_core`-ot, megkerülve a port/factory réteget.

### Útvonal 4: GUI Presentation → Infrastructure
```
GUI workers → src.infrastructure.container.get_weather_client_port()
GUI control_panel → src.infrastructure.container.get_city_manager_port()
```
⚠️ A presentation réteg közvetlenül importál `src.infrastructure.container`-t. Ez technikailag DI container hívás, de a presentation tud az infrastructure-ról. Clean Architecture szerint a presentation csak az application réteget ismerné.

### Config-alapú eltérések:
- `APIConfig.APP_ENV` ("production" vs development) — befolyásolja CORS, rate limit, auth middleware, security headers
- `WeatherClient(preferred_provider)` — "auto" vs explicit provider, runtime routing
- Circuit breaker állapot — OPEN/CLOSED/HALF_OPEN, futásidőben változik

---

## 3. Strukturális káosz jelei

### 3.1 Duplikált orchestration: MultiCityEngine vs AnalyzeMultiCityUseCase ⚠️
- **`MultiCityEngine`** (`src/analytics/multi_city_engine_core.py`): 243 soros orchestrator, saját DI, közvetlen infrastructure import
- **`AnalyzeMultiCityUseCase`** (`src/application/use_cases/analyze_multi_city.py`): 260 soros use case, hasonló orchestráció
- **Probléma**: A `MultiCityEngine` lényegében egy **wrapper/delegátor** a `AnalyzeMultiCityUseCase` felett, de tartalmaz saját `weather_fetch_service`, `analytics_transform_service` inicializációt is (56-96. sorok). Ha a use_case paraméter `None`, sajátot hoz létre, ha meg van adva, azt használja. Ez a kettősség zavaró.

### 3.2 `src/data/` vs `src/infrastructure/` kettősség ⚠️
- `src/data/` könyvtár (4432 sor összesen): `CityManager`, `WeatherClient`, `CircuitBreaker`, `AnomalyProfileManager`, `DistanceCalculator`, `GeoUtils`
- `src/infrastructure/`: `repositories/CityRepository`, `container/` (factory + composition root), `adapters/`
- **Probléma**: A `src/data/` minden eleme infrastruktúra felelősség, de nem az `infrastructure/` könyvtárban van. A `factories.py` lazy importokkal hidalja át (`from src.data.city_manager_stats import CityManagerStats`), ami implicit csatolást teremt.

### 3.3 Párhuzamos Protocol-ok ugyanarra a fogalomra ⚠️
- `CityRepositoryPort` (`src/domain/ports/repository_ports.py:9`) — 6 metódus, `mapped_region`/`original_region`/`country_codes`/`limit`/`hungarian_mapping` paraméterek
- `CityRepositoryProtocol` (`src/domain/analytics/repositories.py:8`) — 3 metódus, `mapped_region`/`original_region`/`country_codes`/`limit`/`hungarian_mapping` (ugyanazok)
- **Probléma**: Két Protocol hasonló, de nem azonos aláírással. A `CityRepository` implementáció az utóbbit implementálja, a factory az előbbit típusként használja.

### 3.4 Legacy wrapper-ek
- `src/analytics/multi_city_legacy.py`: 67 sor, 8 függvény ami másik függvényre delegál (pl. `safe_mean` → `_safe_mean`, `safe_statistics_mean` → `safe_mean` → `_safe_mean`). Három szintű indirekció. ⚠️
- `src/data/city_manager.py`: 55 sor, re-export wrapper ami a refaktorált modulokat exportálja vissza `CityManager` néven.
- `src/config/config.py`: backward compatibility re-export.

### 3.5 Megkerült publikus API-k
- `src/api/routes/wind_rose_support.py:13` — közvetlenül importálja `src.data.weather_client_core.WeatherClient`-et, megkerülve a port/factory rendszert. ⚠️
- A `MultiCityEngine.__init__` közvetlenül hívja a `get_weather_client_port()` factory-t (83. sor) és a `get_city_repository_port()`-ot (72. sor), ami azt jelenti, hogy az analytics réteg tud az infrastructure DI-ról.

### 3.6 God object gyanú
- **`MultiCityEngine`** (`src/analytics/multi_city_engine_core.py`): Bár csak 243 sor, 18 publikus/privát metódussal. Továbbá delegátor metódusai (pl. `_transform_to_city_weather_result`, `_process_weather_results`, `_fetch_weather_data_dual_api_batch`) mind egyszerűen továbbítanak a `weather_fetch_service`-nek és `analytics_transform_service`-nek — felesleges indirekció réteg.
- **`UsageTracker`** (`src/config/usage_config.py`): 278 sor, 12 statikus metódus. Minden metódus static, osztály szintű lockkal. Funkcionálisan ez egy modul, nem osztály.

### 3.7 Névben félrevezető modulok
- `src/data/enums.py` — 62 soros fájl aminek a tartalma: "Moved from src.data.enums as part of Clean Architecture refactoring." Ennek az értéke questioned. ⚠️
- `src/presentation/gui/constants_provider.py` — mypy ignore-errors, valószínűleg konstansokat szolgáltat, de "provider" néven, ami inkább infrastructure minta.
- `src/analytics/ports/analysis_ports.py` — `WindAnalysisPort`, `AnomalyDetectionPort`, stb. Ezeket a portokat **semmilyen implementáció nem teljesíti** a kódbázisban — a factory-k csak `CityRepositoryPort`, `WeatherClientPort`, `CityManagerPort`, `AnomalyProfilePort`-ot implementálnak. ⚠️

### 3.8 "Dead but still wired" kód
- `src/analytics/ports/analysis_ports.py` — `WindAnalysisPort`, `AnomalyDetectionPort`, `AnalyticsQueryPort`, `QueryTypeConfigPort` — ezek a portok definícióban léteznek, de nincs implementációjuk, és a factory-k nem hivatkoznak rájuk. ⚠️
- `src/data/weather_client_extensions.py` — `get_current_weather()` és `get_weather_for_date_range()` "backward compatibility" metódusok. A kód használja ezeket, de a "legacy" jelző alapján kiirthatók lennének.
- `src/config/__init__.py:82` — `datetime = _datetime` backward compat, ami a `datetime` modult re-exportálja mint attribútum.

---

## 4. Domain logika integritása

### 4.1 Domain → infrastruktúra szivárgás ⚠️
- **KRITIKUS**: `src/domain/analytics/services/trend_statistics.py:8-9` — `import numpy as np` és `import pandas as pd`
- `src/domain/analytics/wind_analysis_service.py:8` — `import pandas as pd`
- `src/domain/analytics/wind_statistics.py:7` — `import pandas as pd`
- `src/domain/analytics/services/trend_data_processor.py:8` — `import pandas as pd`
- `src/domain/analytics/wind_extractors.py:7` — `import pandas as pd`

Ezek a domain modulok harmadik féltől származó I/O könyvtáraktól függenek. A domain rétegnek external dependency-mentesnek kellene lennie. Ha a numpy/pandas tényleges számítást végez, az infrastructure/service-ként kellene, hogy funkcionáljon, nem domain-ként.

### 4.2 Adapterek üzleti logikával
- `src/config/provider_config.py:221-246` — `get_resolved_provider()` függvény üzleti logikát tartalmaz: provider routing strategy ("auto" → smart routing by use_case). Ez nem config, hanem application service felelősség. ⚠️
- `src/config/usage_config.py` — `UsageTracker` osztály statikus metódusai tartalmaznak üzleti logikát (warning level calculation, cost estimation, monthly reset strategy). Ez application/domain felelősség, nem config. ⚠️

### 4.3 Hiányzó validáció
- `src/domain/analytics/services/analytics_transform_service.py:84-86` — `_extract_metric_value` `getattr(city_data, metric_name, None)` — ha a `metric_name` hibás, csendben `None`-t ad vissza, nem jelez hibát. A fallback logika (109-126. sor) ezen alapul, ami elfedheti az adatproblémákat.
- `src/data/weather_client_core.py:260-276` — `_validate_inputs` csak latitude/longitude range-et és dátumformátumot ellenőriz. Nem validálja, hogy a dátumok nem túl régiek vagy túl távoliak a provider képességeihez.

---

## 5. Hibakezelés

### 5.1 Stratégia inkonzisztencia
A projekt három különböző hibakezelési stratégiát használ:

1. **Use Case eredmény típus** (`UseCaseResult` with `ResultStatus`): Az `AnalyzeMultiCityUseCase.execute()` mindig `UseCaseResult`-ot ad vissza, hiba esetén is — nincs exception dobás a hívónak. ⚠️
2. **Exception-alapú**: A `WeatherClient.get_weather_data()` `ProviderNotAvailableError`-t és `WeatherAPIError`-t dob. Ezek propagálódnak a hívó felé.
3. **Silent fallback**: A `MultiCityEngine.execute_analytics_query()` és `analyze_multi_city()` metódusok exception-t elkapnak és üres `AnalyticsResult`-ot adnak vissza (120-124., 159-164. sorok). A hívó nem tudja megkülönböztetni a "nincs adat" és "hiba történt" esetet.

### 5.2 Csendben elnyelt hibák ⚠️
- `src/data/weather_client_core.py:130-131` — Ha a circuit breaker OPEN, a provider csendben átugródik (`return None, None`), a hívó nem kap jelzést arról, hogy provider ki lett hagyva.
- `src/data/weather_client_extensions.py:92-94` — `get_current_weather()` exception-t elkap és `(None, "error")`-t ad vissza. A hívó nem látja az eredeti hibát.
- `src/analytics/multi_city_engine_core.py:85-87` — `ImportError` esetén `self.weather_client = None`, ami később `AttributeError`-t okozhat.

### 5.3 Broad Exception catch-ek ⚠️
A prezentációs rétegben találhatók a legszélesebb exception catch-ek:
- `src/presentation/gui/charts/` könyvtárban 35+ `except Exception as e:` blokk található
- Ezek mindegyike naplózza a hibát, de csendben folytatja — a GUI "nem csinál semmit" hiba esetén, a felhasználó nem kap visszajelzést.

---

## 6. Tesztelhetőség

### 6.1 Nehezen tesztelhető modulok
1. **`UsageTracker`** (`src/config/usage_config.py`): Minden metódus static, osztály-szintű `_lock`-kal, fájl I/O-val és időpont-függőséggel. Monkeypatching szükséges a teszteléshez (lásd `usage_config_helpers.py` ami pont erre szolgál). ⚠️
2. **`MultiCityEngine`** (`src/analytics/multi_city_engine_core.py`): Az `__init__` metódus közvetlenül hívja a `get_weather_client_port()` factory-t, ha nincs explicit use_case megadva. Alapértelmezetten I/O műveleteket végez (DB validáció, provider inicializálás). ⚠️
3. **`WeatherClient`** (`src/data/weather_client_core.py`): Az `__init__` metódus azonnal létrehozza a providereket (`OpenMeteoProvider()`, `MeteostatProvider()`) — nincs lazy initialization vagy injectable provider factory. ⚠️

### 6.2 Dependency injection minősége
- **Composition root**: Létezik (`src/infrastructure/container/composition_root.py`), de csak két use case-hez.
- **Factory függvények**: Négy port factory (`get_city_manager_port`, `get_weather_client_port`, `get_city_repository_port`, `get_anomaly_profile_port`), mind lazy importtal.
- **Hardcoded értékek** a composition_root-ban: `max_workers=8`, `request_timeout=90`, `max_retries=2`, `retry_delay=3.0` — nem konfigurálhatók. ⚠️
- **A GUI nem használja a composition_root-ot**: A presentation réteg közvetlenül hívja a port factory-ket (`get_city_manager_port()`, stb.) és saját maga építi fel a szolgáltatásokat, megkerülve a composition_root-ot. ⚠️

### 6.3 Első 3 modul tesztelhetőségi refaktoráláshoz:
1. `src/config/usage_config.py` — `UsageTracker` → instance-alapú, injectálható datetime/file path
2. `src/data/weather_client_core.py` — `WeatherClient` → provider factory injectálás
3. `src/analytics/multi_city_engine_core.py` — `MultiCityEngine` → teljes DI, ne hívjon factory-t __init__-ben

---

## 7. Dependency reality check

### 7.1 Valóban centrális modulok
| Modul | Miért centrális | Mi omlik össze nélküle |
|-------|-----------------|----------------------|
| `src/domain/entities/analytics_models.py` | `AnalyticsResult`, `AnalyticsQuestion`, `QueryResults` — minden analytics flow ezeket adja vissza | API + GUI + Use case-ek |
| `src/domain/value_objects/enums.py` | `AnalyticsMetric`, `DataSource`, `QuestionType`, `RegionScope` — minden réteg használja | Teljes alkalmazás |
| `src/data/weather_client_core.py` | `WeatherClient` — egyetlen időjárási adatforrás | Időjárási funkciók |
| `src/config/` | APIConfig, ProviderConfig, ProjectPaths — globális konfig | Minden I/O művelet |
| `src/infrastructure/container/factories.py` | Port factory-k — minden DI ezen megy keresztül | API + GUI use case-ek |

### 7.2 Névleg centrális, de kihagyhatók
- `src/analytics/ports/analysis_ports.py` — 4 Protocol definíció, 0 implementáció
- `src/data/enums.py` — csak egy komment: "Moved from src.data.enums"
- `src/analytics/multi_city_legacy.py` — wrapper függvények, használhatók a domain közvetlenül is

### 7.3 Implicit globális állapot ⚠️
1. **`UsageTracker._lock`** — osztály-szintű `threading.Lock`, processz-szintű állapot
2. **`APIConfig`** — osztály-szintű konstansok, de `os.environ`-ből olvassák az értékeket import időben. Minden importáló modul ugyanazt a példányt látja.
3. **`ProviderConfig.PROVIDERS`** — `MappingProxyType` immutable, de tartalma `_PROVIDER_DATA` dict-ből jön, ami mutable class variable.
4. **`ProjectPaths`** (`src/config/paths_config.py`) — modul-szintű `Path` konstansok, import időben kalkulálódnak, monkeypatching szükséges teszteléshez.

### 7.4 Gyanús dependency minták
- **`src/analytics/multi_city_engine_core.py`** → `src/infrastructure/container` (analytics tud infrastructure-ról) ⚠️
- **`src/api/routes/wind_rose_support.py`** → `src.data.weather_client_core` (API route tud data layer-ről) ⚠️
- **`src/domain/analytics/services/`** → `pandas`, `numpy` (domain külső I/O könyvtáraktól függ) ⚠️

---

## 8. Executive summary

1. **`src/data/` vs `src/infrastructure/` kettősség** — Az infrastruktúra két külön könyvtárban van, nincs egyértelmű határ. A factory-k `src/data/`-t importálják `src/infrastructure/`-ból, ami implicit csatolást teremt.

2. **Duplikált repository interfész** — `CityRepositoryPort` és `CityRepositoryProtocol` két különböző Protocol ugyanarra a fogalomra, eltérő metódusaláírásokkal. A `CityRepository` az egyet implementálja, a factory a másikat deklarálja.

3. **WeatherClientPort vs valós implementáció inkompatibilitás** — A port `WeatherDataProtocol | None`-ot ígér, a valós `WeatherClient` `list[dict[str, Any]]`-t ad. A típusrendszer hazudik.

4. **Domain réteg pandas/numpy függőség** — 5 domain modul importálja a pandas/numpy könyvtárakat, megsértve a Clean Architecture "domain = dependency-free" elvét.

5. **MultiCityEngine mint felesleges wrapper** — Az `src/analytics/multi_city_engine_core.py` 18 metódusa nagyrészt delegál a `AnalyzeMultiCityUseCase`-hez és a domain service-ekhez. Extra indirekció réteg előny nélkül.

6. **Analytics portok implementálatlanok** — `WindAnalysisPort`, `AnomalyDetectionPort`, `AnalyticsQueryPort`, `QueryTypeConfigPort` — definícióban léteznek, de nincs implementációjuk.

7. **Presentation réteg közvetlenül importál infrastructure-t** — A GUI modulok közvetlenül hívják a port factory-ket, megkerülve a composition_root-ot.

8. **Composition root hiányos** — Csak 2 use case-hez van composition root, a GUI szolgáltatásaihoz nincs.

9. **Hardcoded konfiguráció** — `max_workers=8`, `request_timeout=90`, stb. a composition_root-ban, nem konfigurálhatók.

10. **Hibakezelési inkonzisztencia** — Három különböző stratégia (result type / exception / silent fallback) keveredik, a hívó nem tudja mire számítson.

11. **Config modulok üzleti logikával** — `UsageTracker`, `get_resolved_provider()` és `ProviderConfig` üzleti logikát tartalmaznak (cost estimation, warning levels, routing strategy), ami nem config felelősség.

12. **Silent failure a circuit breaker-ben** — OPEN állapotban a provider csendben átugródik, a hívó nem kap jelzést.

13. **Mypy ignore-errors elterjedtsége** — 50+ fájl tartalmaz `# mypy: ignore-errors` direktívát, főként a prezentációs rétegben. A típusrendszer nem biztosít valódi védelmet.

14. **Legacy wrapper láncolás** — `safe_statistics_mean` → `safe_mean` → `_safe_mean` háromszoros indirekció egyetlen függvényhívásért.

15. **Tesztelhetőségi problémák** — A `UsageTracker`, `WeatherClient`, és `MultiCityEngine` közvetlen I/O-t és factory hívásokat végez inicializáláskor, ami mockolást tesz szükségessé.

### Mi a fő oka annak, hogy a projekt "szétcsúszottnak" érződik?

A projekt "szétcsúszottságának" fő oka az **inkonzisztens rétegfelosztás**: a `src/data/` és `src/infrastructure/` kettősség, a párhuzamos interfészek (`CityRepositoryPort` vs `CityRepositoryProtocol`), a MultiCityEngine use case-wrapper, és az analytics portok implementálatlan volta mind azt mutatja, hogy a Clean Architecture refaktorálás **félkész** — az új réteghatárok ki lettek húzva, de a régi kód nem lett teljesen migrálva, hanem wrapper-ekkel és backward compatibility re-exportokkal tartják fenn a kompatibilitást. Ez a "félkész migráció" hozza létre a strukturális káoszt.

---

## 9. Refactor priority list (Top 10)

| # | Lépés | Várható haszon | Kockázat | Előfeltételek |
|---|-------|----------------|----------|---------------|
| 1 | **Egyesítsd a két City Repository Protocol-t** — Töröld `CityRepositoryProtocol`-t, használd `CityRepositoryPort`-ot mindenhol | Egységes interfész, kevesebb zavart | Közepes — multiple files need update | None |
| 2 | **Helyezd át a pandas/numpy domain service-eket** `src/infrastructure/`-ba, domain-ben csak Protocol | Domain dependency-free lesz | Magas — circular import risk | Protocols defined first |
| 3 | **Szüntesd meg a MultiCityEngine wrapper-t** — GUI és API egyaránt használja a composition_root-ot + UseCase-t | Egyszerűsödik a call graph | Közepes — GUI refaktor | Composition root complete |
| 4 | **Egyesítsd `src/data/` és `src/infrastructure/`** — mozgass mindent `infrastructure/` alá | Egyértelmű rétegstruktúra | Magas — több tucat import path | Protocol merge first |
| 5 | **Javítsd a WeatherClientPort aláírását** hogy kompatibilis legyen a valós implementációval | Típusbiztonság | Alacsony | None |
| 6 | **Töröld az implementálatlan portokat** (`WindAnalysisPort`, `AnomalyDetectionPort`, stb.) vagy implementáld | Kisebb dead code | Alacsony | None |
| 7 | **Készíts teljes composition root-ot** a GUI szolgáltatásaihoz is | Következetes DI | Közepes | Data/infra merge helpful |
| 8 | **Konfigurálhatóvá tedd a hardcoded értékeket** (max_workers, timeout, stb.) | Flexibilis deployment | Alacsony | None |
| 9 | **Szüntesd meg a legacy wrapper láncokat** (`multi_city_legacy.py`, `safe_statistics_*`) | Kevesebb indirekció | Alacsony | Check all callers |
| 10 | **Konvertáld a `UsageTracker`-t instance-alapúra**, injectálható file path-pel és datetime-nal | Jobb tesztelhetőség | Közepes — all callers update | None |

---

## Finding-ek részletesen

#### F1: Kettős City Repository Protocol
- **Severity:** MAGAS
- **Érintett fájlok:** `src/domain/ports/repository_ports.py:9`, `src/domain/analytics/repositories.py:8`, `src/infrastructure/repositories/city_repository.py:14`, `src/infrastructure/container/factories.py:56`, `src/analytics/multi_city_engine_core.py:16`, `src/application/use_cases/analyze_multi_city.py:11`
- **Mi sérül:** Egységes interfész a city repository-hoz
- **Miért probléma:** Két Protocol hasonló, de nem azonos aláírással. A `CityRepository` a `CityRepositoryProtocol`-t implementálja, de a factory `CityRepositoryPort`-ot deklarálja visszatérési típusként. A típusrendszer nem garantálja a kompatibilitást.
- **Gyakorlati következmény:** Ha valaki a `CityRepositoryPort`-on keresztül hív egy metódust amit csak a `CityRepositoryProtocol` definiál (pl. `autocomplete_city_name`), runtime `AttributeError`.
- **Minimális irány a rendrakáshoz:** Egyesítsd a két Protocol-t egyetlen `CityRepositoryPort`-ba `src/domain/ports/`-ban. Töröld a `src/domain/analytics/repositories.py`-t. Frissítsd az összes hivatkozást.
- **Bizonyosság:** MEGERŐSÍTETT

#### F2: Domain réteg pandas/numpy függőség
- **Severity:** MAGAS
- **Érintett fájlok:** `src/domain/analytics/services/trend_statistics.py:8-9`, `src/domain/analytics/wind_analysis_service.py:8`, `src/domain/analytics/wind_statistics.py:7`, `src/domain/analytics/services/trend_data_processor.py:8`, `src/domain/analytics/wind_extractors.py:7`
- **Mi sérül:** Clean Architecture "domain = no external dependencies" elv
- **Miért probléma:** A domain réteg harmadik féltől származó I/O könyvtáraktól függ, ami megakadályozza a domain izolált tesztelését és újrafelhasználását.
- **Gyakorlati következmény:** Domain unit tesztekhez telepíteni kell a pandas/numpy csomagokat. Ha a domain-t új kontextusban akarod használni (pl. más UI framework), a pandas/numpy is jön.
- **Minimális irány a rendrakáshoz:** Mozgasd a számítási logikát `src/infrastructure/analytics/`-ba. A domain-ben csak Protocol-t definiálj. Az application service hivatkozzon a Protocol-ra, az infrastructure implementálja.
- **Bizonyosság:** MEGERŐSÍTETT

#### F3: MultiCityEngine felesleges wrapper
- **Severity:** KÖZEPES
- **Érintett fájlok:** `src/analytics/multi_city_engine_core.py`, `src/analytics/multi_city_engine.py`
- **Mi sérül:** Architekturális egyértelműség
- **Miért probléma:** A `MultiCityEngine` 18 metódusából 10+ egyszerű delegáció a `AnalyzeMultiCityUseCase`-hez és domain service-ekhez. Az `__init__` duplikálja a composition_root DI logikáját (saját `WeatherFetchService`, `AnalyticsTransformService` inicializálás).
- **Gyakorlati következmény:** Ha valaki a `MultiCityEngine`-t használja (GUI), és valaki a composition_root-ot (API), két különböző DI útvonalon fut ugyanaz a logika. Hardcoded konfiguráció (max_workers=8) kétszer van definiálva.
- **Minimális irány a rendrakáshoz:** A `MultiCityEngine` maradhat thin facade, de az `__init__` ne végezze el a DI-t — fogadja a `AnalyzeMultiCityUseCase`-et kötelező paraméterként. A GUI is használja a composition_root-ot.
- **Bizonyosság:** MEGERŐSÍTETT

#### F4: src/data/ vs src/infrastructure/ kettősség
- **Severity:** KÖZEPES
- **Érintett fájlok:** Teljes `src/data/` könyvtár (4432 sor, 32 fájl)
- **Mi sérül:** Következetes réteghatárok
- **Miért probléma:** Az `src/data/` és `src/infrastructure/` könyvtárak infrastruktúra felelősségű kódot tartalmaznak. A factory-k lazy importokkal hidalják át a távolságot. Nincs egyértelmű szabály, hogy mi hova kerül.
- **Gyakorlati következmény:** Új fejlesztő nem tudja, hova tegye az új provider-t vagy repository-t. Duplikáció veszélye.
- **Minimális irány a rendrakáshoz:** `src/data/` tartalmát mozgasd `src/infrastructure/data/` alá. Vagy fordítva: `src/infrastructure/` tartalmát mozgasd `src/data/` alá. A lényeg: egy hely legyen.
- **Bizonyosság:** MEGERŐSÍTETT

#### F5: API route közvetlen data layer import
- **Severity:** KÖZEPES
- **Érintett fájlok:** `src/api/routes/wind_rose_support.py:13-14`
- **Mi sérül:** Clean Architecture rétegszabály (API → application, nem API → data)
- **Miért probléma:** A `wind_rose_support.py` közvetlenül importálja `src.data.weather_client_core.WeatherClient`-et és `src.infrastructure.container`-t. Megkerüli a port rendszert.
- **Gyakorlati következmény:** Ha a `WeatherClient` megváltozik, a wind rose route is törik. A tesztek nem tudják mockolni a portot, konkrét implementációt kell mockolni.
- **Minimális irány a rendrakáshoz:** Használja a `get_weather_client_port()` factory-t a composition_root-ból, és a `WeatherClientPort` interfészt.
- **Bizonyosság:** MEGERŐSÍTETT

#### F6: Hibakezelési inkonzisztencia (UseCaseResult vs Exception)
- **Severity:** KÖZEPES
- **Érintett fájlok:** `src/application/use_cases/analyze_multi_city.py:152-158`, `src/analytics/multi_city_engine_core.py:119-124`, `src/data/weather_client_core.py:156-167`
- **Mi sérül:** Konzisztens hibajelzés a hívó felé
- **Miért probléma:** A use case `UseCaseResult`-ot ad vissza (soha nem dob exception-t), a `WeatherClient` exception-t dob. A `MultiCityEngine` mindkettőt kezeli — de a `analyze_multi_city()` metódus elkapja a use case `UseCaseResult(ERROR)`-t és `AnalyticsResult`-t ad vissza, ami nem tartalmazza a hiba státuszt.
- **Gyakorlati következmény:** A hívó (GUI/API) nem tudja megkülönböztetni a "sikeres, de üres eredmény" és a "hiba történt" esetet. Hibás diagnostics.
- **Minimális irány a rendrakáshoz:** Definiálj egységes Result típust amit a teljes lánc használ. Vagy használj exception-t a use case-ekben is, és a presentation layer kapja el.
- **Bizonyosság:** MEGERŐSÍTETT

#### F7: UsageTracker statikus osztály tesztelhetőségi probléma
- **Severity:** KÖZEPES
- **Érintett fájlok:** `src/config/usage_config.py` (278 sor), `src/config/usage_config_helpers.py`
- **Mi sérül:** Tesztelhetőség, Dependency Inversion
- **Miért probléma:** Minden metódus `@staticmethod`, fájl I/O-t végez, és időpont-függő. A `usage_config_helpers.py` kifejezetten monkeypatching helper-ként jött létre a teszteléshez — ami workaround, nem megoldás.
- **Gyakorlati következmény:** Minden tesztnek mockolnia kell a `usage_config_helpers._now` és `_get_usage_tracking_file` függvényeket. Komplex teszt setup.
- **Minimális irány a rendrakáshoz:** Konvertáljd instance-alapú osztállyá. Injektálható `datetime_provider` és `storage_path`. A factory hozza létre a megfelelő konfigurációval.
- **Bizonyosság:** MEGERŐSÍTETT

#### F8: Mypy ignore-errors elterjedtség
- **Severity:** ALACSONY
- **Érintett fájlok:** 50+ fájl a `src/presentation/` könyvtárban, további fájljok más rétegekben (composition_root, factories, config)
- **Mi sérül:** Típusbiztonság
- **Miért probléma:** A `# mypy: ignore-errors` direktíva teljesen kikapcsolja a típusellenőrzést az adott fájlra. A prezentációs réteg gyakorlatilag típusellenőrizetlen.
- **Gyakorlati következmény:** Típushibák csak runtime-ban derülnek ki. A CI mypy gate nem biztosít valódi védelmet.
- **Minimális irány a rendrakáshoz:** Fokozatosan cseréld le a `# mypy: ignore-errors`-t specifikus `# type: ignore[...]` direktívákra. Kezdd a domain és application réteggel.
- **Bizonyosság:** MEGERŐSÍTETT

#### F9: Implementálatlan analytics portok
- **Severity:** ALACSONY
- **Érintett fájlok:** `src/analytics/ports/analysis_ports.py:26-120`
- **Mi sérül:** Architekturális tisztaság
- **Miért probléma:** `WindAnalysisPort`, `AnomalyDetectionPort`, `AnalyticsQueryPort`, `QueryTypeConfigPort` — 4 Protocol definíció, 0 implementáció, 0 factory. "Dead architecture".
- **Gyakorlati következmény:** Zavaró az új fejlesztők számára. Ha valaki implementálni próbálja, nincs gyár ami visszaadná.
- **Minimális irány a rendrakáshoz:** Töröld ha nincs rájuk szükség, vagy implementáld ha a tervek között szerepelnek. Legalább kommentben jelezd a státuszt.
- **Bizonyosság:** HIPOTÉZIS – ellenőrzendő (lehet, hogy használatban vannak dinamikus úton)

#### F10: Config modulok üzleti logikával
- **Severity:** KÖZEPES
- **Érintett fájlok:** `src/config/provider_config.py:221-246`, `src/config/usage_config.py` (teljes)
- **Mi sérül:** Separation of concerns
- **Miért probléma:** A `get_resolved_provider()` provider routing strategy-t valósít meg (üzleti logika). A `UsageTracker` cost estimation-t, warning level calculation-t, és monthly reset logic-ot tartalmaz. Ezek nem config felelősségek.
- **Gyakorlati következmény:** Ha az üzleti logika változik (pl. új pricing modell), a config modult kell módosítani, ami megsérti a "config csak adat" elvet.
- **Minimális irány a rendrakáshoz:** Mozgasd a routing logic-ot egy application service-be. A UsageTracker legyen instance, a cost estimation legyen külön service.
- **Bizonyosság:** MEGERŐSÍTETT
