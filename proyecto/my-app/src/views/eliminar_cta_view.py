import asyncio

import flet as ft

from services import sesion
from services.auth import eliminar_cuenta


def eliminar_cuenta_view(page: ft.Page):
    usuario = sesion.usuario() or {}

    async def volver(e):
        await page.push_route("/index")

    txt_email = ft.TextField(
        label="Correo electrónico",
        value=usuario.get("email", ""),
        border_color=ft.Colors.GREY_700,
        color=ft.Colors.WHITE,
        keyboard_type=ft.KeyboardType.EMAIL,
    )
    txt_password = ft.TextField(
        label="Contraseña",
        password=True,
        can_reveal_password=True,
        border_color=ft.Colors.GREY_700,
        color=ft.Colors.WHITE,
    )

    mensaje = ft.Text("", size=13, color=ft.Colors.RED_400, text_align=ft.TextAlign.CENTER)

    # ---------- Paneles ----------
    panel_formulario = ft.Column(spacing=0)
    panel_confirmacion = ft.Column(visible=False, spacing=0)

    def mostrar_confirmacion(e):
        if not txt_email.value or not txt_password.value:
            mensaje.value = "Ingresa tu correo y contraseña."
            page.update()
            return
        panel_formulario.visible = False
        panel_confirmacion.visible = True
        page.update()

    def cancelar(e):
        panel_confirmacion.visible = False
        panel_formulario.visible = True
        page.update()

    async def confirmar_eliminar(e):
        mensaje.color = ft.Colors.RED_400
        try:
            eliminar_cuenta(
                txt_email.value,
                txt_password.value,
            )
        except ValueError as err:
            mensaje.value = str(err)
            panel_confirmacion.visible = False
            panel_formulario.visible = True
            page.update()
            return

        sesion.cerrar()
        panel_confirmacion.visible = False
        mensaje.color = ft.Colors.GREEN_400
        mensaje.value = "Cuenta eliminada."
        page.update()

        await asyncio.sleep(1.5)
        await page.push_route("/")

    # ---------- Formulario ----------
    panel_formulario.controls = [
        ft.Text("Confirma tu identidad para continuar.",
                size=12, color=ft.Colors.GREY_400),
        ft.Divider(height=6, color=ft.Colors.TRANSPARENT),
        txt_email,
        ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
        txt_password,
        ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
        mensaje,
        ft.Divider(height=6, color=ft.Colors.TRANSPARENT),
        ft.Button(
            content=ft.Text("Eliminar mi cuenta", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            bgcolor=ft.Colors.RED_700,
            width=280,
            height=48,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=25)),
            on_click=mostrar_confirmacion,
        ),
    ]

    # ---------- Confirmación ----------
    panel_confirmacion.controls = [
        ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color=ft.Colors.RED_400, size=50),
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    ft.Text("¿Deseas eliminar tu cuenta?",
                            size=18, weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER),
                    ft.Divider(height=6, color=ft.Colors.TRANSPARENT),
                    ft.Text("Se eliminarán todos tus productos, ventas y datos de cuenta.\n"
                            "Esta acción es irreversible.",
                            size=12, color=ft.Colors.GREY_400, text_align=ft.TextAlign.CENTER),
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    ft.Button(
                        content=ft.Text("Sí, eliminar", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        bgcolor=ft.Colors.RED_700,
                        width=230,
                        height=46,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=25)),
                        on_click=confirmar_eliminar,
                    ),
                    ft.Divider(height=6, color=ft.Colors.TRANSPARENT),
                    ft.Button(
                        content=ft.Text("No, cancelar", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        bgcolor=ft.Colors.GREY_700,
                        width=230,
                        height=46,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=25)),
                        on_click=cancelar,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,
            ),
            bgcolor=ft.Colors.BLACK,
            border_radius=14,
            padding=30,
        ),
        mensaje,
    ]

    # ---------- Tarjeta ----------
    contenido = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK,
                            icon_color=ft.Colors.WHITE,
                            on_click=volver,
                        ),
                        ft.Text("Eliminar Cuenta", size=20,
                                weight=ft.FontWeight.BOLD, color=ft.Colors.RED_400),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                ),
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color=ft.Colors.AMBER_600, size=40),
                            ft.Text("Esta acción es irreversible.",
                                    size=14, weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER),
                            ft.Text("Se eliminarán todos tus productos, ventas y datos de cuenta.",
                                    size=12, color=ft.Colors.GREY_400, text_align=ft.TextAlign.CENTER),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                    ),
                    bgcolor=ft.Colors.BLACK,
                    border_radius=14,
                    padding=18,
                ),
                ft.Divider(height=6, color=ft.Colors.TRANSPARENT),
                panel_formulario,
                panel_confirmacion,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15,
            scroll=ft.ScrollMode.AUTO,
        ),
        width=360,
        height=680,
        bgcolor=ft.Colors.GREY_900,
        border_radius=40,
        padding=25,
        border=ft.Border.all(2, ft.Colors.GREY_800),
    )

    return ft.Container(
        content=contenido,
        alignment=ft.Alignment.CENTER,
        expand=True,
    )