import flet as ft

def login_view(page: ft.Page):
    # Ilustración central
    ilustracion = ft.Container(
    content=ft.Image(
        src="logo sin fondo.png",
        width=260,
        height=220,
        fit=ft.BoxFit.CONTAIN, 
    ),
    width=280,
    height=220,
    alignment=ft.Alignment.CENTER,
    )
    # Título 
    titulo_brand = ft.Row(
        controls=[
            ft.Text("Stock", size=35, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ft.Text("IN", size=35, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_800),
        ],
        alignment=ft.MainAxisAlignment.START,
        spacing=0,
    )

    # Slogan
    slogan = ft.Column(
        controls=[
            ft.Text("'Nunca te quedes", size=34, weight=ft.FontWeight.W_600, color=ft.Colors.WHITE),
            ft.Row(
                controls=[
                    ft.Text("OUT ", size=34, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_800),
                    ft.Text("de Stock\"", size=34, weight=ft.FontWeight.W_600, color=ft.Colors.WHITE),
                ],
                alignment=ft.MainAxisAlignment.START,
                spacing=0,
            ),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.START,
        spacing=0,
    )

    # Botones
    btn_email = ft.ElevatedButton(
        content=ft.Text("Iniciar Sesión con Email", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
        bgcolor=ft.Colors.ORANGE_800,
        width=280,
        height=48,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=25),
        ),
        on_click=lambda _: print("Clic en Login Email"),
    )

    btn_google = ft.OutlinedButton(
        content=ft.Text("Google", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
        width=135,
        height=45,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=20),
            side=ft.BorderSide(1, ft.Colors.GREY_700),
        ),
    )

    btn_apple = ft.OutlinedButton(
        content=ft.Text("Apple ID", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
        width=135,
        height=45,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=20),
            side=ft.BorderSide(1, ft.Colors.GREY_700),
        ),
    )

    fila_social = ft.Row(
        controls=[btn_google, btn_apple],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=10,
    )

    # Tarjeta Celular
    tarjeta_movil = ft.Container(
        content=ft.Column(
            controls=[
                ilustracion,
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                titulo_brand,
                slogan,
                ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
                btn_email,
                fila_social,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.SPACE_EVENLY,
        ),
        width=360,
        height=680,
        bgcolor=ft.Colors.GREY_900,
        border_radius=40,
        padding=25,
        border=ft.Border.all(2, ft.Colors.GREY_800),
    )

    return ft.Container(
        content=tarjeta_movil,
        alignment=ft.Alignment.CENTER,
        expand=True,
    )