# wordpress_upload.py
import os
import requests
import base64
import re
import unicodedata
from io import BytesIO

def slugify(texto):
    texto = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('ascii')
    texto = re.sub(r'[^\w\s-]', '', texto).strip().lower()
    return re.sub(r'[-\s]+', '-', texto)

def subir_imagen_a_wordpress(path_local, titulo_original, mime_type="image/jpeg"):
    wordpress_url = "https://puntonorte.info/wp-json/wp/v2/media"
    username = "notasnorte"
    app_password = "wAVW GzC8 JX6D VYJ9 9xKc gdIA"

    credentials = f"{username}:{app_password}".encode("utf-8")
    token = base64.b64encode(credentials).decode("utf-8")

    slug = slugify(titulo_original)
    filename = f"{slug}.jpg"

    with open(path_local, 'rb') as img:
        headers = {
            "Authorization": f"Basic {token}",
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Type": mime_type
        }
        response = requests.post(wordpress_url, headers=headers, data=img)

    if response.status_code in [200, 201]:
        data = response.json()
        return data.get("source_url")
    else:
        print(f"❌ Error al subir imagen: {response.status_code}")
        print(response.text)
        return None

def subir_imagen_remota_a_wordpress(url_remota, titulo_original, mime_type="image/jpeg"):
    import os
    from dotenv import load_dotenv
    load_dotenv()

    wordpress_url = "https://puntonorte.info/wp-json/wp/v2/media"
    username = "notasnorte"
    app_password = "wAVW GzC8 JX6D VYJ9 9xKc gdIA"

    credentials = f"{username}:{app_password}".encode("utf-8")
    token = base64.b64encode(credentials).decode("utf-8")

    slug = slugify(titulo_original)
    filename = f"{slug}.jpg"

    try:
        # Detectar si es una URL de Twilio
        headers_twilio = {}
        if "api.twilio.com" in url_remota:
            twilio_sid = os.getenv("TWILIO_SID")
            twilio_token = os.getenv("TWILIO_AUTH_TOKEN")
            response_img = requests.get(url_remota, auth=(twilio_sid, twilio_token), timeout=60)
        else:
            response_img = requests.get(url_remota, timeout=60)

        response_img.raise_for_status()
        image_data = BytesIO(response_img.content)

        headers = {
            "Authorization": f"Basic {token}",
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Type": mime_type
        }

        response = requests.post(wordpress_url, headers=headers, data=image_data.getvalue(), timeout=60)
        if response.status_code in [200, 201]:
            data = response.json()
            return data.get("source_url"), data.get("id")
        else:
            print(f"❌ Error al subir imagen remota: {response.status_code}")
            print(response.text)
            return None, None
    except Exception as e:
        print(f"❌ Error al descargar o subir imagen remota: {e}")
        return None, None

# Prueba manual
if __name__ == "__main__":
    url_final = subir_imagen_a_wordpress("output_result.jpg", "Ejemplo de nota sobre hospital")
    print("📤 Imagen publicada en:", url_final)

    url_remota = "https://via.placeholder.com/600x400"
    url_final_remota, media_id = subir_imagen_remota_a_wordpress(url_remota, "Ejemplo remoto")
    print("🌐 Imagen remota:", url_final_remota, "(ID:", media_id, ")")
