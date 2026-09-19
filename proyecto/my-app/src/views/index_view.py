import flet as ft

from services import sesion


def index_view(page: ft.Page):
    usuario = sesion.usuario() or {}
    nombre = usuario.get("nombre") or "UsuarioApp"

    # ---------- Navegación ----------
    async def ir_a_inventario(e):
        await page.push_route("/inventario")

    def proximamente(nombre_vista: str):
        async def _handler(e):
            print(f"[AVISO] {nombre_vista}: próximamente")
        return _handler

    async def cerrar_sesion(e):
        sesion.cerrar()
        await page.push_route("/")
        
    async def ir_a_inventario(e):
        await page.push_route("/inventario")

    # ---------- Encabezado ----------
    encabezado = ft.Row(
        controls=[
            ft.Text("Home", size=13, color=ft.Colors.GREY_400),
            ft.IconButton(
                icon=ft.Icons.ACCOUNT_CIRCLE,
                icon_color=ft.Colors.GREY_500,
                icon_size=34,
                tooltip="Perfil",
                on_click=proximamente("Perfil"),
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    saludo = ft.Column(
        controls=[
            ft.Text("Hello", size=30, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ft.Text(f'"{nombre}"', size=30, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
        ],
        spacing=0,
    )

    btn_overview = ft.Button(
        content=ft.Text("Overview", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
        bgcolor=ft.Colors.BLUE_600,
        width=110,
        height=34,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=20)),
        on_click=proximamente("Overview"),
    )

    # ---------- Tarjeta grande (resumen) ----------
    def barra(alto: int, color: str):
        return ft.Container(width=9, height=alto, bgcolor=color, border_radius=3)

    resumen = ft.Container(
        content=ft.Container(
            content=ft.Row(
                controls=[
                    barra(28, ft.Colors.ORANGE_800),
                    barra(45, ft.Colors.BLUE_400),
                    barra(22, ft.Colors.GREY_600),
                    barra(58, ft.Colors.ORANGE_800),
                    barra(38, ft.Colors.BLUE_400),
                    barra(50, ft.Colors.GREY_600),
                    barra(30, ft.Colors.ORANGE_800),
                ],
                alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                vertical_alignment=ft.CrossAxisAlignment.END,
                spacing=6,
            ),
            bgcolor=ft.Colors.GREY_900,
            border=ft.Border.all(2, ft.Colors.ORANGE_800),
            border_radius=10,
            padding=14,
            margin=14,
        ),
        height=135,
        bgcolor=ft.Colors.BLACK,
        border_radius=18,
        on_click=proximamente("Dashboard"),
        ink=True,
    )

    # ---------- Alerta de stock bajo ----------
    alerta_stock = ft.Container(
        content=ft.Row(
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color=ft.Colors.AMBER_600, size=24),
                        ft.Text("Stock BAJO en Lapices", size=14,
                                weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ],
                    spacing=12,
                ),
                ft.Icon(ft.Icons.CHEVRON_RIGHT, color=ft.Colors.GREY_500, size=20),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        bgcolor=ft.Colors.BLACK,
        border_radius=14,
        padding=ft.Padding.symmetric(horizontal=14, vertical=14),
        on_click=ir_a_inventario,
        ink=True,
    )

    # ---------- Inventario ----------
    def linea_producto(nombre_producto: str, proporcion: float, color: str):
        return ft.Column(
            controls=[
                ft.Text(nombre_producto, size=10, color=ft.Colors.WHITE),
                ft.ProgressBar(value=proporcion, color=color,
                               bgcolor=ft.Colors.GREY_800, height=5, border_radius=3),
            ],
            spacing=3,
        )

    tarjeta_inventario = ft.Column(
        controls=[
            ft.Text("Inventario", size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ft.Container(
                content=ft.Column(
                    controls=[
                        linea_producto("Libros", 0.85, ft.Colors.GREEN_400),
                        linea_producto("Cuadernos", 0.45, ft.Colors.AMBER_600),
                        linea_producto("Lapices", 0.10, ft.Colors.RED_400),
                    ],
                    spacing=10,
                ),
                bgcolor=ft.Colors.BLACK,
                border_radius=14,
                padding=14,
                height=110,
                on_click=ir_a_inventario,
                ink=True,
            ),
        ],
        spacing=8,
        expand=True,
    )

    # ---------- Maps ----------
    tarjeta_maps = ft.Column(
        controls=[
            ft.Text("Maps", size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ft.Container(
                content=ft.Icon(ft.Icons.MAP, color=ft.Colors.BLUE_300, size=40),
                alignment=ft.Alignment.CENTER,
                bgcolor=ft.Colors.BLUE_GREY_900,
                border_radius=14,
                height=110,
                on_click=proximamente("Maps"),
                ink=True,
            ),
        ],
        spacing=8,
        expand=True,
    )

    # ---------- Barra inferior ----------
    barra_inferior = ft.Container(
        content=ft.Row(
            controls=[
                ft.IconButton(icon=ft.Icons.HOME, icon_color=ft.Colors.WHITE,
                              icon_size=22, tooltip="Home"),
                ft.Container(
                    content=ft.Icon(ft.Icons.ADD, color=ft.Colors.WHITE, size=24),
                    width=48,
                    height=48,
                    bgcolor=ft.Colors.BLUE_600,
                    border_radius=24,
                    alignment=ft.Alignment.CENTER,
                    on_click=proximamente("Agregar producto"),
                    ink=True,
                ),
                ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, icon_color=ft.Colors.GREY_500,
                              icon_size=22, tooltip="Vender producto",
                              on_click=proximamente("Vender producto")),
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
                        saludo,
                        btn_overview,
                        ft.Divider(height=6, color=ft.Colors.TRANSPARENT),
                        resumen,
                        ft.Divider(height=6, color=ft.Colors.TRANSPARENT),
                        alerta_stock,
                        ft.Divider(height=6, color=ft.Colors.TRANSPARENT),
                        ft.Row(
                            controls=[tarjeta_inventario, tarjeta_maps],
                            spacing=14,
                            vertical_alignment=ft.CrossAxisAlignment.START,
                        ),
                        ft.TextButton(
                            content=ft.Text("Cerrar sesión", size=12, color=ft.Colors.GREY_500),
                            on_click=cerrar_sesion,
                        ),
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