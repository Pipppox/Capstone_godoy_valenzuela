import asyncio

import flet as ft

from services.auth import registrar_usuario
from components.terminos import panel_terminos


def crear_cuenta_view(page: ft.Page):
    async def volver_login(e):
        await page.push_route("/")

    async def ir_a_restablecer(e):
        await page.push_route("/restablecer_contra")

    # Campos
    txt_nombre = ft.TextField(
        label="Nombre",
        border_color=ft.Colors.OUTLINE,
        color=ft.Colors.ON_SURFACE,
        capitalization=ft.TextCapitalization.WORDS,
    )
    txt_apellido = ft.TextField(
        label="Apellido",
        border_color=ft.Colors.OUTLINE,
        color=ft.Colors.ON_SURFACE,
        capitalization=ft.TextCapitalization.WORDS,
    )
    txt_email = ft.TextField(
        label="Correo electrónico",
        border_color=ft.Colors.OUTLINE,
        color=ft.Colors.ON_SURFACE,
        keyboard_type=ft.KeyboardType.EMAIL,
    )
    txt_telefono = ft.TextField(
        label="Numero telefonico",
        border_color=ft.Colors.OUTLINE,
        color=ft.Colors.ON_SURFACE,
        keyboard_type=ft.KeyboardType.PHONE,
    )
    txt_empresa = ft.TextField(
        label="Nombre del emprendimiento",
        border_color=ft.Colors.OUTLINE,
        color=ft.Colors.ON_SURFACE,
        capitalization=ft.TextCapitalization.WORDS,
    )

    txt_password = ft.TextField(
        label="Contraseña",
        password=True,
        can_reveal_password=True,
        border_color=ft.Colors.OUTLINE,
        color=ft.Colors.ON_SURFACE,
    )

    mensaje = ft.Text("", size=13, color=ft.Colors.RED_400, text_align=ft.TextAlign.CENTER)

    # ---------- Creación de la cuenta (solo se ejecuta si acepta los términos) ----------
    async def crear_cuenta_confirmada(e):
        mensaje.color = ft.Colors.RED_400
        try:
            registrar_usuario(
                txt_nombre.value,
                txt_apellido.value,
                txt_email.value,
                txt_telefono.value,
                txt_password.value,
                txt_empresa.value,
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

    # ---------- Términos y condiciones ----------
    async def al_rechazar(e):
        await page.push_route("/")

    panel_legal = panel_terminos(page, crear_cuenta_confirmada, al_rechazar)

    async def pedir_aceptacion(e):
        panel_legal.visible = True
        page.update()

    btn_registrar = ft.Button(
        content=ft.Text("Registrarse", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
        bgcolor=ft.Colors.ORANGE_800,
        width=280,
        height=48,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=25)),
        on_click=pedir_aceptacion,
    )

    # ---------- Tarjeta con el formulario ----------
    formulario = ft.Container(
        expand=True,
        padding=25,
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK,
                            icon_color=ft.Colors.ON_SURFACE,
                            on_click=volver_login,
                        ),
                        ft.Text("Crear Cuenta", size=24, weight=ft.FontWeight.BOLD,
                                color=ft.Colors.ON_SURFACE),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                ),
                txt_nombre,
                txt_apellido,
                txt_email,
                txt_telefono,
                txt_empresa,
                txt_password,
                mensaje,
                btn_registrar,
                ft.TextButton(
                    content=ft.Text("¿Ya tienes cuenta? Restablece tu contraseña",
                                    size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                    on_click=ir_a_restablecer,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        ),
    )

    # El panel de términos va encima del formulario (Stack)
    tarjeta = ft.Container(
        content=ft.Stack(
            controls=[
                formulario,
                panel_legal,
            ],
        ),
        width=360,
        height=680,
        bgcolor=ft.Colors.SURFACE,
        border_radius=40,
        border=ft.Border.all(2, ft.Colors.OUTLINE_VARIANT),
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
    )

    return ft.Container(
        content=tarjeta,
        alignment=ft.Alignment.CENTER,
        expand=True,
    )