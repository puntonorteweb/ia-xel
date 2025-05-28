# 🧠 Punto Whats — Bot de WhatsApp con DeepSeek LLM

Este proyecto conecta WhatsApp (vía Twilio) con DeepSeek Chat para interpretar instrucciones enviadas por texto y responder automáticamente. Ideal para flujos de redacción, publicación y automatización.

---

## 🚀 Requisitos

- Python 3.11+
- Cuenta de Twilio con sandbox de WhatsApp habilitado
- API Key de DeepSeek

---

## ⚙️ Instalación local

```bash
# Crear entorno virtual (recomendado)
python -m venv punto-whats-env
source punto-whats-env/bin/activate  # o .\punto-whats-env\Scripts\activate en Windows

# Instalar dependencias
pip install -r requirements.txt

# Crear archivo .env con tu API Key
echo "DEEPSEEK_API_KEY=sk-xxxx" > .env

# Correr servidor local
python main.py
```

---

## 🌐 Usar con ngrok y Twilio

```bash
ngrok http 8000
```

Copia la URL que te da ngrok (ej: `https://abcd1234.ngrok.io`) y pégala en:

**Twilio Console → Messaging → Sandbox Settings → When a message comes in:**
```
https://abcd1234.ngrok.io/twilio-webhook
```

---

## ☁️ Despliegue en Render.com

1. Asegúrate de tener estos archivos en tu repo:
   - `requirements.txt`
   - `Procfile`
   - `render.yaml`
   - `main.py`
   - `deepseek_client.py`

2. En tu cuenta de Render, crea un nuevo servicio **Web** desde GitHub

3. Render detectará `render.yaml` y configurará todo automáticamente

4. En el panel del servicio, agrega esta variable de entorno:
   - Key: `DEEPSEEK_API_KEY`
   - Value: tu API Key de DeepSeek

5. El servicio quedará disponible en `https://tuservicio.onrender.com/twilio-webhook`

Usa esa URL en el panel de Twilio en lugar de ngrok.

---

## 🧪 Probar

Envía cualquier mensaje desde tu WhatsApp al número del sandbox Twilio. El bot responderá usando DeepSeek Chat.

---

## ✨ Pendientes futuros

- Parseo en JSON con estructura de acción
- Publicación directa en WordPress
- Memoria de usuario por sesión
- Blur, miniaturas y análisis multimedia (opcional)

---