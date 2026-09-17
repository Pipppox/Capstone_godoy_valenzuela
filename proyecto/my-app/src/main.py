import flet as ft
from views.login_view import login_view
from views.crear_cuenta_view import crear_cuenta_view
from views.iniciar_sesion_email_view import iniciar_sesion_email_view
from views.iniciar_sesion_celu_view import iniciar_sesion_celu_view
from database.db import init_db

def main(page: ft.Page):
    init_db()
    page.title = "StockIN"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = ft.Colors.BLACK
    page.padding = 0

    # Mapa de rutas -> función que construye la vista
    rutas = {
        "/": login_view,
        "/crear_cuenta": crear_cuenta_view,
        "/iniciar_sesion_email": iniciar_sesion_email_view,
        "/iniciar_sesion_celu": iniciar_sesion_celu_view,
    }

    def construir_view(route: str) -> ft.View:
        return ft.View(
            route=route,
            controls=[rutas[route](page)],
            bgcolor=ft.Colors.BLACK,
            padding=0,
        )

    def route_change(e=None):
        page.views.clear()
        page.views.append(construir_view("/"))          # login siempre abajo
        if page.route != "/" and page.route in rutas:
            page.views.append(construir_view(page.route))  # vista actual encima
        page.update()

    async def view_pop(e):
        # Botón atrás del celular / navegador
        if e.view is not None:
            page.views.remove(e.view)
            await page.push_route(page.views[-1].route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    route_change()


if __name__ == "__main__":
    ft.run(main, assets_dir="src/assets")