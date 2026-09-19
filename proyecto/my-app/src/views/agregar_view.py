import flet as ft

from services import productos


def agregar_view(page: ft.Page):
    async def volver(e):
        await page.push_route("/inventario")

    def campo(label, keyboard=None):
        return ft.TextField(
            label=label,
            border_color=ft.Colors.GREY_700,
            color=ft.Colors.WHITE,
            keyboard_type=keyboard,
        )

    txt_codigo = campo("Código")
    txt_nombre = campo("Nombre / Descripción")
    txt_categoria = campo("Categoría")
    txt_precio = campo("Precio ($)", ft.KeyboardType.NUMBER)
    txt_stock = campo("Stock", ft.KeyboardType.NUMBER)

    mensaje = ft.Text("", size=13, color=ft.Colors.RED_400, text_align=ft.TextAlign.CENTER)

    async def agregar(e):
        mensaje.color = ft.Colors.RED_400
        try:
            productos.crear(
                txt_codigo.value,
                txt_nombre.value,
                txt_categoria.value,
                txt_precio.value,
                txt_stock.value,
            )
        except ValueError as err:
            mensaje.value = str(err)
            page.update()
            return

        for campo_txt in (txt_codigo, txt_nombre, txt_categoria, txt_precio, txt_stock):
            campo_txt.value = ""
        mensaje.color = ft.Colors.GREEN_400
        mensaje.value = "Producto agregado. Puedes agregar otro."
        page.update()

    txt_stock.on_submit = agregar

    encabezado = ft.Row(
        controls=[
            ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color=ft.Colors.WHITE, on_click=volver),
            ft.Text("Agregar Producto", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
        ],
        alignment=ft.MainAxisAlignment.START,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    formulario = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text("Agrega tu ", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ft.Text("Producto", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_800),
                    ],
                    spacing=0,
                ),
                ft.Divider(height=4, color=ft.Colors.TRANSPARENT),
                txt_codigo,
                txt_nombre,
                txt_categoria,
                txt_precio,
                txt_stock,
            ],
            spacing=12,
        ),
        bgcolor=ft.Colors.BLACK,
        border_radius=14,
        padding=18,
    )

    btn_agregar = ft.Button(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.ADD_BOX, color=ft.Colors.WHITE, size=18),
                ft.Text("Agregar Producto", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
        ),
        bgcolor=ft.Colors.ORANGE_800,
        width=230,
        height=46,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=25)),
        on_click=agregar,
    )

    tarjeta_movil = ft.Container(
        content=ft.Column(
            controls=[
                encabezado,
                ft.Divider(height=6, color=ft.Colors.TRANSPARENT),
                formulario,
                mensaje,
                btn_agregar,
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