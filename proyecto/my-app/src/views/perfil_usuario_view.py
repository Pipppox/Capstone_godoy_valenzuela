from pathlib import Path

import flet as ft

from services import sesion
from services.auth import actualizar_foto
from components.avatar import AVATARES, construir_avatar, valor_desde_bytes
from views.inventario_view import _obtener_picker


def perfil_usuario_view(page: ft.Page):
    usuario = sesion.usuario() or {}
    nombre = usuario.get("nombre", "Usuario")
    apellido = usuario.get("apellido", "")
    email = usuario.get("email", "")
    empresa = usuario.get("nombre_empresa", "")
    foto_actual = usuario.get("foto_perfil", "")

    async def volver(e):
        await page.push_route("/index")

    async def ir_a_configuracion(e):
        await page.push_route("/configuracion")

    # ---------- Foto de perfil ----------
    picker = _obtener_picker(page)

    img_perfil = construir_avatar(foto_actual)

    contenedor_foto = ft.Container(
        content=img_perfil,
        alignment=ft.Alignment.CENTER,
        on_click=lambda e: mostrar_selector_foto(e),
        ink=True,
    )

    # ---------- Paneles ----------
    panel_principal = ft.Column(spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    panel_confirmar_logout = ft.Column(visible=False, spacing=0,
                                       horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    panel_selector_foto = ft.Column(visible=False, spacing=0,
                                     horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    # ---------- Selector de foto ----------
    mensaje_foto = ft.Text("", size=12, color=ft.Colors.RED_400, text_align=ft.TextAlign.CENTER)
    cargando_foto = ft.ProgressRing(width=18, height=18, stroke_width=2,
                                    color=ft.Colors.ORANGE_800, visible=False)

    def aplicar_foto(valor: str):
        """Guarda la foto, actualiza la sesión y vuelve al perfil."""
        actualizar_foto(usuario["id"], valor)
        usuario["foto_perfil"] = valor
        sesion.iniciar(usuario)  # así las demás pantallas ven la foto nueva
        contenedor_foto.content = construir_avatar(valor)
        mensaje_foto.value = ""
        panel_selector_foto.visible = False
        panel_principal.visible = True
        page.update()

    def seleccionar_avatar(idx):
        def handler(e):
            aplicar_foto(f"icon:{idx}:avatar:predefinido")
        return handler

    async def subir_foto(e):
        mensaje_foto.value = ""
        try:
            archivos = await picker.pick_files(
                dialog_title="Elige tu foto de perfil",
                file_type=ft.FilePickerFileType.IMAGE,
                with_data=True,
                compression_quality=70,  # en el celular reduce el peso de la foto
            )
        except Exception as err:
            print(f"[FOTO] Error al abrir el selector: {err!r}")
            mensaje_foto.value = "No se pudo abrir el selector de imágenes."
            page.update()
            return

        if not archivos:
            return  # el usuario canceló

        cargando_foto.visible = True
        page.update()
        try:
            archivo = archivos[0]
            datos = archivo.bytes
            if datos is None and archivo.path:
                datos = Path(archivo.path).read_bytes()
            valor = valor_desde_bytes(datos)
        except ValueError as err:
            mensaje_foto.value = str(err)
            return
        except Exception as err:
            print(f"[FOTO] Error al leer la imagen: {err!r}")
            mensaje_foto.value = "No se pudo leer la imagen."
            return
        finally:
            cargando_foto.visible = False
            page.update()

        print(f"[FOTO] Foto subida: {archivo.name} ({len(datos) // 1024} KB)")
        aplicar_foto(valor)

    def quitar_foto(e):
        aplicar_foto("")

    def mostrar_selector_foto(e):
        mensaje_foto.value = ""
        panel_principal.visible = False
        panel_selector_foto.visible = True
        page.update()

    def cancelar_selector(e):
        panel_selector_foto.visible = False
        panel_principal.visible = True
        page.update()

    # Grid de avatares
    grid_avatares = ft.Row(
        controls=[
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.CircleAvatar(
                            radius=28,
                            bgcolor=AVATARES[i][1],
                            content=ft.Icon(AVATARES[i][0], color=AVATARES[i][2], size=26),
                        ),
                        ft.Text(AVATARES[i][3], size=9, color=ft.Colors.ON_SURFACE_VARIANT,
                                text_align=ft.TextAlign.CENTER),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=4,
                ),
                on_click=seleccionar_avatar(i),
                ink=True,
                padding=4,
            )
            for i in range(len(AVATARES))
        ],
        wrap=True,
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=10,
        run_spacing=10,
    )

    panel_selector_foto.controls = [
        ft.Row(
            controls=[
                ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color=ft.Colors.ON_SURFACE,
                              on_click=cancelar_selector),
                ft.Text("Cambiar foto", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.ON_SURFACE),
                ft.Container(width=40),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        ft.Divider(height=14, color=ft.Colors.TRANSPARENT),
        ft.Text("Elige un avatar", size=13, color=ft.Colors.ON_SURFACE_VARIANT),
        ft.Divider(height=8, color=ft.Colors.TRANSPARENT),
        ft.Container(
            content=grid_avatares,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            border_radius=14,
            padding=14,
        ),
        ft.Divider(height=16, color=ft.Colors.TRANSPARENT),
        ft.Text("O sube tu propia foto", size=13, color=ft.Colors.ON_SURFACE_VARIANT),
        ft.Divider(height=8, color=ft.Colors.TRANSPARENT),
        ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("JPG, PNG o WEBP · máximo 2 MB", size=11,
                            color=ft.Colors.ON_SURFACE_VARIANT),
                    ft.Row(
                        controls=[
                            ft.Button(
                                content=ft.Row(
                                    controls=[
                                        ft.Icon(ft.Icons.PHOTO_LIBRARY_OUTLINED,
                                                color=ft.Colors.WHITE, size=18),
                                        ft.Text("Subir foto", size=12, weight=ft.FontWeight.BOLD,
                                                color=ft.Colors.WHITE),
                                    ],
                                    spacing=8,
                                    tight=True,
                                ),
                                bgcolor=ft.Colors.ORANGE_800,
                                height=40,
                                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=20)),
                                on_click=subir_foto,
                            ),
                            cargando_foto,
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=10,
                    ),
                    mensaje_foto,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            border_radius=14,
            padding=14,
        ),
        ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
        ft.TextButton(
            content=ft.Text("Quitar foto", size=12, color=ft.Colors.RED_400),
            on_click=quitar_foto,
        ),
    ]

    # ---------- Cerrar sesión con confirmación ----------
    def mostrar_confirmar_logout(e):
        panel_principal.visible = False
        panel_confirmar_logout.visible = True
        page.update()

    def cancelar_logout(e):
        panel_confirmar_logout.visible = False
        panel_principal.visible = True
        page.update()

    async def confirmar_logout(e):
        sesion.cerrar()
        await page.push_route("/")

    panel_confirmar_logout.controls = [
        ft.Divider(height=80, color=ft.Colors.TRANSPARENT),
        ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(ft.Icons.LOGOUT, color=ft.Colors.ORANGE_800, size=50),
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    ft.Text("¿Deseas cerrar sesión?",
                            size=18, weight=ft.FontWeight.BOLD,
                            color=ft.Colors.ON_SURFACE, text_align=ft.TextAlign.CENTER),
                    ft.Divider(height=6, color=ft.Colors.TRANSPARENT),
                    ft.Text("Tendrás que volver a iniciar sesión\npara acceder a tu cuenta.",
                            size=12, color=ft.Colors.ON_SURFACE_VARIANT, text_align=ft.TextAlign.CENTER),
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    ft.Button(
                        content=ft.Text("Sí, cerrar sesión", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        bgcolor=ft.Colors.ORANGE_800,
                        width=230,
                        height=46,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=25)),
                        on_click=confirmar_logout,
                    ),
                    ft.Divider(height=6, color=ft.Colors.TRANSPARENT),
                    ft.Button(
                        content=ft.Text("No, cancelar", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        bgcolor=ft.Colors.GREY_700,
                        width=230,
                        height=46,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=25)),
                        on_click=cancelar_logout,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,
            ),
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            border_radius=14,
            padding=30,
        ),
    ]

    # ---------- Info del usuario ----------
    info_usuario = ft.Column(
        controls=[
            ft.Text(f"{nombre} {apellido}", size=22, weight=ft.FontWeight.BOLD,
                    color=ft.Colors.ON_SURFACE, text_align=ft.TextAlign.CENTER),
            ft.Text(email, size=13, color=ft.Colors.ON_SURFACE_VARIANT,
                    text_align=ft.TextAlign.CENTER),
            ft.Text(empresa if empresa else "Sin emprendimiento", size=12,
                    color=ft.Colors.ORANGE_800, text_align=ft.TextAlign.CENTER,
                    italic=True),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=4,
    )

    # ---------- Encabezado ----------
    encabezado = ft.Row(
        controls=[
            ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                icon_color=ft.Colors.ON_SURFACE,
                on_click=volver,
            ),
            ft.Text("Perfil", size=18, weight=ft.FontWeight.BOLD,
                    color=ft.Colors.ON_SURFACE, text_align=ft.TextAlign.CENTER),
            ft.IconButton(
                icon=ft.Icons.SETTINGS,
                icon_color=ft.Colors.ON_SURFACE_VARIANT,
                icon_size=24,
                tooltip="Configuración",
                on_click=ir_a_configuracion,
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # ---------- Botón cerrar sesión ----------
    btn_logout = ft.Button(
        content=ft.Text("Cerrar sesión", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
        bgcolor=ft.Colors.ORANGE_800,
        width=200,
        height=42,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=25)),
        on_click=mostrar_confirmar_logout,
    )

    # ---------- Texto "toca para cambiar" ----------
    hint_foto = ft.Text("Toca la foto para cambiar", size=10, color=ft.Colors.ON_SURFACE_VARIANT,
                        text_align=ft.TextAlign.CENTER)

    # ---------- Contenido principal ----------
    panel_principal.controls = [
        encabezado,
        ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
        contenedor_foto,
        hint_foto,
        ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
        info_usuario,
        ft.Divider(height=30, color=ft.Colors.TRANSPARENT),
        btn_logout,
    ]

    # ---------- Tarjeta Celular ----------
    tarjeta_movil = ft.Container(
        content=ft.Column(
            controls=[
                panel_principal,
                panel_confirmar_logout,
                panel_selector_foto,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
        ),
        width=360,
        height=680,
        bgcolor=ft.Colors.SURFACE,
        border_radius=40,
        padding=ft.Padding.only(left=22, right=22, top=22, bottom=6),
        border=ft.Border.all(2, ft.Colors.OUTLINE_VARIANT),
    )

    return ft.Container(
        content=tarjeta_movil,
        alignment=ft.Alignment.CENTER,
        expand=True,
    )