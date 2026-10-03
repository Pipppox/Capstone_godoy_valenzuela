import flet as ft

from services import productos, ventas, sesion
from services.geocoding import autocompletar, guardar_lugar_desde_place


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

    # ---------- Autocompletado de lugar ----------
    lugar_seleccionado = {"place_id": None, "descripcion": ""}

    txt_lugar = ft.TextField(
        label="Lugar de venta",
        hint_text="Buscar lugar...",
        border_color=ft.Colors.GREY_700,
        color=ft.Colors.WHITE,
    )

    lista_sugerencias = ft.Column(visible=False, spacing=2)

    def on_lugar_change(e):
        texto = txt_lugar.value or ""
        lugar_seleccionado["place_id"] = None
        lugar_seleccionado["descripcion"] = ""

        if len(texto) < 3:
            lista_sugerencias.visible = False
            page.update()
            return

        sugerencias = autocompletar(texto)

        if not sugerencias:
            lista_sugerencias.visible = False
            page.update()
            return

        lista_sugerencias.controls.clear()
        for s in sugerencias:
            lista_sugerencias.controls.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.LOCATION_ON, color=ft.Colors.RED_400, size=16),
                            ft.Text(s["descripcion"], size=12, color=ft.Colors.WHITE,
                                    expand=True, max_lines=2),
                        ],
                        spacing=8,
                    ),
                    padding=ft.Padding.symmetric(horizontal=10, vertical=8),
                    border_radius=8,
                    ink=True,
                    on_click=lambda e, sug=s: seleccionar_lugar(sug),
                )
            )

        lista_sugerencias.visible = True
        page.update()

    def seleccionar_lugar(sugerencia: dict):
        lugar_seleccionado["place_id"] = sugerencia["place_id"]
        lugar_seleccionado["descripcion"] = sugerencia["descripcion"]
        txt_lugar.value = sugerencia["descripcion"]
        lista_sugerencias.visible = False
        page.update()

    txt_lugar.on_change = on_lugar_change

    contenedor_sugerencias = ft.Container(
        content=lista_sugerencias,
        bgcolor=ft.Colors.GREY_800,
        border_radius=10,
        padding=4,
    )

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

                # Geocodificar el lugar de venta
        lugar_vendido = (txt_lugar.value or "").strip().title()
        if lugar_seleccionado["place_id"]:
            from services.geocoding import obtener_coordenadas_place
            from database.db import conexion as get_conn
            coords = obtener_coordenadas_place(lugar_seleccionado["place_id"])
            if coords:
                with get_conn() as conn:
                    conn.execute(
                        "INSERT OR REPLACE INTO lugares_cache (lugar, lat, lng) VALUES (?, ?, ?)",
                        (lugar_vendido, coords["lat"], coords["lng"]),
                    )
                mensaje.value += f'\n📍 {coords.get("direccion_formateada", lugar_vendido)}'
        elif lugar_vendido:
            from services.geocoding import geocodificar_y_guardar
            geo = geocodificar_y_guardar(lugar_vendido)
            if geo:
                mensaje.value += f'\n📍 {geo.get("lugar", lugar_vendido)}'
                
        # Refrescar el desplegable
        dd_producto.options = [
            ft.dropdown.Option(
                key=str(p["id"]),
                text=f'{p["codigo"]} - {p["nombre"]} ({p["stock"]} u.)',
            )
            for p in productos.listar()
        ]
        dd_producto.value = None
        txt_cantidad.value = "1"
        txt_lugar.value = ""
        lugar_seleccionado["place_id"] = None
        lugar_seleccionado["descripcion"] = ""
        lista_sugerencias.visible = False
        page.update()

        # Popup de stock bajo
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
                txt_lugar,
                contenedor_sugerencias,
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