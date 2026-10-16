"""Colores de la app para modo oscuro y modo claro.

Las vistas NO usan colores fijos (BLACK, WHITE, GREY_900...), sino colores
"con significado" que cambian solos según el modo:

    Fondo exterior ........ ft.Colors.SURFACE_CONTAINER_LOWEST
    Tarjeta del celular ... ft.Colors.SURFACE
    Tarjetas / paneles .... ft.Colors.SURFACE_CONTAINER_HIGHEST
    Texto principal ....... ft.Colors.ON_SURFACE
    Texto secundario ...... ft.Colors.ON_SURFACE_VARIANT
    Bordes de campos ...... ft.Colors.OUTLINE
    Bordes suaves ......... ft.Colors.OUTLINE_VARIANT

Los colores de marca (naranjo, azul, rojo, verde) y el texto blanco
sobre botones de color se mantienen igual en ambos modos.
"""
import flet as ft

from services import preferencias

TEMA_OSCURO = ft.Theme(
    color_scheme=ft.ColorScheme(
        primary=ft.Colors.ORANGE_800,
        surface=ft.Colors.GREY_900,
        on_surface=ft.Colors.WHITE,
        on_surface_variant=ft.Colors.GREY_400,
        surface_container_highest=ft.Colors.BLACK,
        surface_container_lowest=ft.Colors.BLACK,
        outline=ft.Colors.GREY_700,
        outline_variant=ft.Colors.GREY_800,
    ),
)

TEMA_CLARO = ft.Theme(
    color_scheme=ft.ColorScheme(
        primary=ft.Colors.ORANGE_800,
        surface=ft.Colors.WHITE,
        on_surface=ft.Colors.GREY_900,
        on_surface_variant=ft.Colors.GREY_600,
        surface_container_highest=ft.Colors.GREY_100,
        surface_container_lowest=ft.Colors.GREY_300,
        outline=ft.Colors.GREY_400,
        outline_variant=ft.Colors.GREY_300,
    ),
)


def configurar(page: ft.Page) -> None:
    """Se llama una vez al iniciar la app (en main.py)."""
    page.theme = TEMA_CLARO
    page.dark_theme = TEMA_OSCURO
    aplicar(page)


def aplicar(page: ft.Page) -> None:
    """Pone el modo del usuario conectado (o oscuro si no hay sesión).
    main.py lo llama en cada cambio de pantalla: así, al iniciar o cerrar
    sesión, la app toma el modo del usuario correcto."""
    page.theme_mode = ft.ThemeMode.DARK if preferencias.modo_oscuro() else ft.ThemeMode.LIGHT


def cambiar_modo(page: ft.Page, oscuro: bool) -> None:
    """Cambia el modo al instante y lo guarda en el usuario conectado."""
    preferencias.guardar_modo_oscuro(oscuro)
    page.theme_mode = ft.ThemeMode.DARK if oscuro else ft.ThemeMode.LIGHT
    page.update()