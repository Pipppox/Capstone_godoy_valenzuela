"""Foto de perfil del usuario: un solo lugar para dibujarla en toda la app.

Valores posibles de usuarios.foto_perfil:
    ""                         -> ícono genérico
    "icon:<n>:avatar:predefinido" -> uno de los 8 avatares
    "img:<base64>"             -> foto subida desde el celular/computador
    "http..."                  -> URL (versiones anteriores de la app)
"""
import base64

import flet as ft

# Avatares predefinidos: (icono, color_fondo, color_icono, etiqueta)
AVATARES = [
    (ft.Icons.STORE, ft.Colors.ORANGE_800, ft.Colors.WHITE, "Tienda"),
    (ft.Icons.SHOPPING_BAG, ft.Colors.BLUE_600, ft.Colors.WHITE, "Bolsa"),
    (ft.Icons.RESTAURANT, ft.Colors.RED_700, ft.Colors.WHITE, "Comida"),
    (ft.Icons.CHECKROOM, ft.Colors.PURPLE_600, ft.Colors.WHITE, "Ropa"),
    (ft.Icons.HANDYMAN, ft.Colors.AMBER_700, ft.Colors.WHITE, "Herramientas"),
    (ft.Icons.LOCAL_FLORIST, ft.Colors.GREEN_600, ft.Colors.WHITE, "Flores"),
    (ft.Icons.PETS, ft.Colors.BROWN_600, ft.Colors.WHITE, "Mascotas"),
    (ft.Icons.BRUSH, ft.Colors.PINK_600, ft.Colors.WHITE, "Arte"),
]

PREFIJO_IMAGEN = "img:"
TAMANO_MAXIMO = 2 * 1024 * 1024  # 2 MB


def valor_desde_bytes(datos: bytes) -> str:
    """Convierte una imagen a texto para guardarla en la base de datos."""
    if not datos:
        raise ValueError("No se pudo leer la imagen.")
    if len(datos) > TAMANO_MAXIMO:
        mb = len(datos) / 1024 / 1024
        raise ValueError(f"La imagen pesa {mb:.1f} MB. Elige una de máximo 2 MB.")
    return PREFIJO_IMAGEN + base64.b64encode(datos).decode("ascii")


def _circulo_generico(radio: float):
    return ft.CircleAvatar(
        radius=radio,
        bgcolor=ft.Colors.OUTLINE_VARIANT,
        content=ft.Icon(ft.Icons.PERSON, color=ft.Colors.ON_SURFACE_VARIANT, size=radio * 0.9),
    )


def construir_avatar(foto: str | None, radio: float = 55):
    """Dibuja la foto de perfil como círculo del tamaño indicado."""
    foto = foto or ""

    if foto.startswith(PREFIJO_IMAGEN) or foto.startswith("http"):
        src = foto[len(PREFIJO_IMAGEN):] if foto.startswith(PREFIJO_IMAGEN) else foto
        return ft.Container(
            width=radio * 2,
            height=radio * 2,
            border_radius=radio,
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            bgcolor=ft.Colors.OUTLINE_VARIANT,
            content=ft.Image(
                src=src,
                fit=ft.BoxFit.COVER,
                width=radio * 2,
                height=radio * 2,
                error_content=ft.Icon(ft.Icons.PERSON, color=ft.Colors.ON_SURFACE_VARIANT),
            ),
        )

    if foto.startswith("icon:"):
        partes = foto.split(":")
        try:
            idx = int(partes[1])
        except (IndexError, ValueError):
            idx = -1
        if 0 <= idx < len(AVATARES):
            icono, bg, ic, _ = AVATARES[idx]
            return ft.CircleAvatar(
                radius=radio,
                bgcolor=bg,
                content=ft.Icon(icono, color=ic, size=radio * 0.82),
            )

    return _circulo_generico(radio)


def boton_perfil(page: ft.Page, radio: float = 17):
    """Foto de perfil pequeña y clickeable para los encabezados.
    Al tocarla lleva a la pantalla de Perfil."""
    from services import sesion

    usuario = sesion.usuario() or {}

    async def ir_a_perfil(e):
        await page.push_route("/perfil_usuario")

    return ft.Container(
        content=construir_avatar(usuario.get("foto_perfil"), radio),
        on_click=ir_a_perfil,
        ink=True,
        border_radius=radio + 2,
        padding=2,
        tooltip="Perfil",
    )