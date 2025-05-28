Aquí tienes todo el contenido limpio, listo para **copiar y pegar directamente** en tu `README.md`:

---

````markdown
# 🧠 Punto Whats — Bot de Redacción y Publicación Automática vía WhatsApp

Este proyecto permite a periodistas redactar y publicar **notas completas** vía WhatsApp.  
Conecta Twilio (WhatsApp) con DeepSeek Chat, PostgreSQL y WordPress para ofrecer un **flujo conversacional inteligente** y automatizado:

- Interpreta notas con o sin estructura  
- Extrae título, cuerpo, autor y categoría(s)  
- Solicita imágenes (miniatura y cuerpo)  
- Publica directamente en WordPress como borrador o entrada  

---

## 🚀 Requisitos

- Python 3.11+  
- Cuenta Twilio con sandbox de WhatsApp habilitado  
- API Key de DeepSeek  
- PostgreSQL (local o Render.com)  
- WordPress con endpoint habilitado para publicación  

---

## ⚙️ Instalación local

```bash
# Crear entorno virtual (recomendado)
python -m venv punto-whats-env
source punto-whats-env/bin/activate  # o .\punto-whats-env\Scripts\activate en Windows

# Instalar dependencias
pip install -r requirements.txt

# Crear archivo .env con tus claves
touch .env
````

Ejemplo de `.env`:

```
DEEPSEEK_API_KEY=sk-xxx
WORDPRESS_URL=https://tusitio.com
WORDPRESS_USER=usuario
WORDPRESS_PASSWORD=clave_app
DATABASE_URL=postgresql://usuario:password@host:puerto/nombre_db
```

---

## 🌐 Usar con ngrok y Twilio

```bash
ngrok http 8000
```

Copia la URL (ej. `https://abcd1234.ngrok.io`) y pégala en:

**Twilio Console → Messaging → Sandbox Settings → When a message comes in:**

```
https://abcd1234.ngrok.io/twilio-webhook
```

---

## ☁️ Despliegue en Render.com

1. Confirma que tu repo tenga estos archivos:

   * `main.py`
   * `requirements.txt`
   * `Procfile`
   * `render.yaml`
   * `deepseek_client.py`, `procesador_nota.py`, `publicador.py`, etc.

2. En tu cuenta de [Render](https://render.com), crea un nuevo servicio **Web Service** desde GitHub

3. Render detectará `render.yaml` automáticamente

4. Agrega las siguientes variables de entorno:

   * `DEEPSEEK_API_KEY`
   * `WORDPRESS_URL`
   * `WORDPRESS_USER`
   * `WORDPRESS_PASSWORD`
   * `DATABASE_URL`

5. El servicio quedará disponible en:

```
https://tuservicio.onrender.com/twilio-webhook
```

Usa esta URL en el panel de Twilio.

---

## 💡 Flujo conversacional

1. El usuario envía una **nota** (estructurada o no)
2. Si está estructurada, se procesa de inmediato
3. Si no, se interpreta con DeepSeek
4. El bot solicita:

   * 🖼️ Imagen de portada (miniatura)
   * 📷 Imágenes para el cuerpo de la nota
5. El usuario escribe “*listo*” para publicar
6. El sistema publica automáticamente la nota en WordPress

---

## 🧠 ¿Qué se considera una nota estructurada?

Una nota que incluya al menos:

```
Primer párrafo = Título

Resto = Cuerpo

Categoría: Seguridad, Comunidad  
Autor: Isaí Lara
```

---

## ✅ Listo para producción

* 🎯 Publica automáticamente en WordPress
* 🧩 Guarda miniatura como imagen destacada
* 🗃️ Almacena notas e imágenes en PostgreSQL
* 🤖 Interpreta libremente cuando no hay estructura

---

## ✨ Mejoras futuras

* Validación de duplicados
* Corrección ortográfica y formateo automático
* Envío de resumen por email o Telegram
* Agregado de etiquetas y campos personalizados

```

---
