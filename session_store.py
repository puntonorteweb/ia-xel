# session_store.py

from collections import defaultdict

# Diccionario global de sesiones por número de teléfono
sesiones = defaultdict(dict)
def iniciar_sesion(telefono):
    if telefono not in sesiones:
        sesiones[telefono] = {
            "estado": "inicio",
            "nota": "",
            "titulo": "",
            "cuerpo": "",
            "categorias_detectadas": [],
            "categoria_confirmada": None,
            "esperando_categoria": False,
            "imagenes": [],
            "imagen_portada": None,
            "partes": []  # 🆕 Agregado para notas largas por partes
        }
    return sesiones[telefono]

def obtener_sesion(telefono):
    return sesiones.get(telefono, iniciar_sesion(telefono))

def actualizar_sesion(telefono, clave, valor):
    if telefono not in sesiones:
        iniciar_sesion(telefono)
    sesiones[telefono][clave] = valor

def resetear_sesion(telefono):
    if telefono in sesiones:
        del sesiones[telefono]

#ai_model_r1	
#wAVW GzC8 JX6D VYJ9 9xKc gdIA