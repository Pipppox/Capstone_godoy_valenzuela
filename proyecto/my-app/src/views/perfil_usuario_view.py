import flet as ft

from services import sesion
from services.auth import actualizar_datos


def perfil_usuario_view(page: ft.Page):
    usuario = sesion.usuario() or {}
    nombre = usuario.get("nombre", "Usuario")
    apellido = usuario.get("apellido", "")
    email = usuario.get("email", "")
    telefono = usuario.get("telefono", "")
    empresa = usuario.get("nombre_empresa", "")

    async def volver(e):
        await page.push_route("/index")

    async def ir_a_configuracion(e):
        await page.push_route("/configuracion")

    # ---------- Foto de perfil ----------
    contenedor_foto = ft.CircleAvatar(
        radius=55,
        bgcolor=ft.Colors.GREY_800,
        content=ft.Icon(ft.Icons.PERSON, color=ft.Colors.GREY_500, size=50),
    )

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

    # ---------- Campos editables ----------
    txt_nombre = ft.TextField(
        label="Nombre",
        value=nombre,
        border_color=ft.Colors.GREY_700,
        color=ft.Colors.WHITE,
        capitalization=ft.TextCapitalization.WORDS,
    )
    txt_apellido = ft.TextField(
        label="Apellido",
        value=apellido,
        border_color=ft.Colors.GREY_700,
        color=ft.Colors.WHITE,
        capitalization=ft.TextCapitalization.WORDS,
    )
    txt_email = ft.TextField(
        label="Correo electrónico",
        value=email,
        border_color=ft.Colors.GREY_700,
        color=ft.Colors.WHITE,
        keyboard_type=ft.KeyboardType.EMAIL,
    )
    txt_telefono = ft.TextField(
        label="Numero telefonico",
        value=telefono,
        border_color=ft.Colors.GREY_700,
        color=ft.Colors.WHITE,
        keyboard_type=ft.KeyboardType.PHONE,
    )

    txt_empresa = ft.TextField(
        label="Nombre del emprendimiento",
        value=empresa,
        border_color=ft.Colors.GREY_700,
        color=ft.Colors.WHITE,
        capitalization=ft.TextCapitalization.WORDS,
    )

    mensaje = ft.Text("", size=13, color=ft.Colors.RED_400, text_align=ft.TextAlign.CENTER)

    def guardar_cambios(e):
        mensaje.color = ft.Colors.RED_400
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
            mensaje.value = str(err)
            page.update()
            return

        # Actualizar la sesión en memoria
        sesion.iniciar(usuario_actualizado)

        # Actualizar la info visible
        info_usuario.controls[0] = ft.Text(
            f'{usuario_actualizado["nombre"]} {usuario_actualizado["apellido"]}',
            size=22, weight=ft.FontWeight.BOLD,
            color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER,
        )
        info_usuario.controls[1] = ft.Text(
            usuario_actualizado["email"],
            size=13, color=ft.Colors.GREY_400,
            text_align=ft.TextAlign.CENTER,
        )

        mensaje.color = ft.Colors.GREEN_400
        mensaje.value = "Datos actualizados."
        page.update()

    btn_guardar = ft.Button(
        content=ft.Text("Guardar cambios", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
        bgcolor=ft.Colors.ORANGE_800,
        width=230,
        height=46,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=25)),
        on_click=guardar_cambios,
    )

    formulario = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Editar datos", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_400),
                ft.Divider(height=6, color=ft.Colors.TRANSPARENT),
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

    # ---------- Tarjeta Celular ----------
    tarjeta_movil = ft.Container(
        content=ft.Column(
            controls=[
                encabezado,
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                contenedor_foto,
                ft.Divider(height=14, color=ft.Colors.TRANSPARENT),
                info_usuario,
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                formulario,
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                mensaje,
                btn_guardar,
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