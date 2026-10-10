"""Exportar e importar el inventario en Excel (.xlsx) o CSV."""
import csv
import io
import unicodedata
from datetime import datetime

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill

from services import productos

COLUMNAS = ["Código", "Nombre", "Categoría", "Precio", "Stock"]
CAMPOS = {"codigo", "nombre", "categoria", "precio", "stock"}

# Nombres de columna aceptados al importar (sin tildes ni mayúsculas)
_ALIAS = {
    "codigo": "codigo", "cod": "codigo", "sku": "codigo",
    "nombre": "nombre", "descripcion": "nombre", "producto": "nombre",
    "nombre / descripcion": "nombre", "nombre/descripcion": "nombre",
    "categoria": "categoria",
    "precio": "precio", "valor": "precio",
    "stock": "stock", "cantidad": "stock", "unidades": "stock",
}


# ---------- Utilidades ----------
def nombre_archivo(extension: str) -> str:
    return f"inventario_stockin_{datetime.now():%Y-%m-%d}.{extension}"


def _normalizar(texto) -> str:
    texto = str(texto or "").strip().lower()
    texto = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in texto if not unicodedata.combining(c))


def _clave_nombre(nombre) -> str:
    """Para comparar nombres sin importar mayúsculas, tildes ni espacios extra."""
    return " ".join(_normalizar(nombre).split())


def _texto(valor) -> str:
    """Convierte una celda a texto (Excel entrega 1990.0 en vez de 1990)."""
    if valor is None:
        return ""
    if isinstance(valor, float) and valor.is_integer():
        return str(int(valor))
    return str(valor).strip()


# ---------- Exportar ----------
def exportar_excel() -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = "Inventario"
    ws.append(COLUMNAS)

    for celda in ws[1]:
        celda.font = Font(bold=True, color="FFFFFF")
        celda.fill = PatternFill("solid", fgColor="E65100")
        celda.alignment = Alignment(horizontal="center")

    for p in productos.listar():
        ws.append([p["codigo"], p["nombre"], p["categoria"], p["precio"], p["stock"]])

    for (celda,) in ws.iter_rows(min_row=2, min_col=4, max_col=4):
        celda.number_format = '"$"#,##0'

    for letra, ancho in zip("ABCDE", [14, 32, 20, 14, 10]):
        ws.column_dimensions[letra].width = ancho
    ws.freeze_panes = "A2"

    buffer = io.BytesIO()
    wb.save(buffer)
    return buffer.getvalue()


def exportar_csv() -> bytes:
    """CSV con ';' y BOM para que Excel en español lo abra con tildes y columnas bien."""
    buffer = io.StringIO()
    escritor = csv.writer(buffer, delimiter=";")
    escritor.writerow(COLUMNAS)
    for p in productos.listar():
        escritor.writerow([p["codigo"], p["nombre"], p["categoria"], p["precio"], p["stock"]])
    return buffer.getvalue().encode("utf-8-sig")


# ---------- Importar ----------
def _leer_filas(nombre: str, datos: bytes) -> list[list]:
    extension = nombre.lower().rsplit(".", 1)[-1]

    if extension == "xlsx":
        try:
            wb = load_workbook(io.BytesIO(datos), read_only=True, data_only=True)
        except Exception:
            raise ValueError("No se pudo abrir el Excel. ¿Está dañado?")
        return [list(fila) for fila in wb.active.iter_rows(values_only=True)]

    if extension == "csv":
        try:
            texto = datos.decode("utf-8-sig")
        except UnicodeDecodeError:
            texto = datos.decode("latin-1")
        primera = texto.splitlines()[0] if texto else ""
        separador = ";" if primera.count(";") >= primera.count(",") else ","
        return list(csv.reader(io.StringIO(texto), delimiter=separador))

    raise ValueError("Formato no soportado. Usa un archivo .xlsx o .csv.")


def analizar(nombre: str, datos: bytes | None) -> dict:
    """Revisa el archivo SIN guardar nada y clasifica cada fila:
    - nuevos:      código que no existe -> se creará
    - actualizar:  mismo código y mismo nombre -> se actualizan precio, stock, etc.
    - conflictos:  mismo código pero OTRO nombre -> no se importa (protege el producto existente)
    - errores:     datos inválidos o códigos repetidos en el archivo
    """
    if not datos:
        raise ValueError("No se pudo leer el archivo.")

    filas = [
        f for f in _leer_filas(nombre, datos)
        if f and any(_texto(c) for c in f)
    ]
    if len(filas) < 2:
        raise ValueError("El archivo no tiene productos.")

    encabezado = [_ALIAS.get(_normalizar(c)) for c in filas[0]]
    faltan = CAMPOS - set(encabezado)
    if faltan:
        raise ValueError(
            "Faltan columnas: " + ", ".join(sorted(faltan))
            + ". Usa como plantilla un archivo exportado desde StockIN."
        )

    existentes = {p["codigo"]: p for p in productos.listar()}
    vistos: set[str] = set()
    nuevos, actualizar, conflictos, errores = [], [], [], []

    for numero, fila in enumerate(filas[1:], start=2):
        valores = {
            campo: _texto(fila[i]) if i < len(fila) else ""
            for i, campo in enumerate(encabezado) if campo
        }

        try:
            codigo, nombre_p, categoria, precio, stock = productos._validar(
                valores["codigo"], valores["nombre"], valores["categoria"],
                valores["precio"], valores["stock"],
            )
        except ValueError as err:
            errores.append(f"Fila {numero}: {err}")
            continue

        if codigo in vistos:
            errores.append(f"Fila {numero}: el código {codigo} está repetido en el archivo.")
            continue
        vistos.add(codigo)

        producto = {
            "codigo": codigo, "nombre": nombre_p, "categoria": categoria,
            "precio": precio, "stock": stock,
        }
        existente = existentes.get(codigo)

        if existente is None:
            nuevos.append(producto)
        elif _clave_nombre(existente["nombre"]) == _clave_nombre(nombre_p):
            actualizar.append({"id": existente["id"], **producto})
        else:
            conflictos.append(
                f'Fila {numero}: el código {codigo} ya es "{existente["nombre"]}" '
                f'(el archivo dice "{nombre_p}")'
            )

    return {
        "nuevos": nuevos,
        "actualizar": actualizar,
        "conflictos": conflictos,
        "errores": errores,
    }


