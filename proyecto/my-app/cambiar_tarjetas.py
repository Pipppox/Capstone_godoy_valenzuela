import re
import shutil
import py_compile
from pathlib import Path
from datetime import datetime

carpeta = Path("src/views")
respaldo = Path(f"respaldo_vistas_{datetime.now():%Y%m%d_%H%M%S}")
respaldo.mkdir()

for archivo in sorted(carpeta.glob("*.py")):
    original = archivo.read_text(encoding="utf-8")

    nuevo = re.sub(r"\bwidth\s*=\s*360\s*,", "expand=True,", original)
    nuevo = re.sub(r"height\s*=\s*680\s*,\s*", "", nuevo)

    if nuevo == original:
        continue

    shutil.copy2(archivo, respaldo / archivo.name)
    archivo.write_text(nuevo, encoding="utf-8")

    try:
        py_compile.compile(str(archivo), doraise=True)
        print(f"OK: {archivo.name}")
    except py_compile.PyCompileError as err:
        shutil.copy2(respaldo / archivo.name, archivo)
        print(f"REVERTIDO: {archivo.name} -> {err}")

print(f"\nRespaldo en: {respaldo.resolve()}")