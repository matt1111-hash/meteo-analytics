import os, pathlib, textwrap
from openai import OpenAI

API_KEY = os.environ.get("DEEPSEEK_API_KEY")
if not API_KEY:
    raise SystemExit("DEEPSEEK_API_KEY hiányzik (export a venv activate-ben).")

BASE_URL = "https://api.deepseek.com"
MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-reasoner")
MAX_TOKENS = int(os.environ.get("DEEPSEEK_MAX_TOKENS", "9000"))

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

file_path = input("Add meg a refaktorálandó Python fájl nevét (pl. src/gui/control_panel.py): ").strip()
p = pathlib.Path(file_path)
if not p.is_file():
    raise SystemExit(f"Nincs ilyen fájl: {file_path}")

code = p.read_text(encoding="utf-8")

# Kiemelten fontos sorok kigyűjtése (megőrzendők)
keepers = []
for ln in code.splitlines():
    s = ln.strip()
    if ".emit(" in s or ".connect(" in s:
        keepers.append(s)

KEEP_LIST = "\n".join(keepers) if keepers else "(nincs explicit .emit / .connect sor)"

INVARIANTS = f"""
SZIGORÚ INSTRUKCIÓK – NEM SÉRTHETŐ:
1) A publikus API marad: osztály- és publikus metódusnevek, paraméternevek NE változzanak.
2) MINDEN Qt jelzés és kapcsolat megmarad:
   - Az alábbi sorok (vagy funkcionális ekvivalenseik) KÖTELEZŐEN szerepeljenek a kimenetben:
   ---
{KEEP_LIST}
   ---
   - Ne töröld, ne nevezd át, ne változtasd meg a hívások sorrendjét és argumentumait indok nélkül.
3) Importok maradjanak kompatibilisek; ne adj hozzá új külső függőséget.
4) Viselkedés változatlan; csak belső refaktor: metódusbontás, típushinták, docstringek, PEP8.
5) Ha nyilvánvaló bugot látsz, maximum # TODO megjegyzést tegyél hozzá, API-t nem törhetsz.
KIMENETI FORMA:
- CSAK teljes futtatható kód egyetlen ```python blokkban. Semmi magyarázat, szöveg vagy más blokk.
"""

SYSTEM = (
    "Senior Python refaktoráló vagy, PySide6/PyQt projektekben tapasztalt. "
    "Cél: olvashatóság és karbantarthatóság növelése, miközben az API és Qt jel-lánc érintetlen marad."
)

USER = f"""Refaktoráld az alábbi fájlt az INVARIÁNSOK betartásával.

{INVARIANTS}

FORRÁSKÓD:
```python
{code}
```"""

print(">> Refaktorálás (invariáns-őr) indul…")
resp = client.chat.completions.create(
    model=MODEL,
    messages=[{"role":"system","content": SYSTEM},
              {"role":"user","content": USER}],
    temperature=0.15,
    max_tokens=MAX_TOKENS,
)

out = resp.choices[0].message.content.strip()

# kódfence kivágás
if out.startswith("```"):
    lines = out.splitlines()
    if lines and lines[0].startswith("```python"):
        lines = lines[1:]
    if lines and lines[-1].strip().startswith("```"):
        lines = lines[:-1]
    out = "\n".join(lines)

dst = p.with_suffix(".refactored.py")
dst.write_text(out, encoding="utf-8")
print(f">> Refaktorált fájl elmentve ide: {dst}")

