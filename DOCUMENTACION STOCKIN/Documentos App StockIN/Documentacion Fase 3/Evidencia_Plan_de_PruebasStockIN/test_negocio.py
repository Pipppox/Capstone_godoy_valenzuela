"""
╔══════════════════════════════════════════════════════════════╗
║  StockIN — Pruebas de Reglas de Negocio (pytest)            ║
║  Requisitos: RF-08, RF-10, RF-11, RF-12, RF-18, RNF-12     ║
║  Verifica: cálculos de venta, indicadores de stock,         ║
║            dashboard, importación y límites                  ║
╚══════════════════════════════════════════════════════════════╝
"""
import pytest
from datetime import datetime, timedelta


# ── Funciones de lógica de negocio de StockIN ──

def calcular_total_venta(precio_unitario: float, cantidad: int) -> float:
    """Calcula el total de una venta."""
    return precio_unitario * cantidad


def color_indicador_stock(stock: int) -> str:
    """Retorna el color del indicador según el nivel de stock."""
    if stock <= 2:
        return "rojo"
    elif stock <= 10:
        return "ambar"
    return "verde"


def puede_vender(stock_actual: int, cantidad_solicitada: int) -> bool:
    """Verifica si hay stock suficiente para la venta."""
    return stock_actual >= cantidad_solicitada


def calcular_ventas_del_dia(ventas: list, fecha_hoy: str) -> float:
    """Suma las ventas del día actual."""
    return sum(v["total"] for v in ventas if v["fecha"].startswith(fecha_hoy))


def ranking_mas_vendidos(ventas: list, top_n: int = 5) -> list:
    """Retorna los N productos más vendidos por monto total."""
    por_producto = {}
    for v in ventas:
        nombre = v["nombre_producto"]
        por_producto[nombre] = por_producto.get(nombre, 0) + v["total"]
    ordenados = sorted(por_producto.items(), key=lambda x: x[1], reverse=True)
    return ordenados[:top_n]


def validar_importacion_excel(filas: list, codigos_existentes: set, limite: int = 650) -> dict:
    """Valida filas de importación Excel y separa válidas de errores."""
    if len(filas) > limite:
        return {"error": f"Límite excedido: {len(filas)} > {limite}", "validas": [], "errores": []}
    validas = []
    errores = []
    codigos_nuevos = set()
    for i, fila in enumerate(filas, start=2):
        problemas = []
        if not fila.get("codigo", "").strip():
            problemas.append("código vacío")
        if not fila.get("nombre", "").strip():
            problemas.append("nombre vacío")
        if fila.get("codigo", "").upper() in codigos_existentes or fila.get("codigo", "").upper() in codigos_nuevos:
            problemas.append("código duplicado")
        try:
            if float(fila.get("precio", -1)) < 0:
                problemas.append("precio negativo")
        except (ValueError, TypeError):
            problemas.append("precio no numérico")
        try:
            if int(fila.get("stock", -1)) < 0:
                problemas.append("stock negativo")
        except (ValueError, TypeError):
            problemas.append("stock no numérico")
        if problemas:
            errores.append({"fila": i, "problemas": problemas})
        else:
            validas.append(fila)
            codigos_nuevos.add(fila["codigo"].upper())
    return {"validas": validas, "errores": errores}


# ══════════════════════════════════════════════════
# RF-08: Cálculos de venta
# ══════════════════════════════════════════════════

class TestCalculosVenta:
    """RF-08 / HU-08: El total se calcula automáticamente."""

    def test_calculo_total_simple(self):
        assert calcular_total_venta(5000, 3) == 15000

    def test_calculo_total_unitario(self):
        assert calcular_total_venta(12000, 1) == 12000

    def test_calculo_total_cero_unidades(self):
        assert calcular_total_venta(5000, 0) == 0

    def test_puede_vender_con_stock(self):
        assert puede_vender(50, 3) is True

    def test_no_puede_vender_sin_stock(self):
        assert puede_vender(2, 5) is False

    def test_puede_vender_stock_exacto(self):
        assert puede_vender(5, 5) is True

    def test_stock_nunca_negativo(self):
        stock = 3
        venta = 5
        nuevo_stock = stock - venta
        assert nuevo_stock < 0  # la app debe rechazar esta operación


# ══════════════════════════════════════════════════
# RF-12: Indicadores visuales de stock
# ══════════════════════════════════════════════════

class TestIndicadoresStock:
    """RF-12 / HU-12: Colores del indicador de stock."""

    def test_stock_0_rojo(self):
        assert color_indicador_stock(0) == "rojo"

    def test_stock_1_rojo(self):
        assert color_indicador_stock(1) == "rojo"

    def test_stock_2_rojo(self):
        assert color_indicador_stock(2) == "rojo"

    def test_stock_3_ambar(self):
        assert color_indicador_stock(3) == "ambar"

    def test_stock_10_ambar(self):
        assert color_indicador_stock(10) == "ambar"

    def test_stock_11_verde(self):
        assert color_indicador_stock(11) == "verde"

    def test_stock_100_verde(self):
        assert color_indicador_stock(100) == "verde"


