# 🚀 **KOMPREHENZÍV KÓDOLÁSI SZABÁLYOK**
## **Professzionális Fejlesztési Útmutató és Projektstandard**

> **KRITIKUS FONTOSSÁGÚ DOKUMENTUM**  
> Minden projekt, minden kódsor, minden LLM interakció ennek a dokumentumnak a szellemében történik.  
> Ez a professzionális szoftverfejlesztés alapja!

---

## **1. Projektstruktúra és Konfiguráció**

### **📁 Mappaszervezés**
```
project/
├── src/                    # Forráskód
│   ├── __init__.py
│   ├── gui/               # GUI komponensek
│   ├── core/              # Üzleti logika
│   ├── data/              # Adatkezelés
│   └── utils/             # Segédeszközök
├── tests/                 # Unit tesztek
├── docs/                  # Dokumentáció
├── config/                # Konfigurációs fájlok
├── requirements.txt       # Függőségek
├── .env.example          # Környezeti változók példa
├── .gitignore            # Git kizárások
├── README.md             # Projekt dokumentáció
└── ARCHITECTURE.md       # Architektúra leírás
```

### **⚙️ Konfigurációs Alapelvek**
- **Minden globális/állítható érték** `config.py`-ben vagy `.env`-ben legyen
- **Titkos kulcsokat SOHA ne commitolj!** (Használd `.env`, `python-dotenv`)
- **Környezeti változók**: `DEV`, `PROD`, `TEST` módok támogatása
- **Konfigurációs validáció**: startup-kor ellenőrizd a kötelező értékeket

---

## **2. Alapvető Kódolási Elvek**

### **🔄 DRY (Don't Repeat Yourself)**
- **Egy logika, egy helyen** - Ismétlődő kódot szervezz függvénybe/osztályba
- **Közös komponensek** külön modulba kiemelése
- **Utility függvények** központi helyen (`utils/`)

### **💎 KISS (Keep It Simple, Stupid)**
- **Csak azt valósítsd meg, amire _most_ szükség van**
- **Ne bonyolítsd túl** - az egyszerű megoldás a jobb
- **Olvashatóság > Okosság**

### **🚫 YAGNI (You Ain't Gonna Need It)**
- **Amit nem kértek, azt ne írd meg előre**
- **Konkrét igényekre fókuszálj**
- **Premature optimization is the root of all evil**

### **🏗️ SOLID Principles**
- **Single Responsibility**: 1 osztály = 1 felelősség
- **Open/Closed**: bővítésre nyitott, módosításra zárt
- **Liskov Substitution**: altípusok helyettesíthetők
- **Interface Segregation**: specifikus interface-ek
- **Dependency Inversion**: absztrakciókra támaszkodás

---

## **3. Bővíthetőség és Modularitás**

### **🧩 Moduláris Architektúra**
- **Minden fő funkció legyen külön modulban**
- **Példa**: `src/gui/chart_widgets.py`, `src/core/weather_analyzer.py`
- **Lazy loading**: modulok csak szükség esetén töltődjenek

### **🎨 Színkezelés és Témák**
- **Soha ne kódolj színt keményen egy widgetbe!**
- **Központi színpaletta/osztály** (pl. `ThemeManager`, `ColorScheme`)
- **Többféle téma támogatása** (világos/sötét mód)
- **Dinamikus témaváltás** runtime-ban

---

## **4. Error Handling & Logging (Hibakezelés és Naplózás)**

### **🚨 Egységes Hibakezelés**
```python
# Saját kivétel osztályok
class WeatherAPIError(Exception):
    """API kapcsolati hibák"""
    pass

class DatabaseError(Exception):
    """Adatbázis műveleti hibák"""
    pass

class ConfigurationError(Exception):
    """Konfigurációs hibák"""
    pass

# Specifikus kivételkezelés
try:
    weather_data = api.fetch_weather()
except WeatherAPIError as e:
    logger.error(f"API hiba: {e}")
    # Fallback mechanizmus
except Exception as e:
    logger.critical(f"Váratlan hiba: {e}")
    # Graceful degradation
```

