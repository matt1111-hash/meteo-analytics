# Folium térkép betöltési probléma debug script
# Másold be ezt a Python console-ba vagy futtasd külön fájlként

def debug_folium_map_issue():
    """
    🔍 Folium térkép betöltési problémák diagnosztizálása
    """
    print("🔍 FOLIUM TÉRKÉP DEBUG ELINDÍTVA...")

    # 1. Folium library ellenőrzés
    try:
        import folium
        print(f"✅ Folium version: {folium.__version__}")
    except ImportError as e:
        print(f"❌ Folium hiányzik: {e}")
        print("📥 Telepítsd: pip install folium branca")
        return

    # 2. HTML fájl generálás teszt
    try:
        import os
        import tempfile
        from datetime import datetime

        # Teszt térkép generálás
        test_map = folium.Map(location=[47.1625, 19.5033], zoom_start=7)

        # Temp fájl létrehozás
        temp_dir = tempfile.gettempdir()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_html_path = os.path.join(temp_dir, f"folium_test_{timestamp}.html")

        # Mentés
        test_map.save(test_html_path)

        # Ellenőrzés
        if os.path.exists(test_html_path):
            file_size = os.path.getsize(test_html_path)
            print(f"✅ Teszt HTML generálva: {test_html_path}")
            print(f"📏 Fájl méret: {file_size} bytes")

            if file_size > 1000:
                print("✅ HTML fájl méret megfelelő")
            else:
                print("❌ HTML fájl túl kicsi!")

        else:
            print("❌ HTML fájl nem jött létre!")

    except Exception as e:
        print(f"❌ HTML generálási hiba: {e}")

    # 3. WebEngine beállítások ellenőrzés
    try:
        from PySide6.QtWebEngineCore import QWebEngineSettings
        from PySide6.QtWebEngineWidgets import QWebEngineView
        print("✅ WebEngine modulok elérhetők")
    except ImportError as e:
        print(f"❌ WebEngine modulok hiányoznak: {e}")

    # 4. Temp könyvtár ellenőrzés
    temp_dir = tempfile.gettempdir()
    print(f"📁 Temp könyvtár: {temp_dir}")

    # Folium HTML fájlok keresése
    html_files = []
    try:
        for file in os.listdir(temp_dir):
            if file.startswith('hungarian_folium_map_') and file.endswith('.html'):
                file_path = os.path.join(temp_dir, file)
                file_size = os.path.getsize(file_path)
                file_time = os.path.getmtime(file_path)
                html_files.append({
                    'name': file,
                    'path': file_path,
                    'size': file_size,
                    'time': datetime.fromtimestamp(file_time)
                })

        print(f"🗺️ Folium HTML fájlok találva: {len(html_files)}")
        for file_info in sorted(html_files, key=lambda x: x['time'], reverse=True)[:3]:
            print(f"   📄 {file_info['name']} - {file_info['size']} bytes - {file_info['time']}")

    except Exception as e:
        print(f"❌ Temp könyvtár olvasási hiba: {e}")

    print("\n🔧 JAVASOLT MEGOLDÁSOK:")
    print("1. ⚡ Kattints a 'Kényszerített Újratöltés' gombra")
    print("2. 🔄 Próbáld meg a 'Frissítés' gombot")
    print("3. 🏠 Kattints az 'Alaphelyzet' gombra")
    print("4. 💥 Ha semmi sem működik, próbáld a 'Nuclear Reset' opciót (ha elérhető)")

    # 5. WebEngine specific debug
    print("\n🌐 WEBENGINE DEBUG TANÁCSOK:")
    print("- Ellenőrizd a console-t JavaScript hibákért")
    print("- Nézd meg, hogy van-e 'file://' protokoll korlátozás")
    print("- Próbáld meg más browser engine-nel (ha elérhető)")

# Futtatás
if __name__ == "__main__":
    debug_folium_map_issue()
else:
    debug_folium_map_issue()