def aplicar(analisis: dict) -> dict:
    """Guarda los nuevos y las actualizaciones. Los conflictos y errores se omiten."""
    creados = actualizados = 0
    errores: list[str] = []

    for p in analisis["nuevos"]:
        try:
            productos.crear(p["codigo"], p["nombre"], p["categoria"], p["precio"], p["stock"])
            creados += 1
        except ValueError as err:
            errores.append(f'{p["codigo"]}: {err}')

    for p in analisis["actualizar"]:
        try:
            productos.actualizar(
                p["id"], p["codigo"], p["nombre"], p["categoria"], p["precio"], p["stock"],
            )
            actualizados += 1
        except ValueError as err:
            errores.append(f'{p["codigo"]}: {err}')

    return {"creados": creados, "actualizados": actualizados, "errores": errores}


# ============================================================
#  EXPORTAR VENTAS (solo exportar)
# ============================================================
COLUMNAS_VENTAS = [
    "Fecha", "Código", "Producto", "Categoría",
    "Cantidad", "Precio unitario", "Total", "Lugar", "Estado producto",
]


def nombre_archivo_ventas(extension: str) -> str:
    return f"ventas_stockin_{datetime.now():%Y-%m-%d}.{extension}"


def _ventas_usuario() -> list[dict]:
    """Todas las ventas del usuario, incluidas las de productos eliminados."""
    from database.db import conexion

    uid = productos._usuario_id()
    if uid is None:
        return []

    with conexion() as conn:
        filas = conn.execute(
            """SELECT v.fecha, p.codigo, p.nombre, p.categoria,
                      v.cantidad, v.precio_unitario, v.total,
                      COALESCE(v.lugar, '') AS lugar, p.activo
               FROM ventas v
               JOIN productos p ON p.id = v.producto_id
               WHERE v.usuario_id = ?
               ORDER BY v.fecha DESC""",
            (uid,),
        ).fetchall()

    ventas = []
    for f in filas:
        v = dict(f)
        # Los productos eliminados guardan el código como "P01#ELIM5": se muestra "P01"
        v["codigo"] = v["codigo"].split("#ELIM")[0]
        v["estado"] = "Activo" if v["activo"] else "Eliminado"
        ventas.append(v)
    return ventas


def _fecha(texto: str):
    try:
        return datetime.strptime(texto, "%Y-%m-%d %H:%M:%S")
    except (TypeError, ValueError):
        return texto


def exportar_ventas_excel() -> bytes:
    ventas = _ventas_usuario()
    if not ventas:
        raise ValueError("Aún no hay ventas para exportar.")

    wb = Workbook()
    ws = wb.active
    ws.title = "Ventas"
    ws.append(COLUMNAS_VENTAS)

    for celda in ws[1]:
        celda.font = Font(bold=True, color="FFFFFF")
        celda.fill = PatternFill("solid", fgColor="E65100")
        celda.alignment = Alignment(horizontal="center")

    for v in ventas:
        ws.append([
            _fecha(v["fecha"]), v["codigo"], v["nombre"], v["categoria"],
            v["cantidad"], v["precio_unitario"], v["total"], v["lugar"], v["estado"],
        ])

    ultima = ws.max_row
    for fila in ws.iter_rows(min_row=2, max_row=ultima):
        fila[0].number_format = "dd-mm-yyyy hh:mm"
        fila[5].number_format = '"$"#,##0'
        fila[6].number_format = '"$"#,##0'

    # Fila de totales (unidades y monto)
    ws.append([])
    ws.append(["TOTAL", "", "", "", f"=SUM(E2:E{ultima})", "", f"=SUM(G2:G{ultima})"])
    fila_total = ws.max_row
    for celda in ws[fila_total]:
        celda.font = Font(bold=True)
    ws.cell(row=fila_total, column=7).number_format = '"$"#,##0'

    for letra, ancho in zip("ABCDEFGHI", [17, 12, 30, 16, 10, 15, 14, 40, 15]):
        ws.column_dimensions[letra].width = ancho
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:I{ultima}"

    buffer = io.BytesIO()
    wb.save(buffer)
    return buffer.getvalue()


def exportar_ventas_csv() -> bytes:
    ventas = _ventas_usuario()
    if not ventas:
        raise ValueError("Aún no hay ventas para exportar.")

    buffer = io.StringIO()
    escritor = csv.writer(buffer, delimiter=";")
    escritor.writerow(COLUMNAS_VENTAS)
    for v in ventas:
        escritor.writerow([
            v["fecha"], v["codigo"], v["nombre"], v["categoria"],
            v["cantidad"], v["precio_unitario"], v["total"], v["lugar"], v["estado"],
        ])
    return buffer.getvalue().encode("utf-8-sig")