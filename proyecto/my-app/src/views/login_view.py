import flet as ft


def login_view(page: ft.Page):
    # Navegación
    async def ir_a_crear_cuenta(e):
        await page.push_route("/crear_cuenta")

    async def ir_a_iniciar_sesion_email(e):
        await page.push_route("/iniciar_sesion_email")

    async def ir_a_iniciar_sesion_celu(e):
        await page.push_route("/iniciar_sesion_celu")

    # Ilustración central
    ilustracion = ft.Container(
        content=ft.Image(
            src="logo sin fondo.png",
            height=200,
            fit=ft.BoxFit.CONTAIN,
        ),
        alignment=ft.Alignment.CENTER,
    )

    # Título
    titulo_brand = ft.Row(
        controls=[
            ft.Text("Stock", size=35, weight=ft.FontWeight.BOLD, color=ft.Colors.ON_SURFACE),
            ft.Text("IN", size=35, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_800),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=0,
    )

    # Slogan
    slogan = ft.Column(
        controls=[
            ft.Text("\"Nunca te quedes", size=25, weight=ft.FontWeight.W_600, color=ft.Colors.ON_SURFACE),
            ft.Row(
                controls=[
                    ft.Text("OUT ", size=26, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_800),
                    ft.Text("de Stock\"", size=25, weight=ft.FontWeight.W_600, color=ft.Colors.ON_SURFACE),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=0,
            ),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=0,
    )

    # Botones (llenan el ancho de la tarjeta)
    def boton(texto, color_fondo, color_texto, accion):
        return ft.Button(
            content=ft.Text(texto, weight=ft.FontWeight.BOLD, color=color_texto),
            bgcolor=color_fondo,
            height=48,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=25)),
            on_click=accion,
        )

    btn_email = boton("Iniciar Sesión con Email", ft.Colors.ORANGE_800, ft.Colors.WHITE, ir_a_iniciar_sesion_email)
    btn_telefono = boton("Iniciar Sesión con Teléfono", ft.Colors.GREY_700, ft.Colors.WHITE, ir_a_iniciar_sesion_celu)
    btn_crear_cuenta = boton("Crea tu Cuenta", ft.Colors.GREY_500, ft.Colors.ON_SURFACE, ir_a_crear_cuenta)

    # Contenido: logo arriba, texto al centro, botones abajo
    contenido = ft.Column(
        controls=[
            ilustracion,
            ft.Column(
                controls=[titulo_brand, slogan],
                spacing=8,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            ft.Column(
                controls=[btn_email, btn_telefono, btn_crear_cuenta],
                spacing=12,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            ),
        ],
        expand=True,
        alignment=ft.MainAxisAlignment.SPACE_EVENLY,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
    )

    # Tarjeta: ocupa todo el espacio disponible, igual que las demás vistas
    tarjeta_movil = ft.Container(
        content=contenido,
        expand=True,
        bgcolor=ft.Colors.SURFACE,
        border_radius=40,
        padding=25,
        border=ft.Border.all(2, ft.Colors.OUTLINE_VARIANT),
    )

    return ft.Container(
        content=tarjeta_movil,
        expand=True,
        padding=ft.Padding.symmetric(horizontal=16, vertical=12),
    )