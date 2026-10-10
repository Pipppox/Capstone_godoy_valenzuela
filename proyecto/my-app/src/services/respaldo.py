"""Respaldo en la nube (Supabase) cifrado con la contraseña del usuario.

- En la nube NO se guarda el email: solo una huella (hash).
- Los datos viajan y se guardan CIFRADOS: sin la contraseña nadie puede leerlos.
- Solo quien conoce la contraseña puede sobrescribir el respaldo.
"""
import base64
import gzip
import hashlib
import hmac
import json
import os
from datetime import datetime

import requests
from cryptography.fernet import Fernet, InvalidToken
from dotenv import load_dotenv

from database.db import conexion
from services import sesion
from services.auth import _hashear

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
VERSION = 1

CAMPOS_PERFIL = ("nombre", "apellido", "nombre_empresa", "notificaciones", "foto_perfil")


# ============================================================
#  Utilidades
# ============================================================
def _usuario_actual() -> dict:
    usuario = sesion.usuario()
    if not usuario:
        raise ValueError("Debes iniciar sesión.")
    return usuario


def _verificar_password(usuario_id: int, password: str) -> None:
    """Comprueba la contraseña igual que el login (PBKDF2 + salt)."""
    if not password:
        raise ValueError("Ingresa tu contraseña.")
    with conexion() as conn:
        fila = conn.execute(
            "SELECT password_hash, salt FROM usuarios WHERE id = ?", (usuario_id,)
        ).fetchone()
    if fila is None:
        raise ValueError("Cuenta no encontrada.")
    hash_ingresado = _hashear(password, bytes.fromhex(fila["salt"]))
    if not hmac.compare_digest(hash_ingresado, fila["password_hash"]):
        raise ValueError("Contraseña incorrecta.")


def _claves(email: str, password: str) -> tuple[str, str, Fernet]:
    """Deriva de email + contraseña:
    - id:          huella del email (identifica el respaldo sin guardar el email)
    - verificador: prueba de que se conoce la contraseña (no permite descifrar)
    - fernet:      llave de cifrado de los datos
    """
    email = (email or "").strip().lower()
    material = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"),
        f"stockin-respaldo:{email}".encode("utf-8"), 200_000, dklen=64,
    )
    fernet = Fernet(base64.urlsafe_b64encode(material[:32]))
    verificador = hashlib.sha256(material[32:]).hexdigest()
    id_respaldo = hashlib.sha256(f"stockin:{email}".encode("utf-8")).hexdigest()
    return id_respaldo, verificador, fernet


def _rpc(funcion: str, parametros: dict):
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Falta configurar SUPABASE_URL y SUPABASE_KEY en el archivo .env.")
    try:
        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/rpc/{funcion}",
            headers={"apikey": SUPABASE_KEY, "Content-Type": "application/json"},
            json=parametros,
            timeout=20,
        )
    except requests.RequestException as err:
        print(f"[RESPALDO] Error de conexión: {err!r}")
        raise ValueError("Sin conexión a internet. Intenta de nuevo.")

    if r.status_code >= 400:
        print(f"[RESPALDO] Error {r.status_code}: {r.text}")
        raise ValueError("El servidor de respaldo respondió con un error. Intenta más tarde.")
    return r.json()


def _guardar_fecha_local(usuario_id: int, fecha: str) -> None:
    with conexion() as conn:
        try:
            conn.execute("ALTER TABLE usuarios ADD COLUMN ultimo_respaldo TEXT")
        except Exception:
            pass  # la columna ya existe
        conn.execute("UPDATE usuarios SET ultimo_respaldo = ? WHERE id = ?", (fecha, usuario_id))


def ultimo_respaldo() -> str | None:
    """Fecha del último respaldo hecho desde este dispositivo (o None)."""
    usuario = sesion.usuario()
    if not usuario:
        return None
    with conexion() as conn:
        try:
            fila = conn.execute(
                "SELECT ultimo_respaldo FROM usuarios WHERE id = ?", (usuario["id"],)
            ).fetchone()
        except Exception:
            return None
    return fila["ultimo_respaldo"] if fila else None


# ============================================================
#  Empaquetar los datos del usuario
# ============================================================
def _empaquetar(usuario_id: int) -> dict:
    with conexion() as conn:
        perfil = dict(conn.execute(
            f"SELECT {', '.join(CAMPOS_PERFIL)} FROM usuarios WHERE id = ?", (usuario_id,)
        ).fetchone())
        productos = [dict(f) for f in conn.execute(
            """SELECT id, codigo, nombre, categoria, precio, stock, activo, creado_en
               FROM productos WHERE usuario_id = ?""", (usuario_id,)
        ).fetchall()]
        ventas = [dict(f) for f in conn.execute(
            """SELECT producto_id, cantidad, precio_unitario, total, lugar, fecha
               FROM ventas WHERE usuario_id = ?""", (usuario_id,)
        ).fetchall()]
        lugares = [dict(f) for f in conn.execute(
            """SELECT lugar, lat, lng FROM lugares_cache
               WHERE lugar IN (SELECT DISTINCT lugar FROM ventas
                               WHERE usuario_id = ? AND lugar IS NOT NULL)""",
            (usuario_id,),
        ).fetchall()]

    return {
        "version": VERSION,
        "creado": datetime.now().isoformat(timespec="seconds"),
        "perfil": perfil,
        "productos": productos,
        "ventas": ventas,
        "lugares": lugares,
    }


