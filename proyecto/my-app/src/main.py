import flet as ft

from database.db import init_db
from services import sesion
from views.login_view import login_view
from views.crear_cuenta_view import crear_cuenta_view
from views.iniciar_sesion_email_view import iniciar_sesion_email_view
from views.iniciar_sesion_celu_view import iniciar_sesion_celu_view
from views.index_view import index_view
from views.inventario_view import inventario_view
from views.agregar_view import agregar_view
from views.vender_view import vender_view


def main(page: ft.Page):
    init_db()
    page.title = "StockIN"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = ft.Colors.BLACK
    page.padding = 0

    # Rutas sin sesión (se apilan sobre el login)
    rutas_publicas = {
        "/": login_view,
        "/crear_cuenta": crear_cuenta_view,
        "/iniciar_sesion_email": iniciar_sesion_email_view,
        "/iniciar_sesion_celu": iniciar_sesion_celu_view,
    }

    # Rutas que requieren sesión (se apilan sobre el index)
    rutas_privadas = {
        "/index": index_view,
        "/inventario": inventario_view,
        "/agregar": agregar_view,
        "/vender": vender_view,
    }

    def construir_view(route: str, builder) -> ft.View:
        return ft.View(
            route=route,
            controls=[builder(page)],
            bgcolor=ft.Colors.BLACK,
            padding=0,
        )

    def route_change(e=None):
        page.views.clear()
        ruta = page.route
        print(f"[RUTA] {ruta} | sesión activa: {sesion.activa()}")

        if ruta in rutas_privadas:
            if not sesion.activa():
                print("[RUTA] Sin sesión -> se muestra el login")
                page.views.append(construir_view("/", login_view))
            else:
                page.views.append(construir_view("/index", index_view))
                if ruta != "/index":
                    page.views.append(construir_view(ruta, rutas_privadas[ruta]))
        elif ruta in rutas_publicas:
            page.views.append(construir_view("/", login_view))
            if ruta != "/":
                page.views.append(construir_view(ruta, rutas_publicas[ruta]))
        else:
            # Ruta desconocida: falta agregarla a alguno de los diccionarios
            print(f"[RUTA] '{ruta}' no está registrada en rutas_publicas ni rutas_privadas")
            destino = "/index" if sesion.activa() else "/"
            page.views.append(
                construir_view(destino, index_view if sesion.activa() else login_view)
            )

        page.update()

    async def view_pop(e):
        # Botón atrás: no se sale de la vista base (login o index)
        if e.view is not None and len(page.views) > 1:
            page.views.remove(e.view)
            await page.push_route(page.views[-1].route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    route_change()


if __name__ == "__main__":
    ft.run(main, assets_dir="assets")