### **📝 Strukturált Naplózás**
```python
import logging

# Minden modulban
logger = logging.getLogger(__name__)

# Konfigurációs példa
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

# Használati példák
logger.debug("Részletes debug információ")
logger.info("Általános információ")
logger.warning("Figyelmeztetés")
logger.error("Hiba történt")
logger.critical("Kritikus hiba")
```

### **🎯 Hibakezelési Stratégia**
- **Fail Fast**: hibák korai észlelése
- **Graceful Degradation**: alkalmazás továbbműködése hibák esetén
- **User-friendly Messages**: technikai hibák ne kerüljenek a felhasználó elé
- **Error Recovery**: automatikus újrapróbálkozás mechanizmusok

---

## **5. Kódminőség és Stílus**

### **📏 Kódformázás**
- **PEP8** kompatibilitás kötelező
- **Black** automatikus kódformázás
- **isort** import szervezés
- **flake8** vagy **pylint** linting

### **🏷️ Névadási Konvenciók**
```python
# Változók és függvények
wind_speed_max = 120.5           # snake_case
get_weather_data()               # snake_case

# Osztályok
class WeatherDataProcessor:      # PascalCase
    pass

# Konstansok
API_BASE_URL = "https://api..."  # UPPER_CASE
MAX_RETRY_COUNT = 3

# Privát elemek
def _private_method(self):       # egy underscore
    pass

def __very_private(self):        # két underscore
    pass

# Fájlnevek
weather_analyzer.py              # snake_case
chart_widgets.py                 # snake_case
```

### **📖 Dokumentáció**
```python
def calculate_wind_gusts(hourly_data: List[float]) -> float:
    """
    Kiszámítja a napi maximum széllökést óránkénti adatokból.
    
    Args:
        hourly_data: Óránkénti széllökés értékek km/h-ban
        
    Returns:
        Napi maximum széllökés km/h-ban
        
    Raises:
        ValueError: Ha az input lista üres
        
    Example:
        >>> hourly_gusts = [45.2, 67.8, 89.1, 76.3]
        >>> calculate_wind_gusts(hourly_gusts)
        89.1
    """
    if not hourly_data:
        raise ValueError("Óránkénti adatok nem lehetnek üresek")
    
    return max(hourly_data)
```

### **✅ Type Hints**
```python
from typing import Optional, Dict, List, Union
from dataclasses import dataclass

@dataclass
class WeatherData:
    temperature: float
    humidity: int
    wind_speed: Optional[float] = None
    
def process_weather_data(
    data: Dict[str, Any],
    city_name: str,
    include_forecasts: bool = False
) -> Optional[WeatherData]:
    """Type hints minden paraméternél és return értéknél"""
    pass
```

---

## **6. Performance és Optimalizáció**

### **⚡ Performance Alapelvek**
- **Profiling**: `cProfile`, `memory_profiler` használata
- **Memory Management**: generátorok nagy listáknál
- **Lazy Loading**: adatok csak szükség esetén töltődjenek
- **Caching**: gyakran használt adatok gyorsítótárazása

### **🗄️ Database Optimalizáció**
```python
# Indexek használata
CREATE INDEX idx_weather_date ON weather_data(date);

# Batch műveletek
cursor.executemany(
    "INSERT INTO weather_data VALUES (?, ?, ?)",
    data_batch
)

# Query optimalizáció
SELECT * FROM weather_data 
WHERE date BETWEEN ? AND ?
ORDER BY date
LIMIT 100;
```

### **🖥️ GUI Performance**
- **Progress Bar**: hosszú műveleteknél feedback
- **Background Threading**: UI blokkolás elkerülése
- **Lazy Loading**: widget-ek csak szükség esetén töltődjenek
- **Memory Cleanup**: unused objektumok felszabadítása

---

## **7. GUI Specifikus Elvek (PySide6/PyQt)**

### **🏛️ MVC/MVP Pattern**
```python
# Model: Adatok és üzleti logika
class WeatherModel:
    def get_weather_data(self) -> WeatherData:
        pass

# View: Felhasználói interfész
class WeatherView(QWidget):
    def display_weather(self, data: WeatherData):
        pass

# Controller: Koordináció
class WeatherController:
    def __init__(self, model: WeatherModel, view: WeatherView):
        self.model = model
        self.view = view
```

