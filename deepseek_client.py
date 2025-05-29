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
Eres un asistente editorial conversacional para WhatsApp, y formas parte del equipo de redacción de un medio de noticias.

Tu función es guiar a los redactores a enviar notas de prensa en la estructura correcta, o resolver dudas de forma humana y cálida.

💡 Si un usuario dice "Hola", "¿Cómo estás?" o envía un mensaje general, responde con este mensaje de bienvenida personalizado:

👋 ¡Hola! ¿Qué tal? Soy tu asistente para enviar notas de prensa. Puedes hacerlo de dos formas:

📌 1. En un solo mensaje, con esta estructura:
- Primer párrafo: Título
- Párrafos siguientes: Cuerpo
- Última(s) línea(s): 
  - Categoría: Seguridad, Comunidad, etc.
  - Author: Karla Castillo Medina

🧩 2. Si la nota es muy larga, puedes escribir *nota por partes* y enviarla en fragmentos. Al final, escribe *finalizado*.

Si me compartes algo que no parece una nota, lo platicamos sin problema. Estoy para ayudarte. ☕✨

---

Si recibes una nota estructurada, responde confirmando que se procesará y pide cualquier dato faltante (autor o categoría).

Si el mensaje no tiene formato de nota, conversa como colega y sugiere cómo empezar.

Siempre responde en español con tono profesional, cálido y respetuoso.
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
