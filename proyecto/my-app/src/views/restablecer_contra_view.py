import asyncio

import flet as ft

from services.auth import restablecer_password


def restablecer_contra_view(page: ft.Page):
    async def volver(e):
        await page.push_route("/")

    txt_email = ft.TextField(
        label="Correo electrónico",
        border_color=ft.Colors.GREY_700,
        color=ft.Colors.WHITE,
        keyboard_type=ft.KeyboardType.EMAIL,
    )
    txt_telefono = ft.TextField(
        label="Numero telefonico",
        hint_text="912345678",
        border_color=ft.Colors.GREY_700,
        color=ft.Colors.WHITE,
        keyboard_type=ft.KeyboardType.PHONE,
    )
    txt_nueva_password = ft.TextField(
        label="Nueva contraseña",
        password=True,
        can_reveal_password=True,
        border_color=ft.Colors.GREY_700,
        color=ft.Colors.WHITE,
    )

    mensaje = ft.Text("", size=13, color=ft.Colors.RED_400, text_align=ft.TextAlign.CENTER)

    async def restablecer(e):
        mensaje.color = ft.Colors.RED_400
        try:
            restablecer_password(
                txt_email.value,
                txt_telefono.value,
                txt_nueva_password.value,
            )
        except ValueError as err:
            mensaje.value = str(err)
            page.update()
            return

        mensaje.color = ft.Colors.GREEN_400
        mensaje.value = "Contraseña actualizada. Ya puedes iniciar sesión."
        page.update()

        await asyncio.sleep(1.5)
        await page.push_route("/iniciar_sesion_email")

    txt_nueva_password.on_submit = restablecer

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
                        ft.Text("Restablecer Contraseña", size=20,
                                weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                ),
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                ft.Text("Ingresa tu correo y teléfono para verificar tu identidad.",
                        size=12, color=ft.Colors.GREY_400),
                ft.Divider(height=6, color=ft.Colors.TRANSPARENT),
                txt_email,
                txt_telefono,
                txt_nueva_password,
                mensaje,
                ft.Button(
                    content=ft.Text("Restablecer", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    bgcolor=ft.Colors.ORANGE_800,
                    width=280,
                    height=48,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=25)),
                    on_click=restablecer,
                ),
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