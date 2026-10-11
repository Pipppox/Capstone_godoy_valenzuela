"""Sesión del usuario.

La sesión vive en memoria (rápido) y además se guarda en la base local,
para que al reabrir la app (o si se reinicia) el usuario siga conectado.
Solo se borra al presionar "Cerrar sesión" o al eliminar la cuenta.
"""
from database.db import conexion

_usuario_actual: dict | None = None


def _asegurar_tabla(conn) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sesion_local (
            id         INTEGER PRIMARY KEY CHECK (id = 1),
            usuario_id INTEGER NOT NULL,
            iniciada   TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
        )
    """)


def iniciar(usuario: dict) -> None:
    """Activa la sesión y la recuerda en el dispositivo."""
    global _usuario_actual
    _usuario_actual = usuario
    try:
        with conexion() as conn:
            _asegurar_tabla(conn)
            conn.execute(
                "INSERT OR REPLACE INTO sesion_local (id, usuario_id) VALUES (1, ?)",
                (usuario["id"],),
            )
    except Exception as err:
        print(f"[SESION] No se pudo recordar la sesión: {err!r}")


def cerrar() -> None:
    """Cierra la sesión y la olvida del dispositivo."""
    global _usuario_actual
    _usuario_actual = None
    try:
        with conexion() as conn:
            _asegurar_tabla(conn)
            conn.execute("DELETE FROM sesion_local")
    except Exception as err:
        print(f"[SESION] No se pudo borrar la sesión guardada: {err!r}")


def restaurar() -> bool:
    """Al abrir la app: si había una sesión guardada, la vuelve a activar."""
    global _usuario_actual
    try:
        with conexion() as conn:
            _asegurar_tabla(conn)
            fila = conn.execute(
                """SELECT u.* FROM sesion_local s
                   JOIN usuarios u ON u.id = s.usuario_id
                   WHERE s.id = 1"""
            ).fetchone()
    except Exception as err:
        print(f"[SESION] No se pudo restaurar la sesión: {err!r}")
        return False

    if fila is None:
        return False

    usuario = dict(fila)
    usuario.pop("password_hash", None)
    usuario.pop("salt", None)
    _usuario_actual = usuario
    print(f"[SESION] Sesión restaurada: {usuario.get('email')}")
    return True


def usuario() -> dict | None:
    return _usuario_actual


def activa() -> bool:
    return _usuario_actual is not None