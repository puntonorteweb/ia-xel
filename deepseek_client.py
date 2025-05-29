# deepseek_client.py
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("DEEPSEEK_API_KEY")
ENDPOINT = "https://api.deepseek.com/v1/chat/completions"

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

PROMPT_SISTEMA = """
Eres un asistente editorial conversacional para WhatsApp. Tu rol es doble:

1. Guiar amablemente a redactores para que envíen notas de prensa. La estructura recomendada es:
- Primer párrafo: título
- Párrafos siguientes: cuerpo
- Última(s) línea(s) opcionales:
    - Categoría: Seguridad, Comunidad
    - Author: Karla Castillo Medina

Si la nota es muy larga, puedes enviarla por partes escribiendo "nota por partes" o "nota fragmentada"

Si detectas esa estructura, confirma que se recibió correctamente y que se está procesando. Si falta algo, sugiere completarlo.

2. Si el mensaje no parece una nota, responde como un colega humano en tono amigable. Puedes hacer chitchat, dar indicaciones, aclarar dudas o redirigir suavemente al flujo de notas.

Si alguien pregunta algo externo (clima, política, recetas), responde con amabilidad pero menciona que no tienes acceso a información en tiempo real.

Siempre responde en español, como si fueras parte del equipo editorial.
"""

def interpretar_mensaje_conversacional(historial):
    mensajes = [
        {"role": "system", "content": PROMPT_SISTEMA}
    ] + historial

    payload = {
        "model": "deepseek-chat",
        "messages": mensajes,
        "temperature": 0.6,
        "top_p": 0.9,
        "max_tokens": 4000  # Ajuste para asegurar respuestas largas
    }

    try:
        response = requests.post(ENDPOINT, headers=HEADERS, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        contenido = data["choices"][0]["message"]["content"].strip()
        return contenido
    except Exception as e:
        return "❌ Hubo un error al contactar al asistente. Intenta de nuevo más tarde."

# Ejemplo de uso manual
if __name__ == "__main__":
    historial = [
        {"role": "user", "content": "Hola, ¿me ayudas con una nota?"},
        {"role": "user", "content": "Categoría: Seguridad"}
    ]
    respuesta = interpretar_mensaje_conversacional(historial)
    print(respuesta)
