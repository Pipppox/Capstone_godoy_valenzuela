from pathlib import Path

import flet as ft

from database.db import conexion
from services import estadisticas
from services import productos as srv_productos
from services import inventario_io
from views.inventario_view import _obtener_picker


def dashboard_view(page: ft.Page):
    async def volver(e):
        await page.push_route("/index")

    def proximamente(nombre: str):
        def handler(e):
            print(f"[AVISO] {nombre}: próximamente")
        return handler

    picker = _obtener_picker(page)

    def carpeta_descargas() -> str | None:
        """Carpeta inicial del diálogo: Descargas (fuera del proyecto)."""
        if page.web:
            return None
        descargas = Path.home() / "Downloads"
        return str(descargas if descargas.exists() else Path.home())

    data = estadisticas.resumen()
    lista_productos = srv_productos.listar()

    # ---------- Encabezado ----------
    encabezado = ft.Row(
        controls=[
            ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color=ft.Colors.WHITE,
                          icon_size=22, on_click=volver,
                          style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_600,
                                               shape=ft.CircleBorder())),
            ft.Text("Informacion Ventas", size=18, weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER),
            ft.IconButton(icon=ft.Icons.ACCOUNT_CIRCLE, icon_color=ft.Colors.GREY_500,
                          icon_size=30, on_click=proximamente("Perfil")),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # ---------- Pestañas All / Favorito ----------
    tab_all = ft.Container(
        content=ft.Text("All", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
        bgcolor=ft.Colors.BLUE_600,
        border_radius=20,
        padding=ft.Padding.symmetric(horizontal=20, vertical=8),
    )
    tab_fav = ft.Container(
        content=ft.Text("Favorito", size=12, color=ft.Colors.GREY_500),
        padding=ft.Padding.symmetric(horizontal=20, vertical=8),
        on_click=proximamente("Favoritos"),
    )
    pestanas = ft.Row(controls=[tab_all, tab_fav], spacing=8)

    # ---------- Gráfico de ventas ----------
    dias_7 = data["ultimos_7_dias"]

    if dias_7:
        max_monto = max(d["monto"] for d in dias_7) or 1
        barras = ft.Row(
            controls=[
                ft.Column(
                    controls=[
                        ft.Container(
                            width=24,
                            height=max(int(80 * d["monto"] / max_monto), 4),
                            bgcolor=ft.Colors.ORANGE_800,
                            border_radius=4,
                        ),
                        ft.Text(d["dia"][-5:], size=8, color=ft.Colors.GREY_500),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=4,
                )
                for d in dias_7
            ],
            alignment=ft.MainAxisAlignment.SPACE_EVENLY,
            vertical_alignment=ft.CrossAxisAlignment.END,
            spacing=6,
        )
        contenido_grafico = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Ventas últimos 7 días", size=11, color=ft.Colors.GREY_400),
                    ft.Divider(height=4, color=ft.Colors.TRANSPARENT),
                    ft.Container(content=barras, height=100, alignment=ft.Alignment.BOTTOM_CENTER),
                ],
            ),
            bgcolor=ft.Colors.GREY_900,
            border=ft.Border.all(2, ft.Colors.ORANGE_800),
            border_radius=12,
            padding=14,
        )
    else:
        contenido_grafico = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Ventas últimos 7 días", size=11, color=ft.Colors.GREY_400),
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    ft.Text("Aún no hay ventas registradas.", size=12, color=ft.Colors.GREY_500),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=ft.Colors.GREY_900,
            border=ft.Border.all(2, ft.Colors.ORANGE_800),
            border_radius=12,
            padding=14,
        )

    tarjeta_grafico = ft.Container(
        content=contenido_grafico,
        bgcolor=ft.Colors.BLACK,
        border_radius=18,
        padding=10,
    )

    # ---------- Resumen rápido ----------
    resumen_rapido = ft.Row(
        controls=[
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(ft.Icons.INVENTORY_2, color=ft.Colors.BLUE_400, size=20),
                        ft.Text(str(data["total_productos"]), size=18,
                                weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ft.Text("Productos", size=9, color=ft.Colors.GREY_400),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=2,
                ),
                bgcolor=ft.Colors.BLACK,
                border_radius=12,
                padding=12,
                expand=True,
            ),
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED,
                                color=ft.Colors.RED_400 if data["stock_bajo"] > 0 else ft.Colors.GREEN_400,
                                size=20),
                        ft.Text(str(data["stock_bajo"]), size=18,
                                weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ft.Text("Stock bajo", size=9, color=ft.Colors.GREY_400),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=2,
                ),
                bgcolor=ft.Colors.BLACK,
                border_radius=12,
                padding=12,
                expand=True,
            ),
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(ft.Icons.ATTACH_MONEY, color=ft.Colors.GREEN_400, size=20),
                        ft.Text(f'${data["ventas_dia_monto"]:,}'.replace(",", "."),
                                size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ft.Text("Ventas hoy", size=9, color=ft.Colors.GREY_400),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=2,
                ),
                bgcolor=ft.Colors.BLACK,
                border_radius=12,
                padding=12,
                expand=True,
            ),
        ],
        spacing=10,
    )

    # ---------- Más vendidos ----------
    if lista_productos:
        productos_con_ventas = []
        with conexion() as conn:
            for p in lista_productos:
                vendido = conn.execute(
                    "SELECT COALESCE(SUM(cantidad), 0) AS total FROM ventas WHERE producto_id = ?",
                    (p["id"],),
                ).fetchone()["total"]
                monto_vendido = vendido * p["precio"]
                productos_con_ventas.append({**p, "vendido": vendido, "monto_vendido": monto_vendido})
        productos_con_ventas.sort(key=lambda x: x["vendido"], reverse=True)
        top_5 = productos_con_ventas[:5]
    else:
        top_5 = []

    if top_5:
        filas_top = [
            ft.Row(
                controls=[
                    ft.Text(p["nombre"], size=12, color=ft.Colors.WHITE, width=90),
                    ft.ProgressBar(
                        value=p["vendido"] / max(top_5[0]["vendido"], 1),
                        color=ft.Colors.GREEN_400,
                        bgcolor=ft.Colors.GREY_800,
                        height=5,
                        border_radius=3,
                        expand=True,
                    ),
                    ft.Text(f'${p["monto_vendido"]:,}'.replace(",", "."),
                            size=11, color=ft.Colors.GREY_400, width=70,
                            text_align=ft.TextAlign.RIGHT),
                ],
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            )
            for p in top_5
        ]
    else:
        filas_top = [ft.Text("Sin ventas aún.", size=12, color=ft.Colors.GREY_500)]

    seccion_mas_vendidos = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Mas vendidos", size=16, weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER),
                ft.Divider(height=8, color=ft.Colors.TRANSPARENT),
                *filas_top,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        ),
        bgcolor=ft.Colors.BLACK,
        border_radius=14,
        padding=18,
    )
    # ---------- Mejores lugares de venta ----------
    lugares = data["lugares"]
    top_por_lugar = data["top_por_lugar"]

    if lugares:
        max_lugar = lugares[0]["monto"] or 1

        filas_lugares = []
        for lugar in lugares:
            # Buscar el producto top en este lugar
            mejor_producto = ""
            for tpl in top_por_lugar:
                if tpl["lugar"] == lugar["lugar"]:
                    mejor_producto = tpl["producto"]
                    break

            filas_lugares.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Icon(ft.Icons.LOCATION_ON, color=ft.Colors.BLUE_400, size=18),
                                    ft.Text(lugar["lugar"], size=13, weight=ft.FontWeight.BOLD,
                                            color=ft.Colors.WHITE, expand=True),
                                    ft.Text(f'${lugar["monto"]:,}'.replace(",", "."),
                                            size=12, color=ft.Colors.GREEN_400),
                                ],
                                spacing=8,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            ft.Row(
                                controls=[
                                    ft.ProgressBar(
                                        value=lugar["monto"] / max_lugar,
                                        color=ft.Colors.BLUE_400,
                                        bgcolor=ft.Colors.GREY_800,
                                        height=4,
                                        border_radius=3,
                                        expand=True,
                                    ),
                                ],
                            ),
                            ft.Row(
                                controls=[
                                    ft.Text(f'{lugar["unidades"]}u · {lugar["num_ventas"]} ventas',
                                            size=10, color=ft.Colors.GREY_500),
                                    ft.Text(f'Top: {mejor_producto}' if mejor_producto else "",
                                            size=10, color=ft.Colors.ORANGE_800, italic=True),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                        ],
                        spacing=4,
                    ),
                    padding=ft.Padding.symmetric(horizontal=4, vertical=6),
                )
            )

        seccion_lugares = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.MAP, color=ft.Colors.BLUE_400, size=20),
                            ft.Text("Mejores lugares de venta", size=14,
                                    weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ],
                        spacing=8,
                    ),
                    ft.Divider(height=8, color=ft.Colors.TRANSPARENT),
                    *filas_lugares,
                ],
                spacing=4,
            ),
            bgcolor=ft.Colors.BLACK,
            border_radius=14,
            padding=18,
        )
    else:
        seccion_lugares = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.MAP, color=ft.Colors.BLUE_400, size=20),
                            ft.Text("Mejores lugares de venta", size=14,
                                    weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ],
                        spacing=8,
                    ),
                    ft.Divider(height=6, color=ft.Colors.TRANSPARENT),
                    ft.Text("Registra el lugar al vender para ver estadísticas aquí.",
                            size=12, color=ft.Colors.GREY_500),
                ],
                spacing=4,
            ),
            bgcolor=ft.Colors.BLACK,
            border_radius=14,
            padding=18,
        )
            # ---------- Historial por lugar ----------
    historial = data["historial_lugares"]

    if historial:
        # Agrupar por día
        dias_dict = {}
        for h in historial:
            dia = h["dia"]
            if dia not in dias_dict:
                dias_dict[dia] = []
            dias_dict[dia].append(h)

        filas_historial = []
        for dia, registros in dias_dict.items():
            filas_historial.append(
                ft.Text(dia, size=13, weight=ft.FontWeight.BOLD,
                        color=ft.Colors.ORANGE_800),
            )
            for r in registros:
                filas_historial.append(
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.LOCATION_ON, color=ft.Colors.GREY_500, size=14),
                            ft.Text(r["lugar"], size=11, color=ft.Colors.WHITE, width=80),
                            ft.Text(r["producto"], size=11, color=ft.Colors.GREY_400, expand=True),
                            ft.Text(f'{r["unidades"]}u', size=10, color=ft.Colors.GREY_500, width=30),
                            ft.Text(f'${r["monto"]:,}'.replace(",", "."),
                                    size=11, color=ft.Colors.GREEN_400, width=65,
                                    text_align=ft.TextAlign.RIGHT),
                        ],
                        spacing=6,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                )
            filas_historial.append(ft.Divider(height=8, color=ft.Colors.GREY_800))

        seccion_historial = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.HISTORY, color=ft.Colors.ORANGE_800, size=20),
                            ft.Text("Historial por lugar", size=14,
                                    weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ],
                        spacing=8,
                    ),
                    ft.Divider(height=8, color=ft.Colors.TRANSPARENT),
                    *filas_historial,
                ],
                spacing=4,
            ),
            bgcolor=ft.Colors.BLACK,
            border_radius=14,
            padding=18,
        )
    else:
        seccion_historial = ft.Container(visible=False)

    # ---------- Exportar ventas (solo exportar) ----------
    mensaje_exportar = ft.Text("", size=12, text_align=ft.TextAlign.CENTER)
    panel_exportar = ft.Container(visible=False)

    def mostrar_resultado(texto: str, ok: bool = True):
        mensaje_exportar.value = texto
        mensaje_exportar.color = ft.Colors.GREEN_400 if ok else ft.Colors.RED_400

    def mostrar_exportar(e):
        panel_exportar.visible = not panel_exportar.visible
        mensaje_exportar.value = ""
        page.update()

    def exportar_ventas(formato: str):
        async def handler(e):
            panel_exportar.visible = False
            try:
                if formato == "xlsx":
                    datos = inventario_io.exportar_ventas_excel()
                else:
                    datos = inventario_io.exportar_ventas_csv()
            except ValueError as err:
                mostrar_resultado(str(err), ok=False)
                page.update()
                return
            except Exception as err:
                print(f"[EXPORTAR VENTAS] Error: {err!r}")
                mostrar_resultado(f"No se pudo generar el archivo: {err}", ok=False)
                page.update()
                return

            nombre = inventario_io.nombre_archivo_ventas(formato)
            ruta = await picker.save_file(
                dialog_title="Guardar ventas",
                file_name=nombre,
                initial_directory=carpeta_descargas(),
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=[formato],
                src_bytes=datos,
            )

            if page.web:
                mostrar_resultado(f"Descargado como {nombre}")
            elif ruta:
                mostrar_resultado("Ventas exportadas correctamente.")
            else:
                mostrar_resultado("Exportación cancelada.", ok=False)
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
                        boton_formato("Excel", ft.Icons.TABLE_CHART, ft.Colors.GREEN_700, exportar_ventas("xlsx")),
                        boton_formato("CSV", ft.Icons.DESCRIPTION, ft.Colors.BLUE_GREY_700, exportar_ventas("csv")),
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

    btn_exportar = ft.Container(
        content=ft.Row(
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.FILE_DOWNLOAD, color=ft.Colors.GREEN_400, size=20),
                        ft.Text("Exportar ventas", size=13, weight=ft.FontWeight.BOLD,
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
        on_click=mostrar_exportar,
        ink=True,
    )

    # ---------- Barra inferior ----------
    barra_inferior = ft.Container(
        content=ft.Row(
            controls=[
                ft.IconButton(icon=ft.Icons.HOME, icon_color=ft.Colors.GREY_500,
                              icon_size=22, on_click=volver),
                ft.Container(
                    content=ft.Icon(ft.Icons.ADD, color=ft.Colors.WHITE, size=24),
                    width=48, height=48, bgcolor=ft.Colors.BLUE_600,
                    border_radius=24, alignment=ft.Alignment.CENTER,
                    on_click=proximamente("Agregar producto"), ink=True,
                ),
                ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, icon_color=ft.Colors.GREY_500,
                              icon_size=22, on_click=proximamente("Vender producto")),
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
                        pestanas,
                        ft.Divider(height=8, color=ft.Colors.TRANSPARENT),
                        tarjeta_grafico,
                        ft.Divider(height=8, color=ft.Colors.TRANSPARENT),
                        resumen_rapido,
                        ft.Divider(height=8, color=ft.Colors.TRANSPARENT),
                        seccion_mas_vendidos,
                        ft.Divider(height=8, color=ft.Colors.TRANSPARENT),
                        seccion_lugares,
                        ft.Divider(height=8, color=ft.Colors.TRANSPARENT),
                        seccion_historial,
                        ft.Divider(height=8, color=ft.Colors.TRANSPARENT),
                        btn_exportar,
                        panel_exportar,
                        mensaje_exportar,
                    ],
                    spacing=0,
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