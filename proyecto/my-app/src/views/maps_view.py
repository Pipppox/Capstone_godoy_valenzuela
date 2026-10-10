import webbrowser

import flet as ft

from services.geocoding import obtener_marcadores, generar_url_google_maps
from services import sesion
from components.mapa import crear_mapa


def maps_view(page: ft.Page):
    async def volver(e):
        await page.push_route("/index")

    uid = (sesion.usuario() or {}).get("id")
    marcadores = obtener_marcadores(usuario_id=uid)

    # ---------- Encabezado ----------
    encabezado = ft.Row(
        controls=[
            ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color=ft.Colors.WHITE,
                          icon_size=22, on_click=volver),
            ft.Text("Maps", size=20, weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER),
            ft.Container(width=40),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # ---------- Info ----------
    cantidad = len(marcadores)
    info = ft.Text(
        f"{cantidad} lugar{'es' if cantidad != 1 else ''} de venta registrado{'s' if cantidad != 1 else ''}",
        size=11, color=ft.Colors.GREY_400, text_align=ft.TextAlign.CENTER,
    )

    # ---------- Mapa dinámico ----------
    mapa = crear_mapa(marcadores, alto=280, etiquetas=True)

    # ---------- Botón abrir en Google Maps ----------
    def abrir_en_navegador(e):
        url = generar_url_google_maps(marcadores)
        webbrowser.open(url)

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
        disabled=not marcadores,
    )

    # ---------- Lista de lugares ----------
    if marcadores:
        filas_lugares = [
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.Text(chr(65 + i) if i < 26 else "·",
                                            size=11, weight=ft.FontWeight.BOLD,
                                            color=ft.Colors.WHITE,
                                            text_align=ft.TextAlign.CENTER),
                            width=26,
                            height=26,
                            bgcolor=ft.Colors.ORANGE_800,
                            border_radius=13,
                            alignment=ft.Alignment.CENTER,
                        ),
                        ft.Text(m["lugar"], size=13, color=ft.Colors.WHITE, expand=True),
                    ],
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.Padding.symmetric(horizontal=4, vertical=8),
            )
            for i, m in enumerate(marcadores)
        ]
    else:
        filas_lugares = [
            ft.Text("Vende productos indicando el lugar\npara verlos aquí en el mapa.",
                    size=12, color=ft.Colors.GREY_500, text_align=ft.TextAlign.CENTER),
        ]

    lista_lugares = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Lugares de venta", size=14, weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE),
                ft.Divider(height=6, color=ft.Colors.TRANSPARENT),
                *filas_lugares,
            ],
            spacing=4,
        ),
        bgcolor=ft.Colors.BLACK,
        border_radius=14,
        padding=18,
    )

    # ---------- Tarjeta Celular ----------
    tarjeta_movil = ft.Container(
        content=ft.Column(
            controls=[
                encabezado,
                info,
                ft.Divider(height=6, color=ft.Colors.TRANSPARENT),
                mapa,
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                btn_abrir_maps,
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                lista_lugares,
            ],
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        width=360,
        height=680,
        bgcolor=ft.Colors.GREY_900,
        border_radius=40,
        padding=ft.Padding.only(left=22, right=22, top=22, bottom=6),
        border=ft.Border.all(2, ft.Colors.GREY_800),
    )

    return ft.Container(
        content=tarjeta_movil,
        alignment=ft.Alignment.CENTER,
        expand=True,
    )