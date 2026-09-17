import asyncio

import flet as ft

from services.auth import registrar_usuario


def crear_cuenta_view(page: ft.Page):
    async def volver_login(e):
        await page.push_route("/")

    # Campos
    txt_nombre = ft.TextField(
        label="Nombre",
        border_color=ft.Colors.GREY_700,
        color=ft.Colors.WHITE,
        capitalization=ft.TextCapitalization.WORDS,
    )
    txt_apellido = ft.TextField(
        label="Apellido",
        border_color=ft.Colors.GREY_700,
        color=ft.Colors.WHITE,
        capitalization=ft.TextCapitalization.WORDS,
    )
    txt_email = ft.TextField(
        label="Correo electrónico",
        border_color=ft.Colors.GREY_700,
        color=ft.Colors.WHITE,
        keyboard_type=ft.KeyboardType.EMAIL,
    )
    txt_telefono = ft.TextField(
        label="Numero telefonico",
        border_color=ft.Colors.GREY_700,
        color=ft.Colors.WHITE,
        keyboard_type=ft.KeyboardType.PHONE,
    )
    txt_password = ft.TextField(
        label="Contraseña",
        password=True,
        can_reveal_password=True,
        border_color=ft.Colors.GREY_700,
        color=ft.Colors.WHITE,
    )

    mensaje = ft.Text("", size=13, color=ft.Colors.RED_400, text_align=ft.TextAlign.CENTER)

    async def registrar(e):
        mensaje.color = ft.Colors.RED_400
        try:
            registrar_usuario(
                txt_nombre.value,
                txt_apellido.value,
                txt_email.value,
                txt_telefono.value,
                txt_password.value,
            )
        except ValueError as err:
            mensaje.value = str(err)
            page.update()
            return

        mensaje.color = ft.Colors.GREEN_400
        mensaje.value = "¡Cuenta creada! Ya puedes iniciar sesión."
        btn_registrar.disabled = True
        page.update()

        await asyncio.sleep(1.5)
        await page.push_route("/iniciar_sesion_email")

    btn_registrar = ft.Button(
        content=ft.Text("Registrarse", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
        bgcolor=ft.Colors.ORANGE_800,
        width=280,
        height=48,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=25)),
        on_click=registrar,
    )

    contenido = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK,
                            icon_color=ft.Colors.WHITE,
                            on_click=volver_login,
                        ),
                        ft.Text("Crear Cuenta", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                ),
                txt_nombre,
                txt_apellido,
                txt_email,
                txt_telefono,
                txt_password,
                mensaje,
                btn_registrar,
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