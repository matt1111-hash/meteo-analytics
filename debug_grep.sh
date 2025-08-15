#!/bin/bash

# 🔍 VÁROS ELEMZÉS SIGNAL CHAIN HIBAKERESÉS - GREP PARANCSOK
# Ezeket a parancsokat futtasd le a projektben a hibakereséshez!

echo "🔍 === VÁROS ELEMZÉS SIGNAL CHAIN HIBAKERESÉS ==="

# 1. SIGNAL CONNECTION ELLENŐRZÉSE - van-e a megfelelő signal connection?
echo "🔗 1. SIGNAL CONNECTION keresése..."
grep -r "analysis_completed" src/gui/ --include="*.py" -n
echo ""

# 2. CONTROLLER SIGNAL EMIT keresése - emittálja-e a Controller a signalt?
echo "📡 2. CONTROLLER SIGNAL EMIT keresése..."
grep -r "analysis_completed.emit" src/ --include="*.py" -n -A 2 -B 2
echo ""

# 3. ANALYSIS WORKER SIGNAL EMIT keresése - emittálja-e a Worker a signalt?
echo "⚙️ 3. ANALYSIS WORKER SIGNAL EMIT keresése..."
grep -r "analysis_completed" src/gui/workers/ --include="*.py" -n -A 3 -B 3
echo ""

# 4. MAINWINDOW ON_ANALYSIS_COMPLETED keresése - van-e a handler metódus?
echo "🎯 4. MAINWINDOW HANDLER keresése..."
grep -r "_on_analysis_completed" src/gui/main_window.py -n -A 5 -B 5
echo ""

# 5. ANALYTICS VIEW UPDATE_DATA keresése - van-e az update metódus?
echo "📊 5. ANALYTICS VIEW UPDATE keresése..."
grep -r "update_data" src/gui/analytics_view.py -n -A 3 -B 3
echo ""

# 6. WEATHER DATA FLOW keresése - weather_data kulcsszó ahol átadják
echo "🌍 6. WEATHER DATA FLOW keresése..."
grep -r "weather_data" src/gui/ --include="*.py" -n -C 2
echo ""

# 7. MOSCOW KERESÉSE - van-e Moscow specifikus log vagy kód?
echo "🏙️ 7. MOSCOW KERESÉS..."
grep -ri "moscow" src/ --include="*.py" -n
echo ""

# 8. ERROR és EXCEPTION keresése - vannak-e hibák a logokban?
echo "❌ 8. ERROR/EXCEPTION keresése..."
grep -r "error\|Error\|ERROR\|exception\|Exception" src/gui/ --include="*.py" -n -i -C 1
echo ""

# 9. SIGNAL CONNECTION HIBÁS ESETEK keresése
echo "🚨 9. SIGNAL CONNECTION PROBLÉMÁK keresése..."
grep -r "connect.*analysis" src/gui/ --include="*.py" -n -C 2
echo ""

# 10. SIGNAL EMIT HIBÁS ESETEK keresése  
echo "🚨 10. SIGNAL EMIT PROBLÉMÁK keresése..."
grep -r "emit.*analysis" src/gui/ --include="*.py" -n -C 2
echo ""

# 11. DEBUG PRINT keresése - vannak-e debug üzenetek?
echo "🐛 11. DEBUG PRINT keresése..."
grep -r "print.*DEBUG\|print.*debug" src/gui/ --include="*.py" -n -C 1
echo ""

# 12. CONTROLLER CONNECTION keresése - MainWindow -> Controller kapcsolat
echo "🎮 12. CONTROLLER CONNECTION keresése..."
grep -r "controller\." src/gui/main_window.py -n -C 2
echo ""

# 13. WORKER MANAGER keresése - van-e worker manager kapcsolat?
echo "⚙️ 13. WORKER MANAGER keresése..."
grep -r "worker_manager" src/gui/ --include="*.py" -n -C 2
echo ""

# 14. ANALYTICS PANEL keresése - van-e analytics_panel referencia?
echo "📊 14. ANALYTICS PANEL REFERENCIA keresése..."
grep -r "analytics_panel" src/gui/main_window.py -n -C 2
echo ""

# 15. IMPORT HIBÁK keresése - vannak-e import problémák?
echo "📦 15. IMPORT HIBÁK keresése..."
grep -r "import.*analytics\|from.*analytics" src/gui/ --include="*.py" -n
echo ""

echo ""
echo "🎯 === KÖVETKEZŐ LÉPÉSEK ==="
echo "1. Futtasd le ezeket a grep parancsokat"
echo "2. Nézd meg melyik lépésnél szakad meg a signal chain"
echo "3. Ellenőrizd hogy a signal connection és emit parancsok helyesek-e"
echo "4. Keress hiányzó import-okat vagy metódus definíciókat"
echo ""

# 🔍 EXTRA DEBUG PARANCSOK - ha a fentiek nem elegendők

echo "🔍 === EXTRA DEBUG PARANCSOK ==="

# APP CONTROLLER Analysis related keresése
echo "🎮 APP CONTROLLER Analysis keresése..."
grep -r "class AppController" src/gui/app_controller.py -n -A 20 -B 5
echo ""

# ANALYSIS WORKER osztály keresése  
echo "⚙️ ANALYSIS WORKER osztály keresése..."
grep -r "class.*Worker" src/gui/workers/ --include="*.py" -n -A 10
echo ""

# SIGNAL DEFINITION keresése - vannak-e definiálva a signalok?
echo "📡 SIGNAL DEFINITION keresése..."
grep -r "Signal(" src/gui/ --include="*.py" -n -C 1
echo ""

# SLOT DECORATOR keresése - vannak-e @Slot dekorátorok?
echo "🎰 SLOT DECORATOR keresése..."
grep -r "@Slot\|@slot" src/gui/ --include="*.py" -n -C 1
echo ""

echo ""
echo "🎯 === SIGNAL CHAIN DIAGRAM ==="
echo "ELVÁRT MŰKÖDÉS:"
echo "1. ControlPanel.analysis_requested → 2. AppController.handle_analysis_request"
echo "3. AppController → 4. AnalysisWorker.run_analysis"  
echo "5. AnalysisWorker.analysis_completed.emit() → 6. MainWindow._on_analysis_completed_with_city_fix()"
echo "7. MainWindow → 8. AnalyticsView.update_data(weather_data)"
echo ""
echo "GREP-pel keress rá hogy melyik lépés hiányzik! 🕵️"