### **📡 Signal/Slot Komunikáció**
```python
class WeatherWidget(QWidget):
    # Saját signalok
    weather_updated = Signal(dict)
    error_occurred = Signal(str)
    
    def __init__(self):
        super().__init__()
        # Loose coupling
        self.weather_updated.connect(self.update_display)
        self.error_occurred.connect(self.show_error)
```

### **🎨 Theme Management**
```python
class ThemeManager:
    def __init__(self):
        self.themes = {
            'light': LightTheme(),
            'dark': DarkTheme()
        }
    
    def apply_theme(self, theme_name: str):
        theme = self.themes.get(theme_name)
        if theme:
            theme.apply_to_application()
```

---

## **8. Dependency és Titkos Adatkezelés**

### **📦 Dependency Management**
```bash
# Virtual environment KÖTELEZŐ
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Requirements kezelés
pip install -r requirements.txt
pip freeze > requirements.txt

# Development dependencies
pip install -r requirements-dev.txt
```

### **🔐 Environment Variables**
```python
# .env fájl
API_KEY=your_secret_key_here
DATABASE_URL=postgresql://user:pass@localhost/db
DEBUG=True
LOG_LEVEL=DEBUG

# Használat
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv('API_KEY')
if not API_KEY:
    raise ConfigurationError("API_KEY hiányzik!")
```

### **🚫 .gitignore Alapok**
```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
.venv/

# Environment
.env
.env.local
.env.prod

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Data
*.db
*.sqlite
data/
```

---

## **9. Verziókezelés és Workflow**

### **🌳 Git Workflow**
```bash
# Branch strategy
git checkout -b feature/wind-gust-support
git checkout -b bugfix/chart-rendering
git checkout -b hotfix/critical-security

# Commit konvenciók
git commit -m "feat: add wind_gusts_max support to charts"
git commit -m "fix: resolve chart rendering issue"
git commit -m "docs: update API documentation"
git commit -m "refactor: optimize database queries"
```

### **📋 Commit Message Format**
```
type: rövid leírás (max 50 karakter)

Részletesebb leírás, ha szükséges.
Magyarázd meg a MIÉRT-et, nem a MIT-et.

Fixes #123
Closes #456
```

**Types:**
- `feat`: új funkció
- `fix`: bugfix
- `docs`: dokumentáció
- `style`: formázás
- `refactor`: kód átszervezés
- `test`: tesztek
- `chore`: egyéb feladatok

---

## **10. Tesztelés**

### **🧪 Unit Tesztek**
```python
import unittest
from unittest.mock import Mock, patch

class TestWeatherProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = WeatherProcessor()
    
    def test_calculate_wind_gusts(self):
        # Arrange
        hourly_data = [45.2, 67.8, 89.1, 76.3]
        expected = 89.1
        
        # Act
        result = self.processor.calculate_wind_gusts(hourly_data)
        
        # Assert
        self.assertEqual(result, expected)
    
    @patch('requests.get')
    def test_api_call(self, mock_get):
        # Mock API response
        mock_get.return_value.json.return_value = {'temp': 25.5}
        
        result = self.processor.fetch_weather()
        
        self.assertEqual(result['temp'], 25.5)
        mock_get.assert_called_once()
```

### **🔍 Integration Testing**
```python
class TestWeatherAppIntegration(unittest.TestCase):
    def test_full_workflow(self):
        # End-to-end teszt
        app = WeatherApp()
        result = app.process_weather_request('Budapest')
        
        self.assertIsNotNone(result)
        self.assertIn('temperature', result)
```

---

## **11. Dokumentáció**

### **📘 README.md Struktúra**
```markdown
# Projekt Név

## Leírás
Rövid leírás a projekt céljáról.

## Telepítés
```bash
pip install -r requirements.txt
```

## Futtatás
```bash
python main.py
```

## Konfigurációs
...

## API Dokumentáció
...

## Közreműködés
...
```

