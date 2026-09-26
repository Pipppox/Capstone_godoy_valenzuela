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


def registrar_usuario(nombre, apellido, email, telefono, password, nombre_empresa="") -> None:
    """Registra al usuario. Lanza ValueError con un mensaje para mostrar en pantalla."""
    nombre = (nombre or "").strip()
    apellido = (apellido or "").strip()
    email = normalizar_email(email)
    telefono = normalizar_telefono(telefono)
    password = password or ""
    nombre_empresa = (nombre_empresa or "").strip()

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
            """INSERT INTO usuarios (nombre, apellido, email, telefono, password_hash, salt, nombre_empresa)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (nombre, apellido, email, telefono, password_hash, salt.hex(), nombre_empresa),
        )
        print(f"[REGISTRO] Guardado: {email} / {telefono}")


# ---------- Login (listo para las vistas de inicio de sesión) ----------
def _login(columna: str, valor: str, password: str) -> dict | None:
    print(f"[LOGIN] Buscando {columna} = {valor!r}")
    with conexion() as conn:
        fila = conn.execute(
            f"SELECT * FROM usuarios WHERE {columna} = ?", (valor,)
        ).fetchone()

    if fila is None:
        print("[LOGIN] No existe un usuario con ese dato")
        return None

    hash_ingresado = _hashear(password or "", bytes.fromhex(fila["salt"]))
    if not hmac.compare_digest(hash_ingresado, fila["password_hash"]):
        print("[LOGIN] Usuario encontrado, pero la contraseña no coincide")
        return None

    print("[LOGIN] OK")
    usuario = dict(fila)
    usuario.pop("password_hash")
    usuario.pop("salt")
    return usuario


def login_con_email(email: str, password: str) -> dict | None:
    return _login("email", normalizar_email(email), password)


def login_con_telefono(telefono: str, password: str) -> dict | None:
    return _login("telefono", normalizar_telefono(telefono), password)

def restablecer_password(email: str, telefono: str, nueva_password: str) -> None:
    """Cambia la contraseña si email + teléfono coinciden."""
    email = normalizar_email(email)
    telefono = normalizar_telefono(telefono)

    if not email or not telefono or not nueva_password:
        raise ValueError("Completa todos los campos.")

    if len(nueva_password) < 8:
        raise ValueError("La contraseña debe tener al menos 8 caracteres.")

    with conexion() as conn:
        fila = conn.execute(
            "SELECT id FROM usuarios WHERE email = ? AND telefono = ?",
            (email, telefono),
        ).fetchone()

        if fila is None:
            raise ValueError("No se encontró una cuenta con esos datos.")

        salt = secrets.token_bytes(16)
        password_hash = _hashear(nueva_password, salt)

        conn.execute(
            "UPDATE usuarios SET password_hash = ?, salt = ? WHERE id = ?",
            (password_hash, salt.hex(), fila["id"]),
        )

def eliminar_cuenta(email: str, password: str) -> None:
    """Elimina la cuenta si la contraseña es correcta."""
    email = normalizar_email(email)

    if not email or not password:
        raise ValueError("Ingresa tu correo y contraseña.")

    with conexion() as conn:
        fila = conn.execute(
            "SELECT * FROM usuarios WHERE email = ?", (email,)
        ).fetchone()

        if fila is None:
            raise ValueError("Cuenta no encontrada.")

        hash_ingresado = _hashear(password, bytes.fromhex(fila["salt"]))
        if not hmac.compare_digest(hash_ingresado, fila["password_hash"]):
            raise ValueError("Contraseña incorrecta.")

        conn.execute("DELETE FROM ventas WHERE usuario_id = ?", (fila["id"],))
        conn.execute("DELETE FROM productos WHERE usuario_id = ?", (fila["id"],))
        conn.execute("DELETE FROM usuarios WHERE id = ?", (fila["id"],))        

def actualizar_foto(usuario_id: int, ruta_foto: str) -> None:
    with conexion() as conn:
        conn.execute(
            "UPDATE usuarios SET foto_perfil = ? WHERE id = ?",
            (ruta_foto, usuario_id),
        )

def actualizar_datos(usuario_id: int, nombre: str, apellido: str, email: str, telefono: str,  nombre_empresa: str = "") -> dict:
    """Actualiza los datos del usuario. Devuelve el usuario actualizado."""
    nombre = (nombre or "").strip()
    apellido = (apellido or "").strip()
    email = normalizar_email(email)
    telefono = normalizar_telefono(telefono)
    nombre_empresa = (nombre_empresa or "").strip()

    if not all([nombre, apellido, email, telefono]):
        raise ValueError("Completa todos los campos.")

    if not EMAIL_RE.match(email):
        raise ValueError("El correo no es válido.")

    if len(telefono) != 9:
        raise ValueError("El teléfono debe tener 9 dígitos.")

    with conexion() as conn:
        duplicado_email = conn.execute(
            "SELECT 1 FROM usuarios WHERE email = ? AND id != ?",
            (email, usuario_id),
        ).fetchone()
        if duplicado_email:
            raise ValueError("Ese correo ya está en uso por otra cuenta.")

        duplicado_tel = conn.execute(
            "SELECT 1 FROM usuarios WHERE telefono = ? AND id != ?",
            (telefono, usuario_id),
        ).fetchone()
        if duplicado_tel:
            raise ValueError("Ese teléfono ya está en uso por otra cuenta.")

        conn.execute(
            """UPDATE usuarios SET nombre = ?, apellido = ?, email = ?, telefono = ?, nombre_empresa = ?
               WHERE id = ?""",
            (nombre, apellido, email, telefono, nombre_empresa, usuario_id),
        )

        fila = conn.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,)).fetchone()

    usuario = dict(fila)
    usuario.pop("password_hash")
    usuario.pop("salt")
    return usuario