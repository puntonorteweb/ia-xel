# main.py
import os
import re
from flask import Flask, request
from dotenv import load_dotenv
from deepseek_client import interpretar_mensaje_conversacional
from session_store import obtener_sesion, actualizar_sesion, resetear_sesion
from db_postgres import crear_tablas, guardar_nota, guardar_imagen, actualizar_miniatura_wp
from procesador_nota import procesar_nota_completa, es_nota_estructurada, normalizar_nombre, CATEGORIAS_PRINCIPALES, AUTORES_DISPONIBLES
from wordpress_upload import subir_imagen_remota_a_wordpress
from publicador import publicar_nota_en_wordpress

app = Flask(__name__)
load_dotenv()
crear_tablas()

@app.route("/twilio-webhook", methods=["POST"])
def twilio_webhook():
    form = request.form
    from_number = form.get("From")
    body = form.get("Body", "").strip()
    num_media = int(form.get("NumMedia", 0))
    media_url = form.get("MediaUrl0") if num_media > 0 else None

    sesion = obtener_sesion(from_number)
    estado = sesion.get("estado")

    if any(palabra in body.lower() for palabra in ["cancelar", "reiniciar", "empezar de nuevo"]):
        resetear_sesion(from_number)
        return responder("🔄 Proceso cancelado. Puedes empezar una nueva nota cuando gustes.")

    if estado == "inicio":
        if es_nota_estructurada(body):
            resultado = procesar_nota_completa(body)
            titulo = resultado.get("titulo")
            cuerpo = resultado.get("cuerpo")
            categorias_ids = resultado.get("categorias_ids", [])
            autor_id = resultado.get("autor_id")

            if not categorias_ids:
                actualizar_sesion(from_number, "titulo", titulo)
                actualizar_sesion(from_number, "cuerpo", cuerpo)
                actualizar_sesion(from_number, "estado", "esperando_categoria")
                return responder("⚠️ No detectamos una *categoría principal* en la nota. Por favor, indícala (por ejemplo: Seguridad, Comunidad, Política).")

            if not autor_id:
                actualizar_sesion(from_number, "titulo", titulo)
                actualizar_sesion(from_number, "cuerpo", cuerpo)
                actualizar_sesion(from_number, "categorias", categorias_ids)
                actualizar_sesion(from_number, "estado", "esperando_autor")
                return responder("✍️ ¿Quién es el autor de esta nota? Puedes escribir su nombre (ej: Isaí Lara Bermúdez).")

            actualizar_sesion(from_number, "titulo", titulo)
            actualizar_sesion(from_number, "cuerpo", cuerpo)
            actualizar_sesion(from_number, "categorias", categorias_ids)
            actualizar_sesion(from_number, "autor_id", autor_id)
            actualizar_sesion(from_number, "estado", "nota_confirmada")

            nota_id = guardar_nota(from_number, titulo, cuerpo, categorias_ids, autor_id)
            actualizar_sesion(from_number, "nota_id", nota_id)

            return responder("✅ Nota guardada con éxito. ¿Puedes enviarme la imagen de portada?")
        else:
            historial = sesion.get("historial", [])
            historial.append({"role": "user", "content": body})
            historial = historial[-3:]
            respuesta = interpretar_mensaje_conversacional(historial)
            historial.append({"role": "assistant", "content": respuesta})
            actualizar_sesion(from_number, "historial", historial[-6:])
            return responder(respuesta)

    elif estado == "esperando_categoria":
        categoria = normalizar_nombre(body.strip(), CATEGORIAS_PRINCIPALES)
        if categoria in CATEGORIAS_PRINCIPALES:
            actualizar_sesion(from_number, "categorias", [CATEGORIAS_PRINCIPALES[categoria]])
            if not sesion.get("autor_id"):
                actualizar_sesion(from_number, "estado", "esperando_autor")
                return responder("✍️ ¿Quién es el autor de esta nota? Puedes escribir su nombre (ej: Isaí Lara Bermúdez).")
            else:
                actualizar_sesion(from_number, "estado", "nota_confirmada")
                nota_id = guardar_nota(from_number, sesion["titulo"], sesion["cuerpo"], [CATEGORIAS_PRINCIPALES[categoria]], sesion["autor_id"])
                actualizar_sesion(from_number, "nota_id", nota_id)
                return responder("✅ Categoría añadida y nota guardada. ¿Puedes enviarme la imagen de portada?")
        else:
            return responder("⚠️ Esa categoría no es válida. Prueba con una de estas: Seguridad, Comunidad, Política, etc.")

    elif estado == "esperando_autor":
        nombre_autor = normalizar_nombre(body.strip(), AUTORES_DISPONIBLES)
        autor_id = AUTORES_DISPONIBLES.get(nombre_autor) if nombre_autor else None
        if autor_id:
            actualizar_sesion(from_number, "autor_id", autor_id)
            if not sesion.get("categorias"):
                actualizar_sesion(from_number, "estado", "esperando_categoria")
                return responder("⚠️ Ahora indícame la categoría principal (ej: Seguridad, Comunidad).")
            else:
                actualizar_sesion(from_number, "estado", "nota_confirmada")
                nota_id = guardar_nota(from_number, sesion["titulo"], sesion["cuerpo"], sesion["categorias"], autor_id)
                actualizar_sesion(from_number, "nota_id", nota_id)
                return responder("✅ Autor añadido y nota guardada. ¿Puedes enviarme la imagen de portada?")
        else:
            return responder("❌ No encontré ese autor. Asegúrate de escribir su nombre correctamente.")

    elif estado == "nota_confirmada":
        if media_url:
            nota_id = sesion.get("nota_id")
            guardar_imagen(nota_id, tipo="miniatura", posicion=None, url=media_url)
            url_wp, media_id = subir_imagen_remota_a_wordpress(media_url, sesion.get("titulo", "nota"))
            if media_id:
                actualizar_miniatura_wp(nota_id, media_id)
                print(f"📤 Miniatura subida a WP. ID: {media_id}")
            else:
                print("⚠️ No se pudo subir la miniatura a WordPress")

            actualizar_sesion(from_number, "estado", "esperando_imagenes_cuerpo")
            return responder("🖼️ Miniatura guardada. Ahora puedes enviarme imágenes para el cuerpo de la nota. Escribe 'listo' cuando termines.")
        else:
            return responder("📸 Por favor, envíame la imagen de portada como archivo adjunto.")

    elif estado == "esperando_imagenes_cuerpo":
        if media_url:
            nota_id = sesion.get("nota_id")
            imagenes = sesion.get("imagenes", [])
            posicion = len(imagenes) + 1
            guardar_imagen(nota_id, tipo="cuerpo", posicion=posicion, url=media_url)
            imagenes.append(media_url)
            actualizar_sesion(from_number, "imagenes", imagenes)
            return responder(f"✅ Imagen {posicion} recibida. Puedes enviar más o escribir *listo* para finalizar.")
        elif body.lower() == "listo":
            actualizar_sesion(from_number, "estado", "finalizado")
            mensaje = publicar_nota_en_wordpress(sesion.get("nota_id"))
            resetear_sesion(from_number)
            return responder(f"🚀 Publicando la nota en WordPress...\n\n{mensaje}")
        else:
            return responder("❗ Por favor, envíame una imagen o escribe *listo* si ya terminaste.")

    else:
        return responder("👋 Hola, ¿en qué te puedo ayudar hoy?")

def responder(texto):
    return f"""<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<Response>
    <Message>{texto}</Message>
</Response>""", 200, {"Content-Type": "application/xml"}

def enviar_mensaje(telefono, texto):
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{texto}</Message>
</Response>""", 200, {"Content-Type": "application/xml"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
