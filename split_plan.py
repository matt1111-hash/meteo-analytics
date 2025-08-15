import os
import pathlib
from openai import OpenAI

API_KEY = os.environ.get("DEEPSEEK_API_KEY")
if not API_KEY:
    raise SystemExit("DEEPSEEK_API_KEY hiányzik (export a venv activate-ben).")

BASE_URL = "https://api.deepseek.com"
MODEL = "deepseek-reasoner"  # gondolkodós mód

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

file_path = "src/gui/control_panel.py"
p = pathlib.Path(file_path)
if not p.is_file():
    raise SystemExit(f"Nincs ilyen fájl: {file_path}")

code = p.read_text(encoding="utf-8")

system_prompt = (
    "Te egy tapasztalt Python szoftver-architekt vagy, "
    "PySide6/PyQt GUI projektekben jártas. "
    "Cél: a nagy, monolit kód feldarabolása kezelhető, logikailag koherens modulokra."
)

user_prompt = f"""
Ez a fájl túl nagy és nehezen karbantartható.
Olvasd át és javasolj egy bontási tervet.

Adj egy listát:
- Új fájlok neve
- Fő felelősségi kör (responsibility)
- Becsült sorhossz (max 400 sor/fájl ajánlott)
- Melyik részek kerüljenek át (osztályok, metódusok, funkciók)

A cél:
- Könnyebb karbantartás
- Egyértelmű felelősségi határok
- Publikus API és Signal/Slot kapcsolatok sértetlensége

Forráskód:
{code}
"""

resp = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ],
    temperature=0.2,
    max_tokens=4000
)

print(resp.choices[0].message.content)

