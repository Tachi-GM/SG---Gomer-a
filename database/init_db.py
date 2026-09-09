"""
Script de Inicialización de la Base de Datos para 'Gomería El Puente'.

Crea las tablas con sus restricciones de integridad (PRIMARY KEY, FOREIGN KEY, CHECK, UNIQUE)
e inserta los datos semilla iniciales que coinciden con los bocetos de Canva (remitos 20213 y 20412).
"""

import sys
from pathlib import Path

# Asegurar que se pueda importar connection independientemente de donde se ejecute
sys.path.insert(0, str(Path(__file__).resolve().parent))
from connection import get_db_connection


def crear_tablas():
    """Crea la estructura relacional completa si no existe."""
    ddl_script = """
    -- 1. Empresas / Clientes
    CREATE TABLE IF NOT EXISTS clientes (
        id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
        nom_cli TEXT NOT NULL,
        cuit TEXT UNIQUE,
        tel TEXT,
        mail TEXT
    );

    -- 2. Vehículos de cada empresa
    CREATE TABLE IF NOT EXISTS vehiculos (
        id_vehiculo INTEGER PRIMARY KEY AUTOINCREMENT,
        patente TEXT NOT NULL UNIQUE,
        id_cliente INTEGER NOT NULL,
        FOREIGN KEY (id_cliente) REFERENCES clientes (id_cliente) ON DELETE CASCADE
    );

    -- 3. Catálogo de Tareas y Tarifas (El Tarifario de la Gomería)
    CREATE TABLE IF NOT EXISTS tareas (
        id_tarea INTEGER PRIMARY KEY AUTOINCREMENT,
        nom_tar TEXT NOT NULL UNIQUE,
        precio REAL NOT NULL CHECK (precio >= 0)
    );

    -- 4. Cabecera de Trabajos / Remitos
    CREATE TABLE IF NOT EXISTS trabajos (
        id_trabajo INTEGER PRIMARY KEY AUTOINCREMENT,
        remito TEXT NOT NULL UNIQUE,
        fecha TEXT NOT NULL, -- Formato ISO YYYY-MM-DD
        id_cliente INTEGER NOT NULL,
        id_vehiculo INTEGER,
        total REAL NOT NULL DEFAULT 0 CHECK (total >= 0),
        estado TEXT NOT NULL DEFAULT 'PENDIENTE', -- PENDIENTE, PAGADO
        FOREIGN KEY (id_cliente) REFERENCES clientes (id_cliente) ON DELETE RESTRICT,
        FOREIGN KEY (id_vehiculo) REFERENCES vehiculos (id_vehiculo) ON DELETE SET NULL
    );

    -- 5. Detalle de Tareas realizadas por cada Trabajo (Maestro-Detalle)
    CREATE TABLE IF NOT EXISTS detalle_trabajos (
        id_detalle INTEGER PRIMARY KEY AUTOINCREMENT,
        id_trabajo INTEGER NOT NULL,
        id_tarea INTEGER NOT NULL,
        cantidad INTEGER NOT NULL DEFAULT 1 CHECK (cantidad > 0),
        precio_unitario REAL NOT NULL CHECK (precio_unitario >= 0),
        subtotal REAL NOT NULL CHECK (subtotal >= 0),
        FOREIGN KEY (id_trabajo) REFERENCES trabajos (id_trabajo) ON DELETE CASCADE,
        FOREIGN KEY (id_tarea) REFERENCES tareas (id_tarea) ON DELETE RESTRICT
    );

    -- 6. Pagos recibidos de clientes (Cuenta Corriente)
    CREATE TABLE IF NOT EXISTS pagos (
        id_pago INTEGER PRIMARY KEY AUTOINCREMENT,
        id_cliente INTEGER NOT NULL,
        fecha TEXT NOT NULL, -- Formato ISO YYYY-MM-DD
        monto REAL NOT NULL CHECK (monto > 0),
        metodo_pago TEXT NOT NULL, -- 'Transferencia', 'Efectivo', 'Cheque'
        observaciones TEXT,
        FOREIGN KEY (id_cliente) REFERENCES clientes (id_cliente) ON DELETE RESTRICT
    );
    """
    with get_db_connection() as conn:
        conn.executescript(ddl_script)
    print("[OK] Tablas creadas con exito.")


