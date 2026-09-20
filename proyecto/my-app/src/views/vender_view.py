import flet as ft

from services import productos, ventas


def vender_view(page: ft.Page):
    async def volver(e):
        await page.push_route("/inventario")

    lista = productos.listar()

    dd_producto = ft.Dropdown(
        label="Producto a vender",
        border_color=ft.Colors.GREY_700,
        color=ft.Colors.WHITE,
        options=[
            ft.dropdown.Option(
                key=str(p["id"]),
                text=f'{p["codigo"]} - {p["nombre"]} ({p["stock"]} u.)',
            )
            for p in lista
        ],
    )

    txt_cantidad = ft.TextField(
        label="Cantidad",
        value="1",
        keyboard_type=ft.KeyboardType.NUMBER,
        border_color=ft.Colors.GREY_700,
        color=ft.Colors.WHITE,
    )

    txt_lugar = ft.TextField(
        label="Lugar de venta (opcional)",
        hint_text="Feria Recoleta, Metro Baquedano...",
        border_color=ft.Colors.GREY_700,
        color=ft.Colors.WHITE,
    )

    mensaje = ft.Text("", size=13, color=ft.Colors.RED_400, text_align=ft.TextAlign.CENTER)

    async def vender(e):
        mensaje.color = ft.Colors.RED_400
        try:
            resumen = ventas.registrar(
                dd_producto.value,
                txt_cantidad.value,
                txt_lugar.value,
            )
        except ValueError as err:
            mensaje.value = str(err)
            page.update()
            return

        mensaje.color = ft.Colors.GREEN_400
        mensaje.value = (
            f'Vendiste {resumen["cantidad"]} x {resumen["nombre"]} '
            f'por ${resumen["total"]:,}'.replace(",", ".")
            + f' — quedan {resumen["stock_nuevo"]} unidades.'
        )

        # Refrescar el desplegable con el stock actualizado
        dd_producto.options = [
            ft.dropdown.Option(
                key=str(p["id"]),
                text=f'{p["codigo"]} - {p["nombre"]} ({p["stock"]} u.)',
            )
            for p in productos.listar()
        ]
        dd_producto.value = None
        txt_cantidad.value = "1"
        page.update()

    txt_cantidad.on_submit = vender

    encabezado = ft.Row(
        controls=[
            ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color=ft.Colors.WHITE, on_click=volver),
            ft.Text("Vender Producto", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
        ],
        alignment=ft.MainAxisAlignment.START,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    if lista:
        cuerpo = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text("Producto ", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_800),
                        ft.Text("a vender", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ],
                    spacing=0,
                ),
                ft.Divider(height=4, color=ft.Colors.TRANSPARENT),
                dd_producto,
                txt_cantidad,
                txt_lugar,
            ],
            spacing=12,
        )
    else:
        cuerpo = ft.Column(
            controls=[
                ft.Text("No tienes productos para vender.", size=13, color=ft.Colors.GREY_400),
                ft.Text("Agrega uno primero desde Inventario.", size=12, color=ft.Colors.GREY_500),
            ],
            spacing=6,
        )

    formulario = ft.Container(
        content=cuerpo,
        bgcolor=ft.Colors.BLACK,
        border_radius=14,
        padding=18,
    )

    btn_vender = ft.Button(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.SELL, color=ft.Colors.WHITE, size=18),
                ft.Text("Vender producto", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
        ),
        bgcolor=ft.Colors.RED_700,
        width=230,
        height=46,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=25)),
        on_click=vender,
        disabled=not lista,
    )

    tarjeta_movil = ft.Container(
        content=ft.Column(
            controls=[
                encabezado,
                ft.Divider(height=6, color=ft.Colors.TRANSPARENT),
                formulario,
                mensaje,
                btn_vender,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=14,
            scroll=ft.ScrollMode.AUTO,
        ),
        width=360,
        height=680,
        bgcolor=ft.Colors.GREY_900,
        border_radius=40,
        padding=22,
        border=ft.Border.all(2, ft.Colors.GREY_800),
    )

    return ft.Container(
        content=tarjeta_movil,
        alignment=ft.Alignment.CENTER,
        expand=True,
    )