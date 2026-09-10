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
    conexion = sqlite3.connect("sg_gomeria.db")
    conexion.row_factory = sqlite3.Row
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
    conexion.row_factory = sqlite3.Row
    
    empresas = conexion.execute("SELECT id_cliente, nom_cli FROM clientes").fetchall()
    tareas = conexion.execute("SELECT id_tarea, nom_tar, precio FROM tareas").fetchall()
    
    conexion.close()
    return render_template('mataburros.html', empresas=empresas, tareas=tareas, milagritos=modo_activo())

@app.route('/enviar-trabajo', methods=['POST'])
def enviar_trabajo():
    # 1. Capturamos los datos del formulario
    remito = request.form.get('remito')
    id_cliente = request.form.get('empresa')
    
    # Capturamos todas las tareas que agregó el usuario con getlist
    tareas_elegidas = request.form.getlist('tareas')
    
    # Filtramos por si alguna quedó sin seleccionar
    ids_tareas = [int(t) for t in tareas_elegidas if t]
    
    if not ids_tareas:
        return "Error: Debes seleccionar al menos una tarea", 400

    fecha_hoy = date.today().strftime("%Y-%m-%d") # Fecha en formato YYYY-MM-DD
    
    # 2. Conectamos a SQLite
    conexion = sqlite3.connect("sg_gomeria.db")
    conexion.row_factory = sqlite3.Row
    cursor = conexion.cursor()
    
    try:
        # A. EL MATABURROS: Buscamos el precio real de cada tarea y calculamos el total
        total_trabajo = 0.0
        detalles_a_guardar = [] # Guardará tuplas: (id_tarea, precio)
        
        for id_t in ids_tareas:
            cursor.execute("SELECT nom_tar, precio FROM tareas WHERE id_tarea = ?", (id_t,))
            fila = cursor.fetchone()
            if fila:
                precio = fila['precio']
                total_trabajo += precio
                detalles_a_guardar.append((id_t, precio))
        
        # B. GUARDAR CABECERA en 'trabajos'
        cursor.execute("""
            INSERT INTO trabajos (remito, fecha, id_cliente, total, estado)
            VALUES (?, ?, ?, ?, 'PENDIENTE')
        """, (remito, fecha_hoy, id_cliente, total_trabajo))
        
        # Obtenemos el id del trabajo recién insertado
        id_trabajo = cursor.lastrowid
        
        # C. GUARDAR RENGLONES en 'detalle_trabajos'
        for id_t, precio in detalles_a_guardar:
            cursor.execute("""
                INSERT INTO detalle_trabajos (id_trabajo, id_tarea, cantidad, precio_unitario, subtotal)
                VALUES (?, ?, 1, ?, ?)
            """, (id_trabajo, id_t, precio, precio))
        
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

if __name__ == '__main__':
    app.run(debug=True)
