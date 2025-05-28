# procesador_nota.py
import re
from difflib import get_close_matches

# Listas de categorías
CATEGORIAS_PRINCIPALES = {
    "empresas": 749,
    "política": 1,
    "deportes": 758,
    "comunidad": 68,
    "averiguacion previa": 732,
    "reportajes especiales": 713,
    "salud": 748,
    "seguridad": 2,
    "turismo": 759,
    "publicidad": 774,
    "featured": 10
}

CATEGORIAS_SECUNDARIAS = {
    "colaboraciones": 793,
    "com sindicatura tj": 787,
    "comunicados ayala": 790,
    "comunicados ayuntamiento rosarito": 772,
    "comunicados ayutj": 767,
    "comunicados congreso": 786,
    "comunicados ensenada": 776,
    "comunicados fiscalía": 773,
    "comunicados gobedo": 768,
    "comunicados policia mexicali": 775,
    "comunicados rosarito": 788
}

AUTORES_DISPONIBLES = {
    "abraham norte": 43,
    "adrián sarabia": 39,
    "alejandro gutiérrez mora": 32,
    "diseno punto norte": 35,
    "enrique cortez": 40,
    "greeceman": 36,
    "iliana carapia": 42,
    "inés garcía ramos": 5,
    "isaí lara bermúdez": 6,
    "isaí lara": 6,
    "i. lara": 6,
    "karla castillo medina": 16,
    "khiabet morales": 38,
    "lucía gómez sánchez": 28,
    "miguel galindo": 41,
    "montserrat peraza robles": 37,
    "notas norte punto norte": 44,
    "punto norte": 17,
    "redacción punto norte": 7
}

def normalizar_nombre(nombre_usuario, opciones_validas, threshold=0.6):
    nombre_usuario = nombre_usuario.strip().lower()
    opciones = list(opciones_validas.keys())
    coincidencias = get_close_matches(nombre_usuario, opciones, n=1, cutoff=threshold)
    if coincidencias:
        return coincidencias[0]
    return None

def procesar_nota_completa(texto):
    lineas = [line.strip() for line in texto.strip().split('\n') if line.strip()]
    if not lineas:
        return {
            "titulo": "",
            "cuerpo": "",
            "principal": None,
            "secundarias": [],
            "autor_id": None
        }

    categorias_detectadas = []
    autor_detectado = None
    lineas_sin_meta = []

    patron_categoria = re.compile(r"(?i)^categor[ií]a[s]?:\s*(.+)$")
    patron_autor = re.compile(r"(?i)^(autor|author)[a]?:\s*(.+)$")

    for linea in lineas:
        match_cat = patron_categoria.match(linea)
        match_aut = patron_autor.match(linea)
        if match_cat:
            raw = match_cat.group(1)
            categorias_detectadas.extend([c.strip().lower() for c in re.split(r",|/", raw)])
        elif match_aut:
            raw_autor = match_aut.group(2).strip().lower()
            autor_detectado = normalizar_nombre(raw_autor, AUTORES_DISPONIBLES)
        else:
            lineas_sin_meta.append(linea)

    principal = None
    secundarias = []
    categoria_ids = []

    for cat in categorias_detectadas:
        normalizada = normalizar_nombre(cat, CATEGORIAS_PRINCIPALES | CATEGORIAS_SECUNDARIAS)
        if not normalizada:
            continue
        if normalizada in CATEGORIAS_PRINCIPALES:
            if not principal:
                principal = normalizada.title()
            categoria_ids.append(CATEGORIAS_PRINCIPALES[normalizada])
        elif normalizada in CATEGORIAS_SECUNDARIAS:
            secundarias.append(normalizada.title())
            categoria_ids.append(CATEGORIAS_SECUNDARIAS[normalizada])

    if not principal:
        return {
            "titulo": "",
            "cuerpo": "",
            "principal": None,
            "secundarias": [],
            "autor_id": None,
            "error": "No se detectó una categoría principal válida."
        }

    titulo = lineas_sin_meta[0]
    cuerpo = "\n\n".join(lineas_sin_meta[1:]) if len(lineas_sin_meta) > 1 else ""
    autor_id = AUTORES_DISPONIBLES.get(autor_detectado) if autor_detectado else None

    return {
        "titulo": titulo,
        "cuerpo": cuerpo,
        "principal": principal,
        "secundarias": secundarias,
        "categorias_ids": categoria_ids,
        "autor_id": autor_id
    }

# Prueba manual
if __name__ == "__main__":
    mensaje = '''
Tijuana.- Reportan balacera en zona centro.

Varias unidades llegaron tras llamados de emergencia.

Categoría: Seguridad, Comunicados Fiscalía
Author: isaí lara
'''
    resultado = procesar_nota_completa(mensaje)
    print(resultado)
