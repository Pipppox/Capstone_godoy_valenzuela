from database.db import conexion
from services import sesion

STOCK_MINIMO = 2


def _uid() -> int | None:
    return (sesion.usuario() or {}).get("id")


def resumen() -> dict:
    """Resumen ejecutivo completo para el dashboard."""
    uid = _uid()
    if uid is None:
        return _vacio()

    with conexion() as conn:
        # Total productos
        total = conn.execute(
            "SELECT COUNT(*) AS n FROM productos WHERE usuario_id = ?", (uid,)
        ).fetchone()["n"]

        # Stock bajo
        bajo = conn.execute(
            "SELECT COUNT(*) AS n FROM productos WHERE usuario_id = ? AND stock <= ?",
            (uid, STOCK_MINIMO),
        ).fetchone()["n"]

        # Ventas del día
        dia = conn.execute(
            """SELECT COALESCE(SUM(total), 0) AS monto,
                      COALESCE(SUM(cantidad), 0) AS unidades
               FROM ventas
               WHERE usuario_id = ? AND date(fecha) = date('now', 'localtime')""",
            (uid,),
        ).fetchone()

        # Producto más vendido (todo el tiempo)
        top = conn.execute(
            """SELECT p.nombre, COALESCE(SUM(v.cantidad), 0) AS total_vendido
               FROM ventas v
               JOIN productos p ON p.id = v.producto_id
               WHERE v.usuario_id = ?
               GROUP BY v.producto_id
               ORDER BY total_vendido DESC
               LIMIT 1""",
            (uid,),
        ).fetchone()

        # Producto más vendido de la semana
        top_semana = conn.execute(
            """SELECT p.nombre, COALESCE(SUM(v.cantidad), 0) AS total_vendido
               FROM ventas v
               JOIN productos p ON p.id = v.producto_id
               WHERE v.usuario_id = ?
                 AND date(v.fecha) >= date('now', 'localtime', '-7 days')
               GROUP BY v.producto_id
               ORDER BY total_vendido DESC
               LIMIT 1""",
            (uid,),
        ).fetchone()

        # Ventas últimos 7 días (para gráfico)
        ultimos_7 = conn.execute(
            """SELECT date(fecha) AS dia,
                      COALESCE(SUM(total), 0) AS monto,
                      COALESCE(SUM(cantidad), 0) AS unidades
               FROM ventas
               WHERE usuario_id = ?
                 AND date(fecha) >= date('now', 'localtime', '-7 days')
               GROUP BY date(fecha)
               ORDER BY dia""",
            (uid,),
        ).fetchall()

        # Categorías más vendidas
        categorias = conn.execute(
            """SELECT p.categoria, COALESCE(SUM(v.cantidad), 0) AS total_vendido
               FROM ventas v
               JOIN productos p ON p.id = v.producto_id
               WHERE v.usuario_id = ?
               GROUP BY p.categoria
               ORDER BY total_vendido DESC
               LIMIT 5""",
            (uid,),
        ).fetchall()

                # Mejores lugares de venta
        lugares = conn.execute(
            """SELECT lugar, 
                      COALESCE(SUM(total), 0) AS monto,
                      COALESCE(SUM(cantidad), 0) AS unidades,
                      COUNT(*) AS num_ventas
               FROM ventas
               WHERE usuario_id = ? AND lugar IS NOT NULL AND lugar != ''
               GROUP BY lugar
               ORDER BY monto DESC
               LIMIT 5""",
            (uid,),
        ).fetchall()

        # Top producto por lugar
        top_por_lugar = conn.execute(
            """SELECT v.lugar,
                      p.nombre AS producto,
                      SUM(v.cantidad) AS total_vendido,
                      SUM(v.total) AS monto
               FROM ventas v
               JOIN productos p ON p.id = v.producto_id
               WHERE v.usuario_id = ? AND v.lugar IS NOT NULL AND v.lugar != ''
               GROUP BY v.lugar, v.producto_id
               ORDER BY v.lugar, total_vendido DESC""",
            (uid,),
        ).fetchall()

        # Historial de ventas por lugar y día
        historial_lugares = conn.execute(
            """SELECT date(v.fecha) AS dia,
                      v.lugar,
                      p.nombre AS producto,
                      SUM(v.cantidad) AS unidades,
                      SUM(v.total) AS monto
               FROM ventas v
               JOIN productos p ON p.id = v.producto_id
               WHERE v.usuario_id = ? AND v.lugar IS NOT NULL AND v.lugar != ''
               GROUP BY date(v.fecha), v.lugar, v.producto_id
               ORDER BY date(v.fecha) DESC, monto DESC""",
            (uid,),
        ).fetchall()

    return {
        "total_productos": total,
        "stock_bajo": bajo,
        "ventas_dia_monto": dia["monto"],
        "ventas_dia_unidades": dia["unidades"],
        "top_producto": dict(top) if top else None,
        "top_semana": dict(top_semana) if top_semana else None,
        "ultimos_7_dias": [dict(f) for f in ultimos_7],
        "categorias": [dict(f) for f in categorias],
        "lugares": [dict(f) for f in lugares],
        "top_por_lugar": [dict(f) for f in top_por_lugar],
        "historial_lugares": [dict(f) for f in historial_lugares],
        
    }


def _vacio() -> dict:
    return {
        "total_productos": 0,
        "stock_bajo": 0,
        "ventas_dia_monto": 0,
        "ventas_dia_unidades": 0,
        "top_producto": None,
        "top_semana": None,
        "ultimos_7_dias": [],
        "categorias": [],
        "lugares": [],
        "top_por_lugar": [],
        "historial_lugares": [],
    }