import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

# En el celular Flet entrega una carpeta propia de la app; en tu PC se usa src/storage
_carpeta = os.getenv("FLET_APP_STORAGE_DATA") or str(Path(__file__).resolve().parent.parent / "storage")
DB_PATH = Path(_carpeta) / "stockin.db"


@contextmanager
def conexion():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with conexion() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre        TEXT NOT NULL,
                apellido      TEXT NOT NULL,
                email         TEXT NOT NULL UNIQUE,
                telefono      TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                salt          TEXT NOT NULL,
                creado_en     TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
            )
        """)