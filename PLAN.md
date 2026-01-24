# PROJEKT TERV - Anomaly Detection Refactor

## 🎯 Cél
A jelenleg GUI rétegbe (`src/gui/results_panel/anomaly_detector.py`) drótozott anomália detektálási logika leváltása a tiszta Domain alapú megoldásra (`src/domain/services/anomaly_detector.py`).

---

## 📅 Fázisok

### ✅ Fázis 1: Domain Spike (KÉSZ)
- [x] Domain entitások (`ClimateAnomaly`)
- [x] Value objects (`AnomalyThresholdSet`)
- [x] Domain service (`AnomalyDetectorService`)
- [x] Unit tesztek magas lefedettséggel
- [x] Git konfiguráció javítása (`.gitignore`)

### 🚧 Fázis 2: Application Layer (KÖVETKEZŐ LÉPÉS)
**Cél:** A domain logika elérhetővé tétele a külvilág számára egy Use Case-en keresztül.
- [ ] **DTO létrehozása**: `AnomalyDetectionInput` és `AnomalyDetectionOutput` (ha szükséges a leválasztáshoz).
- [ ] **Use Case implementálása**: `src/application/use_cases/detect_anomalies.py`.
    - Ez fogja koordinálni az adatlekérést és a detektálást.
- [ ] **Use Case tesztek**: `tests/application/use_cases/test_detect_anomalies.py`.

### ⏳ Fázis 3: Infrastructure & Data
**Cél:** Az adatok előkészítése a Domain Service számára.
- [ ] **Repository illesztés**: Biztosítani, hogy a `WeatherRepository` vagy `WeatherClient` olyan formátumban adja vissza az adatokat (list of floats), amit a `AnomalyDetectorService` vár.
- [ ] **Data Mapping**: Ha szükséges, adapter írása az API válasz és a Domain bemenet közé.

### ⏳ Fázis 4: GUI Integráció & Cleanup
**Cél:** A régi kód kivezetése.
- [ ] **GUI bekötés**: A `ControlPanel` vagy `ResultsPanel` hívja meg az új Use Case-t.
- [ ] **Legacy kód törlése**: `src/gui/results_panel/anomaly_detector.py` törlése.
- [ ] **Verifikáció**: Az alkalmazás futtatása és ellenőrzése, hogy az anomáliák ugyanúgy (vagy jobban) jelennek-e meg.

---

## 📝 Szabályok
- Minden új fájlhoz tartozzon teszt.
- Coverage maradjon >95% az új kódra.
- Clean Architecture szabályok szigorú betartása (a GUI nem nyúlhat közvetlenül a Domainbe, csak Application rétegen keresztül).
