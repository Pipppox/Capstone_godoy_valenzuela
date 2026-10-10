import flet as ft
import flet_map as ftm

from services.geocoding import sesion_tiles_google, API_KEY

# ============================================================
#  ESTILO DEL MAPA
#  "google_oscuro" -> Google Maps con tema oscuro (combina con la app)
#  "google"        -> Google Maps normal (claro)
#  "satelite"      -> Foto satelital Esri + nombres (respaldo, sin key)
#  "calles"        -> Esri World Street Map (respaldo, sin key)
#  Si Google falla (sin internet, API no habilitada), usa "calles".
# ============================================================
ESTILO = "google_oscuro"

SANTIAGO = (-33.45, -70.65)
ZOOM_MAX = 20
ZOOM_MIN = 3
ZOOM_UN_LUGAR = 17   # al mostrar una sola dirección (ej. al elegirla en Vender)
ZOOM_VARIOS = 11     # al mostrar varios lugares o ninguno

ESRI_CALLES = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}"
ESRI_SATELITE = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
ESRI_NOMBRES = "https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}"


def _url_google(oscuro: bool) -> str | None:
    token = sesion_tiles_google(oscuro=oscuro)
    if not token:
        return None
    return (
        "https://tile.googleapis.com/v1/2dtiles/{z}/{x}/{y}"
        f"?session={token}&key={API_KEY}"
    )


def _capas(estilo: str) -> tuple[list[str], str]:
    """Devuelve (urls de capas, texto de atribución) para el estilo pedido."""
    if estilo in ("google", "google_oscuro"):
        url = _url_google(oscuro=(estilo == "google_oscuro"))
        if url:
            return [url], "Google"
        print("[MAPA] No se pudo usar Google, usando Esri como respaldo")
        estilo = "calles"

    if estilo == "satelite":
        return [ESRI_SATELITE, ESRI_NOMBRES], "Esri"

    return [ESRI_CALLES], "Esri"


def _marcador(m: dict, indice: int, etiquetas: bool):
    if etiquetas:
        contenido = ft.Container(
            content=ft.Text(
                chr(65 + indice) if indice < 26 else "·",
                size=11,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.WHITE,
                text_align=ft.TextAlign.CENTER,
            ),
            width=26,
            height=26,
            bgcolor=ft.Colors.ORANGE_800,
            border_radius=13,
            border=ft.Border.all(2, ft.Colors.WHITE),
            alignment=ft.Alignment.CENTER,
            tooltip=m.get("lugar", ""),
        )
    else:
        contenido = ft.Icon(
            ft.Icons.LOCATION_ON,
            color=ft.Colors.ORANGE_800,
            size=36,
            tooltip=m.get("lugar", ""),
        )

    return ftm.Marker(
        content=contenido,
        coordinates=ftm.MapLatitudeLongitude(m["lat"], m["lng"]),
    )


def _atribucion(texto: str, compacta: bool):
    """Créditos propios, pequeños y discretos (reemplaza el 'flutter_map | ...')."""
    return ft.Container(
        right=6,
        bottom=4,
        content=ft.Text(
            texto,
            size=8 if compacta else 9,
            color=ft.Colors.with_opacity(0.7, ft.Colors.WHITE),
            weight=ft.FontWeight.W_500,
        ),
        bgcolor=ft.Colors.with_opacity(0.35, ft.Colors.BLACK),
        border_radius=4,
        padding=ft.Padding.symmetric(horizontal=4, vertical=1),
    )


def crear_mapa(
    marcadores: list[dict] | None = None,
    zoom: float | None = None,
    alto: int = 250,
    etiquetas: bool = False,
    interactivo: bool = True,
    estilo: str | None = None,
):
    """
    marcadores: lista de dicts {"lugar", "lat", "lng"} (formato de obtener_marcadores).
    zoom: fuerza un zoom inicial (si no, se calcula solo).
    etiquetas: True muestra letras A, B, C... en vez del ícono de ubicación.
    interactivo: False = mapa fijo (para vistas previas clickeables).
    estilo: "google_oscuro", "google", "satelite" o "calles" (si no, usa ESTILO).
    Si no hay marcadores, centra en Santiago.
    """
    marcadores = marcadores or []
    urls, atribucion = _capas(estilo or ESTILO)

    if marcadores:
        lat = sum(m["lat"] for m in marcadores) / len(marcadores)
        lng = sum(m["lng"] for m in marcadores) / len(marcadores)
        zoom_final = zoom or (ZOOM_UN_LUGAR if len(marcadores) == 1 else ZOOM_VARIOS)
    else:
        lat, lng = SANTIAGO
        zoom_final = zoom or ZOOM_VARIOS

    mapa = ftm.Map(
        left=0, top=0, right=0, bottom=0,
        initial_center=ftm.MapLatitudeLongitude(lat, lng),
        initial_zoom=zoom_final,
        max_zoom=ZOOM_MAX,
        min_zoom=ZOOM_MIN,
        interaction_configuration=ftm.InteractionConfiguration(
            flags=ftm.InteractionFlag.ALL if interactivo else ftm.InteractionFlag.NONE
        ),
        layers=[
            *[ftm.TileLayer(url_template=url) for url in urls],
            ftm.MarkerLayer(
                markers=[
                    _marcador(m, i, etiquetas) for i, m in enumerate(marcadores)
                ]
            ),
        ],
    )

    return ft.Container(
        height=alto,
        border_radius=12,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        content=ft.Stack(
            controls=[
                mapa,
                _atribucion(atribucion, compacta=not interactivo),
            ],
        ),
    )