# ============================================================
#  Respaldar
# ============================================================
def respaldar(password: str) -> dict:
    """Sube un respaldo cifrado. Devuelve un resumen para mostrar en pantalla."""
    usuario = _usuario_actual()
    _verificar_password(usuario["id"], password)

    paquete = _empaquetar(usuario["id"])
    id_respaldo, verificador, fernet = _claves(usuario["email"], password)

    comprimido = gzip.compress(json.dumps(paquete, ensure_ascii=False).encode("utf-8"))
    cifrado = fernet.encrypt(comprimido).decode("ascii")

    resultado = _rpc("guardar_respaldo", {
        "p_id": id_respaldo, "p_verificador": verificador, "p_datos": cifrado,
    })
    if resultado == "clave_incorrecta":
        raise ValueError(
            "Ya existe un respaldo de esta cuenta hecho con otra contraseña. "
            "Si la cambiaste, usa la contraseña anterior."
        )

    fecha = datetime.now().strftime("%d-%m-%Y %H:%M")
    _guardar_fecha_local(usuario["id"], fecha)
    return {
        "fecha": fecha,
        "productos": sum(1 for p in paquete["productos"] if p["activo"]),
        "ventas": len(paquete["ventas"]),
    }


# ============================================================
#  Restaurar
# ============================================================
def restaurar(password: str) -> dict:
    """Descarga el respaldo y REEMPLAZA los productos y ventas de esta cuenta."""
    usuario = _usuario_actual()
    _verificar_password(usuario["id"], password)

    id_respaldo, verificador, fernet = _claves(usuario["email"], password)
    filas = _rpc("obtener_respaldo", {"p_id": id_respaldo, "p_verificador": verificador})
    if not filas:
        raise ValueError(
            "No se encontró un respaldo para esta cuenta con esa contraseña. "
            "Si la cambiaste, el respaldo usa la contraseña anterior."
        )

    try:
        paquete = json.loads(gzip.decompress(fernet.decrypt(filas[0]["datos"].encode("ascii"))))
    except (InvalidToken, OSError, ValueError):
        raise ValueError("No se pudo descifrar el respaldo.")

    uid = usuario["id"]
    # Todo en una sola transacción: si algo falla, no se pierde nada
    with conexion() as conn:
        conn.execute("DELETE FROM ventas WHERE usuario_id = ?", (uid,))
        conn.execute("DELETE FROM productos WHERE usuario_id = ?", (uid,))

        nuevo_id = {}
        for p in paquete["productos"]:
            cursor = conn.execute(
                """INSERT INTO productos
                   (usuario_id, codigo, nombre, categoria, precio, stock, activo, creado_en)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (uid, p["codigo"], p["nombre"], p["categoria"], p["precio"],
                 p["stock"], p.get("activo", 1), p["creado_en"]),
            )
            nuevo_id[p["id"]] = cursor.lastrowid

        for v in paquete["ventas"]:
            producto_id = nuevo_id.get(v["producto_id"])
            if producto_id is None:
                continue
            conn.execute(
                """INSERT INTO ventas
                   (usuario_id, producto_id, cantidad, precio_unitario, total, lugar, fecha)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (uid, producto_id, v["cantidad"], v["precio_unitario"],
                 v["total"], v["lugar"], v["fecha"]),
            )

        for l in paquete.get("lugares", []):
            conn.execute(
                "INSERT OR IGNORE INTO lugares_cache (lugar, lat, lng) VALUES (?, ?, ?)",
                (l["lugar"], l["lat"], l["lng"]),
            )

        perfil = paquete.get("perfil", {})
        conn.execute(
            """UPDATE usuarios SET nombre = ?, apellido = ?, nombre_empresa = ?,
                      notificaciones = ?, foto_perfil = ?
               WHERE id = ?""",
            (perfil.get("nombre") or usuario.get("nombre"),
             perfil.get("apellido") or usuario.get("apellido"),
             perfil.get("nombre_empresa") or "",
             perfil.get("notificaciones") or 0,
             perfil.get("foto_perfil"),
             uid),
        )

    # Refrescar la sesión con el perfil restaurado
    for campo in CAMPOS_PERFIL:
        if campo in perfil:
            usuario[campo] = perfil[campo]
    sesion.iniciar(usuario)

    return {
        "fecha": paquete.get("creado", "")[:16].replace("T", " "),
        "productos": sum(1 for p in paquete["productos"] if p.get("activo", 1)),
        "ventas": len(paquete["ventas"]),
    }