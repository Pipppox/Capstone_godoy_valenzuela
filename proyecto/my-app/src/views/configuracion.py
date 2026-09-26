import flet as ft

from services import sesion


def configuracion_view(page: ft.Page):
    usuario = sesion.usuario() or {}

    async def volver(e):
        await page.push_route("/perfil_usuario")

    async def ir_a_eliminar(e):
        await page.push_route("/eliminar_cuenta")

    # ---------- Notificaciones ----------
    notificaciones_activas = False

    def toggle_notificaciones(e):
        nonlocal notificaciones_activas
        notificaciones_activas = switch_notif.value
        estado = "activadas" if notificaciones_activas else "desactivadas"
        print(f"[CONFIG] Notificaciones {estado}")

    switch_notif = ft.Switch(
        value=False,
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

    # ---------- Tarjeta Celular ----------
    tarjeta_movil = ft.Container(
        content=ft.Column(
            controls=[
                encabezado,
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                ft.Text("General", size=12, color=ft.Colors.GREY_400),
                ft.Divider(height=6, color=ft.Colors.TRANSPARENT),
                fila_notificaciones,
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                ft.Text("Cuenta", size=12, color=ft.Colors.GREY_400),
                ft.Divider(height=6, color=ft.Colors.TRANSPARENT),
                fila_eliminar,
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