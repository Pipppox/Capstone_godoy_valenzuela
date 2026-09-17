import flet as ft

def iniciar_sesion_email_view(page: ft.Page):
    async def volver_login(e):
        await page.push_route("/")

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
                        ft.Text("Iniciar Sesión ", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                ),
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                ft.TextField(
                    label="Correo electrónico",
                    border_color=ft.Colors.GREY_700,
                    color=ft.Colors.WHITE,
                ),
                ft.TextField(
                    label="Contraseña",
                    password=True,
                    can_reveal_password=True,
                    border_color=ft.Colors.GREY_700,
                    color=ft.Colors.WHITE,
                ),
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                ft.Button(
                    content=ft.Text("Ingresar", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    bgcolor=ft.Colors.ORANGE_800,
                    width=280,
                    height=48,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=25)),
                    on_click=lambda _: print("Registrando usuario..."),
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