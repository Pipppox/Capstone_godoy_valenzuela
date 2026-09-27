import flet as ft

from services import sesion
from services.auth import actualizar_foto


# Avatares predefinidos: (icono, color_fondo, color_icono, etiqueta)
AVATARES = [
    (ft.Icons.STORE, ft.Colors.ORANGE_800, ft.Colors.WHITE, "Tienda"),
    (ft.Icons.SHOPPING_BAG, ft.Colors.BLUE_600, ft.Colors.WHITE, "Bolsa"),
    (ft.Icons.RESTAURANT, ft.Colors.RED_700, ft.Colors.WHITE, "Comida"),
    (ft.Icons.CHECKROOM, ft.Colors.PURPLE_600, ft.Colors.WHITE, "Ropa"),
    (ft.Icons.HANDYMAN, ft.Colors.AMBER_700, ft.Colors.WHITE, "Herramientas"),
    (ft.Icons.LOCAL_FLORIST, ft.Colors.GREEN_600, ft.Colors.WHITE, "Flores"),
    (ft.Icons.PETS, ft.Colors.BROWN_600, ft.Colors.WHITE, "Mascotas"),
    (ft.Icons.BRUSH, ft.Colors.PINK_600, ft.Colors.WHITE, "Arte"),
]


def perfil_usuario_view(page: ft.Page):
    usuario = sesion.usuario() or {}
    nombre = usuario.get("nombre", "Usuario")
    apellido = usuario.get("apellido", "")
    email = usuario.get("email", "")
    empresa = usuario.get("nombre_empresa", "")
    foto_actual = usuario.get("foto_perfil", "")

    async def volver(e):
        await page.push_route("/index")

    async def ir_a_configuracion(e):
        await page.push_route("/configuracion")

    # ---------- Foto de perfil ----------
    def construir_avatar(foto: str):
        """Construye el avatar según el valor guardado."""
        if foto and foto.startswith("http"):
            return ft.CircleAvatar(
                radius=55,
                foreground_image_src=foto,
                bgcolor=ft.Colors.GREY_800,
            )
        if foto and foto.startswith("icon:"):
            partes = foto.split(":")
            if len(partes) == 4:
                idx = int(partes[1])
                if 0 <= idx < len(AVATARES):
                    icono, bg, ic, _ = AVATARES[idx]
                    return ft.CircleAvatar(
                        radius=55,
                        bgcolor=bg,
                        content=ft.Icon(icono, color=ic, size=45),
                    )
        return ft.CircleAvatar(
            radius=55,
            bgcolor=ft.Colors.GREY_800,
            content=ft.Icon(ft.Icons.PERSON, color=ft.Colors.GREY_500, size=50),
        )

    img_perfil = construir_avatar(foto_actual)

    contenedor_foto = ft.Container(
        content=img_perfil,
        alignment=ft.Alignment.CENTER,
        on_click=lambda e: mostrar_selector_foto(e),
        ink=True,
    )

    # ---------- Paneles ----------
    panel_principal = ft.Column(spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    panel_confirmar_logout = ft.Column(visible=False, spacing=0,
                                       horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    panel_selector_foto = ft.Column(visible=False, spacing=0,
                                     horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    # ---------- Selector de foto ----------
    mensaje_foto = ft.Text("", size=12, color=ft.Colors.RED_400, text_align=ft.TextAlign.CENTER)
    txt_url = ft.TextField(
        label="URL de tu foto",
        hint_text="https://ejemplo.com/mi-foto.jpg",
        border_color=ft.Colors.GREY_700,
        color=ft.Colors.WHITE,
        keyboard_type=ft.KeyboardType.URL,
    )

    def seleccionar_avatar(idx):
        def handler(e):
            valor = f"icon:{idx}:avatar:predefinido"
            actualizar_foto(usuario["id"], valor)
            usuario["foto_perfil"] = valor
            contenedor_foto.content = construir_avatar(valor)
            panel_selector_foto.visible = False
            panel_principal.visible = True
            page.update()
        return handler

    def guardar_url(e):
        url = (txt_url.value or "").strip()
        if not url:
            mensaje_foto.value = "Ingresa una URL."
            page.update()
            return
        if not url.startswith("http"):
            mensaje_foto.value = "La URL debe empezar con http:// o https://"
            page.update()
            return
        actualizar_foto(usuario["id"], url)
        usuario["foto_perfil"] = url
        contenedor_foto.content = construir_avatar(url)
        txt_url.value = ""
        mensaje_foto.value = ""
        panel_selector_foto.visible = False
        panel_principal.visible = True
        page.update()

    def quitar_foto(e):
        actualizar_foto(usuario["id"], "")
        usuario["foto_perfil"] = ""
        contenedor_foto.content = construir_avatar("")
        panel_selector_foto.visible = False
        panel_principal.visible = True
        page.update()

    def mostrar_selector_foto(e):
        mensaje_foto.value = ""
        panel_principal.visible = False
        panel_selector_foto.visible = True
        page.update()

    def cancelar_selector(e):
        panel_selector_foto.visible = False
        panel_principal.visible = True
        page.update()

    # Grid de avatares
    grid_avatares = ft.Row(
        controls=[
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.CircleAvatar(
                            radius=28,
                            bgcolor=AVATARES[i][1],
                            content=ft.Icon(AVATARES[i][0], color=AVATARES[i][2], size=26),
                        ),
                        ft.Text(AVATARES[i][3], size=9, color=ft.Colors.GREY_400,
                                text_align=ft.TextAlign.CENTER),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=4,
                ),
                on_click=seleccionar_avatar(i),
                ink=True,
                padding=4,
            )
            for i in range(len(AVATARES))
        ],
        wrap=True,
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=10,
        run_spacing=10,
    )

    panel_selector_foto.controls = [
        ft.Row(
            controls=[
                ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color=ft.Colors.WHITE,
                              on_click=cancelar_selector),
                ft.Text("Cambiar foto", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ft.Container(width=40),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        ft.Divider(height=14, color=ft.Colors.TRANSPARENT),
        ft.Text("Elige un avatar", size=13, color=ft.Colors.GREY_400),
        ft.Divider(height=8, color=ft.Colors.TRANSPARENT),
        ft.Container(
            content=grid_avatares,
            bgcolor=ft.Colors.BLACK,
            border_radius=14,
            padding=14,
        ),
        ft.Divider(height=16, color=ft.Colors.TRANSPARENT),
        ft.Text("O usa una URL", size=13, color=ft.Colors.GREY_400),
        ft.Divider(height=8, color=ft.Colors.TRANSPARENT),
        ft.Container(
            content=ft.Column(
                controls=[
                    txt_url,
                    mensaje_foto,
                    ft.Button(
                        content=ft.Text("Usar esta foto", size=12, weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.WHITE),
                        bgcolor=ft.Colors.ORANGE_800,
                        width=180,
                        height=38,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=20)),
                        on_click=guardar_url,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            bgcolor=ft.Colors.BLACK,
            border_radius=14,
            padding=14,
        ),
        ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
        ft.TextButton(
            content=ft.Text("Quitar foto", size=12, color=ft.Colors.RED_400),
            on_click=quitar_foto,
        ),
    ]

    # ---------- Cerrar sesión con confirmación ----------
    def mostrar_confirmar_logout(e):
        panel_principal.visible = False
        panel_confirmar_logout.visible = True
        page.update()

    def cancelar_logout(e):
        panel_confirmar_logout.visible = False
        panel_principal.visible = True
        page.update()

    async def confirmar_logout(e):
        sesion.cerrar()
        await page.push_route("/")

    panel_confirmar_logout.controls = [
        ft.Divider(height=80, color=ft.Colors.TRANSPARENT),
        ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(ft.Icons.LOGOUT, color=ft.Colors.ORANGE_800, size=50),
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    ft.Text("¿Deseas cerrar sesión?",
                            size=18, weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER),
                    ft.Divider(height=6, color=ft.Colors.TRANSPARENT),
                    ft.Text("Tendrás que volver a iniciar sesión\npara acceder a tu cuenta.",
                            size=12, color=ft.Colors.GREY_400, text_align=ft.TextAlign.CENTER),
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    ft.Button(
                        content=ft.Text("Sí, cerrar sesión", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        bgcolor=ft.Colors.ORANGE_800,
                        width=230,
                        height=46,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=25)),
                        on_click=confirmar_logout,
                    ),
                    ft.Divider(height=6, color=ft.Colors.TRANSPARENT),
                    ft.Button(
                        content=ft.Text("No, cancelar", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        bgcolor=ft.Colors.GREY_700,
                        width=230,
                        height=46,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=25)),
                        on_click=cancelar_logout,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,
            ),
            bgcolor=ft.Colors.BLACK,
            border_radius=14,
            padding=30,
        ),
    ]

    # ---------- Info del usuario ----------
    info_usuario = ft.Column(
        controls=[
            ft.Text(f"{nombre} {apellido}", size=22, weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER),
            ft.Text(email, size=13, color=ft.Colors.GREY_400,
                    text_align=ft.TextAlign.CENTER),
            ft.Text(empresa if empresa else "Sin emprendimiento", size=12,
                    color=ft.Colors.ORANGE_800, text_align=ft.TextAlign.CENTER,
                    italic=True),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=4,
    )

    # ---------- Encabezado ----------
    encabezado = ft.Row(
        controls=[
            ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                icon_color=ft.Colors.WHITE,
                on_click=volver,
            ),
            ft.Text("Perfil", size=18, weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER),
            ft.IconButton(
                icon=ft.Icons.SETTINGS,
                icon_color=ft.Colors.GREY_400,
                icon_size=24,
                tooltip="Configuración",
                on_click=ir_a_configuracion,
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # ---------- Botón cerrar sesión ----------
    btn_logout = ft.Button(
        content=ft.Text("Cerrar sesión", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
        bgcolor=ft.Colors.ORANGE_800,
        width=200,
        height=42,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=25)),
        on_click=mostrar_confirmar_logout,
    )

    # ---------- Texto "toca para cambiar" ----------
    hint_foto = ft.Text("Toca la foto para cambiar", size=10, color=ft.Colors.GREY_500,
                        text_align=ft.TextAlign.CENTER)

    # ---------- Contenido principal ----------
    panel_principal.controls = [
        encabezado,
        ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
        contenedor_foto,
        hint_foto,
        ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
        info_usuario,
        ft.Divider(height=30, color=ft.Colors.TRANSPARENT),
        btn_logout,
    ]

    # ---------- Tarjeta Celular ----------
    tarjeta_movil = ft.Container(
        content=ft.Column(
            controls=[
                panel_principal,
                panel_confirmar_logout,
                panel_selector_foto,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
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