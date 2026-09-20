import flet as ft

from database.db import conexion
from services import sesion

STOCK_MINIMO = 2


def _usuario_id() -> int | None:
    return (sesion.usuario() or {}).get("id")


# ---------- Consultas ----------
def listar() -> list[dict]:
    uid = _usuario_id()
    if uid is None:
        return []
    with conexion() as conn:
        filas = conn.execute(
            "SELECT * FROM productos WHERE usuario_id = ? ORDER BY nombre",
            (uid,),
        ).fetchall()
    return [dict(f) for f in filas]


def con_stock_bajo() -> list[dict]:
    return [p for p in listar() if p["stock"] <= STOCK_MINIMO]


# ---------- Presentación ----------
def maximo_stock(lista: list[dict]) -> int:
    return max((p["stock"] for p in lista), default=0) or 1


def proporcion(producto: dict, maximo: int) -> float:
    return min(producto["stock"] / max(maximo, 1), 1)


def color_stock(stock: int) -> str:
    if stock <= STOCK_MINIMO:
        return ft.Colors.RED_400
    if stock <= 10:
        return ft.Colors.AMBER_600
    return ft.Colors.GREEN_400


# ---------- Alta ----------
def crear(codigo, nombre, categoria, precio, stock) -> None:
    """Registra un producto. Lanza ValueError con un mensaje para la pantalla."""
    uid = _usuario_id()
    if uid is None:
        raise ValueError("Debes iniciar sesión.")

    codigo = (codigo or "").strip().upper()
    nombre = (nombre or "").strip()
    categoria = (categoria or "").strip()

    if not all([codigo, nombre, categoria]):
        raise ValueError("Completa código, nombre y categoría.")

    try:
        precio = int(str(precio).replace(".", "").replace("$", "").strip())
        stock = int(str(stock).strip())
    except ValueError:
        raise ValueError("Precio y stock deben ser números enteros.")

    if precio <= 0:
        raise ValueError("El precio debe ser mayor que 0.")
    if stock < 0:
        raise ValueError("El stock no puede ser negativo.")

    with conexion() as conn:
        existe = conn.execute(
            "SELECT 1 FROM productos WHERE usuario_id = ? AND codigo = ?",
            (uid, codigo),
        ).fetchone()
        if existe:
            raise ValueError(f"Ya tienes un producto con el código {codigo}.")

        conn.execute(
            """INSERT INTO productos (usuario_id, codigo, nombre, categoria, precio, stock)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (uid, codigo, nombre, categoria, precio, stock),
        )