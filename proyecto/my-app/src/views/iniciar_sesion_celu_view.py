import flet as ft

from services import sesion
from services.auth import login_con_telefono


def iniciar_sesion_celu_view(page: ft.Page):
    async def volver_login(e):
        await page.push_route("/")

    txt_celular = ft.TextField(
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

    async def ingresar(e):
        if not txt_celular.value or not txt_password.value:
            mensaje.value = "Ingresa tu Numero telefonico y contraseña."
            page.update()
            return

        usuario = login_con_telefono(txt_celular.value, txt_password.value)
        if usuario is None:
            mensaje.value = "Numero telefonico o contraseña incorrectos."
            txt_password.value = ""
            page.update()
            return

        sesion.iniciar(usuario)
        await page.push_route("/index")

    # Enter en la contraseña también inicia sesión
    txt_password.on_submit = ingresar

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
                        ft.Text("Iniciar Sesión", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                ),
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                txt_celular,
                txt_password,
                mensaje,
                ft.Button(
                    content=ft.Text("Ingresar", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    bgcolor=ft.Colors.ORANGE_800,
                    width=280,
                    height=48,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=25)),
                    on_click=ingresar,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15,
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