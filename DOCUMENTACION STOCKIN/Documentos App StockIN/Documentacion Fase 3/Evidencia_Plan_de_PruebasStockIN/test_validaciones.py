"""
╔══════════════════════════════════════════════════════════════╗
║  StockIN — Pruebas de Validaciones de Datos (pytest)        ║
║  Requisitos: RF-01, RF-03, RF-24, RF-29                    ║
║  Verifica: validación de correo, contraseña, teléfono,      ║
║            campos obligatorios de producto y código          ║
╚══════════════════════════════════════════════════════════════╝
"""
import re


# ── Funciones de validación de StockIN ──

def validar_correo(correo: str) -> bool:
    """Valida formato de correo electrónico."""
    patron = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(patron, correo.strip()))


def validar_password(password: str) -> bool:
    """La contraseña debe tener al menos 8 caracteres."""
    return len(password) >= 8


def validar_telefono(telefono: str) -> bool:
    """El teléfono debe tener exactamente 9 dígitos numéricos."""
    limpio = telefono.strip().replace(" ", "")
    return limpio.isdigit() and len(limpio) == 9


def validar_producto(codigo: str, nombre: str, categoria: str) -> bool:
    """Código, nombre y categoría son obligatorios."""
    return all(campo.strip() for campo in [codigo, nombre, categoria])


def normalizar_codigo(codigo: str) -> str:
    """El código del producto se guarda en mayúsculas."""
    return codigo.strip().upper()


def validar_precio(precio) -> bool:
    """El precio debe ser un número no negativo."""
    try:
        return float(precio) >= 0
    except (ValueError, TypeError):
        return False


def validar_stock(stock) -> bool:
    """El stock debe ser un entero no negativo."""
    try:
        return int(stock) >= 0
    except (ValueError, TypeError):
        return False


# ══════════════════════════════════════════════════
# PRUEBAS — RF-01: Validación de registro de cuenta
# ══════════════════════════════════════════════════

class TestValidacionCuenta:
    """RF-01 / HU-01: Validaciones del formulario de registro."""

    def test_correo_valido(self):
        assert validar_correo("juan@correo.cl") is True

    def test_correo_con_puntos(self):
        assert validar_correo("juan.godoy@duoc.cl") is True

    def test_correo_sin_arroba(self):
        assert validar_correo("juancorreo.cl") is False

    def test_correo_sin_dominio(self):
        assert validar_correo("juan@") is False

    def test_correo_vacio(self):
        assert validar_correo("") is False

    def test_correo_con_espacios(self):
        assert validar_correo("  juan@correo.cl  ") is True

    def test_password_valida_8_chars(self):
        assert validar_password("12345678") is True

    def test_password_valida_larga(self):
        assert validar_password("MiClaveSegura2026") is True

    def test_password_corta_5_chars(self):
        assert validar_password("12345") is False

    def test_password_vacia(self):
        assert validar_password("") is False

    def test_telefono_9_digitos(self):
        assert validar_telefono("912345678") is True

    def test_telefono_con_espacios(self):
        assert validar_telefono("9 1234 5678") is True

    def test_telefono_8_digitos(self):
        assert validar_telefono("91234567") is False

    def test_telefono_con_letras(self):
        assert validar_telefono("91234abc9") is False


# ══════════════════════════════════════════════════
# PRUEBAS — RF-03/RF-24: Validación de productos
# ══════════════════════════════════════════════════

class TestValidacionProducto:
    """RF-03 / RF-24 / HU-03: Validaciones al registrar producto."""

    def test_producto_completo(self):
        assert validar_producto("PROD001", "Camiseta azul", "Ropa") is True

    def test_producto_sin_nombre(self):
        assert validar_producto("PROD001", "", "Ropa") is False

    def test_producto_sin_codigo(self):
        assert validar_producto("", "Camiseta", "Ropa") is False

    def test_producto_sin_categoria(self):
        assert validar_producto("PROD001", "Camiseta", "") is False

    def test_producto_todo_vacio(self):
        assert validar_producto("", "", "") is False

    def test_producto_solo_espacios(self):
        assert validar_producto("   ", "Camiseta", "Ropa") is False

    def test_codigo_se_normaliza_mayusculas(self):
        assert normalizar_codigo("prod001") == "PROD001"

    def test_codigo_ya_en_mayusculas(self):
        assert normalizar_codigo("ABC123") == "ABC123"

    def test_codigo_con_espacios(self):
        assert normalizar_codigo("  prod001  ") == "PROD001"

    def test_precio_valido(self):
        assert validar_precio(5000) is True

    def test_precio_cero(self):
        assert validar_precio(0) is True

    def test_precio_negativo(self):
        assert validar_precio(-100) is False

    def test_precio_texto(self):
        assert validar_precio("abc") is False

    def test_stock_valido(self):
        assert validar_stock(50) is True

    def test_stock_cero(self):
        assert validar_stock(0) is True

    def test_stock_negativo(self):
        assert validar_stock(-1) is False

    def test_stock_texto(self):
        assert validar_stock("muchos") is False
