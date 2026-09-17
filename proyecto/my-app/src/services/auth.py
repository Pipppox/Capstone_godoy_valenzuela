import hashlib
import hmac
import re
import secrets

from database.db import conexion

ITERACIONES = 200_000
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


# ---------- Utilidades ----------
def _hashear(password: str, salt: bytes) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, ITERACIONES).hex()


def normalizar_telefono(telefono: str) -> str:
    """Deja solo dígitos y quita el +56 si viene incluido."""
    digitos = re.sub(r"\D", "", telefono or "")
    if digitos.startswith("56") and len(digitos) == 11:
        digitos = digitos[2:]
    return digitos


def normalizar_email(email: str) -> str:
    return (email or "").strip().lower()


# ---------- Registro ----------
def _validar_registro(nombre, apellido, email, telefono, password) -> str | None:
    if not all([nombre, apellido, email, telefono, password]):
        return "Completa todos los campos."
    if not EMAIL_RE.match(email):
        return "El correo no es válido."
    if len(telefono) != 9:
        return "El teléfono debe tener 9 dígitos (ej: 912345678)."
    if len(password) < 8:
        return "La contraseña debe tener al menos 8 caracteres."
    return None


def registrar_usuario(nombre, apellido, email, telefono, password) -> None:
    """Registra al usuario. Lanza ValueError con un mensaje para mostrar en pantalla."""
    nombre = (nombre or "").strip()
    apellido = (apellido or "").strip()
    email = normalizar_email(email)
    telefono = normalizar_telefono(telefono)
    password = password or ""

    error = _validar_registro(nombre, apellido, email, telefono, password)
    if error:
        raise ValueError(error)

    salt = secrets.token_bytes(16)
    password_hash = _hashear(password, salt)

    with conexion() as conn:
        if conn.execute("SELECT 1 FROM usuarios WHERE email = ?", (email,)).fetchone():
            raise ValueError("Ese correo ya está registrado.")
        if conn.execute("SELECT 1 FROM usuarios WHERE telefono = ?", (telefono,)).fetchone():
            raise ValueError("Ese teléfono ya está registrado.")

        conn.execute(
            """INSERT INTO usuarios (nombre, apellido, email, telefono, password_hash, salt)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (nombre, apellido, email, telefono, password_hash, salt.hex()),
        )


# ---------- Login (listo para las vistas de inicio de sesión) ----------
def _login(columna: str, valor: str, password: str) -> dict | None:
    with conexion() as conn:
        fila = conn.execute(
            f"SELECT * FROM usuarios WHERE {columna} = ?", (valor,)
        ).fetchone()

    if fila is None:
        return None

    hash_ingresado = _hashear(password or "", bytes.fromhex(fila["salt"]))
    if not hmac.compare_digest(hash_ingresado, fila["password_hash"]):
        return None

    usuario = dict(fila)
    usuario.pop("password_hash")
    usuario.pop("salt")
    return usuario


def login_con_email(email: str, password: str) -> dict | None:
    return _login("email", normalizar_email(email), password)


def login_con_telefono(telefono: str, password: str) -> dict | None:
    return _login("telefono", normalizar_telefono(telefono), password)