### **🏗️ ARCHITECTURE.md**
```markdown
# Architektúra Áttekintés

## Fő Komponensek
- **AppController**: Alkalmazás vezérlő
- **MainWindow**: Főablak
- **WorkerManager**: Háttérszálak kezelője

## Adatfolyam
1. User Input → Controller
2. Controller → Model
3. Model → Database/API
4. Response → View Update

## Signal/Slot Láncok
UserAction → Controller.handle_action → Model.process → View.update
```

---

## **12. Security és Adatvédelem**

### **🔒 Biztonsági Alapelvek**
- **Soha ne naplózz titkos adatot!**
- **Input validáció**: minden felhasználói bemenetet ellenőrizz
- **SQL Injection**: parameterized queries használata
- **XSS Protection**: output escaping

### **🛡️ API Biztonsága**
```python
def validate_api_key(api_key: str) -> bool:
    """API kulcs validálása"""
    if not api_key or len(api_key) < 32:
        return False
    
    # További validáció...
    return True

def sanitize_input(user_input: str) -> str:
    """Felhasználói input tisztítása"""
    return user_input.strip().replace(';', '').replace('--', '')
```

---

## **13. LLM Promptolási Szabályok**

### **🤖 AI Fejlesztési Irányelvek**
Amikor AI-t használsz fejlesztéshez:

1. **Specifikus legyen a kérés:**
   ```
   "Frissítsd a chart_widgets.py-t wind_gusts_max támogatással,
   alkalmazva a DRY és SOLID elveket, PEP8 formázással,
   type hints-szel és részletes docstring-ekkel."
   ```

2. **Technikai követelmények:**
   - Nyelv, platform, könyvtárak megadása
   - Kódminőségi elvárások (PEP8, type hints, dokumentáció)
   - Tesztelhetőség biztosítása

3. **Tiltott válaszok:**
   - `"rest of the code remains the same"`
   - `"..."`
   - Hiányos kódrészletek

4. **Elvárások:**
   - Teljes, működő kód
   - Moduláris felépítés
   - Hibakezelés
   - Dokumentáció

---

## **14. Karbantarthatóság és Evolúció**

### **🔄 Refactoring Ciklus**
1. **Rendszeres code review**
2. **Duplikált kód azonosítása**
3. **Moduláris átszervezés**
4. **Teljesítmény optimalizálás**
5. **Dokumentáció frissítés**

### **📊 Code Quality Metrics**
- **Cyclomatic Complexity**: < 10 per function
- **Code Coverage**: > 80%
- **Duplication**: < 5%
- **Maintainability Index**: > 70

---

## **15. Összefoglalás és Checklist**

### **✅ Projekt Indítási Checklist**
- [ ] Virtual environment létrehozása
- [ ] Requirements.txt készítése
- [ ] .gitignore beállítása
- [ ] Logging konfigurálása
- [ ] Tesztelési framework beállítása
- [ ] Code quality tools telepítése
- [ ] CI/CD pipeline konfigurálása
- [ ] Dokumentáció vázának létrehozása

### **🎯 Fejlesztési Checklist**
- [ ] DRY, KISS, YAGNI, SOLID elvek alkalmazása
- [ ] Type hints minden függvénynél
- [ ] Docstring minden modulnál/osztálynál
- [ ] Unit tesztek minden funkcióhoz
- [ ] Error handling implementálása
- [ ] Logging hozzáadása
- [ ] Performance optimalizálás
- [ ] Security validáció

### **🚀 Release Checklist**
- [ ] Összes teszt átmegy
- [ ] Code coverage > 80%
- [ ] Dokumentáció frissítve
- [ ] Security audit elvégezve
- [ ] Performance benchmark futtatva
- [ ] User acceptance testing
- [ ] Deployment guide elkészítve

---

> **FONTOS EMLÉKEZTETŐ:**  
> Ez a dokumentum minden projektnél, minden kódnál, minden LLM interakciónál alkalmazandó.  
> Ezek az elvek garantálják a professzionális, karbantartható, bővíthető kódot!

**Verziószám:** 1.0  
**Utolsó frissítés:** 2025  
**Státusz:** Éles használatra kész