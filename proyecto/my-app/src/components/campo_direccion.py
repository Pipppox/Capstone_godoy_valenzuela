import flet as ft

from services import geocoding
from components.mapa import crear_mapa


class CampoDireccion(ft.Column):
    """Campo de texto con autocompletado de Google Places + mapa dinámico."""

    def __init__(self, label="Lugar de venta", mostrar_mapa=True, alto_mapa=180):
        super().__init__(spacing=8)
        self.token = geocoding.nuevo_token()
        self.lugar = None  # dict {"lugar", "lat", "lng"} cuando se elige una sugerencia
        self.alto_mapa = alto_mapa

        self.campo = ft.TextField(
            label=label,
            hint_text="Buscar lugar...",
            border_color=ft.Colors.GREY_700,
            color=ft.Colors.WHITE,
            on_change=self._buscar,
        )

        self.lista = ft.Column(spacing=2)
        self.contenedor_sugerencias = ft.Container(
            content=self.lista,
            bgcolor=ft.Colors.GREY_800,
            border_radius=10,
            padding=4,
            visible=False,
        )

        self.contenedor_mapa = ft.Container(
            content=crear_mapa(alto=alto_mapa),
            visible=mostrar_mapa,
        )

        self.controls = [self.campo, self.contenedor_sugerencias, self.contenedor_mapa]

    def texto(self) -> str:
        """Lugar elegido de las sugerencias, o el texto escrito a mano."""
        if self.lugar:
            return self.lugar["lugar"]
        return (self.campo.value or "").strip()

    def _buscar(self, e):
        self.lugar = None  # si vuelve a escribir, se descarta la selección anterior
        texto = self.campo.value or ""

        if len(texto.strip()) < 3:
            self.contenedor_sugerencias.visible = False
            self.update()
            return

        resultados = geocoding.autocompletar(texto, self.token)

        self.lista.controls = [
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.LOCATION_ON, color=ft.Colors.RED_400, size=16),
                        ft.Text(
                            r["descripcion"], size=12, color=ft.Colors.WHITE,
                            expand=True, max_lines=2,
                        ),
                    ],
                    spacing=8,
                ),
                padding=ft.Padding.symmetric(horizontal=10, vertical=8),
                border_radius=8,
                ink=True,
                on_click=lambda e, r=r: self._elegir(r),
            )
            for r in resultados
        ]
        self.contenedor_sugerencias.visible = bool(resultados)
        self.update()

    def _elegir(self, r: dict):
        info = geocoding.guardar_lugar_desde_place(r["place_id"], r["descripcion"], self.token)
        self.token = geocoding.nuevo_token()  # se cierra la sesión de búsqueda
        if not info:
            return

        self.lugar = info
        self.campo.value = info["lugar"]
        self.contenedor_sugerencias.visible = False
        self.contenedor_mapa.content = crear_mapa([info], alto=self.alto_mapa)
        self.update()

    def limpiar(self):
        self.lugar = None
        self.token = geocoding.nuevo_token()
        self.campo.value = ""
        self.contenedor_sugerencias.visible = False
        self.contenedor_mapa.content = crear_mapa(alto=self.alto_mapa)
        self.update()