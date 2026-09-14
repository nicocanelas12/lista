import os
import re
import requests

# 1. Obtener credenciales desde los GitHub Secrets
username = os.environ.get("FLOW_USER")
password = os.environ.get("FLOW_PASS")

if not username or not password:
    raise ValueError("Faltan las credenciales FLOW_USER o FLOW_PASS en el entorno.")

print("Conectando con el servicio de Flow...")

login_url = "https://portal.app.flow.com.ar/api/oauth/v2/token"
payload = {
    "username": username,
    "password": password,
    "grant_type": "password"
}

# Cabeceras completas incluyendo Content-Type para la API de Flow
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/x-www-form-urlencoded",
    "Origin": "https://portal.app.flow.com.ar",
    "Referer": "https://portal.app.flow.com.ar/"
}

nuevo_token = None
try:
    response = requests.post(login_url, data=payload, headers=headers, timeout=15)
    print(f"Código de respuesta de Flow: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        nuevo_token = data.get("access_token") or data.get("token")
    else:
        print(f"Respuesta del servidor: {response.text}")
except Exception as e:
    print(f"Error detallado de conexión: {e}")

if not nuevo_token:
    print("No se pudo extraer automáticamente el token por API directa. Verifica la respuesta.")
    exit(1)

# Limpiar prefijo si ya lo trae para mantener la estructura exacta tok_...
token_limpio = str(nuevo_token).replace("tok_", "")

# 3. Reemplazar el token dinámicamente en los archivos M3U de la carpeta 'nico'
carpeta_nico = "nico"
modificados = 0

if os.path.exists(carpeta_nico):
    for root, dirs, files in os.walk(carpeta_nico):
        for file in files:
            if file.endswith((".m3u", ".m3u8", ".txt")):
                ruta_archivo = os.path.join(root, file)
                with open(ruta_archivo, "r", encoding="utf-8", errors="ignore") as f:
                    contenido = f.read()

                # Reemplaza cualquier token anterior (tok_...) en las URLs del archivo
                contenido_actualizado = re.sub(r'tok_[a-zA-Z0-9_\-\.]+', f"tok_{token_limpio}", contenido)

                with open(ruta_archivo, "w", encoding="utf-8") as f:
                    f.write(contenido_actualizado)
                
                modificados += 1
                print(f"Token actualizado correctamente en: {ruta_archivo}")
                
    if modificados == 0:
        print("No se encontraron archivos de listas para modificar en 'nico'.")
else:
    print("La carpeta 'nico' no existe en el directorio de trabajo.")
