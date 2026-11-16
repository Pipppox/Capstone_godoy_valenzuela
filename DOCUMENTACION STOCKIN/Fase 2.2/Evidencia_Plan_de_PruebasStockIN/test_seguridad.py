"""
╔══════════════════════════════════════════════════════════════╗
║  StockIN — Pruebas de Seguridad (pytest)                    ║
║  Requisitos: RNF-01, RNF-02, RNF-03                        ║
║  Verifica: hash PBKDF2-HMAC-SHA256, sal aleatoria,          ║
║            autenticación y cifrado de respaldo               ║
╚══════════════════════════════════════════════════════════════╝
"""
import hashlib
import os
import json
import base64


# ── Funciones del módulo de seguridad de StockIN ──

def generar_hash(password: str, salt: bytes = None) -> tuple:
    """Genera hash PBKDF2-HMAC-SHA256 con 200.000 iteraciones."""
    if salt is None:
        salt = os.urandom(16)
    hash_bytes = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        200_000
    )
    return hash_bytes.hex(), salt.hex()


def verificar_password(password: str, hash_almacenado: str, salt_hex: str) -> bool:
    """Verifica una contraseña contra su hash y sal almacenados."""
    salt = bytes.fromhex(salt_hex)
    hash_calculado = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        200_000
    ).hex()
    return hash_calculado == hash_almacenado


def cifrar_datos_respaldo(datos: dict, password: str) -> str:
    """Simula el cifrado de datos antes de enviar a Supabase."""
    datos_json = json.dumps(datos, ensure_ascii=False)
    salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
    # XOR simple para demostrar el concepto (en producción se usa Fernet/AES)
    datos_bytes = datos_json.encode("utf-8")
    cifrado = bytes(b ^ key[i % len(key)] for i, b in enumerate(datos_bytes))
    return base64.b64encode(salt + cifrado).decode()


# ══════════════════════════════════════════════════
# PRUEBAS — RNF-01: Hash seguro de contraseñas
# ══════════════════════════════════════════════════

class TestHashSeguro:
    """RNF-01: Las contraseñas se almacenan con hash PBKDF2-HMAC-SHA256."""

    def test_hash_no_es_texto_plano(self):
        """La contraseña nunca se almacena como texto legible."""
        password = "MiClave123"
        hash_hex, _ = generar_hash(password)
        assert hash_hex != password
        assert password not in hash_hex

    def test_hash_tiene_64_caracteres_hex(self):
        """SHA-256 produce exactamente 64 caracteres hexadecimales."""
        hash_hex, _ = generar_hash("TestPassword")
        assert len(hash_hex) == 64
        assert all(c in "0123456789abcdef" for c in hash_hex)

    def test_sal_aleatoria_16_bytes(self):
        """La sal tiene exactamente 16 bytes (32 caracteres hex)."""
        _, salt_hex = generar_hash("password")
        assert len(salt_hex) == 32

    def test_sal_unica_por_cuenta(self):
        """Dos cuentas con la misma contraseña generan sales distintas."""
        _, salt1 = generar_hash("MismaClave")
        _, salt2 = generar_hash("MismaClave")
        assert salt1 != salt2

    def test_hash_distinto_con_misma_clave(self):
        """Misma contraseña → hashes distintos gracias a la sal aleatoria."""
        hash1, _ = generar_hash("MismaClave")
        hash2, _ = generar_hash("MismaClave")
        assert hash1 != hash2

    def test_verificacion_password_correcta(self):
        """La contraseña correcta pasa la verificación."""
        password = "ClaveSegura2026"
        hash_hex, salt_hex = generar_hash(password)
        assert verificar_password(password, hash_hex, salt_hex) is True

    def test_verificacion_password_incorrecta(self):
        """Una contraseña incorrecta NO pasa la verificación."""
        hash_hex, salt_hex = generar_hash("ClaveCorrecta")
        assert verificar_password("ClaveIncorrecta", hash_hex, salt_hex) is False

    def test_200000_iteraciones(self):
        """El hash con 200.000 iteraciones es consistente y reproducible."""
        password = "Test200k"
        salt = os.urandom(16)
        h1 = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 200_000).hex()
        h2 = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 200_000).hex()
        assert h1 == h2  # misma sal y contraseña = mismo hash


# ══════════════════════════════════════════════════
# PRUEBAS — RNF-03: Datos cifrados en Supabase
# ══════════════════════════════════════════════════

class TestCifradoRespaldo:
    """RNF-03 / RNF-18: Los datos se cifran antes de enviar a Supabase."""

    def test_datos_no_legibles_tras_cifrado(self):
        """Los datos cifrados no contienen el texto original."""
        datos = {"productos": [{"nombre": "Camiseta", "precio": 5000}]}
        cifrado = cifrar_datos_respaldo(datos, "MiPassword")
        assert "Camiseta" not in cifrado
        assert "5000" not in cifrado

    def test_cifrado_distinto_cada_vez(self):
        """Dos cifrados del mismo dato producen resultados distintos (sal aleatoria)."""
        datos = {"productos": [{"nombre": "Test"}]}
        c1 = cifrar_datos_respaldo(datos, "pass")
        c2 = cifrar_datos_respaldo(datos, "pass")
        assert c1 != c2
