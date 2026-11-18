from database.db import conexion
from services import sesion


def _usuario_id() -> int | None:
    return (sesion.usuario() or {}).get("id_usuario")


def registrar(id_producto, cantidad, lugar="") -> dict:
    """Registra una venta y descuenta el stock.
    Devuelve un resumen. Lanza ValueError con un mensaje para la pantalla.
    La geocodificación del lugar la hace la vista (CampoDireccion) antes de llamar aquí."""
    uid = _usuario_id()
    if uid is None:
        raise ValueError("Debes iniciar sesión.")

    if not id_producto:
        raise ValueError("Selecciona un producto.")

    try:
        cantidad = int(str(cantidad).strip())
    except (ValueError, TypeError):
        raise ValueError("La cantidad debe ser un número entero.")

    if cantidad <= 0:
        raise ValueError("La cantidad debe ser mayor que 0.")

    with conexion() as conn:
        producto = conn.execute(
            "SELECT * FROM productos WHERE id_producto = ? AND id_usuario = ? AND activo = 1",
            (id_producto, uid),
        ).fetchone()

        if producto is None:
            raise ValueError("El producto no existe.")

        if producto["stock"] < cantidad:
            raise ValueError(
                f'Solo tienes {producto["stock"]} unidades de {producto["nombre"]}.'
            )

        total = producto["precio"] * cantidad

        conn.execute(
            """INSERT INTO ventas
               (id_usuario, id_producto, cantidad, precio_unitario, total, lugar)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (uid, id_producto, cantidad, producto["precio"], total,
             (lugar or "").strip() or None),
        )

        conn.execute(
            "UPDATE productos SET stock = stock - ? WHERE id_producto = ?",
            (cantidad, id_producto),
        )

        stock_nuevo = producto["stock"] - cantidad

    return {
        "nombre": producto["nombre"],
        "cantidad": cantidad,
        "total": total,
        "stock_nuevo": stock_nuevo,
    }


def ventas_del_dia() -> dict:
    """Monto y cantidad vendidos hoy (para el dashboard).
    Incluye ventas de productos eliminados: la venta ocurrió igual."""
    uid = _usuario_id()
    if uid is None:
        return {"monto": 0, "unidades": 0}

    with conexion() as conn:
        fila = conn.execute(
            """SELECT COALESCE(SUM(total), 0) AS monto,
                      COALESCE(SUM(cantidad), 0) AS unidades
               FROM ventas
               WHERE id_usuario = ? AND date(fecha) = date('now', 'localtime')""",
            (uid,),
        ).fetchone()

    return {"monto": fila["monto"], "unidades": fila["unidades"]}

def limpiar_historial(id_usuario: int) -> int:
    """Borra todas las ventas del usuario. Los productos no se tocan."""
    with conexion() as conn:
        cursor = conn.execute(
            "DELETE FROM ventas WHERE id_usuario = ?",
            (id_usuario,),
        )
        return cursor.rowcount