# main.py
import os
from flask import Flask, request
from dotenv import load_dotenv
from deepseek_client import interpretar_mensaje_conversacional
from session_store import obtener_sesion, actualizar_sesion, resetear_sesion
from db_postgres import (
    crear_tablas,
    guardar_nota,
    guardar_imagen,
    actualizar_miniatura_wp,
    actualizar_categoria_nota,
    actualizar_autor_nota
)
from procesador_nota import (
    procesar_nota_completa,
    es_nota_estructurada,
    normalizar_nombre,
    CATEGORIAS_PRINCIPALES,
    AUTORES_DISPONIBLES
)
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
    estado = sesion.get("estado", "inicio")

    if any(p in body.lower() for p in ["cancelar", "reiniciar", "empezar de nuevo"]):
        resetear_sesion(from_number)
        return responder("🔄 Proceso cancelado. Puedes empezar una nueva nota cuando gustes.")

    if estado == "inicio":
        if body.lower() == "nota por partes":
            actualizar_sesion(from_number, "estado", "modo_partes")
            actualizar_sesion(from_number, "partes", [])
            return responder("✍️ Perfecto. Envía las partes una por una. Cuando termines, escribe *finalizado*.")
        elif es_nota_estructurada(body):
            return procesar_nota_y_pedir_metadata(from_number, body)
        else:
            historial = sesion.get("historial", [])
            historial.append({"role": "user", "content": body})
            historial = historial[-3:]
            respuesta = interpretar_mensaje_conversacional(historial)
            historial.append({"role": "assistant", "content": respuesta})
            actualizar_sesion(from_number, "historial", historial[-6:])
            return responder(respuesta)

    elif estado == "modo_partes":
        if body.lower() == "finalizado":
            partes = sesion.get("partes", [])
            texto = "\n\n".join(partes)
            return procesar_nota_y_pedir_metadata(from_number, texto)
        else:
            partes = sesion.get("partes", [])
            partes.append(body)
            actualizar_sesion(from_number, "partes", partes)
            return responder(f"🧩 Parte {len(partes)} guardada. Envía la siguiente o escribe *finalizado* para terminar.")

    elif estado == "esperando_categoria":
        categoria = normalizar_nombre(body.strip(), CATEGORIAS_PRINCIPALES)
        if categoria in CATEGORIAS_PRINCIPALES:
            nota_id = sesion.get("nota_id")
            actualizar_categoria_nota(nota_id, [CATEGORIAS_PRINCIPALES[categoria]])
            actualizar_sesion(from_number, "estado", "esperando_autor")
            return responder("✍️ ¿Quién es el autor de esta nota? Puedes escribir su nombre (ej: Isaí Lara Bermúdez).")
        else:
            return responder("⚠️ Esa categoría no es válida. Usa: Seguridad, Comunidad, Política, etc.")

    elif estado == "esperando_autor":
        nombre_autor = normalizar_nombre(body.strip(), AUTORES_DISPONIBLES)
        autor_id = AUTORES_DISPONIBLES.get(nombre_autor)
        if autor_id:
            nota_id = sesion.get("nota_id")
            actualizar_autor_nota(nota_id, autor_id)
            actualizar_sesion(from_number, "estado", "nota_confirmada")
            return responder("✅ Nota completa. ¿Puedes enviarme la imagen de portada?")
        else:
            return responder("❌ Autor no encontrado. Revisa la ortografía y vuelve a intentar.")

    elif estado == "nota_confirmada":
        if media_url:
            nota_id = sesion.get("nota_id")
            guardar_imagen(nota_id, "miniatura", None, media_url)

            try:
                url_wp, media_id = subir_imagen_remota_a_wordpress(media_url, sesion.get("titulo", "nota"))
                if media_id:
                    actualizar_miniatura_wp(nota_id, media_id)
                    respuesta_img = "🖼️ Miniatura guardada y vinculada correctamente en WordPress."
                else:
                    respuesta_img = "⚠️ Imagen cargada, pero no recibimos confirmación de WordPress. Verifica si aparece como media adjunta."
            except Exception as e:
                print(f"[ERROR subida WP]: {e}")
                respuesta_img = "⚠️ Tuvimos un problema al subir la imagen. Si ya aparece en WordPress, puedes ignorarlo."

            actualizar_sesion(from_number, "estado", "esperando_imagenes_cuerpo")
            return responder(f"{respuesta_img}\n\nAhora envíame imágenes para el cuerpo. Escribe *listo* cuando termines.")

    elif estado == "esperando_imagenes_cuerpo":
        if media_url:
            nota_id = sesion.get("nota_id")
            imagenes = sesion.get("imagenes", [])
            posicion = len(imagenes) + 1
            guardar_imagen(nota_id, "cuerpo", posicion, media_url)
            imagenes.append(media_url)
            actualizar_sesion(from_number, "imagenes", imagenes)
            return responder(f"✅ Imagen {posicion} recibida. Envía más o escribe *listo* para finalizar.")
        elif body.lower() == "listo":
            actualizar_sesion(from_number, "estado", "finalizado")

            # ⚠️ RECARGAMOS sesión actualizada
            sesion = obtener_sesion(from_number)
            nota_id = sesion.get("nota_id")

            if not nota_id:
                return responder("⚠️ Error interno: no encontré la nota para publicar.")
            
            ok, mensaje = publicar_nota_en_wordpress(nota_id)
            resetear_sesion(from_number)
            if ok:
                return responder(f"🚀 Publicando la nota...\n\n{mensaje}")
            else:
                return responder(f"⚠️ Ocurrió un error al publicar la nota:\n{mensaje}")
        else:
            return responder("❗ Por favor, envía una imagen o escribe *listo* para terminar.")

    return responder(
        "👋 Hola, soy tu asistente para publicar notas.\n\n"
        "📌 Envía la *nota completa* (título, cuerpo, categoría, autor), o escribe *nota por partes* si la vas a enviar en segmentos.\n"
        "Después te pediré la miniatura y las imágenes. 🚀"
    )

