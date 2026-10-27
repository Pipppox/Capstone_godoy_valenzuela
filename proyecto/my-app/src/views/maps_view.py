import flet as ft

from services.geocoding import generar_url_google_maps
from components.mapa import crear_mapa


def maps_view(page: ft.Page):
    async def volver(e):
        await page.push_route("/index")

    # Servicio para abrir enlaces (funciona en PC y en Android)
    url_launcher = ft.UrlLauncher()
    page.services.append(url_launcher)

    async def abrir_en_navegador(e):
        await url_launcher.launch_url(generar_url_google_maps([]))

    # ---------- Encabezado ----------
    encabezado = ft.Row(
        controls=[
            ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                icon_color=ft.Colors.ON_SURFACE,
                icon_size=22,
                on_click=volver,
            ),
            ft.Text(
                "Maps",
                size=22,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.ON_SURFACE,
            ),
        ],
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=4,
    )

    # ---------- Mapa dentro de una tarjeta redondeada ----------
    mapa = ft.Container(
        content=crear_mapa(alto=480),
        border_radius=16,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        expand=True,
    )

    # ---------- Botón ----------
    btn_abrir_maps = ft.Button(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.OPEN_IN_NEW, color=ft.Colors.WHITE, size=18),
                ft.Text("Abrir en Google Maps", weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
        ),
        bgcolor=ft.Colors.BLUE_600,
        height=48,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=25)),
        on_click=abrir_en_navegador,
    )

    contenido = ft.Column(
        controls=[encabezado, mapa, btn_abrir_maps],
        spacing=16,
        expand=True,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
    )

    pantalla = ft.Container(
        content=contenido,
        bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
        padding=ft.Padding.only(left=20, right=20, top=16, bottom=20),
        expand=True,
    )

    # SafeArea evita que el contenido quede bajo la barra de navegación del celular
    return ft.SafeArea(content=pantalla, expand=True)