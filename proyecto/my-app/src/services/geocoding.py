import os
import json
import urllib.request
import urllib.parse
from pathlib import Path

from dotenv import load_dotenv

from database.db import conexion

load_dotenv()

API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")
BASE_URL = "https://maps.googleapis.com/maps/api/geocode/json"


def geocodificar(direccion: str) -> dict | None:
    if not API_KEY:
        print("[GEO] No hay API key configurada")
        return None

    if not direccion:
        return None

    query = f"{direccion}, Chile"
    params = urllib.parse.urlencode({"address": query, "key": API_KEY})
    url = f"{BASE_URL}?{params}"

    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            data = json.loads(resp.read().decode())
    except Exception as e:
        print(f"[GEO] Error de conexion: {e}")
        return None

    if data.get("status") != "OK" or not data.get("results"):
        print(f"[GEO] No se encontro '{direccion}': {data.get('status')}")
        return None

    resultado = data["results"][0]
    location = resultado["geometry"]["location"]
    return {
        "lat": location["lat"],
        "lng": location["lng"],
        "direccion_formateada": resultado.get("formatted_address", direccion),
    }


def geocodificar_y_guardar(lugar: str) -> dict | None:
    if not lugar:
        return None

    lugar_normalizado = lugar.strip().title()

    with conexion() as conn:
        existente = conn.execute(
            "SELECT lugar, lat, lng FROM lugares_cache WHERE lugar = ?",
            (lugar_normalizado,),
        ).fetchone()

        if existente:
            return {"lat": existente["lat"], "lng": existente["lng"], "lugar": existente["lugar"]}

    coords = geocodificar(lugar_normalizado)
    if coords is None:
        return None

    # Usar la dirección formateada de Google como nombre del lugar
    nombre_lugar = coords.get("direccion_formateada", lugar_normalizado)
    # Limpiar el ", Chile" del final si viene
    if nombre_lugar.endswith(", Chile"):
        nombre_lugar = nombre_lugar[:-7]

    with conexion() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO lugares_cache (lugar, lat, lng) VALUES (?, ?, ?)",
            (nombre_lugar, coords["lat"], coords["lng"]),
        )

    return {"lat": coords["lat"], "lng": coords["lng"], "lugar": nombre_lugar}

def obtener_marcadores(usuario_id: int = None) -> list[dict]:
    """Devuelve los lugares donde vendió el usuario, con coordenadas."""
    with conexion() as conn:
        if usuario_id:
            # Obtener lugares distintos de las ventas del usuario
            lugares_usuario = conn.execute(
                """SELECT DISTINCT lugar FROM ventas
                   WHERE usuario_id = ? AND lugar IS NOT NULL AND lugar != ''""",
                (usuario_id,),
            ).fetchall()

            marcadores = []
            for lv in lugares_usuario:
                nombre = lv["lugar"]
                # Buscar en cache con coincidencia flexible
                cache = conn.execute(
                    "SELECT lugar, lat, lng FROM lugares_cache WHERE LOWER(lugar) LIKE '%' || LOWER(?) || '%' OR LOWER(?) LIKE '%' || LOWER(lugar) || '%'",
                    (nombre, nombre),
                ).fetchone()

                if cache:
                    marcadores.append({"lugar": nombre, "lat": cache["lat"], "lng": cache["lng"]})

            return marcadores
        else:
            return []


def generar_url_mapa(ancho=600, alto=400, zoom=13, marcadores=None) -> str | None:
    if not API_KEY:
        return None

    # Estilo oscuro completo
    estilos = [
        "feature:all|element:geometry|color:0x242f3e",
        "feature:all|element:labels.text.stroke|color:0x242f3e",
        "feature:all|element:labels.text.fill|color:0x746855",
        "feature:road|element:geometry|color:0x38414e",
        "feature:road|element:geometry.stroke|color:0x212a37",
        "feature:water|element:geometry|color:0x17263c",
        "feature:poi|element:labels|visibility:off",
    ]

    params = [
        ("size", f"{ancho}x{alto}"),
        ("scale", "2"),
        ("maptype", "roadmap"),
        ("key", API_KEY),
    ]

    for estilo in estilos:
        params.append(("style", estilo))

    if marcadores:
        # Calcular centro y zoom apropiado
        lats = [m["lat"] for m in marcadores]
        lngs = [m["lng"] for m in marcadores]
        centro_lat = sum(lats) / len(lats)
        centro_lng = sum(lngs) / len(lngs)

        # Marcadores con etiqueta
        for i, m in enumerate(marcadores):
            label = chr(65 + i) if i < 26 else ""
            params.append(("markers", f"color:red|label:{label}|{m['lat']},{m['lng']}"))

        # Si los marcadores están muy separados, dejar que Google ajuste el zoom
        lat_diff = max(lats) - min(lats)
        lng_diff = max(lngs) - min(lngs)

        if lat_diff < 0.05 and lng_diff < 0.05:
            params.append(("center", f"{centro_lat},{centro_lng}"))
            params.append(("zoom", "14"))
        # Si no, Google ajusta automáticamente al no pasar center ni zoom
    else:
        params.append(("center", "-33.45,-70.65"))
        params.append(("zoom", str(zoom)))

    return f"https://maps.googleapis.com/maps/api/staticmap?{urllib.parse.urlencode(params)}"


