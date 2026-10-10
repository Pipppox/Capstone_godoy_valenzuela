from pathlib import Path

import flet as ft

from services import productos, inventario_io


def _obtener_picker(page: ft.Page) -> ft.FilePicker:
    """En Flet 1.0 FilePicker es un servicio: se registra una sola vez en page.services."""
    for servicio in page.services:
        if isinstance(servicio, ft.FilePicker):
            return servicio
    picker = ft.FilePicker()
    page.services.append(picker)
    return picker


def inventario_view(page: ft.Page):
    picker = _obtener_picker(page)

    def carpeta_descargas() -> str | None:
        """Carpeta inicial de los diálogos: Descargas (fuera del proyecto).
        Así el archivo no cae dentro de src/ y 'flet run -r' no reinicia la app."""
        if page.web:
            return None
        descargas = Path.home() / "Downloads"
        return str(descargas if descargas.exists() else Path.home())

    # ---------- Navegación ----------
    async def volver(e):
        await page.push_route("/index")

    async def ir_a_agregar(e):
        await page.push_route("/agregar")

    async def ir_a_vender(e):
        await page.push_route("/vender")

    async def ir_a_perfil(e):
        await page.push_route("/perfil_usuario")

    # ---------- Estado ----------
    lista = productos.listar()
    maximo = productos.maximo_stock(lista)

    contenedor_productos = ft.Column(spacing=14)
    mensaje = ft.Text("", size=13, color=ft.Colors.GREEN_400, text_align=ft.TextAlign.CENTER)

    def mostrar_mensaje(texto: str, ok: bool = True):
        mensaje.color = ft.Colors.GREEN_400 if ok else ft.Colors.RED_400
        mensaje.value = texto

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
                    ft.Text("Sus ventas se conservan en el historial.",
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
            mostrar_mensaje(f'"{producto_a_eliminar["nombre"]}" eliminado.')
        except ValueError as err:
            mostrar_mensaje(str(err), ok=False)
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

        mostrar_mensaje("Producto actualizado.")
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

    # ---------- Exportar ----------
    panel_exportar = ft.Container(visible=False)

    def mostrar_exportar(e):
        panel_exportar.visible = not panel_exportar.visible
        page.update()

    def exportar(formato: str):
        async def handler(e):
            panel_exportar.visible = False
            if not lista:
                mostrar_mensaje("No hay productos para exportar.", ok=False)
                page.update()
                return

            try:
                if formato == "xlsx":
                    datos = inventario_io.exportar_excel()
                else:
                    datos = inventario_io.exportar_csv()
            except Exception as err:
                mostrar_mensaje(f"No se pudo generar el archivo: {err}", ok=False)
                page.update()
                return

            nombre = inventario_io.nombre_archivo(formato)
            ruta = await picker.save_file(
                dialog_title="Guardar inventario",
                file_name=nombre,
                initial_directory=carpeta_descargas(),
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=[formato],
                src_bytes=datos,
            )

            if page.web:
                mostrar_mensaje(f"Descargado como {nombre}")
            elif ruta:
                mostrar_mensaje(f"Inventario exportado ({len(lista)} productos).")
            else:
                mostrar_mensaje("Exportación cancelada.", ok=False)
            page.update()
        return handler

    def boton_formato(texto, icono, color, handler):
        return ft.Button(
            content=ft.Row(
                controls=[
                    ft.Icon(icono, color=ft.Colors.WHITE, size=16),
                    ft.Text(texto, size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ],
                spacing=6,
                tight=True,
            ),
            bgcolor=color,
            height=36,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=20)),
            on_click=handler,
        )

    panel_exportar.content = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("¿En qué formato?", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ft.Row(
                    controls=[
                        boton_formato("Excel", ft.Icons.TABLE_CHART, ft.Colors.GREEN_700, exportar("xlsx")),
                        boton_formato("CSV", ft.Icons.DESCRIPTION, ft.Colors.BLUE_GREY_700, exportar("csv")),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        ),
        bgcolor=ft.Colors.BLACK,
        border_radius=14,
        padding=14,
        border=ft.Border.all(1, ft.Colors.GREY_800),
    )

    # ---------- Importar ----------
    mensaje_importar = ft.Text("", size=12, text_align=ft.TextAlign.CENTER)

    def resultado_importar(texto: str, ok: bool):
        """Muestra el resultado arriba (mensaje) y junto al botón (mensaje_importar)."""
        mostrar_mensaje(texto, ok)
        mensaje_importar.value = texto
        mensaje_importar.color = ft.Colors.GREEN_400 if ok else ft.Colors.RED_400

    async def importar(e):
        mensaje_importar.value = ""
        try:
            archivos = await picker.pick_files(
                dialog_title="Selecciona un archivo de inventario",
                initial_directory=carpeta_descargas(),
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=["xlsx", "csv"],
                with_data=True,
            )
        except Exception as err:
            print(f"[IMPORTAR] Error al abrir el selector: {err!r}")
            resultado_importar(f"No se pudo abrir el selector de archivos: {err}", ok=False)
            page.update()
            return

        if not archivos:
            print("[IMPORTAR] Selección cancelada")
            return

        archivo = archivos[0]
        print(f"[IMPORTAR] Archivo: {archivo.name} | path={archivo.path} | "
              f"bytes={'sí' if archivo.bytes else 'no'}")

        try:
            datos = archivo.bytes
            if datos is None and archivo.path:
                datos = Path(archivo.path).read_bytes()
        except PermissionError:
            resultado_importar(
                "No se pudo leer el archivo. ¿Está abierto en Excel? Ciérralo e intenta de nuevo.",
                ok=False,
            )
            page.update()
            return
        except Exception as err:
            print(f"[IMPORTAR] Error leyendo el archivo: {err!r}")
            resultado_importar(f"No se pudo leer el archivo: {err}", ok=False)
            page.update()
            return

        try:
            analisis = inventario_io.analizar(archivo.name, datos)
        except ValueError as err:
            print(f"[IMPORTAR] {err}")
            resultado_importar(str(err), ok=False)
            page.update()
            return
        except Exception as err:
            print(f"[IMPORTAR] Error inesperado: {err!r}")
            resultado_importar(f"Error al importar: {err}", ok=False)
            page.update()
            return

        print(
            f'[IMPORTAR] Análisis: {len(analisis["nuevos"])} nuevos, '
            f'{len(analisis["actualizar"])} a actualizar, '
            f'{len(analisis["conflictos"])} conflictos, {len(analisis["errores"])} errores'
        )
        mostrar_resumen_importacion(analisis)

    # ---------- Resumen antes de importar (alerta de conflictos) ----------
    panel_importar = ft.Container(visible=False)
    importacion_pendiente: dict = {}

    def _lineas(titulo: str, color, items: list[str], maximo: int = 3):
        if not items:
            return []
        controles = [ft.Text(titulo, size=12, weight=ft.FontWeight.BOLD, color=color)]
        for item in items[:maximo]:
            controles.append(ft.Text(f"• {item}", size=11, color=ft.Colors.GREY_300))
        if len(items) > maximo:
            controles.append(ft.Text(f"(+{len(items) - maximo} más)", size=11, color=ft.Colors.GREY_500))
        return controles

    def mostrar_resumen_importacion(analisis: dict):
        importacion_pendiente.clear()
        importacion_pendiente.update(analisis)

        n_nuevos = len(analisis["nuevos"])
        n_actualizar = len(analisis["actualizar"])
        hay_algo = n_nuevos + n_actualizar > 0

        contenido = [
            ft.Text("Revisar importación", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ft.Text(f"✓ {n_nuevos} productos nuevos", size=12, color=ft.Colors.GREEN_400),
            ft.Text(f"↻ {n_actualizar} se actualizarán (mismo código y nombre)",
                    size=12, color=ft.Colors.BLUE_300),
        ]
        contenido += _lineas(
            f'⚠ {len(analisis["conflictos"])} con código ya usado por otro producto (no se importarán):',
            ft.Colors.AMBER_600, analisis["conflictos"],
        )
        contenido += _lineas(
            f'✕ {len(analisis["errores"])} filas con error (no se importarán):',
            ft.Colors.RED_400, analisis["errores"],
        )
        if not hay_algo:
            contenido.append(ft.Text("No hay productos válidos para importar.",
                                     size=12, color=ft.Colors.GREY_400))

        if hay_algo:
            botones = [
                ft.Button(
                    content=ft.Text("Importar", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    bgcolor=ft.Colors.BLUE_600,
                    height=36,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=20)),
                    on_click=confirmar_importacion,
                ),
                ft.Button(
                    content=ft.Text("Cancelar", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    bgcolor=ft.Colors.GREY_700,
                    height=36,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=20)),
                    on_click=cancelar_importacion,
                ),
            ]
        else:
            # Nada que importar: solo se puede cerrar el panel
            botones = [
                ft.Button(
                    content=ft.Text("Cerrar", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    bgcolor=ft.Colors.GREY_700,
                    height=36,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=20)),
                    on_click=cerrar_resumen,
                ),
            ]

        contenido.append(
            ft.Row(
                controls=botones,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
            )
        )

        hay_problemas = analisis["conflictos"] or analisis["errores"]
        panel_importar.content = ft.Container(
            content=ft.Column(controls=contenido, spacing=6),
            bgcolor=ft.Colors.BLACK,
            border_radius=14,
            padding=14,
            border=ft.Border.all(1, ft.Colors.AMBER_600 if hay_problemas else ft.Colors.GREY_800),
        )
        panel_importar.visible = True
        mensaje_importar.value = ""
        page.update()

    def confirmar_importacion(e):
        resultado = inventario_io.aplicar(importacion_pendiente)
        omitidos = len(importacion_pendiente.get("conflictos", [])) + len(importacion_pendiente.get("errores", []))
        importacion_pendiente.clear()
        panel_importar.visible = False

        texto = (
            f'Importación lista: {resultado["creados"]} nuevos, '
            f'{resultado["actualizados"]} actualizados.'
        )
        if omitidos:
            texto += f" {omitidos} filas omitidas."
        if resultado["errores"]:
            texto += "\n" + "\n".join(resultado["errores"][:3])
        print(f"[IMPORTAR] {texto}")
        resultado_importar(texto, ok=not resultado["errores"])
        refrescar()

    def cancelar_importacion(e):
        importacion_pendiente.clear()
        panel_importar.visible = False
        resultado_importar("Importación cancelada.", ok=False)
        page.update()

    def cerrar_resumen(e):
        importacion_pendiente.clear()
        panel_importar.visible = False
        resultado_importar("No se importó nada: revisa los conflictos del archivo.", ok=False)
        page.update()

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
            boton_accion("Exportar inventario", ft.Icons.FILE_DOWNLOAD, ft.Colors.GREEN_400, mostrar_exportar),
            panel_exportar,
            boton_accion("Importar inventario", ft.Icons.FILE_UPLOAD, ft.Colors.BLUE_400, importar),
            panel_importar,
            mensaje_importar,
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