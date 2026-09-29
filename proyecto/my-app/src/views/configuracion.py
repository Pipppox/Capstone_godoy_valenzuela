import flet as ft

from services import sesion
from services.auth import actualizar_datos
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