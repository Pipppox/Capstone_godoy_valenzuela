import flet as ft

from services import productos, ventas, sesion
from services.geocoding import geocodificar_y_guardar
from components.campo_direccion import CampoDireccion


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

    # ---------- Lugar de venta (autocompletado + mapa) ----------
    campo_lugar = CampoDireccion(label="Lugar de venta", alto_mapa=180)

    mensaje = ft.Text("", size=13, color=ft.Colors.RED_400, text_align=ft.TextAlign.CENTER)

    alerta_stock = ft.Container(
        visible=False,
        bgcolor=ft.Colors.BLACK,
        border_radius=12,
        padding=ft.Padding.symmetric(horizontal=14, vertical=10),
    )

    panel_popup = ft.Container(visible=False)

    def cerrar_popup(e):
        panel_popup.visible = False
        panel_formulario.visible = True
        page.update()

    async def vender_producto(e):
        mensaje.color = ft.Colors.RED_400

        # ---- Resolver el lugar antes de registrar ----
        lugar_texto = campo_lugar.texto()
        geo = campo_lugar.lugar  # viene listo si eligió una sugerencia

        if lugar_texto and not geo and dd_producto.value:
            # Escribió a mano sin elegir sugerencia: respaldo con Geocoding
            geo = geocodificar_y_guardar(lugar_texto)

        # Guardar la venta con el mismo nombre que queda en lugares_cache
        lugar_final = geo["lugar"] if geo else lugar_texto

        try:
            resumen = ventas.registrar(
                dd_producto.value,
                txt_cantidad.value,
                lugar_final,
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
        if geo:
            mensaje.value += f'\n📍 {geo["lugar"]}'

        # ---- Refrescar formulario ----
        dd_producto.options = [
            ft.dropdown.Option(
                key=str(p["id"]),
                text=f'{p["codigo"]} - {p["nombre"]} ({p["stock"]} u.)',
            )
            for p in productos.listar()
        ]
        dd_producto.value = None
        txt_cantidad.value = "1"
        campo_lugar.limpiar()
        page.update()

        # ---- Popup de stock bajo ----
        if resumen["stock_nuevo"] <= productos.STOCK_MINIMO:
            notif_activas = bool((sesion.usuario() or {}).get("notificaciones", 0))
            if notif_activas:
                panel_popup.content = ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color=ft.Colors.AMBER_600, size=50),
                            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                            ft.Text("¡Stock bajo!", size=20, weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.AMBER_600, text_align=ft.TextAlign.CENTER),
                            ft.Divider(height=6, color=ft.Colors.TRANSPARENT),
                            ft.Text(
                                f'"{resumen["nombre"]}" tiene solo {resumen["stock_nuevo"]} unidades.',
                                size=13, color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                            ft.Button(
                                content=ft.Text("Entendido", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                bgcolor=ft.Colors.ORANGE_800,
                                width=180,
                                height=42,
                                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=25)),
                                on_click=cerrar_popup,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=0,
                    ),
                    bgcolor=ft.Colors.BLACK,
                    border_radius=14,
                    padding=30,
                    border=ft.Border.all(2, ft.Colors.AMBER_600),
                )
                panel_formulario.visible = False
                panel_popup.visible = True
                page.update()

    txt_cantidad.on_submit = vender_producto

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
                campo_lugar,
            ],
            spacing=12,
        )
    else:
        cuerpo = ft.Column(
            controls=[
                ft.Text("No tienes productos para vender.", size=13, color=ft.Colors.GREY_400),
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
        on_click=vender_producto,
        disabled=not lista,
    )

    panel_formulario = ft.Column(
        controls=[
            encabezado,
            ft.Divider(height=6, color=ft.Colors.TRANSPARENT),
            formulario,
            mensaje,
            alerta_stock,
            btn_vender,
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=14,
        scroll=ft.ScrollMode.AUTO,
    )

    tarjeta_movil = ft.Container(
        content=ft.Column(
            controls=[
                panel_formulario,
                panel_popup,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
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