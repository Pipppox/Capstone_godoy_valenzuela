"""Preferencias guardadas POR USUARIO (columna en la tabla usuarios).

- Cada usuario tiene su propio modo oscuro/claro.
- Sin sesión iniciada (pantallas de login) la app usa modo oscuro.
"""
from database.db import conexion
from services import sesion


def _asegurar_columna(conn) -> None:
    try:
        conn.execute("ALTER TABLE usuarios ADD COLUMN modo_oscuro INTEGER NOT NULL DEFAULT 1")
    except Exception:
        pass  # la columna ya existe


# ---------- Modo oscuro ----------
def modo_oscuro() -> bool:
    """Modo del usuario conectado. Sin sesión: oscuro."""
    usuario = sesion.usuario()
    if not usuario:
        return True
    try:
        with conexion() as conn:
            _asegurar_columna(conn)
            fila = conn.execute(
                "SELECT modo_oscuro FROM usuarios WHERE id = ?", (usuario["id"],)
            ).fetchone()
        return bool(fila["modo_oscuro"]) if fila else True
    except Exception as err:
        print(f"[PREFERENCIAS] Error al leer el modo: {err!r}")
        return True


def guardar_modo_oscuro(activado: bool) -> None:
    """Guarda el modo en el usuario conectado."""
    usuario = sesion.usuario()
    if not usuario:
        return
    try:
        with conexion() as conn:
            _asegurar_columna(conn)
            conn.execute(
                "UPDATE usuarios SET modo_oscuro = ? WHERE id = ?",
                (1 if activado else 0, usuario["id"]),
            )
        usuario["modo_oscuro"] = 1 if activado else 0
    except Exception as err:
        print(f"[PREFERENCIAS] Error al guardar el modo: {err!r}")