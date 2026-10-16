import webbrowser

import flet as ft

from services.geocoding import generar_url_google_maps
from components.mapa import crear_mapa


def maps_view(page: ft.Page):
    async def volver(e):
        await page.push_route("/index")

    # ---------- Encabezado ----------
    encabezado = ft.Row(
        controls=[
            ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color=ft.Colors.ON_SURFACE,
                          icon_size=22, on_click=volver),
            ft.Text("Maps", size=20, weight=ft.FontWeight.BOLD,
                    color=ft.Colors.ON_SURFACE, text_align=ft.TextAlign.CENTER),
            ft.Container(width=40),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # ---------- Mapa para navegar (Google Maps) ----------
    mapa = crear_mapa(alto=500)

    # ---------- Botón abrir en Google Maps ----------
    def abrir_en_navegador(e):
        webbrowser.open(generar_url_google_maps([]))

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
        width=250,
        height=42,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=25)),
        on_click=abrir_en_navegador,
    )

    # ---------- Tarjeta Celular ----------
    tarjeta_movil = ft.Container(
        content=ft.Column(
            controls=[
                encabezado,
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                mapa,
                ft.Divider(height=16, color=ft.Colors.TRANSPARENT),
                btn_abrir_maps,
            ],
            spacing=0,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        width=360,
        height=680,
        bgcolor=ft.Colors.SURFACE,
        border_radius=40,
        padding=ft.Padding.only(left=22, right=22, top=22, bottom=6),
        border=ft.Border.all(2, ft.Colors.OUTLINE_VARIANT),
    )

    return ft.Container(
        content=tarjeta_movil,
        alignment=ft.Alignment.CENTER,
        expand=True,
    )