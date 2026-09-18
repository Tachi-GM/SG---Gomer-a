from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from datetime import date

app = Flask(__name__)
app.secret_key = "modo-milagritos-activo"  # necesario para usar session

def obtener_conexion():
    conexion = sqlite3.connect("sg_gomeria.db")
    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA foreign_keys = ON")
    return conexion

def modo_activo():
    # Devuelve True/False según si Milagritos está prendido
    return session.get('modo_milagritos', False)

# Ruta para prender/apagar el modo, y volver a donde estabas
@app.route('/toggle-milagritos')
def toggle_milagritos():
    session['modo_milagritos'] = not session.get('modo_milagritos', False)
    # request.referrer = la página desde la que vino el usuario
    return redirect(request.referrer or url_for('home'))

# Pantalla de inicio (Botones Mataburros / Clientes)
@app.route('/')
def home():
    return render_template('index.html', milagritos=modo_activo())

# Pantalla de Gestión de Clientes y Dashboard General
@app.route('/clientes')
def clientes():
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    
    empresas = cursor.execute("""
        SELECT id_cliente, nom_cli, cuit, tel, mail 
        FROM clientes 
        ORDER BY nom_cli
    """).fetchall()
    
    remitos = cursor.execute("""
        SELECT t.id_trabajo, t.remito, t.fecha, c.nom_cli, t.total, t.estado
        FROM trabajos t
        JOIN clientes c ON t.id_cliente = c.id_cliente
        ORDER BY t.fecha DESC, t.id_trabajo DESC
    """).fetchall()
    
    conexion.close()
    return render_template('clientes.html', empresas=empresas, remitos=remitos, milagritos=modo_activo())

# Pantalla del Formulario Mataburros
@app.route('/mataburros')
def mataburros():
    conexion = obtener_conexion()
    
    empresas = conexion.execute("SELECT id_cliente, nom_cli, cuit FROM clientes").fetchall()
    tareas = conexion.execute("SELECT id_tarea, nom_tar, precio, precio2, precio3 FROM tareas").fetchall()
    
    conexion.close()
    return render_template('mataburros.html', empresas=empresas, tareas=tareas, milagritos=modo_activo())

@app.route('/precios')
def precios():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    tareas = cursor.execute("SELECT nom_tar, precio, precio2, precio3 FROM tareas").fetchall()
    
    conexion.close()
    return render_template('precios.html', tareas=tareas , milagritos=modo_activo())

@app.route('/historial-cliente')
def historial_cliente():
    id_cliente = request.args.get('id_cliente')
    periodo_seleccionado = request.args.get('periodo', 'todos')

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cliente = cursor.execute("SELECT id_cliente, nom_cli, cuit FROM clientes WHERE id_cliente = ?", (id_cliente,)).fetchone()
    # 1. Armamos la consulta base y la lista de parámetros
    query = """
        SELECT t.id_trabajo, t.remito, t.fecha, t.total,
               GROUP_CONCAT(tar.nom_tar, ', ') AS detalle_tareas
        FROM trabajos t
        LEFT JOIN detalle_trabajos dt ON t.id_trabajo = dt.id_trabajo
        LEFT JOIN tareas tar ON dt.id_tarea = tar.id_tarea
        WHERE t.id_cliente = ?
    """
    parametros = [id_cliente]

    # Buscamos qué meses/años tienen trabajos para crear las pestañas
    meses_disponibles = cursor.execute("""
        SELECT DISTINCT strftime('%Y-%m', fecha) AS periodo
        FROM trabajos
        WHERE id_cliente = ?
        ORDER BY periodo DESC
    """, (id_cliente,)).fetchall()

    # 2. Si eligió un mes específico (y no "todos"), le sumamos la condición:
    if periodo_seleccionado and periodo_seleccionado != 'todos':
        query += " AND strftime('%Y-%m', t.fecha) = ?"
        parametros.append(periodo_seleccionado)

    # 3. Le agregamos el cierre obligatorio (agrupar y ordenar por fecha)
    query += " GROUP BY t.id_trabajo ORDER BY t.fecha DESC"

    # 4. Ejecutamos la consulta con sus parámetros
    remitos = cursor.execute(query, parametros).fetchall()

    # 5. Obtenemos el total y el total por mes
    total_mes = sum(r['total'] for r in remitos)
    cursor.close()
    return render_template('historial-cliente.html',
                        cliente=cliente,
                        remitos=remitos, 
                        total_mes=total_mes,
                        meses_disponibles=meses_disponibles,
                        periodo_seleccionado=periodo_seleccionado)