def sembrar_datos_prueba():
    """Inserta datos de prueba basados en los bocetos de Canva para probar el sistema."""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Verificar si ya existen clientes cargados
        cursor.execute("SELECT COUNT(*) FROM clientes")
        if cursor.fetchone()[0] > 0:
            print("ℹ La base de datos ya contiene registros. No se duplican datos semilla.")
            return

        print("Cargando datos semilla iniciales...")

        # 1. Clientes (Empresas)
        cursor.execute("""
            INSERT INTO clientes (nom_cli, cuit, tel, mail)
            VALUES (?, ?, ?, ?)
        """, ('Toyota', '30-68312345-4', '011-4567-8900', 'flota@toyota.com.ar'))
        id_toyota = cursor.lastrowid

        cursor.execute("""
            INSERT INTO clientes (nom_cli, cuit, tel, mail)
            VALUES (?, ?, ?, ?)
        """, ('Transporte Gomez', '30-71239845-9', '03487-421122', 'taller@gomeztrans.com'))
        id_gomez = cursor.lastrowid

        # 2. Vehículos
        cursor.execute("INSERT INTO vehiculos (patente, id_cliente) VALUES (?, ?)", ('ABC123', id_toyota))
        id_veh_toyota1 = cursor.lastrowid
        cursor.execute("INSERT INTO vehiculos (patente, id_cliente) VALUES (?, ?)", ('AF123JK', id_toyota))
        cursor.execute("INSERT INTO vehiculos (patente, id_cliente) VALUES (?, ?)", ('AE987ZA', id_gomez))

        # 3. Catálogo de Tareas (con los precios del boceto)
        tareas_iniciales = [
            ('Cambio de cubierta', 60000.0),
            ('Pinchadura', 10000.0),
            ('Alineación y balanceo', 35000.0),
            ('Válvula nueva', 5000.0),
            ('Rotación de neumáticos', 15000.0)
        ]
        tareas_dict = {}
        for nom, precio in tareas_iniciales:
            cursor.execute("INSERT INTO tareas (nom_tar, precio) VALUES (?, ?)", (nom, precio))
            tareas_dict[nom] = (cursor.lastrowid, precio)

        # 4. Trabajos (Exactamente los del boceto 2.png)
        # Trabajo 1: 20/08 - Remito 20213 - Cambio de cubierta - $60.000
        cursor.execute("""
            INSERT INTO trabajos (remito, fecha, id_cliente, id_vehiculo, total, estado)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ('20213', '2026-08-20', id_toyota, id_veh_toyota1, 60000.0, 'PENDIENTE'))
        id_trabajo1 = cursor.lastrowid

        id_tar_cubierta, precio_cubierta = tareas_dict['Cambio de cubierta']
        cursor.execute("""
            INSERT INTO detalle_trabajos (id_trabajo, id_tarea, cantidad, precio_unitario, subtotal)
            VALUES (?, ?, ?, ?, ?)
        """, (id_trabajo1, id_tar_cubierta, 1, precio_cubierta, 60000.0))

        # Trabajo 2: 21/08 - Remito 20412 - Pinchadura x2 - $20.000
        cursor.execute("""
            INSERT INTO trabajos (remito, fecha, id_cliente, id_vehiculo, total, estado)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ('20412', '2026-08-21', id_toyota, id_veh_toyota1, 20000.0, 'PENDIENTE'))
        id_trabajo2 = cursor.lastrowid

        id_tar_pincha, precio_pincha = tareas_dict['Pinchadura']
        cursor.execute("""
            INSERT INTO detalle_trabajos (id_trabajo, id_tarea, cantidad, precio_unitario, subtotal)
            VALUES (?, ?, ?, ?, ?)
        """, (id_trabajo2, id_tar_pincha, 2, precio_pincha, 20000.0))

        print("[OK] Datos semilla cargados con exito.")
        print("  - 2 Empresas: 'Toyota' y 'Transporte Gomez'")
        print("  - 5 Tareas de catalogo")
        print("  - 2 Trabajos para 'Toyota' en Agosto (Remitos 20213 y 20412, Total: $80.000)")


if __name__ == '__main__':
    print("=== Inicializando Base de Datos 'Gomeria El Puente' ===")
    crear_tablas()
    sembrar_datos_prueba()
    print("=== Listo para operar ===")