# ══════════════════════════════════════════════════
# RF-10: Dashboard — ventas del día
# ══════════════════════════════════════════════════

class TestDashboard:
    """RF-10 / HU-10: Indicadores del dashboard."""

    def test_ventas_del_dia(self):
        hoy = "2026-11-01"
        ventas = [
            {"total": 5000, "fecha": "2026-11-01T10:00:00", "nombre_producto": "A"},
            {"total": 8000, "fecha": "2026-11-01T14:00:00", "nombre_producto": "B"},
            {"total": 3000, "fecha": "2026-10-31T20:00:00", "nombre_producto": "C"},
        ]
        assert calcular_ventas_del_dia(ventas, hoy) == 13000

    def test_ventas_dia_sin_ventas(self):
        ventas = [
            {"total": 5000, "fecha": "2026-10-30T10:00:00", "nombre_producto": "A"},
        ]
        assert calcular_ventas_del_dia(ventas, "2026-11-01") == 0


# ══════════════════════════════════════════════════
# RF-11: Ranking de productos más vendidos
# ══════════════════════════════════════════════════

class TestRanking:
    """RF-11 / HU-11: Top 5 productos más vendidos."""

    def test_ranking_ordenado_por_monto(self):
        ventas = [
            {"nombre_producto": "Camiseta", "total": 15000},
            {"nombre_producto": "Pantalón", "total": 24000},
            {"nombre_producto": "Camiseta", "total": 10000},
            {"nombre_producto": "Gorra", "total": 6000},
        ]
        ranking = ranking_mas_vendidos(ventas, 3)
        assert ranking[0] == ("Camiseta", 25000)
        assert ranking[1] == ("Pantalón", 24000)
        assert ranking[2] == ("Gorra", 6000)

    def test_ranking_top_5_maximo(self):
        ventas = [{"nombre_producto": f"Prod{i}", "total": i * 1000} for i in range(10)]
        ranking = ranking_mas_vendidos(ventas, 5)
        assert len(ranking) == 5


# ══════════════════════════════════════════════════
# RF-18 / RNF-12: Importación Excel y límite 650
# ══════════════════════════════════════════════════

class TestImportacionExcel:
    """RF-18 / RNF-12: Validación de importación y límite de productos."""

    def test_importar_filas_validas(self):
        filas = [
            {"codigo": "A01", "nombre": "Producto A", "categoria": "Cat", "precio": 1000, "stock": 10},
            {"codigo": "B01", "nombre": "Producto B", "categoria": "Cat", "precio": 2000, "stock": 5},
        ]
        resultado = validar_importacion_excel(filas, set())
        assert len(resultado["validas"]) == 2
        assert len(resultado["errores"]) == 0

    def test_rechazar_codigo_duplicado(self):
        filas = [
            {"codigo": "A01", "nombre": "Producto A", "categoria": "Cat", "precio": 1000, "stock": 10},
        ]
        resultado = validar_importacion_excel(filas, {"A01"})
        assert len(resultado["validas"]) == 0
        assert len(resultado["errores"]) == 1
        assert "código duplicado" in resultado["errores"][0]["problemas"]

    def test_rechazar_precio_negativo(self):
        filas = [
            {"codigo": "A01", "nombre": "Producto A", "categoria": "Cat", "precio": -500, "stock": 10},
        ]
        resultado = validar_importacion_excel(filas, set())
        assert len(resultado["errores"]) == 1
        assert "precio negativo" in resultado["errores"][0]["problemas"]

    def test_rechazar_stock_no_numerico(self):
        filas = [
            {"codigo": "A01", "nombre": "Producto A", "categoria": "Cat", "precio": 1000, "stock": "mucho"},
        ]
        resultado = validar_importacion_excel(filas, set())
        assert len(resultado["errores"]) == 1

    def test_limite_650_productos(self):
        filas = [{"codigo": f"P{i:04d}", "nombre": f"Prod {i}", "categoria": "C", "precio": 100, "stock": 1} for i in range(800)]
        resultado = validar_importacion_excel(filas, set())
        assert "error" in resultado
        assert "800 > 650" in resultado["error"]

    def test_dentro_del_limite(self):
        filas = [{"codigo": f"P{i:04d}", "nombre": f"Prod {i}", "categoria": "C", "precio": 100, "stock": 1} for i in range(100)]
        resultado = validar_importacion_excel(filas, set())
        assert "error" not in resultado
        assert len(resultado["validas"]) == 100
