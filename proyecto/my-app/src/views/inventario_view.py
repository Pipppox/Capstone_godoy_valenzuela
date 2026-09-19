import flet as ft

from services import productos


def inventario_view(page: ft.Page):
    # ---------- Navegación ----------
    async def volver(e):
        await page.push_route("/index")

    async def ir_a_agregar(e):
        await page.push_route("/agregar")

    async def ir_a_vender(e):
        await page.push_route("/vender")

    def proximamente(nombre_vista: str):
        async def _handler(e):
            print(f"[AVISO] {nombre_vista}: próximamente")
        return _handler

    # ---------- Datos ----------
    lista = productos.listar()
    maximo = productos.maximo_stock(lista)

    def fila_producto(producto: dict):
        return ft.Row(
            controls=[
                ft.Text(producto["nombre"], size=12, color=ft.Colors.WHITE, width=75),
                ft.ProgressBar(
                    value=productos.proporcion(producto, maximo),
                    color=productos.color_stock(producto["stock"]),
                    bgcolor=ft.Colors.GREY_800,
                    height=5,
                    border_radius=3,
                    expand=True,
                ),
                ft.Text(f'{producto["stock"]} unidades', size=11,
                        color=ft.Colors.GREY_400, width=72,
                        text_align=ft.TextAlign.RIGHT),
            ],
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    if lista:
        filas = [fila_producto(p) for p in lista]
    else:
        filas = [
            ft.Text("Aún no tienes productos. Agrega el primero.",
                    size=12, color=ft.Colors.GREY_500),
        ]

    # ---------- Encabezado ----------
    encabezado = ft.Row(
        controls=[
            ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                icon_color=ft.Colors.WHITE,
                on_click=volver,
            ),
            ft.Text("Inventario", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ft.IconButton(
                icon=ft.Icons.ACCOUNT_CIRCLE,
                icon_color=ft.Colors.GREY_500,
                icon_size=30,
                tooltip="Perfil",
                on_click=proximamente("Perfil"),
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # ---------- Inventario total ----------
    inventario_total = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Inventario total", size=15, weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE),
                ft.Divider(height=6, color=ft.Colors.TRANSPARENT),
                *filas,
            ],
            spacing=14,
        ),
        bgcolor=ft.Colors.BLACK,
        border_radius=14,
        padding=18,
    )

    # ---------- Botones de acción ----------
    def boton_accion(texto: str, icono: str, color: str, handler):
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(icono, color=color, size=20),
                            ft.Text(texto, size=13, weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.WHITE),
                        ],
                        spacing=12,
                    ),
                    ft.Icon(ft.Icons.CHEVRON_RIGHT, color=ft.Colors.GREY_500, size=20),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            bgcolor=ft.Colors.BLACK,
            border_radius=14,
            padding=ft.Padding.symmetric(horizontal=16, vertical=14),
            on_click=handler,
            ink=True,
        )

    btn_agregar = boton_accion(
        "Agregar Producto", ft.Icons.ADD_BOX, ft.Colors.ORANGE_800,
        ir_a_agregar,
    )
    btn_vender = boton_accion(
        "Vender Producto", ft.Icons.SELL, ft.Colors.RED_400,
        ir_a_vender,
    )

    # ---------- Barra inferior ----------
    barra_inferior = ft.Container(
        content=ft.Row(
            controls=[
                ft.IconButton(icon=ft.Icons.HOME, icon_color=ft.Colors.GREY_500,
                              icon_size=22, tooltip="Home", on_click=volver),
                ft.Container(
                    content=ft.Icon(ft.Icons.ADD, color=ft.Colors.WHITE, size=24),
                    width=48,
                    height=48,
                    bgcolor=ft.Colors.BLUE_600,
                    border_radius=24,
                    alignment=ft.Alignment.CENTER,
                    on_click=ir_a_agregar,
                    ink=True,
                ),
                ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, icon_color=ft.Colors.GREY_500,
                              icon_size=22, tooltip="Vender producto",
                              on_click=ir_a_vender),
            ],
            alignment=ft.MainAxisAlignment.SPACE_AROUND,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        height=64,
    )

    # ---------- Tarjeta Celular ----------
    tarjeta_movil = ft.Container(
        content=ft.Column(
            controls=[
                ft.Column(
                    controls=[
                        encabezado,
                        ft.Divider(height=8, color=ft.Colors.TRANSPARENT),
                        inventario_total,
                        ft.Divider(height=8, color=ft.Colors.TRANSPARENT),
                        btn_agregar,
                        btn_vender,
                    ],
                    spacing=12,
                    scroll=ft.ScrollMode.AUTO,
                    expand=True,
                ),
                barra_inferior,
            ],
            spacing=0,
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
