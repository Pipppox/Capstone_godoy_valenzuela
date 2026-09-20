import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent   # .../my-app/src
PROYECTO_DIR = SRC_DIR.parent                       # .../my-app


def _carpeta_datos() -> Path:
    """En el celular usa la carpeta que entrega Flet.
    En desarrollo, si esa carpeta cae dentro de src/, usa my-app/storage
    para que la recarga automática (-r) no reinicie la app al guardar."""
    env = os.getenv("FLET_APP_STORAGE_DATA")
    if env:
        ruta = Path(env).resolve()
        if not ruta.is_relative_to(SRC_DIR):
            return ruta
    return PROYECTO_DIR / "storage"


DB_PATH = _carpeta_datos() / "stockin.db"


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
        conn.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                codigo     TEXT NOT NULL,
                nombre     TEXT NOT NULL,
                categoria  TEXT NOT NULL,
                precio     INTEGER NOT NULL,
                stock      INTEGER NOT NULL,
                creado_en  TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
                UNIQUE (usuario_id, codigo),
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ventas (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id     INTEGER NOT NULL,
                producto_id    INTEGER NOT NULL,
                cantidad       INTEGER NOT NULL,
                precio_unitario INTEGER NOT NULL,
                total          INTEGER NOT NULL,
                lugar          TEXT,
                fecha          TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
                FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE CASCADE
            )
        """)
        filas = conn.execute("SELECT id, email, telefono FROM usuarios").fetchall()
        print(f"[DB] Archivo: {DB_PATH}")
        print(f"[DB] Usuarios registrados: {[dict(f) for f in filas]}")


        