# Global Weather Analyzer

Asztali (PySide6) időjárási elemző alkalmazás, amely több szolgáltató (Open-Meteo, Meteostat)
adatait használja egyedi lokációk, régiók és megyék többéves vizsgálatához. Támogatja a
single-location, multi-city és county elemzéseket, statisztikákat számol, térképes és grafikonos
nézeteken jelenít meg eredményeket, valamint biztosítja a lekérések megszakítását és a provider
használat monitorozását.

## Fő komponensek és architektúra

- `meteo_gui_starter.py`: belépési pont, Qt alkalmazás indítása.
- `src/config.py` és `src/config/`: alap beállítások, könyvtár-készítés, felhasználói preferenciák.
- `src/gui/`: prezentációs réteg (PySide6).
  - `control_panel.py`: widget-aggregátor, egyetlen `analysis_requested(dict)` kimenő jellel.
  - `panel_widgets/`: elemzési típus, lokáció, multi-city, dátumtartomány, provider és API beállítás
    widgetek, query/cancel vezérlés.
  - `app_controller.py`: központi vezérlő, request validálás, worker lifecycle, provider routing.
  - `workers/analysis_worker.py`: háttérszál az elemzési motorok futtatásához, megszakítás-támogatással.
  - `analytics_view.py`, `results_panel/`, `map_visualizer.py`: eredmények, grafikonok, térképek
    megjelenítése.
  - `main_window.py`: főablak, menük, status bar, signal összekötések.
- `src/analytics/`: elemzési logika, többvárosos motor, statisztikai számítások.
- `src/data/`: adat-hozzáférés, városadatbázis, API kliensek, modellek.
- `tests/`: pytest alapú egység- és integrációs tesztek.
- `docs/`: kiegészítő tervek, jegyzetek, architektúra vázlatok.

## Tipikus vezérlési folyamat

1) Felhasználó beállítja az elemzési típust, lokációt vagy régiót, dátumtartományt, providert és API
   opciókat a ControlPanelben.
2) A ControlPanel egyetlen `analysis_requested` jelet küld az összesített paraméterekkel.
3) Az AppController validál, kiegészíti a kérést provider routinggal, majd elindít egy AnalysisWorkert.
4) Az AnalysisWorker a MultiCityEngine-t és/vagy WeatherClientet futtatja, progresszt, hibát vagy
   eredményt jelez vissza.
5) A MainWindow fogadja a lifecycle jeleket, frissíti a státuszt, grafikonokat, térképeket és táblákat.

## Futási útmutató

1) Hozz létre virtuális környezetet, telepítsd a függőségeket:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2) Indítsd a grafikus alkalmazást:
   ```bash
   python meteo_gui_starter.py
   ```

## Projekt célok

- Magyar fókuszú meteorológiai elemzés és vizualizáció egyetlen asztali alkalmazásban.
- Tiszta, moduláris architektúra (Clean Architecture) a GUI, vezérlés, adat-hozzáférés és elemzés
  rétegeinek szétválasztásával.
- Megbízható, megszakítható lekérések, robusztus validáció, provider-használat monitorozása.

File complete: README.md
