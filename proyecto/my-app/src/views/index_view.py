import flet as ft

from services import sesion


def index_view(page: ft.Page):
    usuario = sesion.usuario() or {}

    async def cerrar_sesion(e):
        sesion.cerrar()
        await page.push_route("/")

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Home", size=14, color=ft.Colors.GREY_400),
                ft.Text(f"Hola {usuario.get('nombre', '')}", size=32,
                        weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ft.TextButton("Cerrar sesión", on_click=cerrar_sesion),
            ],
        ),
        padding=25,
        expand=True,
    )