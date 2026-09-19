from database.db import conexion
from services import sesion


def _usuario_id() -> int | None:
    return (sesion.usuario() or {}).get("id")


def registrar(producto_id, cantidad, lugar="") -> dict:
    """Registra una venta y descuenta el stock.
    Devuelve un resumen. Lanza ValueError con un mensaje para la pantalla."""
    uid = _usuario_id()
    if uid is None:
        raise ValueError("Debes iniciar sesión.")

    if not producto_id:
        raise ValueError("Selecciona un producto.")

    try:
        cantidad = int(str(cantidad).strip())
    except (ValueError, TypeError):
        raise ValueError("La cantidad debe ser un número entero.")

    if cantidad <= 0:
        raise ValueError("La cantidad debe ser mayor que 0.")

    with conexion() as conn:
        producto = conn.execute(
            "SELECT * FROM productos WHERE id = ? AND usuario_id = ?",
            (producto_id, uid),
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
               (usuario_id, producto_id, cantidad, precio_unitario, total, lugar)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (uid, producto_id, cantidad, producto["precio"], total,
             (lugar or "").strip() or None),
        )

        conn.execute(
            "UPDATE productos SET stock = stock - ? WHERE id = ?",
            (cantidad, producto_id),
        )

        stock_nuevo = producto["stock"] - cantidad

    return {
        "nombre": producto["nombre"],
        "cantidad": cantidad,
        "total": total,
        "stock_nuevo": stock_nuevo,
    }


def ventas_del_dia() -> dict:
    """Monto y cantidad vendidos hoy (para el dashboard)."""
    uid = _usuario_id()
    if uid is None:
        return {"monto": 0, "unidades": 0}

    with conexion() as conn:
        fila = conn.execute(
            """SELECT COALESCE(SUM(total), 0) AS monto,
                      COALESCE(SUM(cantidad), 0) AS unidades
               FROM ventas
               WHERE usuario_id = ? AND date(fecha) = date('now', 'localtime')""",
            (uid,),
        ).fetchone()

    return {"monto": fila["monto"], "unidades": fila["unidades"]}