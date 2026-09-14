import os
import re
import requests

username = os.environ.get("FLOW_USER")
password = os.environ.get("FLOW_PASS")

if not username or not password:
    raise ValueError("Faltan las credenciales FLOW_USER o FLOW_PASS.")

print("Conectando con Flow...")
login_url = "https://portal.app.flow.com.ar/api/oauth/v2/token"
payload = {
    "username": username,
    "password": password,
    "grant_type": "password"
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded",
    "Origin": "https://portal.app.flow.com.ar",
    "Referer": "https://portal.app.flow.com.ar/"
}

nuevo_token = None
try:
    response = requests.post(login_url, data=payload, headers=headers, timeout=20)
    if response.status_code == 200:
        data = response.json()
        nuevo_token = data.get("access_token") or data.get("token")
    else:
        print(f"Error en la API: {response.text}")
except Exception as e:
    print(f"Excepción de red: {e}")

if not nuevo_token:
    print("No se pudo obtener el token nuevo.")
    exit(1)

token_limpio = str(nuevo_token).replace("tok_", "")

carpeta_nico = "nico"
modificados = 0

if os.path.exists(carpeta_nico):
    for root, dirs, files in os.walk(carpeta_nico):
        for file in files:
            if file.endswith((".m3u", ".m3u8", ".txt")):
                ruta_archivo = os.path.join(root, file)
                with open(ruta_archivo, "r", encoding="utf-8", errors="ignore") as f:
                    contenido = f.read()

                contenido_actualizado = re.sub(r'tok_[a-zA-Z0-9_\-\.]+', f"tok_{token_limpio}", contenido)

                with open(ruta_archivo, "w", encoding="utf-8") as f:
                    f.write(contenido_actualizado)
                
                modificados += 1
                print(f"Actualizado: {ruta_archivo}")

print(f"Proceso finalizado. Archivos modificados: {modificados}")