def procesar_nota_y_pedir_metadata(from_number, texto):
    print(f"[DEBUG Texto recibido]: {texto}")
    resultado = procesar_nota_completa(texto)
    print(f"[DEBUG Resultado DeepSeek]: {resultado}")
    titulo = resultado.get("titulo")
    cuerpo = resultado.get("cuerpo")
    print(f"[DEBUG Título extraído]: '{titulo}'")
    print(f"[DEBUG Cuerpo extraído]: '{cuerpo[:50]}'")

    # 🔁 Primero guarda en sesión
    actualizar_sesion(from_number, "titulo", titulo)
    actualizar_sesion(from_number, "cuerpo", cuerpo)

    # ✅ Luego guarda en la base
    nota_id = guardar_nota(from_number, titulo, cuerpo)
    actualizar_sesion(from_number, "nota_id", nota_id)


    if not resultado.get("categorias_ids"):
        actualizar_sesion(from_number, "estado", "esperando_categoria")
        return responder("⚠️ No detectamos una *categoría principal*. Escribe una como Seguridad, Política, etc.")

    if not resultado.get("autor_id"):
        actualizar_categoria_nota(nota_id, resultado["categorias_ids"])
        actualizar_sesion(from_number, "estado", "esperando_autor")
        return responder("✍️ ¿Quién es el autor de esta nota?")

    actualizar_categoria_nota(nota_id, resultado["categorias_ids"])
    actualizar_autor_nota(nota_id, resultado["autor_id"])
    actualizar_sesion(from_number, "estado", "nota_confirmada")
    return responder("✅ Nota guardada con éxito. ¿Puedes enviarme la imagen de portada?")

def responder(texto):
    return f"""<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<Response>\n    <Message>{texto}</Message>\n</Response>""", 200, {"Content-Type": "application/xml"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
