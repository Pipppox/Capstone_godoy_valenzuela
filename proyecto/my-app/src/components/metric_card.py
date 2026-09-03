import flet as ft

def crear_tarjeta_metrica(titulo: str, valor: str, icono: str, color_icono: str):
    """
    Función que retoma una tarjeta de indicador/métrica estilizada.
    """
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(name=icono, size=36, color=color_icono),
                ft.Column(
                    controls=[
                        ft.Text(titulo, size=14, color=ft.Colors.GREY_400),
                        ft.Text(valor, size=24, weight=ft.FontWeight.BOLD),
                    ],
                    spacing=2,
                ),
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15,
        ),
        bgcolor=ft.Colors.SURFACE_VARIANT,
        padding=15,
        border_radius=10,
        expand=True,  # Hace que la tarjeta sea responsiva
    )