@app.route('/enviar-trabajo', methods=['POST'])
def enviar_trabajo():
    # 1. Capturamos los datos del formulario
    remito = request.form.get('remito')
    id_cliente = request.form.get('empresa')
    tipo_lista = request.form.get('tipo_lista', '1')  # 1, 2 o 3

    columnas_precio = {'1': 'precio', '2': 'precio2', '3': 'precio3'}
    columna_elegida = columnas_precio.get(tipo_lista, 'precio')  # Por defecto, 'precio'

    # Capturamos todas las tareas y cantidades que agregó el usuario con getlist
    tareas_elegidas = request.form.getlist('tareas')
    cantidades = request.form.getlist('cantidades')
    
    # Filtramos por si alguna quedó sin seleccionar
    ids_tareas = [int(t) for t in tareas_elegidas if t]
    
    if not ids_tareas:
        return "Error: Debes seleccionar al menos una tarea", 400

    fecha_hoy = date.today().strftime("%Y-%m-%d") # Fecha en formato YYYY-MM-DD
    
    # 2. Conectamos a SQLite
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    
    try:
        # A. EL MATABURROS: Buscamos el precio real de cada tarea y calculamos el total
        total_trabajo = 0.0
        detalles_a_guardar = [] # Guardará tuplas: (id_tarea, precio)
        
        for id_t, cant in zip(ids_tareas, cantidades):
            cantidad = int(cant) if cant else 1
            cursor.execute(f"SELECT nom_tar, {columna_elegida} AS precio_final FROM tareas WHERE id_tarea = ?", (id_t,))
            fila = cursor.fetchone()
            if fila:
                precio = fila['precio_final'] or 0.0 #Por si no tiene precio, lo ponemos en 0
                subtotal = precio * cantidad
                total_trabajo += subtotal
                detalles_a_guardar.append((id_t, cantidad, precio, subtotal))
        
        # B. GUARDAR CABECERA en 'trabajos'
        cursor.execute("""
            INSERT INTO trabajos (remito, fecha, id_cliente, total, estado)
            VALUES (?, ?, ?, ?, 'PENDIENTE')
        """, (remito, fecha_hoy, id_cliente, total_trabajo))
        
        # Obtenemos el id del trabajo recién insertado
        id_trabajo = cursor.lastrowid
        
        # C. GUARDAR RENGLONES en 'detalle_trabajos'
        for id_t, cant, p_unit, sub in detalles_a_guardar:
            cursor.execute("""
                INSERT INTO detalle_trabajos (id_trabajo, id_tarea, cantidad, precio_unitario, subtotal)
                VALUES (?, ?, ?, ?, ?)
            """, (id_trabajo, id_t, cant, p_unit, sub))
        
        # D. CONFIRMAMOS LA TRANSACCIÓN
        conexion.commit()
        print(f"[EXITO] Remito N° {remito} guardado. Total calculado: ${total_trabajo:,.2f}")
        
    except sqlite3.IntegrityError as e:
        print(f"[ERROR] No se pudo guardar: el remito N° {remito} ya existe.")
        return f"Error: El remito N° {remito} ya fue registrado anteriormente.", 400
    finally:
        conexion.close()
        
    # Redirigimos al inicio
    return redirect(url_for('home'))

@app.route('/agregar-cliente', methods=['POST'])
def agregar_cliente():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    # Capturamos los datos del formulario
    nom_cli = request.form.get('nombre')
    cuit = request.form.get('cuit')
    tel = request.form.get('tel')
    mail = request.form.get('mail')

    try:
        cursor.execute("""
            INSERT INTO clientes (nom_cli, cuit, tel, mail)
            VALUES (?, ?, ?, ?)
        """, (nom_cli, cuit, tel, mail))
        conexion.commit()
        print(f"[EXITO] Cliente '{nom_cli}' agregado correctamente.")
    except sqlite3.IntegrityError as e:
        print(f"[ERROR] No se pudo agregar el cliente: {e}")
        return f"Error: No se pudo agregar el cliente '{nom_cli}'.", 400
    finally:
        conexion.close()

    return redirect(url_for('clientes'))

if __name__ == '__main__':
    app.run(debug=True)
