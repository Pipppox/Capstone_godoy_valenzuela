import flet as ft
# Si creas el componente reutilizable, lo importas:
# from components.metric_card import crear_tarjeta_metrica

def index_view(page: ft.Page):
    # 1. Encabezado
    encabezado = ft.Column(
        controls=[
            ft.Text("Dashboard de Inicio", size=28, weight=ft.FontWeight.BOLD),
            ft.Text("Resumen en tiempo real del estado de Stockin", size=14, color=ft.Colors.GREY_400),
        ],
        spacing=2,
    )

    # 2. Seccion de tarjetas informativas (KPIs)
    # Ejemplo directo si aún no usas el componente en otro archivo:
    tarjeta_productos = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.INVENTORY_2, size=32, color=ft.Colors.BLUE_400),
            ft.Column([
                ft.Text("Total Productos", size=12, color=ft.Colors.GREY_400),
                ft.Text("124", size=22, weight=ft.FontWeight.BOLD),
            ], spacing=1)
        ], spacing=15),
        bgcolor=ft.Colors.GREY_900,
        padding=15,
        border_radius=10,
        expand=True
    )

    tarjeta_bajo_stock = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, size=32, color=ft.Colors.ORANGE_400),
            ft.Column([
                ft.Text("Bajo Stock", size=12, color=ft.Colors.GREY_400),
                ft.Text("5", size=22, weight=ft.FontWeight.BOLD),
            ], spacing=1)
        ], spacing=15),
        bgcolor=ft.Colors.GREY_900,
        padding=15,
        border_radius=10,
        expand=True
    )

    tarjeta_ventas = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.ATTACH_MONEY, size=32, color=ft.Colors.GREEN_400),
            ft.Column([
                ft.Text("Ventas Hoy", size=12, color=ft.Colors.GREY_400),
                ft.Text("$150.000", size=22, weight=ft.FontWeight.BOLD),
            ], spacing=1)
        ], spacing=15),
        bgcolor=ft.Colors.GREY_900,
        padding=15,
        border_radius=10,
        expand=True
    )

    # Fila que contiene las 3 tarjetas alineadas horizontalmente
    fila_metricas = ft.Row(
        controls=[tarjeta_productos, tarjeta_bajo_stock, tarjeta_ventas],
        spacing=15
    )

    # 3. Panel inferior (Acciones rápidas / Noticias)
    panel_acciones = ft.Container(
        content=ft.Column([
            ft.Text("Acciones Rápidas", size=18, weight=ft.FontWeight.BOLD),
            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
            ft.Row([
                ft.ElevatedButton(" + Registrar Producto", icon=ft.Icons.ADD, bgcolor=ft.Colors.BLUE_600, color=ft.Colors.WHITE),
                ft.OutlinedButton(" Ver Movimientos", icon=ft.Icons.LIST_ALT),
            ], spacing=10)
        ]),
        bgcolor=ft.Colors.GREY_900,
        padding=20,
        border_radius=10,
    )

    # Vista completa organizada verticalmente con espacio entre secciones
    return ft.Container(
        content=ft.Column(
            controls=[
                encabezado,
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT), # Espaciador transparente
                fila_metricas,
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                panel_acciones,
            ],
            spacing=15
        ),
        padding=25,
        expand=True
    )