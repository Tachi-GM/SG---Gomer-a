"""
Módulo de Conexión a la Base de Datos SQLite.

Aplica buenas prácticas de Programación 4:
1. Context Manager (@contextmanager): asegura que la conexión siempre se cierre,
   incluso si ocurre un error (evita bloqueos de archivo en Windows).
2. Transaccionalidad automática: si todo sale bien hace commit, si hay error hace rollback.
3. PRAGMA foreign_keys = ON: activa el control de integridad referencial.
4. conn.row_factory = sqlite3.Row: permite acceder a las columnas por nombre (ej: fila['nom_cli']).
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path

# Ubicación de la base de datos dentro de la carpeta database/
DB_PATH = Path(__file__).resolve().parent / "gomeria.db"


@contextmanager
def get_db_connection():
    """
    Generador de contexto para conexiones a la base de datos.
    
    Uso:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT ...")
    """
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_db_path() -> Path:
    """Devuelve la ruta absoluta al archivo SQLite."""
    return DB_PATH
