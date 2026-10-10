import flet as ft

from services import sesion, respaldo
from services.auth import actualizar_datos, actualizar_notificaciones


def configuracion_view(page: ft.Page):
    usuario = sesion.usuario() or {}

    async def volver(e):
        await page.push_route("/perfil_usuario")

    async def ir_a_eliminar(e):
        await page.push_route("/eliminar_cuenta")

        # ---------- Notificaciones ----------
    notif_activas = bool(usuario.get("notificaciones", 0))

    def toggle_notificaciones(e):
        actualizar_notificaciones(usuario["id"], switch_notif.value)
        usuario["notificaciones"] = 1 if switch_notif.value else 0
        sesion.iniciar(usuario)

    switch_notif = ft.Switch(
        value=notif_activas,
        active_color=ft.Colors.ORANGE_800,
        on_change=toggle_notificaciones,
    )

    fila_notificaciones = ft.Container(
        content=ft.Row(
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.NOTIFICATIONS_OUTLINED, color=ft.Colors.WHITE, size=22),
                        ft.Text("Activar Notificaciones", size=14, color=ft.Colors.WHITE),
                    ],
                    spacing=12,
                ),
                switch_notif,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor=ft.Colors.BLACK,
        border_radius=14,
        padding=ft.Padding.symmetric(horizontal=16, vertical=12),
    )

    # ---------- Respaldo en la nube ----------
    def texto_ultimo() -> str:
        fecha = respaldo.ultimo_respaldo()
        return f"Último respaldo: {fecha}" if fecha else "Aún no has respaldado tus datos"

    lbl_ultimo = ft.Text(texto_ultimo(), size=11, color=ft.Colors.GREY_500)
    accion_respaldo = {"tipo": None}  # "respaldar" o "restaurar"

    txt_pass_respaldo = ft.TextField(
        label="Confirma tu contraseña",
        password=True,
        can_reveal_password=True,
        border_color=ft.Colors.GREY_700,
        color=ft.Colors.WHITE,
    )
    lbl_titulo_respaldo = ft.Text("", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
    lbl_aviso_respaldo = ft.Text("", size=11, color=ft.Colors.GREY_400)
    mensaje_respaldo = ft.Text("", size=12, text_align=ft.TextAlign.CENTER)
    cargando = ft.ProgressRing(width=18, height=18, stroke_width=2,
                               color=ft.Colors.ORANGE_800, visible=False)
    btn_confirmar = ft.Button(
        content=ft.Text("Confirmar", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
        bgcolor=ft.Colors.ORANGE_800,
        height=38,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=20)),
    )
    btn_cancelar_respaldo = ft.Button(
        content=ft.Text("Cancelar", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
        bgcolor=ft.Colors.GREY_700,
        height=38,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=20)),
    )

    panel_respaldo = ft.Container(
        visible=False,
        content=ft.Column(
            controls=[
                lbl_titulo_respaldo,
                lbl_aviso_respaldo,
                txt_pass_respaldo,
                ft.Row(
                    controls=[btn_confirmar, btn_cancelar_respaldo, cargando],
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10,
                ),
            ],
            spacing=10,
        ),
        bgcolor=ft.Colors.BLACK,
        border_radius=14,
        padding=16,
        border=ft.Border.all(1, ft.Colors.GREY_800),
    )

    def resultado_respaldo(texto: str, ok: bool):
        mensaje_respaldo.value = texto
        mensaje_respaldo.color = ft.Colors.GREEN_400 if ok else ft.Colors.RED_400

    def abrir_panel(tipo: str):
        def handler(e):
            accion_respaldo["tipo"] = tipo
            txt_pass_respaldo.value = ""
            mensaje_respaldo.value = ""
            if tipo == "respaldar":
                lbl_titulo_respaldo.value = "Respaldar en la nube"
                lbl_aviso_respaldo.value = ("Se subirán tus productos, ventas y lugares, "
                                            "cifrados con tu contraseña.")
                lbl_aviso_respaldo.color = ft.Colors.GREY_400
            else:
                lbl_titulo_respaldo.value = "Restaurar respaldo"
                lbl_aviso_respaldo.value = ("⚠ Se reemplazarán los productos y ventas de este "
                                            "dispositivo por los del respaldo.")
                lbl_aviso_respaldo.color = ft.Colors.AMBER_600
            panel_respaldo.visible = True
            page.update()
        return handler

    def cerrar_panel(e=None):
        panel_respaldo.visible = False
        txt_pass_respaldo.value = ""
        page.update()

    def ejecutar_respaldo(e):
        password = txt_pass_respaldo.value or ""
        btn_confirmar.disabled = True
        cargando.visible = True
        mensaje_respaldo.value = ""
        page.update()

        try:
            if accion_respaldo["tipo"] == "respaldar":
                r = respaldo.respaldar(password)
                resultado_respaldo(
                    f'Respaldo listo: {r["productos"]} productos y {r["ventas"]} ventas.', ok=True)
                lbl_ultimo.value = texto_ultimo()
            else:
                r = respaldo.restaurar(password)
                resultado_respaldo(
                    f'Datos restaurados: {r["productos"]} productos y {r["ventas"]} ventas '
                    f'(respaldo del {r["fecha"]}).', ok=True)
            panel_respaldo.visible = False
            txt_pass_respaldo.value = ""
        except ValueError as err:
            resultado_respaldo(str(err), ok=False)
        except Exception as err:
            print(f"[RESPALDO] Error inesperado: {err!r}")
            resultado_respaldo(f"Error inesperado: {err}", ok=False)
        finally:
            btn_confirmar.disabled = False
            cargando.visible = False
            page.update()

    btn_confirmar.on_click = ejecutar_respaldo
    btn_cancelar_respaldo.on_click = cerrar_panel
    txt_pass_respaldo.on_submit = ejecutar_respaldo

    def fila_opcion(texto, icono, color, handler, subtitulo=None):
        textos = [ft.Text(texto, size=14, color=ft.Colors.WHITE)]
        if subtitulo is not None:
            textos.append(subtitulo)
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(icono, color=color, size=22),
                            ft.Column(controls=textos, spacing=2),
                        ],
                        spacing=12,
                    ),
                    ft.Icon(ft.Icons.CHEVRON_RIGHT, color=ft.Colors.GREY_500, size=20),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=ft.Colors.BLACK,
            border_radius=14,
            padding=ft.Padding.symmetric(horizontal=16, vertical=14),
            on_click=handler,
            ink=True,
        )

    fila_respaldar = fila_opcion("Respaldar ahora", ft.Icons.CLOUD_UPLOAD_OUTLINED,
                                 ft.Colors.GREEN_400, abrir_panel("respaldar"), lbl_ultimo)
    fila_restaurar = fila_opcion("Restaurar respaldo", ft.Icons.CLOUD_DOWNLOAD_OUTLINED,
                                 ft.Colors.BLUE_400, abrir_panel("restaurar"))

    # ---------- Eliminar cuenta ----------
    fila_eliminar = ft.Container(
        content=ft.Row(
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.DELETE_FOREVER, color=ft.Colors.RED_400, size=22),
                        ft.Text("Eliminar Cuenta", size=14, color=ft.Colors.RED_400),
                    ],
                    spacing=12,
                ),
                ft.Icon(ft.Icons.CHEVRON_RIGHT, color=ft.Colors.GREY_500, size=20),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor=ft.Colors.BLACK,
        border_radius=14,
        padding=ft.Padding.symmetric(horizontal=16, vertical=14),
        on_click=ir_a_eliminar,
        ink=True,
    )

    # ---------- Editar datos ----------
    panel_principal = ft.Column(spacing=0)
    panel_editar = ft.Column(visible=False, spacing=0)

    txt_nombre = ft.TextField(
        label="Nombre", value=usuario.get("nombre", ""),
        border_color=ft.Colors.GREY_700, color=ft.Colors.WHITE,
        capitalization=ft.TextCapitalization.WORDS,
    )
    txt_apellido = ft.TextField(
        label="Apellido", value=usuario.get("apellido", ""),
        border_color=ft.Colors.GREY_700, color=ft.Colors.WHITE,
        capitalization=ft.TextCapitalization.WORDS,
    )
    txt_email = ft.TextField(
        label="Correo electrónico", value=usuario.get("email", ""),
        border_color=ft.Colors.GREY_700, color=ft.Colors.WHITE,
        keyboard_type=ft.KeyboardType.EMAIL,
    )
    txt_telefono = ft.TextField(
        label="Numero telefonico", value=usuario.get("telefono", ""),
        border_color=ft.Colors.GREY_700, color=ft.Colors.WHITE,
        keyboard_type=ft.KeyboardType.PHONE,
    )
    txt_empresa = ft.TextField(
        label="Nombre del emprendimiento", value=usuario.get("nombre_empresa", ""),
        border_color=ft.Colors.GREY_700, color=ft.Colors.WHITE,
        capitalization=ft.TextCapitalization.WORDS,
    )

    mensaje_editar = ft.Text("", size=13, color=ft.Colors.RED_400, text_align=ft.TextAlign.CENTER)

    def mostrar_editar(e):
        panel_principal.visible = False
        panel_editar.visible = True
        mensaje_editar.value = ""
        page.update()

    def cancelar_editar(e):
        panel_editar.visible = False
        panel_principal.visible = True
        page.update()

    def guardar_cambios(e):
        mensaje_editar.color = ft.Colors.RED_400
        try:
            usuario_actualizado = actualizar_datos(
                usuario["id"],
                txt_nombre.value,
                txt_apellido.value,
                txt_email.value,
                txt_telefono.value,
                txt_empresa.value,
            )
        except ValueError as err:
            mensaje_editar.value = str(err)
            page.update()
            return

        sesion.iniciar(usuario_actualizado)
        mensaje_editar.color = ft.Colors.GREEN_400
        mensaje_editar.value = "Datos actualizados."
        page.update()

    fila_editar_datos = ft.Container(
        content=ft.Row(
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.EDIT, color=ft.Colors.BLUE_400, size=22),
                        ft.Text("Editar Datos", size=14, color=ft.Colors.WHITE),
                    ],
                    spacing=12,
                ),
                ft.Icon(ft.Icons.CHEVRON_RIGHT, color=ft.Colors.GREY_500, size=20),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor=ft.Colors.BLACK,
        border_radius=14,
        padding=ft.Padding.symmetric(horizontal=16, vertical=14),
        on_click=mostrar_editar,
        ink=True,
    )

    panel_editar.controls = [
        ft.Row(
            controls=[
                ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color=ft.Colors.WHITE, on_click=cancelar_editar),
                ft.Text("Editar Datos", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ft.Container(width=40),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
        ft.Container(
            content=ft.Column(
                controls=[
                    txt_nombre,
                    txt_apellido,
                    txt_email,
                    txt_telefono,
                    txt_empresa,
                ],
                spacing=12,
            ),
            bgcolor=ft.Colors.BLACK,
            border_radius=14,
            padding=18,
        ),
        ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
        mensaje_editar,
        ft.Row(
            controls=[
                ft.Button(
                    content=ft.Text("Guardar", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    bgcolor=ft.Colors.ORANGE_800,
                    height=42,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=20)),
                    on_click=guardar_cambios,
                ),
                ft.Button(
                    content=ft.Text("Cancelar", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    bgcolor=ft.Colors.GREY_700,
                    height=42,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=20)),
                    on_click=cancelar_editar,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
        ),
    ]

    # ---------- Encabezado ----------
    encabezado = ft.Row(
        controls=[
            ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                icon_color=ft.Colors.WHITE,
                on_click=volver,
            ),
            ft.Text("Configuración", size=18, weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER),
            ft.Container(width=40),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # ---------- Panel principal ----------
    panel_principal.controls = [
        encabezado,
        ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
        ft.Text("General", size=12, color=ft.Colors.GREY_400),
        ft.Divider(height=6, color=ft.Colors.TRANSPARENT),
        fila_notificaciones,
        ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
        ft.Text("Respaldo en la nube", size=12, color=ft.Colors.GREY_400),
        ft.Divider(height=6, color=ft.Colors.TRANSPARENT),
        fila_respaldar,
        ft.Divider(height=8, color=ft.Colors.TRANSPARENT),
        fila_restaurar,
        ft.Divider(height=8, color=ft.Colors.TRANSPARENT),
        panel_respaldo,
        mensaje_respaldo,
        ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
        ft.Text("Cuenta", size=12, color=ft.Colors.GREY_400),
        ft.Divider(height=6, color=ft.Colors.TRANSPARENT),
        fila_editar_datos,
        ft.Divider(height=8, color=ft.Colors.TRANSPARENT),
        fila_eliminar,
    ]

    # ---------- Tarjeta Celular ----------
    tarjeta_movil = ft.Container(
        content=ft.Column(
            controls=[
                panel_principal,
                panel_editar,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.START,
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
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