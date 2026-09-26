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

    async def ir_a_perfil(e):
            await page.push_route("/perfil_usuario")  

    def proximamente(nombre_vista: str):
        async def _handler(e):
            print(f"[AVISO] {nombre_vista}: próximamente")
        return _handler

    # ---------- Estado ----------
    lista = productos.listar()
    maximo = productos.maximo_stock(lista)

    contenedor_productos = ft.Column(spacing=14)
    mensaje = ft.Text("", size=13, color=ft.Colors.GREEN_400, text_align=ft.TextAlign.CENTER)

    def refrescar():
        nonlocal lista, maximo
        lista = productos.listar()
        maximo = productos.maximo_stock(lista)
        contenedor_productos.controls.clear()
        if lista:
            for p in lista:
                contenedor_productos.controls.append(fila_producto(p))
        else:
            contenedor_productos.controls.append(
                ft.Text("Aún no tienes productos. Agrega el primero.",
                        size=12, color=ft.Colors.GREY_500),
            )
        page.update()

    # ---------- Eliminar producto ----------
    panel_confirmar = ft.Container(visible=False)
    producto_a_eliminar = {"id": None, "nombre": ""}

    def pedir_confirmar_eliminar(producto):
        def handler(e):
            producto_a_eliminar["id"] = producto["id"]
            producto_a_eliminar["nombre"] = producto["nombre"]
            panel_confirmar.content = ft.Column(
                controls=[
                    ft.Text(f'¿Eliminar "{producto["nombre"]}"?',
                            size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE,
                            text_align=ft.TextAlign.CENTER),
                    ft.Text("Se eliminarán también sus ventas registradas.",
                            size=11, color=ft.Colors.GREY_400, text_align=ft.TextAlign.CENTER),
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    ft.Row(
                        controls=[
                            ft.Button(
                                content=ft.Text("Sí, eliminar", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                bgcolor=ft.Colors.RED_700,
                                height=36,
                                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=20)),
                                on_click=confirmar_eliminar,
                            ),
                            ft.Button(
                                content=ft.Text("Cancelar", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                bgcolor=ft.Colors.GREY_700,
                                height=36,
                                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=20)),
                                on_click=cancelar_eliminar,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=10,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
            panel_confirmar.visible = True
            page.update()
        return handler

    def confirmar_eliminar(e):
        try:
            productos.eliminar(producto_a_eliminar["id"])
            mensaje.color = ft.Colors.GREEN_400
            mensaje.value = f'"{producto_a_eliminar["nombre"]}" eliminado.'
        except ValueError as err:
            mensaje.color = ft.Colors.RED_400
            mensaje.value = str(err)
        panel_confirmar.visible = False
        refrescar()

    def cancelar_eliminar(e):
        panel_confirmar.visible = False
        page.update()

    # ---------- Editar producto ----------
    panel_editar = ft.Container(visible=False)
    producto_editando = {"id": None}

    txt_edit_codigo = ft.TextField(label="Código", border_color=ft.Colors.GREY_700, color=ft.Colors.WHITE)
    txt_edit_nombre = ft.TextField(label="Nombre / Descripción", border_color=ft.Colors.GREY_700, color=ft.Colors.WHITE)
    txt_edit_categoria = ft.TextField(label="Categoría", border_color=ft.Colors.GREY_700, color=ft.Colors.WHITE)
    txt_edit_precio = ft.TextField(label="Precio ($)", border_color=ft.Colors.GREY_700, color=ft.Colors.WHITE, keyboard_type=ft.KeyboardType.NUMBER)
    txt_edit_stock = ft.TextField(label="Stock", border_color=ft.Colors.GREY_700, color=ft.Colors.WHITE, keyboard_type=ft.KeyboardType.NUMBER)
    mensaje_editar = ft.Text("", size=12, color=ft.Colors.RED_400, text_align=ft.TextAlign.CENTER)

    def abrir_editar(producto):
        def handler(e):
            producto_editando["id"] = producto["id"]
            txt_edit_codigo.value = producto["codigo"]
            txt_edit_nombre.value = producto["nombre"]
            txt_edit_categoria.value = producto["categoria"]
            txt_edit_precio.value = str(producto["precio"])
            txt_edit_stock.value = str(producto["stock"])
            mensaje_editar.value = ""
            panel_editar.visible = True
            panel_lista.visible = False
            page.update()
        return handler

    def guardar_edicion(e):
        mensaje_editar.color = ft.Colors.RED_400
        try:
            productos.actualizar(
                producto_editando["id"],
                txt_edit_codigo.value,
                txt_edit_nombre.value,
                txt_edit_categoria.value,
                txt_edit_precio.value,
                txt_edit_stock.value,
            )
        except ValueError as err:
            mensaje_editar.value = str(err)
            page.update()
            return

        mensaje.color = ft.Colors.GREEN_400
        mensaje.value = "Producto actualizado."
        panel_editar.visible = False
        panel_lista.visible = True
        refrescar()

    def cancelar_edicion(e):
        panel_editar.visible = False
        panel_lista.visible = True
        page.update()

    panel_editar.content = ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color=ft.Colors.WHITE, on_click=cancelar_edicion),
                    ft.Text("Editar Producto", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ],
                alignment=ft.MainAxisAlignment.START,
            ),
            ft.Divider(height=6, color=ft.Colors.TRANSPARENT),
            txt_edit_codigo,
            txt_edit_nombre,
            txt_edit_categoria,
            txt_edit_precio,
            txt_edit_stock,
            mensaje_editar,
            ft.Divider(height=6, color=ft.Colors.TRANSPARENT),
            ft.Row(
                controls=[
                    ft.Button(
                        content=ft.Text("Guardar", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        bgcolor=ft.Colors.ORANGE_800,
                        height=40,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=20)),
                        on_click=guardar_edicion,
                    ),
                    ft.Button(
                        content=ft.Text("Cancelar", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        bgcolor=ft.Colors.GREY_700,
                        height=40,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=20)),
                        on_click=cancelar_edicion,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
            ),
        ],
        spacing=10,
    )

    # ---------- Fila de producto ----------
    def fila_producto(producto: dict):
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Text(producto["nombre"], size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                            ft.Text(f'{producto["codigo"]} · {producto["categoria"]}', size=10, color=ft.Colors.GREY_400),
                            ft.Row(
                                controls=[
                                    ft.ProgressBar(
                                        value=productos.proporcion(producto, maximo),
                                        color=productos.color_stock(producto["stock"]),
                                        bgcolor=ft.Colors.GREY_800,
                                        height=5,
                                        border_radius=3,
                                        width=120,
                                    ),
                                    ft.Text(f'{producto["stock"]}u · ${producto["precio"]:,}'.replace(",", "."),
                                            size=10, color=ft.Colors.GREY_400),
                                ],
                                spacing=8,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                        ],
                        spacing=3,
                        expand=True,
                    ),
                    ft.IconButton(icon=ft.Icons.EDIT, icon_color=ft.Colors.BLUE_400,
                                  icon_size=20, tooltip="Editar",
                                  on_click=abrir_editar(producto)),
                    ft.IconButton(icon=ft.Icons.DELETE, icon_color=ft.Colors.RED_400,
                                  icon_size=20, tooltip="Eliminar",
                                  on_click=pedir_confirmar_eliminar(producto)),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=ft.Colors.BLACK,
            border_radius=12,
            padding=ft.Padding.symmetric(horizontal=14, vertical=10),
        )

    # ---------- Encabezado ----------
    encabezado = ft.Row(
        controls=[
            ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color=ft.Colors.WHITE, on_click=volver),
            ft.Text("Inventario", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ft.IconButton(icon=ft.Icons.ACCOUNT_CIRCLE, icon_color=ft.Colors.GREY_500,
                          icon_size=30, tooltip="Perfil", on_click=ir_a_perfil),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # ---------- Botones de acción ----------
    def boton_accion(texto, icono, color, handler):
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Row(controls=[ft.Icon(icono, color=color, size=20),
                                     ft.Text(texto, size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)], spacing=12),
                    ft.Icon(ft.Icons.CHEVRON_RIGHT, color=ft.Colors.GREY_500, size=20),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            bgcolor=ft.Colors.BLACK, border_radius=14,
            padding=ft.Padding.symmetric(horizontal=16, vertical=14),
            on_click=handler, ink=True,
        )

    # ---------- Barra inferior ----------
    barra_inferior = ft.Container(
        content=ft.Row(
            controls=[
                ft.IconButton(icon=ft.Icons.HOME, icon_color=ft.Colors.GREY_500, icon_size=22, on_click=volver),
                ft.Container(content=ft.Icon(ft.Icons.ADD, color=ft.Colors.WHITE, size=24),
                             width=48, height=48, bgcolor=ft.Colors.BLUE_600, border_radius=24,
                             alignment=ft.Alignment.CENTER, on_click=ir_a_agregar, ink=True),
                ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, icon_color=ft.Colors.GREY_500,
                              icon_size=22, on_click=ir_a_vender),
            ],
            alignment=ft.MainAxisAlignment.SPACE_AROUND,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        height=64,
    )

    # Llenar lista inicial
    refrescar()

    # ---------- Panel lista ----------
    panel_lista = ft.Column(
        controls=[
            encabezado,
            ft.Divider(height=8, color=ft.Colors.TRANSPARENT),
            ft.Text("Inventario total", size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            mensaje,
            panel_confirmar,
            contenedor_productos,
            ft.Divider(height=8, color=ft.Colors.TRANSPARENT),
            boton_accion("Agregar Producto", ft.Icons.ADD_BOX, ft.Colors.ORANGE_800, ir_a_agregar),
            boton_accion("Vender Producto", ft.Icons.SELL, ft.Colors.RED_400, ir_a_vender),
        ],
        spacing=12,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

    # ---------- Tarjeta Celular ----------
    tarjeta_movil = ft.Container(
        content=ft.Column(
            controls=[
                ft.Column(
                    controls=[panel_lista, panel_editar],
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