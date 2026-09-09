import sqlite3

def obtener_conexion():
    conexion = sqlite3.connect("sg_gomeria.db")
    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA foreign_keys = ON")
    return conexion

# 1. Función para agregar empresa (devuelve el id_cliente generado)
def agregar_cliente(nombre, cuit, tel, mail):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    try:
        cursor.execute("""
            INSERT INTO clientes (nom_cli, cuit, tel, mail)
            VALUES (?, ?, ?, ?)
        """, (nombre, cuit, tel, mail))
        conexion.commit()
        nuevo_id = cursor.lastrowid  # Obtenemos el ID autoincremental
        print(f"[OK] Cliente '{nombre}' guardado con ID: {nuevo_id}")
        return nuevo_id
    except sqlite3.IntegrityError:
        print(f"[AVISO] Ya existe un cliente con el CUIT '{cuit}'.")
        return None
    finally:
        conexion.close()

# 2. Función para asociar un vehículo a una empresa
def agregar_vehiculo(patente, id_cliente):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    try:
        cursor.execute("""
            INSERT INTO vehiculos (patente, id_cliente)
            VALUES (?, ?)
        """, (patente.upper(), id_cliente)) # Guardamos la patente en mayúsculas
        conexion.commit()
        print(f"[OK] Vehículo '{patente.upper()}' asociado al cliente ID: {id_cliente}")
    except sqlite3.IntegrityError as e:
        print(f"[ERROR] No se pudo agregar vehículo: la patente ya existe o el cliente no es válido.")
    finally:
        conexion.close()

# 3. Función para listar todos los vehículos de una empresa específica
def obtener_vehiculos_de_cliente(id_cliente):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM vehiculos WHERE id_cliente = ?", (id_cliente,))
    vehiculos = cursor.fetchall()
    conexion.close()
    return vehiculos


# ========================================================
# ZONA DE PRUEBAS
# ========================================================

print("--- 1. Registrando empresas de prueba ---")
id_toyota = agregar_cliente("Toyota Argentina", "30-68312345-4", "011-4567-8900", "flota@toyota.com")
id_transporte = agregar_cliente("Transporte Gomez", "30-71239845-9", "03487-421122", "taller@gomez.com")

print("\n--- 2. Asignando vehículos a las empresas ---")
if id_toyota:
    agregar_vehiculo("ABC123", id_toyota)
    agregar_vehiculo("AF123JK", id_toyota)

if id_transporte:
    agregar_vehiculo("AE987ZA", id_transporte)

print("\n--- 3. Consultando la flota de Toyota ---")
if id_toyota:
    flota = obtener_vehiculos_de_cliente(id_toyota)
    print(f"Vehículos de Toyota (Cliente #{id_toyota}):")
    for v in flota:
        print(f" -> Patente: {v['patente']}")