def generar_url_google_maps(marcadores: list[dict]) -> str:
    """Genera una URL de Google Maps web para abrir en el navegador."""
    if not marcadores:
        return "https://www.google.com/maps/@-33.45,-70.65,13z"

    if len(marcadores) == 1:
        m = marcadores[0]
        nombre = urllib.parse.quote(m["lugar"])
        return f"https://www.google.com/maps/search/?api=1&query={m['lat']},{m['lng']}&query_place_id={nombre}"

    # Múltiples marcadores: crear una ruta para que se vean todos
    puntos = [f"{m['lat']},{m['lng']}" for m in marcadores]
    origen = puntos[0]
    destino = puntos[-1]
    waypoints = "/".join(puntos[1:-1]) if len(puntos) > 2 else ""

    if waypoints:
        return f"https://www.google.com/maps/dir/{origen}/{waypoints}/{destino}"
    else:
        return f"https://www.google.com/maps/dir/{origen}/{destino}"

AUTOCOMPLETE_URL_NEW = "https://places.googleapis.com/v1/places:autocomplete"
PLACE_DETAILS_URL_NEW = "https://places.googleapis.com/v1/places"


def autocompletar(texto: str) -> list[dict]:
    if not API_KEY or not texto or len(texto) < 3:
        return []

    body = json.dumps({
        "input": texto,
        "includedRegionCodes": ["cl"],
        "languageCode": "es",
    }).encode("utf-8")

    req = urllib.request.Request(
        AUTOCOMPLETE_URL_NEW,
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-Goog-Api-Key": API_KEY,
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
    except Exception as e:
        print(f"[GEO] Error autocompletado: {e}")
        return []

    return [
        {
            "descripcion": s.get("placePrediction", {}).get("text", {}).get("text", ""),
            "place_id": s.get("placePrediction", {}).get("placeId", ""),
        }
        for s in data.get("suggestions", [])
        if s.get("placePrediction")
    ]

def obtener_coordenadas_place(place_id: str) -> dict | None:
    if not API_KEY or not place_id:
        return None

    url = f"{PLACE_DETAILS_URL_NEW}/{place_id}"
    req = urllib.request.Request(
        url,
        headers={
            "X-Goog-Api-Key": API_KEY,
            "X-Goog-FieldMask": "location,formattedAddress",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
    except Exception as e:
        print(f"[GEO] Error place details: {e}")
        return None

    location = data.get("location", {})
    direccion = data.get("formattedAddress", "")

    if not location:
        return None

    if direccion.endswith(", Chile"):
        direccion = direccion[:-7]

    return {
        "lat": location.get("latitude"),
        "lng": location.get("longitude"),
        "direccion_formateada": direccion,
    }


def guardar_lugar_desde_place(place_id: str, nombre: str) -> dict | None:
    """Geocodifica con place_id y guarda en cache."""
    coords = obtener_coordenadas_place(place_id)
    if coords is None:
        return None

    lugar_nombre = coords.get("direccion_formateada", nombre)

    with conexion() as conn:
        existente = conn.execute(
            "SELECT lugar, lat, lng FROM lugares_cache WHERE lugar = ?",
            (lugar_nombre,),
        ).fetchone()

        if existente:
            return {"lat": existente["lat"], "lng": existente["lng"], "lugar": existente["lugar"]}

        conn.execute(
            "INSERT OR IGNORE INTO lugares_cache (lugar, lat, lng) VALUES (?, ?, ?)",
            (lugar_nombre, coords["lat"], coords["lng"]),
        )

    return {"lat": coords["lat"], "lng": coords["lng"], "lugar": lugar_nombre}