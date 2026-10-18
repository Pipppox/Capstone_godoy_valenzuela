import flet as ft

TERMINOS = [
    ("Datos que recopilamos",
     "Nombre, correo electrónico, contraseña (guardada solo como hash cifrado), "
     "productos, ventas, lugares de venta y la foto de perfil si la subes."),
    ("Para qué los usamos",
     "Para operar la app: manejar tu inventario, registrar ventas, mostrar el mapa "
     "de lugares de venta, generar alertas de stock y respaldar tu información."),
    ("Dónde se guardan",
     "Tu información se guarda en el dispositivo. Si usas el respaldo en la nube, "
     "se cifra con tu contraseña antes de salir del dispositivo."),
    ("Terceros",
     "No vendemos tus datos. Para funcionar usamos servicios de terceros: Google Maps "
     "(las direcciones de venta se envían a Google para ubicarlas) y Supabase (respaldo)."),
    ("Tus derechos",
     "Puedes ver, corregir o eliminar tus datos. Para eliminar tu cuenta, usa la "
     "opción 'Eliminar cuenta' en Configuración."),
    ("Protección legal",
     "Tratamos tus datos conforme a la legislación chilena de protección de datos "
     "personales (Ley N° 19.628)."),
]


def panel_terminos(page: ft.Page, al_aceptar, al_rechazar) -> ft.Container:
    """Panel superpuesto con los términos. Empieza oculto (visible=False).

    al_aceptar / al_rechazar: funciones async que reciben el evento.
    """

    async def aceptar(e):
        panel.visible = False
        page.update()
        await al_aceptar(e)

    async def rechazar(e):
        panel.visible = False
        page.update()
        await al_rechazar(e)

    secciones = []
    for titulo, texto in TERMINOS:
        secciones.append(ft.Text(titulo, size=13, weight=ft.FontWeight.BOLD,
                                 color=ft.Colors.ON_SURFACE))
        secciones.append(ft.Text(texto, size=11, color=ft.Colors.ON_SURFACE_VARIANT))
        secciones.append(ft.Divider(height=8, color=ft.Colors.TRANSPARENT))

    panel = ft.Container(
        visible=False,
        left=0, top=0, right=0, bottom=0,
        bgcolor=ft.Colors.SURFACE,
        padding=ft.Padding.symmetric(horizontal=18, vertical=18),
        content=ft.Column(
            controls=[
                ft.Text("Términos y condiciones", size=18,
                        weight=ft.FontWeight.BOLD, color=ft.Colors.ON_SURFACE),
                ft.Divider(height=8, color=ft.Colors.TRANSPARENT),
                ft.Column(controls=secciones, spacing=2, scroll=ft.ScrollMode.AUTO,
                          expand=True),
                ft.Button(
                    content=ft.Text("Acepto", weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.WHITE),
                    bgcolor=ft.Colors.ORANGE_800,
                    width=260, height=44,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=25)),
                    on_click=aceptar,
                ),
                ft.Button(
                    content=ft.Text("No acepto", weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.WHITE),
                    bgcolor=ft.Colors.GREY_700,
                    width=260, height=44,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=25)),
                    on_click=rechazar,
                ),
            ],
            spacing=8,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )
    return panel