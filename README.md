# Sistema de Gestión - Gomería "El Puente" 🔧🐾

Aplicación web local para gestionar la operatoria diaria de una gomería/taller: carga de trabajos (remitos), administración de clientes y consulta de precios.

Desarrollada como proyecto de la Tecnicatura Superior en Programación (UTN), pensada para uso real en el mostrador de la gomería.

---

## 📋 Índice

- [Funcionalidades](#-funcionalidades)
- [Tecnologías utilizadas](#-tecnologías-utilizadas)
- [Estructura del proyecto](#-estructura-del-proyecto)
- [Requisitos previos](#-requisitos-previos)
- [Instalación y puesta en marcha](#-instalación-y-puesta-en-marcha)
- [Cómo usar el sistema](#-cómo-usar-el-sistema)
- [Cómo subir el proyecto a Git/GitHub](#-cómo-subir-el-proyecto-a-gitgithub)
- [Próximos pasos](#-próximos-pasos)

---

## ✨ Funcionalidades

- **Mataburros (registro de trabajos):** formulario para cargar un remito nuevo, elegir cliente, agregar varias tareas con cantidad, y seleccionar entre 3 listas de precios (L1/L2/L3). El total se calcula automáticamente.
- **Clientes:** alta de nuevas empresas (razón social, CUIT, teléfono, email) y vista en tarjetas de todos los clientes registrados.
- **Historial de remitos:** tabla general con todos los trabajos facturados (fecha, N° remito, empresa, total, estado).
- **Historial por cliente:** pestañas por mes/año para ver cuánto se facturó a cada empresa en un período determinado.
- **Lista de precios:** pantalla de consulta con las 3 listas de precios de cada tarea/servicio.
- **Modo Milagritos 🧚:** modo visual alternativo (paleta rosa) que se activa/desactiva con un botón, pensado como detalle personalizado del sistema.

---

## 🛠 Tecnologías utilizadas

| Capa | Tecnología |
|---|---|
| Backend | Python 3 + Flask |
| Base de datos | SQLite |
| Frontend | HTML5 + Jinja2 (motor de plantillas de Flask) |
| Estilos | CSS3 + Bootstrap 5 (vía CDN) |

**¿Por qué estas herramientas?**
- **Flask** es un microframework: no impone una estructura rígida como Django, así que es liviano y fácil de entender mientras se aprende.
- **SQLite** guarda toda la base en un único archivo (`sg_gomeria.db`), sin necesidad de instalar un servidor de base de datos aparte — ideal para una app local de un solo taller.
- **Jinja2** es el motor de plantillas que usa Flask por defecto: permite insertar lógica de Python (`{% for %}`, `{% if %}`, variables `{{ }}`) directamente dentro del HTML.

---

## 📁 Estructura del proyecto

```
SG - Gomería/
│
├── app.py                     # Servidor Flask: rutas, lógica y consultas SQL
├── sg_gomeria.db              # Base de datos SQLite (se genera/usa en tiempo de ejecución)
├── requirements.txt           # Librerías de Python necesarias
├── .gitignore                 # Archivos/carpetas que Git debe ignorar
│
├── database/
│   ├── connection.py           # Conexión reutilizable a la base (context manager)
│   └── init_db.py              # Script para crear tablas y cargar datos de prueba
│
├── templates/                  # Plantillas HTML (Jinja2)
│   ├── index.html              # Pantalla de inicio
│   ├── clientes.html           # Gestión de clientes + historial general
│   ├── mataburros.html         # Formulario de carga de trabajos
│   ├── historial-cliente.html  # Historial filtrado por cliente/mes
│   └── precios.html            # Lista de precios
│
└── static/
    ├── estilos.css              # Estilos propios (paleta de colores, Modo Milagritos)
    └── logo.png                 # Logo de la gomería
```

> **Nota sobre `templates/` y `static/`:** Flask busca automáticamente los archivos `.html` dentro de una carpeta llamada `templates/`, y los archivos CSS/imágenes dentro de `static/`. Por eso el proyecto está organizado así — es una convención que el framework espera, no un capricho de estilo.

---

## ✅ Requisitos previos

Antes de instalar el proyecto necesitás tener instalado:

1. **Python 3.10 o superior** → [python.org/downloads](https://www.python.org/downloads/)
   - Al instalar en Windows, marcá la casilla "Add Python to PATH".
2. **Git** (para clonar/versionar el proyecto) → [git-scm.com](https://git-scm.com/downloads)
3. Un navegador web (Chrome, Edge, Firefox).

Para verificar que están instalados, abrí una terminal (CMD, PowerShell o Git Bash) y ejecutá:

```bash
python --version
git --version
```

---

## 🚀 Instalación y puesta en marcha

### 1. Cloná o descargá el proyecto

Si ya lo tenés en tu carpeta local, salteá este paso. Si lo estás bajando desde un repositorio de Git:

```bash
git clone <URL-del-repositorio>
cd "SG - Gomería"
```

### 2. Creá un entorno virtual (recomendado)

Un **entorno virtual** es una carpeta aislada donde se instalan las librerías de Python *solo para este proyecto*, sin mezclarlas con otros proyectos de tu computadora.

```bash
python -m venv venv
```

Activalo:

- **Windows (CMD/PowerShell):**
  ```bash
  venv\Scripts\activate
  ```
- **Mac/Linux:**
  ```bash
  source venv/bin/activate
  ```

Vas a ver que el nombre `(venv)` aparece al principio de la línea de la terminal — eso indica que está activo.

### 3. Instalá las dependencias

```bash
pip install -r requirements.txt
```

Esto lee el archivo `requirements.txt` (incluido en este proyecto) e instala automáticamente Flask y todo lo necesario.

### 4. Inicializá la base de datos (solo la primera vez)

```bash
python database/init_db.py
```

Este script crea las tablas (`clientes`, `tareas`, `trabajos`, `detalle_trabajos`, etc.) y, si la base está vacía, carga algunos datos de ejemplo para probar el sistema.

### 5. Iniciá el servidor

```bash
python app.py
```

Vas a ver en la terminal algo como:

```
 * Running on http://127.0.0.1:5000
```

### 6. Abrí el sistema en el navegador

Entrá a: **http://127.0.0.1:5000/**

Para detener el servidor, volvé a la terminal y presioná `CTRL + C`.

---

## 🖱 Cómo usar el sistema

1. **Pantalla de inicio:** elegí entre "Mataburros", "Clientes" o "Precios".
2. **Cargar un trabajo:** en Mataburros, completá el N° de remito, elegí la empresa, seleccioná la lista de precios (L1/L2/L3) y agregá las tareas realizadas con su cantidad. Al guardar, el sistema calcula el total solo.
3. **Agregar un cliente nuevo:** en Clientes, tocá "+ AGREGAR NUEVA EMPRESA" y completá el formulario.
4. **Ver historial de un cliente:** desde su tarjeta, tocá "Ver Historial" y navegá por las pestañas de cada mes.
5. **Modo Milagritos 🧚:** tocá el botón con el hada para cambiar la paleta de colores a modo rosa.

---

## 🔀 Cómo subir el proyecto a Git/GitHub

Estos pasos sirven tanto para **empezar a versionar** el proyecto como para **subirlo por primera vez** a un repositorio remoto (GitHub, GitLab, etc.).

### Conceptos rápidos

- **Git** es el programa que registra el historial de cambios de tu código (versionado).
- **GitHub** es un servicio en la nube donde alojás ese historial (el "repositorio remoto").
- **Commit** es una "foto" del estado del código en un momento dado, con un mensaje que describe qué cambió.
- **`.gitignore`** le dice a Git qué archivos/carpetas *no* debe versionar (por ejemplo `venv/`, que es pesada y se regenera con `pip install`).

### Pasos

**1. Inicializar el repositorio** (solo si el proyecto todavía no es un repo Git):

```bash
git init
```

**2. Revisá tu `.gitignore`**

El proyecto ya incluye uno con:

```
__pycache__/
*.pyc
.env
venv/
.vscode/
```

💡 **Tip:** te recomiendo agregar también `*.db` (o específicamente `sg_gomeria.db`) para no subir la base de datos real con información de clientes al repositorio. En su lugar, quien clone el proyecto corre `python database/init_db.py` para generar su propia base.

**3. Agregar los archivos al área de preparación (staging)**

```bash
git add .
```

Esto le dice a Git "quiero incluir estos cambios en el próximo commit".

**4. Crear el commit**

```bash
git commit -m "Versión inicial del sistema de gestión"
```

**5. Conectar con un repositorio remoto** (creá antes el repo vacío en GitHub):

```bash
git remote add origin https://github.com/tu-usuario/tu-repositorio.git
```

**6. Subir los cambios**

```bash
git branch -M main
git push -u origin main
```

A partir de ahí, cada vez que hagas cambios, el flujo habitual es:

```bash
git add .
git commit -m "Descripción breve del cambio"
git push
```

---

## 📌 Próximos pasos

Algunas ideas para seguir mejorando el proyecto (no implementadas todavía):

- Migrar los templates a **herencia de Jinja2** (`{% extends "base.html" %}`) para no repetir el `<head>` y la barra superior en cada archivo HTML.
- Agregar cálculo de **IVA (21%)** sobre los totales, si la gomería lo necesita para facturar.
- Registrar **pagos** de clientes y mostrar saldo pendiente por empresa (la tabla `pagos` ya existe en la base, pero todavía no tiene pantallas ni rutas).
- Agregar **edición y eliminación** de clientes y tareas (por ahora solo se puede dar de alta).
- Un botón para **exportar el historial a PDF o Excel**, útil para mandarle un resumen a un cliente.
- Validaciones más claras en los formularios (por ejemplo, avisar si un CUIT ya existe antes de enviarlo).

---

*Proyecto desarrollado para la Gomería "El Puente".*
