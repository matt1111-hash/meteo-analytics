# Refactor Completion Report - Anomaly Detection Extraction

## Cél
- A GUI rétegben lévő anomália detektáló logika kiemelése domain szolgáltatásba.
- Backward kompatibilis wrapper biztosítása a meglévő GUI komponensekhez.

## Elvégzett munka
- Domain service: `src/domain/services/anomaly_detector.py` (stdlib-only).
- BC wrapper: `src/gui/results_panel/anomaly_detector.py` – változatlan interface, domain delegáció.
- Threshold value object és entity már korábban elkészült, wrapper ezeket használja.
- Numpy teljesen eltávolítva a GUI wrapperből.

## Tesztelés
- `pytest tests/ -v` → hibába futott hiányzó függőség miatt (`requests` nincs telepítve), ezért a teljes suite nem futott le lokálisan.
- Korábbi futások alapján (megelőző napok) 51 teszt zöld volt, a BC wrapper működött.

## Quality gate státusz
- Pytest: nem futott végig (hiányzó `requests` dependency a `tests/test_weather_client_core.py` modulban).
- Coverage/Pylint/Flake8: most nem futtatható a fenti hiba miatt.

## Következő lépések
1. Telepíteni a hiányzó `requests` csomagot (vagy mock/skip a konkrét CLI nélkül futtatott tesztre), majd újra: `pytest tests/ -v --cov=src/domain --cov=src/gui/results_panel/anomaly_detector.py --cov-report=term-missing`.
2. Pylint: `pylint src/domain/ src/gui/results_panel/anomaly_detector.py --fail-under=8.0`.
3. Flake8: `flake8 src/domain/ src/gui/results_panel/anomaly_detector.py`.
4. Ha minden zöld, végleges commit: `git add -A && git commit -m "refactor: complete domain extraction + BC wrapper"`.

## Migráció röviden
- GUI továbbra is `AnomalyDetector` osztályt hívja, de az a domain `AnomalyDetectorService`-re delelál.
- Thresholdök a `AnomalyThresholdSet`-en keresztül mennek, dynamic settings támogatással.
- Nincs numpy függőség; stdlib átlag/szűrés használatban.
