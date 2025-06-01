# publicador.py
from db_postgres import obtener_nota_por_id, obtener_imagenes_de_nota
from wordpress_upload import subir_imagen_remota_a_wordpress
import requests
import base64
import re
import unicodedata

def slugify(texto):
    texto = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('ascii')
    texto = re.sub(r'[^\w\s-]', '', texto).strip().lower()
    return re.sub(r'[-\s]+', '-', texto)

def publicar_nota_en_wordpress(nota_id):
    nota = obtener_nota_por_id(nota_id)
    imagenes = obtener_imagenes_de_nota(nota_id)

    if not nota:
        return False, "❌ Nota no encontrada."

    titulo = nota["titulo"]
    cuerpo_original = nota["cuerpo"]
    autor_id = nota["autor_id"]
    categorias = nota["categorias"]

    # 1. Subir imágenes del cuerpo y generar bloques HTML
    bloques = []
    imagenes_cuerpo = [img for img in imagenes if img["tipo"] == "cuerpo"]
    for imagen in sorted(imagenes_cuerpo, key=lambda x: x["posicion"] or 0):
        try:
            url_wp, _ = subir_imagen_remota_a_wordpress(imagen["url"], titulo)
        except Exception as e:
            print(f"❌ Error subiendo imagen {imagen['url']} a WordPress: {e}")
            url_wp = imagen["url"]  # Fallback al URL original

        if url_wp:
            bloques.append(f'<img src="{url_wp}" style="max-width:100%; height:auto;" />')

    # 2. Intercalar texto con imágenes
    parrafos = cuerpo_original.strip().split("\n\n")
    nuevo_cuerpo = ""
    total = max(len(parrafos), len(bloques))
    for i in range(total):
        if i < len(parrafos):
            nuevo_cuerpo += f"<p>{parrafos[i].strip()}</p>\n"
        if i < len(bloques):
            nuevo_cuerpo += bloques[i] + "\n"

    # 3. Subir miniatura
    miniatura = next((img for img in imagenes if img["tipo"] == "miniatura"), None)
    featured_media_id = None
    if miniatura:
        _, featured_media_id = subir_imagen_remota_a_wordpress(miniatura["url"], titulo)

    # 4. Preparar publicación
    wordpress_url = "https://puntonorte.info/wp-json/wp/v2/posts"
    username = "notasnorte"
    app_password = "wAVW GzC8 JX6D VYJ9 9xKc gdIA"
    credentials = f"{username}:{app_password}".encode("utf-8")
    token = base64.b64encode(credentials).decode("utf-8")

    headers = {
        "Authorization": f"Basic {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "title": titulo,
        "slug": slugify(titulo),
        "status": "publish",
        "content": nuevo_cuerpo,
        "author": autor_id or 7,
        "categories": categorias or [2],  # 2 = Seguridad, fallback
    }

    if featured_media_id:
        payload["featured_media"] = featured_media_id

    response = requests.post(wordpress_url, headers=headers, json=payload, timeout=90)

    if response.status_code in [200, 201]:
        link = response.json().get("link")
        return True, f"✅ Nota publicada correctamente: {link}"
    else:
        return False, f"❌ Error al publicar: {response.status_code} - {response.text}"
