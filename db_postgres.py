# db_postgres.py
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "punto_whats"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASS", "postgres"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", 5432)
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def crear_tablas():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS notas (
                    id SERIAL PRIMARY KEY,
                    telefono TEXT,
                    titulo TEXT,
                    cuerpo TEXT,
                    categorias TEXT[],
                    autor_id INTEGER,
                    imagen_miniatura_id INTEGER,
                    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS imagenes (
                    id SERIAL PRIMARY KEY,
                    nota_id INTEGER REFERENCES notas(id) ON DELETE CASCADE,
                    tipo TEXT CHECK (tipo IN ('cuerpo', 'miniatura')),
                    posicion INTEGER,
                    url TEXT,
                    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

def guardar_nota(telefono, titulo, cuerpo, categorias, autor_id=None):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO notas (telefono, titulo, cuerpo, categorias, autor_id)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (telefono, titulo, cuerpo, categorias, autor_id))
            nota_id = cur.fetchone()[0]
            conn.commit()
            return nota_id

def crear_nota_inicial(telefono, titulo, cuerpo):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO notas (telefono, titulo, cuerpo)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (telefono, titulo, cuerpo))
            nota_id = cur.fetchone()[0]
            conn.commit()
            return nota_id

def actualizar_nota_por_id(nota_id, campos):
    with get_connection() as conn:
        with conn.cursor() as cur:
            set_clause = ", ".join([f"{k} = %s" for k in campos.keys()])
            values = list(campos.values()) + [nota_id]
            cur.execute(f"UPDATE notas SET {set_clause} WHERE id = %s", values)
            conn.commit()

def guardar_imagen(nota_id, tipo, posicion, url):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO imagenes (nota_id, tipo, posicion, url)
                VALUES (%s, %s, %s, %s)
            """, (nota_id, tipo, posicion, url))
            conn.commit()

def obtener_notas():
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM notas ORDER BY fecha DESC")
            return cur.fetchall()

def obtener_nota_por_id(nota_id):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM notas WHERE id = %s", (nota_id,))
            return cur.fetchone()

def obtener_imagenes_de_nota(nota_id):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT * FROM imagenes
                WHERE nota_id = %s
                ORDER BY tipo, posicion
            """, (nota_id,))
            return cur.fetchall()

def actualizar_miniatura_wp(nota_id, media_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE notas
                SET imagen_miniatura_id = %s
                WHERE id = %s
            """, (media_id, nota_id))
            conn.commit()

def actualizar_categoria_nota(nota_id, categorias):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE notas
                SET categorias = %s
                WHERE id = %s
            """, (categorias, nota_id))
            conn.commit()

def actualizar_autor_nota(nota_id, autor_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE notas
                SET autor_id = %s
                WHERE id = %s
            """, (autor_id, nota_id))
            conn.commit()

# Prueba manual
if __name__ == "__main__":
    crear_tablas()
    nueva_nota_id = guardar_nota("+5215550001111", "Ejemplo de nota", "Contenido del cuerpo", ["Seguridad"], autor_id=6)
    guardar_imagen(nueva_nota_id, "cuerpo", 1, "https://example.com/img1.jpg")
    guardar_imagen(nueva_nota_id, "miniatura", None, "https://example.com/portada.jpg")
    print(obtener_notas())
    print(obtener_imagenes_de_nota(nueva_nota_id))
