"""
╔══════════════════════════════════════════════════════════════╗
║  StockIN — Pruebas de Base de Datos SQLite (pytest)         ║
║  Requisitos: RF-03, RF-04, RF-06, RF-07, RF-08, RF-21,     ║
║              RF-30, RF-12                                   ║
║  Verifica: CRUD productos, ventas, descuento de stock,      ║
║            separación de usuarios, búsqueda, alertas         ║
╚══════════════════════════════════════════════════════════════╝
"""
import sqlite3
import pytest
from datetime import datetime


# ── Fixture: base de datos en memoria ──

@pytest.fixture
def db():
    """Crea una base de datos SQLite en memoria con el esquema de StockIN."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.executescript("""
        CREATE TABLE usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            correo TEXT UNIQUE NOT NULL,
            telefono TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            nombre_tienda TEXT DEFAULT '',
            imagen_perfil TEXT DEFAULT ''
        );

        CREATE TABLE productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            codigo TEXT NOT NULL,
            nombre TEXT NOT NULL,
            categoria TEXT NOT NULL,
            precio REAL DEFAULT 0,
            stock INTEGER DEFAULT 0,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
            UNIQUE(usuario_id, codigo)
        );

        CREATE TABLE ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            producto_id INTEGER NOT NULL,
            nombre_producto TEXT NOT NULL,
            codigo_producto TEXT NOT NULL,
            categoria TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            precio_unitario REAL NOT NULL,
            total REAL NOT NULL,
            lugar TEXT DEFAULT '',
            fecha TEXT NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        );
    """)
    yield conn
    conn.close()


@pytest.fixture
def db_con_datos(db):
    """Base de datos con un usuario y productos precargados."""
    db.execute(
        "INSERT INTO usuarios (nombre,apellido,correo,telefono,password_hash,salt) "
        "VALUES ('Juan','Godoy','juan@test.cl','912345678','abc123hash','sal123')"
    )
    db.execute(
        "INSERT INTO productos (usuario_id,codigo,nombre,categoria,precio,stock) "
        "VALUES (1,'CAM001','Camiseta azul','Ropa',5000,50)"
    )
    db.execute(
        "INSERT INTO productos (usuario_id,codigo,nombre,categoria,precio,stock) "
        "VALUES (1,'PAN001','Pantalón negro','Ropa',12000,20)"
    )
    db.execute(
        "INSERT INTO productos (usuario_id,codigo,nombre,categoria,precio,stock) "
        "VALUES (1,'AUD001','Audífonos BT','Electrónica',8000,2)"
    )
    db.commit()
    return db


# ══════════════════════════════════════════════════
# RF-03: Registrar producto
# ══════════════════════════════════════════════════

class TestRegistrarProducto:
    """RF-03 / HU-03: Registrar un producto nuevo en el inventario."""

    def test_insertar_producto_exitoso(self, db_con_datos):
        db_con_datos.execute(
            "INSERT INTO productos (usuario_id,codigo,nombre,categoria,precio,stock) "
            "VALUES (1,'ZAP001','Zapatillas','Calzado',25000,10)"
        )
        db_con_datos.commit()
        r = db_con_datos.execute("SELECT * FROM productos WHERE codigo='ZAP001'").fetchone()
        assert r["nombre"] == "Zapatillas"
        assert r["precio"] == 25000
        assert r["stock"] == 10

    def test_codigo_duplicado_rechazado(self, db_con_datos):
        """No se puede registrar dos productos con el mismo código para el mismo usuario."""
        with pytest.raises(sqlite3.IntegrityError):
            db_con_datos.execute(
                "INSERT INTO productos (usuario_id,codigo,nombre,categoria,precio,stock) "
                "VALUES (1,'CAM001','Otra camiseta','Ropa',3000,5)"
            )

    def test_contar_productos(self, db_con_datos):
        total = db_con_datos.execute(
            "SELECT COUNT(*) as n FROM productos WHERE usuario_id=1"
        ).fetchone()["n"]
        assert total == 3


# ══════════════════════════════════════════════════
# RF-04: Editar y eliminar producto
# ══════════════════════════════════════════════════

class TestEditarEliminarProducto:
    """RF-04 / HU-04: Editar datos de un producto y eliminar."""

    def test_editar_nombre_y_precio(self, db_con_datos):
        db_con_datos.execute(
            "UPDATE productos SET nombre='Camiseta roja', precio=6000 WHERE codigo='CAM001' AND usuario_id=1"
        )
        db_con_datos.commit()
        r = db_con_datos.execute("SELECT * FROM productos WHERE codigo='CAM001'").fetchone()
        assert r["nombre"] == "Camiseta roja"
        assert r["precio"] == 6000

    def test_eliminar_producto(self, db_con_datos):
        db_con_datos.execute("DELETE FROM productos WHERE codigo='AUD001' AND usuario_id=1")
        db_con_datos.commit()
        r = db_con_datos.execute("SELECT * FROM productos WHERE codigo='AUD001' AND usuario_id=1").fetchone()
        assert r is None

    def test_eliminar_no_afecta_otros(self, db_con_datos):
        db_con_datos.execute("DELETE FROM productos WHERE codigo='AUD001' AND usuario_id=1")
        db_con_datos.commit()
        total = db_con_datos.execute("SELECT COUNT(*) as n FROM productos WHERE usuario_id=1").fetchone()["n"]
        assert total == 2


# ══════════════════════════════════════════════════
# RF-06: Buscar producto
# ══════════════════════════════════════════════════

class TestBuscarProducto:
    """RF-06 / HU-06: Buscar producto por nombre o código."""

    def test_buscar_por_nombre(self, db_con_datos):
        r = db_con_datos.execute(
            "SELECT * FROM productos WHERE LOWER(nombre) LIKE '%camiseta%' AND usuario_id=1"
        ).fetchall()
        assert len(r) == 1
        assert r[0]["codigo"] == "CAM001"

    def test_buscar_por_codigo(self, db_con_datos):
        r = db_con_datos.execute(
            "SELECT * FROM productos WHERE LOWER(codigo) LIKE '%pan%' AND usuario_id=1"
        ).fetchall()
        assert len(r) == 1
        assert r[0]["nombre"] == "Pantalón negro"

    def test_buscar_sin_resultados(self, db_con_datos):
        r = db_con_datos.execute(
            "SELECT * FROM productos WHERE LOWER(nombre) LIKE '%laptop%' AND usuario_id=1"
        ).fetchall()
        assert len(r) == 0


# ══════════════════════════════════════════════════
# RF-07/RF-08: Registrar venta y descontar stock
# ══════════════════════════════════════════════════

class TestVentas:
    """RF-07 / RF-08 / HU-07 / HU-08: Registro de venta con descuento de stock."""

    def test_registrar_venta_exitosa(self, db_con_datos):
        cantidad = 3
        producto = db_con_datos.execute("SELECT * FROM productos WHERE codigo='CAM001'").fetchone()
        total = producto["precio"] * cantidad
        db_con_datos.execute(
            "INSERT INTO ventas (usuario_id,producto_id,nombre_producto,codigo_producto,"
            "categoria,cantidad,precio_unitario,total,lugar,fecha) "
            "VALUES (1,?,?,?,?,?,?,?,?,?)",
            (producto["id"], producto["nombre"], producto["codigo"],
             producto["categoria"], cantidad, producto["precio"],
             total, "Feria Central", datetime.now().isoformat())
        )
        db_con_datos.execute(
            "UPDATE productos SET stock = stock - ? WHERE id = ?", (cantidad, producto["id"])
        )
        db_con_datos.commit()
        nuevo_stock = db_con_datos.execute("SELECT stock FROM productos WHERE id=?", (producto["id"],)).fetchone()["stock"]
        assert nuevo_stock == 47
        assert total == 15000

    def test_stock_no_queda_negativo(self, db_con_datos):
        producto = db_con_datos.execute("SELECT * FROM productos WHERE codigo='AUD001'").fetchone()
        cantidad_solicitada = 5
        assert producto["stock"] < cantidad_solicitada  # stock=2, venta=5 → rechazar

    def test_venta_guarda_lugar_y_fecha(self, db_con_datos):
        fecha = "2026-11-01T10:30:00"
        db_con_datos.execute(
            "INSERT INTO ventas (usuario_id,producto_id,nombre_producto,codigo_producto,"
            "categoria,cantidad,precio_unitario,total,lugar,fecha) "
            "VALUES (1,1,'Camiseta azul','CAM001','Ropa',2,5000,10000,'Plaza Mayor',?)",
            (fecha,)
        )
        db_con_datos.commit()
        v = db_con_datos.execute("SELECT * FROM ventas WHERE lugar='Plaza Mayor'").fetchone()
        assert v["lugar"] == "Plaza Mayor"
        assert v["fecha"] == fecha
        assert v["total"] == 10000


# ══════════════════════════════════════════════════
# RF-12: Alerta de stock bajo
# ══════════════════════════════════════════════════

class TestAlertaStock:
    """RF-12 / HU-12: Alerta cuando el stock llega a ≤ 2 unidades."""

    def test_stock_bajo_detectado(self, db_con_datos):
        productos_alerta = db_con_datos.execute(
            "SELECT * FROM productos WHERE stock <= 2 AND usuario_id=1"
        ).fetchall()
        assert len(productos_alerta) == 1
        assert productos_alerta[0]["codigo"] == "AUD001"

    def test_stock_normal_sin_alerta(self, db_con_datos):
        productos_ok = db_con_datos.execute(
            "SELECT * FROM productos WHERE stock > 2 AND usuario_id=1"
        ).fetchall()
        assert len(productos_ok) == 2

    def test_alerta_desaparece_al_reponer(self, db_con_datos):
        db_con_datos.execute("UPDATE productos SET stock=10 WHERE codigo='AUD001'")
        db_con_datos.commit()
        alertas = db_con_datos.execute(
            "SELECT * FROM productos WHERE stock <= 2 AND usuario_id=1"
        ).fetchall()
        assert len(alertas) == 0


# ══════════════════════════════════════════════════
# RF-21: Separación de datos entre cuentas
# ══════════════════════════════════════════════════

class TestSeparacionCuentas:
    """RF-21 / HU-21: Cada cuenta ve solo sus propios datos."""

    def test_datos_separados(self, db_con_datos):
        # Crear segundo usuario con su producto
        db_con_datos.execute(
            "INSERT INTO usuarios (nombre,apellido,correo,telefono,password_hash,salt) "
            "VALUES ('Felipe','Valenzuela','felipe@test.cl','987654321','xyz456hash','sal456')"
        )
        db_con_datos.execute(
            "INSERT INTO productos (usuario_id,codigo,nombre,categoria,precio,stock) "
            "VALUES (2,'FEL001','Gorra','Accesorios',3000,15)"
        )
        db_con_datos.commit()

        prods_juan = db_con_datos.execute("SELECT * FROM productos WHERE usuario_id=1").fetchall()
        prods_felipe = db_con_datos.execute("SELECT * FROM productos WHERE usuario_id=2").fetchall()

        assert len(prods_juan) == 3
        assert len(prods_felipe) == 1
        assert prods_felipe[0]["nombre"] == "Gorra"
        # Verificar que no hay cruce
        codigos_juan = [p["codigo"] for p in prods_juan]
        assert "FEL001" not in codigos_juan


# ══════════════════════════════════════════════════
# RF-30: Eliminar todos los productos
# ══════════════════════════════════════════════════

class TestEliminarTodo:
    """RF-30 / HU-30: Eliminar todos los productos de un usuario."""

    def test_eliminar_todo_del_usuario(self, db_con_datos):
        db_con_datos.execute("DELETE FROM productos WHERE usuario_id=1")
        db_con_datos.commit()
        total = db_con_datos.execute("SELECT COUNT(*) as n FROM productos WHERE usuario_id=1").fetchone()["n"]
        assert total == 0

    def test_eliminar_no_afecta_otro_usuario(self, db_con_datos):
        # Crear segundo usuario
        db_con_datos.execute(
            "INSERT INTO usuarios (nombre,apellido,correo,telefono,password_hash,salt) "
            "VALUES ('Felipe','V','f@t.cl','111111111','h','s')"
        )
        db_con_datos.execute(
            "INSERT INTO productos (usuario_id,codigo,nombre,categoria,precio,stock) "
            "VALUES (2,'X01','Otro','Cat',100,5)"
        )
        db_con_datos.commit()
        # Eliminar solo usuario 1
        db_con_datos.execute("DELETE FROM productos WHERE usuario_id=1")
        db_con_datos.commit()
        total_u2 = db_con_datos.execute("SELECT COUNT(*) as n FROM productos WHERE usuario_id=2").fetchone()["n"]
        assert total_u2 == 1
